"""Duplicate and conflict disposition state machine (CUS02, SR04, SR33; FEAT02).

This module is the **policy** half of TK15 (#121). `datara.storage` owns the
bytes; this module decides what a submission *means* and records that meaning
on the source chain. It implements the authoritative precedence table of
`docs/management/source-evidence/duplicate-conflict-options.md` section 5 and
the canonical comparison values of section 6, both of which are the selected
outcome of TK14 (#120) and the founder's D01 record
(`docs/management/p0-decision-baseline-2026-10-01.md:48`). That decision is not
reopened here.

One submission, exactly one disposition, first matching rule wins:

===== ==========================================================================
Rule  Precondition                                     Disposition
===== ==========================================================================
P1    SHA-256 equals an *accepted* original of owner   ``duplicate_of_existing``
P2    SHA-256 equals a *quarantined* original of owner ``duplicate_of_quarantined``
P3    bytes differ, tuple equals an *accepted* tuple   ``quarantined_conflict``
P4    bytes differ, tuple equals a *quarantined* tuple ``quarantined_conflict``
P5    bytes differ, tuple differs                      ``accepted``
P6    bytes equal a previously *rejected* submission   ``rejected``, re-evaluated
P7    bytes equal a superseded or deleted original      reference is *unavailable*
===== ==========================================================================

The four hard prohibitions of section 7 are properties of this state machine,
not cautions attached to it:

* **Never silently merge** -- merge is not an outcome of the state machine at
  all. No branch combines a field of one original with a field of another, so a
  later transition cannot introduce a merge either.
* **Never tolerance or fuzzy matching** -- the tuple is compared by integer
  equality on the section 6 canonical values. There is no threshold parameter
  anywhere in the public surface, and ``assert_no_tolerance_parameters()``
  machine-checks that by introspecting every public callable, so adding one is
  a test failure rather than a silent product defect.
* **Never overwrite** -- originals are immutable (see `datara.storage`), and a
  conflict is resolved by appending a disposition, never by rewriting the
  candidate or the original it collides with.
* **No cross-owner disclosure** -- every query is owner-scoped, so an identical
  digest belonging to another identity produces no hit, no count and no
  distinct error, exactly as section 7 requires.

Two decisions this module makes where the architecture left a consequence rather
than a rule, both recorded here because they are visible in the code:

1. **P6 needs no implementation.** D01 discards rejected raw bytes promptly,
   so a rejected submission leaves no ``SourceObject`` and no digest to match.
   ``ingest()`` is therefore only ever called for a submission that already
   decoded and normalized successfully; a file that failed any check is rejected
   upstream of this module and never reaches storage. See ``REJECTION_BOUNDARY``.
2. **The unreferenced-original residue is resolved fail-safe.** If a crash left
   a ``SourceObject`` with no published ``Activity`` and no ``Quarantine``, P1-P7
   name no case. It is reported as ``duplicate_of_existing`` with
   ``UNREFERENCED_ORIGINAL`` and creates neither a second original nor a second
   activity -- it can neither merge nor overwrite.

**Binding architectural condition.** Nothing in this module persists the
outcome of executing a skill against a model, under any name, and there is no
mutable "latest result" or current-value pointer: history is queried, never
"latest". ``assert_no_outcome_fields`` additionally refuses an outcome-shaped
key arriving through the write path. This module calls no model and contains no
provider transport (SR06).

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence

from django.db import IntegrityError, transaction

from datara import CONTRACT_VERSION, IDENTITY_LABEL, NORMALIZER_VERSION
from datara.models import (
    Activity,
    Import,
    Quarantine,
    ResourceNotVisible,
    Session,
    Snapshot,
    SourceObject,
)
from datara.storage import (
    OriginalStore,
    StoredOriginal,
    resolve_owner_id,
    sha256_digest,
)


# --------------------------------------------------------------------------
# Section 6 -- canonical comparison values
# --------------------------------------------------------------------------

#: The approved normalised sport enum. Section 6 fixes the canonical comparison
#: value as the *integer*; the string form is the display name of the same
#: approved pair and is what `Session.sport` stores. This is a closed two-value
#: vocabulary taken verbatim from section 6, not an invented mapping.
SPORT_CODES: dict[int, str] = {1: "running", 2: "cycling"}

#: `sub_sport` is deliberately NOT a tuple component (section 6): a re-export
#: that changed only the sub-sport classification therefore still conflicts,
#: which is the conservative direction.
TUPLE_COMPONENTS: tuple[str, ...] = (
    "owner_id",
    "sport_code",
    "start_epoch_seconds",
    "elapsed_duration_ms",
)

#: Documented boundary rather than a policy. `ingest` is called only after the
#: submitter's bytes decoded and normalized successfully; a decode, integrity,
#: limit or required-field failure rejects the whole file upstream, which is
#: where the rejected-bytes path of P6 lives.
REJECTION_BOUNDARY = (
    "ingest() is entered only for a submission that already passed decoding, "
    "conformance and eligibility; rejected bytes never reach this module"
)


def canonical_sport_code(value: Any) -> int:
    """Return the canonical integer sport code for a normalised value.

    Section 6 fixes the comparison value as the integer enum code. An
    unrecognised value is refused rather than coerced, because coercing it would
    invent a sport and therefore invent a tuple.
    """

    if isinstance(value, bool):
        raise ValueError("sport must be a sport code, not a bool")
    if isinstance(value, int):
        if value not in SPORT_CODES:
            raise ValueError(
                f"sport code {value!r} is outside the approved set {sorted(SPORT_CODES)}"
            )
        return value
    if isinstance(value, str):
        folded = value.strip().lower()
        for code, name in SPORT_CODES.items():
            if folded == name:
                return code
        raise ValueError(
            f"sport {value!r} is not in the approved normalised set {sorted(SPORT_CODES)}"
        )
    raise ValueError(f"cannot canonicalise sport of type {type(value).__name__}")


def sport_name(code: int) -> str:
    return SPORT_CODES[canonical_sport_code(code)]


@dataclass(frozen=True)
class SessionFacts:
    """The canonical normalised inputs of one session.

    These are the values of section 6 expressed as integers, supplied by the
    normalizer that decoded the original. They are not re-derived from a
    display string or a float anywhere in this module.
    """

    sport_code: int
    session_start_utc: datetime
    elapsed_duration_ms: int
    session_index: int = 0
    session_count: int = 1
    timer_duration_seconds: int | None = None

    def __post_init__(self) -> None:
        canonical_sport_code(self.sport_code)
        if not isinstance(self.elapsed_duration_ms, int) or isinstance(
            self.elapsed_duration_ms, bool
        ):
            raise TypeError(
                "elapsed duration must be an exact integer, never a float: a "
                "float would reintroduce an approximate comparison"
            )
        if self.elapsed_duration_ms < 0:
            raise ValueError("elapsed duration must not be negative")
        start = self.session_start_utc
        if start.tzinfo is None:
            raise ValueError("session start must be an aware UTC datetime")
        if start.microsecond != 0:
            # Section 6 compares the start as an exact integer number of seconds
            # since the epoch. A sub-second instant cannot be represented by
            # that canonical value, so accepting one would silently discard
            # precision and could merge two genuinely different activities.
            raise ValueError(
                "session start must be an exact whole second: the canonical "
                "comparison value is integer epoch seconds"
            )

    @property
    def start_epoch_seconds(self) -> int:
        """Exact integer seconds since the Unix epoch (section 6)."""

        return int(self.session_start_utc.timestamp())


@dataclass(frozen=True)
class LogicalTuple:
    """The exact logical tuple of section 6, and the only conflict key.

    Equality is integer equality on the four canonical values. There is no
    tolerance, epsilon, rounding or normalisation step, because there is
    nothing to configure: `TOLERANCE_PARAMETERS` is empty and
    `assert_no_tolerance_parameters` keeps it that way.
    """

    owner_id: int
    sport_code: int
    start_epoch_seconds: int
    elapsed_duration_ms: int

    @classmethod
    def from_session(cls, owner_id: int, facts: SessionFacts) -> "LogicalTuple":
        return cls(
            owner_id=owner_id,
            sport_code=canonical_sport_code(facts.sport_code),
            start_epoch_seconds=facts.start_epoch_seconds,
            elapsed_duration_ms=facts.elapsed_duration_ms,
        )

    def as_dict(self) -> dict[str, Any]:
        """The persisted form, carrying the unit of every component.

        The units are written into the record rather than assumed by a reader,
        so `elapsed_duration_ms` cannot later be compared as if it were seconds.
        """

        return {
            "owner_id": self.owner_id,
            "sport_code": self.sport_code,
            "sport_name": sport_name(self.sport_code),
            "start_epoch_seconds": self.start_epoch_seconds,
            "elapsed_duration_ms": self.elapsed_duration_ms,
            "start_unit": "integer_seconds_since_unix_epoch",
            "elapsed_unit": "integer_milliseconds",
            "comparison": "exact_integer_equality",
            "tolerance": None,
            "sub_sport_is_a_component": False,
            "contract": "duplicate-conflict-options section 6",
        }


# --------------------------------------------------------------------------
# Dispositions
# --------------------------------------------------------------------------


class Disposition(str, Enum):
    """The five per-file dispositions of section 5 / section 10."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DUPLICATE_OF_EXISTING = "duplicate_of_existing"
    DUPLICATE_OF_QUARANTINED = "duplicate_of_quarantined"
    QUARANTINED_CONFLICT = "quarantined_conflict"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


