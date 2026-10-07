"""TK11 tests - approved file classification and diagnostics.

Trace: CUS01; SR01, SR02, SR27, SR32; FEAT01; WP02; D01.  TC01, TC19, TC21.

Run (from the repository root of the TK11 worktree)::

    python -X utf8 datara/tests/test_classification.py

stdlib ``unittest`` only, so the pinned command needs no test-runner dependency.
``datara/__init__.py`` is owned by another task, so this module loads the two
modules under test directly by path.  That keeps the pinned command runnable
whether or not the package ``__init__`` currently imports cleanly.

FIXTURE PROVENANCE (docs/management/source-evidence/fixture-provenance.md FIX01)
---------------------------------------------------------------------------
Every fixture here is **DATARA-authored synthetic**, produced by the
``_build_fit`` encoder in this file.  No upstream SDK sample binary is used,
copied, committed or hashed, because FIX02-FIX04 record that the applicable
redistribution rights for those paths are unresolved.

* Author: Worker - Torsten Maier_space-bunny-free-max_OpenCode (AI agent).
* Generator: ``_build_fit`` in this file, version ``TK11-FIXTURE-1``.
* Mapping reference: pinned ``garmin-fit-sdk`` 21.217.0 profile
  (``garmin_fit_sdk.Profile``), tag ``production/release/21.217.0-0-g248b1c46``.
* Structure reference: the pinned decoder's own header, definition-record, CRC
  and compressed-timestamp handling, read from ``garmin_fit_sdk`` 21.217.0.
* Expected values are authored here as literals, independent of the decoder, so
  a generator and decoder sharing a mapping error cannot be the sole oracle - the
  condition ``fixture-provenance.md`` requires.

The founder's private telemetry in ``demo_file/`` is never read, listed, hashed
or stat'ed by this suite; no test in this file refers to that path.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import struct
import sys
import unittest
from typing import Iterable, Sequence

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_TESTS_DIR))


def _load(name: str, relpath: str):
    """Load a module by path, independent of the package ``__init__``."""
    full = os.path.join(_REPO_ROOT, relpath)
    spec = importlib.util.spec_from_file_location(name, full)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ``classification`` has no intra-package imports; ``intake`` does a relative
# import, so it is loaded as a real package member of a throwaway package.
from datara import classification, intake  # noqa: E402

C = classification
I = intake


# ---------------------------------------------------------------------------
# DATARA-authored synthetic FIT encoder.  Version TK11-FIXTURE-1.
#
# Layout follows the pinned decoder's own reading rules for 21.217.0
# (garmin_fit_sdk.fit): bit 7 compressed, bit 6 definition, bit 5 developer data,
# bits 0-3 local message number.
#   header (14 bytes, with header CRC) | definition+data records | file CRC (2)
# Definition record: reserved=0, architecture=0 (LE), global_mesg_num (u16),
#   num_fields, then num_fields * (field_def_num, size, base_type).
# Normal record header: local_mesg_num (bits 0-3), no definition/developer bits.
# Compressed timestamp record: 0x80 | local_mesg_num, then 4 bytes of
#   local_mesg_num | (time_offset << 5).
# File CRC covers header + data, per the pinned ``check_integrity``.
# A definition is emitted once and reused for its data records, as real files do,
# so local message numbers stay inside the 4-bit field.
# ---------------------------------------------------------------------------
GENERATOR_VERSION = "TK11-FIXTURE-1"

# Base type codes, from the pinned fit.BASE_TYPE_DEFINITIONS.
ENUM, UINT8, UINT16, UINT32, SINT32 = 0x00, 0x02, 0x04, 0x06, 0x05

#: FIT ``date_time`` is seconds since 1989-12-31T00:00:00Z (the pinned decoder
#: adds Unix offset 631065600 to reach a Unix instant).  The raw value below is an
#: authored literal, and the expected UTC string asserted against it in the tests
#: is a SEPARATE authored literal - so the pair is not an oracle for itself.
#: raw 1142497800 == 2026-03-15T08:30:00Z.
FIT_TIME_BASE = 1142497800
EXPECTED_START_UTC = "2026-03-15T08:30:00Z"
#: The same instant as whole seconds since the Unix epoch, as the canonical tuple carries it.
EXPECTED_START_EPOCH_SECONDS = 1773563400
INVALID_UINT8 = 0xFF
INVALID_UINT16 = 0xFFFF
INVALID_UINT32 = 0xFFFFFFFF


def _crc16(payload: bytes) -> int:
    table = [
        0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
        0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
    ]

    def update(value: int, crc: int) -> int:
        temp = table[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ temp ^ table[value & 0xF]
        temp = table[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        return crc ^ temp ^ table[(value >> 4) & 0xF]

    crc = 0
    for byte in payload:
        crc = update(byte, crc)
    return crc


def _definition(
    local_num: int,
    global_num: int,
    fields: Sequence[tuple[int, int, int]],
    big_endian: bool = False,
) -> bytes:
    out = bytearray()
    out.append(0x40 | local_num)  # definition record, no developer data
    out.append(0)  # reserved
    out.append(1 if big_endian else 0)  # architecture: 0 = little, 1 = big
    out += struct.pack(">H" if big_endian else "<H", global_num)
    out.append(len(fields))
    for field_num, size, base_type in fields:
        out += bytes((field_num, size, base_type))
    return bytes(out)


def _data(
    local_num: int,
    fields: Sequence[tuple[int, int, int]],
    values: Sequence[int],
    big_endian: bool = False,
) -> bytes:
    assert len(fields) == len(values)
    out = bytearray()
    out.append(local_num)  # normal record, no definition/developer bits
    order = "big" if big_endian else "little"
    for (_field_num, size, _base_type), value in zip(fields, values):
        out += int(value).to_bytes(size, order)
    return bytes(out)


def _compressed_timestamp_record(local_num: int, time_offset: int) -> bytes:
    """The record form the pinned decoder raises on (MAP03 lines 347-348)."""
    packed = local_num | (time_offset << 5)
    return bytes((0x80 | local_num,)) + packed.to_bytes(4, "little")


def _build_fit(
    *,
    file_type: int = 4,
    sport: int | None = 1,
    sub_sport: int | None = None,
    start_time: int | None = FIT_TIME_BASE,
    total_elapsed_time: int | None = 1_800_000,  # 1800.000 s == 30 min
    total_timer_time: int | None | object = "omit",
    total_distance: int | None | object = "omit",
    num_sessions: int | None | object = "omit",
    activity_type: int | None | object = "omit",
    session_count: int = 1,
    record_count: int = 0,
    big_endian: bool = False,
    undefined_base_type: bool = False,
    compressed: bool = False,
    protocol_version: int = 0x10,
    profile_version: int = 2170,  # 21.70 as the header stores it
    header_size: int = 14,
    corrupt_header_crc: bool = False,
    corrupt_file_crc: bool = False,
    data_size_override: int | None = None,
    trailing_bytes: int = 0,
) -> bytes:
    """Build one synthetic FIT file. Every field default is an accepted file."""
    body = bytearray()
    local = 0

    if file_type is not None:
        fields = [(0, 1, ENUM)]
        body += _definition(local, 0, fields)
        body += _data(local, fields, [file_type])
        local += 1

    # Session fields are assembled once and the definition is reused, so repeated
    # session messages share a local message number.
    s_fields: list[tuple[int, int, int]] = []
    s_values: list[int] = []
    if start_time is not None:
        s_fields.append((2, 4, UINT32))
        s_values.append(start_time)
    if sport is not None:
        s_fields.append((5, 1, ENUM))
        s_values.append(sport)
    if sub_sport is not None:
        s_fields.append((6, 1, ENUM))
        s_values.append(sub_sport)
    if total_elapsed_time is not None:
        s_fields.append((7, 4, UINT32))
        s_values.append(total_elapsed_time)
    if total_timer_time != "omit":
        s_fields.append((8, 4, UINT32))
        s_values.append(0 if total_timer_time is None else int(total_timer_time))
    if total_distance != "omit":
        s_fields.append((9, 4, UINT32))
        s_values.append(0 if total_distance is None else int(total_distance))

    if record_count:
        rec_fields = [(253, 4, UINT32)]
        body += _definition(local, 20, rec_fields)
        for i in range(record_count):
            body += _data(local, rec_fields, [FIT_TIME_BASE + i * 60])
        local += 1

    if compressed:
        # The pinned decoder raises on the first compressed timestamp record, so
        # the definition it would reference is emitted first, as in a real file.
        body += _definition(local, 20, [(253, 4, UINT32)])
        body += _compressed_timestamp_record(local, 0)
        local += 1

    if undefined_base_type:
        # A field whose base type code 0x7F the pinned profile does not define.
        body += _definition(local, 18, [(2, 4, 0x7F)])
        body += _data(local, [(2, 4, 0x7F)], [FIT_TIME_BASE])
        local += 1

    if s_fields:
        for _ in range(session_count):
            body += _definition(local, 18, s_fields, big_endian)
            body += _data(local, s_fields, s_values, big_endian)
        local += 1

    if num_sessions != "omit" or activity_type != "omit":
        a_fields: list[tuple[int, int, int]] = []
        a_values: list[int] = []
        if num_sessions != "omit":
            a_fields.append((1, 2, UINT16))
            a_values.append(0 if num_sessions is None else int(num_sessions))
        if activity_type != "omit":
            a_fields.append((2, 1, ENUM))
            a_values.append(0 if activity_type is None else int(activity_type))
        body += _definition(local, 34, a_fields)
        body += _data(local, a_fields, a_values)
        local += 1

    data_size = len(body) if data_size_override is None else data_size_override
    header = bytearray()
    header.append(header_size)
    header.append(protocol_version)
    header += struct.pack("<H", profile_version)
    header += struct.pack("<I", data_size)
    header += b".FIT"
    if header_size == 14:
        header += struct.pack("<H", _crc16(bytes(header)))

    if header_size == 14 and corrupt_header_crc:
        header[12] ^= 0xFF

    out = bytes(header) + bytes(body)
    crc = _crc16(out)
    if corrupt_file_crc:
        crc ^= 0xFFFF
    out += struct.pack("<H", crc)
    out += b"\x00" * trailing_bytes
    return out


def _zip(*mutations: Iterable[bytes]) -> dict[str, bytes]:
    return {f"file{i}.fit": m for i, m in enumerate(mutations)}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class PinnedEnvironmentTest(unittest.TestCase):
    """The suite must run against the pinned artifact or say so, not fake it."""

    def test_pinned_sdk_is_importable(self):
        # Mutation: run in an environment without garmin-fit-sdk 21.217.0.
        # Then decoder_available() is False and this fails loudly instead of the
        # suite silently passing against an unpinned profile.
        self.assertTrue(
            C.decoder_available(),
            "garmin-fit-sdk 21.217.0 is required; no result may be claimed without it",
        )

    def test_profile_constants_match_the_tk10_matrix(self):
        # Mutation: change an expected constant here and the assertion fires.
        profile = C.pinned_profile()
        self.assertEqual(
            profile["version"],
            {"major": 21, "minor": 217, "patch": 0, "type": "Release"},
        )
        self.assertEqual(C.sport_name(1), "running")
        self.assertEqual(C.sport_name(2), "cycling")
        self.assertEqual(C.file_type_name(4), "activity")
        self.assertEqual(C.file_type_name(5), "workout")
        self.assertEqual(C.file_type_name(6), "course")
        self.assertEqual(C.file_type_name(28), "monitoring_daily")
        self.assertEqual(C.activity_type_name(1), "auto_multi_sport")


class AcceptCaseTest(unittest.TestCase):
    """A valid file classifies as accepted, with D01's four required inputs."""

    def test_valid_run_is_accepted_with_required_inputs(self):
        # Mutation: drop start_time -> REASON_MISSING_START_TIME, not accepted.
        data = _build_fit()
        result = C.classify_bytes(data)
        self.assertEqual(result.disposition, "accepted", result.reason_detail)
        self.assertEqual(result.reason_code, C.REASON_ACCEPTED)
        # Authored expected values, written independently of the decoder.
        self.assertEqual(result.sport_name, "running")
        self.assertEqual(result.sport_raw, 1)
        self.assertEqual(result.start_time_utc, EXPECTED_START_UTC)
        self.assertEqual(result.elapsed_duration_seconds, "1800")
        self.assertIsNone(result.timer_duration_seconds)
        self.assertIn(C.WARN_TIMER_TIME_ABSENT, result.warnings)

    def test_valid_cycling_with_optional_values_is_accepted(self):
        # Mutation: set sport=1 -> running; the assertion on 'cycling' fails.
        data = _build_fit(
            sport=2,
            sub_sport=7,  # road
            total_timer_time=1_800_000,
            total_distance=5_000_000,  # 50000.00 m
        )
        result = C.classify_bytes(data)
        self.assertEqual(result.disposition, "accepted", result.reason_detail)
        self.assertEqual(result.sport_name, "cycling")
        self.assertEqual(result.sub_sport_name, "road")
        self.assertEqual(result.timer_duration_seconds, "1800")
        self.assertEqual(result.total_distance_metres, "50000")

    def test_indoor_run_is_accepted_without_gps(self):
        # Mutation: sub_sport=2 (street) -> sub_sport_name changes and fails.
        data = _build_fit(sport=1, sub_sport=45, record_count=0)  # indoor_running
        result = C.classify_bytes(data)
        self.assertEqual(result.disposition, "accepted", result.reason_detail)
        self.assertEqual(result.sub_sport_name, "indoor_running")
        # Missing GPS is valid for indoor activities: no sample warning is an error.
        self.assertIn(C.WARN_NO_RECORD_SAMPLES, result.warnings)

    def test_cross_check_result_is_propagated_from_the_pinned_decoder(self):
        """The classifier must actually consult the pinned decoder and report it.

        Without this, hard-coding ``DecoderCheck(verified=True)`` would be
        invisible: every other test only ever sees a cross-check that agrees.

        Mutation: replacing the ``verify_with_pinned_decoder(data)`` call with a
        constant makes the call count zero and fails this test.
        """
        calls: list[bytes] = []
        original = C.verify_with_pinned_decoder

        def spy(data):
            calls.append(bytes(data))
            return C.DecoderCheck(verified=False, error="synthetic disagreement")

        C.verify_with_pinned_decoder = spy
        try:
            result = C.classify_bytes(_build_fit())
        finally:
            C.verify_with_pinned_decoder = original
        self.assertEqual(len(calls), 1, "the pinned decoder must be consulted exactly once")
        self.assertFalse(result.decoder_verified)
        self.assertEqual(result.decoder_check_error, "synthetic disagreement")

    def test_absent_pinned_decoder_reports_unavailable_instead_of_guessing(self):
        """Without the pinned artifact the answer is 'unavailable', not a guess.

        D01 requires pinned official rules; an environment without them must not
        silently fall back to hand-rolled behaviour.

        Mutation: returning a successful DecoderCheck on the unavailable path
        fails the first assertion.
        """
        check = C.verify_with_pinned_decoder(_build_fit())
        self.assertTrue(check.available)

        original = C._PINNED_AVAILABLE
        C._PINNED_AVAILABLE = False
        try:
            unavailable = C.verify_with_pinned_decoder(_build_fit())
            result = C.classify_bytes(_build_fit())
        finally:
            C._PINNED_AVAILABLE = original
        self.assertFalse(unavailable.verified)
        self.assertFalse(unavailable.available)
        self.assertEqual(result.disposition, "rejected")
        self.assertEqual(result.reason_code, C.REASON_DECODER_UNAVAILABLE)

    def test_pinned_decoder_genuinely_cannot_read_a_compressed_file(self):
        """Direct, quotable evidence for the known pinned-decoder defect.

        Asserts the pinned 21.217.0 decoder's OWN error text, so the blocker in
        discussion #297 is demonstrated rather than restated.  If a future decoder
        release fixes this, this test fails and the change must be a deliberate
        contract decision (the D01 engine/coverage question), not a silent win.

        Mutation: replacing the decoder call with a stub that reports success
        fails the ``verified is False`` assertion.
        """
        data = _build_fit(compressed=True)
        check = C.verify_with_pinned_decoder(data)
        self.assertFalse(check.verified)
        self.assertIn("Compressed timestamp", check.error or "")
        # The classifier's own disposition agrees, and is the one that gates.
        result = C.classify_bytes(data)
        self.assertEqual(result.reason_code, C.REASON_COMPRESSED_TIMESTAMP_UNSUPPORTED)
        self.assertEqual(result.disposition, "rejected")

    def test_undefined_base_type_rejects_with_the_true_cause(self):
        """An unreadable field must not be reported as a missing one.

        The pinned decoder fails such a file with "Invalid field definition base
        type".  Without an explicit rule the classifier would instead surface a
        downstream symptom (``missing_required_sport``), which would misinform the
        athlete about why their file was rejected.

        Mutation: removing the base-type check makes this report
        ``missing_required_sport`` instead.
        """
        data = _build_fit(undefined_base_type=True)
        self.assertEqual(
            C.classify_bytes(data).reason_code, C.REASON_UNDEFINED_BASE_TYPE
        )

    def test_big_endian_message_is_read_correctly(self):
        """The architecture byte is honoured, not assumed little-endian.

        Mutation: forcing little-endian reads yields a different start instant
        (or an invalid one) and fails the expected-value assertion.
        """
        data = _build_fit(big_endian=True)
        result = C.classify_bytes(data)
        self.assertEqual(result.disposition, "accepted", result.reason_detail)
        self.assertEqual(result.start_time_utc, EXPECTED_START_UTC)
        self.assertEqual(result.elapsed_duration_seconds, "1800")

    def test_pinned_decoder_also_reads_an_accepted_file(self):
        # Mutation: corrupt the body without fixing the CRC -> decoder disagrees.
        data = _build_fit()
        result = C.classify_bytes(data)
        self.assertTrue(result.decoder_verified)


