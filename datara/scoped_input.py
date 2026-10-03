"""Versioned, scoped skill input over already accepted and prepared records.

TK21 -- CUS03; SR07, SR28, SR34; FEAT21; WP03. Oracles TC05, TC20, TC23.
Work package 1 contract conformance: ``docs/p0-design/implementation-contracts.md``
(contract rules 2, 3, 6; unit 3 ``TK04 / WP03``).

WHAT A SKILL INPUT IS, AND WHAT IT IS NOT
-----------------------------------------
It **is** a versioned, scoped selection of records that are already accepted and
prepared, referenced by their canonical identity. It is **not** a raw upload,
and it is **not** a model prompt. Three consequences are enforced in code:

* it references *prepared* records, so a value in it is a normalized value with a
  recorded digest, not a re-read of bytes;
* it carries no provider, credential or model-instruction content, because the
  envelope is built before any model is selected and must be identical whichever
  connection later reads it (contract rule 4, SR28);
* it contains no outcome of executing a skill against a model. **A skill input
  is not a result.** Nothing in this module names, stores or implies one, and
  ``datara.db.find_forbidden_schema_entities`` machine-checks the schema this
  module writes to.

THE SCOPE CONTRACT -- EXACTLY WHAT A SCOPE MAY AND MAY NOT CONTAIN
------------------------------------------------------------------
Stated as data, so a reviewer can check the code against the sentence instead of
against a comment:

**A scope MAY contain** only

* a stated :class:`ActivityScope`: a scope kind, a stated half-open time window
  ``[start_utc, end_utc)`` in canonical UTC text, an explicit sport narrowing
  (``None`` meaning "no sport narrowing", which is distinct from an empty set),
  a hard activity capacity, and the method versions it selects;
* records whose canonical identity is already a prepared normalization digest;
* those records' **declared** fields, plus the two automatic scope-member
  lineage fields (:data:`HEADER_CANONICAL_IDENTITY`,
  :data:`HEADER_SOURCE_DIGEST`);
* the recorded absence explanation of any declared field with no value.

**A scope MAY NOT contain**

* a quarantined candidate, in any state, for any reason -- an unresolved
  candidate is not data and is not selected (:data:`EXCLUDED_QUARANTINED`);
* a record whose import disposition is not ``published``;
* a record outside the stated window, of an unselected sport, or prepared under
  a different policy, mapping reference or preparation version;
* a field the skill did not declare, an out-of-scope record, a record beyond the
  stated capacity, or a silent truncation to fit;
* raw source bytes, a credential, a provider or model identifier, a prompt, a
  recommendation, or any other value matching
  :data:`PROHIBITED_PAYLOAD_TOKENS` -- checked by :func:`assert_no_prohibited_content`.

WHY QUARANTINE IS AN *EXISTING* MECHANISM, NOT A NEW RULE
---------------------------------------------------------
This module does not re-derive what a quarantined candidate is. It consumes the
two places the merged schema already expresses it: ``Activity.disposition`` and
the ``datara.models.Quarantine`` record with ``state='quarantined'``. Both are
read by :meth:`MilestoneAInputStore.scope_candidates` and both set the same
``ScopedRecord.quarantined`` flag. The exclusion is then recorded through the
existing mechanism -- :class:`datara.normalization.ExcludedActivity` reason codes
persisted into ``Snapshot.exclusions`` -- not through a new vocabulary invented
here.

IMMUTABILITY, AND WHY A NEW VERSION IS A NEW ROW
------------------------------------------------
A version's identity **is** the digest of its canonical payload. Two
preparations of the same scope over the same accepted records produce the same
payload and therefore the same identity; a different field selection, window or
policy produces a different identity. ``append_version`` only ever creates; the
class has no ``update``/``overwrite``/``delete`` method, the test suite asserts
that, and a repeat append of an identical version returns the existing row
instead of writing a second one. There is no "latest" accessor on this store, and
none may be added: the founder's constraint is that history is append-only and
*queried*, never "latest".

WHY PERSISTENCE IS BEHIND A NARROW INTERFACE
---------------------------------------------
The Architect is concurrently widening ``SR32`` and may change the ``Import`` /
P1 model shape. The pure half of this module -- :class:`ActivityScope`,
:class:`InputFieldSpec`, :class:`ScopedRecord`, :func:`prepare_scoped_input` --
imports no Django at all, and the persistence half is reached only through the
:class:`VersionedInputStore` protocol. A schema change therefore lands in
:class:`MilestoneAInputStore` and in nothing else. :meth:`MilestoneAInputStore.
schema_binding` names, in one place, every field of the merged schema this module
depends on, so a reviewer can see the coupling surface without reading the body.

DETERMINISM
-----------
Pure and model-free: no clock, no randomness, no environment lookup, no network,
no model call. Every collection in the payload is sorted by an explicit key, so
the same scope over the same accepted records is byte-identical across two
preparations and across two processes with different ``PYTHONHASHSEED``.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from datara import NORMALIZER_VERSION
from datara.canonical import (
    CANONICAL_DURATION_UNIT,
    LogicalIdentity,
    canonical_sport_code,
    require_elapsed_duration_ms,
    sport_name,
    start_epoch_seconds_from_datetime,
    start_epoch_seconds_from_utc_text,
)
from datara.normalization import (
    NormalizationPolicy,
    canonical_json,
    digest_matches,
    sha256_digest,
)
from datara.provenance import (
    MAX_ROW_REFERENCE_LENGTH,
    VALUE_CLASS_QUALITY_WARNING,
    VALUE_CLASS_SCOPE_MEMBER,
    VALUE_CLASS_SOURCE_OBSERVATION,
    AbsentObservation,
    ProvenanceError,
    ProvenanceLedger,
    ProvenanceIncomplete,
    ScopedField,
    build_display,
    build_ledger,
    require_canonical_identity,
)

# ---------------------------------------------------------------------------
# Contract identity
# ---------------------------------------------------------------------------

#: Contract identity of the scoped-input envelope. Any change to the payload
#: shape or to a reason-code vocabulary is a breaking change and must bump it.
SCOPED_INPUT_CONTRACT_VERSION = "datara-milestone-a/scoped-input/1"

#: Identity of this implementation. Bumping it changes every scoped-input digest.
SCOPED_INPUT_VERSION = "tk21-scoped-input/1"

#: The scope window is half-open. Stated once, in the payload, so a reader never
#: has to guess whether an activity exactly on the end instant is in scope.
SCOPE_WINDOW = "[start_utc,end_utc)"

#: The two lineage fields every scoped record carries without being declared.
#: They are the record's own canonical identity and its source bytes' digest, so
#: a scope is self-describing: every value can be attributed even if the
#: declaring skill asked for no fields at all.
HEADER_CANONICAL_IDENTITY = "canonical_identity"
HEADER_SOURCE_DIGEST = "source_digest"
HEADER_FIELDS: tuple[str, ...] = (HEADER_CANONICAL_IDENTITY, HEADER_SOURCE_DIGEST)

#: ``datara.models.Activity.DISPOSITION_CHOICES``, restated as data so the pure
#: layer imports no Django. :meth:`MilestoneAInputStore.schema_binding` asserts
#: these equal the model's own constants, so the two cannot drift.
DISPOSITION_PUBLISHED = "published"
DISPOSITION_QUARANTINED = "quarantined"
SCOPABLE_DISPOSITIONS: frozenset[str] = frozenset({DISPOSITION_PUBLISHED})

# ---------------------------------------------------------------------------
# Exclusion reason codes
# ---------------------------------------------------------------------------

#: Frozen vocabulary. Each code names *why* a record is not in the scope, in the
#: precedence order applied by :func:`prepare_scoped_input`. An exclusion with a
#: code outside this set is a defect, not a new reason.
EXCLUDED_QUARANTINED = "quarantined_candidate"
EXCLUDED_DISPOSITION = "disposition_not_published"
EXCLUDED_OUTSIDE_WINDOW = "outside_scope_window"
EXCLUDED_SPORT = "sport_not_selected"
EXCLUDED_POLICY_VERSION = "policy_version_not_selected"
EXCLUDED_MAPPING_REFERENCE = "mapping_reference_not_selected"
EXCLUDED_PREPARATION_VERSION = "preparation_version_not_selected"
EXCLUDED_REQUIRED_FIELD_ABSENT = "required_field_absent"
EXCLUDED_DUPLICATE_IDENTITY = "duplicate_canonical_identity"
EXCLUDED_CAPACITY = "scope_capacity_exceeded"

EXCLUSION_REASONS: tuple[str, ...] = (
    EXCLUDED_QUARANTINED,
    EXCLUDED_DISPOSITION,
    EXCLUDED_OUTSIDE_WINDOW,
    EXCLUDED_SPORT,
    EXCLUDED_POLICY_VERSION,
    EXCLUDED_MAPPING_REFERENCE,
    EXCLUDED_PREPARATION_VERSION,
    EXCLUDED_REQUIRED_FIELD_ABSENT,
    EXCLUDED_DUPLICATE_IDENTITY,
    EXCLUDED_CAPACITY,
)
EXCLUSION_REASON_SET: frozenset[str] = frozenset(EXCLUSION_REASONS)

#: The precedence a candidate is judged by, in order. Quarantine is first and
#: unconditional: no other reason may be reported in place of "this candidate is
#: quarantined", because a scope must never make a quarantined candidate look
#: like a merely out-of-window record.
EXCLUSION_PRECEDENCE: tuple[str, ...] = (
    EXCLUDED_QUARANTINED,
    EXCLUDED_DISPOSITION,
    EXCLUDED_OUTSIDE_WINDOW,
    EXCLUDED_SPORT,
    EXCLUDED_POLICY_VERSION,
    EXCLUDED_MAPPING_REFERENCE,
    EXCLUDED_PREPARATION_VERSION,
    EXCLUDED_REQUIRED_FIELD_ABSENT,
    EXCLUDED_DUPLICATE_IDENTITY,
)

# ---------------------------------------------------------------------------
# Prohibited content (TC05 / TC20 negatives)
# ---------------------------------------------------------------------------

#: Key tokens that may not appear anywhere in a scoped-input payload. Matched
#: case-insensitively against every key at every depth, and against the key's
#: underscore-free form, so ``api_key``, ``apiKey`` and ``API-KEY`` are all
#: caught. The list is a prohibition on *content classes*, not on a fixed
#: key list: a payload that grows a new credential-shaped key is refused.
PROHIBITED_PAYLOAD_TOKENS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "completion",
    "credential",
    "file_bytes",
    "model",
    "password",
    "prompt",
    "provider",
    "raw_bytes",
    "recommendation",
    "response",
    "secret",
    "token",
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ScopedInputError(Exception):
    """Base for every scoped-input failure."""


class ScopeContractError(ScopedInputError):
    """The stated scope is not a valid, bounded scope."""


class ScopeCapacityExceeded(ScopedInputError):
    """The scope's stated capacity cannot hold the selected records."""


