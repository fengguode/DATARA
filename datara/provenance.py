"""Reconstructible provenance for a versioned scoped skill input.

TK21 -- CUS03; SR07, SR28, SR34; FEAT21; WP03. Oracles TC05, TC20, TC23.

WHY THIS MODULE EXISTS
----------------------
A skill input is a *versioned, scoped selection of already accepted and prepared
records*. That statement is only meaningful if every value in it can be traced
back. The founder's requirement is exact: for **any** value, name the source
record, its digest, the preparation version and the mapping reference that
produced it. This module is that naming, as executable data rather than as a
promise in a comment.

THE ONE RULE THIS MODULE ENFORCES
----------------------------------
**A value with no provenance source is a failure, not a default.**

The tempting alternative -- emit the field with a null, or with a placeholder
"unknown" digest, and let the consumer notice -- is exactly the defect this
module exists to prevent, because a null is indistinguishable from a genuinely
absent measurement, and a placeholder digest is indistinguishable from a real
one. So :meth:`ProvenanceLedger.require_complete` raises
:class:`ProvenanceIncomplete`, and :meth:`ProvenanceLedger.resolve` raises
:class:`UnresolvableProvenance`. There is no code path that emits a
default provenance.

WHY AN ABSENT VALUE IS NOT A ZERO
---------------------------------
D01 forbids imputation and SR34/TC23 require an absent optional value to be
presented as unavailable/unknown rather than zero or inferred. So an absent
value is represented as ``value_canonical is None`` **plus** a mandatory
:class:`AbsentObservation` naming the *recorded* warning that explains the
absence. The explanation is not re-derived here: it is the warning the
normalizer already stored on the source record
(:class:`datara.normalization.QualityWarning`), so a consumer can tell "this
athlete had no heart-rate sensor in this file" from "this field was dropped".

VALUE CLASSES (SR34, TC23)
--------------------------
SR34 requires presentation to distinguish observations, computed metrics and
quality warnings. Those are the value classes. Milestone A can produce only
three of the four:

* ``source_observation`` -- a value read from the source and normalised;
* ``quality_warning``    -- a recorded data-quality observation;
* ``scope_member``       -- the record's own canonical identity and lineage;
* ``computed_metric``    -- **declared, unavailable**. Milestone A has no
  ``Metric`` table, ``datara.db.record_evidence`` refuses the
  ``computed_metric`` evidence kind, and the metric field contract is an
  unapproved D02/WP02 output. A class that is in the contract vocabulary but
  that nothing can produce is the honest state; inventing one would be a
  fabricated measurement.

NAMING, AND THE BINDING ARCHITECTURAL CONDITION
-----------------------------------------------
The founder's binding condition excludes, by *meaning*, any entity that is the
outcome of executing a skill against a model. Nothing in this module is one, and
the names here are chosen so that a future widening of ``datara.db``'s
forbidden-entity list does not collide with a provenance record by accident:
``FieldProvenance`` names where a value came from, never what a model said. A
skill input is not a result. ``datara/tests/test_scoped_input.py`` asserts that
none of these class names folds to a forbidden entity name -- including the
names the Architect is reported to be adding -- so this is checked, not asserted
in prose.

PURE. No database, no Django, no filesystem, no network, no clock, no model
call. That is what lets the determinism test run the same code in a bare
subprocess with a different ``PYTHONHASHSEED``.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from datara.normalization import (
    WARNING_ABSENT,
    WARNING_INVALID,
    WARNING_OUT_OF_RANGE,
    WARNING_UNIT_CODE_ABSENT,
    canonical_json,
    digest_matches,
    sha256_digest,
)

# ---------------------------------------------------------------------------
# Value classes
# ---------------------------------------------------------------------------

VALUE_CLASS_SOURCE_OBSERVATION = "source_observation"
VALUE_CLASS_COMPUTED_METRIC = "computed_metric"
VALUE_CLASS_QUALITY_WARNING = "quality_warning"
VALUE_CLASS_SCOPE_MEMBER = "scope_member"

#: The full contract vocabulary, including the class Milestone A cannot produce.
#: Kept complete so a later task can add a producer without redefining the
#: vocabulary, and so a consumer can recognise the class when it appears.
VALUE_CLASSES: frozenset[str] = frozenset(
    {
        VALUE_CLASS_SOURCE_OBSERVATION,
        VALUE_CLASS_COMPUTED_METRIC,
        VALUE_CLASS_QUALITY_WARNING,
        VALUE_CLASS_SCOPE_MEMBER,
    }
)

#: What a Milestone A scoped input may actually carry. ``computed_metric`` is
#: absent on purpose; :class:`ValueClassUnavailable` explains why when asked for.
MILESTONE_A_VALUE_CLASSES: frozenset[str] = frozenset(
    {
        VALUE_CLASS_SOURCE_OBSERVATION,
        VALUE_CLASS_QUALITY_WARNING,
        VALUE_CLASS_SCOPE_MEMBER,
    }
)

#: Human-facing labels for SR34 presentation. Presentation is a later task's
#: render step; these are the deterministic label *inputs*, so a rendered screen
#: cannot invent a fourth class name.
VALUE_CLASS_LABELS: Mapping[str, str] = {
    VALUE_CLASS_SOURCE_OBSERVATION: "measured value from the source file",
    VALUE_CLASS_COMPUTED_METRIC: "value calculated by DATARA from other values",
    VALUE_CLASS_QUALITY_WARNING: "recorded data-quality observation",
    VALUE_CLASS_SCOPE_MEMBER: "selected record identity and lineage",
}

#: The single rendering for a value that does not exist. SR34 and TC23: an
#: absent optional value is unavailable/unknown, never zero and never inferred.
#: One constant, so no call site can invent a different placeholder.
UNAVAILABLE_LABEL = "unavailable"

#: The recorded-warning codes that may explain an absence. Reused from
#: ``datara.normalization`` rather than restated, so TK21 cannot drift from the
#: vocabulary TK18 wrote.
ABSENT_REASON_CODES: frozenset[str] = frozenset(
    {WARNING_ABSENT, WARNING_INVALID, WARNING_OUT_OF_RANGE, WARNING_UNIT_CODE_ABSENT}
)

_FIELD_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,39}$")
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

#: ``Evidence.field_path`` is ``CharField(max_length=128)`` and
#: ``Evidence.activity_ref`` / ``source_object_ref`` are ``max_length=64``.
#: Enforced here so a long identity cannot be silently truncated by the database
#: into a reference that resolves to the wrong row.
MAX_FIELD_PATH_LENGTH = 128
MAX_ROW_REFERENCE_LENGTH = 64
MAX_VERSION_REFERENCE_LENGTH = 64

#: A canonical identity is a normalization digest: ``sha256:`` + 64 hex.
_CANONICAL_IDENTITY_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

FIELD_PATH_SEPARATOR = "."


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ProvenanceError(Exception):
    """Base for every provenance failure in this module."""


class ValueClassUnavailable(ProvenanceError):
    """A value class was requested that Milestone A cannot produce."""

    def __init__(self, value_class: str, field_name: str) -> None:
        self.value_class = value_class
        self.field_name = field_name
        super().__init__(
            f"field {field_name!r} declares value class {value_class!r}, which "
            "Milestone A cannot produce: there is no Metric table, "
            "datara.db.record_evidence refuses the 'computed_metric' evidence "
            "kind, and the metric field contract is an unapproved D02/WP02 "
            "output. A computed metric must not be invented here."
        )


class ProvenanceIncomplete(ProvenanceError):
    """A declared field of the input has no provenance entry.

    This is the enforcement of "a field with no provenance source is a failure,
    not a default". It is raised, never returned as a warning, and never
    substituted with a placeholder.
    """

    def __init__(self, missing: Sequence[str]) -> None:
        self.missing = tuple(missing)
        super().__init__(
            f"{len(self.missing)} declared field(s) have no provenance source: "
            f"{', '.join(self.missing[:8])}"
            + (" ..." if len(self.missing) > 8 else "")
        )


class UnresolvableProvenance(ProvenanceError):
    """A field path was asked for that the ledger does not resolve."""


class DuplicateFieldPath(ProvenanceError):
    """Two different values claimed the same field path."""


# ---------------------------------------------------------------------------
# Absent values
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AbsentObservation:
    """Why a declared field has no value, quoting the recorded warning.

    ``code`` and ``detail`` are the normalizer's own vocabulary, and
    ``source_field`` is the source field path the normalizer recorded for it.
    The absence is therefore itself provenance-bearing: a reader can distinguish
    "no heart-rate sensor in this file" from "this field was dropped".
    """

    code: str
    detail: str
    source_field: str | None = None

    def __post_init__(self) -> None:
        if self.code not in ABSENT_REASON_CODES:
            raise ProvenanceError(
                f"absent-value code {self.code!r} is outside the recorded "
                f"warning vocabulary {sorted(ABSENT_REASON_CODES)}"
            )
        if not self.detail:
            raise ProvenanceError("an absent value must name a warning detail")

    @classmethod
    def from_warning_record(cls, record: Mapping[str, Any]) -> "AbsentObservation":
        """Build from a stored ``Activity.quality_warnings`` entry.

        Reads the record the normalizer already wrote rather than deciding
        anything, so the explanation cannot drift from preparation.
        """

        return cls(
            code=str(record.get("code", "")),
            detail=str(record.get("detail", "")),
            source_field=record.get("source_field"),
        )

    def as_record(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "detail": self.detail,
            "source_field": self.source_field,
        }


# ---------------------------------------------------------------------------
# One value plus its lineage
# ---------------------------------------------------------------------------


def _require_field_name(value: Any, *, origin: str) -> str:
    if not isinstance(value, str) or not _FIELD_NAME_RE.match(value):
        raise ProvenanceError(
            f"{origin}: field name must match {_FIELD_NAME_RE.pattern}, got {value!r}"
        )
    return value


def _require_version_reference(value: Any, *, origin: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProvenanceError(f"{origin}: a version reference must be a non-empty string")
    if len(value) > MAX_VERSION_REFERENCE_LENGTH:
        raise ProvenanceError(
            f"{origin}: version reference {value!r} exceeds the {MAX_VERSION_REFERENCE_LENGTH} "
            "character column limit; a truncated reference would resolve wrongly"
        )
    return value


def _require_digest(value: Any, *, origin: str) -> str:
    if not isinstance(value, str) or not digest_matches(value):
        raise ProvenanceError(
            f"{origin}: expected 'sha256:' + 64 lowercase hex, got {value!r}"
        )
    return value


def require_canonical_identity(value: Any, *, origin: str) -> str:
    """A prepared record's canonical identity: its normalization digest.

    This is the identity a scope references records by. It is content-derived,
    so re-preparing the same accepted bytes yields the same identity -- which is
    what makes a version's bytes stable across preparations. A generated
    ``activity_id`` is *not* an acceptable substitute: it differs between two
    preparations of the same records.
    """

    return _require_digest(value, origin=origin)


@dataclass(frozen=True)
class ScopedField:
    """One value inside a scoped input, carrying the lineage that produced it.

    The value and its provenance are one object on purpose. Splitting them into
    a parallel map is how a value ends up without provenance: the two structures
    drift, and the drift is invisible until a consumer resolves the field and
    finds nothing. Here the absence of provenance is unrepresentable.
    """

    field_name: str
    value_class: str
    value_canonical: str | None
    preparation_version: str
    mapping_reference: str
    absent: AbsentObservation | None = None

    def __post_init__(self) -> None:
        _require_field_name(self.field_name, origin="ScopedField")
        if self.value_class not in VALUE_CLASSES:
            raise ProvenanceError(
                f"ScopedField {self.field_name!r}: unknown value class {self.value_class!r}; "
                f"the contract vocabulary is {sorted(VALUE_CLASSES)}"
            )
        if self.value_class not in MILESTONE_A_VALUE_CLASSES:
            raise ValueClassUnavailable(self.value_class, self.field_name)
        _require_version_reference(
            self.preparation_version, origin=f"ScopedField {self.field_name!r}.preparation_version"
        )
        if not self.mapping_reference:
            raise ProvenanceError(
                f"ScopedField {self.field_name!r}: a mapping reference is required; a value "
                "with no declared mapping has no reproducible provenance"
            )
        if len(self.mapping_reference) > 128:
            raise ProvenanceError(
                f"ScopedField {self.field_name!r}: mapping reference exceeds 128 characters"
            )
        # The invariant that makes "not a default" checkable: a value is either
        # present, or absent with a recorded reason. Neither "present and
        # explained as absent" nor "absent with no reason" is representable.
        if self.value_canonical is None and self.absent is None:
            raise ProvenanceError(
                f"ScopedField {self.field_name!r}: a null value must carry an "
                "AbsentObservation naming the recorded warning. A null with no "
                "reason is exactly the silent default this module forbids."
            )
        if self.value_canonical is not None and self.absent is not None:
            raise ProvenanceError(
                f"ScopedField {self.field_name!r}: a value cannot be both present "
                f"({self.value_canonical!r}) and explained as absent"
            )

    @property
    def available(self) -> bool:
        return self.value_canonical is not None

    def as_record(self) -> dict[str, Any]:
        """The canonical form. Key order is irrelevant: it is emitted with
        ``sort_keys=True``. ``None`` and a string are distinguishable, and the
        absence reason travels with the null."""

        return {
            "field_name": self.field_name,
            "value_class": self.value_class,
            "value_canonical": self.value_canonical,
            "preparation_version": self.preparation_version,
            "mapping_reference": self.mapping_reference,
            "absent": None if self.absent is None else self.absent.as_record(),
        }


# ---------------------------------------------------------------------------
# The ledger
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FieldProvenance:
    """The resolvable lineage of one field of the input.

    Assembled from the enclosing record's canonical identity and digest plus the
    field's own preparation version and mapping reference. This is the record
    persisted as ``datara.Evidence``, so a consumer resolves a field to a real,
    owner-scoped source row rather than to a string.
    """

    field_path: str
    value_class: str
    canonical_identity: str
    source_digest: str
    preparation_version: str
    mapping_reference: str
    value_canonical: str | None
    absent: AbsentObservation | None = None

    def __post_init__(self) -> None:
        if len(self.field_path) > MAX_FIELD_PATH_LENGTH:
            raise ProvenanceError(
                f"field path {self.field_path!r} exceeds the {MAX_FIELD_PATH_LENGTH} character "
                "Evidence.field_path limit; a truncated path would resolve to the wrong field"
            )
        require_canonical_identity(self.canonical_identity, origin="FieldProvenance")
        _require_digest(self.source_digest, origin="FieldProvenance")
        _require_version_reference(
            self.preparation_version, origin=f"FieldProvenance {self.field_path!r}"
        )
        if self.value_class not in VALUE_CLASSES:
            raise ProvenanceError(f"FieldProvenance: unknown value class {self.value_class!r}")
        # The value travels with its lineage. An entry therefore cannot exist
        # without saying what the value is, and a present value cannot be paired
        # with an absence explanation.
        if self.value_canonical is None and self.absent is None:
            raise ProvenanceError(
                f"FieldProvenance {self.field_path!r}: an unavailable value must name the "
                "recorded warning that explains it"
            )
        if self.value_canonical is not None and self.absent is not None:
            raise ProvenanceError(
                f"FieldProvenance {self.field_path!r}: a value cannot be both present "
                f"({self.value_canonical!r}) and explained as absent"
            )

    @property
    def available(self) -> bool:
        return self.value_canonical is not None

    def record_key(self) -> tuple[str, str]:
        return (self.field_path, self.canonical_identity)

    def as_record(self) -> dict[str, Any]:
        return {
            "field_path": self.field_path,
            "value_class": self.value_class,
            "canonical_identity": self.canonical_identity,
            "source_digest": self.source_digest,
            "preparation_version": self.preparation_version,
            "mapping_reference": self.mapping_reference,
            "value_canonical": self.value_canonical,
            "available": self.available,
            "absent": None if self.absent is None else self.absent.as_record(),
        }


def build_field_path(canonical_identity: str, field_name: str) -> str:
    """The stable address of one field: ``<canonical identity>.<field name>``.

    Addressed by canonical identity rather than by list index or row id, so the
    address means the same thing before and after re-preparation, and a
    reordered scope does not silently re-point a provenance reference at a
    different value.
    """

    require_canonical_identity(canonical_identity, origin="build_field_path")
    _require_field_name(field_name, origin="build_field_path")
    path = f"{canonical_identity}{FIELD_PATH_SEPARATOR}{field_name}"
    if len(path) > MAX_FIELD_PATH_LENGTH:
        raise ProvenanceError(
            f"field path {path!r} exceeds {MAX_FIELD_PATH_LENGTH} characters; the field name "
            "is too long for the Evidence.field_path column"
        )
    return path


def build_ledger(
    records: Iterable[tuple[str, str, Sequence[ScopedField]]],
) -> "ProvenanceLedger":
    """Build the ledger from ``(canonical identity, source digest, fields)``.

    Every field of every record produces exactly one entry. There is no code
    path that produces a record whose field is skipped, which is the structural
    half of "a field with no provenance source is a failure".
    """

    entries: list[FieldProvenance] = []
    for canonical_identity, source_digest, fields in records:
        require_canonical_identity(canonical_identity, origin="build_ledger")
        _require_digest(source_digest, origin="build_ledger")
        for item in fields:
            entries.append(
                FieldProvenance(
                    field_path=build_field_path(canonical_identity, item.field_name),
                    value_class=item.value_class,
                    canonical_identity=canonical_identity,
                    source_digest=source_digest,
                    preparation_version=item.preparation_version,
                    mapping_reference=item.mapping_reference,
                    value_canonical=item.value_canonical,
                    absent=item.absent,
                )
            )
    return ProvenanceLedger(entries=tuple(entries))


@dataclass(frozen=True)
class ProvenanceLedger:
    """The complete, ordered set of lineage entries for one input version."""

    entries: tuple[FieldProvenance, ...]

    def __post_init__(self) -> None:
        ordered = tuple(sorted(self.entries, key=lambda e: e.field_path))
        seen: set[str] = set()
        for entry in ordered:
            if entry.field_path in seen:
                raise DuplicateFieldPath(
                    f"two different values claim field path {entry.field_path!r}; a field path "
                    "must address exactly one value"
                )
            seen.add(entry.field_path)
        object.__setattr__(self, "entries", ordered)

    def field_paths(self) -> tuple[str, ...]:
        return tuple(entry.field_path for entry in self.entries)

    def resolve(self, field_path: str) -> FieldProvenance:
        """The entry for ``field_path``, or a loud failure.

        There is no ``None`` return and no default entry. A consumer that asks
        for a field the input does not carry learns that immediately.
        """

        for entry in self.entries:
            if entry.field_path == field_path:
                return entry
        raise UnresolvableProvenance(
            f"no provenance entry for field path {field_path!r}; the input does not "
            "carry that value, and this module supplies no default for it"
        )

    def require_complete(self, declared_field_paths: Sequence[str]) -> None:
        """Raise unless every declared field of the input has an entry.

        This is the check the acceptance criteria name: a field with no
        provenance source is a failure. It raises even when the ledger is merely
        *shorter* than the declaration, which is the case a naive
        "is the entry present for this one field" check would miss.
        """

        have = set(self.field_paths())
        missing = [path for path in declared_field_paths if path not in have]
        if missing:
            raise ProvenanceIncomplete(sorted(missing))

    def for_class(self, value_class: str) -> tuple[FieldProvenance, ...]:
        return tuple(e for e in self.entries if e.value_class == value_class)

    def unavailable(self) -> tuple[FieldProvenance, ...]:
        return tuple(e for e in self.entries if not e.available)

    def digest(self) -> str:
        """A digest over the whole ledger, for comparing two ledgers."""

        return sha256_digest(
            canonical_json([entry.as_record() for entry in self.entries])
        )

    def as_records(self) -> tuple[dict[str, Any], ...]:
        return tuple(entry.as_record() for entry in self.entries)


# ---------------------------------------------------------------------------
# Display (SR34 / TC23 data)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProvenanceDisplay:
    """One display row: a labelled value with its class and its source.

    This is the deterministic *data* behind the SR34 presentation, not the
    rendered interface. TC23 is a rendered-UI oracle and remains Not run; what
    is testable here is that a row never invents a value, and that the class of
    every row is stated rather than implied by position or colour.
    """

    field_path: str
    value_class: str
    value_class_label: str
    rendered_value: str
    unavailable: bool
    unavailable_reason: str | None
    preparation_version: str
    mapping_reference: str
    source_digest: str

    def as_record(self) -> dict[str, Any]:
        return {
            "field_path": self.field_path,
            "value_class": self.value_class,
            "value_class_label": self.value_class_label,
            "rendered_value": self.rendered_value,
            "unavailable": self.unavailable,
            "unavailable_reason": self.unavailable_reason,
            "preparation_version": self.preparation_version,
            "mapping_reference": self.mapping_reference,
            "source_digest": self.source_digest,
        }


def build_display(ledger: ProvenanceLedger) -> tuple[ProvenanceDisplay, ...]:
    """Render every ledger entry as a labelled row.

    An unavailable value renders as :data:`UNAVAILABLE_LABEL` plus the recorded
    reason. It never renders as ``0``, ``0.0``, an empty string or a guess, and
    it never reuses the presentation of a different value class.
    """

    rows: list[ProvenanceDisplay] = []
    for entry in ledger.entries:
        if entry.available:
            # The canonical text is rendered verbatim: no rounding, no unit
            # conversion, no reformatting. A display step that re-derives a
            # number is a display step that can disagree with the value.
            rendered = str(entry.value_canonical)
            reason = None
        else:
            # The absence reason comes from the recorded warning. An explicit
            # raise, not an assert: `python -O` strips asserts, and a display
            # that then fell through would render a blank instead of saying the
            # value is unavailable.
            if entry.absent is None:  # pragma: no cover - refused at construction
                raise UnresolvableProvenance(
                    f"{entry.field_path} is marked unavailable with no recorded reason; refusing "
                    f"to render it as anything other than {UNAVAILABLE_LABEL}"
                )
            reason = f"{entry.absent.code}/{entry.absent.detail}"
            rendered = f"{UNAVAILABLE_LABEL} ({reason})"
        rows.append(
            ProvenanceDisplay(
                field_path=entry.field_path,
                value_class=entry.value_class,
                value_class_label=VALUE_CLASS_LABELS[entry.value_class],
                rendered_value=rendered,
                unavailable=not entry.available,
                unavailable_reason=reason,
                preparation_version=entry.preparation_version,
                mapping_reference=entry.mapping_reference,
                source_digest=entry.source_digest,
            )
        )
    return tuple(rows)


__all__ = [
    "VALUE_CLASSES",
    "MILESTONE_A_VALUE_CLASSES",
    "VALUE_CLASS_LABELS",
    "VALUE_CLASS_SOURCE_OBSERVATION",
    "VALUE_CLASS_COMPUTED_METRIC",
    "VALUE_CLASS_QUALITY_WARNING",
    "VALUE_CLASS_SCOPE_MEMBER",
    "UNAVAILABLE_LABEL",
    "ABSENT_REASON_CODES",
    "MAX_FIELD_PATH_LENGTH",
    "MAX_ROW_REFERENCE_LENGTH",
    "MAX_VERSION_REFERENCE_LENGTH",
    "FIELD_PATH_SEPARATOR",
    "ProvenanceError",
    "ValueClassUnavailable",
    "ProvenanceIncomplete",
    "UnresolvableProvenance",
    "DuplicateFieldPath",
    "AbsentObservation",
    "ScopedField",
    "FieldProvenance",
    "ProvenanceLedger",
    "ProvenanceDisplay",
    "build_field_path",
    "build_ledger",
    "build_display",
    "require_canonical_identity",
]