class UnsupportedDimensionTest(unittest.TestCase):
    """Each unsupported dimension rejects with its own stable reason."""

    def _reason(self, **kwargs) -> str:
        return C.classify_bytes(_build_fit(**kwargs)).reason_code

    def test_unsupported_sport_rejects(self):
        # Mutation: sport=1 -> running -> accepted, reason_code != this.
        self.assertEqual(self._reason(sport=5), C.REASON_UNSUPPORTED_SPORT)  # swimming

    def test_sport_alias_is_not_silently_applied(self):
        # 'generic' (0) and 'transition' (3) must not be folded into running.
        # Mutation: removing the in-scope check would make these accepted.
        self.assertEqual(self._reason(sport=0), C.REASON_UNSUPPORTED_SPORT)
        self.assertEqual(self._reason(sport=3), C.REASON_UNSUPPORTED_SPORT)
        self.assertEqual(self._reason(sport=11), C.REASON_UNSUPPORTED_SPORT)  # walking

    def test_invalid_sport_sentinel_rejects_distinctly(self):
        # Mutation: present-but-invalid must differ from absent.
        self.assertEqual(self._reason(sport=None), C.REASON_MISSING_SPORT)
        self.assertEqual(self._reason(sport=INVALID_UINT8), C.REASON_INVALID_SPORT)

    def test_missing_required_semantics_reject_distinctly(self):
        # Mutation: restoring the field makes each of these accepted.
        self.assertEqual(
            self._reason(start_time=None), C.REASON_MISSING_START_TIME
        )
        self.assertEqual(self._reason(total_elapsed_time=None), C.REASON_MISSING_ELAPSED_DURATION)
        # Present but invalid is a different cause from absent.
        self.assertEqual(
            self._reason(total_elapsed_time=INVALID_UINT32),
            C.REASON_INVALID_ELAPSED_DURATION,
        )
        self.assertEqual(
            self._reason(total_elapsed_time=0), C.REASON_INVALID_ELAPSED_DURATION
        )
        self.assertEqual(self._reason(start_time=INVALID_UINT32), C.REASON_INVALID_START_TIME)
        # Below the pinned date_time minimum.
        self.assertEqual(self._reason(start_time=1), C.REASON_INVALID_START_TIME)

    def test_multisport_layout_rejects(self):
        # Mutation: two session messages -> 'multisport_or_chained_layout'.
        self.assertEqual(self._reason(session_count=2), C.REASON_MULTISPORT_LAYOUT)
        self.assertEqual(
            self._reason(activity_type=1), C.REASON_MULTISPORT_LAYOUT
        )  # auto_multi_sport
        # Declared count disagreeing with the observed count is its own reason.
        self.assertEqual(
            self._reason(num_sessions=2, session_count=1),
            C.REASON_SESSION_COUNT_MISMATCH,
        )

    def test_missing_session_rejects(self):
        # Mutation: adding a session message makes this accepted.
        data = _build_fit(session_count=0)
        self.assertEqual(C.classify_bytes(data).reason_code, C.REASON_MISSING_SESSION)

    def test_every_rejection_reason_is_in_the_frozen_vocabulary(self):
        # Mutation: returning an unlisted code trips the assert in _reject.
        for kwargs in (
            {"sport": 5},
            {"file_type": 5},
            {"file_type": 6},
            {"file_type": 28},
            {"start_time": None},
            {"total_elapsed_time": 0},
            {"session_count": 2},
        ):
            result = C.classify_bytes(_build_fit(**kwargs))
            self.assertEqual(result.disposition, "rejected", kwargs)
            self.assertIn(result.reason_code, C.REJECTION_REASONS, kwargs)


