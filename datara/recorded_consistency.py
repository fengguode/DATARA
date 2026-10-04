"""Pure complete-UTC-day recorded consistency.

D02 option A; WP03/CUS03-05/SR05-11/SR28-29; assignment #370.
Persistence/public projection and authorization remain separate contracts.
Attribution: System Architect — Feng Guo_gpt-6.1-sol-low_Codex (AI agent)
Configured model/effort; effective backend/native role loading unconfirmed.
"""
from __future__ import annotations

from dataclasses import dataclass, fields

from datara.normalization import sha256_digest
from datara.recorded_metrics import (
    ADAPTER_VERSION, ExactValue, RecordedInputRefusal, RecordedMetricInput,
    _base, _codec, _input_required, _strict_equal, _utc,
)

CONSISTENCY_CONTRACT_VERSION = "datara/internal-recorded-consistency/1"
_DAY = 86400
_SPECIFICATION = (
    "D02 recorded consistency v1 option A; scoped-input/1 core projection; "
    "ceil selected start to UTC midnight, floor selected end to UTC midnight; "
    "only complete half-open UTC days; each selected member belongs to its "
    "start day; active once per day across sports; leading/trailing gaps; "
    "eligible with >=28 complete days and >=1 selected member, including "
    "partial-edge-only members; counts and longest runs available even when "
    "ineligible; no complete days means zero counts/runs; missing records "
    "never prove no training; no model, distance, timer or prescription"
)
_SPECIFICATION_DIGEST = sha256_digest(_SPECIFICATION)


@dataclass(frozen=True)
class RecordedDay:
    start_epoch_seconds: int
    end_epoch_seconds: int
    members: tuple[str, ...]
    activity_count: ExactValue
    recorded_active: bool
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        try:
            if (type(self.start_epoch_seconds) is not int
                    or type(self.end_epoch_seconds) is not int
                    or self.start_epoch_seconds % _DAY
                    or self.end_epoch_seconds != self.start_epoch_seconds + _DAY
                    or type(self.members) is not tuple
                    or any(type(member) is not str for member in self.members)
                    or len(set(self.members)) != len(self.members)
                    or type(self.recorded_active) is not bool
                    or self.recorded_active != bool(self.members)
                    or not _strict_equal(self.activity_count,
                        ExactValue("activity_count", "exact_integer", integer=len(self.members)))
                    or not _strict_equal(self.limitations,
                        ("recorded_data_only",) + (() if self.members else ("missing_records",)))):
                raise RecordedInputRefusal("invalid_consistency_day")
        except RecordedInputRefusal:
            raise RecordedInputRefusal("invalid_consistency_day") from None
        except Exception:
            raise RecordedInputRefusal("invalid_consistency_day") from None

    def as_record(self) -> dict:
        self.__post_init__()
        return {
            "start_utc": _utc(self.start_epoch_seconds),
            "end_utc": _utc(self.end_epoch_seconds), "grouping": "overall",
            "members": list(self.members), "count": str(self.activity_count.integer),
            "recorded_active": self.recorded_active,
            "limitations": list(self.limitations),
        }


@dataclass(frozen=True)
class PreparedConsistency:
    eligible: bool
    unmet_reasons: tuple[str, ...]
    days: tuple[RecordedDay, ...]
    outside_effective: tuple[str, ...]
    evaluated_day_count: ExactValue
    active_day_count: ExactValue
    longest_active_streak: ExactValue
    longest_no_record_streak: ExactValue
    canonical_content: bytes
    source: RecordedMetricInput

    def __post_init__(self) -> None:
        _result_required(self)


def _day_count(value: int) -> ExactValue:
    return ExactValue("day_count", "exact_integer", integer=value)


