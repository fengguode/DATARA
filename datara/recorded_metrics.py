"""Internal D02 recorded elapsed/count preparation, without persistence.

WP02/WP03; CUS03-05; SR05-11, SR28-29. This is prepared numeric
content, not an assessment, saved Metric capability or authorization evidence.
Only the supported immutable scoped source contract is accepted. Database users
must separately establish owner-scoped retrieval and persisted provenance.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from fractions import Fraction
import hashlib
import json
import re

from datara import NORMALIZER_VERSION
from datara.canonical import canonical_sport_code, require_elapsed_duration_ms
from datara.normalization import QualityWarning, canonical_json, sha256_digest, _validate_policy
from datara.provenance import build_ledger, VALUE_CLASS_SCOPE_MEMBER
from datara.scoped_input import (
    EXCLUSION_REASON_SET, HEADER_FIELDS, MILESTONE_A_FIELD_SOURCES, SCOPED_INPUT_CONTRACT_VERSION,
    SCOPED_INPUT_VERSION, ScopedInputVersion, assert_no_prohibited_content,
    require_declared,
)

METRIC_CONTRACT_VERSION = "datara/internal-recorded-metrics/1"
ADAPTER_VERSION = "scoped-recorded-core/1"
MANIFEST_VERSION = "recorded-membership/1"
CODEC_VERSION = "ascii-json-integer-strings/1"
_CORE = ("sport", "start_epoch_seconds", "elapsed_duration_ms")
_INTEGER = re.compile(r"(?:0|[1-9][0-9]*|-[1-9][0-9]*)\Z")
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_WEEK = 7 * 86400
_LIMITATIONS = ("recorded_data_only", "utc_start_attribution", "optional_metrics_excluded")
# Semantic specification identity is independent of a checkout or generated ID.
_SPECIFICATION = (
    "D02 recorded elapsed/count v1; scoped-input/1 core projection; exact ms; "
    "unique members; per-sport summary; overall last four complete Monday UTC "
    "weeks wholly in scope; scope >=28 days; recorded activity in >=3/4 weeks; "
    "E=first2,L=last2,D=L-E,magnitude=abs(D),percent=100D/E reduced; "
    "exact sign; empty recorded buckets=0; no timer/distance/consistency"
)
_SPECIFICATION_DIGEST = sha256_digest(_SPECIFICATION)


class RecordedInputRefusal(ValueError):
    """Unsupported or inconsistent source content; no partial input is returned."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True)
class SourceOperand:
    source_digest: str
    normalization_digest: str
    source_field_path: str
    preparation_version: str
    mapping_reference: str
    value: str

    def as_record(self) -> dict:
        return {
            "source_digest": self.source_digest,
            "normalization_digest": self.normalization_digest,
            "source_field_path": self.source_field_path,
            "preparation_version": self.preparation_version,
            "mapping_reference": self.mapping_reference,
            "value": self.value,
        }


@dataclass(frozen=True)
class RecordedMember:
    normalization_digest: str
    source_digest: str
    start_epoch_seconds: int
    sport: str
    elapsed_ms: int
    operands: tuple[SourceOperand, ...]

    def as_record(self) -> dict:
        return {
            "normalization_digest": self.normalization_digest,
            "source_digest": self.source_digest,
            "start_utc": _utc(self.start_epoch_seconds),
            "sport": self.sport,
            "operands": [operand.as_record() for operand in self.operands],
        }


@dataclass(frozen=True)
class RecordedExclusion:
    normalization_digest: str
    reason_code: str
    multiplicity: int

    def as_record(self) -> dict:
        return {"normalization_digest": self.normalization_digest,
                "reason_code": self.reason_code, "multiplicity": str(self.multiplicity)}


@dataclass(frozen=True)
class RecordedMetricInput:
    input_content_digest: str
    selected_scope_content: bytes
    start_epoch_seconds: int
    end_epoch_seconds: int
    members: tuple[RecordedMember, ...]
    exclusions: tuple[RecordedExclusion, ...]
    adapter_version: str = ADAPTER_VERSION