class ProhibitedScopeContent(ScopedInputError):
    """The payload carries a class of content a scope may not contain."""


class QuarantinedCandidateInScope(ScopedInputError):
    """A quarantined candidate reached the selected set.

    Unreachable through :func:`prepare_scoped_input`, which filters first. It
    exists because a version is also constructible by hand, and the property
    "no quarantined candidate is in any scope" must hold for *any* construction,
    not only for the one that filters correctly.
    """


class UndeclaredFieldInRecord(ScopedInputError):
    """A record offered a field the skill did not declare."""


class DeclaredFieldMissing(ScopedInputError):
    """A record did not carry a field the skill declared."""


class AmbiguousCanonicalIdentity(ScopedInputError):
    """A canonical identity resolved to more than one stored record."""


# ---------------------------------------------------------------------------
# The scope
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ActivityScope:
    """A defined set of activities over a stated time window.

    Every field has no default, on purpose. An unbounded scope is not a scope:
    it cannot be prepared deterministically, it cannot be reviewed by the user
    before a value is produced from it, and its payload would grow with the
    owner's whole history. The caller must therefore state the window, the
    capacity and the method versions rather than inheriting them.
    """

    kind: str
    start_utc: str
    end_utc: str
    sports: frozenset[str] | None
    max_activities: int
    preparation_version: str
    policy_version: str
    mapping_reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ScopeContractError("a scope must name its kind")
        if len(self.kind) > 64:
            raise ScopeContractError("scope kind exceeds 64 characters")
        self._require_instant(self.start_utc, origin="ActivityScope.start_utc")
        self._require_instant(self.end_utc, origin="ActivityScope.end_utc")
        start = start_epoch_seconds_from_utc_text(self.start_utc, origin="ActivityScope.start_utc")
        end = start_epoch_seconds_from_utc_text(self.end_utc, origin="ActivityScope.end_utc")
        if start >= end:
            raise ScopeContractError(
                f"scope window start {self.start_utc!r} must be strictly before end "
                f"{self.end_utc!r}; an empty or reversed window cannot define a set"
            )
        if self.sports is not None:
            if not isinstance(self.sports, frozenset):
                raise ScopeContractError(
                    "scope sports must be a frozenset, or None for no sport narrowing; "
                    f"got {type(self.sports).__name__}"
                )
            if not self.sports:
                # Distinct from None on purpose: None means "no narrowing", an
                # empty set means "nothing at all", which cannot be a scope.
                raise ScopeContractError(
                    "an empty sport set selects nothing; pass None to mean no sport narrowing"
                )
            for name in self.sports:
                # Validated through the single canonical definition, so an
                # unsupported sport is a loud refusal rather than a silent filter
                # that matches nothing.
                canonical_sport_code(name, origin=f"ActivityScope.sports[{name!r}]")
        if isinstance(self.max_activities, bool) or not isinstance(self.max_activities, int):
            raise ScopeContractError(
                f"max_activities must be an int, got {type(self.max_activities).__name__}"
            )
        if self.max_activities < 1:
            raise ScopeContractError("max_activities must be at least 1; a capacity of 0 selects nothing")
        for name in ("preparation_version", "policy_version", "mapping_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ScopeContractError(f"a scope must state its {name}")
        if len(self.mapping_reference) > 128:
            raise ScopeContractError("mapping_reference exceeds 128 characters")

    @staticmethod
    def _require_instant(value: Any, *, origin: str) -> None:
        if not isinstance(value, str):
            raise ScopeContractError(f"{origin} must be canonical UTC text, got {type(value).__name__}")
        # Raises on a naive or sub-second instant: a start that cannot be
        # compared exactly must not become a window bound.
        start_epoch_seconds_from_utc_text(value, origin=origin)

    @property
    def start_epoch_seconds(self) -> int:
        return start_epoch_seconds_from_utc_text(self.start_utc, origin="ActivityScope.start_utc")

    @property
    def end_epoch_seconds(self) -> int:
        return start_epoch_seconds_from_utc_text(self.end_utc, origin="ActivityScope.end_utc")

    def contains_start(self, start_epoch_seconds: int) -> bool:
        """Half-open containment: start is included, end is not."""

        return self.start_epoch_seconds <= start_epoch_seconds < self.end_epoch_seconds

    def selects_sport(self, sport_code: int) -> bool:
        if self.sports is None:
            return True
        return sport_name(sport_code, origin="ActivityScope.selects_sport") in self.sports

    def as_record(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "start_utc": self.start_utc,
            "end_utc": self.end_utc,
            "window": SCOPE_WINDOW,
            "sports": None if self.sports is None else sorted(self.sports),
            "max_activities": self.max_activities,
            "preparation_version": self.preparation_version,
            "policy_version": self.policy_version,
            "mapping_reference": self.mapping_reference,
        }


# ---------------------------------------------------------------------------
# Declaration and candidates
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InputFieldSpec:
    """One field the skill declared it needs.

    Milestone A has no ``SkillDefinition`` entity -- it is an excluded entity
    under the binding architectural condition -- so the declaration is plain
    data supplied by the caller rather than a catalogue row. The consequence is
    that "only the selected dataset" is enforced by requiring the record's field
    set to equal exactly the declared set plus the two header fields: an
    undeclared field is a refusal, not an inclusion.
    """

    field_name: str
    value_class: str
    required: bool

    def __post_init__(self) -> None:
        # ScopedField performs the full validation (name pattern, value-class
        # vocabulary, Milestone A availability). Constructing one here means the
        # declaration is validated by exactly the same code that validates the
        # value, so the two cannot disagree about what a field may be.
        ScopedField(
            field_name=self.field_name,
            value_class=self.value_class,
            value_canonical="declared",
            preparation_version="declaration",
            mapping_reference="declaration",
        )
        if self.field_name in HEADER_FIELDS:
            raise ScopeContractError(
                f"{self.field_name!r} is an automatic scope-member field and is always "
                "present; it may not be declared"
            )
        if not isinstance(self.required, bool):
            raise ScopeContractError(
                f"InputFieldSpec.required must be a bool, got {type(self.required).__name__}"
            )

    def as_record(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "value_class": self.value_class,
            "required": self.required,
        }


def require_declared(
    field_specs: Sequence[InputFieldSpec],
) -> tuple[InputFieldSpec, ...]:
    """Validate a declaration and return it in canonical (sorted) order.

    Sorted rather than caller-ordered so two callers declaring the same fields
    in different orders produce the same version -- declaration order is not
    information.
    """

    if not field_specs:
        raise ScopeContractError(
            "a scoped input must declare at least one field; an empty declaration "
            "would produce an envelope that carries only record identity and no data"
        )
    seen: set[str] = set()
    for spec in field_specs:
        if spec.field_name in seen:
            raise ScopeContractError(f"field {spec.field_name!r} is declared twice")
        seen.add(spec.field_name)
    return tuple(sorted(field_specs, key=lambda s: s.field_name))


@dataclass(frozen=True)
class ScopedRecord:
    """One prepared record offered to a scope.

    The record's identity is its normalization digest, never a generated row id:
    re-preparing the same accepted bytes yields the same canonical identity, and
    that is what makes a version's bytes stable across two preparations.
    """

    canonical_identity: str
    source_digest: str
    logical_tuple: LogicalIdentity
    preparation_version: str
    policy_version: str
    mapping_reference: str
    disposition: str
    quarantined: bool
    fields: tuple[ScopedField, ...]

    def __post_init__(self) -> None:
        require_canonical_identity(self.canonical_identity, origin="ScopedRecord")
        if not isinstance(self.source_digest, str) or not digest_matches(self.source_digest):
            raise ScopedInputError(
                f"ScopedRecord {self.canonical_identity}: source digest must be 'sha256:' + 64 "
                f"lowercase hex, got {self.source_digest!r}"
            )
        if not isinstance(self.logical_tuple, LogicalIdentity):
            raise ScopedInputError(
                "ScopedRecord.logical_tuple must be a datara.canonical.LogicalIdentity, so the "
                "record is compared with the same exact integer key the conflict machinery "
                f"uses; got {type(self.logical_tuple).__name__}"
            )
        for name in ("preparation_version", "policy_version", "mapping_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ScopedInputError(
                    f"ScopedRecord {self.canonical_identity}: {name} is required"
                )
        if not isinstance(self.disposition, str) or not self.disposition:
            raise ScopedInputError(
                f"ScopedRecord {self.canonical_identity}: an import disposition is required"
            )
        if not isinstance(self.quarantined, bool):
            raise ScopedInputError(
                f"ScopedRecord {self.canonical_identity}: quarantined must be a bool"
            )
        ordered = tuple(sorted(self.fields, key=lambda f: f.field_name))
        names = [item.field_name for item in ordered]
        if len(set(names)) != len(names):
            raise ScopedInputError(
                f"ScopedRecord {self.canonical_identity}: a field is present twice"
            )
        object.__setattr__(self, "fields", ordered)

    def field(self, field_name: str) -> ScopedField:
        for item in self.fields:
            if item.field_name == field_name:
                return item
        raise DeclaredFieldMissing(
            f"ScopedRecord {self.canonical_identity} carries no field {field_name!r}"
        )

    def as_record(self) -> dict[str, Any]:
        # ``disposition`` and ``quarantined`` are part of the payload, not
        # incidental metadata: a reader has to be able to see *why* each record
        # was scopable, and the round trip has to re-establish the quarantine
        # postcondition from the stored bytes rather than trusting the row.
        return {
            "canonical_identity": self.canonical_identity,
            "source_digest": self.source_digest,
            "logical_tuple": self.logical_tuple.as_dict(),
            "preparation_version": self.preparation_version,
            "policy_version": self.policy_version,
            "mapping_reference": self.mapping_reference,
            "disposition": self.disposition,
            "quarantined": self.quarantined,
            "fields": {item.field_name: item.as_record() for item in self.fields},
        }


@dataclass(frozen=True)
class ScopedExclusion:
    """One record kept out of the scope, with the reason it was kept out.

    ``activity_ref`` is the record's canonical identity rather than a generated
    row id, for the same reason the payload references records by canonical
    identity: an exclusion list that named row ids would differ between two
    preparations of the same scope, and the snapshot's bytes would stop being
    reproducible. ``datara.db.record_snapshot`` stores it under its own
    ``activity_ref`` key, which is the existing snapshot exclusion contract.
    """

    canonical_identity: str
    reason_code: str

    def __post_init__(self) -> None:
        require_canonical_identity(self.canonical_identity, origin="ScopedExclusion")
        if self.reason_code not in EXCLUSION_REASON_SET:
            raise ScopedInputError(
                f"unknown scope exclusion reason {self.reason_code!r}; the frozen vocabulary is "
                f"{list(EXCLUSION_REASONS)}"
            )

    @property
    def activity_ref(self) -> str:
        return self.canonical_identity

    def as_record(self) -> dict[str, Any]:
        return {"canonical_identity": self.canonical_identity, "reason_code": self.reason_code}


# ---------------------------------------------------------------------------
# The versioned value
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScopedInputVersion:
    """One immutable version of a scoped skill input. A value, not a row class.

    Frozen, so a version cannot be edited in place. A change of window, field
    selection, policy or record set produces a *different* value with a different
    ``input_digest``, which is a new version; the prior value is untouched. The
    attribute names ``scope_kind``, ``scope_start_utc``, ``scope_end_utc``,
    ``included_digests``, ``included_count``, ``excluded_count``, ``exclusions``,
    ``snapshot_digest``, ``canonical_payload``, ``preparation_version``,
    ``policy_version`` and ``mapping_reference`` are the surface
    ``datara.db.record_snapshot`` already reads, so TK21 persists through the
    existing owner-scoped store instead of adding a schema.
    """

    contract_version: str
    scoped_input_version: str
    scope: ActivityScope
    policy: NormalizationPolicy
    records: tuple[ScopedRecord, ...]
    exclusions: tuple[ScopedExclusion, ...]
    declared: tuple[InputFieldSpec, ...]
    canonical_payload: str
    input_digest: str
    ledger: ProvenanceLedger

    def __post_init__(self) -> None:
        if self.contract_version != SCOPED_INPUT_CONTRACT_VERSION:
            raise ScopedInputError(
                f"scoped input contract version {self.contract_version!r} is not "
                f"{SCOPED_INPUT_CONTRACT_VERSION!r}"
            )
        if self.input_digest != sha256_digest(self.canonical_payload):
            raise ScopedInputError(
                "the version digest does not match its own canonical payload; a version whose "
                "digest is not the digest of its content is not a version"
            )
        identities = [record.canonical_identity for record in self.records]
        if len(set(identities)) != len(identities):
            raise ScopedInputError("a scope cannot include the same canonical identity twice")
        if len(self.records) > self.scope.max_activities:
            raise ScopeCapacityExceeded(
                f"the version holds {len(self.records)} records but its scope states a capacity "
                f"of {self.scope.max_activities}"
            )
        # The structural quarantine postcondition, enforced on *any* construction
        # rather than only on the path that filters: an unresolved candidate is
        # not data and is in no scope.
        for record in self.records:
            if record.quarantined:
                raise QuarantinedCandidateInScope(
                    f"record {record.canonical_identity} is a quarantined candidate and cannot be "
                    "part of a scope"
                )
            if record.disposition not in SCOPABLE_DISPOSITIONS:
                raise QuarantinedCandidateInScope(
                    f"record {record.canonical_identity} has import disposition "
                    f"{record.disposition!r}, which is not a scopable disposition"
                )
        self._require_exact_declaration()
        # Executed, not assumed: every declared field of every included record
        # must resolve. A field with no provenance source fails the version.
        self.ledger.require_complete(self.declared_field_paths())

    def _require_exact_declaration(self) -> None:
        expected = set(HEADER_FIELDS) | {spec.field_name for spec in self.declared}
        for record in self.records:
            present = {item.field_name for item in record.fields}
            undeclared = sorted(present - expected)
            if undeclared:
                raise UndeclaredFieldInRecord(
                    f"record {record.canonical_identity} offers undeclared field(s) "
                    f"{undeclared}; a scope may contain only the selected fields"
                )
            missing = sorted(expected - present)
            if missing:
                raise DeclaredFieldMissing(
                    f"record {record.canonical_identity} is missing declared field(s) {missing}"
                )

    # -- the surface datara.db.record_snapshot reads -------------------------

    @property
    def scope_kind(self) -> str:
        return self.scope.kind

    @property
    def scope_start_utc(self) -> str:
        return self.scope.start_utc

    @property
    def scope_end_utc(self) -> str:
        return self.scope.end_utc

    @property
    def included_digests(self) -> tuple[str, ...]:
        return tuple(sorted(record.canonical_identity for record in self.records))

    @property
    def included_count(self) -> int:
        return len(self.records)

    @property
    def excluded_count(self) -> int:
        return len(self.exclusions)

    @property
    def preparation_version(self) -> str:
        return self.scope.preparation_version

    @property
    def policy_version(self) -> str:
        return self.scope.policy_version

    @property
    def mapping_reference(self) -> str:
        return self.scope.mapping_reference

    #: ``datara.db.record_snapshot`` stores the value under this name. It is the
    #: scope's identity: the same canonical bytes, so two preparations of the
    #: same scope share it.
    @property
    def snapshot_digest(self) -> str:
        return self.input_digest

    # -- derived views -------------------------------------------------------

    def declared_field_paths(self) -> tuple[str, ...]:
        """Every ``(record, declared field)`` path, in canonical order.

        This is the set the *declaration* is accountable for, and it is what
        :meth:`ProvenanceLedger.require_complete` is called with.
        """

        paths: list[str] = []
        for record in self.records:
            for spec in self.declared:
                paths.append(f"{record.canonical_identity}.{spec.field_name}")
        return tuple(sorted(paths))

    def all_field_paths(self) -> tuple[str, ...]:
        """Every field path the version carries, declared plus the header fields.

        This is the set the *persisted provenance rows* are accountable for. It
        is a superset of :meth:`declared_field_paths`, because the two automatic
        scope-member lineage fields are written as provenance rows too.
        """

        return self.ledger.field_paths()

    def resolve_provenance(self, canonical_identity: str, field_name: str) -> Any:
        return self.ledger.resolve(f"{canonical_identity}.{field_name}")

    def provenance_display(self) -> tuple[Any, ...]:
        return build_display(self.ledger)

    def version_of_record(self, canonical_identity: str) -> str:
        return next(
            record.canonical_identity
            for record in self.records
            if record.canonical_identity == canonical_identity
        )

    def as_record(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "scoped_input_version": self.scoped_input_version,
            "input_digest": self.input_digest,
            "scope": self.scope.as_record(),
            "record_count": self.included_count,
            "exclusions": [item.as_record() for item in self.exclusions],
            "declared": [spec.as_record() for spec in self.declared],
        }

    # -- round trip ----------------------------------------------------------

    @classmethod
    def from_canonical_payload(cls, text: str) -> "ScopedInputVersion":
        """Rebuild the value from its persisted canonical payload.

        This is how a version is read back rather than recomputed, and it is also
        an integrity check: the text must be *canonical* (re-serialising the
        parsed value must reproduce it exactly), and the digest is recomputed
        from that text. A payload edited in the database therefore fails to
        round-trip instead of being read as if it were the version it claims.
        """

        import json  # local import: keeps module import cost trivial

        try:
            parsed = json.loads(text)
        except ValueError as exc:
            raise ScopedInputError("the stored canonical payload is not JSON") from exc
        if not isinstance(parsed, dict):
            raise ScopedInputError("the stored canonical payload is not a JSON object")
        if canonical_json(parsed) != text:
            raise ScopedInputError(
                "the stored canonical payload is not in canonical form; a non-canonical "
                "payload cannot be digest-verified and is refused rather than trusted"
            )
        digest = sha256_digest(text)
        if parsed.get("contract_version") != SCOPED_INPUT_CONTRACT_VERSION:
            raise ScopedInputError(
                f"stored payload declares contract version {parsed.get('contract_version')!r}, "
                f"which this build cannot read ({SCOPED_INPUT_CONTRACT_VERSION!r})"
            )
        scope = _scope_from_record(parsed["scope"])
        policy_block = parsed["policy"]
        policy = NormalizationPolicy(
            policy_version=policy_block["policy_version"],
            mapping_reference=policy_block["mapping_reference"],
            supported_sports=frozenset(policy_block["supported_sports"]),
            max_elapsed_duration_seconds=policy_block["max_elapsed_duration_seconds"],
            max_timer_duration_seconds=policy_block["max_timer_duration_seconds"],
            max_distance_value=policy_block["max_distance_value"],
            max_record_sample_count=policy_block["max_record_sample_count"],
            max_gps_point_count=policy_block["max_gps_point_count"],
            max_heart_rate_value=policy_block["max_heart_rate_value"],
        )
        declared = tuple(
            sorted(
                (
                    InputFieldSpec(
                        field_name=item["field_name"],
                        value_class=item["value_class"],
                        required=item["required"],
                    )
                    for item in parsed["declared"]
                ),
                key=lambda s: s.field_name,
            )
        )
        records = tuple(
            sorted((_record_from_record(item) for item in parsed["records"]), key=lambda r: r.canonical_identity)
        )
        exclusions = tuple(
            sorted(
                (
                    ScopedExclusion(
                        canonical_identity=item["canonical_identity"],
                        reason_code=item["reason_code"],
                    )
                    for item in parsed["exclusions"]
                ),
                key=lambda e: (e.canonical_identity, e.reason_code),
            )
        )
        return cls(
            contract_version=parsed["contract_version"],
            scoped_input_version=parsed["scoped_input_version"],
            scope=scope,
            policy=policy,
            records=records,
            exclusions=exclusions,
            declared=declared,
            canonical_payload=text,
            input_digest=digest,
            # The ledger is rebuilt from the payload's own values rather than
            # trusted from a stored digest, so `require_complete` in
            # __post_init__ re-executes the completeness check on read.
            ledger=_ledger_from_payload(records),
        )


def _scope_from_record(block: Mapping[str, Any]) -> ActivityScope:
    sports = block["sports"]
    return ActivityScope(
        kind=block["kind"],
        start_utc=block["start_utc"],
        end_utc=block["end_utc"],
        sports=None if sports is None else frozenset(sports),
        max_activities=block["max_activities"],
        preparation_version=block["preparation_version"],
        policy_version=block["policy_version"],
        mapping_reference=block["mapping_reference"],
    )


def _record_from_record(block: Mapping[str, Any]) -> ScopedRecord:
    tuple_block = block["logical_tuple"]
    identity = LogicalIdentity(
        sport_code=tuple_block["sport_code"],
        start_epoch_seconds=tuple_block["start_epoch_seconds"],
        elapsed_duration_ms=tuple_block["elapsed_duration_ms"],
    )
    fields = []
    for name in sorted(block["fields"]):
        item = block["fields"][name]
        absent_block = item["absent"]
        fields.append(
            ScopedField(
                field_name=item["field_name"],
                value_class=item["value_class"],
                value_canonical=item["value_canonical"],
                preparation_version=item["preparation_version"],
                mapping_reference=item["mapping_reference"],
                absent=None
                if absent_block is None
                else AbsentObservation(
                    code=absent_block["code"],
                    detail=absent_block["detail"],
                    source_field=absent_block["source_field"],
                ),
            )
        )
    return ScopedRecord(
        canonical_identity=block["canonical_identity"],
        source_digest=block["source_digest"],
        logical_tuple=identity,
        preparation_version=block["preparation_version"],
        policy_version=block["policy_version"],
        mapping_reference=block["mapping_reference"],
        disposition=block["disposition"],
        # The payload records a quarantined candidate only ever in the exclusion
        # list. If one appears under `records`, the postcondition must fire
        # rather than the value being trusted.
        quarantined=bool(block["quarantined"]),
        fields=tuple(fields),
    )


def _ledger_from_payload(records: Sequence[ScopedRecord]) -> ProvenanceLedger:
    return build_ledger(
        (record.canonical_identity, record.source_digest, record.fields) for record in records
    )


# ---------------------------------------------------------------------------
# Prohibited content
# ---------------------------------------------------------------------------


def _fold(text: str) -> str:
    return text.replace("-", "").replace("_", "").replace(" ", "").lower()


def assert_no_prohibited_content(payload: Any, *, origin: str = "scoped input payload") -> None:
    """Refuse a payload carrying any prohibited content class.

    Walks every mapping key at every depth. The check is on the *class* of the
    key, matched against a fixed token list plus the class list itself, so a
    payload cannot acquire a credential-shaped, prompt-shaped or
    recommendation-shaped field by being extended. ``bytes`` is refused too: a
    raw-blob value is precisely the "raw upload" a skill input is not, and
    ``canonical_json`` would fail on it later with a much less useful message.
    """

    folded_tokens = tuple(_fold(token) for token in PROHIBITED_PAYLOAD_TOKENS)
    stack: list[tuple[str, Any]] = [(origin, payload)]
    while stack:
        path, node = stack.pop()
        if isinstance(node, bytes):
            raise ProhibitedScopeContent(
                f"{path} carries raw bytes; a scoped input references prepared values, not "
                "an upload"
            )
        if isinstance(node, Mapping):
            for key in node:
                if not isinstance(key, str):
                    raise ProhibitedScopeContent(f"{path} has a non-string key {key!r}")
                folded = _fold(key)
                for token in folded_tokens:
                    if token in folded:
                        raise ProhibitedScopeContent(
                            f"{path}.{key} matches the prohibited content token {token!r}; a "
                            "scope may not contain credentials, provider or model identifiers, "
                            "prompts, recommendations or response-shaped content"
                        )
                stack.append((f"{path}.{key}", node[key]))
        elif isinstance(node, (list, tuple)):
            for index, item in enumerate(node):
                stack.append((f"{path}[{index}]", item))


# ---------------------------------------------------------------------------
# Preparation
# ---------------------------------------------------------------------------


def _exclusion_reason(
    record: ScopedRecord, scope: ActivityScope, declared: Sequence[InputFieldSpec]
) -> str | None:
    """The first matching exclusion reason for ``record``, or ``None`` to include.

    Evaluated strictly in :data:`EXCLUSION_PRECEDENCE` order. Quarantine is first
    and unconditional.
    """

    if record.quarantined:
        return EXCLUDED_QUARANTINED
    if record.disposition not in SCOPABLE_DISPOSITIONS:
        return EXCLUDED_DISPOSITION
    if not scope.contains_start(record.logical_tuple.start_epoch_seconds):
        return EXCLUDED_OUTSIDE_WINDOW
    if not scope.selects_sport(record.logical_tuple.sport_code):
        return EXCLUDED_SPORT
    if record.policy_version != scope.policy_version:
        return EXCLUDED_POLICY_VERSION
    if record.mapping_reference != scope.mapping_reference:
        return EXCLUDED_MAPPING_REFERENCE
    if record.preparation_version != scope.preparation_version:
        return EXCLUDED_PREPARATION_VERSION
    for spec in declared:
        if spec.required and not record.field(spec.field_name).available:
            return EXCLUDED_REQUIRED_FIELD_ABSENT
    return None


def _payload(
    *,
    scope: ActivityScope,
    policy: NormalizationPolicy,
    records: Sequence[ScopedRecord],
    exclusions: Sequence[ScopedExclusion],
    declared: Sequence[InputFieldSpec],
) -> dict[str, Any]:
    """The canonical structure of a scoped input.

    There is deliberately **no parallel ``provenance`` block**. The lineage of a
    value is carried inline: each field record holds its own ``value_class``,
    ``preparation_version`` and ``mapping_reference``, and its record holds the
    ``canonical_identity`` and ``source_digest``. A separate derived index beside
    the values is the structure that drifts -- a value with no matching entry, or
    an entry with no value -- which is the failure this module exists to make
    unrepresentable. The completeness check is therefore executed on the values
    themselves, in :meth:`ScopedInputVersion.__post_init__`.
    """

    return {
        "contract_version": SCOPED_INPUT_CONTRACT_VERSION,
        "scoped_input_version": SCOPED_INPUT_VERSION,
        "preparation_version": scope.preparation_version,
        "normalizer_version": NORMALIZER_VERSION,
        "policy": policy.canonical(),
        "scope": scope.as_record(),
        "declared": [spec.as_record() for spec in declared],
        "records": [record.as_record() for record in records],
        "record_count": len(records),
        "excluded_count": len(exclusions),
        "exclusions": [item.as_record() for item in exclusions],
    }


def prepare_scoped_input(
    *,
    scope: ActivityScope,
    records: Sequence[ScopedRecord],
    field_specs: Sequence[InputFieldSpec],
    policy: NormalizationPolicy,
) -> ScopedInputVersion:
    """Select, bind and version a scope. Pure.

    No clock, no randomness, no environment lookup, no database, no network, no
    model call. Every collection is sorted by an explicit key, so the same scope
    over the same accepted records yields byte-identical output.

    Capacity is applied *after* eligibility and the surplus is reported as an
    explicit exclusion, never as a silent truncation. Which records are dropped
    is a function of the canonical identities, not of the order the caller
    supplied, so the retained set is reproducible.
    """

    declared = require_declared(field_specs)
    if policy.policy_version != scope.policy_version:
        raise ScopeContractError(
            f"the supplied policy is {policy.policy_version!r} but the scope selects "
            f"{scope.policy_version!r}; a version must bind one policy"
        )
    if policy.mapping_reference != scope.mapping_reference:
        raise ScopeContractError(
            f"the supplied policy names mapping reference {policy.mapping_reference!r} but the "
            f"scope selects {scope.mapping_reference!r}"
        )

    # Validate the whole candidate set before selecting anything, so a malformed
    # candidate is a loud refusal rather than a record that is silently dropped
    # for an unrelated reason.
    # A fixed evaluation order. Note precisely what this does and does not buy:
    # every output list is sorted again by canonical identity below, and each
    # candidate's outcome is computed independently, so this sort is *not* what
    # makes the version reproducible -- the output sorts are. What it does fix is
    # the order in which candidates are judged, which keeps the result stable if a
    # future rule ever consults an already-seen candidate. A mutation run recorded
    # in the TK21 contribution report established that this line is *not* itself
    # load-bearing -- removing it alone changes no test outcome -- rather than this
    # comment asserting it.
    ordered = tuple(sorted(records, key=lambda r: r.canonical_identity))

    included: list[ScopedRecord] = []
    exclusions: list[ScopedExclusion] = []
    seen_identities: set[str] = set()
    for record in ordered:
        reason = _exclusion_reason(record, scope, declared)
        if reason is not None:
            exclusions.append(ScopedExclusion(record.canonical_identity, reason))
            continue
        if record.canonical_identity in seen_identities:
            exclusions.append(ScopedExclusion(record.canonical_identity, EXCLUDED_DUPLICATE_IDENTITY))
            continue
        seen_identities.add(record.canonical_identity)
        included.append(record)

    if len(included) > scope.max_activities:
        kept = included[: scope.max_activities]
        dropped = included[scope.max_activities :]
        for record in dropped:
            exclusions.append(ScopedExclusion(record.canonical_identity, EXCLUDED_CAPACITY))
        included = kept

    ordered_exclusions = tuple(
        sorted(exclusions, key=lambda e: (e.canonical_identity, e.reason_code))
    )
    ordered_records = tuple(sorted(included, key=lambda r: r.canonical_identity))
    ledger = _ledger_from_payload(ordered_records)

    block = _payload(
        scope=scope,
        policy=policy,
        records=ordered_records,
        exclusions=ordered_exclusions,
        declared=declared,
    )
    # Scanned as a structure, so a prohibited key is *named* rather than hunted
    # for inside a serialised string.
    assert_no_prohibited_content(json_safe(block))
    text = canonical_json(block)

    return ScopedInputVersion(
        contract_version=SCOPED_INPUT_CONTRACT_VERSION,
        scoped_input_version=SCOPED_INPUT_VERSION,
        scope=scope,
        policy=policy,
        records=ordered_records,
        exclusions=ordered_exclusions,
        declared=declared,
        canonical_payload=text,
        input_digest=sha256_digest(text),
        ledger=ledger,
    )


def json_safe(payload: Any) -> Any:
    """The payload as plain JSON types, for the content scan.

    The scan runs on the structure rather than on the serialised text, so a
    prohibited key is named rather than hunted for inside a string.
    """

    if isinstance(payload, Mapping):
        return {str(key): json_safe(value) for key, value in payload.items()}
    if isinstance(payload, (list, tuple)):
        return [json_safe(item) for item in payload]
    return payload


# ---------------------------------------------------------------------------
# The narrow persistence interface
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VersionedInputHandle:
    """A reference to a persisted version row, plus whether this call created it.

    ``version_ref`` is the persisted row's own primary key. It is a *reference*,
    not a pointer to a newest value: the store exposes no way to ask for the
    latest, and the founder's constraint is that history is queried, never
    "latest".
    """

    version_ref: str
    input_digest: str
    record_count: int
    excluded_count: int
    created: bool

    def as_record(self) -> dict[str, Any]:
        return {
            "version_ref": self.version_ref,
            "input_digest": self.input_digest,
            "record_count": self.record_count,
            "excluded_count": self.excluded_count,
            "created": self.created,
        }


@runtime_checkable
class VersionedInputStore(Protocol):
    """Everything TK21 needs from persistence, and nothing else.

    This is the seam the Architect's concurrent schema work lands on. A change to
    the ``Import``/P1 model shape or to ``SR32`` is absorbed by the
    implementation; the scope contract, the selection rules, the payload and the
    provenance ledger above are unaffected. The interface is deliberately
    write-once: it has no update, overwrite or delete operation, so "a prior
    version is never mutated in place" is not a convention a caller can bypass.
    """

    def scope_candidates(
        self, scope: ActivityScope, field_specs: Sequence[InputFieldSpec]
    ) -> tuple[ScopedRecord, ...]:
        """Read this owner's prepared records as scope candidates.

        The implementation is the only place that knows the schema, and it is
        responsible for consuming the existing quarantine signals rather than
        re-deriving them.
        """

    def append_version(self, version: ScopedInputVersion) -> VersionedInputHandle:
        """Persist a version. Creates a row; never rewrites one."""

    def get_version(self, version_ref: Any) -> ScopedInputVersion:
        """Read one version back by reference, re-verifying its digest."""

    def list_versions(self) -> tuple[VersionedInputHandle, ...]:
        """Every version of this owner, in append order."""


#: The merged-schema fields this module depends on, named in one place. A
#: reviewer can see the coupling surface without reading the adapter body, and
#: the adapter asserts each entry exists, so a schema change fails loudly here
#: rather than as an ``AttributeError`` deeper in.
MILESTONE_A_SCHEMA_BINDING: Mapping[str, tuple[str, ...]] = {
    "Activity": (
        "activity_id",
        "normalization_digest",
        "normalizer_version",
        "policy_version",
        "mapping_reference",
        "disposition",
        "quality_warnings",
        "timer_duration_seconds",
        "distance_value",
        "distance_unit_code",
        "record_sample_count",
        "gps_point_count",
        "heart_rate_value",
        "heart_rate_unit_code",
        "source_object",
        "import_record",
    ),
    "Session": ("sport", "session_start_utc", "elapsed_duration_ms", "timer_duration_seconds"),
    "SourceObject": ("source_object_id", "digest", "owner"),
    "Import": ("import_id", "source_digest", "status"),
    "Quarantine": ("import_record", "candidate_source_object", "state"),
    "Snapshot": (
        "snapshot_id",
        "scope_kind",
        "scope_start_utc",
        "scope_end_utc",
        "included_activity_ids",
        "included_digests",
        "included_count",
        "excluded_count",
        "exclusions",
        "snapshot_digest",
        "canonical_payload",
        "preparation_version",
        "policy_version",
        "mapping_reference",
        "created_at",
    ),
    "Evidence": (
        "evidence_id",
        "snapshot",
        "kind",
        "source_object_ref",
        "activity_ref",
        "field_path",
        "value_canonical",
        "method_version",
        "method_inputs",
    ),
}


#: Which stored column supplies each declared field, and which recorded warning
#: field explains an absence. ``None`` for ``warning_field`` means the value is
#: required, so it has no absence case. This mapping is the entire coupling
#: between a declared field name and the Milestone A schema.
MILESTONE_A_FIELD_SOURCES: Mapping[str, tuple[str, str | None]] = {
    "sport": (VALUE_CLASS_SOURCE_OBSERVATION, None),
    "sport_code": (VALUE_CLASS_SOURCE_OBSERVATION, None),
    "start_epoch_seconds": (VALUE_CLASS_SOURCE_OBSERVATION, None),
    "elapsed_duration_ms": (VALUE_CLASS_SOURCE_OBSERVATION, None),
    "timer_duration_seconds": (VALUE_CLASS_SOURCE_OBSERVATION, "timer_duration"),
    "distance_value": (VALUE_CLASS_SOURCE_OBSERVATION, "distance"),
    "distance_unit_code": (VALUE_CLASS_SOURCE_OBSERVATION, "distance"),
    "record_sample_count": (VALUE_CLASS_SOURCE_OBSERVATION, "record_samples"),
    "gps_point_count": (VALUE_CLASS_SOURCE_OBSERVATION, "gps"),
    "heart_rate_value": (VALUE_CLASS_SOURCE_OBSERVATION, "heart_rate"),
    "heart_rate_unit_code": (VALUE_CLASS_SOURCE_OBSERVATION, "heart_rate"),
    "quality_warnings": (VALUE_CLASS_QUALITY_WARNING, None),
}


class MilestoneAInputStore:
    """The :class:`VersionedInputStore` implementation over the merged schema.

    Every persistence detail lives here. Django is imported lazily inside the
    methods, so ``import datara.scoped_input`` stays free of the framework and
    the determinism test can run the pure preparation in a bare subprocess with
    a different ``PYTHONHASHSEED`` -- the same reason
    ``datara.intake`` defers its classification import.
    """

    def __init__(self, store: Any) -> None:
        self._store = store

    @property
    def owner_id(self) -> int:
        return int(self._store.scope.owner_id)

    def schema_binding(self) -> Mapping[str, tuple[str, ...]]:
        """Assert every bound field still exists, and return the binding.

        A schema change cannot be absorbed silently: a renamed or removed field
        fails here, naming the model and the field, before any query runs.
        """

        from datara import models as m

        for model_name, field_names in MILESTONE_A_SCHEMA_BINDING.items():
            model = getattr(m, model_name, None)
            if model is None:
                raise ScopedInputError(
                    f"the merged schema no longer defines {model_name}; TK21's persistence "
                    "binding must be revisited (this is the SR32 / Import shape change)"
                )
            present = {field.name for field in model._meta.get_fields()}
            missing = [name for name in field_names if name not in present]
            if missing:
                raise ScopedInputError(
                    f"{model_name} no longer defines {missing}; TK21's persistence binding must "
                    "be revisited"
                )
        if m.Activity.PUBLISHED != DISPOSITION_PUBLISHED:
            raise ScopedInputError(
                f"Activity.PUBLISHED is {m.Activity.PUBLISHED!r}, not {DISPOSITION_PUBLISHED!r}; "
                "the scope disposition vocabulary has drifted"
            )
        if m.Activity.QUARANTINED != DISPOSITION_QUARANTINED:
            raise ScopedInputError(
                f"Activity.QUARANTINED is {m.Activity.QUARANTINED!r}, not "
                f"{DISPOSITION_QUARANTINED!r}; the scope disposition vocabulary has drifted"
            )
        return MILESTONE_A_SCHEMA_BINDING

    # -- candidates ----------------------------------------------------------

    def scope_candidates(
        self, scope: ActivityScope, field_specs: Sequence[InputFieldSpec]
    ) -> tuple[ScopedRecord, ...]:
        """Read this owner's prepared records as scope candidates.

        Consumes both existing quarantine signals -- ``Activity.disposition`` and
        an unresolved ``Quarantine`` record -- rather than re-deriving either. The
        ``Quarantine`` lookup is owner-scoped, and the candidate's source object
        and import record are re-read through owner-scoped querysets rather than
        through Django's forward descriptors, which are not an authorization
        boundary (``datara.models.OwnerScopedManager`` documents this).
        """

        from django.db.models import Q

        from datara import models as m

        self.schema_binding()
        declared = require_declared(field_specs)
        unknown = sorted({spec.field_name for spec in declared} - set(MILESTONE_A_FIELD_SOURCES))
        if unknown:
            raise ScopedInputError(
                f"field(s) {unknown} have no Milestone A source; the supported declared fields are "
                f"{sorted(MILESTONE_A_FIELD_SOURCES)}"
            )
        # A skill may not relabel a measurement. If the declaration's class differs
        # from the class the stored column implies, the SR34/TC23 value-class label
        # would misdescribe the value, and that is a data-integrity defect rather
        # than a presentation detail.
        mislabelled = sorted(
            f"{spec.field_name}={spec.value_class}"
            for spec in declared
            if MILESTONE_A_FIELD_SOURCES[spec.field_name][0] != spec.value_class
        )
        if mislabelled:
            raise ScopedInputError(
                f"declared value class(es) {mislabelled} do not match the class the Milestone A "
                f"source column implies; sources are {sorted(MILESTONE_A_FIELD_SOURCES)}"
            )
        owner_id = self.owner_id

        activities = list(
            m.Activity.objects.for_owner(owner_id).select_related("import_record").order_by(
                "normalization_digest", "activity_id"
            )
        )
        source_object_ids = {activity.source_object_id for activity in activities}
        import_ids = {activity.import_record_id for activity in activities}
        # Owner-scoped reads, not forward-descriptor traversal. The assertion is
        # the isolation control: a row belonging to another identity is refused
        # rather than used to answer this owner's scope.
        source_objects = {
            row.source_object_id: row
            for row in m.SourceObject.objects.for_owner(owner_id).filter(
                source_object_id__in=source_object_ids
            )
        }
        if set(source_objects) != source_object_ids:
            raise ScopedInputError(
                "an activity references a source object this owner cannot see; refusing to "
                "build a scope rather than answering from another identity's row"
            )
        imports = {
            row.import_id: row for row in m.Import.objects.for_owner(owner_id).filter(import_id__in=import_ids)
        }
        if set(imports) != import_ids:
            raise ScopedInputError(
                "an activity references an import record this owner cannot see; refusing to "
                "build a scope rather than answering from another identity's row"
            )
        quarantined_imports = set(
            m.Quarantine.objects.for_owner(owner_id)
            .filter(
                state=m.Quarantine.STATE_QUARANTINED,
            )
            .filter(Q(import_record_id__in=import_ids) | Q(candidate_source_object_id__in=source_object_ids))
            .values_list("import_record_id", flat=True)
        )

        sessions = {}
        for session in m.Session.objects.for_owner(owner_id).select_related("activity"):
            if session.owner_id != owner_id:  # pragma: no cover - defensive
                raise ScopedInputError("a session row is not owned by this scope's owner")
            sessions[session.activity_id] = session

        candidates: list[ScopedRecord] = []
        for activity in activities:
            if activity.activity_id not in sessions:
                # A file-level record with no normalized session is not a prepared
                # record and cannot supply a canonical logical tuple. It is left
                # out of the candidate set entirely rather than offered and
                # excluded, because there is no window value to judge it against.
                continue
            source_object = source_objects[activity.source_object_id]
            import_row = imports[activity.import_record_id]
            if import_row.source_digest != source_object.digest:
                # Provenance consistency: the prepared record's bytes digest and
                # the import's own digest must agree, or a value's provenance
                # would name two different sources.
                raise ScopedInputError(
                    f"activity {activity.activity_id}: import digest {import_row.source_digest!r} "
                    f"and source object digest {source_object.digest!r} disagree"
                )
            quarantined = (
                activity.disposition == DISPOSITION_QUARANTINED
                or activity.import_record_id in quarantined_imports
            )
            candidates.append(
                self._build_record(
                    activity=activity,
                    session=sessions[activity.activity_id],
                    source_digest=source_object.digest,
                    declared=declared,
                    quarantined=quarantined,
                )
            )
        return tuple(candidates)

    def _build_record(
        self,
        *,
        activity: Any,
        session: Any,
        source_digest: str,
        declared: Sequence[InputFieldSpec],
        quarantined: bool,
    ) -> ScopedRecord:
        from datara.canonical import LogicalIdentity

        start_seconds = start_epoch_seconds_from_datetime(
            session.session_start_utc,
            origin="MilestoneAInputStore.session_start_utc",
        )
        # The canonical unit guard, with the unit declared. The write site
        # already asserted it, and the database constrains it, but the value is
        # compared and serialised here too, so it is checked on the way out as
        # well as on the way in.
        elapsed_ms = require_elapsed_duration_ms(
            session.elapsed_duration_ms,
            origin="MilestoneAInputStore.elapsed_duration_ms",
            unit=CANONICAL_DURATION_UNIT,
        )
        identity = LogicalIdentity(
            sport_code=canonical_sport_code(
                session.sport, origin="MilestoneAInputStore.sport"
            ),
            start_epoch_seconds=start_seconds,
            elapsed_duration_ms=elapsed_ms,
        )
        warnings = {str(item.get("field")): item for item in (activity.quality_warnings or [])}

        fields: list[ScopedField] = [
            ScopedField(
                field_name=HEADER_CANONICAL_IDENTITY,
                value_class=VALUE_CLASS_SCOPE_MEMBER,
                value_canonical=activity.normalization_digest,
                preparation_version=activity.normalizer_version,
                mapping_reference=activity.mapping_reference,
            ),
            ScopedField(
                field_name=HEADER_SOURCE_DIGEST,
                value_class=VALUE_CLASS_SCOPE_MEMBER,
                value_canonical=source_digest,
                preparation_version=activity.normalizer_version,
                mapping_reference=activity.mapping_reference,
            ),
        ]
        for spec in declared:
            value, warning_field = self._extract(spec.field_name, activity, session, identity)
            absent = None
            if value is None:
                if warning_field is None:
                    raise DeclaredFieldMissing(
                        f"field {spec.field_name!r} has no Milestone A source column and no "
                        "recorded absence vocabulary, so a null for it would be a silent default"
                    )
                recorded = warnings.get(warning_field)
                if recorded is None:
                    # An explicit raise, not an assert: under `python -O` an
                    # assert would vanish and a null value with no explanation
                    # would reach the envelope -- exactly the silent default the
                    # module forbids. TK18's no-imputation invariant guarantees
                    # one of the two is wrong, and guessing is not an option.
                    raise ProvenanceError(
                        f"field {spec.field_name!r} is absent but the prepared record carries no "
                        f"recorded warning for {warning_field!r}; TK18's no-imputation invariant "
                        "means one of the two is wrong, and guessing is not an option"
                    )
                absent = AbsentObservation.from_warning_record(recorded)
            fields.append(
                ScopedField(
                    field_name=spec.field_name,
                    value_class=spec.value_class,
                    value_canonical=value,
                    preparation_version=activity.normalizer_version,
                    mapping_reference=activity.mapping_reference,
                    absent=absent,
                )
            )
        return ScopedRecord(
            canonical_identity=activity.normalization_digest,
            source_digest=source_digest,
            logical_tuple=identity,
            preparation_version=activity.normalizer_version,
            policy_version=activity.policy_version,
            mapping_reference=activity.mapping_reference,
            disposition=activity.disposition,
            quarantined=quarantined,
            fields=tuple(fields),
        )

    def _extract(
        self, field_name: str, activity: Any, session: Any, identity: LogicalIdentity
    ) -> tuple[str | None, str | None]:
        """The canonical text of one declared field, plus its warning field.

        Returns ``(None, warning_field)`` for an absent optional value; the caller
        then takes the absence reason from the record's own recorded warning, so
        the explanation is preparation's, not this module's.
        """

        _, warning_field = MILESTONE_A_FIELD_SOURCES[field_name]
        if field_name == "sport":
            return session.sport, warning_field
        if field_name == "sport_code":
            return str(identity.sport_code), warning_field
        if field_name == "start_epoch_seconds":
            return str(identity.start_epoch_seconds), warning_field
        if field_name == "elapsed_duration_ms":
            return str(identity.elapsed_duration_ms), warning_field
        if field_name == "quality_warnings":
            return canonical_json(list(activity.quality_warnings or [])), warning_field
        raw = getattr(activity, field_name, None)
        if raw is None:
            return None, warning_field
        if isinstance(raw, bool):
            # A bool is an int in Python and would silently become 0 or 1.
            raise ScopedInputError(
                f"stored field {field_name!r} holds a bool ({raw!r}); TK18's normalizer never "
                "writes one, so the stored record is not the record it claims to be"
            )
        if isinstance(raw, int):
            return str(raw), warning_field
        if isinstance(raw, str):
            return raw, warning_field
        return canonical_json(raw), warning_field

    # -- append / read -------------------------------------------------------

    def append_version(self, version: ScopedInputVersion) -> VersionedInputHandle:
        """Persist a version by creating one row plus its provenance rows.

        Idempotent by content: an identical version is recognised by its digest
        and its complete lineage is checked before returning ``created=False``. That is what
        proves a re-version never mutates a prior version -- the second call does
        not write at all. Cooperative scoped appends serialize on the owner row
        before lookup; generic writers do not provide universal uniqueness.
        A different version gets its own row and leaves the earlier one untouched.
        A returned handle inside a caller transaction remains subject to that
        transaction's outermost commit or rollback.
        """

        from datara import models as m

        self.schema_binding()
        serialized = getattr(self._store, "_owner_serialized_write", None)
        if not callable(serialized):
            raise ScopedInputError("the persistence store must supply an owner-serialized write context")
        with serialized():
            owner_id = self.owner_id
            matches = list(
                m.Snapshot.objects.for_owner(owner_id)
                .filter(snapshot_digest=version.input_digest)
                .order_by("snapshot_id")[:2]
            )
            if len(matches) > 1:
                raise ScopedInputError("the stored version identity is ambiguous")
            existing = matches[0] if matches else None
            if existing is not None:
                stored = self.get_version(existing.snapshot_id)
                if (
                    stored.canonical_payload != version.canonical_payload
                    or existing.included_count != version.included_count
                    or existing.excluded_count != version.excluded_count
                ):
                    raise ScopedInputError(
                        "the existing version does not match the requested immutable version"
                    )
                # Refuse historical partial writes; never repair immutable history.
                self.provenance_rows(existing.snapshot_id)
                return VersionedInputHandle(
                    version_ref=str(existing.snapshot_id),
                    input_digest=existing.snapshot_digest,
                    record_count=existing.included_count,
                    excluded_count=existing.excluded_count,
                    created=False,
                )

            activity_ids = self.resolve_activity_ids(
                tuple(record.canonical_identity for record in version.records)
            )
            snapshot = self._store.record_snapshot(version, activity_ids)
            self._write_provenance(snapshot, version)
            return VersionedInputHandle(
                version_ref=str(snapshot.snapshot_id),
                input_digest=snapshot.snapshot_digest,
                record_count=snapshot.included_count,
                excluded_count=snapshot.excluded_count,
                created=True,
            )

    def resolve_activity_ids(self, canonical_identities: Sequence[str]) -> tuple[Any, ...]:
        """Resolve canonical identities to this owner's stored records.

        Owner-scoped, and exact: an identity that matches no row, or more than one
        row, is a refusal. Silently taking the first match would let a scope
        reference a record it did not actually select.
        """

        from datara import models as m

        if not canonical_identities:
            return ()
        rows = list(
            m.Activity.objects.for_owner(self.owner_id).filter(
                normalization_digest__in=list(canonical_identities)
            )
        )
        by_digest: dict[str, list[Any]] = {}
        for row in rows:
            by_digest.setdefault(row.normalization_digest, []).append(row)
        missing = sorted(set(canonical_identities) - set(by_digest))
        if missing:
            raise ScopedInputError(
                f"canonical identit{'y' if len(missing) == 1 else 'ies'} {missing} are not "
                "stored for this owner; a scope may reference only prepared records it can resolve"
            )
        ambiguous = sorted(d for d, group in by_digest.items() if len(group) > 1)
        if ambiguous:
            raise AmbiguousCanonicalIdentity(
                f"canonical identit{'y' if len(ambiguous) == 1 else 'ies'} {ambiguous} match more "
                "than one stored record for this owner"
            )
        # Returned in the caller's order so the mapping is explicit, not inferred
        # from a query's ordering.
        return tuple(by_digest[identity][0].activity_id for identity in canonical_identities)

    def _write_provenance(self, snapshot: Any, version: ScopedInputVersion) -> None:
        """Write one ``Evidence`` row per scoped field, from the ledger.

        Written from the ledger rather than from the records, so the persisted
        provenance is exactly the set the completeness check verified. The
        payload deliberately carries no generated row id; these rows are what
        makes a field resolvable to a real source row.

        See :meth:`provenance_rows` for the recorded gap on
        ``Evidence.method_version`` / ``method_inputs``.
        """

        from datara import models as m

        activity_refs = dict(
            zip(
                version.included_digests,
                (str(value) for value in self.resolve_activity_ids(version.included_digests)),
            )
        )
        source_refs = self._source_object_refs(version)
        for entry in version.ledger.entries:
            row_reference = activity_refs[entry.canonical_identity]
            if len(row_reference) > MAX_ROW_REFERENCE_LENGTH:  # pragma: no cover - UUID is 36
                raise ScopedInputError(
                    f"activity reference {row_reference!r} exceeds the Evidence.activity_ref limit"
                )
            self._store.record_evidence(
                snapshot,
                kind=m.Evidence.KIND_SOURCE_RECORD,
                source_object_ref=source_refs[entry.canonical_identity],
                activity_ref=row_reference,
                field_path=entry.field_path,
                value_canonical=entry.value_canonical,
            )

    def _source_object_refs(self, version: ScopedInputVersion) -> dict[str, str]:
        from datara import models as m

        rows = list(
            m.Activity.objects.for_owner(self.owner_id).filter(
                normalization_digest__in=list(version.included_digests)
            )
        )
        refs: dict[str, str] = {}
        for row in rows:
            reference = str(row.source_object_id)
            if len(reference) > MAX_ROW_REFERENCE_LENGTH:  # pragma: no cover
                raise ScopedInputError(
                    f"source object reference {reference!r} exceeds the Evidence limit"
                )
            refs[row.normalization_digest] = reference
        missing = sorted(set(version.included_digests) - set(refs))
        if missing:
            raise ScopedInputError(f"no stored source object for canonical identities {missing}")
        return refs

    def get_version(self, version_ref: Any) -> ScopedInputVersion:
        snapshot = self._store.get_snapshot(version_ref)
        version = ScopedInputVersion.from_canonical_payload(snapshot.canonical_payload)
        if version.input_digest != snapshot.snapshot_digest:
            raise ScopedInputError(
                "the stored digest does not match the stored canonical payload; the version row "
                "is inconsistent and is refused rather than returned"
            )
        return version

    def list_versions(self) -> tuple[VersionedInputHandle, ...]:
        """Every version of this owner, oldest first.

        Append-only history, ordered. There is deliberately no
        ``latest_version``: the founder's constraint is that history is queried,
        never "latest", and a newest-value accessor is the first step towards a
        mutable current-value pointer.
        """

        from datara import models as m

        return tuple(
            VersionedInputHandle(
                version_ref=str(row.snapshot_id),
                input_digest=row.snapshot_digest,
                record_count=row.included_count,
                excluded_count=row.excluded_count,
                created=False,
            )
            for row in m.Snapshot.objects.for_owner(self.owner_id).order_by(
                "created_at", "snapshot_id"
            )
        )

    def provenance_rows(self, version_ref: Any) -> tuple[dict[str, Any], ...]:
        """The persisted provenance rows for a version, checked against its ledger.

        Checked in both directions: a carried field with no stored row is a
        missing provenance source, and a stored row addressing a field the
        version does not carry is a reference to a value that is not in the
        input. One-directional completeness would let an orphan row pass.

        Known gap, reported rather than worked around: the current
        ``datara.db.OwnerScopedStore.record_evidence`` signature accepts only
        ``kind``/``source_object_ref``/``activity_ref``/``field_path``/
        ``value_canonical``, so ``Evidence.method_version`` and
        ``Evidence.method_inputs`` are written as null by the store. The
        preparation version and the mapping reference that produced each value
        are therefore carried by the version's own payload and ledger (where they
        are digest-bound and verifiable) and are *not* on the evidence row yet.
        Closing that needs a ``record_evidence`` parameter change, which is
        outside this assignment's file ownership.
        """

        snapshot = self._store.get_snapshot(version_ref)
        version = self.get_version(version_ref)
        rows = _evidence_rows_for_snapshot(self._store, snapshot, include_kind=True)
        stored_paths = {str(row["field_path"]) for row in rows}
        expected = set(version.all_field_paths())
        missing = sorted(expected - stored_paths)
        if missing:
            raise ProvenanceIncomplete(missing)
        orphan = sorted(stored_paths - expected)
        if orphan:
            raise ProvenanceError(
                f"provenance row(s) {orphan} address fields the version does not carry; a stored "
                "reference to a value that is not in the input is a defect"
            )
        unvalued = sorted(
            str(row["field_path"])
            for row in rows
            if version.ledger.resolve(str(row["field_path"])).available
            and row["value_canonical"] is None
        )
        if unvalued:
            raise ProvenanceError(
                f"provenance row(s) {unvalued} carry no value although the version's field is "
                "present; a reference that does not carry the value it references is not "
                "reconstructible"
            )
        from datara import models as m

        activity_refs = dict(
            zip(
                version.included_digests,
                (str(value) for value in self.resolve_activity_ids(version.included_digests)),
            )
        )
        source_refs = self._source_object_refs(version)
        by_path: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_path.setdefault(str(row["field_path"]), []).append(row)
        invalid = []
        for entry in version.ledger.entries:
            matches = by_path[entry.field_path]
            if len(matches) != 1:
                invalid.append(entry.field_path)
                continue
            row = matches[0]
            if (
                row["kind"] != m.Evidence.KIND_SOURCE_RECORD
                or row["activity_ref"] != activity_refs[entry.canonical_identity]
                or row["source_object_ref"] != source_refs[entry.canonical_identity]
                or row["value_canonical"] != entry.value_canonical
            ):
                invalid.append(entry.field_path)
        if invalid:
            raise ProvenanceError(
                f"provenance row(s) {sorted(invalid)} do not match the complete expected lineage"
            )
        return tuple({key: value for key, value in row.items() if key != "kind"} for row in rows)

    # -- introspection used by the tests -------------------------------------

    def mutable_version_api(self) -> list[str]:
        """Public names that could rewrite or remove a version.

        Mirrors ``datara.storage.OriginalStore.mutating_public_api``: the
        immutability claim is testable because adding an ``update``/``overwrite``/
        ``delete`` method fails a test instead of quietly creating a defect.
        """

        forbidden = ("update", "overwrite", "replace", "delete", "remove", "mutate", "truncate", "rewrite", "patch")
        found: list[str] = []
        for name in dir(type(self)):
            if name.startswith("_"):
                continue
            attribute = getattr(type(self), name, None)
            if callable(attribute) and any(token in name.lower() for token in forbidden):
                found.append(name)
        return sorted(found)

    def newest_value_api(self) -> list[str]:
        """Public names that would answer "the newest value".

        The founder's constraint is that history is append-only and *queried*,
        never "latest". ``datara.db``'s column guard cannot see a method name, so
        this check exists: adding ``latest_version`` or ``current_version`` fails
        a test rather than introducing a current-value pointer.
        """

        adjectives = ("latest", "last", "current", "most_recent", "newest")
        # This method's own name contains "newest"; it is excluded, or the check
        # would report itself and be meaningless.
        found: list[str] = []
        for name in dir(type(self)):
            if name.startswith("_") or name == "newest_value_api":
                continue
            found.extend(name for adjective in adjectives if adjective in name.lower())
        return sorted(set(found))


def _evidence_rows_for_snapshot(
    store: Any, snapshot: Any, *, include_kind: bool = False
) -> list[dict[str, Any]]:
    """Read owned source-record evidence for a snapshot, excluding computed graphs."""

    from datara import models as m

    return [
        {
            **({"kind": row.kind} if include_kind else {}),
            "field_path": row.field_path,
            "activity_ref": row.activity_ref,
            "source_object_ref": row.source_object_ref,
            "value_canonical": row.value_canonical,
            "method_version": row.method_version,
            "method_inputs": row.method_inputs,
        }
        for row in m.Evidence.objects.for_owner(store.scope.owner_id).filter(
            snapshot=snapshot, kind="source_record"
        ).order_by(
            "field_path", "evidence_id"
        )
    ]


__all__ = [
    "SCOPED_INPUT_CONTRACT_VERSION",
    "SCOPED_INPUT_VERSION",
    "SCOPE_WINDOW",
    "HEADER_CANONICAL_IDENTITY",
    "HEADER_SOURCE_DIGEST",
    "HEADER_FIELDS",
    "DISPOSITION_PUBLISHED",
    "DISPOSITION_QUARANTINED",
    "SCOPABLE_DISPOSITIONS",
    "EXCLUSION_REASONS",
    "EXCLUSION_REASON_SET",
    "EXCLUSION_PRECEDENCE",
    "EXCLUDED_QUARANTINED",
    "EXCLUDED_DISPOSITION",
    "EXCLUDED_OUTSIDE_WINDOW",
    "EXCLUDED_SPORT",
    "EXCLUDED_POLICY_VERSION",
    "EXCLUDED_MAPPING_REFERENCE",
    "EXCLUDED_PREPARATION_VERSION",
    "EXCLUDED_REQUIRED_FIELD_ABSENT",
    "EXCLUDED_DUPLICATE_IDENTITY",
    "EXCLUDED_CAPACITY",
    "PROHIBITED_PAYLOAD_TOKENS",
    "MILESTONE_A_SCHEMA_BINDING",
    "MILESTONE_A_FIELD_SOURCES",
    "ScopedInputError",
    "ScopeContractError",
    "ScopeCapacityExceeded",
    "ProhibitedScopeContent",
    "QuarantinedCandidateInScope",
    "UndeclaredFieldInRecord",
    "DeclaredFieldMissing",
    "AmbiguousCanonicalIdentity",
    "ActivityScope",
    "InputFieldSpec",
    "require_declared",
    "ScopedRecord",
    "ScopedExclusion",
    "ScopedInputVersion",
    "VersionedInputHandle",
    "VersionedInputStore",
    "MilestoneAInputStore",
    "assert_no_prohibited_content",
    "prepare_scoped_input",
    "json_safe",
]