class P0SourceScopeExclusionTest(unittest.TestCase):
    """Wellness, planned workout/course and archive imports reject, by name.

    D01 names these exclusions explicitly, so each must be rejected with its own
    reason rather than landing in a generic bucket by accident.
    """

    def _reason(self, file_type: int) -> str:
        return C.classify_bytes(_build_fit(file_type=file_type)).reason_code

    def test_planned_workout_rejects_with_its_own_reason(self):
        # Mutation: file_type=4 -> accepted, reason_code != this.
        self.assertEqual(self._reason(5), C.REASON_UNSUPPORTED_FILE_TYPE_WORKOUT)

    def test_course_rejects_with_its_own_reason(self):
        self.assertEqual(self._reason(6), C.REASON_UNSUPPORTED_FILE_TYPE_COURSE)

    def test_schedules_reject_with_its_own_reason(self):
        self.assertEqual(self._reason(7), C.REASON_UNSUPPORTED_FILE_TYPE_SCHEDULES)

    def test_wellness_rejects_with_its_own_reason(self):
        # 21.217.0 carries wellness data under the monitoring / weight /
        # blood-pressure file categories.  Raw values are taken from the pinned
        # enum, not assumed: 28=monitoring_daily, 9=weight, 14=blood_pressure.
        for raw, name in (
            (28, "monitoring_daily"),
            (9, "weight"),
            (14, "blood_pressure"),
        ):
            with self.subTest(file_type=name):
                self.assertEqual(
                    self._reason(raw), C.REASON_UNSUPPORTED_FILE_TYPE_WELLNESS
                )
                # The pinned enum really does name it that.
                self.assertEqual(C.file_type_name(raw), name)

    def test_other_non_activity_file_type_rejects(self):
        self.assertEqual(self._reason(2), C.REASON_UNSUPPORTED_FILE_TYPE)  # settings
        self.assertEqual(self._reason(10), C.REASON_UNSUPPORTED_FILE_TYPE)  # totals

    def test_arbitrary_archive_import_is_not_a_fit_file(self):
        # A .zip is not a FIT container: no .FIT signature.
        # Mutation: real FIT signature -> different reason.
        self.assertEqual(
            C.classify_bytes(b"PK\x03\x04" + b"\x00" * 200).reason_code,
            C.REASON_NOT_A_FIT_FILE,
        )

    def test_file_id_type_absent_or_invalid_rejects(self):
        self.assertEqual(
            C.classify_bytes(_build_fit(file_type=None)).reason_code,
            C.REASON_MISSING_FILE_ID,
        )
        self.assertEqual(
            C.classify_bytes(_build_fit(file_type=INVALID_UINT8)).reason_code,
            C.REASON_INVALID_FILE_ID_TYPE,
        )