#: Reason codes are a stable, safe vocabulary: no filename, no byte content and
#: no other owner's data ever appears in one.
REASON_ACCEPTED = "ACCEPTED"
REASON_DUPLICATE_OF_EXISTING = "DUPLICATE_OF_EXISTING"
REASON_DUPLICATE_OF_QUARANTINED = "DUPLICATE_OF_QUARANTINED"
REASON_LOGICAL_TUPLE_CONFLICT = Quarantine.REASON_LOGICAL_TUPLE_CONFLICT
REASON_UNREFERENCED_ORIGINAL = "UNREFERENCED_ORIGINAL"
REASON_REFERENCE_UNAVAILABLE = "REFERENCE_UNAVAILABLE"
REASON_NOTHING_COMMITTED = "NOTHING_COMMITTED"

#: Defence in depth on the write path. The authoritative guarantee is the
#: schema itself, which has no such column; this refuses an outcome-shaped key
#: arriving through ``activity_payload`` so the semantic exclusion cannot be
#: defeated by a caller adding a field name the schema never intended.
FORBIDDEN_OUTCOME_FIELDS: frozenset[str] = frozenset(
    {
        "run",
        "runs",
        "run_id",
        "execution",
        "selected_skill_execution",
        "attempt",
        "assessment",
        "assessment_result",
        "finding",
        "findings",
        "result",
        "result_id",
        "results",
        "latest_result",
        "latest_assessment",
        "current_result",
        "current_value",
        "model_verdict",
        "model_output",
        "recommendation",
    }
)