@dataclass(frozen=True)
class ExactValue:
    """Available integer/fraction or unavailable value with no numeric placeholder."""
    unit: str
    precision: str
    integer: int | None = None
    fraction: Fraction | None = None
    unavailable_reason: str | None = None

    def __post_init__(self) -> None:
        if sum(x is not None for x in (self.integer, self.fraction, self.unavailable_reason)) != 1:
            raise ValueError("an exact value must have exactly one availability representation")
        if self.integer is not None and type(self.integer) is not int:
            raise TypeError("exact integer required")
        if self.fraction is not None and not isinstance(self.fraction, Fraction):
            raise TypeError("exact fraction required")

    def as_record(self) -> dict:
        result = {"unit": self.unit, "precision": self.precision}
        if self.unavailable_reason is not None:
            result.update(status="unavailable", reason_code=self.unavailable_reason)
        elif self.integer is not None:
            result.update(status="available", value=str(self.integer))
        else:
            result.update(status="available", numerator=str(self.fraction.numerator),
                          denominator=str(self.fraction.denominator))
        return result


@dataclass(frozen=True)
class SportSummary:
    sport: str
    members: tuple[str, ...]
    activity_count: ExactValue
    elapsed_ms: ExactValue


@dataclass(frozen=True)
class RecordedWeek:
    start_epoch_seconds: int
    end_epoch_seconds: int
    members: tuple[str, ...]
    activity_count: ExactValue
    elapsed_ms: ExactValue

    def as_record(self) -> dict:
        return {"start_utc": _utc(self.start_epoch_seconds),
                "end_utc": _utc(self.end_epoch_seconds), "grouping": "overall",
                "members": list(self.members), "count": str(len(self.members)),
                "elapsed_ms": self.elapsed_ms.as_record(),
                "limitations": ["recorded_data_only"] + ([] if self.members else ["missing_records"])}


@dataclass(frozen=True)
class PreparedSummary:
    eligible: bool
    unmet_reasons: tuple[str, ...]
    groups: tuple[SportSummary, ...]
    canonical_content: bytes


@dataclass(frozen=True)
class PreparedTrend:
    eligible: bool
    unmet_reasons: tuple[str, ...]
    weeks: tuple[RecordedWeek, ...]
    outside_comparison: tuple[str, ...]
    earlier_total: ExactValue
    later_total: ExactValue
    signed_difference: ExactValue
    magnitude: ExactValue
    percentage: ExactValue
    classification: str | None
    canonical_content: bytes


def _integer(text: str, *, positive: bool = False) -> int:
    if not isinstance(text, str) or not _INTEGER.fullmatch(text):
        raise RecordedInputRefusal("noncanonical_integer")
    value = int(text)
    if value < 0 or (positive and value == 0):
        raise RecordedInputRefusal("invalid_source_integer")
    return value