class IntegrityTest(unittest.TestCase):
    """Integrity failures are reported, never silently repaired."""

    def test_header_crc_failure_rejects_and_is_not_repaired(self):
        # Mutation: corrupt_header_crc=False -> accepted.
        data = _build_fit(corrupt_header_crc=True)
        result = C.classify_bytes(data)
        self.assertEqual(result.reason_code, C.REASON_HEADER_CRC_INVALID)
        self.assertIn("not repaired", result.reason_detail)
        # Proof of no repair: the returned object carries no usable activity.
        self.assertIsNone(result.start_time_utc)
        self.assertIsNone(result.elapsed_duration_seconds)
        self.assertFalse(result.accepted)

    def test_file_crc_failure_rejects_and_is_not_repaired(self):
        # Mutation: corrupt_file_crc=False -> accepted.
        result = C.classify_bytes(_build_fit(corrupt_file_crc=True))
        self.assertEqual(result.reason_code, C.REASON_FILE_CRC_INVALID)
        self.assertIn("not repaired", result.reason_detail)
        self.assertIsNone(result.elapsed_duration_seconds)

    def test_body_mutation_breaks_the_file_crc(self):
        # A single flipped byte in the data section must be caught, not tolerated.
        data = bytearray(_build_fit())
        data[20] ^= 0x01
        self.assertEqual(
            C.classify_bytes(bytes(data)).reason_code, C.REASON_FILE_CRC_INVALID
        )

    def test_malformed_header_rejects(self):
        # Mutation: data_size_override=None -> accepted.
        self.assertEqual(
            C.classify_bytes(_build_fit(data_size_override=999_999)).reason_code,
            C.REASON_MALFORMED_HEADER,
        )
        self.assertEqual(
            C.classify_bytes(_build_fit(header_size=13)).reason_code,
            C.REASON_NOT_A_FIT_FILE,
        )
        self.assertEqual(C.classify_bytes(b"").reason_code, C.REASON_EMPTY_FILE)

    def test_non_fit_signature_rejects(self):
        data = bytearray(_build_fit())
        data[8:12] = b"XXXX"
        self.assertEqual(
            C.classify_bytes(bytes(data)).reason_code, C.REASON_NOT_A_FIT_FILE
        )