def _consistency_fields(data: RecordedMetricInput) -> tuple:
    # Replay full input/ledger and typed projection, not only the digest.
    _input_required(data)
    start = -(-data.start_epoch_seconds // _DAY) * _DAY
    end = data.end_epoch_seconds // _DAY * _DAY
    days = []
    for instant in range(start, end, _DAY):
        members = tuple(member.normalization_digest for member in data.members
                        if instant <= member.start_epoch_seconds < instant + _DAY)
        days.append(RecordedDay(instant, instant + _DAY, members,
                    ExactValue("activity_count", "exact_integer", integer=len(members)),
                    bool(members), ("recorded_data_only",)
                    + (() if members else ("missing_records",))))
    days = tuple(days)
    effective = ({"start_utc": _utc(start), "end_utc": _utc(end)} if days else
                 {"status": "unavailable", "reason_code": "no_complete_utc_days"})
    included = {identity for day in days for identity in day.members}
    outside = tuple(member.normalization_digest for member in data.members
                    if member.normalization_digest not in included)
    reasons = []
    if len(days) < 28:
        reasons.append("scope_less_than_28_complete_days")
    if not data.members:
        reasons.append("no_included_activity")
    longest_active = longest_gap = active_run = gap_run = active_days = 0
    for day in days:
        if day.recorded_active:
            active_days += 1
            active_run += 1
            gap_run = 0
            longest_active = max(longest_active, active_run)
        else:
            gap_run += 1
            active_run = 0
            longest_gap = max(longest_gap, gap_run)
    values = tuple(_day_count(value) for value in
                   (len(days), active_days, longest_active, longest_gap))
    content = _base(data, "training-consistency", effective,
                    [day.as_record() for day in days])
    content["metric_contract_version"] = CONSISTENCY_CONTRACT_VERSION
    content["method_identity"] = {
        "method_id": "training-consistency", "method_version": "1",
        "specification_digest": _SPECIFICATION_DIGEST,
        "adapter_id": "scoped-recorded-core", "adapter_version": ADAPTER_VERSION,
    }
    limitations = content["limitations"]
    if any(not day.recorded_active for day in days):
        limitations.append("missing_records")
    if (start != data.start_epoch_seconds or end != data.end_epoch_seconds):
        limitations.append("partial_days_excluded")
    if outside and not included:
        limitations.append("selected_activity_only_in_partial_days")
    content.update(
        grouping="overall", method_parameters={"minimum_scope_complete_days": "28",
            "day_start": "midnight_utc", "partial_days": "excluded"},
        eligibility={"eligible": not reasons, "unmet_reasons": reasons},
        outside_effective=list(outside),
        values_kind="eligible" if not reasons else "ineligible_diagnostic",
        values={name: value.as_record() for name, value in zip(
            ("evaluated_day_count", "active_day_count", "longest_active_streak",
             "longest_no_record_streak"), values)},
    )
    return (not reasons, tuple(reasons), days, outside, *values, _codec(content))


def _result_required(result: PreparedConsistency) -> bytes:
    """Reconstruct typed fields and export bytes, including constructor bypass."""
    try:
        if type(result) is not PreparedConsistency:
            raise RecordedInputRefusal("unsupported_consistency_result")
        expected = _consistency_fields(result.source) + (result.source,)
        actual = tuple(getattr(result, field.name) for field in fields(PreparedConsistency))
        if not _strict_equal(actual, expected):
            raise RecordedInputRefusal("prepared_consistency_mismatch")
        return expected[-2]
    except RecordedInputRefusal as exc:
        raise RecordedInputRefusal(exc.reason_code) from None
    except Exception:
        raise RecordedInputRefusal("invalid_consistency_result") from None


def prepare_recorded_consistency(data: RecordedMetricInput) -> PreparedConsistency:
    """Prepare counts/runs over complete UTC days from validated selected data."""
    try:
        return PreparedConsistency(*_consistency_fields(data), source=data)
    except RecordedInputRefusal as exc:
        raise RecordedInputRefusal(exc.reason_code) from None
    except Exception:
        raise RecordedInputRefusal("invalid_metric_input") from None


def canonical_consistency_content(result: PreparedConsistency) -> bytes:
    return _result_required(result)


__all__ = ["RecordedDay", "PreparedConsistency", "prepare_recorded_consistency",
           "canonical_consistency_content", "CONSISTENCY_CONTRACT_VERSION"]