#: Activity/Snapshot columns a caller may supply through ``activity_payload``.
#: It is an allowlist, so an unlisted column cannot be written by accident.
REQUIRED_PAYLOAD_FIELDS: tuple[str, ...] = (
    "normalization_digest",
    "policy_version",
    "mapping_reference",
)
OPTIONAL_PAYLOAD_FIELDS: tuple[str, ...] = (
    "quality_warnings",
    "timer_duration_seconds",
    "distance_value",
    "distance_unit_code",
    "record_sample_count",
    "gps_point_count",
    "heart_rate_value",
    "heart_rate_unit_code",
    "normalizer_version",
    "contract_version",
)


@dataclass(frozen=True)
class DispositionOutcome:
    """The single outcome of one submission.

    Every field is nullable on purpose: a disposition names what exists, and the
    shape of what exists differs per rule. A reference is a reference, never a
    copy of the referenced record.
    """

    disposition: Disposition
    rule: str
    reason_code: str
    digest: str
    owner_id: int
    created_original: bool
    created_activity: bool
    import_record: Import | None = None
    source_object: SourceObject | None = None
    referenced_source_object: SourceObject | None = None
    activity: Activity | None = None
    quarantine: Quarantine | None = None
    logical_tuple: LogicalTuple | None = None
    detail: str = ""

    @property
    def is_excluded_from_history(self) -> bool:
        """True when this submission contributes nothing to normal history.

        A quarantined candidate and a duplicate reference both leave history
        exactly as it was. Only ``accepted`` adds to it.
        """

        return self.disposition is not Disposition.ACCEPTED

    def counts_toward_volume(self) -> bool:
        """Section 9 rule 3: a quarantined candidate is never counted anywhere."""

        return self.disposition is Disposition.ACCEPTED


# --------------------------------------------------------------------------
# Section 7 -- machine-checked absence of tolerance
# --------------------------------------------------------------------------

#: Any public parameter containing one of these tokens would be a tolerance.
TOLERANCE_PARAMETER_TOKENS: tuple[str, ...] = (
    "tolerance",
    "epsilon",
    "threshold",
    "fuzzy",
    "approx",
    "slack",
    "grace",
    "within",
    "near_",
    "close_",
    "window",
)


def tolerance_parameters() -> dict[str, list[str]]:
    """Introspect this module's public surface for a tolerance parameter.

    Returns a mapping of callable name to the offending parameter names. It is
    empty by construction; it is written so that it stays empty.
    """

    found: dict[str, list[str]] = {}
    for name, member in list(globals().items()):
        if name.startswith("_"):
            continue
        targets: list[tuple[str, Any]] = []
        if inspect.isfunction(member):
            targets.append((name, member))
        elif inspect.isclass(member) and member.__module__ == __name__:
            for attr_name, attr in vars(member).items():
                if attr_name.startswith("_"):
                    continue
                if isinstance(attr, property):
                    continue
                if inspect.isfunction(attr):
                    targets.append((f"{name}.{attr_name}", attr))
        for target_name, func in targets:
            try:
                signature = inspect.signature(func)
            except (TypeError, ValueError):  # pragma: no cover - defensive
                continue
            offenders = [
                parameter
                for parameter in signature.parameters
                if any(
                    token in parameter.lower() for token in TOLERANCE_PARAMETER_TOKENS
                )
            ]
            if offenders:
                found[target_name] = sorted(offenders)
    return found


def assert_no_tolerance_parameters() -> None:
    """Fail loudly if a tolerance parameter has been introduced.

    Also re-checks that the logical tuple still carries exactly the four
    canonical integer components, so widening the key -- the other way a
    tolerance could sneak in -- is a failure too.
    """

    offenders = tolerance_parameters()
    if offenders:
        raise AssertionError(
            "a tolerance parameter exists on the intake surface, which D01 "
            f"prohibits: {offenders}"
        )
    if tuple(LogicalTuple.__dataclass_fields__) != TUPLE_COMPONENTS:
        raise AssertionError(
            "the logical tuple key changed; it must be exactly "
            f"{TUPLE_COMPONENTS}, got {tuple(LogicalTuple.__dataclass_fields__)}"
        )
    for field_name, field_def in LogicalTuple.__dataclass_fields__.items():
        if field_def.type != "int" and field_def.type is not int:
            raise AssertionError(
                f"logical tuple component {field_name} is not an exact integer: "
                f"{field_def.type}"
            )


def assert_no_outcome_fields(payload: Mapping[str, Any]) -> None:
    """Refuse a payload carrying a skill-against-model outcome under any name."""

    offending = sorted(
        key
        for key in payload
        if key.lower() in FORBIDDEN_OUTCOME_FIELDS
        or any(token in key.lower() for token in ("latest", "current_", "model_output"))
    )
    if offending:
        raise AssertionError(
            "refusing to persist a skill-against-model outcome; Milestone A "
            f"persists no such entity (decision-register binding architectural "
            f"condition). Offending keys: {offending}"
        )


# --------------------------------------------------------------------------
# Exact tuple matching
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class TupleMatch:
    """An existing session of this owner whose exact tuple equals a candidate's."""

    session: Session
    activity: Activity
    logical_tuple: LogicalTuple