class ProtocolAndLayoutTest(unittest.TestCase):
    """Protocol coverage is FIT 1.0 and 2.0; chained and compressed reject."""

    def test_fit_1_0_and_2_0_are_covered(self):
        # Mutation: protocol_version=0x10 -> the 2.0 assertion fails.
        self.assertEqual(
            C.classify_bytes(_build_fit(protocol_version=0x10)).disposition,
            "accepted",
        )
        self.assertEqual(
            C.classify_bytes(_build_fit(protocol_version=0x20)).disposition,
            "accepted",
        )

    def test_other_protocol_versions_reject(self):
        # Mutation: widening SUPPORTED_PROTOCOL_MAJORS would make this pass wrongly.
        self.assertEqual(
            C.classify_bytes(_build_fit(protocol_version=0x30)).reason_code,
            C.REASON_UNSUPPORTED_PROTOCOL_VERSION,
        )

    def test_chained_layout_rejects(self):
        # A chained file carries a further complete segment after the first, so
        # bytes remain after one header+data+CRC segment - which is precisely
        # what the pinned decoder's read loop would pick up as another file.
        # Mutation: trailing_bytes=0 -> accepted.
        self.assertEqual(
            C.classify_bytes(_build_fit(trailing_bytes=64)).reason_code,
            C.REASON_CHAINED_FILE_LAYOUT,
        )
        # A genuine second segment, not just padding.
        first = _build_fit()
        self.assertEqual(
            C.classify_bytes(first + first).reason_code,
            C.REASON_CHAINED_FILE_LAYOUT,
        )

    def test_compressed_timestamp_is_reported_not_papered_over(self):
        """The known pinned-decoder defect, asserted rather than hidden.

        discussion #297: garmin-fit-sdk 21.217.0 cannot decode compressed
        timestamp records.  A file containing one must be REJECTED with a stable
        reason, never partially decoded and never labelled accepted.
        """
        # Mutation: making classify_bytes accept this file would fail here, which
        # is the point - a future decoder change must be a deliberate contract
        # change, not an accident.
        result = C.classify_bytes(_build_fit(compressed=True))
        self.assertEqual(result.disposition, "rejected")
        self.assertEqual(
            result.reason_code, C.REASON_COMPRESSED_TIMESTAMP_UNSUPPORTED
        )
        self.assertIn("21.217.0", result.reason_detail)
        self.assertIsNone(result.start_time_utc)
        # The pinned decoder really does fail on this file, which is why.
        self.assertFalse(result.decoder_verified)

    def test_no_model_call_and_no_forbidden_entity(self):
        """The binding architectural condition, asserted mechanically via AST.

        Parses both modules and inspects declared class names, function names and
        annotated/assigned field names.  Checking the syntax tree rather than raw
        text keeps the assertion meaningful: prose may legitimately discuss the
        exclusion, and an unrelated identifier such as ``DecoderUnavailable``
        must not trip it.

        Mutation: declaring ``class Run``, ``class Assessment``, a field named
        ``latest_result``, or any un-frozen dataclass trips these assertions.
        """
        import ast

        forbidden = {
            "run",
            "runs",
            "assessment",
            "assessments",
            "finding",
            "findings",
            "result",
            "results",
            "latest_result",
            "recommendation",
            "recommendations",
            "verdict",
            "readiness",
            "outcome_of_skill",
        }

        for relpath in ("datara/classification.py", "datara/intake.py"):
            with self.subTest(module=relpath):
                path = os.path.join(_REPO_ROOT, relpath)
                with open(path, encoding="utf-8") as handle:
                    tree = ast.parse(handle.read(), filename=path)

                declared: list[str] = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        declared.append(node.name)
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        declared.append(node.name)
                    elif isinstance(node, ast.AnnAssign) and isinstance(
                        node.target, ast.Name
                    ):
                        declared.append(node.target.id)
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                declared.append(target.id)

                offenders = [
                    name
                    for name in declared
                    if name.lower() in forbidden
                    or name.lower().startswith("latest_")
                ]
                self.assertEqual(
                    offenders,
                    [],
                    f"{relpath} declares a prohibited entity: {offenders}",
                )

                # No mutable latest-value pointer: every dataclass is frozen.
                # A ``@dataclass`` decorator is in ``decorator_list``, NOT in
                # ``bases``, so the check must read decorator_list - checking
                # bases silently never runs.
                for node in ast.walk(tree):
                    if not isinstance(node, ast.ClassDef):
                        continue
                    decorator_names: set[str] = set()
                    is_dataclass = False
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Name) and dec.id == "dataclass":
                            is_dataclass = True
                            decorator_names.add("dataclass")
                        elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                            if dec.func.id == "dataclass":
                                is_dataclass = True
                                decorator_names.add("dataclass")
                            for kw in dec.keywords:
                                if kw.arg:
                                    decorator_names.add(kw.arg)
                    if is_dataclass:
                        self.assertIn(
                            "frozen",
                            decorator_names,
                            f"{relpath}:{node.name} must be a frozen dataclass, so no "
                            "value on it can be a mutable latest-result pointer",
                        )