def _utc(epoch: int) -> str:
    return (_EPOCH + timedelta(seconds=epoch)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _codec(value: dict) -> bytes:
    """Canonical metric JSON; integers in content must be decimal strings."""
    def check(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if not isinstance(key, str) or not key.isascii():
                    raise RecordedInputRefusal("nonportable_content")
                check(child)
        elif isinstance(node, (list, tuple)):
            for child in node:
                check(child)
        elif isinstance(node, str):
            if not node.isascii():
                raise RecordedInputRefusal("nonportable_content")
        elif node is not None and type(node) is not bool:
            raise RecordedInputRefusal("nonportable_content")
    check(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def _source_payload(version: ScopedInputVersion) -> dict:
    # Reconstruct every supported source field, rather than hashing arbitrary text.
    return {
        "contract_version": SCOPED_INPUT_CONTRACT_VERSION,
        "scoped_input_version": SCOPED_INPUT_VERSION,
        "preparation_version": version.scope.preparation_version,
        "normalizer_version": NORMALIZER_VERSION,
        "policy": version.policy.canonical(), "scope": version.scope.as_record(),
        "declared": [spec.as_record() for spec in sorted(version.declared, key=lambda s: s.field_name)],
        "records": [record.as_record() for record in sorted(version.records, key=lambda r: r.canonical_identity)],
        "record_count": len(version.records), "excluded_count": len(version.exclusions),
        "exclusions": [item.as_record() for item in sorted(version.exclusions,
                       key=lambda e: (e.canonical_identity, e.reason_code))],
    }


def prepare_recorded_input(version: ScopedInputVersion) -> RecordedMetricInput:
    """Validate full source content/ledger, then project immutable core operands.

    Optional values and their recorded absence are structurally validated but
    never calculated or copied into the metric operand projection. The full
    original scoped input digest remains the binding, including optional data.
    """
    try:
        return _prepare_recorded_input(version)
    except RecordedInputRefusal:
        raise
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise RecordedInputRefusal("invalid_scoped_input") from exc
    except Exception as exc:
        # Existing scoped/provenance contract exceptions do not inherit ValueError.
        # Do not include untrusted source values or diagnostics in the safe reason.
        raise RecordedInputRefusal("invalid_scoped_input") from exc


def _prepare_recorded_input(version: ScopedInputVersion) -> RecordedMetricInput:
    if type(version) is not ScopedInputVersion:
        raise RecordedInputRefusal("unsupported_input_type")
    if (version.contract_version != SCOPED_INPUT_CONTRACT_VERSION
            or version.scoped_input_version != SCOPED_INPUT_VERSION):
        raise RecordedInputRefusal("unsupported_input_version")
    payload = _source_payload(version)
    assert_no_prohibited_content(payload)
    if (canonical_json(payload) != version.canonical_payload
            or sha256_digest(version.canonical_payload) != version.input_digest):
        raise RecordedInputRefusal("input_content_mismatch")
    reconstructed = ScopedInputVersion.from_canonical_payload(version.canonical_payload)
    if canonical_json(_source_payload(reconstructed)) != version.canonical_payload:
        raise RecordedInputRefusal("unsupported_source_shape")
    expected_ledger = build_ledger((r.canonical_identity, r.source_digest, r.fields)
                                  for r in reconstructed.records)
    if version.ledger != expected_ledger:
        raise RecordedInputRefusal("lineage_mismatch")
    declared = require_declared(reconstructed.declared)
    specs = {spec.field_name: spec for spec in declared}
    if not set(_CORE).issubset(specs):
        raise RecordedInputRefusal("core_declaration_missing")
    for spec in declared:
        if (spec.field_name not in MILESTONE_A_FIELD_SOURCES
                or spec.value_class != MILESTONE_A_FIELD_SOURCES[spec.field_name][0]
                or type(spec.required) is not bool):
            raise RecordedInputRefusal("unsupported_declaration")
    _validate_policy(reconstructed.policy)
    scope = reconstructed.scope
    if (reconstructed.policy.policy_version != scope.policy_version
            or reconstructed.policy.mapping_reference != scope.mapping_reference
            or not reconstructed.policy.supported_sports.issubset({"running", "cycling"})):
        raise RecordedInputRefusal("policy_scope_mismatch")
    # Canonical UTC text is stricter than the existing parser's accepted spelling.
    if _utc(scope.start_epoch_seconds) != scope.start_utc or _utc(scope.end_epoch_seconds) != scope.end_utc:
        raise RecordedInputRefusal("noncanonical_scope_utc")
    members = []
    logical_identities = set()
    for record in reconstructed.records:
        if (record.preparation_version != scope.preparation_version
                or record.mapping_reference != scope.mapping_reference
                or record.policy_version != scope.policy_version):
            raise RecordedInputRefusal("record_scope_lineage_mismatch")
        warnings = None
        if "quality_warnings" in specs:
            field = record.field("quality_warnings")
            if not field.available:
                raise RecordedInputRefusal("quality_warnings_unavailable")
            warnings = json.loads(field.value_canonical)
            if not isinstance(warnings, list) or canonical_json(warnings) != field.value_canonical:
                raise RecordedInputRefusal("invalid_quality_warnings")
            for warning in warnings:
                if not isinstance(warning, dict) or set(warning) != {"code", "field", "detail", "source_field"}:
                    raise RecordedInputRefusal("invalid_quality_warnings")
                QualityWarning(**warning)
        for field in record.fields:
            if (field.preparation_version != record.preparation_version
                    or field.mapping_reference != record.mapping_reference
                    or (field.available and not isinstance(field.value_canonical, str))):
                raise RecordedInputRefusal("field_lineage_mismatch")
            if field.field_name in HEADER_FIELDS:
                value = record.canonical_identity if field.field_name == "canonical_identity" else record.source_digest
                if field.value_class != VALUE_CLASS_SCOPE_MEMBER or field.value_canonical != value:
                    raise RecordedInputRefusal("header_lineage_mismatch")
            elif field.value_class != specs[field.field_name].value_class:
                raise RecordedInputRefusal("field_declaration_class_mismatch")
            elif not field.available:
                warning_field = MILESTONE_A_FIELD_SOURCES[field.field_name][1]
                if warning_field is None or specs[field.field_name].required:
                    raise RecordedInputRefusal("required_value_unavailable")
                absent = field.absent
                QualityWarning(absent.code, warning_field, absent.detail, absent.source_field)
                if warnings is not None and {"code": absent.code, "field": warning_field,
                        "detail": absent.detail, "source_field": absent.source_field} not in warnings:
                    raise RecordedInputRefusal("absence_warning_mismatch")
            elif field.field_name not in _CORE and field.field_name not in ("sport_code", "quality_warnings"):
                warning_field = MILESTONE_A_FIELD_SOURCES[field.field_name][1]
                if warnings is not None and any(w["field"] == warning_field for w in warnings):
                    raise RecordedInputRefusal("present_value_has_absence_warning")
                if field.field_name.endswith("_unit_code"):
                    if not field.value_canonical:
                        raise RecordedInputRefusal("empty_optional_unit")
                else:
                    _integer(field.value_canonical)
        sport_field, start_field, elapsed_field = (record.field(name) for name in _CORE)
        if not all(field.available for field in (sport_field, start_field, elapsed_field)):
            raise RecordedInputRefusal("core_value_unavailable")
        sport = sport_field.value_canonical
        if sport not in ("running", "cycling"):
            raise RecordedInputRefusal("unsupported_sport")
        start = _integer(start_field.value_canonical)
        elapsed = _integer(elapsed_field.value_canonical, positive=True)
        require_elapsed_duration_ms(elapsed, origin="recorded metric source")
        identity = record.logical_tuple
        logical_key = (identity.sport_code, identity.start_epoch_seconds, identity.elapsed_duration_ms)
        if logical_key in logical_identities:
            raise RecordedInputRefusal("ambiguous_logical_identity")
        logical_identities.add(logical_key)
        if (canonical_sport_code(sport, origin="recorded metric source") != identity.sport_code
                or start != identity.start_epoch_seconds or elapsed != identity.elapsed_duration_ms
                or not scope.contains_start(start) or not scope.selects_sport(identity.sport_code)
                or sport not in reconstructed.policy.supported_sports):
            raise RecordedInputRefusal("core_identity_scope_mismatch")
        if "sport_code" in specs and record.field("sport_code").value_canonical != str(identity.sport_code):
            raise RecordedInputRefusal("sport_code_mismatch")
        operands = tuple(SourceOperand(record.source_digest, record.canonical_identity,
                         f"{record.canonical_identity}.{name}", record.preparation_version,
                         record.mapping_reference, record.field(name).value_canonical)
                         for name in sorted(_CORE))
        members.append(RecordedMember(record.canonical_identity, record.source_digest,
                                      start, sport, elapsed, operands))
    exclusions = Counter((e.canonical_identity, e.reason_code) for e in reconstructed.exclusions)
    return RecordedMetricInput(version.input_digest, _codec(_portable_scope(scope.as_record())),
        scope.start_epoch_seconds, scope.end_epoch_seconds,
        tuple(sorted(members, key=lambda m: (m.start_epoch_seconds, m.normalization_digest))),
        tuple(RecordedExclusion(identity, reason, count)
              for (identity, reason), count in sorted(exclusions.items())))


def _portable_scope(scope: dict) -> dict:
    result = dict(scope)
    result["max_activities"] = str(result["max_activities"])
    return result


def _input_required(data: RecordedMetricInput) -> None:
    try:
        _validate_metric_input(data)
    except RecordedInputRefusal:
        raise
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise RecordedInputRefusal("incomplete_metric_input") from exc


def _validate_metric_input(data: RecordedMetricInput) -> None:
    if type(data) is not RecordedMetricInput or data.adapter_version != ADAPTER_VERSION:
        raise RecordedInputRefusal("unsupported_metric_input")
    if (type(data.members) is not tuple or type(data.exclusions) is not tuple
            or type(data.selected_scope_content) is not bytes
            or type(data.start_epoch_seconds) is not int or type(data.end_epoch_seconds) is not int
            or data.start_epoch_seconds < 0 or data.end_epoch_seconds <= data.start_epoch_seconds
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", data.input_content_digest)):
        raise RecordedInputRefusal("incomplete_metric_input")
    scope = json.loads(data.selected_scope_content)
    if (_codec(scope) != data.selected_scope_content
            or scope.get("start_utc") != _utc(data.start_epoch_seconds)
            or scope.get("end_utc") != _utc(data.end_epoch_seconds)):
        raise RecordedInputRefusal("metric_scope_mismatch")
    seen = set()
    for member in data.members:
        if (type(member) is not RecordedMember or type(member.operands) is not tuple
                or member.normalization_digest in seen or member.sport not in ("running", "cycling")
                or type(member.start_epoch_seconds) is not int or type(member.elapsed_ms) is not int
                or member.elapsed_ms <= 0
                or not data.start_epoch_seconds <= member.start_epoch_seconds < data.end_epoch_seconds):
            raise RecordedInputRefusal("invalid_metric_member")
        seen.add(member.normalization_digest)
        for digest in (member.normalization_digest, member.source_digest):
            if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
                raise RecordedInputRefusal("invalid_metric_identity")
        expected = {"sport": member.sport, "start_epoch_seconds": str(member.start_epoch_seconds),
                    "elapsed_duration_ms": str(member.elapsed_ms)}
        if len(member.operands) != len(expected):
            raise RecordedInputRefusal("incomplete_metric_operands")
        for operand in member.operands:
            if type(operand) is not SourceOperand:
                raise RecordedInputRefusal("invalid_metric_operand")
            name = operand.source_field_path.rsplit(".", 1)[-1]
            if (name not in expected or operand.value != expected.pop(name)
                    or operand.source_field_path != f"{member.normalization_digest}.{name}"
                    or operand.source_digest != member.source_digest
                    or operand.normalization_digest != member.normalization_digest
                    or operand.preparation_version != scope.get("preparation_version")
                    or operand.mapping_reference != scope.get("mapping_reference")):
                raise RecordedInputRefusal("metric_operand_mismatch")
    if data.members != tuple(sorted(data.members, key=lambda m: (m.start_epoch_seconds, m.normalization_digest))):
        raise RecordedInputRefusal("noncanonical_metric_members")
    for exclusion in data.exclusions:
        if (type(exclusion) is not RecordedExclusion or type(exclusion.multiplicity) is not int
                or exclusion.multiplicity <= 0 or exclusion.reason_code not in EXCLUSION_REASON_SET
                or not re.fullmatch(r"sha256:[0-9a-f]{64}", exclusion.normalization_digest)):
            raise RecordedInputRefusal("invalid_metric_exclusion")
    keys = tuple((e.normalization_digest, e.reason_code) for e in data.exclusions)
    if keys != tuple(sorted(set(keys))):
        raise RecordedInputRefusal("noncanonical_metric_exclusions")


def _duration(value: int) -> ExactValue:
    return ExactValue("integer_milliseconds", "exact_integer", integer=value)


def _count(value: int) -> ExactValue:
    return ExactValue("activity_count", "exact_integer", integer=value)


def _method(code: str) -> dict:
    return {"method_id": code, "method_version": "1",
            "specification_digest": _SPECIFICATION_DIGEST,
            "adapter_id": "scoped-recorded-core", "adapter_version": ADAPTER_VERSION}


def _base(data: RecordedMetricInput, code: str, effective: dict, buckets: list) -> dict:
    selected = json.loads(data.selected_scope_content)
    manifest = {"manifest_version": MANIFEST_VERSION, "selected_scope": selected,
                "effective_scope": effective, "members": [m.as_record() for m in data.members],
                "exclusions": [e.as_record() for e in data.exclusions], "buckets": buckets}
    operands = [{"role": f"{member.normalization_digest}.{operand.source_field_path.rsplit('.', 1)[-1]}",
                 "source": operand.as_record()} for member in data.members for operand in member.operands]
    return {"metric_contract_version": METRIC_CONTRACT_VERSION, "metric_code": code,
            "method_identity": _method(code), "supported_input_contract_version": SCOPED_INPUT_CONTRACT_VERSION,
            "input_content_digest": data.input_content_digest, "selected_scope": selected,
            "effective_scope": effective, "codec_version": CODEC_VERSION,
            "manifest": manifest, "operands": sorted(operands, key=lambda o: o["role"]),
            "limitations": list(_LIMITATIONS), "quality_records": []}


def summarize_recorded(data: RecordedMetricInput) -> PreparedSummary:
    _input_required(data)
    groups = tuple(SportSummary(sport, tuple(m.normalization_digest for m in data.members if m.sport == sport),
                _count(sum(m.sport == sport for m in data.members)),
                _duration(sum(m.elapsed_ms for m in data.members if m.sport == sport)))
                for sport in sorted({m.sport for m in data.members}))
    reasons = () if data.members else ("no_included_activity",)
    buckets = [{"grouping": group.sport, "members": list(group.members),
                "count": str(len(group.members)), "limitations": ["recorded_data_only"]} for group in groups]
    effective = {"start_utc": _utc(data.start_epoch_seconds), "end_utc": _utc(data.end_epoch_seconds)}
    content = _base(data, "activity-summary", effective, buckets)
    content.update(grouping="per_sport", method_parameters={},
        eligibility={"eligible": not reasons, "unmet_reasons": list(reasons)},
        values=[{"sport": group.sport, "activity_count": group.activity_count.as_record(),
                 "elapsed_ms": group.elapsed_ms.as_record()} for group in groups])
    return PreparedSummary(not reasons, reasons, groups, _codec(content))


def prepare_overall_trend(data: RecordedMetricInput) -> PreparedTrend:
    _input_required(data)
    end = _EPOCH + timedelta(seconds=data.end_epoch_seconds)
    monday = end - timedelta(days=end.weekday(), hours=end.hour, minutes=end.minute,
                             seconds=end.second, microseconds=end.microsecond)
    delta = monday - _EPOCH
    end_epoch = delta.days * 86400 + delta.seconds
    start_epoch = end_epoch - 4 * _WEEK
    reasons = []
    if data.end_epoch_seconds - data.start_epoch_seconds < 4 * _WEEK:
        reasons.append("scope_less_than_28_days")
    if start_epoch < data.start_epoch_seconds:
        reasons.append("fewer_than_four_complete_weeks")
    weeks = ()
    effective = {"status": "unavailable", "reason_code": "insufficient_scope"}
    if start_epoch >= data.start_epoch_seconds:
        weeks = tuple(RecordedWeek(start_epoch + i * _WEEK, start_epoch + (i + 1) * _WEEK,
                tuple(m.normalization_digest for m in data.members
                      if start_epoch + i * _WEEK <= m.start_epoch_seconds < start_epoch + (i + 1) * _WEEK),
                _count(sum(start_epoch + i * _WEEK <= m.start_epoch_seconds < start_epoch + (i + 1) * _WEEK
                           for m in data.members)),
                _duration(sum(m.elapsed_ms for m in data.members
                              if start_epoch + i * _WEEK <= m.start_epoch_seconds < start_epoch + (i + 1) * _WEEK)))
                      for i in range(4))
        effective = {"start_utc": _utc(start_epoch), "end_utc": _utc(end_epoch)}
        if sum(bool(week.members) for week in weeks) < 3:
            reasons.append("fewer_than_three_recorded_weeks")
    comparison_members = {identity for week in weeks for identity in week.members}
    outside = tuple(m.normalization_digest for m in data.members if m.normalization_digest not in comparison_members)
    if weeks:
        earlier = sum(w.elapsed_ms.integer for w in weeks[:2])
        later = sum(w.elapsed_ms.integer for w in weeks[2:])
        difference = later - earlier
        values = (_duration(earlier), _duration(later), _duration(difference), _duration(abs(difference)),
                  ExactValue("percent", "exact_rational", fraction=Fraction(100 * difference, earlier))
                  if earlier else ExactValue("percent", "exact_rational", unavailable_reason="zero_baseline"))
        # Ineligible arithmetic is diagnostic; no sign finding is classified.
        classification = ("increased" if difference > 0 else "decreased" if difference < 0 else "equal") if not reasons else None
    else:
        values = tuple(ExactValue("integer_milliseconds", "exact_integer", unavailable_reason="insufficient_scope")
                       for _ in range(4)) + (ExactValue("percent", "exact_rational", unavailable_reason="insufficient_scope"),)
        classification = None
    content = _base(data, "training-volume-trend", effective, [week.as_record() for week in weeks])
    content.update(grouping="overall", method_parameters={"complete_weeks": "4", "minimum_recorded_weeks": "3",
        "minimum_scope_days": "28", "week_start": "monday_00_utc"},
        eligibility={"eligible": not reasons, "unmet_reasons": reasons},
        outside_comparison=list(outside), values_kind="eligible" if not reasons else "ineligible_diagnostic",
        values={name: value.as_record() for name, value in zip(
            ("earlier_total", "later_total", "signed_difference", "magnitude", "percentage"), values)})
    if classification is not None:
        content["classification"] = classification
    return PreparedTrend(not reasons, tuple(reasons), weeks, outside, *values, classification, _codec(content))


def canonical_metric_content(metric: PreparedSummary | PreparedTrend) -> bytes:
    if type(metric) not in (PreparedSummary, PreparedTrend):
        raise TypeError("prepared internal recorded metric required")
    return metric.canonical_content


def metric_content_digest(metric: PreparedSummary | PreparedTrend) -> str:
    return "sha256:" + hashlib.sha256(canonical_metric_content(metric)).hexdigest()




