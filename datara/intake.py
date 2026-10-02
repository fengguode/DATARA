"""TK11 - P0 source intake: per-file disposition, resource limits, duplicate and
conflict planning.

Trace: CUS01; SR01, SR02, SR27, SR32; FEAT01; WP02; D01.  TC01, TC19, TC21.

This module turns bytes plus an owner key into a *plan* for a caller-owned
persistence layer.  It deliberately does not touch a database: the Milestone A
entity set and the shared model layer belong to other tasks, and coordinating
through a returned, inspectable value keeps this task free of a schema claim it
cannot make.

BOUNDING ARCHITECTURAL CONDITION (decision register, G0 replacement for
Milestone A).  Nothing here names, stores or implies an entity whose meaning is
"the outcome of executing a skill against a model".  Concretely, and this is the
whole reason the shapes below are what they are:

* there is no ``Run``, ``Assessment``, ``Finding``, ``Result`` or ``latest_result``
  anywhere in this module, under any spelling;
* no object here carries a mutable pointer to a most-recent value.  Every object
  is frozen and every value is derived from bytes plus a rule version, so
  re-running intake of the same bytes yields the same plan;
* an ``ImportOutcome`` describes a *file disposition* - a deterministic data
  observation - not a judgement about an activity's meaning.  Rejected bytes
  never become accepted history: :func:`plan_import` emits no ``SourceObject``
  material at all for a rejected file.

D01 behaviour implemented here:

* 16 MiB per file; 50 files and 128 MiB of submitted bytes per batch; 200,000
  decoded messages and 100,000 sample records per file.  Limits are inclusive:
  exactly-at is accepted, one byte or one record over is rejected.  A limit
  failure creates no accepted activity.
* A batch reports per-file outcomes.  One rejected file does not undo
  independently accepted files, and a file contributes no partial accepted
  activity.
* Same owner + same SHA-256 is idempotent and references existing history.
  Different bytes with the exact logical tuple ``(owner, sport, UTC start,
  elapsed duration)`` are quarantined as a possible conflict.  Exact equality
  only - no tolerance matching, no silent merge, no overwrite.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Sequence

from datara.canonical import LogicalIdentity

from .classification import (
    REASON_BATCH_FILE_COUNT_EXCEEDED,
    REASON_BATCH_SIZE_LIMIT_EXCEEDED,
    REASON_FILE_CRC_INVALID,
    REASON_FILE_SIZE_LIMIT_EXCEEDED,
    REASON_HEADER_CRC_INVALID,
    REASON_MALFORMED_HEADER,
    REASON_MESSAGE_LIMIT_EXCEEDED,
    REASON_SAMPLE_LIMIT_EXCEEDED,
    RULE_VERSION,
    FileClassification,
    classify_bytes,
)

# ---------------------------------------------------------------------------
# D01 pilot resource limits.  Inclusive upper bounds.
# ---------------------------------------------------------------------------
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_BATCH_FILES = 50
MAX_BATCH_BYTES = 128 * 1024 * 1024
MAX_FILE_MESSAGES = 200_000
MAX_FILE_SAMPLE_RECORDS = 100_000
MAX_FILE_WALL_SECONDS = 60
MAX_FILE_MEMORY_MIB = 512

# Disposition states for one file in a batch.
DISPOSITION_ACCEPTED = "accepted"
DISPOSITION_REJECTED = "rejected"
DISPOSITION_DUPLICATE = "duplicate"
DISPOSITION_QUARANTINED = "quarantined"

#: Precedence for a submitted file, in order.  Recorded so the per-file outcome is
#: reproducible and so a reviewer can see which rule decided it.  Digest-only
#: idempotence first, then logical-tuple quarantine, then explicit owner
#: resolution (owned by the caller; this module never resolves on the user's
#: behalf).
PRECEDENCE = (
    "resource_limit",
    "integrity",
    "file_conformance",
    "exact_digest_duplicate",
    "logical_tuple_conflict",
)


def sha256_hex(data: bytes) -> str:
    """SHA-256 of the original bytes. Immutable-original storage key."""
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class QuarantineRecord:
    """A possible logical-tuple conflict, awaiting explicit owner resolution.

    This is a disposition state on the source chain, not a finding about an
    activity.  It names no skill and no model.  It retains the conflicting
    original by digest and the candidate's normalised tuple so both valid
    originals and their lineage are preserved, per D01.
    """

    owner_key: str
    conflicting_digest: str
    candidate_digest: str
    existing_reference: str
    logical_tuple: "LogicalIdentity"
    rule_version: str = RULE_VERSION
    reason_detail: str = ""


@dataclass(frozen=True)
class ImportOutcome:
    """Per-file outcome inside a batch. Frozen; no mutable latest-value pointer."""

    filename: str
    owner_key: str
    disposition: str
    classification: FileClassification
    digest: str
    byte_size: int
    #: Present only when the file is an exact byte duplicate of an already
    #: accepted original for the same owner.  References existing history.
    duplicate_of_digest: str | None = None
    #: Present only when disposition is ``quarantined``.
    quarantine: QuarantineRecord | None = None
    #: True when the file was not admitted and its raw bytes should be discarded
    #: promptly rather than retained as accepted history.
    discard_raw_bytes: bool = False
    decided_by: str = ""

    @property
    def accepted(self) -> bool:
        return self.disposition == DISPOSITION_ACCEPTED

    @property
    def reason_code(self) -> str:
        return self.classification.reason_code


@dataclass(frozen=True)
class ImportPlan:
    """The whole batch result. Frozen and reproducible from the same inputs."""

    owner_key: str
    outcomes: tuple[ImportOutcome, ...]
    rule_version: str = RULE_VERSION

    @property
    def accepted(self) -> tuple[ImportOutcome, ...]:
        return tuple(o for o in self.outcomes if o.disposition == DISPOSITION_ACCEPTED)

    @property
    def rejected(self) -> tuple[ImportOutcome, ...]:
        return tuple(o for o in self.outcomes if o.disposition == DISPOSITION_REJECTED)

    @property
    def quarantined(self) -> tuple[ImportOutcome, ...]:
        return tuple(o for o in self.outcomes if o.disposition == DISPOSITION_QUARANTINED)

    @property
    def duplicates(self) -> tuple[ImportOutcome, ...]:
        return tuple(o for o in self.outcomes if o.disposition == DISPOSITION_DUPLICATE)

    def accepted_source_objects(self) -> tuple[dict[str, object], ...]:
        """The minimal, complete source object for each accepted file.

        These are the four D01 required normalised inputs plus identity and
        provenance.  A rejected, duplicated or quarantined file contributes
        nothing here, which is how "rejected bytes are never published as
        accepted history" is enforced structurally rather than by convention.
        """
        return tuple(
            {
                "owner_key": o.owner_key,
                "digest_sha256": o.digest,
                "byte_size": o.byte_size,
                "filename": o.filename,
                "sport": o.classification.sport_name,
                "sport_raw": o.classification.sport_raw,
                "start_time_utc": o.classification.start_time_utc,
                "elapsed_duration_seconds": o.classification.elapsed_duration_seconds,
                "rule_version": o.classification.rule_version,
                "warnings": o.classification.warnings,
            }
            for o in self.accepted
        )


def _limit_outcome(
    filename: str,
    owner_key: str,
    digest: str,
    size: int,
    reason: str,
    detail: str,
    decided_by: str = "resource_limit",
) -> ImportOutcome:
    """A rejection that happened before any decoding attempt.

    Classification is skipped entirely: no accepted activity can be produced, and
    the raw bytes are marked for prompt discard per D01.  The reason is the
    limit's own stable code - a size rejection never borrows a structural or
    integrity reason, because that would misreport the cause to the athlete.
    """
    from .classification import REJECTION_REASONS  # noqa: PLC0415

    # An explicit raise, not an assert: `python -O` strips asserts, and a limit
    # reason code that quietly stopped being checked could reach the stable
    # vocabulary as an unrecognised code.
    if reason not in REJECTION_REASONS:
        raise ValueError(f"unstable reason code: {reason!r}")
    classification = FileClassification(
        disposition="rejected",
        reason_code=reason,
        reason_detail=detail,
        message_count=0,
        record_sample_count=0,
    )
    return ImportOutcome(
        filename=filename,
        owner_key=owner_key,
        disposition=DISPOSITION_REJECTED,
        classification=classification,
        digest=digest,
        byte_size=size,
        discard_raw_bytes=True,
        decided_by=decided_by,
    )


def plan_import(
    owner_key: str,
    files: Sequence[tuple[str, bytes]],
    *,
    accepted_digests: Iterable[str] = (),
    known_tuples: Iterable[LogicalIdentity] = (),
    max_file_bytes: int = MAX_FILE_BYTES,
    max_batch_files: int = MAX_BATCH_FILES,
    max_batch_bytes: int = MAX_BATCH_BYTES,
    max_file_messages: int = MAX_FILE_MESSAGES,
    max_file_sample_records: int = MAX_FILE_SAMPLE_RECORDS,
) -> ImportPlan:
    """Plan the intake of one batch of files for one owner.

    ``accepted_digests`` are digests already stored as accepted originals for this
    owner.  ``known_tuples`` are already-accepted logical tuples, as
    ``datara.canonical.LogicalIdentity`` values -- the *same* type a candidate's
    key is, so an existing activity and a new candidate are compared by exact
    integer equality rather than by two unrelated string shapes.  The owner
    component is ``owner_key``, so two different owners never collide here.

    Previously ``known_tuples`` were ``(sport, start_time_utc,
    elapsed_duration_seconds)`` string triples while the candidate key was a
    ``LogicalIdentity``: the two could never be equal, so a caller-supplied
    existing tuple was silently ignored and its file was accepted rather than
    quarantined.  The parameter type and this docstring now agree with the
    comparison that is actually performed.

    Pure: no I/O, no database, no model call, no clock.  The same inputs always
    produce an equal plan.
    """
    if not owner_key:
        raise ValueError("owner_key is required; an unowned file cannot be classified")

    seen_digests: dict[str, str] = {}
    known_digest_set = set(accepted_digests)
    # Keyed by the same type the candidate key is, so a caller-supplied existing
    # tuple is actually comparable. A type mismatch here is refused rather than
    # ignored: silently dropping the caller's existing tuples would accept a
    # duplicate that should have been quarantined.
    known_tuple_map: dict[LogicalIdentity, str] = {}
    for reference, identity in known_tuples:
        if not isinstance(identity, LogicalIdentity):
            raise TypeError(
                "known_tuples must carry datara.canonical.LogicalIdentity values, "
                f"the same type a candidate's logical_tuple is; got "
                f"{type(identity).__name__} for reference {reference!r}. A "
                "differently-shaped key can never equal a candidate, so it would "
                "be ignored and a duplicate accepted."
            )
        known_tuple_map[identity] = reference

    outcomes: list[ImportOutcome] = []
    total_bytes = 0

    if len(files) > max_batch_files:
        # The whole batch is out of policy.  Report it as a batch-level rejection
        # without decoding anything, rather than silently truncating to a subset
        # the user did not ask for.
        for filename, data in files:
            outcomes.append(
                _limit_outcome(
                    filename,
                    owner_key,
                    sha256_hex(data),
                    len(data),
                    REASON_BATCH_FILE_COUNT_EXCEEDED,
                    f"batch of {len(files)} files exceeds the inclusive D01 limit of "
                    f"{max_batch_files}; the batch is rejected as submitted and was "
                    "not silently truncated",
                    decided_by="resource_limit",
                )
            )
        return ImportPlan(owner_key=owner_key, outcomes=tuple(outcomes))

    for filename, data in files:
        digest = sha256_hex(data)
        size = len(data)
        total_bytes += size

        if size > max_file_bytes:
            outcomes.append(
                _limit_outcome(
                    filename,
                    owner_key,
                    digest,
                    size,
                    REASON_FILE_SIZE_LIMIT_EXCEEDED,
                    f"file is {size} bytes, above the inclusive D01 per-file limit of "
                    f"{max_file_bytes}",
                )
            )
            continue

        if total_bytes > max_batch_bytes:
            outcomes.append(
                _limit_outcome(
                    filename,
                    owner_key,
                    digest,
                    size,
                    REASON_BATCH_SIZE_LIMIT_EXCEEDED,
                    f"batch would total {total_bytes} bytes, above the inclusive D01 "
                    f"batch limit of {max_batch_bytes}",
                )
            )
            continue

        classification = classify_bytes(
            data,
            max_messages=max_file_messages,
            max_samples=max_file_sample_records,
        )

        if not classification.accepted:
            # Precedence 1-3: resource limit, integrity, file conformance.
            decided = (
                "resource_limit"
                if classification.reason_code
                in (REASON_MESSAGE_LIMIT_EXCEEDED, REASON_SAMPLE_LIMIT_EXCEEDED)
                else (
                    "integrity"
                    if classification.reason_code
                    in (
                        REASON_HEADER_CRC_INVALID,
                        REASON_FILE_CRC_INVALID,
                        REASON_MALFORMED_HEADER,
                    )
                    else "file_conformance"
                )
            )
            outcomes.append(
                ImportOutcome(
                    filename=filename,
                    owner_key=owner_key,
                    digest=digest,
                    byte_size=size,
                    disposition=DISPOSITION_REJECTED,
                    classification=classification,
                    discard_raw_bytes=True,
                    decided_by=decided,
                )
            )
            continue

        # Precedence 4: exact byte duplicate for the same owner is idempotent.
        if digest in known_digest_set or digest in seen_digests:
            outcomes.append(
                ImportOutcome(
                    filename=filename,
                    owner_key=owner_key,
                    digest=digest,
                    byte_size=size,
                    disposition=DISPOSITION_DUPLICATE,
                    classification=classification,
                    duplicate_of_digest=digest,
                    decided_by="exact_digest_duplicate",
                )
            )
            continue

        # Precedence 5: different bytes, same exact logical tuple -> quarantine.
        # Explicit, not an assert: under python -O the assert vanished, `key`
        # became None, and every distinct-byte file was keyed on None -- so a
        # file with a genuinely new activity could be quarantined against an
        # unrelated one, or accepted as new when it was the same activity.
        key = classification.logical_tuple
        if key is None:  # pragma: no cover - an accepted classification has one
            raise RuntimeError(
                f"{filename!r} reached the duplicate decision with no logical "
                "tuple, so no exact comparison is possible and no disposition "
                "can be claimed"
            )
        reference = known_tuple_map.get(key)
        if reference is not None:
            record = QuarantineRecord(
                owner_key=owner_key,
                conflicting_digest=reference,
                candidate_digest=digest,
                existing_reference=reference,
                logical_tuple=key,
                reason_detail=(
                    f"different bytes share the exact logical tuple {key} for this "
                    "owner; awaiting explicit owner resolution"
                ),
            )
            outcomes.append(
                ImportOutcome(
                    filename=filename,
                    owner_key=owner_key,
                    digest=digest,
                    byte_size=size,
                    disposition=DISPOSITION_QUARANTINED,
                    classification=classification,
                    quarantine=record,
                    decided_by="logical_tuple_conflict",
                )
            )
            continue

        seen_digests[digest] = filename
        known_tuple_map[key] = digest
        outcomes.append(
            ImportOutcome(
                filename=filename,
                owner_key=owner_key,
                digest=digest,
                byte_size=size,
                disposition=DISPOSITION_ACCEPTED,
                classification=classification,
                decided_by="file_conformance",
            )
        )

    return ImportPlan(owner_key=owner_key, outcomes=tuple(outcomes))