def find_exact_tuple_matches(
    owner_id: int, candidate: LogicalTuple
) -> list[TupleMatch]:
    """Return every existing session of ``owner_id`` with the *exact* same tuple.

    The start instant is matched by the database as an exact aware-datetime
    equality, which is an integer-second equality because `SessionFacts` refuses
    a sub-second instant. The sport and the elapsed duration are then compared
    by integer equality in Python, so there is no range predicate, no
    `__gte`/`__lte` window and no rounding anywhere in the comparison.

    Candidates are narrowed by owner first and by start instant second, so a
    match can only ever be another activity of the *same* identity. This is the
    function a fuzzy implementation would have to change; a near-match that
    differs by one second or one millisecond returns nothing here and the
    submission is accepted separately by P5.

    Every match is returned rather than only the first, because the state
    machine must distinguish "an accepted activity holds this tuple" from "a
    quarantined candidate already holds this tuple", and a tuple can legitimately
    have both at once.
    """

    start = datetime.fromtimestamp(
        candidate.start_epoch_seconds, tz=timezone.utc
    )
    matches: list[TupleMatch] = []
    for session in (
        Session.objects.for_owner(owner_id)
        .filter(session_start_utc=start)
        .select_related("activity", "activity__source_object")
        .order_by("pk")
    ):
        if canonical_sport_code(session.sport) != candidate.sport_code:
            continue
        if session.elapsed_duration_seconds != candidate.elapsed_duration_ms:
            continue
        matches.append(
            TupleMatch(
                session=session,
                activity=session.activity,
                logical_tuple=LogicalTuple(
                    owner_id=owner_id,
                    sport_code=candidate.sport_code,
                    start_epoch_seconds=candidate.start_epoch_seconds,
                    elapsed_duration_ms=candidate.elapsed_duration_ms,
                ),
            )
        )
    return matches


def find_exact_tuple_match(
    owner_id: int, candidate: LogicalTuple
) -> TupleMatch | None:
    """The first exact tuple match, or ``None``. See `find_exact_tuple_matches`."""

    matches = find_exact_tuple_matches(owner_id, candidate)
    return matches[0] if matches else None


# --------------------------------------------------------------------------
# The precedence state machine
# --------------------------------------------------------------------------


