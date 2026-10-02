"""TK11 - Approved file classification and diagnostics for DATARA P0 source intake.

Trace: CUS01; SR01, SR02, SR27, SR32; FEAT01; WP02; D01.  TC01, TC19, TC21.

CONTRACT SOURCES (read-only, authoritative).  Nothing in this module invents a sport
enumeration, a value range or a field mapping:

* ``docs/management/p0-decision-baseline-2026-10-01.md`` -> D01 selected direction:
  protocol coverage is FIT 1.0 and 2.0 using the official decoder; initial semantic
  scope is single-session running and cycling, indoor and outdoor; a device-model
  allowlist is not a substitute for file conformance; unsupported file types,
  sports, multisport/chained layouts and required semantics receive a stable
  explanation; P0 source scope excludes wellness, planned workout/course and
  arbitrary archive imports; the four required normalised inputs are source
  reference/digest, sport, session UTC start instant and valid elapsed duration;
  whole-file rejection on missing/invalid required fields, broken required
  relations, malformed structure or failed integrity; decoder success alone is
  insufficient evidence under SR27.
* ``docs/p0-design/fit-support-matrix.md`` (TK10) -> the approved mapping evidence
  (MAP01-MAP05) and the named open gaps this module must not silently close.
* ``docs/management/decision-register.md`` -> the founder's G0 replacement for
  Milestone A and the binding architectural condition.

SCOPE / NON-GOALS, stated so a reviewer does not have to infer them:

* This module is **pure**: no database, no Django, no filesystem, no network and
  **no model call of any kind**.  It maps file bytes to a disposition and an
  explanation, nothing more.
* It persists nothing.  ``datara/intake.py`` owns the disposition record, the
  quarantine record and the logical-tuple duplicate decision.
* It does not compute skills, models, recommendations, readiness verdicts or any
  other assessment of an activity's *meaning*.  Under the Milestone A binding
  condition, no entity whose meaning is "the outcome of executing a skill against a
  model" may exist.  What follows is a deterministic *data* classification of file
  bytes, reproducible from stored inputs by a versioned method.
* Raw bytes of a rejected file are never converted into accepted history here.

The pinned decoder (``garmin-fit-sdk`` 21.217.0) supplies the profile constants and
the CRC algorithm.  Structure walking, raw-presence diagnostics and the stable
reason vocabulary are implemented here so that every outcome is explainable and
distinguishable: the pinned decoder deliberately collapses "absent" and "present
but equal to the base-type invalid sentinel" into the same observable result, while
D01 requires those to be distinct source causes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from datara.canonical import (
    CANONICAL_DURATION_UNIT,
    LogicalIdentity,
    require_elapsed_duration_ms,
)

# ---------------------------------------------------------------------------
# Rule version.  Every classification carries it, so a stored disposition can be
# re-derived or invalidated when the rules change.  Pure function of file bytes.
# ---------------------------------------------------------------------------
RULE_VERSION = "TK11-CLASS-1"

#: SDK/profile identity this module is written against (MAP01/MAP03).  Recorded as
#: evidence on every outcome; never used to derive a file's own profile version.
PINNED_SDK_VERSION = "21.217.0"
PINNED_SDK_TAG = "production/release/21.217.0-0-g248b1c46"

# FIT constants, all read from the pinned decoder/CRC table in 21.217.0
# (``garmin_fit_sdk.fit``): bit 7 compressed, bit 6 definition, bit 5 developer
# data, bits 0-3 local message number.
HEADER_WITH_CRC_SIZE = 14
HEADER_WITHOUT_CRC_SIZE = 12
CRC_SIZE = 2
FIT_SIGNATURE = b".FIT"
MESG_DEFINITION_MASK = 0x40
COMPRESSED_HEADER_MASK = 0x80
LOCAL_MESG_NUM_MASK = 0x0F
DEVELOPER_DATA_MASK = 0x20

# D01: "Protocol coverage is FIT 1.0 and 2.0."
SUPPORTED_PROTOCOL_MAJORS = (1, 2)

# Pinned profile constants (MAP01) - global message numbers.
MESG_NUM_FILE_ID = 0
MESG_NUM_RECORD = 20
MESG_NUM_SESSION = 18
MESG_NUM_ACTIVITY = 34

# Pinned profile constants (MAP01) - field definition numbers.
FILE_ID_TYPE = 0
ACTIVITY_NUM_SESSIONS = 1
ACTIVITY_TYPE = 2
SESSION_START_TIME = 2
SESSION_SPORT = 5
SESSION_SUB_SPORT = 6
SESSION_TOTAL_ELAPSED_TIME = 7
SESSION_TOTAL_TIMER_TIME = 8
SESSION_TOTAL_DISTANCE = 9

#: Pinned base-type invalid sentinels (MAP02 / ``fit.BASE_TYPE_DEFINITIONS``).
INVALID_ENUM = 0xFF
INVALID_UINT8 = 0xFF
INVALID_UINT16 = 0xFFFF
INVALID_UINT32 = 0xFFFFFFFF

#: Pinned profile minimum for ``date_time`` (MAP01 ``types.date_time``).
DATE_TIME_MIN = 268435456

# ---------------------------------------------------------------------------
# Stable reason vocabulary.
#
# Every rejection gets exactly one of these.  They are the public diagnostic
# contract for a file disposition, so they are a frozen tuple: a new cause gets a
# new code rather than being folded into a neighbouring one.  A raw exception
# string from a decoder is deliberately NOT a reason code.
# ---------------------------------------------------------------------------
REASON_ACCEPTED = "accepted"

# Container / structure
REASON_EMPTY_FILE = "empty_file"
REASON_NOT_A_FIT_FILE = "not_a_fit_file"
REASON_MALFORMED_HEADER = "malformed_file_header"
REASON_MALFORMED_STRUCTURE = "malformed_structure"
#: A field declared with a base type the pinned profile does not define.  D01:
#: "Reject a required interpretation that depends on an unknown field, native
#: override or unverified feature."  Without this the failure would surface later
#: as a misleading downstream symptom (for example a required field reported as
#: "missing" when it is actually unreadable), and the pinned decoder would fail
#: the same file with "Invalid field definition base type".
REASON_UNDEFINED_BASE_TYPE = "undefined_base_type"

# Integrity - reported, never repaired (D01: "failed integrity" rejects the file).
REASON_HEADER_CRC_INVALID = "header_crc_invalid"
REASON_FILE_CRC_INVALID = "file_crc_invalid"

# Protocol / layout
REASON_UNSUPPORTED_PROTOCOL_VERSION = "unsupported_protocol_version"
REASON_CHAINED_FILE_LAYOUT = "chained_file_layout"
REASON_COMPRESSED_TIMESTAMP_UNSUPPORTED = "compressed_timestamp_unsupported"

# File category.  D01 excludes wellness, planned workout/course and arbitrary
# archive imports from P0 source scope.  Each excluded category gets its OWN
# reason so that a rejection is never "unsupported by accident".
REASON_UNSUPPORTED_FILE_TYPE = "unsupported_file_type"
REASON_UNSUPPORTED_FILE_TYPE_WORKOUT = "unsupported_file_type_planned_workout"
REASON_UNSUPPORTED_FILE_TYPE_COURSE = "unsupported_file_type_course"
REASON_UNSUPPORTED_FILE_TYPE_WELLNESS = "unsupported_file_type_wellness"
REASON_UNSUPPORTED_FILE_TYPE_SCHEDULES = "unsupported_file_type_schedules"
REASON_MISSING_FILE_ID = "missing_file_id"
REASON_INVALID_FILE_ID_TYPE = "invalid_file_id_type"

# Semantics / cardinality
REASON_MISSING_SESSION = "missing_session"
REASON_MULTISPORT_LAYOUT = "multisport_or_chained_layout"
REASON_SESSION_COUNT_MISMATCH = "session_count_mismatch"

# Required semantics
REASON_MISSING_SPORT = "missing_required_sport"
REASON_INVALID_SPORT = "invalid_required_sport"
REASON_UNSUPPORTED_SPORT = "unsupported_sport"
REASON_MISSING_START_TIME = "missing_required_start_time"
REASON_INVALID_START_TIME = "invalid_required_start_time"
REASON_MISSING_ELAPSED_DURATION = "missing_required_elapsed_duration"
REASON_INVALID_ELAPSED_DURATION = "invalid_required_elapsed_duration"

# Resource limits (D01 pilot limits, inclusive)
REASON_FILE_SIZE_LIMIT_EXCEEDED = "file_size_limit_exceeded"
REASON_BATCH_FILE_COUNT_EXCEEDED = "batch_file_count_exceeded"
REASON_BATCH_SIZE_LIMIT_EXCEEDED = "batch_size_limit_exceeded"
REASON_MESSAGE_LIMIT_EXCEEDED = "message_limit_exceeded"
REASON_SAMPLE_LIMIT_EXCEEDED = "sample_limit_exceeded"

# Decoder availability
REASON_DECODER_UNAVAILABLE = "decoder_unavailable"
REASON_DECODE_ERROR = "decode_error"

REJECTION_REASONS = frozenset(
    {
        REASON_EMPTY_FILE,
        REASON_NOT_A_FIT_FILE,
        REASON_MALFORMED_HEADER,
        REASON_MALFORMED_STRUCTURE,
        REASON_UNDEFINED_BASE_TYPE,
        REASON_HEADER_CRC_INVALID,
        REASON_FILE_CRC_INVALID,
        REASON_UNSUPPORTED_PROTOCOL_VERSION,
        REASON_CHAINED_FILE_LAYOUT,
        REASON_COMPRESSED_TIMESTAMP_UNSUPPORTED,
        REASON_UNSUPPORTED_FILE_TYPE,
        REASON_UNSUPPORTED_FILE_TYPE_WORKOUT,
        REASON_UNSUPPORTED_FILE_TYPE_COURSE,
        REASON_UNSUPPORTED_FILE_TYPE_WELLNESS,
        REASON_UNSUPPORTED_FILE_TYPE_SCHEDULES,
        REASON_MISSING_FILE_ID,
        REASON_INVALID_FILE_ID_TYPE,
        REASON_MISSING_SESSION,
        REASON_MULTISPORT_LAYOUT,
        REASON_SESSION_COUNT_MISMATCH,
        REASON_MISSING_SPORT,
        REASON_INVALID_SPORT,
        REASON_UNSUPPORTED_SPORT,
        REASON_MISSING_START_TIME,
        REASON_INVALID_START_TIME,
        REASON_MISSING_ELAPSED_DURATION,
        REASON_INVALID_ELAPSED_DURATION,
        REASON_FILE_SIZE_LIMIT_EXCEEDED,
        REASON_BATCH_FILE_COUNT_EXCEEDED,
        REASON_BATCH_SIZE_LIMIT_EXCEEDED,
        REASON_MESSAGE_LIMIT_EXCEEDED,
        REASON_SAMPLE_LIMIT_EXCEEDED,
        REASON_DECODER_UNAVAILABLE,
        REASON_DECODE_ERROR,
    }
)

#: Warning codes.  Warnings never turn a rejection into an acceptance and never
#: downgrade a rejection; they record a deterministic data-quality observation.
WARN_ACTIVITY_MESSAGE_ABSENT = "activity_message_absent"
WARN_SUB_SPORT_ABSENT = "sub_sport_absent"
WARN_SUB_SPORT_INVALID = "sub_sport_invalid"
WARN_SUB_SPORT_NOT_IN_SCOPE = "sub_sport_outside_pinned_evidence"
WARN_TIMER_TIME_ABSENT = "total_timer_time_absent"
WARN_TIMER_TIME_INVALID = "total_timer_time_invalid"
WARN_DISTANCE_ABSENT = "total_distance_absent"
WARN_DISTANCE_INVALID = "total_distance_invalid"
WARN_NO_RECORD_SAMPLES = "no_record_samples"
#: D01: unknown optional/developer fields may be ignored for normalisation only
#: when the supported file structure is independently verified, and the ignored
#: data must be reported.  The structure IS walked correctly, so the data is
#: skipped and disclosed rather than guessed at or silently dropped.
WARN_DEVELOPER_FIELDS_IGNORED = "developer_fields_ignored"


# ---------------------------------------------------------------------------
# Pinned profile lookups.
#
# These are read from the pinned SDK at import time and asserted below against the
# literal values recorded in the TK10 matrix.  If the pinned artifact ever changes,
# the assertion fails loudly instead of silently re-basing the contract.
# ---------------------------------------------------------------------------
def _load_pinned_profile() -> dict[str, Any]:
    from garmin_fit_sdk import Profile  # noqa: PLC0415 - optional dependency
    import garmin_fit_sdk.fit as fit  # noqa: PLC0415

    return {
        "version": dict(Profile["version"]),
        "file": dict(Profile["types"]["file"]),
        "sport": dict(Profile["types"]["sport"]),
        "sub_sport": dict(Profile["types"]["sub_sport"]),
        "activity": dict(Profile["types"]["activity"]),
        "date_time": dict(Profile["types"]["date_time"]),
        "mesg_num": dict(Profile["mesg_num"]),
        "base_invalid": {
            code: defn["invalid"] for code, defn in fit.BASE_TYPE_DEFINITIONS.items()
        },
        "base_types": frozenset(fit.BASE_TYPE_DEFINITIONS),
    }


class DecoderUnavailable(RuntimeError):
    """Raised when the pinned SDK is not importable.

    **Absence**, not disagreement. A missing decoder and a decoder that does not
    match the contract are different facts and are never reported as the same
    one: absence means nothing can be claimed, disagreement means the pinned
    artifact changed and the contract would silently re-base.
    """


class PinnedProfileMismatch(RuntimeError):
    """The pinned decoder is importable but does not match the TK10 matrix.

    Distinct from `DecoderUnavailable` on purpose. The old code asserted the
    profile inside ``try/except Exception``, so a mismatch was indistinguishable
    from "not installed" *and* vanished entirely under ``python -O``, which
    strips every ``assert``: the contract would then re-base silently on whatever
    profile the installed SDK happened to carry. A mismatch now raises, and it
    raises a different exception from absence.
    """


#: The profile facts section 6 / the TK10 matrix fixes, as literals. Kept apart
#: from the loader so `verify_pinned_profile` is a pure function that a test can
#: feed a deliberately wrong profile to.
EXPECTED_PROFILE_VERSION: Mapping[str, Any] = {
    "major": 21,
    "minor": 217,
    "patch": 0,
    "type": "Release",
}
EXPECTED_FILE_TYPE_ACTIVITY = 4
EXPECTED_SPORT_NAMES: Mapping[int, str] = {1: "running", 2: "cycling"}
EXPECTED_ACTIVITY_AUTO_MULTI_SPORT = 1


def verify_pinned_profile(profile: Mapping[str, Any] | None) -> None:
    """Raise `PinnedProfileMismatch` unless ``profile`` is the pinned one.

    A pure function, deliberately: the facts are compared here with explicit
    ``!=`` tests rather than ``assert`` statements, so the check survives
    ``python -O`` and can be exercised against a wrong profile directly.

    Mutation that fails: replace any explicit comparison below with an ``assert``
    -- under ``PYTHONOPTIMIZE=1`` the check disappears, this stops raising, and
    `test_a_profile_mismatch_is_raised_not_absorbed` fails.
    """

    if profile is None:
        raise PinnedProfileMismatch("the pinned profile could not be read at all")
    mismatches: list[str] = []
    version = profile.get("version")
    if dict(version or {}) != EXPECTED_PROFILE_VERSION:
        mismatches.append(
            f"version {dict(version or {})!r} != pinned {EXPECTED_PROFILE_VERSION!r}"
        )
    file_types = profile.get("file") or {}
    if file_types.get(EXPECTED_FILE_TYPE_ACTIVITY) != "activity":
        mismatches.append(
            f"file_id.type[{EXPECTED_FILE_TYPE_ACTIVITY}] "
            f"{file_types.get(EXPECTED_FILE_TYPE_ACTIVITY)!r} != 'activity'"
        )
    sport = profile.get("sport") or {}
    for code, name in EXPECTED_SPORT_NAMES.items():
        if sport.get(code) != name:
            mismatches.append(f"sport[{code}] {sport.get(code)!r} != {name!r}")
    date_time = profile.get("date_time") or {}
    if date_time != {DATE_TIME_MIN: "min"}:
        mismatches.append(f"date_time {dict(date_time)!r} != {{{DATE_TIME_MIN!r}: 'min'}}")
    activity = profile.get("activity") or {}
    if activity.get(EXPECTED_ACTIVITY_AUTO_MULTI_SPORT) != "auto_multi_sport":
        mismatches.append(
            f"activity[{EXPECTED_ACTIVITY_AUTO_MULTI_SPORT}] "
            f"{activity.get(EXPECTED_ACTIVITY_AUTO_MULTI_SPORT)!r} != 'auto_multi_sport'"
        )
    if mismatches:
        raise PinnedProfileMismatch(
            "the pinned garmin-fit-sdk profile does not match the TK10 matrix, so "
            "the classification contract would silently re-base: "
            + "; ".join(mismatches)
        )


def _load_pinned_state() -> tuple[str, Mapping[str, Any] | None, str | None]:
    """Return ``(state, profile, detail)`` without raising.

    ``state`` is ``"available"``, ``"absent"`` (the SDK cannot be imported) or
    ``"mismatch"`` (it can, and it disagrees with the matrix).
    """

    try:
        profile = _load_pinned_profile()
    except Exception as exc:  # noqa: BLE001 - absence is reported, not raised
        return "absent", None, f"{exc.__class__.__name__}: {exc}"
    try:
        verify_pinned_profile(profile)
    except PinnedProfileMismatch as exc:
        return "mismatch", profile, str(exc)
    return "available", profile, None


_PINNED_STATE, _PINNED_PROFILE, _PINNED_DETAIL = _load_pinned_state()

#: The single boolean the guards below read. It is *derived* from
#: `_PINNED_STATE`, so a mismatch reads False exactly as absence does, and the
#: distinction between the two survives in `pinned_state()` /
#: `pinned_state_detail()` and in which exception `pinned_profile()` raises.
_PINNED_AVAILABLE: bool = _PINNED_STATE == "available"


def pinned_state() -> str:
    """``"available"``, ``"absent"`` (SDK not importable) or ``"mismatch"``.

    One of the three is always reported. Absence is never reported as a
    mismatch, and a mismatch is never reported as absence.
    """

    return _PINNED_STATE


def pinned_state_detail() -> str | None:
    """Why the state is ``"absent"`` or ``"mismatch"``; ``None`` when available."""

    return _PINNED_DETAIL


def pinned_profile() -> Mapping[str, Any]:
    """The pinned profile snapshot.

    Raises `DecoderUnavailable` when the SDK is absent and
    `PinnedProfileMismatch` when it is present but disagrees with the matrix.
    """

    if _PINNED_STATE == "mismatch":
        raise PinnedProfileMismatch(_PINNED_DETAIL or "pinned profile mismatch")
    if not _PINNED_AVAILABLE or _PINNED_PROFILE is None:
        raise DecoderUnavailable(REASON_DECODER_UNAVAILABLE)
    return _PINNED_PROFILE


def decoder_available() -> bool:
    """Whether the pinned SDK is importable *and* matches the TK10 matrix.

    A mismatch is not availability: a decoder that would re-base the contract
    cannot decode against it.
    """

    return _PINNED_AVAILABLE


def file_type_name(raw: int) -> str | None:
    """Pinned profile name for a ``file_id.type`` raw enum, or ``None`` if unknown."""
    if not _PINNED_AVAILABLE:
        return None
    return _PINNED_PROFILE["file"].get(raw)


def sport_name(raw: int) -> str | None:
    if not _PINNED_AVAILABLE:
        return None
    return _PINNED_PROFILE["sport"].get(raw)


def sub_sport_name(raw: int) -> str | None:
    if not _PINNED_AVAILABLE:
        return None
    return _PINNED_PROFILE["sub_sport"].get(raw)


def activity_type_name(raw: int) -> str | None:
    if not _PINNED_AVAILABLE:
        return None
    return _PINNED_PROFILE["activity"].get(raw)


#: D01 initial semantic scope.  "single-session running and cycling, indoor and
#: outdoor".  Only the two sport raws are in scope.  Indoor/outdoor is a property
#: of which *variants* are admitted, not a classification this module is allowed to
#: infer - the matrix explicitly forbids inferring it from GPS absence, so both
#: indoor and outdoor sub-sport evidence is admitted and neither is labelled.
SPORT_IN_SCOPE: Mapping[int, str] = {1: "running", 2: "cycling"}

#: Pinned file_id.type categories that D01 places outside P0 source scope.  Each
#: maps to its own reason so a rejection is never merely unsupported-by-accident.
#: Keys are pinned profile *file enum* names only - verified against 21.217.0, so
#: no category is asserted that the pinned profile does not define.
FILE_TYPE_EXCLUSIONS: Mapping[str, str] = {
    # Planned workout and course are named exclusions in D01.
    "workout": REASON_UNSUPPORTED_FILE_TYPE_WORKOUT,
    "course": REASON_UNSUPPORTED_FILE_TYPE_COURSE,
    "schedules": REASON_UNSUPPORTED_FILE_TYPE_SCHEDULES,
    # Wellness is named in D01.  21.217.0 carries wellness/monitoring data under
    # the monitoring, weight and blood-pressure file categories rather than a
    # single "wellness" enum, so all of them reject with the wellness reason.
    "monitoring_daily": REASON_UNSUPPORTED_FILE_TYPE_WELLNESS,
    "weight": REASON_UNSUPPORTED_FILE_TYPE_WELLNESS,
    "blood_pressure": REASON_UNSUPPORTED_FILE_TYPE_WELLNESS,
}


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FieldValue:
    """A raw field as it appears in the file, with presence distinguished from value."""

    present: bool
    raw: int | None = None
    invalid: bool = False  # present and equal to the pinned base-type sentinel

    @property
    def usable(self) -> bool:
        return self.present and not self.invalid and self.raw is not None


ABSENT = FieldValue(present=False)


@dataclass(frozen=True)
class FitHeaderFacts:
    """Header bytes as read under the pinned 21.217.0 rules."""

    header_size: int
    protocol_version: int
    profile_version: int
    data_size: int
    signature_ok: bool
    header_crc_declared: int | None
    header_crc_computed: int | None
    trailing_bytes: int
    file_total_size: int

    @property
    def protocol_major(self) -> int:
        return self.protocol_version >> 4

    @property
    def protocol_minor_tenths(self) -> int:
        return self.protocol_version & 0x0F


@dataclass(frozen=True)
class StructureScan:
    """Deterministic structural walk of one FIT file segment."""

    header: FitHeaderFacts
    message_count: int
    record_sample_count: int
    definition_count: int
    has_compressed_timestamp: bool
    session_messages: int
    raw_fields: Mapping[tuple[int, int], FieldValue]
    developer_field_definitions: int = 0
    structural_error: str | None = None
    structural_detail: str | None = None


@dataclass(frozen=True)
class FileClassification:
    """The per-file outcome.  Deterministic: a pure function of ``data``."""

    disposition: str  # "accepted" | "rejected"
    reason_code: str
    reason_detail: str
    rule_version: str = RULE_VERSION
    decoder: str = f"garmin-fit-sdk {PINNED_SDK_VERSION} ({PINNED_SDK_TAG})"
    protocol_version: str | None = None
    profile_version_raw: int | None = None
    file_type_raw: int | None = None
    file_type_name: str | None = None
    sport_raw: int | None = None
    sport_name: str | None = None
    sub_sport_raw: int | None = None
    sub_sport_name: str | None = None
    activity_type_raw: int | None = None
    activity_type_name: str | None = None
    declared_session_count: int | None = None
    observed_session_count: int = 0
    message_count: int = 0
    record_sample_count: int = 0
    # D01's four required normalised inputs.  ``None`` on any rejection, so a
    # rejected file can never be persisted as accepted history downstream.
    start_time_utc: str | None = None
    elapsed_duration_seconds: str | None = None
    timer_duration_seconds: str | None = None
    total_distance_metres: str | None = None
    #: The same elapsed duration in the **canonical comparison unit**: integer
    #: milliseconds (``datara.canonical.CANONICAL_DURATION_UNIT``). FIT's
    #: ``session.total_elapsed_time`` is a scaled integer whose scale is 1000,
    #: so the raw value already *is* the millisecond count and no rounding or
    #: rescaling is involved.
    #:
    #: This field exists because ``elapsed_duration_seconds`` above is an exact
    #: decimal *string* ("1800", or "1800.5" when the file's own resolution is
    #: finer than a second), and a string cannot be compared with the integer
    #: logical tuple the persistence layer uses. Three representations of one
    #: quantity -- integer seconds, integer milliseconds and decimal string --
    #: is how one activity came to be written as 1800 by one path, 1800000 by the
    #: next, and accepted twice. ``None`` whenever the seconds form is ``None``,
    #: i.e. on every rejection.
    elapsed_duration_ms: int | None = None
    warnings: tuple[str, ...] = ()
    decoder_verified: bool = False
    #: Why the pinned-decoder cross-check did or did not agree.  Carried so an
    #: unavailable decoder is never reported as a decoder disagreement.
    decoder_check_error: str | None = None

    @property
    def accepted(self) -> bool:
        return self.disposition == "accepted"

    @property
    def logical_tuple(self) -> LogicalIdentity | None:
        """The D01 quarantine key, as the one canonical definition.

        D01's key is ``(sport, UTC start, elapsed duration)``. It used to be a
        three-**string** tuple built here, while ``datara.dedup`` compared an
        integer four-tuple and the same column was written in two units, so the
        two definitions could not be compared with each other at all. It is now
        `datara.canonical.LogicalIdentity`: three exact **integers**, in the
        canonical unit, checked by ``datara.canonical`` on the way in.

        The owner component is applied by the caller, which owns identity, so the
        identity half is returned rather than the full `LogicalTuple`.
        D01 uses *exact* tuple equality; this is a conservative application
        heuristic and not comprehensive duplicate detection.

        ``None`` on any rejection, so a rejected file cannot contribute a tuple.
        """

        if not self.accepted:
            return None
        if self.elapsed_duration_ms is None or self.start_time_utc is None:
            return None
        return LogicalIdentity.from_values(
            sport_code=self.sport_name or "",
            session_start_utc=self.start_time_utc,
            elapsed_duration_ms=self.elapsed_duration_ms,
            origin="FileClassification.logical_tuple",
        )


def _reject(code: str, detail: str, **kwargs: Any) -> FileClassification:
    # An explicit raise, not an assert: `python -O` strips asserts, and a reason
    # code that quietly stopped being checked would let an unrecognised code into
    # the stable vocabulary this module's whole contract rests on.
    if code not in REJECTION_REASONS:
        raise ValueError(f"unstable reason code: {code!r}")
    return FileClassification(
        disposition="rejected", reason_code=code, reason_detail=detail, **kwargs
    )


# ---------------------------------------------------------------------------
# CRC - pinned algorithm via the pinned SDK.
# ---------------------------------------------------------------------------
def _crc16(data: bytes) -> int:
    from garmin_fit_sdk import CrcCalculator  # noqa: PLC0415

    return CrcCalculator.calculate_crc(data, 0, len(data))


# ---------------------------------------------------------------------------
# Structural walk
# ---------------------------------------------------------------------------
def _u(raw: bytes, little_endian: bool) -> int:
    return int.from_bytes(raw, "little" if little_endian else "big")


def _read_header(data: bytes) -> FitHeaderFacts:
    header_size = data[0]
    protocol_version = data[1]
    profile_version = _u(data[2:4], True)  # header profile version is always LE
    data_size = _u(data[4:8], True)
    signature_ok = data[8:12] == FIT_SIGNATURE
    header_crc_declared: int | None = None
    header_crc_computed: int | None = None
    if header_size == HEADER_WITH_CRC_SIZE:
        header_crc_declared = _u(data[12:14], True)
        header_crc_computed = _crc16(data[0:12])
    # Chained layout is detected from bytes beyond one complete segment, which is
    # unambiguous and observable in the pinned decoder: ``read`` loops
    # ``while position < length`` calling ``__decode_next_file``, so any remainder
    # after one header+data+CRC segment is another file.
    #
    # The protocol's header-level "chained file" flag is deliberately NOT used as
    # a rule here.  The TK10 matrix records that official protocol prose was never
    # substantively captured (SRC05) and that chained-layout detection "needs
    # independent fixtures", and the pinned decoder carries a TODO for exactly
    # this case.  Asserting a flag position from memory would be an invented rule,
    # so the question is reported as open instead.  See the TK11 report.
    file_total_size = header_size + data_size
    trailing = max(0, len(data) - (file_total_size + CRC_SIZE))
    return FitHeaderFacts(
        header_size=header_size,
        protocol_version=protocol_version,
        profile_version=profile_version,
        data_size=data_size,
        signature_ok=signature_ok,
        header_crc_declared=header_crc_declared,
        header_crc_computed=header_crc_computed,
        trailing_bytes=trailing,
        file_total_size=file_total_size,
    )


def _scan(data: bytes) -> StructureScan:
    """Walk one FIT segment deterministically, capturing raw field presence."""
    header = _read_header(data)
    # local message number -> (global num, fields, normal size, dev size, LE)
    local_defs: dict[int, tuple[int, list[tuple[int, int, int]], int, int, bool]] = {}
    raw_fields: dict[tuple[int, int], FieldValue] = {}
    message_count = 0
    record_count = 0
    definition_count = 0
    session_messages = 0
    compressed = False
    developer_fields = 0
    error: str | None = None
    detail: str | None = None

    pos = header.header_size
    end = header.header_size + header.data_size
    if end > len(data):
        return StructureScan(
            header=header,
            message_count=0,
            record_sample_count=0,
            definition_count=0,
            has_compressed_timestamp=False,
            session_messages=0,
            raw_fields={},
            structural_error=REASON_MALFORMED_HEADER,
            structural_detail=(
                f"declared data_size {header.data_size} runs past end of file"
            ),
        )

    while pos < end:
        header_byte = data[pos]

        # Compressed timestamp record: the pinned decoder raises here (MAP03
        # "Compressed timestamp messages are not currently supported").  Recorded
        # rather than worked around - see classify_bytes for the honest report.
        if header_byte & COMPRESSED_HEADER_MASK:
            compressed = True
            pos += 5
            message_count += 1
            continue

        local_num = header_byte & LOCAL_MESG_NUM_MASK
        is_developer = bool(header_byte & DEVELOPER_DATA_MASK)

        if header_byte & MESG_DEFINITION_MASK:
            if pos + 6 > end:
                error, detail = REASON_MALFORMED_STRUCTURE, "truncated message definition"
                break
            reserved, architecture = data[pos + 1], data[pos + 2]
            little_endian = architecture == 0
            # The global message number is written in the definition's own byte
            # order, so it must be read after the architecture byte is known.
            global_num = _u(data[pos + 3 : pos + 5], little_endian)
            num_fields = data[pos + 5]
            if reserved != 0:
                error, detail = REASON_MALFORMED_STRUCTURE, "message definition reserved byte is not zero"
                break
            # Fixed part is 6 bytes: record header, reserved, architecture,
            # 2-byte global message number, field count.
            definition_end = pos + 6 + 3 * num_fields
            if is_developer:
                # A developer-data definition appends num_dev_fields and one
                # (field_def_num, size, dev_data_index) triple per developer field.
                if definition_end + 1 > end:
                    error, detail = REASON_MALFORMED_STRUCTURE, "truncated developer field count"
                    break
                num_dev_fields = data[definition_end]
                definition_end += 1 + 3 * num_dev_fields
                developer_fields += num_dev_fields
            if definition_end > end:
                error, detail = REASON_MALFORMED_STRUCTURE, "message definition field table runs past data section"
                break
            fields: list[tuple[int, int, int]] = []
            cursor = pos + 6
            for _ in range(num_fields):
                field_def_num = data[cursor]
                field_size = data[cursor + 1]
                base_type = data[cursor + 2]
                if _PINNED_AVAILABLE and base_type not in _PINNED_PROFILE["base_types"]:
                    error = REASON_UNDEFINED_BASE_TYPE
                    detail = (
                        f"field {field_def_num} of message {global_num} declares base "
                        f"type 0x{base_type:02X}, which pinned profile 21.217.0 does "
                        "not define; its value cannot be interpreted"
                    )
                    break
                fields.append((field_def_num, field_size, base_type))
                cursor += 3
            if error is not None:
                break
            dev_size = 0
            if is_developer:
                dev_count = data[pos + 6 + 3 * num_fields]
                dev_cursor = pos + 7 + 3 * num_fields
                for _ in range(dev_count):
                    dev_size += data[dev_cursor + 1]
                    dev_cursor += 3
            # architecture 0 = little endian, 1 = big endian (pinned decoder).
            local_defs[local_num] = (
                global_num,
                fields,
                sum(f[1] for f in fields),
                dev_size,
                little_endian,
            )
            definition_count += 1
            pos = definition_end
            continue

        definition = local_defs.get(local_num)
        if definition is None:
            error, detail = (
                REASON_MALFORMED_STRUCTURE,
                f"data record references undefined local message {local_num}",
            )
            break
        global_num, fields, normal_size, dev_size, little_endian = definition
        message_size = normal_size + dev_size
        if pos + 1 + message_size > end:
            error, detail = REASON_MALFORMED_STRUCTURE, "data record runs past data section"
            break
        offset = pos + 1
        for field_num, size, _base_type in fields:
            if field_num in (0, 1, 2, 3, 5, 6, 7, 8, 9, 253):
                if (global_num, field_num) not in raw_fields:
                    chunk = data[offset : offset + size]
                    raw = _u(chunk, little_endian) if chunk else None
                    raw_fields[(global_num, field_num)] = FieldValue(
                        present=True,
                        raw=raw,
                        invalid=_is_invalid(raw, size),
                    )
            offset += size
        message_count += 1
        if global_num == MESG_NUM_RECORD:
            record_count += 1
        if global_num == MESG_NUM_SESSION:
            session_messages += 1
        pos = pos + 1 + message_size

    return StructureScan(
        header=header,
        message_count=message_count,
        record_sample_count=record_count,
        definition_count=definition_count,
        has_compressed_timestamp=compressed,
        session_messages=session_messages,
        raw_fields=raw_fields,
        developer_field_definitions=developer_fields,
        structural_error=error,
        structural_detail=detail,
    )


def _is_invalid(raw: int | None, size: int) -> bool:
    """Compare a raw value against the pinned base-type invalid sentinel."""
    if raw is None:
        return False
    if size == 1:
        return raw == INVALID_UINT8
    if size == 2:
        return raw == INVALID_UINT16
    if size == 4:
        return raw == INVALID_UINT32
    return False


def _field(scan: StructureScan, global_num: int, field_num: int) -> FieldValue:
    """Raw value of a field, or absent.

    ``_scan`` keeps the FIRST occurrence of each ``(global, field)`` pair, so a
    later session's value can never be mistaken for the first one.  Session
    cardinality is checked separately, from ``session_messages`` and the
    declared count, before any of these values are relied on.
    """
    return scan.raw_fields.get((global_num, field_num), ABSENT)


def _utc_from_fit_date_time(raw: int) -> str:
    """FIT ``date_time`` seconds since 1989-12-31T00:00:00Z -> ISO-8601 UTC.

    MAP04: the pinned decoder adds Unix offset 631065600 seconds.  Computed with
    exact integer arithmetic and rendered without a floating-point conversion.
    """
    import datetime as _dt

    unix_seconds = raw + 631065600
    moment = _dt.datetime.fromtimestamp(unix_seconds, tz=_dt.timezone.utc)
    return moment.isoformat().replace("+00:00", "Z")


def _exact_scaled(raw: int, scale: int) -> str:
    """Exact decimal value from a raw scaled integer. No float in the path.

    MAP03 observes ``raw / scale - offset`` after invalid handling; these fields
    have offset 0, so the exact quotient is rendered as a decimal string.  No
    tolerance, rounding or near-equality threshold is applied, per D02's
    canonical fixed-precision arithmetic rule.
    """
    whole, remainder = divmod(raw, scale)
    if remainder == 0:
        return f"{whole}"
    decimals = str(remainder).rjust(len(str(scale)) - 1, "0")
    return f"{whole}.{decimals}"


def _integrity_and_structure(data: bytes) -> tuple[StructureScan | None, FileClassification | None]:
    """Order of checks matters and is part of the stable contract."""
    if not _PINNED_AVAILABLE:
        return None, _reject(
            REASON_DECODER_UNAVAILABLE,
            "pinned garmin-fit-sdk 21.217.0 profile/CRC is not importable; "
            "no classification is claimed",
        )
    if not data:
        return None, _reject(REASON_EMPTY_FILE, "file is empty")

    if len(data) < HEADER_WITHOUT_CRC_SIZE:
        return None, _reject(
            REASON_NOT_A_FIT_FILE,
            f"file is {len(data)} bytes; too short to contain a FIT header",
        )

    header_size = data[0]
    if header_size not in (HEADER_WITH_CRC_SIZE, HEADER_WITHOUT_CRC_SIZE):
        return None, _reject(
            REASON_NOT_A_FIT_FILE,
            f"header size byte is {header_size}; FIT requires 12 or 14",
        )
    if data[8:12] != FIT_SIGNATURE:
        return None, _reject(
            REASON_NOT_A_FIT_FILE,
            f"data type signature is {data[8:12]!r}, not b'.FIT'",
        )

    scan = _scan(data)
    header = scan.header

    # Integrity before semantics: D01 requires a failed integrity check to reject
    # the whole file, and the failure is reported, never repaired.
    if header.header_size == HEADER_WITH_CRC_SIZE and (
        header.header_crc_declared != header.header_crc_computed
    ):
        return None, _reject(
            REASON_HEADER_CRC_INVALID,
            f"header CRC is 0x{header.header_crc_declared:04X}, "
            f"computed 0x{header.header_crc_computed:04X}; reported, not repaired",
            protocol_version=f"{header.protocol_major}.{header.protocol_minor_tenths}",
            profile_version_raw=header.profile_version,
        )

    if header.header_size + header.data_size + CRC_SIZE > len(data):
        return None, _reject(
            REASON_MALFORMED_HEADER,
            f"declared content {header.header_size + header.data_size + CRC_SIZE} bytes "
            f"exceeds the {len(data)} bytes present",
            protocol_version=f"{header.protocol_major}.{header.protocol_minor_tenths}",
            profile_version_raw=header.profile_version,
        )

    file_crc_declared = _u(
        data[header.file_total_size : header.file_total_size + CRC_SIZE], True
    )
    file_crc_computed = _crc16(data[: header.file_total_size])
    if file_crc_declared != file_crc_computed:
        return None, _reject(
            REASON_FILE_CRC_INVALID,
            f"file CRC is 0x{file_crc_declared:04X}, computed 0x{file_crc_computed:04X}; "
            "reported, not repaired",
            protocol_version=f"{header.protocol_major}.{header.protocol_minor_tenths}",
            profile_version_raw=header.profile_version,
        )

    # Chained layout: D01 excludes it.  Detected from bytes remaining after one
    # complete segment, which is exactly what the pinned decoder's own read loop
    # would treat as a further file.
    if header.trailing_bytes > 0:
        return None, _reject(
            REASON_CHAINED_FILE_LAYOUT,
            f"{header.trailing_bytes} bytes remain after one complete FIT segment, "
            "which is a chained layout; D01 accepts single-session files only",
            protocol_version=f"{header.protocol_major}.{header.protocol_minor_tenths}",
            profile_version_raw=header.profile_version,
        )

    if header.protocol_major not in SUPPORTED_PROTOCOL_MAJORS:
        return None, _reject(
            REASON_UNSUPPORTED_PROTOCOL_VERSION,
            f"protocol version is {header.protocol_major}."
            f"{header.protocol_minor_tenths}; D01 covers FIT "
            f"{' and '.join(str(v) + '.x' for v in SUPPORTED_PROTOCOL_MAJORS)}",
            protocol_version=f"{header.protocol_major}.{header.protocol_minor_tenths}",
            profile_version_raw=header.profile_version,
        )

    if scan.structural_error is not None:
        return None, _reject(
            scan.structural_error,
            scan.structural_detail or "malformed FIT record structure",
            protocol_version=f"{header.protocol_major}.{header.protocol_minor_tenths}",
            profile_version_raw=header.profile_version,
        )

    return scan, None


def classify_bytes(
    data: bytes,
    *,
    max_messages: int | None = None,
    max_samples: int | None = None,
) -> FileClassification:
    """Classify one FIT file. Deterministic, pure, and free of any model call.

    ``max_messages``/``max_samples`` are the D01 per-file decoded resource limits
    (200,000 messages and 100,000 sample records).  They are inclusive: a file
    exactly at the limit is accepted, one byte-count of records over it is
    rejected.  ``None`` disables the check for callers that enforce limits
    separately in a resource-isolated worker.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("data must be bytes")
    data = bytes(data)

    scan, failure = _integrity_and_structure(data)
    if failure is not None:
        return failure
    if scan is None:  # explicit, not an assert: survives python -O
        raise RuntimeError(
            "internal contract violation: _integrity_and_structure returned "
            "neither a scan nor a rejection, so no disposition can be claimed"
        )
    header = scan.header
    protocol_label = f"{header.protocol_major}.{header.protocol_minor_tenths}"
    common = {
        "protocol_version": protocol_label,
        "profile_version_raw": header.profile_version,
        "message_count": scan.message_count,
        "record_sample_count": scan.record_sample_count,
    }

    # KNOWN DEFECT, reported rather than worked around.
    # discussion #297 / the TK10 matrix: the pinned Python decoder raises
    # "Compressed timestamp messages are not currently supported" (MAP03).  A file
    # carrying a compressed timestamp record is therefore NOT ACCEPTED here.  The
    # original bytes are retained by the caller for the open D01 engine/coverage
    # decision; this module neither reconstructs the timestamps, omits the
    # affected samples, nor labels partially decoded data as accepted.
    if scan.has_compressed_timestamp:
        return _reject(
            REASON_COMPRESSED_TIMESTAMP_UNSUPPORTED,
            "file contains a compressed timestamp record, which the pinned "
            f"decoder ({PINNED_SDK_VERSION}) cannot decode; the D01 engine and "
            "coverage decision for this path is still open (discussion #297)",
            **common,
        )

    if max_messages is not None and scan.message_count > max_messages:
        return _reject(
            REASON_MESSAGE_LIMIT_EXCEEDED,
            f"{scan.message_count} decoded messages exceeds the D01 per-file limit "
            f"of {max_messages}",
            **common,
        )
    if max_samples is not None and scan.record_sample_count > max_samples:
        return _reject(
            REASON_SAMPLE_LIMIT_EXCEEDED,
            f"{scan.record_sample_count} sample records exceeds the D01 per-file limit "
            f"of {max_samples}",
            **common,
        )

    # ---- file category -----------------------------------------------------
    file_id_type = _field(scan, MESG_NUM_FILE_ID, FILE_ID_TYPE)
    if not file_id_type.present:
        return _reject(
            REASON_MISSING_FILE_ID,
            "no file_id message with a type field; the file category cannot be "
            "established, and D01 admits activity files only",
            **common,
        )
    ft_name = file_type_name(file_id_type.raw) if file_id_type.usable else None
    if file_id_type.invalid or not file_id_type.usable:
        return _reject(
            REASON_INVALID_FILE_ID_TYPE,
            f"file_id.type raw value 0x{file_id_type.raw:02X} is the pinned invalid "
            "sentinel; the file category is unknown",
            file_type_raw=file_id_type.raw,
            **common,
        )
    if ft_name != "activity":
        # Each P0 exclusion gets its own reason (wellness, planned workout,
        # course) rather than a generic "unsupported".
        reason = FILE_TYPE_EXCLUSIONS.get(ft_name or "", REASON_UNSUPPORTED_FILE_TYPE)
        detail = f"file_id.type is {ft_name!r} (raw {file_id_type.raw}); "
        if reason == REASON_UNSUPPORTED_FILE_TYPE_COURSE:
            detail += "planned courses are outside P0 source scope"
        elif reason == REASON_UNSUPPORTED_FILE_TYPE_WORKOUT:
            detail += "planned workouts are outside P0 source scope"
        elif reason == REASON_UNSUPPORTED_FILE_TYPE_WELLNESS:
            detail += "wellness/monitoring data is outside P0 source scope"
        elif reason == REASON_UNSUPPORTED_FILE_TYPE_SCHEDULES:
            detail += "scheduled workout data is outside P0 source scope"
        else:
            detail += "D01 admits activity files only"
        return _reject(
            reason,
            detail,
            file_type_raw=file_id_type.raw,
            file_type_name=ft_name,
            **common,
        )

    # ---- session cardinality ----------------------------------------------
    activity_num = _field(scan, MESG_NUM_ACTIVITY, ACTIVITY_NUM_SESSIONS)
    activity_type = _field(scan, MESG_NUM_ACTIVITY, ACTIVITY_TYPE)
    declared_sessions = (
        activity_num.raw if activity_num.usable else None
    )
    if scan.session_messages == 0:
        return _reject(
            REASON_MISSING_SESSION,
            "no session message; D01 requires a single-session activity file",
            file_type_raw=file_id_type.raw,
            file_type_name=ft_name,
            declared_session_count=declared_sessions,
            observed_session_count=0,
            **common,
        )
    if scan.session_messages > 1:
        return _reject(
            REASON_MULTISPORT_LAYOUT,
            f"{scan.session_messages} session messages; D01 initial scope is "
            "single-session running and cycling",
            file_type_raw=file_id_type.raw,
            file_type_name=ft_name,
            declared_session_count=declared_sessions,
            observed_session_count=scan.session_messages,
            **common,
        )
    if activity_type.usable and activity_type.raw == 1:
        return _reject(
            REASON_MULTISPORT_LAYOUT,
            "activity.type is 'auto_multi_sport' (raw 1); a multisport layout is "
            "outside the D01 single-session scope",
            file_type_raw=file_id_type.raw,
            file_type_name=ft_name,
            activity_type_raw=activity_type.raw,
            activity_type_name=activity_type_name(activity_type.raw),
            declared_session_count=declared_sessions,
            observed_session_count=scan.session_messages,
            **common,
        )
    if declared_sessions is not None and declared_sessions != 1:
        return _reject(
            REASON_SESSION_COUNT_MISMATCH,
            f"activity.num_sessions declares {declared_sessions} but the file carries "
            f"{scan.session_messages} session message(s); D01 initial scope is "
            "single-session",
            file_type_raw=file_id_type.raw,
            file_type_name=ft_name,
            activity_type_raw=activity_type.raw if activity_type.usable else None,
            declared_session_count=declared_sessions,
            observed_session_count=scan.session_messages,
            **common,
        )

    warnings: list[str] = []
    if not activity_num.present and not activity_type.present:
        # The matrix lists activity/session cardinality handling as an open gap.
        # Exactly one decoded session message is taken as the single-session
        # assertion, and the absent activity message is disclosed rather than
        # silently assumed to be single-sport.  Routed to the architect as an
        # open contract item; see the TK11 report.
        warnings.append(WARN_ACTIVITY_MESSAGE_ABSENT)

    # ---- required semantics -----------------------------------------------
    session_base = {
        "file_type_raw": file_id_type.raw,
        "file_type_name": ft_name,
        "activity_type_raw": activity_type.raw if activity_type.usable else None,
        "declared_session_count": declared_sessions,
        "observed_session_count": scan.session_messages,
        **common,
    }

    sport = _field(scan, MESG_NUM_SESSION, SESSION_SPORT)
    if not sport.present:
        return _reject(
            REASON_MISSING_SPORT,
            "session message has no sport field; D01 requires sport as a normalised "
            "input",
            **session_base,
        )
    if sport.invalid:
        return _reject(
            REASON_INVALID_SPORT,
            f"session.sport raw value 0x{sport.raw:02X} is the pinned invalid sentinel",
            sport_raw=sport.raw,
            **session_base,
        )
    sport_label = sport_name(sport.raw)
    if sport.raw not in SPORT_IN_SCOPE:
        return _reject(
            REASON_UNSUPPORTED_SPORT,
            f"session.sport is {sport_label!r} (raw {sport.raw}); the D01 initial "
            "semantic scope is single-session running and cycling, indoor and "
            "outdoor. No alias or fallback is applied to an unmapped sport.",
            sport_raw=sport.raw,
            sport_name=sport_label,
            **session_base,
        )

    start = _field(scan, MESG_NUM_SESSION, SESSION_START_TIME)
    if not start.present:
        return _reject(
            REASON_MISSING_START_TIME,
            "session message has no start_time; D01 requires a session UTC start "
            "instant and forbids substituting local_timestamp, file creation time "
            "or the first sample",
            sport_raw=sport.raw,
            sport_name=sport_label,
            **session_base,
        )
    if start.invalid or (start.raw is not None and start.raw < DATE_TIME_MIN):
        return _reject(
            REASON_INVALID_START_TIME,
            f"session.start_time raw value {start.raw} is not a usable date_time "
            f"(invalid sentinel or below the pinned minimum {DATE_TIME_MIN})",
            sport_raw=sport.raw,
            sport_name=sport_label,
            **session_base,
        )

    elapsed = _field(scan, MESG_NUM_SESSION, SESSION_TOTAL_ELAPSED_TIME)
    if not elapsed.present:
        return _reject(
            REASON_MISSING_ELAPSED_DURATION,
            "session message has no total_elapsed_time; D01 requires a valid elapsed "
            "duration and forbids substituting timer time",
            sport_raw=sport.raw,
            sport_name=sport_label,
            **session_base,
        )
    if (
        elapsed.invalid
        or elapsed.raw is None
        or elapsed.raw == 0
        or elapsed.raw == INVALID_UINT32
    ):
        return _reject(
            REASON_INVALID_ELAPSED_DURATION,
            f"session.total_elapsed_time raw value {elapsed.raw} is not a valid elapsed "
            "duration (invalid sentinel or zero)",
            sport_raw=sport.raw,
            sport_name=sport_label,
            **session_base,
        )

    # ---- optional values: null plus a warning, never imputation -----------
    timer = _field(scan, MESG_NUM_SESSION, SESSION_TOTAL_TIMER_TIME)
    if not timer.present:
        warnings.append(WARN_TIMER_TIME_ABSENT)
    elif timer.invalid or timer.raw is None:
        warnings.append(WARN_TIMER_TIME_INVALID)

    distance = _field(scan, MESG_NUM_SESSION, SESSION_TOTAL_DISTANCE)
    if not distance.present:
        warnings.append(WARN_DISTANCE_ABSENT)
    elif distance.invalid or distance.raw is None:
        warnings.append(WARN_DISTANCE_INVALID)

    sub_sport = _field(scan, MESG_NUM_SESSION, SESSION_SUB_SPORT)
    if not sub_sport.present:
        warnings.append(WARN_SUB_SPORT_ABSENT)
    elif sub_sport.invalid or sub_sport.raw is None:
        warnings.append(WARN_SUB_SPORT_INVALID)
    elif sub_sport_name(sub_sport.raw) is None:
        warnings.append(WARN_SUB_SPORT_NOT_IN_SCOPE)

    if scan.record_sample_count == 0:
        warnings.append(WARN_NO_RECORD_SAMPLES)

    if scan.developer_field_definitions:
        # D01 permits ignoring developer fields for normalisation only when the
        # supported file structure is independently verified - it is walked
        # correctly here - and requires the ignored data to be reported.
        warnings.append(WARN_DEVELOPER_FIELDS_IGNORED)

    decoder_check = verify_with_pinned_decoder(data)
    return FileClassification(
        disposition="accepted",
        reason_code=REASON_ACCEPTED,
        reason_detail=(
            f"single-session {sport_label} activity, protocol {protocol_label}, "
            f"{scan.message_count} messages, {scan.record_sample_count} sample records"
        ),
        warnings=tuple(warnings),
        sport_raw=sport.raw,
        sport_name=sport_label,
        sub_sport_raw=sub_sport.raw if sub_sport.usable else None,
        sub_sport_name=sub_sport_name(sub_sport.raw) if sub_sport.usable else None,
        activity_type_name=(
            activity_type_name(activity_type.raw) if activity_type.usable else None
        ),
        start_time_utc=_utc_from_fit_date_time(start.raw),
        # The canonical comparison value, in the canonical unit. The raw field is
        # already an integer millisecond count (scale 1000), so this is the raw
        # value passed through `datara.canonical`, which refuses a non-integer and
        # enforces the millisecond domain. It is never derived from the seconds
        # string, so no decimal rescaling is possible.
        elapsed_duration_ms=require_elapsed_duration_ms(
            elapsed.raw,
            origin="classification.session.total_elapsed_time",
            unit=CANONICAL_DURATION_UNIT,
        ),
        elapsed_duration_seconds=_exact_scaled(elapsed.raw, 1000),
        timer_duration_seconds=(_exact_scaled(timer.raw, 1000) if timer.usable else None),
        total_distance_metres=(
            _exact_scaled(distance.raw, 100) if distance.usable else None
        ),
        decoder_verified=decoder_check.verified,
        decoder_check_error=decoder_check.error,
        **session_base,
    )