class DeterminismTest(unittest.TestCase):
    """Repeat classification is deterministic and byte-identical."""

    def test_repeated_classification_is_identical(self):
        data = _build_fit(total_timer_time=1_800_000)
        first = C.classify_bytes(data)
        for _ in range(5):
            again = C.classify_bytes(data)
            self.assertEqual(first, again)

    def test_repeated_rejection_is_identical(self):
        data = _build_fit(sport=5)
        self.assertEqual(C.classify_bytes(data), C.classify_bytes(data))

    def test_batch_planning_is_reproducible(self):
        files = [("a.fit", _build_fit()), ("b.fit", _build_fit(sport=5))]
        first = I.plan_import("owner-1", files)
        second = I.plan_import("owner-1", files)
        self.assertEqual(first, second)

    def test_rejected_file_contributes_nothing_to_accepted_history(self):
        data = _build_fit(sport=5)
        plan = I.plan_import("owner-1", [("a.fit", data)])
        self.assertEqual(len(plan.accepted), 0)
        self.assertEqual(plan.accepted_source_objects(), ())
        outcome = plan.outcomes[0]
        self.assertTrue(outcome.discard_raw_bytes)
        self.assertIsNone(outcome.quarantine)


class ResourceLimitTest(unittest.TestCase):
    """Limits are inclusive: exactly at the limit passes, one over fails."""

    def test_file_size_limit_boundary(self):
        data = _build_fit()
        # Mutation: '>' -> '>=' would reject the exactly-at-limit file.
        plan = I.plan_import("o", [("a.fit", data)], max_file_bytes=len(data))
        self.assertEqual(len(plan.accepted), 1)
        plan = I.plan_import("o", [("a.fit", data)], max_file_bytes=len(data) - 1)
        self.assertEqual(plan.outcomes[0].reason_code, C.REASON_FILE_SIZE_LIMIT_EXCEEDED)
        self.assertEqual(plan.outcomes[0].decided_by, "resource_limit")

    def test_message_and_sample_limits_are_inclusive(self):
        data = _build_fit(record_count=3)
        result = C.classify_bytes(data, max_messages=data and 10_000, max_samples=3)
        self.assertEqual(result.disposition, "accepted", result.reason_detail)
        over = C.classify_bytes(data, max_samples=2)
        self.assertEqual(over.reason_code, C.REASON_SAMPLE_LIMIT_EXCEEDED)
        # A limit breach is a rejection, not a warning on an accepted file.
        self.assertEqual(over.disposition, "rejected")
        self.assertIsNone(over.start_time_utc)

    def test_batch_file_count_limit(self):
        files = [(f"f{i}.fit", _build_fit()) for i in range(3)]
        plan = I.plan_import("o", files, max_batch_files=2)
        self.assertEqual(len(plan.outcomes), 3)
        for outcome in plan.outcomes:
            self.assertEqual(
                outcome.reason_code, C.REASON_BATCH_FILE_COUNT_EXCEEDED
            )
        # The batch is not silently truncated to a subset.
        self.assertEqual(len(plan.accepted), 0)

    def test_batch_file_count_limit_boundary(self):
        # Exactly at the limit is accepted, one over is rejected.
        # Mutation: '>=' would reject the exactly-at-limit batch.
        # Exactly at the limit is accepted, one over is rejected.  The two files
        # must differ, or the second would be an idempotent duplicate rather
        # than a second accepted activity.
        run = _build_fit(sport=1)
        ride = _build_fit(sport=2, sub_sport=7)
        at_limit = I.plan_import("o", [("run.fit", run), ("ride.fit", ride)], max_batch_files=2)
        self.assertEqual(len(at_limit.accepted), 2)
        over = I.plan_import(
            "o",
            [("run.fit", run), ("ride.fit", ride), ("run2.fit", _build_fit(sport=1, sub_sport=2))],
            max_batch_files=2,
        )
        self.assertEqual(len(over.accepted), 0)

    def test_plan_import_enforces_the_supplied_message_and_sample_limits(self):
        """The limits must be wired from plan_import through to the classifier.

        Calling ``classify_bytes`` directly would not notice if plan_import
        stopped passing them on.

        Mutation: passing ``max_samples=None`` / ``max_messages=None`` from
        plan_import fails these.
        """
        data = _build_fit(record_count=4)
        plan = I.plan_import(
            "o", [("a.fit", data)], max_file_sample_records=4, max_file_messages=10_000
        )
        self.assertEqual(len(plan.accepted), 1)
        over_samples = I.plan_import(
            "o", [("a.fit", data)], max_file_sample_records=3
        )
        self.assertEqual(over_samples.outcomes[0].reason_code, C.REASON_SAMPLE_LIMIT_EXCEEDED)
        over_messages = I.plan_import("o", [("a.fit", data)], max_file_messages=2)
        self.assertEqual(
            over_messages.outcomes[0].reason_code, C.REASON_MESSAGE_LIMIT_EXCEEDED
        )

    def test_d01_default_limits_are_the_selected_values_and_are_wired(self):
        """The shipped defaults are D01's chosen numbers, and actually reach the call.

        The other limit tests pass explicit values, so without this the defaults
        themselves could drift or be bypassed and no test would notice.
        """
        self.assertEqual(I.MAX_FILE_BYTES, 16 * 1024 * 1024)
        self.assertEqual(I.MAX_BATCH_FILES, 50)
        self.assertEqual(I.MAX_BATCH_BYTES, 128 * 1024 * 1024)
        self.assertEqual(I.MAX_FILE_MESSAGES, 200_000)
        self.assertEqual(I.MAX_FILE_SAMPLE_RECORDS, 100_000)
        self.assertEqual(I.MAX_FILE_WALL_SECONDS, 60)
        self.assertEqual(I.MAX_FILE_MEMORY_MIB, 512)

        import inspect

        params = inspect.signature(I.plan_import).parameters
        self.assertEqual(params["max_file_bytes"].default, I.MAX_FILE_BYTES)
        self.assertEqual(params["max_batch_files"].default, I.MAX_BATCH_FILES)
        self.assertEqual(params["max_batch_bytes"].default, I.MAX_BATCH_BYTES)
        self.assertEqual(params["max_file_messages"].default, I.MAX_FILE_MESSAGES)
        self.assertEqual(
            params["max_file_sample_records"].default, I.MAX_FILE_SAMPLE_RECORDS
        )

    def test_batch_byte_limit(self):
        data = _build_fit()
        plan = I.plan_import("o", [("a.fit", data)], max_batch_bytes=len(data) - 1)
        self.assertEqual(
            plan.outcomes[0].reason_code, C.REASON_BATCH_SIZE_LIMIT_EXCEEDED
        )