def _clean_payload(activity_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate ``activity_payload`` against the allowlist and the exclusions."""

    assert_no_outcome_fields(activity_payload)
    missing = [key for key in REQUIRED_PAYLOAD_FIELDS if key not in activity_payload]
    if missing:
        raise ValueError(f"activity_payload is missing required fields: {missing}")
    unknown = [
        key
        for key in activity_payload
        if key not in REQUIRED_PAYLOAD_FIELDS and key not in OPTIONAL_PAYLOAD_FIELDS
    ]
    if unknown:
        raise ValueError(
            f"activity_payload carries fields that are not part of the "
            f"normalization contract: {unknown}"
        )
    return {
        key: value
        for key, value in activity_payload.items()
        if key in REQUIRED_PAYLOAD_FIELDS or key in OPTIONAL_PAYLOAD_FIELDS
    }


def _claim_original(
    owner_id: int,
    digest: str,
    stored: StoredOriginal,
    media_type: str,
) -> tuple[SourceObject, bool]:
    """Claim the digest for this owner, or return the existing claim.

    Section 8.1: idempotence under concurrency is enforced by the database
    unique constraint on ``(owner, digest)``, **not** by an application-level
    read-then-write. A read-then-write would let two concurrent identical
    submissions both decide "not present" and both insert. Here the insert is
    attempted and the constraint arbitrates; the loser reads back the winner's
    row inside a savepoint so the surrounding transaction stays usable.
    """

    try:
        with transaction.atomic():
            source_object = SourceObject.objects.create(
                owner_id=owner_id,
                digest=digest,
                byte_length=stored.byte_length,
                storage_reference=stored.storage_reference,
                media_type=media_type,
            )
        return source_object, True
    except IntegrityError:
        existing = SourceObject.objects.for_owner(owner_id).get(digest=digest)
        return existing, False


def _classify_existing_original(
    owner_id: int, source_object: SourceObject
) -> tuple[Disposition, Activity | None, Quarantine | None]:
    """Apply P1 then P2 to an original this owner already holds."""

    published = (
        Activity.objects.for_owner(owner_id)
        .filter(source_object=source_object, disposition=Activity.PUBLISHED)
        .order_by("pk")
        .first()
    )
    if published is not None:
        return Disposition.DUPLICATE_OF_EXISTING, published, None

    quarantined = (
        Quarantine.objects.for_owner(owner_id)
        .filter(candidate_source_object=source_object, state=Quarantine.STATE_QUARANTINED)
        .order_by("pk")
        .first()
    )
    if quarantined is not None:
        return Disposition.DUPLICATE_OF_QUARANTINED, None, quarantined

    # Crash residue between the file store and the database: an original with no
    # published activity and no quarantine. Reported as a duplicate reference so
    # that neither a second original nor a second activity is created.
    return Disposition.DUPLICATE_OF_EXISTING, None, None


def ingest(
    owner: Any,
    *,
    data: bytes,
    media_type: str = "application/octet-stream",
    sessions: Sequence[SessionFacts],
    activity_payload: Mapping[str, Any],
    store: OriginalStore,
    submitted_at: datetime | None = None,
    submitted_file_name: str = "upload.bin",
) -> DispositionOutcome:
    """Apply the section 5 precedence table to one submission and persist it.

    ``owner`` must be the server-derived authenticated identity. ``sessions``
    are the canonical normalised values produced by the decoder; ``data`` are
    the submitted bytes, which are written once and never rewritten.

    The conflict test and the ``Activity`` insert share one transaction
    (section 8.2), so two concurrent byte-different submissions with an equal
    tuple cannot both reach an accepted state: one accepts and one quarantines.
    """

    owner_id = resolve_owner_id(owner)
    assert_no_tolerance_parameters()

    if not sessions:
        raise ValueError("a submission must carry at least one normalized session")
    payload = _clean_payload(activity_payload)
    digest = sha256_digest(bytes(data))

    # (1) Byte layer, first and write-once. For a repeat submission this writes
    # nothing: the file already exists and is verified, so a second original
    # cannot be created here either.
    stored = store.put(owner_id, bytes(data), media_type=media_type)

    # (2) Claim the digest. The unique constraint, not a read, arbitrates.
    source_object, claimed_new = _claim_original(owner_id, digest, stored, media_type)

    if not claimed_new:
        disposition, activity, quarantine = _classify_existing_original(
            owner_id, source_object
        )
        unreferenced = (
            disposition is Disposition.DUPLICATE_OF_EXISTING
            and activity is None
            and quarantine is None
        )
        return DispositionOutcome(
            disposition=disposition,
            rule="P2" if disposition is Disposition.DUPLICATE_OF_QUARANTINED else "P1",
            reason_code=(
                REASON_UNREFERENCED_ORIGINAL
                if unreferenced
                else (
                    REASON_DUPLICATE_OF_QUARANTINED
                    if disposition is Disposition.DUPLICATE_OF_QUARANTINED
                    else REASON_DUPLICATE_OF_EXISTING
                )
            ),
            digest=digest,
            owner_id=owner_id,
            created_original=False,
            created_activity=False,
            source_object=source_object,
            referenced_source_object=source_object,
            activity=activity,
            quarantine=quarantine,
            detail=(
                "an original for these bytes already exists for this owner and is "
                "referenced; no second original and no second activity were created"
            ),
        )

    # (3) Bytes are new to this owner. Evaluate the exact logical tuple.
    primary_facts = sessions[0]
    candidate = LogicalTuple.from_session(owner_id, primary_facts)
    matches = find_exact_tuple_matches(owner_id, candidate)
    quarantined_matches = [
        m for m in matches if m.activity.disposition == Activity.QUARANTINED
    ]
    accepted_matches = [
        m for m in matches if m.activity.disposition == Activity.PUBLISHED
    ]

    # P4 is tested before P3 even though the section 5 table lists P3 first.
    # A tuple can legitimately hold an accepted activity *and* an already
    # quarantined candidate at the same time, and in that state both preconditions
    # are true. Applying P3 would create a fresh candidate for every re-export,
    # which is the unbounded fan-out P4 exists to prevent, so P4 governs the
    # candidate slot and P3 creates the first candidate only. This ordering is
    # reported to the Architect as a precedence ambiguity in the table.
    if quarantined_matches:
        return _p4_link_existing_candidate(
            owner_id=owner_id,
            source_object=source_object,
            sessions=sessions,
            payload=payload,
            quarantined_match=quarantined_matches[0],
            accepted_match=accepted_matches[0] if accepted_matches else None,
            candidate=candidate,
            submitted_at=submitted_at,
            submitted_file_name=submitted_file_name,
        )

    if accepted_matches:
        return _p3_quarantine_conflict(
            owner_id=owner_id,
            source_object=source_object,
            sessions=sessions,
            payload=payload,
            match=accepted_matches[0],
            candidate=candidate,
            submitted_at=submitted_at,
            submitted_file_name=submitted_file_name,
        )

    return _p5_accept(
        owner_id=owner_id,
        source_object=source_object,
        sessions=sessions,
        payload=payload,
        candidate=candidate,
        submitted_at=submitted_at,
    )


def _create_import(
    owner_id: int,
    digest: str,
    status: str,
    reason_code: str,
    submitted_at: datetime | None,
) -> Import:
    return Import.objects.create(
        owner_id=owner_id,
        source_digest=digest,
        contract_version=CONTRACT_VERSION,
        status=status,
        reason_code=reason_code,
        accepted_at=(submitted_at or datetime.now(timezone.utc))
        if status == Import.ACCEPTED
        else None,
        parser_version=None,
        profile_reference=None,
        preparation_version=NORMALIZER_VERSION,
        warnings=[],
    )


def _write_sessions(
    owner_id: int, activity: Activity, sessions: Sequence[SessionFacts]
) -> None:
    for facts in sessions:
        Session.objects.create(
            owner_id=owner_id,
            activity=activity,
            session_index=facts.session_index,
            session_count=facts.session_count,
            sport=sport_name(facts.sport_code),
            session_start_utc=facts.session_start_utc,
            elapsed_duration_seconds=facts.elapsed_duration_ms,
            timer_duration_seconds=facts.timer_duration_seconds,
        )


def _p5_accept(
    *,
    owner_id: int,
    source_object: SourceObject,
    sessions: Sequence[SessionFacts],
    payload: Mapping[str, Any],
    candidate: LogicalTuple,
    submitted_at: datetime | None,
) -> DispositionOutcome:
    """P5: bytes differ and the tuple differs, so accept.

    No deduplication claim is made and none is implied. P5 is where the false
    negative of an exact heuristic lives -- a re-export that changed any tuple
    component is accepted as a separate activity -- and that limit is stated to
    the athlete rather than engineered away with an invented threshold.
    """

    with transaction.atomic():
        import_record = _create_import(
            owner_id, source_object.digest, Import.ACCEPTED, REASON_ACCEPTED, submitted_at
        )
        activity = Activity.objects.create(
            owner_id=owner_id,
            source_object=source_object,
            import_record=import_record,
            disposition=Activity.PUBLISHED,
            **payload,
        )
        _write_sessions(owner_id, activity, sessions)

    return DispositionOutcome(
        disposition=Disposition.ACCEPTED,
        rule="P5",
        reason_code=REASON_ACCEPTED,
        digest=source_object.digest,
        owner_id=owner_id,
        created_original=True,
        created_activity=True,
        import_record=import_record,
        source_object=source_object,
        activity=activity,
        logical_tuple=candidate,
        detail=(
            "accepted as a separate activity; the logical tuple differs from every "
            "existing activity of this owner, and no duplicate claim is made"
        ),
    )


def _p3_quarantine_conflict(
    *,
    owner_id: int,
    source_object: SourceObject,
    sessions: Sequence[SessionFacts],
    payload: Mapping[str, Any],
    match: TupleMatch,
    candidate: LogicalTuple,
    submitted_at: datetime | None,
    submitted_file_name: str,
) -> DispositionOutcome:
    """P3: byte-different files sharing an exact tuple with an accepted activity.

    The candidate is a valid original and is retained in quarantined owner scope
    (`implementation-contracts.md:62`), but it is excluded from normal history
    and from every snapshot. Nothing is merged and nothing is overwritten: both
    originals survive intact and the conflict is resolved only by an
    authenticated owner action.
    """

    with transaction.atomic():
        import_record = _create_import(
            owner_id,
            source_object.digest,
            Import.CONFLICT,
            REASON_LOGICAL_TUPLE_CONFLICT,
            submitted_at,
        )
        activity = Activity.objects.create(
            owner_id=owner_id,
            source_object=source_object,
            import_record=import_record,
            disposition=Activity.QUARANTINED,
            **payload,
        )
        _write_sessions(owner_id, activity, sessions)
        quarantine = Quarantine.objects.create(
            owner_id=owner_id,
            import_record=import_record,
            candidate_source_object=source_object,
            conflicting_source_object=match.activity.source_object,
            logical_tuple=candidate.as_dict(),
            candidate_normalization_digest=payload["normalization_digest"],
            candidate_normalized_payload={
                "kind": "logical_tuple_conflict",
                "candidate_activity": str(activity.pk),
                "candidate_file_name": submitted_file_name,
                "submitted_at": (
                    (submitted_at or datetime.now(timezone.utc)).isoformat(
                        timespec="seconds"
                    )
                ),
                "conflicting_activity": str(match.activity.pk),
                "conflict_group": {
                    "primary_quarantine_id": None,
                    "tuple_key": tuple_group_key(candidate),
                },
            },
            reason_code=Quarantine.REASON_LOGICAL_TUPLE_CONFLICT,
            state=Quarantine.STATE_QUARANTINED,
            resolution=None,
            resolved_at=None,
        )

    return DispositionOutcome(
        disposition=Disposition.QUARANTINED_CONFLICT,
        rule="P3",
        reason_code=REASON_LOGICAL_TUPLE_CONFLICT,
        digest=source_object.digest,
        owner_id=owner_id,
        created_original=True,
        created_activity=True,
        import_record=import_record,
        source_object=source_object,
        referenced_source_object=match.activity.source_object,
        activity=activity,
        quarantine=quarantine,
        logical_tuple=candidate,
        detail=(
            "quarantined as a possible conflict: the bytes differ from an existing "
            "accepted activity of this owner while the exact logical tuple matches. "
            "The candidate may be the same activity and is excluded from history and "
            "every snapshot until an authenticated owner resolves it"
        ),
    )


def _p4_link_existing_candidate(
    *,
    owner_id: int,
    source_object: SourceObject,
    sessions: Sequence[SessionFacts],
    payload: Mapping[str, Any],
    quarantined_match: TupleMatch,
    accepted_match: TupleMatch | None,
    candidate: LogicalTuple,
    submitted_at: datetime | None,
    submitted_file_name: str,
) -> DispositionOutcome:
    """P4: the tuple already has a quarantined candidate, so link rather than fan out.

    A second candidate *activity* is not created for the same tuple, which is
    what stops repeated re-exports from growing an unbounded candidate set. The
    new original is still retained, because D01 preserves both valid originals
    and originals are immutable, and it is recorded against the primary
    candidate through the conflict group.
    """

    primary_quarantine = (
        Quarantine.objects.for_owner(owner_id)
        .filter(
            candidate_source_object=quarantined_match.activity.source_object,
            state=Quarantine.STATE_QUARANTINED,
        )
        .order_by("pk")
        .first()
    )
    # The record ultimately conflicts with the accepted activity; the existing
    # candidate it is linked to is carried in the conflict group.
    conflicting_source = (
        accepted_match.activity.source_object
        if accepted_match is not None
        else quarantined_match.activity.source_object
    )
    with transaction.atomic():
        import_record = _create_import(
            owner_id,
            source_object.digest,
            Import.CONFLICT,
            REASON_LOGICAL_TUPLE_CONFLICT,
            submitted_at,
        )
        quarantine = Quarantine.objects.create(
            owner_id=owner_id,
            import_record=import_record,
            candidate_source_object=source_object,
            conflicting_source_object=conflicting_source,
            logical_tuple=candidate.as_dict(),
            candidate_normalization_digest=payload["normalization_digest"],
            candidate_normalized_payload={
                "kind": "logical_tuple_conflict",
                "candidate_activity": None,
                "candidate_file_name": submitted_file_name,
                "submitted_at": (
                    (submitted_at or datetime.now(timezone.utc)).isoformat(
                        timespec="seconds"
                    )
                ),
                "conflicting_activity": str(
                    (accepted_match or quarantined_match).activity.pk
                ),
                "linked_candidate_activity": str(quarantined_match.activity.pk),
                "conflict_group": {
                    "primary_quarantine_id": (
                        str(primary_quarantine.pk) if primary_quarantine else None
                    ),
                    "tuple_key": tuple_group_key(candidate),
                    "no_second_candidate_activity": True,
                },
            },
            reason_code=Quarantine.REASON_LOGICAL_TUPLE_CONFLICT,
            state=Quarantine.STATE_QUARANTINED,
            resolution=None,
            resolved_at=None,
        )

    return DispositionOutcome(
        disposition=Disposition.QUARANTINED_CONFLICT,
        rule="P4",
        reason_code=REASON_LOGICAL_TUPLE_CONFLICT,
        digest=source_object.digest,
        owner_id=owner_id,
        created_original=True,
        created_activity=False,
        import_record=import_record,
        source_object=source_object,
        referenced_source_object=conflicting_source,
        activity=None,
        quarantine=quarantine,
        logical_tuple=candidate,
        detail=(
            "linked to the existing quarantined candidate for this exact tuple; no "
            "second candidate activity was created and the candidate stays excluded "
            "from history and every snapshot"
        ),
    )


def tuple_group_key(candidate: LogicalTuple) -> str:
    """A stable key identifying one conflict group by its exact tuple.

    Built from the four canonical integers only, so two submissions share a
    group if and only if their tuples are exactly equal.
    """

    canonical = LogicalTuple(
        owner_id=candidate.owner_id,
        sport_code=candidate.sport_code,
        start_epoch_seconds=candidate.start_epoch_seconds,
        elapsed_duration_ms=candidate.elapsed_duration_ms,
    )
    return hashlib.sha256(
        json.dumps(
            [
                canonical.owner_id,
                canonical.sport_code,
                canonical.start_epoch_seconds,
                canonical.elapsed_duration_ms,
            ],
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


# --------------------------------------------------------------------------
# Section 8.3 -- uncertain commit is resolved by lookup, not by retry
# --------------------------------------------------------------------------


def resolve_uncertain(
    owner: Any, digest: str, *, store: OriginalStore | None = None
) -> DispositionOutcome | None:
    """Re-query ``(owner, digest)`` after a lost response. Never writes.

    Section 8.3: after any lost response or ambiguous outcome the intake path
    re-queries and reports the disposition rather than resubmitting, because a
    blind retry is what would create a second accepted activity after a partial
    commit. Returns ``None`` when nothing was committed, which is the only
    condition under which the caller may submit again.
    """

    owner_id = resolve_owner_id(owner)
    try:
        source_object = SourceObject.objects.for_owner(owner_id).get(digest=digest)
    except SourceObject.DoesNotExist:
        return DispositionOutcome(
            disposition=Disposition.REJECTED,
            rule="P6",
            reason_code=REASON_NOTHING_COMMITTED,
            digest=digest,
            owner_id=owner_id,
            created_original=False,
            created_activity=False,
            detail="no original is committed for these bytes; the submission may be sent",
        )

    disposition, activity, quarantine = _classify_existing_original(
        owner_id, source_object
    )
    if store is not None:
        store.verify(owner_id, digest)

    return DispositionOutcome(
        disposition=disposition,
        rule="P2" if disposition is Disposition.DUPLICATE_OF_QUARANTINED else "P1",
        reason_code=(
            REASON_DUPLICATE_OF_QUARANTINED
            if disposition is Disposition.DUPLICATE_OF_QUARANTINED
            else REASON_DUPLICATE_OF_EXISTING
        ),
        digest=digest,
        owner_id=owner_id,
        created_original=False,
        created_activity=False,
        source_object=source_object,
        referenced_source_object=source_object,
        activity=activity,
        quarantine=quarantine,
        detail="resolved by lookup after an ambiguous outcome; nothing was resubmitted",
    )


def describe_reference(owner: Any, digest: str) -> str:
    """P7: report a referenced original that has been superseded or deleted.

    Nothing is resurrected and no cross-owner existence is disclosed; the
    wording is identical whether the original is missing or belongs to somebody
    else (D04 unavailable-evidence semantics).
    """

    owner_id = resolve_owner_id(owner)
    try:
        source_object = SourceObject.objects.for_owner(owner_id).get(digest=digest)
    except SourceObject.DoesNotExist:
        return REASON_REFERENCE_UNAVAILABLE
    if source_object.deleted_at is not None or (
        source_object.retention_state != "account_lifetime"
    ):
        return REASON_REFERENCE_UNAVAILABLE
    return "available"


# --------------------------------------------------------------------------
# Exclusion from normal history and from snapshots
# --------------------------------------------------------------------------


def history(owner: Any) -> Any:
    """Normal history: this owner's accepted, non-conflicting sessions.

    A quarantined candidate is absent by construction, not by a filter the caller
    might forget. There is deliberately no ``latest()`` convenience: history is
    append-only and queried, and a mutable "current value" pointer is a defect
    under the binding architectural condition.
    """

    owner_id = resolve_owner_id(owner)
    return (
        Session.objects.for_owner(owner_id)
        .filter(activity__disposition=Activity.PUBLISHED)
        .select_related("activity", "activity__source_object")
        .order_by("session_start_utc", "session_index", "pk")
    )


def excluded_candidates(owner: Any) -> Any:
    """Every quarantined candidate of this owner, whatever its conflict group.

    These are presented in a separate conflicts area, never inside the activity
    list, and are never counted, totalled or date-scoped (section 9).
    """

    owner_id = resolve_owner_id(owner)
    return (
        Session.objects.for_owner(owner_id)
        .filter(activity__disposition=Activity.QUARANTINED)
        .select_related("activity", "activity__source_object")
        .order_by("session_start_utc", "session_index", "pk")
    )


def open_conflicts(owner: Any) -> Any:
    """Unresolved quarantine records of this owner."""

    owner_id = resolve_owner_id(owner)
    return (
        Quarantine.objects.for_owner(owner_id)
        .filter(state=Quarantine.STATE_QUARANTINED)
        .order_by("pk")
    )


def build_snapshot_scope(
    owner: Any,
    *,
    scope_kind: str,
    scope_start_utc: datetime,
    scope_end_utc: datetime,
    policy_version: str,
    mapping_reference: str,
    preparation_version: str,
) -> Snapshot:
    """Build an immutable prepared scope that excludes unresolved candidates.

    Date scopes are half-open ``[start, end)`` (D02). A quarantined candidate
    inside the window is counted in ``excluded_count`` and named in
    ``exclusions``, so its absence is visible and auditable rather than silent.
    """

    owner_id = resolve_owner_id(owner)
    if scope_start_utc.tzinfo is None or scope_end_utc.tzinfo is None:
        raise ValueError("scope bounds must be aware UTC datetimes")
    if scope_end_utc <= scope_start_utc:
        raise ValueError("scope bounds must be a non-empty half-open range")

    window = dict(session_start_utc__gte=scope_start_utc, session_start_utc__lt=scope_end_utc)

    included = list(
        Session.objects.for_owner(owner_id)
        .filter(activity__disposition=Activity.PUBLISHED, **window)
        .select_related("activity", "activity__source_object")
        .order_by("session_start_utc", "session_index", "pk")
    )
    excluded = list(
        Session.objects.for_owner(owner_id)
        .filter(activity__disposition=Activity.QUARANTINED, **window)
        .select_related("activity", "activity__source_object")
        .order_by("session_start_utc", "session_index", "pk")
    )

    canonical = {
        "scope_kind": scope_kind,
        "scope_start_utc": scope_start_utc.isoformat(),
        "scope_end_utc": scope_end_utc.isoformat(),
        "included": [
            {
                "activity": str(item.activity_id),
                "session_index": item.session_index,
                "source_digest": item.activity.source_object.digest,
                "start_epoch_seconds": int(item.session_start_utc.timestamp()),
                "elapsed_duration_ms": item.elapsed_duration_seconds,
            }
            for item in included
        ],
    }
    canonical_text = json.dumps(canonical, sort_keys=True, separators=(",", ":"))

    return Snapshot.objects.create(
        owner_id=owner_id,
        scope_kind=scope_kind,
        scope_start_utc=scope_start_utc,
        scope_end_utc=scope_end_utc,
        included_activity_ids=[str(item.activity_id) for item in included],
        included_digests=[item.activity.source_object.digest for item in included],
        included_count=len(included),
        excluded_count=len(excluded),
        exclusions=[
            {
                "activity": str(item.activity_id),
                "source_digest": item.activity.source_object.digest,
                "reason": Quarantine.REASON_LOGICAL_TUPLE_CONFLICT,
                "excluded": "unresolved quarantine candidate",
            }
            for item in excluded
        ],
        snapshot_digest=sha256_digest(canonical_text.encode("utf-8")),
        canonical_payload=canonical_text,
        contract_version=CONTRACT_VERSION,
        preparation_version=preparation_version,
        policy_version=policy_version,
        mapping_reference=mapping_reference,
    )


# --------------------------------------------------------------------------
# Section 9 -- presentation vocabulary
# --------------------------------------------------------------------------

#: Wording that would imply a merge, an automatic overwrite, or a certainty the
#: system does not have. `outcome_text` is checked against this list.
PROHIBITED_CONFLICT_WORDING: tuple[str, ...] = (
    "merged",
    "replaced automatically",
    "overwritten",
    "duplicate activity",
    "double counted",
    "definitely the same",
    "certainly the same",
    "automatically merged",
)


def outcome_text(
    outcome: DispositionOutcome, *, submitted_file_name: str = "upload.bin"
) -> str:
    """The required wording for one disposition (section 9).

    Three distinct textual states, never merged into one treatment, and the
    conflict text says the candidate *may* be the same activity because the
    tuple is a heuristic and asserting identity would be an unsupported claim.
    """

    if outcome.disposition is Disposition.ACCEPTED:
        return "Accepted. This file is in your activity history."

    if outcome.disposition in (
        Disposition.DUPLICATE_OF_EXISTING,
        Disposition.DUPLICATE_OF_QUARANTINED,
    ):
        return (
            "This file references an activity you already have. The original you "
            f"submitted as {submitted_file_name} is kept unchanged, and your history "
            "still contains it once. This reference is not a further activity: it is "
            "not counted again in any total, total-to-date figure or date range. Open "
            "the activity it references to see it."
        )

    return (
        "An unresolved possible conflict needs your choice. The file you submitted "
        f"as {submitted_file_name} may be the same activity as one you already "
        "have: the sport, the start time and the elapsed duration are exactly the "
        "same, but the file contents differ, so the system will not decide for you. "
        "Choose one of three options. Keep the existing activity, and keep this file "
        "as a reference only. Replace the existing activity with an auditable "
        "supersession, keeping the earlier original and its history intact. Or keep "
        "both activities, which records that you chose to keep them. Until you "
        "choose, this candidate is excluded from your history totals, your training "
        "volume and every skill snapshot."
    )


__all__ = [
    "Disposition",
    "DispositionOutcome",
    "LogicalTuple",
    "REJECTION_BOUNDARY",
    "SessionFacts",
    "SPORT_CODES",
    "TOLERANCE_PARAMETER_TOKENS",
    "TUPLE_COMPONENTS",
    "assert_no_outcome_fields",
    "assert_no_tolerance_parameters",
    "build_snapshot_scope",
    "canonical_sport_code",
    "describe_reference",
    "excluded_candidates",
    "find_exact_tuple_match",
    "find_exact_tuple_matches",
    "history",
    "ingest",
    "open_conflicts",
    "outcome_text",
    "resolve_uncertain",
    "sport_name",
    "tolerance_parameters",
    "tuple_group_key",
]
