"""Deterministic, model-free normalization for DATARA Milestone A.

This module is conventional software. It opens no socket, calls no model and
holds no credential (SR06, CUS03). Every exported function is a pure function of
its arguments: no clock, no randomness, no environment lookup, no database, no
network. Two preparations of the same accepted input under the same
configuration and version therefore produce byte-identical canonical values and
an identical digest (SR05, TC04 *Preparation reproducibility*).

Contract
--------

Four REQUIRED normalized inputs (D01):

1. ``source_digest``    -- source reference/digest, ``sha256:<64 lowercase hex>``
2. ``sport``            -- must be in ``policy.supported_sports``
3. ``session_start_utc``-- a timezone-aware instant, canonicalised to UTC ``...Z``
4. ``elapsed_duration_seconds`` -- recorded elapsed activity duration, strictly
   positive

OPTIONAL inputs: ``timer_duration_seconds`` (official timer duration, retained
separately), ``distance_value`` + ``distance_unit_code``, ``record_sample_count``,
``gps_point_count``, ``heart_rate_value`` + ``heart_rate_unit_code``.

No imputation, ever. An absent or invalid OPTIONAL value becomes ``null`` plus a
recorded quality warning naming the logical field. A missing or invalid REQUIRED
value rejects the whole file with a stable reason code; the normalizer returns
nothing partial.

Elapsed and timer are never interchanged. Duration-based P0 volume means
recorded *elapsed activity duration* (D01). If elapsed is absent while a timer
duration is present, the file is rejected with
``absent_while_timer_present_not_substituted``: substituting the timer value
would be exactly the silent interchange D01 forbids.

No engineering value range or FIT field mapping is invented here. Every bound and
every supported sport code is supplied by the caller through
:class:`NormalizationPolicy`, whose fields have **no defaults**, because the
authoritative mapping is TK10's to publish. If a needed range is absent from the
policy, the normalizer cannot run and says so rather than guessing. Structural
type invariants that are not FIT-specific (an integer must be an integer; a
duration must be strictly positive; a digest must be ``sha256:`` + 64 lowercase
hex) are enforced here and are documented as such.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from datara import (
    CONTRACT_VERSION,
    ELIGIBILITY_RULE_VERSION,
    NORMALIZER_VERSION,
    PREPARATION_VERSION,
)

# ---------------------------------------------------------------------------
# Stable vocabularies
# ---------------------------------------------------------------------------

#: Rejection reason codes. A code is the contract; ``detail`` narrows it from a
#: fixed vocabulary. Both are validated on construction, so free text cannot
#: creep into a stable code.
REASON_POLICY_INVALID = "REQ_POLICY_INVALID"
REASON_SOURCE_DIGEST_MISSING = "REQ_SOURCE_DIGEST_MISSING"
REASON_SOURCE_DIGEST_MALFORMED = "REQ_SOURCE_DIGEST_MALFORMED"
REASON_SPORT_MISSING = "REQ_SPORT_MISSING"
REASON_SPORT_UNSUPPORTED = "REQ_SPORT_UNSUPPORTED"
REASON_SESSION_START_MISSING = "REQ_SESSION_START_MISSING"
REASON_SESSION_START_INVALID = "REQ_SESSION_START_INVALID"
REASON_ELAPSED_MISSING = "REQ_ELAPSED_DURATION_MISSING"
REASON_ELAPSED_INVALID = "REQ_ELAPSED_DURATION_INVALID"
REASON_ELAPSED_OUT_OF_RANGE = "REQ_ELAPSED_DURATION_OUT_OF_RANGE"

REASON_DETAILS: Mapping[str, frozenset[str]] = {
    REASON_POLICY_INVALID: frozenset(
        {"empty_policy_version", "empty_mapping_reference", "empty_supported_sports", "non_positive_maximum"}
    ),
    REASON_SOURCE_DIGEST_MISSING: frozenset({"absent"}),
    REASON_SOURCE_DIGEST_MALFORMED: frozenset({"not_prefixed_sha256", "not_lowercase_hex_64"}),
    REASON_SPORT_MISSING: frozenset({"absent"}),
    REASON_SPORT_UNSUPPORTED: frozenset({"not_in_policy_supported_sports"}),
    REASON_SESSION_START_MISSING: frozenset({"absent"}),
    REASON_SESSION_START_INVALID: frozenset(
        {"not_a_string_or_datetime", "not_iso8601", "not_timezone_aware", "out_of_range"}
    ),
    REASON_ELAPSED_MISSING: frozenset({"absent", "absent_while_timer_present_not_substituted"}),
    REASON_ELAPSED_INVALID: frozenset({"not_an_integer", "negative", "zero", "boolean_value"}),
    REASON_ELAPSED_OUT_OF_RANGE: frozenset({"above_policy_maximum"}),
}

#: Quality-warning codes for OPTIONAL values.
WARNING_ABSENT = "OPT_ABSENT"
WARNING_INVALID = "OPT_INVALID"
WARNING_OUT_OF_RANGE = "OPT_OUT_OF_RANGE"
WARNING_UNIT_CODE_ABSENT = "OPT_UNIT_CODE_ABSENT"

#: The logical optional fields, and the canonical payload keys each one owns.
#: A logical field is null exactly when *all* of its keys are null, and that is
#: equivalent to at least one warning naming the field. This is a machine-checked
#: invariant, asserted by `datara/tests/test_normalization.py`.
OPTIONAL_FIELDS: tuple[str, ...] = (
    "timer_duration",
    "distance",
    "record_samples",
    "gps",
    "heart_rate",
)

OPTIONAL_PAYLOAD_KEYS: Mapping[str, tuple[str, ...]] = {
    "timer_duration": ("timer_duration_seconds",),
    "distance": ("distance_value", "distance_unit_code"),
    "record_samples": ("record_sample_count",),
    "gps": ("gps_point_count",),
    "heart_rate": ("heart_rate_value", "heart_rate_unit_code"),
}

WARNING_DETAILS: Mapping[tuple[str, str], frozenset[str]] = {
    ("timer_duration", WARNING_ABSENT): frozenset({"absent"}),
    ("timer_duration", WARNING_INVALID): frozenset({"not_an_integer", "negative", "boolean_value"}),
    ("timer_duration", WARNING_OUT_OF_RANGE): frozenset({"above_policy_maximum"}),
    ("distance", WARNING_ABSENT): frozenset({"absent"}),
    ("distance", WARNING_INVALID): frozenset({"not_an_integer", "negative", "boolean_value"}),
    ("distance", WARNING_OUT_OF_RANGE): frozenset({"above_policy_maximum"}),
    ("distance", WARNING_UNIT_CODE_ABSENT): frozenset({"unit_code_absent_for_supplied_value"}),
    ("record_samples", WARNING_ABSENT): frozenset({"absent"}),
    ("record_samples", WARNING_INVALID): frozenset({"not_an_integer", "negative", "boolean_value"}),
    ("record_samples", WARNING_OUT_OF_RANGE): frozenset({"above_policy_maximum"}),
    ("gps", WARNING_ABSENT): frozenset({"absent", "zero_or_negative_point_count_reported"}),
    ("gps", WARNING_INVALID): frozenset({"not_an_integer", "negative", "boolean_value"}),
    ("gps", WARNING_OUT_OF_RANGE): frozenset({"above_policy_maximum"}),
    ("heart_rate", WARNING_ABSENT): frozenset({"absent"}),
    ("heart_rate", WARNING_INVALID): frozenset({"not_an_integer", "negative", "boolean_value"}),
    ("heart_rate", WARNING_OUT_OF_RANGE): frozenset({"above_policy_maximum"}),
    ("heart_rate", WARNING_UNIT_CODE_ABSENT): frozenset({"unit_code_absent_for_supplied_value"}),
}

_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_INSTANT_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d{1,9})?([Zz]|[+-]\d{2}:\d{2})?$"
)
_INT_RE = re.compile(r"^-?\d+$")


class VocabularyError(Exception):
    """A code/detail pair outside the frozen vocabulary was constructed."""


# ---------------------------------------------------------------------------
# Canonical serialization
# ---------------------------------------------------------------------------


def canonical_json(payload: Mapping[str, Any]) -> str:
    """Serialize deterministically.

    Sorted keys, no insignificant whitespace, ASCII-escaped, NaN/Infinity
    refused. Every numeric normalized value is carried as a decimal *string* with
    a fixed number of digits, because D02 requires canonical fixed precision and
    a binary float is not one.
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def sha256_digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def digest_matches(value: str) -> bool:
    return bool(_DIGEST_RE.match(value))


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class NormalizationRejection(Exception):
    """A whole-file rejection with a stable reason code.

    Raising this means no normalized record was produced. A rejected file
    contributes no partial accepted activity (D01).
    """

    def __init__(self, reason_code: str, reason_detail: str, field_name: str | None = None) -> None:
        allowed = REASON_DETAILS.get(reason_code)
        if allowed is None or reason_detail not in allowed:
            raise VocabularyError(
                f"reason {reason_code!r} does not accept detail {reason_detail!r}"
            )
        self.reason_code = reason_code
        self.reason_detail = reason_detail
        self.field = field_name
        super().__init__(f"{reason_code}/{reason_detail} ({field_name or '-'})")

    def as_record(self) -> dict[str, str | None]:
        return {
            "reason_code": self.reason_code,
            "reason_detail": self.reason_detail,
            "field": self.field,
        }