class DuplicateAndConflictTest(unittest.TestCase):
    """Digest idempotence first, then exact-tuple quarantine."""

    def test_identical_bytes_are_idempotent_within_a_batch(self):
        data = _build_fit()
        plan = I.plan_import("o", [("a.fit", data), ("copy.fit", data)])
        self.assertEqual(len(plan.accepted), 1)
        self.assertEqual(len(plan.duplicates), 1)
        self.assertEqual(plan.duplicates[0].decided_by, "exact_digest_duplicate")

    def test_digest_against_existing_history_is_idempotent(self):
        data = _build_fit()
        digest = hashlib.sha256(data).hexdigest()
        plan = I.plan_import("o", [("a.fit", data)], accepted_digests=[digest])
        self.assertEqual(len(plan.duplicates), 1)
        self.assertEqual(plan.duplicates[0].duplicate_of_digest, digest)
        self.assertEqual(len(plan.accepted), 0)

    def test_different_bytes_same_tuple_are_quarantined(self):
        first = _build_fit()
        # Same sport, start and elapsed; different bytes (different sub_sport).
        second = _build_fit(sub_sport=2)
        self.assertNotEqual(first, second)
        plan = I.plan_import("o", [("a.fit", first), ("b.fit", second)])
        self.assertEqual(len(plan.accepted), 1)
        self.assertEqual(len(plan.quarantined), 1)
        record = plan.quarantined[0].quarantine
        assert record is not None
        self.assertEqual(record.owner_key, "o")
        self.assertNotEqual(record.conflicting_digest, record.candidate_digest)
        # The logical tuple is the canonical B3 type: an identity-independent
        # value object of exactly three integers, in milliseconds. Asserting the
        # components rather than len() is stronger, and it is what distinguishes a
        # genuine quarantine from an accidental mismatch.
        identity = record.logical_tuple
        self.assertEqual(
            (
                identity.sport_code,
                identity.start_epoch_seconds,
                identity.elapsed_duration_ms,
            ),
            (1, EXPECTED_START_EPOCH_SECONDS, 1800000),
            'the quarantined candidate must carry the exact canonical tuple',
        )

    def test_conflict_is_not_resolved_silently(self):
        # Mutation: auto-resolving to 'accepted' would fail this.
        first = _build_fit()
        second = _build_fit(sub_sport=2)
        plan = I.plan_import(
            "o", [("a.fit", first), ("b.fit", second)], accepted_digests=[]
        )
        quarantined = plan.quarantined[0]
        self.assertFalse(quarantined.accepted)
        # A quarantined file yields no accepted source object.
        self.assertEqual(len(plan.accepted_source_objects()), 1)

    def test_different_owners_never_collide(self):
        data = _build_fit()
        other = _build_fit(sub_sport=2)
        plan = I.plan_import("owner-1", [("a.fit", data)])
        plan2 = I.plan_import("owner-2", [("a.fit", other)])
        self.assertEqual(len(plan.accepted), 1)
        self.assertEqual(len(plan2.accepted), 1)

    def test_no_tolerance_matching_on_near_misses(self):
        # One second apart must NOT be treated as a duplicate: D01 forbids
        # tolerance matching.
        first = _build_fit()
        second = _build_fit(total_elapsed_time=1_800_000 + 1000)
        plan = I.plan_import("o", [("a.fit", first), ("b.fit", second)])
        self.assertEqual(len(plan.accepted), 2)
        self.assertEqual(len(plan.quarantined), 0)

    def test_owner_is_required(self):
        # Mutation: dropping the guard would allow unowned intake.
        with self.assertRaises(ValueError):
            I.plan_import("", [("a.fit", _build_fit())])


class BatchIsolationTest(unittest.TestCase):
    """One rejected file does not undo independently accepted files."""

    def test_mixed_batch_reports_per_file_outcomes(self):
        files = [
            ("good1.fit", _build_fit()),
            ("bad-sport.fit", _build_fit(sport=5)),
            ("good2.fit", _build_fit(sport=2, sub_sport=6, total_timer_time=1_800_000)),
            ("crc.fit", _build_fit(corrupt_file_crc=True)),
        ]
        plan = I.plan_import("o", files)
        self.assertEqual(len(plan.accepted), 2)
        self.assertEqual(len(plan.rejected), 2)
        self.assertEqual(
            {o.reason_code for o in plan.rejected},
            {C.REASON_UNSUPPORTED_SPORT, C.REASON_FILE_CRC_INVALID},
        )
        # Every accepted file has a complete set of D01 required inputs.
        for obj in plan.accepted_source_objects():
            self.assertIsNotNone(obj["sport"])
            self.assertIsNotNone(obj["start_time_utc"])
            self.assertIsNotNone(obj["elapsed_duration_seconds"])
            self.assertEqual(len(str(obj["digest_sha256"])), 64)

    def test_no_file_contributes_a_partial_accepted_activity(self):
        # A file with a valid sport but a missing required duration is rejected
        # whole - its sport never becomes an accepted history row.
        plan = I.plan_import("o", [("a.fit", _build_fit(total_elapsed_time=None))])
        self.assertEqual(len(plan.accepted), 0)
        self.assertEqual(plan.outcomes[0].reason_code, C.REASON_MISSING_ELAPSED_DURATION)
        self.assertEqual(plan.accepted_source_objects(), ())