@dataclass(frozen=True)
class DecoderCheck:
    """Outcome of the independent pinned-decoder cross-check.

    ``verified`` alone would be misleading: an unavailable decoder and a decoder
    that reported an error are different facts, so the reason is carried with it
    and recorded on the classification.
    """

    verified: bool
    error: str | None = None
    available: bool = True


def verify_with_pinned_decoder(data: bytes) -> DecoderCheck:
    """Independently re-decode with the pinned decoder as a cross-check.

    ``verified`` means the pinned 21.217.0 decoder also decoded the file.  It is
    recorded as evidence only: per D01 and SR27, decoder success alone is never
    sufficient evidence of conformance, so it can never turn a rejection into an
    acceptance or lift a rejection.
    """
    if not _PINNED_AVAILABLE:
        return DecoderCheck(verified=False, error="pinned SDK unavailable", available=False)
    try:
        import io  # noqa: PLC0415

        from garmin_fit_sdk import Decoder  # noqa: PLC0415
        from garmin_fit_sdk.stream import Stream  # noqa: PLC0415

        # The pinned Stream calls ``buffered_reader.peek(1)``, which a bare
        # io.BytesIO does not provide; it needs a genuinely buffered reader.
        buffer = io.BufferedReader(io.BytesIO(data))
        _messages, errors = Decoder(Stream(buffer, len(data))).read()
    except Exception as exc:  # pragma: no cover - defensive
        return DecoderCheck(verified=False, error=f"raised {type(exc).__name__}: {exc}")
    if errors:
        return DecoderCheck(verified=False, error="; ".join(str(e) for e in errors))
    return DecoderCheck(verified=True)