class ScopePreparationError(Exception):
    """The supplied scope cannot produce one deterministic snapshot."""


@dataclass(frozen=True)
class QualityWarning:
    """A recorded data-quality observation. Not a finding, and not a verdict."""

    code: str
    field: str
    detail: str
    source_field: str | None = None

    def __post_init__(self) -> None:
        allowed = WARNING_DETAILS.get((self.field, self.code))
        if allowed is None or self.detail not in allowed:
            raise VocabularyError(
                f"warning {self.code!r} on field {self.field!r} does not accept detail {self.detail!r}"
            )

    def as_record(self) -> dict[str, str | None]:
        return {
            "code": self.code,
            "field": self.field,
            "detail": self.detail,
            "source_field": self.source_field,
        }


# ---------------------------------------------------------------------------
# Policy and input
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NormalizationPolicy:
    """Caller-supplied approved configuration.

    Every field has no default on purpose. The authoritative supported-sport list
    and engineering value ranges are TK10's deliverable; this task defines the
    shape and requires the caller to supply the values. A missing range is a
    refusal to run, never a guessed bound.
    """

    policy_version: str
    mapping_reference: str
    supported_sports: frozenset[str]
    max_elapsed_duration_seconds: int
    max_timer_duration_seconds: int
    max_distance_value: int
    max_record_sample_count: int
    max_gps_point_count: int
    max_heart_rate_value: int

    def canonical(self) -> dict[str, Any]:
        return {
            "policy_version": self.policy_version,
            "mapping_reference": self.mapping_reference,
            "supported_sports": sorted(self.supported_sports),
            "max_elapsed_duration_seconds": self.max_elapsed_duration_seconds,
            "max_timer_duration_seconds": self.max_timer_duration_seconds,
            "max_distance_value": self.max_distance_value,
            "max_record_sample_count": self.max_record_sample_count,
            "max_gps_point_count": self.max_gps_point_count,
            "max_heart_rate_value": self.max_heart_rate_value,
        }