def _encoder_file_id_and_session() -> bytes:
    """One FIT file written by the pinned SDK's own encoder.

    Shared by the tests below so the fixture is built once and every assertion
    runs against identical bytes.
    """

    from garmin_fit_sdk.encoder import Encoder

    enc = Encoder()
    enc.write_mesg({"mesg_num": 0, "type": 4, "manufacturer": 1, "product": 1,
                    "serial_number": 1, "time_created": FIT_TIME_BASE})
    enc.write_mesg({"mesg_num": 18, "sport": 1, "sub_sport": 7,
                    "start_time": FIT_TIME_BASE, "total_elapsed_time": 1800.0,
                    "total_timer_time": 1800.0, "total_distance": 50000.0,
                    "num_active_samples": 10})
    return enc.close()


class FlagBitBaseTypeTests(unittest.TestCase):
    """A base-type byte's flag bits must be masked exactly as the decoder masks them.

    Regression cover for the defect that made ingestion impossible: the scanner
    validated the RAW base-type byte, so every file the pinned SDK's own encoder
    wrote -- which sets those flag bits -- was rejected with
    ``undefined_base_type`` while the pinned decoder read it back without
    complaint, and the rejection message blamed the pinned profile.
    """

    def test_the_mask_equals_the_pinned_decoders_own_mask(self):
        import garmin_fit_sdk.fit as fit

        self.assertEqual(C.BASE_TYPE_FLAG_MASK, int(fit.BASE_TYPE_MASK))

    def test_a_flag_bearing_base_type_is_accepted(self):
        """Every message-definition base-type byte in a real file carries flags.

        The fixture is the pinned encoder's own output. The check below walks that
        file's first message-definition record to find its base-type bytes, rather
        than scanning a fixed window for a byte pattern, and asserts that
        flag-bearing bytes are really present before asserting acceptance -- so
        the test cannot be vacuous.
        """
        data = _encoder_file_id_and_session()

        # Walk the first definition record: header(1) reserved(1) arch(1)
        # global_num(2) num_fields(1), then 3 bytes per field: num, size, type.
        record_start = data.index(b"\x40", 14)
        num_fields = data[record_start + 5]
        first_type = record_start + 6
        base_types = [data[first_type + 3 * i + 2] for i in range(num_fields)]
        flag_bearing = [b for b in base_types if b & 0x80]
        self.assertTrue(
            flag_bearing,
            f"fixture carries no flag-bearing base-type byte: {base_types!r}",
        )

        out = C.classify_bytes(data)
        self.assertTrue(out.accepted, out.reason_detail)
        self.assertNotEqual(out.reason_code, C.REASON_UNDEFINED_BASE_TYPE)

    def test_a_genuinely_undefined_type_is_still_rejected(self):
        # 0x7F masks to 0x1F, which the pinned profile does not define either.
        out = C.classify_bytes(_build_fit(undefined_base_type=True))
        self.assertFalse(out.accepted)
        self.assertEqual(out.reason_code, C.REASON_UNDEFINED_BASE_TYPE)
        self.assertIn("0x7F", out.reason_detail)
        self.assertIn("0x1F", out.reason_detail)

    def test_the_mask_equal_guard_fires_when_the_sdk_disagrees(self):
        """The guard's raise branch must be exercisable, or it is decoration.

        Deleting the three raise lines leaves every other test green, so without
        this one the guard could be silently removed.
        """
        import garmin_fit_sdk.fit as fit
        import unittest.mock as mock

        with mock.patch.object(fit, "BASE_TYPE_MASK", 0x7F):
            with self.assertRaises(C.PinnedProfileMismatch) as caught:
                C._load_pinned_profile()
        self.assertIn("BASE_TYPE_MASK", str(caught.exception))

    def test_a_missing_mask_constant_is_a_mismatch_not_a_pass(self):
        """A re-pin that drops the constant must not disable the guard."""
        import garmin_fit_sdk.fit as fit
        import unittest.mock as mock

        with mock.patch.object(fit, "BASE_TYPE_MASK", None):
            with self.assertRaises(C.PinnedProfileMismatch) as caught:
                C._load_pinned_profile()
        self.assertIn("absent from the pinned SDK", str(caught.exception))

    def test_a_mask_disagreement_is_reported_as_mismatch_not_absent(self):
        """Absence and disagreement are different facts and must stay different.

        The module carries a three-state machine for exactly this; a mask
        disagreement landing in "absent" would claim the SDK cannot be imported.
        """
        import garmin_fit_sdk.fit as fit
        import unittest.mock as mock

        with mock.patch.object(fit, "BASE_TYPE_MASK", 0x7F):
            with mock.patch.object(
                C, "_load_pinned_profile", wraps=C._load_pinned_profile
            ):
                state, profile, detail = C._load_pinned_state()
        self.assertEqual(state, "mismatch")
        self.assertIn("BASE_TYPE_MASK", detail)

    def test_a_file_written_by_the_pinned_encoder_is_accepted(self):
        """The round trip that should have existed and did not.

        No test called the pinned SDK's encoder, and no .fit fixture existed
        outside demo_file/, so the input class the SDK itself produces was never
        exercised.
        """
        from garmin_fit_sdk.decoder import Decoder
        from garmin_fit_sdk.stream import Stream

        data = _encoder_file_id_and_session()

        # The pinned decoder must agree it is a FIT file first, otherwise this
        # test would pass for the wrong reason.
        self.assertTrue(Decoder(Stream.from_byte_array(bytearray(data))).is_fit())

        out = C.classify_bytes(data)
        self.assertTrue(out.accepted, out.reason_detail)
        self.assertEqual(out.reason_code, C.REASON_ACCEPTED)
        self.assertEqual(out.sport_name, "running")
        self.assertEqual(out.sub_sport_name, "road")


if __name__ == "__main__":
    unittest.main(verbosity=2)