@dataclass(frozen=True)
class RawActivityInput:
    """What the source layer hands to preparation.

    Field names are *normalized* names, not FIT field names. How a value was
    obtained, and within which declared range it is valid, belongs to the mapping
    reference recorded in ``source_fields``; this task neither defines nor
    invents that mapping (TK10).
    """

    source_digest: str | None = None
    sport: str | None = None
    session_start_utc: Any = None
    elapsed_duration_seconds: Any = None

    timer_duration_seconds: Any = None
    distance_value: Any = None
    distance_unit_code: str | None = None
    record_sample_count: Any = None
    gps_point_count: Any = None
    heart_rate_value: Any = None
    heart_rate_unit_code: str | None = None

    #: Provenance per logical field; a declared source field path or null. Part
    #: of the canonical payload, so provenance is part of the digest.
    source_fields: Mapping[str, str | None] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Scalar parsing
# ---------------------------------------------------------------------------


def _parse_integer(value: Any) -> tuple[int | None, str | None]:
    """Parse a canonical non-negative integer, or report a stable problem.

    ``bool`` is rejected explicitly: ``True`` is an ``int`` in Python and would
    otherwise become the second of one second. ``float`` is rejected because a
    binary float is not a canonical fixed-precision representation of an
    integral duration or count.
    """
    if value is None:
        return None, "absent"
    if isinstance(value, bool):
        return None, "boolean_value"
    if isinstance(value, int):
        return value, None
    if isinstance(value, str) and _INT_RE.match(value):
        return int(value), None
    return None, "not_an_integer"


def _parse_instant(value: Any) -> tuple[datetime | None, str | None]:
    """Parse a timezone-aware instant into an aware UTC ``datetime``.

    An explicitly offset instant such as ``2026-10-01T08:30:00+02:00`` is
    accepted and converted: the conversion is exact and deterministic, so
    rejecting it would reject valid data for no reproducibility gain. A *naive*
    value is refused, because a wall-clock reading with no offset is ambiguous
    and guessing an offset would be inventing a mapping.
    """
    if value is None:
        return None, "absent"
    if isinstance(value, datetime):
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return None, "not_timezone_aware"
        return value.astimezone(timezone.utc), None
    if not isinstance(value, str):
        return None, "not_a_string_or_datetime"
    if not _INSTANT_RE.match(value):
        return None, "not_iso8601"
    text = value[:-1] + "+00:00" if value[-1] in "Zz" else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None, "not_iso8601"
    if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
        return None, "not_timezone_aware"
    return parsed.astimezone(timezone.utc), None


def canonical_instant(moment: datetime) -> str:
    """RFC 3339 UTC with fixed width: second precision, or exactly 6 fraction digits."""
    moment = moment.astimezone(timezone.utc)
    if moment.microsecond:
        return moment.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
    return moment.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NormalizedActivity:
    """The normalized record for one accepted activity."""

    contract_version: str
    normalizer_version: str
    policy_version: str
    mapping_reference: str

    source_digest: str
    sport: str
    session_start_utc: str
    elapsed_duration_seconds: int

    timer_duration_seconds: int | None
    distance_value: int | None
    distance_unit_code: str | None
    record_sample_count: int | None
    gps_point_count: int | None
    heart_rate_value: int | None
    heart_rate_unit_code: str | None

    quality_warnings: tuple[QualityWarning, ...]
    canonical_payload: str
    normalization_digest: str

    @property
    def optional_keys(self) -> dict[str, str | None]:
        return {
            "timer_duration_seconds": _as_text(self.timer_duration_seconds),
            "distance_value": _as_text(self.distance_value),
            "distance_unit_code": self.distance_unit_code,
            "record_sample_count": _as_text(self.record_sample_count),
            "gps_point_count": _as_text(self.gps_point_count),
            "heart_rate_value": _as_text(self.heart_rate_value),
            "heart_rate_unit_code": self.heart_rate_unit_code,
        }

    def has_only_required_inputs(self) -> bool:
        return all(value is None for value in self.optional_keys.values())


def _as_text(value: int | None) -> str | None:
    return None if value is None else str(value)


def _validate_policy(policy: NormalizationPolicy) -> None:
    if not policy.policy_version:
        raise NormalizationRejection(REASON_POLICY_INVALID, "empty_policy_version")
    if not policy.mapping_reference:
        raise NormalizationRejection(REASON_POLICY_INVALID, "empty_mapping_reference")
    if not policy.supported_sports:
        raise NormalizationRejection(REASON_POLICY_INVALID, "empty_supported_sports")
    for name in (
        "max_elapsed_duration_seconds",
        "max_timer_duration_seconds",
        "max_distance_value",
        "max_record_sample_count",
        "max_gps_point_count",
        "max_heart_rate_value",
    ):
        bound = getattr(policy, name)
        if isinstance(bound, bool) or not isinstance(bound, int) or bound <= 0:
            raise NormalizationRejection(REASON_POLICY_INVALID, "non_positive_maximum")


def normalize(raw: RawActivityInput, policy: NormalizationPolicy) -> NormalizedActivity:
    """Normalize one accepted activity. Pure; raises on any required-field failure.

    Rejection order is fixed and documented so the reason code is stable:
    policy, source digest, sport, session start instant, elapsed duration.
    """
    _validate_policy(policy)
    warnings: list[QualityWarning] = []

    def provenance(name: str) -> str | None:
        return raw.source_fields.get(name)

    # --- required: source digest ------------------------------------------
    if raw.source_digest is None:
        raise NormalizationRejection(REASON_SOURCE_DIGEST_MISSING, "absent", "source_digest")
    if not isinstance(raw.source_digest, str):
        raise NormalizationRejection(REASON_SOURCE_DIGEST_MALFORMED, "not_prefixed_sha256", "source_digest")
    if not raw.source_digest.startswith("sha256:"):
        raise NormalizationRejection(REASON_SOURCE_DIGEST_MALFORMED, "not_prefixed_sha256", "source_digest")
    if not _DIGEST_RE.match(raw.source_digest):
        raise NormalizationRejection(REASON_SOURCE_DIGEST_MALFORMED, "not_lowercase_hex_64", "source_digest")
    source_digest = raw.source_digest

    # --- required: sport ---------------------------------------------------
    if raw.sport is None:
        raise NormalizationRejection(REASON_SPORT_MISSING, "absent", "sport")
    if not isinstance(raw.sport, str) or not raw.sport:
        raise NormalizationRejection(REASON_SPORT_MISSING, "absent", "sport")
    sport = raw.sport
    if sport not in policy.supported_sports:
        raise NormalizationRejection(
            REASON_SPORT_UNSUPPORTED, "not_in_policy_supported_sports", "sport"
        )

    # --- required: session UTC start instant --------------------------------
    if raw.session_start_utc is None:
        raise NormalizationRejection(REASON_SESSION_START_MISSING, "absent", "session_start_utc")
    moment, problem = _parse_instant(raw.session_start_utc)
    if moment is None:
        code = REASON_SESSION_START_MISSING if problem == "absent" else REASON_SESSION_START_INVALID
        raise NormalizationRejection(code, problem or "not_iso8601", "session_start_utc")
    session_start_utc = canonical_instant(moment)

    # --- required: elapsed activity duration --------------------------------
    elapsed, problem = _parse_integer(raw.elapsed_duration_seconds)
    if elapsed is None:
        if problem == "absent":
            # The explicit anti-substitution rule. If a timer duration was
            # supplied, it is *not* used as elapsed; the file is rejected.
            detail = (
                "absent_while_timer_present_not_substituted"
                if _parse_integer(raw.timer_duration_seconds)[0] is not None
                else "absent"
            )
            raise NormalizationRejection(REASON_ELAPSED_MISSING, detail, "elapsed_duration_seconds")
        raise NormalizationRejection(REASON_ELAPSED_INVALID, problem, "elapsed_duration_seconds")
    if elapsed < 0:
        raise NormalizationRejection(REASON_ELAPSED_INVALID, "negative", "elapsed_duration_seconds")
    if elapsed == 0:
        raise NormalizationRejection(REASON_ELAPSED_INVALID, "zero", "elapsed_duration_seconds")
    if elapsed > policy.max_elapsed_duration_seconds:
        raise NormalizationRejection(
            REASON_ELAPSED_OUT_OF_RANGE, "above_policy_maximum", "elapsed_duration_seconds"
        )

    # --- optional -----------------------------------------------------------
    def optional_count(
        value: Any, logical: str, maximum: int
    ) -> int | None:
        source_field = provenance(logical)
        parsed, issue = _parse_integer(value)
        if parsed is None:
            if issue == "absent":
                warnings.append(QualityWarning(WARNING_ABSENT, logical, "absent", source_field))
            elif issue == "negative":
                warnings.append(QualityWarning(WARNING_INVALID, logical, "negative", source_field))
            elif issue == "boolean_value":
                warnings.append(QualityWarning(WARNING_INVALID, logical, "boolean_value", source_field))
            else:
                warnings.append(QualityWarning(WARNING_INVALID, logical, "not_an_integer", source_field))
            return None
        if logical == "gps" and parsed == 0:
            warnings.append(
                QualityWarning(WARNING_ABSENT, logical, "zero_or_negative_point_count_reported", source_field)
            )
            return None
        if parsed > maximum:
            warnings.append(QualityWarning(WARNING_OUT_OF_RANGE, logical, "above_policy_maximum", source_field))
            return None
        return parsed

    def optional_quantity(
        value: Any, unit_code: str | None, logical: str, maximum: int
    ) -> tuple[int | None, str | None]:
        """A value without a declared unit code is not a usable measurement.

        Assuming a unit would be inventing an engineering mapping (TK10), so the
        value is discarded with a warning instead.
        """
        source_field = provenance(logical)
        if value is None:
            warnings.append(QualityWarning(WARNING_ABSENT, logical, "absent", source_field))
            return None, None
        if not unit_code:
            warnings.append(
                QualityWarning(WARNING_UNIT_CODE_ABSENT, logical, "unit_code_absent_for_supplied_value", source_field)
            )
            return None, None
        parsed = optional_count(value, logical, maximum)
        if parsed is None:
            # The unit code belongs to the measurement. A discarded measurement
            # does not leave a dangling unit behind.
            return None, None
        return parsed, unit_code

    timer_seconds = optional_count(raw.timer_duration_seconds, "timer_duration", policy.max_timer_duration_seconds)
    distance_value, distance_unit = optional_quantity(
        raw.distance_value, raw.distance_unit_code, "distance", policy.max_distance_value
    )
    record_samples = optional_count(raw.record_sample_count, "record_samples", policy.max_record_sample_count)
    gps_points = optional_count(raw.gps_point_count, "gps", policy.max_gps_point_count)
    heart_rate_value, heart_rate_unit = optional_quantity(
        raw.heart_rate_value, raw.heart_rate_unit_code, "heart_rate", policy.max_heart_rate_value
    )

    warnings.sort(key=lambda w: (w.field, w.code, w.detail, w.source_field or ""))
    warnings_tuple = tuple(warnings)

    optional_keys: dict[str, str | None] = {
        "timer_duration_seconds": _as_text(timer_seconds),
        "distance_value": _as_text(distance_value),
        "distance_unit_code": distance_unit,
        "record_sample_count": _as_text(record_samples),
        "gps_point_count": _as_text(gps_points),
        "heart_rate_value": _as_text(heart_rate_value),
        "heart_rate_unit_code": heart_rate_unit,
    }

    # The no-imputation invariant, enforced in code rather than asserted in prose:
    # every logical optional field is null exactly when a warning names it.
    for logical, keys in OPTIONAL_PAYLOAD_KEYS.items():
        is_null = all(optional_keys[key] is None for key in keys)
        warned = any(w.field == logical for w in warnings_tuple)
        if is_null != warned:
            raise AssertionError(
                f"optional-field invariant violated for {logical!r}: "
                f"is_null={is_null} warned={warned}"
            )

    provenance_map = {logical: provenance(logical) for logical in OPTIONAL_FIELDS}
    provenance_map["source_digest"] = provenance("source_digest")
    provenance_map["sport"] = provenance("sport")
    provenance_map["session_start_utc"] = provenance("session_start_utc")
    provenance_map["elapsed_duration_seconds"] = provenance("elapsed_duration_seconds")

    payload: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "normalizer_version": NORMALIZER_VERSION,
        "policy": policy.canonical(),
        "required": {
            "source_digest": source_digest,
            "sport": sport,
            "session_start_utc": session_start_utc,
            "elapsed_duration_seconds": str(elapsed),
        },
        "optional": optional_keys,
        "provenance": {key: provenance_map[key] for key in sorted(provenance_map)},
        "quality_warnings": [w.as_record() for w in warnings_tuple],
    }
    text = canonical_json(payload)

    return NormalizedActivity(
        contract_version=CONTRACT_VERSION,
        normalizer_version=NORMALIZER_VERSION,
        policy_version=policy.policy_version,
        mapping_reference=policy.mapping_reference,
        source_digest=source_digest,
        sport=sport,
        session_start_utc=session_start_utc,
        elapsed_duration_seconds=elapsed,
        timer_duration_seconds=timer_seconds,
        distance_value=distance_value,
        distance_unit_code=distance_unit,
        record_sample_count=record_samples,
        gps_point_count=gps_points,
        heart_rate_value=heart_rate_value,
        heart_rate_unit_code=heart_rate_unit,
        quality_warnings=warnings_tuple,
        canonical_payload=text,
        normalization_digest=sha256_digest(text),
    )


# ---------------------------------------------------------------------------
# Snapshot preparation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExcludedActivity:
    """One activity deliberately kept out of the scope, with its reason code."""

    activity_ref: str
    reason_code: str


@dataclass(frozen=True)
class SnapshotPreparation:
    """The deterministic prepared scope."""

    contract_version: str
    preparation_version: str
    policy_version: str
    mapping_reference: str
    scope_kind: str
    scope_start_utc: str | None
    scope_end_utc: str | None
    included_digests: tuple[str, ...]
    included_count: int
    excluded_count: int
    exclusions: tuple[ExcludedActivity, ...]
    canonical_payload: str
    snapshot_digest: str

    def as_record(self) -> dict[str, Any]:
        return {
            "scope_kind": self.scope_kind,
            "scope_start_utc": self.scope_start_utc,
            "scope_end_utc": self.scope_end_utc,
            "included_count": self.included_count,
            "excluded_count": self.excluded_count,
            "exclusions": [
                {"activity_ref": e.activity_ref, "reason_code": e.reason_code}
                for e in self.exclusions
            ],
        }


def prepare_snapshot(
    *,
    normalized: Sequence[NormalizedActivity],
    excluded: Sequence[ExcludedActivity],
    policy: NormalizationPolicy,
    scope_kind: str,
    scope_start_utc: datetime | None = None,
    scope_end_utc: datetime | None = None,
    preparation_version: str = PREPARATION_VERSION,
) -> SnapshotPreparation:
    """Bind a canonical scope to a digest. Pure.

    The digest covers the scope, the versions, the policy, the *sorted* set of
    included activity normalization digests and the *sorted* exclusion list. It
    therefore does not depend on the order in which activities were supplied. It
    excludes the owner id, any generated identifier and any processing timestamp,
    because SR05 excludes generated identifiers and processing timestamps.
    """
    _validate_policy(policy)
    for item in normalized:
        if item.policy_version != policy.policy_version or item.mapping_reference != policy.mapping_reference:
            raise ScopePreparationError(
                "every included activity must share the scope policy and mapping reference; "
                f"{item.normalization_digest} has "
                f"{item.policy_version}/{item.mapping_reference}"
            )

    included = tuple(sorted(item.normalization_digest for item in normalized))
    if len(set(included)) != len(included):
        raise ScopePreparationError("a scope cannot include the same activity digest twice")

    exclusions = tuple(sorted(excluded, key=lambda e: (e.activity_ref, e.reason_code)))

    payload: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "preparation_version": preparation_version,
        "normalizer_version": NORMALIZER_VERSION,
        "policy": policy.canonical(),
        "scope": {
            "kind": scope_kind,
            "start_utc": canonical_instant(scope_start_utc) if scope_start_utc else None,
            "end_utc": canonical_instant(scope_end_utc) if scope_end_utc else None,
        },
        "included_digests": list(included),
        "included_count": len(included),
        "excluded_count": len(exclusions),
        "exclusions": [
            {"activity_ref": e.activity_ref, "reason_code": e.reason_code}
            for e in exclusions
        ],
    }
    text = canonical_json(payload)

    return SnapshotPreparation(
        contract_version=CONTRACT_VERSION,
        preparation_version=preparation_version,
        policy_version=policy.policy_version,
        mapping_reference=policy.mapping_reference,
        scope_kind=scope_kind,
        scope_start_utc=payload["scope"]["start_utc"],
        scope_end_utc=payload["scope"]["end_utc"],
        included_digests=included,
        included_count=len(included),
        excluded_count=len(exclusions),
        exclusions=exclusions,
        canonical_payload=text,
        snapshot_digest=sha256_digest(text),
    )


# ---------------------------------------------------------------------------
# Eligibility (pure, deterministic, no model call)
# ---------------------------------------------------------------------------

COMPARATOR_AT_LEAST = "at_least"
COMPARATOR_AT_MOST = "at_most"
COMPARATOR_EQUALS = "equals"
COMPARATOR_PRESENT = "present"
COMPARATORS = (
    COMPARATOR_AT_LEAST,
    COMPARATOR_AT_MOST,
    COMPARATOR_EQUALS,
    COMPARATOR_PRESENT,
)


@dataclass(frozen=True)
class EligibilityRequirement:
    """One declared requirement, supplied by the caller.

    No skill definition exists in Milestone A (``SkillDefinition`` is an excluded
    entity), so requirements arrive as plain data rather than as a catalogue
    entity.
    """

    requirement_id: str
    description: str
    source_key: str
    comparator: str
    required_value: int | str | None = None

    def __post_init__(self) -> None:
        if self.comparator not in COMPARATORS:
            raise VocabularyError(f"unknown comparator {self.comparator!r}")
        if self.comparator != COMPARATOR_PRESENT and self.required_value is None:
            raise VocabularyError(
                f"requirement {self.requirement_id!r} needs a required_value for {self.comparator!r}"
            )


@dataclass(frozen=True)
class EligibilityDecision:
    """A rule version, a boolean, and an explanation for every unmet requirement."""

    rule_set_version: str
    rule_version: str
    eligible: bool
    unmet_requirements: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]

    def as_record(self) -> dict[str, Any]:
        return {
            "rule_set_version": self.rule_set_version,
            "rule_version": self.rule_version,
            "eligible": self.eligible,
            "unmet_requirements": [dict(item) for item in self.unmet_requirements],
            "warnings": list(self.warnings),
        }


def evaluate_eligibility(
    *,
    observations: Mapping[str, int | str | None],
    requirements: Sequence[EligibilityRequirement],
    rule_set_version: str,
    rule_version: str = ELIGIBILITY_RULE_VERSION,
) -> EligibilityDecision:
    """Decide eligibility deterministically and explain every unmet requirement.

    Pure: the only inputs are the two arguments. It makes no model call and
    therefore no ineligible scope can turn into a provider request (CUS05,
    SR10-SR11).
    """
    unmet: list[dict[str, Any]] = []
    warnings: list[str] = []

    seen: set[str] = set()
    for requirement in requirements:
        if requirement.requirement_id in seen:
            raise ValueError(f"duplicate requirement_id {requirement.requirement_id!r}")
        seen.add(requirement.requirement_id)
        observed = observations.get(requirement.source_key)

        if requirement.comparator == COMPARATOR_PRESENT:
            satisfied = observed is not None
        elif observed is None:
            satisfied = False
        elif requirement.comparator == COMPARATOR_AT_LEAST:
            satisfied = _comparable(observed, requirement.required_value) and observed >= requirement.required_value
        elif requirement.comparator == COMPARATOR_AT_MOST:
            satisfied = _comparable(observed, requirement.required_value) and observed <= requirement.required_value
        else:  # equals
            satisfied = observed == requirement.required_value

        if not satisfied:
            unmet.append(
                {
                    "requirement_id": requirement.requirement_id,
                    "description": requirement.description,
                    "source_key": requirement.source_key,
                    "comparator": requirement.comparator,
                    "required_value": requirement.required_value,
                    "observed_value": observed,
                }
            )
        if requirement.source_key not in observations:
            warnings.append(
                f"{requirement.requirement_id}: source key {requirement.source_key!r} was not observed"
            )

    unmet.sort(key=lambda item: item["requirement_id"])
    return EligibilityDecision(
        rule_set_version=rule_set_version,
        rule_version=rule_version,
        eligible=not unmet,
        unmet_requirements=tuple(unmet),
        warnings=tuple(sorted(warnings)),
    )


def _comparable(observed: Any, required: Any) -> bool:
    if isinstance(observed, bool) or isinstance(required, bool):
        return False
    if isinstance(observed, int) and isinstance(required, int):
        return True
    if isinstance(observed, str) and isinstance(required, str):
        return True
    return False


__all__ = [
    "REASON_DETAILS",
    "WARNING_DETAILS",
    "OPTIONAL_FIELDS",
    "OPTIONAL_PAYLOAD_KEYS",
    "VocabularyError",
    "NormalizationRejection",
    "ScopePreparationError",
    "QualityWarning",
    "NormalizationPolicy",
    "RawActivityInput",
    "NormalizedActivity",
    "ExcludedActivity",
    "SnapshotPreparation",
    "EligibilityRequirement",
    "EligibilityDecision",
    "canonical_json",
    "sha256_digest",
    "digest_matches",
    "canonical_instant",
    "normalize",
    "prepare_snapshot",
    "evaluate_eligibility",
]
