"""Deterministic, model-free normalization: TK18, CUS03, SR05, SR06, oracle TC04.

TC04 *Preparation reproducibility*: "Run preprocessing twice with inference
blocked; normalized values match and no inference requests occur."

"Inference blocked" here is literal, not a claim. Every preparation in this
module runs inside :func:`network_disabled`, which replaces ``socket.socket``,
``socket.create_connection`` and ``urllib.request.urlopen`` with a function that
raises. A model call needs a socket, so a model call fails the test.

Fixture provenance
------------------

The fixtures are **synthetic and DATARA-authored**: a hand-written description of
a decoded activity shape, with expected values stated independently of the
normalizer. They are not derived from `demo_file/24563001348_ACTIVITY.fit`, which
is the founder's personal telemetry and is permanently out of scope, and they are
not copies or readings of upstream SDK sample binaries, whose redistribution
rights are unresolved (`docs/management/source-evidence/fixture-provenance.md`).
No FIT binary is committed, and `.gitignore` blocks `*.fit` in any case.

The policy constants below are **synthetic stand-ins**, not the TK10 mapping.
They exist so the shape of the policy is executable. `mapping_reference` names
them as such. No engineering value range and no FIT field mapping is invented
here; if a bound is not in the policy, the normalizer refuses to run.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from datara import CONTRACT_VERSION, NORMALIZER_VERSION
from datara.db import OwnerScopedStore
from datara.normalization import (
    OPTIONAL_PAYLOAD_KEYS,
    EligibilityRequirement,
    NormalizationPolicy,
    NormalizationRejection,
    RawActivityInput,
    VocabularyError,
    canonical_json,
    evaluate_eligibility,
    normalize,
    prepare_snapshot,
    sha256_digest,
)

# ---------------------------------------------------------------------------
# Synthetic, DATARA-authored fixture
# ---------------------------------------------------------------------------

#: Hand-stated expected values for :data:`SYNTHETIC_COMPLETE_RAW`, written
#: without consulting the normalizer. This is the "independent fixture values"
#: oracle of STK019.
SYNTHETIC_COMPLETE_EXPECTED: dict = {
    "required": {
        "source_digest": "sha256:" + "ab" * 32,
        "sport": "running",
        "session_start_utc": "2026-10-01T06:30:00Z",
        "elapsed_duration_seconds": "3600",
    },
    "optional": {
        "timer_duration_seconds": "3540",
        "distance_value": "500000",
        "distance_unit_code": "synthetic_distance_unit_a",
        "record_sample_count": "1800",
        "gps_point_count": "1800",
        "heart_rate_value": "150",
        "heart_rate_unit_code": "synthetic_rate_unit_b",
    },
    "quality_warnings": [],
}

#: A synthetic indoor-shaped activity: no GPS, no heart rate, no distance and no
#: timer duration. Accepted, every absent optional value null, every one of them
#: warned, nothing imputed.
SYNTHETIC_INDOOR_RAW = RawActivityInput(
    source_digest="sha256:" + "cd" * 32,
    sport="cycling",
    session_start_utc="2026-10-01T18:05:00Z",
    elapsed_duration_seconds=2700,
    record_sample_count=900,
    source_fields={
        "source_digest": "synthetic.file.digest",
        "sport": "synthetic.session.sport",
        "session_start_utc": "synthetic.session.start_time_utc",
        "elapsed_duration_seconds": "synthetic.session.elapsed_duration_seconds",
        "record_samples": "synthetic.records.count",
    },
)

#: Synthetic stand-in for the TK10 mapping. Not an approved engineering range.
SYNTHETIC_POLICY = NormalizationPolicy(
    policy_version="synthetic-test-policy-1",
    mapping_reference="TK10-PENDING-SYNTHETIC-STAND-IN",
    supported_sports=frozenset({"running", "cycling"}),
    max_elapsed_duration_seconds=24 * 3600,
    max_timer_duration_seconds=24 * 3600,
    max_distance_value=1_000_000,
    max_record_sample_count=200_000,
    max_gps_point_count=200_000,
    max_heart_rate_value=300,
)

SYNTHETIC_COMPLETE_RAW = RawActivityInput(
    source_digest="sha256:" + "ab" * 32,
    sport="running",
    session_start_utc="2026-10-01T06:30:00Z",
    elapsed_duration_seconds=3600,
    timer_duration_seconds=3540,
    distance_value=500_000,
    distance_unit_code="synthetic_distance_unit_a",
    record_sample_count=1800,
    gps_point_count=1800,
    heart_rate_value=150,
    heart_rate_unit_code="synthetic_rate_unit_b",
    source_fields={
        "source_digest": "synthetic.file.digest",
        "sport": "synthetic.session.sport",
        "session_start_utc": "synthetic.session.start_time_utc",
        "elapsed_duration_seconds": "synthetic.session.elapsed_duration_seconds",
        "timer_duration": "synthetic.session.timer_duration",
        "distance": "synthetic.session.distance",
        "record_samples": "synthetic.records.count",
        "gps": "synthetic.records.gps_points",
        "heart_rate": "synthetic.records.heart_rate",
    },
)


#: A single declared requirement, reused where one requirement is enough.
ONE_ACTIVITY_REQUIREMENT = (
    EligibilityRequirement(
        requirement_id="REQ-AT-LEAST-ONE-ACTIVITY",
        description="the scope contains at least one accepted activity",
        source_key="activity_count",
        comparator="at_least",
        required_value=1,
    ),
)


@contextmanager
def network_disabled():
    """Make any outbound connection an immediate, loud failure.

    This is the executable meaning of "model access disabled" (SR06). It is not
    a mock of the model layer; it removes the transport the model layer would
    need, so the property under test is that preparation never reaches for one.
    """

    def blocked(*args, **kwargs):
        raise AssertionError(
            "outbound connection attempted during a model-free operation"
        )

    with mock.patch("socket.socket", side_effect=blocked), mock.patch(
        "socket.create_connection", side_effect=blocked
    ), mock.patch("urllib.request.urlopen", side_effect=blocked):
        yield


def _payload(normalized) -> dict:
    return json.loads(normalized.canonical_payload)


class RepeatPreparationTests(TestCase):
    """TC04: the task's own verification case."""

    def test_two_preparations_are_byte_identical_and_share_a_digest(self) -> None:
        with network_disabled():
            first = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
            second = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
            scope_first = prepare_snapshot(
                normalized=[first],
                excluded=[],
                policy=SYNTHETIC_POLICY,
                scope_kind="synthetic_single_activity",
            )
            scope_second = prepare_snapshot(
                normalized=[second],
                excluded=[],
                policy=SYNTHETIC_POLICY,
                scope_kind="synthetic_single_activity",
            )

        self.assertEqual(first.canonical_payload, second.canonical_payload)
        self.assertEqual(first.normalization_digest, second.normalization_digest)
        self.assertEqual(scope_first.snapshot_digest, scope_second.snapshot_digest)
        self.assertEqual(
            scope_first.snapshot_digest,
            sha256_digest(scope_first.canonical_payload),
        )

    def test_independent_process_with_different_hash_seeds_agrees(self) -> None:
        """Determinism must not be an artifact of one interpreter's hash seed."""
        with network_disabled():
            local = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
            local_scope = prepare_snapshot(
                normalized=[local],
                excluded=[],
                policy=SYNTHETIC_POLICY,
                scope_kind="synthetic_single_activity",
            )

        child = (
            "import json, os\n"
            "from datara.normalization import (NormalizationPolicy, RawActivityInput,\n"
            "    normalize, prepare_snapshot)\n"
            "policy = NormalizationPolicy(**json.loads(os.environ['TK18_POLICY']))\n"
            "raw = RawActivityInput(**json.loads(os.environ['TK18_RAW']))\n"
            "n = normalize(raw, policy)\n"
            "s = prepare_snapshot(normalized=[n], excluded=[], policy=policy,\n"
            "    scope_kind='synthetic_single_activity')\n"
            "print(json.dumps({'activity': n.normalization_digest,\n"
            "    'snapshot': s.snapshot_digest}))\n"
        )
        repo_root = str(Path(__file__).resolve().parents[2])

        def run_in(seed: str) -> dict:
            env = dict(os.environ)
            env["PYTHONPATH"] = repo_root
            env["PYTHONHASHSEED"] = seed
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["TK18_POLICY"] = json.dumps(
                {
                    "policy_version": SYNTHETIC_POLICY.policy_version,
                    "mapping_reference": SYNTHETIC_POLICY.mapping_reference,
                    "supported_sports": sorted(SYNTHETIC_POLICY.supported_sports),
                    "max_elapsed_duration_seconds": SYNTHETIC_POLICY.max_elapsed_duration_seconds,
                    "max_timer_duration_seconds": SYNTHETIC_POLICY.max_timer_duration_seconds,
                    "max_distance_value": SYNTHETIC_POLICY.max_distance_value,
                    "max_record_sample_count": SYNTHETIC_POLICY.max_record_sample_count,
                    "max_gps_point_count": SYNTHETIC_POLICY.max_gps_point_count,
                    "max_heart_rate_value": SYNTHETIC_POLICY.max_heart_rate_value,
                }
            )
            env["TK18_RAW"] = json.dumps(
                {
                    "source_digest": SYNTHETIC_COMPLETE_RAW.source_digest,
                    "sport": SYNTHETIC_COMPLETE_RAW.sport,
                    "session_start_utc": SYNTHETIC_COMPLETE_RAW.session_start_utc,
                    "elapsed_duration_seconds": SYNTHETIC_COMPLETE_RAW.elapsed_duration_seconds,
                    "timer_duration_seconds": SYNTHETIC_COMPLETE_RAW.timer_duration_seconds,
                    "distance_value": SYNTHETIC_COMPLETE_RAW.distance_value,
                    "distance_unit_code": SYNTHETIC_COMPLETE_RAW.distance_unit_code,
                    "record_sample_count": SYNTHETIC_COMPLETE_RAW.record_sample_count,
                    "gps_point_count": SYNTHETIC_COMPLETE_RAW.gps_point_count,
                    "heart_rate_value": SYNTHETIC_COMPLETE_RAW.heart_rate_value,
                    "heart_rate_unit_code": SYNTHETIC_COMPLETE_RAW.heart_rate_unit_code,
                    "source_fields": dict(SYNTHETIC_COMPLETE_RAW.source_fields),
                }
            )
            completed = subprocess.run(
                [sys.executable, "-X", "utf8", "-c", child],
                capture_output=True,
                text=True,
                env=env,
                timeout=120,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            return json.loads(completed.stdout.strip().splitlines()[-1])

        seed_zero = run_in("0")
        seed_other = run_in("12345")
        self.assertEqual(seed_zero, seed_other)
        self.assertEqual(seed_zero["activity"], local.normalization_digest)
        self.assertEqual(seed_zero["snapshot"], local_scope.snapshot_digest)

    def test_canonical_form_is_stable_and_carries_no_owner_or_timestamp(self) -> None:
        with network_disabled():
            normalized = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
        text = normalized.canonical_payload
        self.assertNotIn(" ", text)
        self.assertEqual(text, canonical_json(json.loads(text)))
        self.assertEqual(
            list(json.loads(text).keys()),
            sorted(json.loads(text).keys()),
        )
        self.assertNotIn("owner", text)
        self.assertNotIn("created_at", text)

    def test_snapshot_digest_is_independent_of_input_order(self) -> None:
        with network_disabled():
            a = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
            b = normalize(SYNTHETIC_INDOOR_RAW, SYNTHETIC_POLICY)
            forward = prepare_snapshot(
                normalized=[a, b], excluded=[], policy=SYNTHETIC_POLICY, scope_kind="synthetic_pair"
            )
            reverse = prepare_snapshot(
                normalized=[b, a], excluded=[], policy=SYNTHETIC_POLICY, scope_kind="synthetic_pair"
            )
        self.assertEqual(forward.snapshot_digest, reverse.snapshot_digest)

    def test_two_persisted_snapshots_share_one_digest(self) -> None:
        user = get_user_model().objects.create_user(username="tk18-repeat-a", password="x")
        store = OwnerScopedStore.for_user(user)
        source = store.record_source_object(
            digest=SYNTHETIC_COMPLETE_RAW.source_digest,
            byte_length=1024,
            storage_reference="synthetic/owner-scoped/object-1",
            media_type="application/vnd.datara.synthetic",
        )
        import_record = store.record_import(
            source_digest=SYNTHETIC_COMPLETE_RAW.source_digest, status="accepted"
        )
        with network_disabled():
            first = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
            second = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
            preparation = prepare_snapshot(
                normalized=[first],
                excluded=[],
                policy=SYNTHETIC_POLICY,
                scope_kind="synthetic_single_activity",
            )
            repeated = prepare_snapshot(
                normalized=[second],
                excluded=[],
                policy=SYNTHETIC_POLICY,
                scope_kind="synthetic_single_activity",
            )
        activity = store.record_normalized_activity(
            source_object=source, import_record=import_record, normalized=first
        )
        snapshot = store.record_snapshot(preparation, [activity.activity_id])
        self.assertEqual(snapshot.snapshot_digest, sha256_digest(snapshot.canonical_payload))
        self.assertEqual(snapshot.snapshot_digest, repeated.snapshot_digest)
        self.assertEqual(snapshot.included_digests, [first.normalization_digest])
        self.assertEqual(
            store.get_snapshot(snapshot.snapshot_id).snapshot_digest, snapshot.snapshot_digest
        )


class IndependentExpectedValueTests(TestCase):
    """The hand-stated oracle: normalizer output must equal it exactly."""

    def test_complete_fixture_matches_hand_stated_expectation(self) -> None:
        with network_disabled():
            normalized = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
        payload = _payload(normalized)
        self.assertEqual(payload["required"], SYNTHETIC_COMPLETE_EXPECTED["required"])
        self.assertEqual(payload["optional"], SYNTHETIC_COMPLETE_EXPECTED["optional"])
        self.assertEqual(payload["quality_warnings"], SYNTHETIC_COMPLETE_EXPECTED["quality_warnings"])
        self.assertEqual(payload["contract_version"], CONTRACT_VERSION)
        self.assertEqual(payload["normalizer_version"], NORMALIZER_VERSION)
        self.assertEqual(normalized.optional_keys, SYNTHETIC_COMPLETE_EXPECTED["optional"])


class RequiredFieldTests(TestCase):
    """A missing or invalid required field rejects the whole file."""

    def _reject(self, raw: RawActivityInput) -> NormalizationRejection:
        with self.assertRaises(NormalizationRejection) as caught:
            with network_disabled():
                normalize(raw, SYNTHETIC_POLICY)
        return caught.exception

    def test_each_required_field_absent_yields_its_stable_reason_code(self) -> None:
        cases = {
            "source_digest": RawActivityInput(
                sport="running", session_start_utc="2026-10-01T06:30:00Z", elapsed_duration_seconds=1
            ),
            "sport": RawActivityInput(
                source_digest="sha256:" + "ab" * 32,
                session_start_utc="2026-10-01T06:30:00Z",
                elapsed_duration_seconds=1,
            ),
            "session_start_utc": RawActivityInput(
                source_digest="sha256:" + "ab" * 32, sport="running", elapsed_duration_seconds=1
            ),
            "elapsed_duration_seconds": RawActivityInput(
                source_digest="sha256:" + "ab" * 32,
                sport="running",
                session_start_utc="2026-10-01T06:30:00Z",
            ),
        }
        expected_codes = {
            "source_digest": "REQ_SOURCE_DIGEST_MISSING",
            "sport": "REQ_SPORT_MISSING",
            "session_start_utc": "REQ_SESSION_START_MISSING",
            "elapsed_duration_seconds": "REQ_ELAPSED_DURATION_MISSING",
        }
        for field, raw in cases.items():
            rejection = self._reject(raw)
            self.assertEqual(rejection.reason_code, expected_codes[field], field)
            self.assertEqual(rejection.field, field)
            self.assertTrue(rejection.reason_detail)

    def test_the_same_input_rejects_with_the_same_code_every_time(self) -> None:
        raw = RawActivityInput(
            source_digest="sha256:" + "ab" * 32, sport="running", session_start_utc="2026-10-01T06:30:00Z"
        )
        codes = {(r.reason_code, r.reason_detail) for r in (self._reject(raw), self._reject(raw))}
        self.assertEqual(codes, {("REQ_ELAPSED_DURATION_MISSING", "absent")})

    def test_malformed_digest_is_refused(self) -> None:
        for digest in ("md5:abc", "sha256:NOTHEX", "sha256:" + "AB" * 32, "abcd"):
            rejection = self._reject(
                RawActivityInput(
                    source_digest=digest,
                    sport="running",
                    session_start_utc="2026-10-01T06:30:00Z",
                    elapsed_duration_seconds=60,
                )
            )
            self.assertEqual(rejection.reason_code, "REQ_SOURCE_DIGEST_MALFORMED")

    def test_invalid_elapsed_values_are_refused(self) -> None:
        for value, detail in ((0, "zero"), (-1, "negative"), (True, "boolean_value"), (1.5, "not_an_integer")):
            rejection = self._reject(
                RawActivityInput(
                    source_digest="sha256:" + "ab" * 32,
                    sport="running",
                    session_start_utc="2026-10-01T06:30:00Z",
                    elapsed_duration_seconds=value,
                )
            )
            self.assertEqual(rejection.reason_code, "REQ_ELAPSED_DURATION_INVALID")
            self.assertEqual(rejection.reason_detail, detail)

    def test_elapsed_above_the_policy_maximum_is_refused(self) -> None:
        rejection = self._reject(
            RawActivityInput(
                source_digest="sha256:" + "ab" * 32,
                sport="running",
                session_start_utc="2026-10-01T06:30:00Z",
                elapsed_duration_seconds=SYNTHETIC_POLICY.max_elapsed_duration_seconds + 1,
            )
        )
        self.assertEqual(rejection.reason_code, "REQ_ELAPSED_DURATION_OUT_OF_RANGE")
        self.assertEqual(rejection.reason_detail, "above_policy_maximum")

    def test_unsupported_sport_is_refused_with_its_own_code(self) -> None:
        rejection = self._reject(
            RawActivityInput(
                source_digest="sha256:" + "ab" * 32,
                sport="multisport",
                session_start_utc="2026-10-01T06:30:00Z",
                elapsed_duration_seconds=60,
            )
        )
        self.assertEqual(rejection.reason_code, "REQ_SPORT_UNSUPPORTED")
        self.assertEqual(rejection.reason_detail, "not_in_policy_supported_sports")

    def test_naive_start_instant_is_refused_rather_than_assumed_utc(self) -> None:
        for value in ("2026-10-01T06:30:00", "not-a-time", 12345):
            rejection = self._reject(
                RawActivityInput(
                    source_digest="sha256:" + "ab" * 32,
                    sport="running",
                    session_start_utc=value,
                    elapsed_duration_seconds=60,
                )
            )
            self.assertEqual(rejection.reason_code, "REQ_SESSION_START_INVALID")

    def test_offset_start_instant_is_converted_exactly_not_guessed(self) -> None:
        with network_disabled():
            utc = normalize(
                RawActivityInput(
                    source_digest="sha256:" + "ab" * 32,
                    sport="running",
                    session_start_utc="2026-10-01T06:30:00Z",
                    elapsed_duration_seconds=3600,
                ),
                SYNTHETIC_POLICY,
            )
            offset = normalize(
                RawActivityInput(
                    source_digest="sha256:" + "ab" * 32,
                    sport="running",
                    session_start_utc="2026-10-01T08:30:00+02:00",
                    elapsed_duration_seconds=3600,
                ),
                SYNTHETIC_POLICY,
            )
        self.assertEqual(utc.session_start_utc, "2026-10-01T06:30:00Z")
        self.assertEqual(utc.session_start_utc, offset.session_start_utc)
        self.assertEqual(utc.normalization_digest, offset.normalization_digest)

    def test_reason_vocabulary_cannot_be_extended_by_free_text(self) -> None:
        with self.assertRaises(VocabularyError):
            NormalizationRejection("REQ_SPORT_MISSING", "because the coach said so")
        with self.assertRaises(VocabularyError):
            NormalizationRejection("REQ_MADE_UP_CODE", "absent")


class OptionalFieldTests(TestCase):
    """No imputation, ever; elapsed and timer never interchanged."""

    def test_indoor_activity_with_no_gps_is_accepted(self) -> None:
        with network_disabled():
            normalized = normalize(SYNTHETIC_INDOOR_RAW, SYNTHETIC_POLICY)
        self.assertIsNone(normalized.gps_point_count)
        gps_warnings = [w for w in normalized.quality_warnings if w.field == "gps"]
        self.assertEqual(len(gps_warnings), 1)
        self.assertEqual((gps_warnings[0].code, gps_warnings[0].detail), ("OPT_ABSENT", "absent"))
        self.assertEqual(_payload(normalized)["optional"]["gps_point_count"], None)

    def test_every_absent_optional_is_null_and_warned_and_nothing_is_imputed(self) -> None:
        with network_disabled():
            normalized = normalize(SYNTHETIC_INDOOR_RAW, SYNTHETIC_POLICY)
            complete = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
        payload = _payload(normalized)
        warned = {w.field for w in normalized.quality_warnings}
        # The invariant: a logical optional field is null exactly when it is warned.
        for logical, keys in OPTIONAL_PAYLOAD_KEYS.items():
            all_null = all(payload["optional"][key] is None for key in keys)
            self.assertEqual(all_null, logical in warned, logical)
        # This fixture supplies record samples, so only the other four are absent.
        self.assertEqual(
            warned, {"distance", "gps", "heart_rate", "timer_duration"}
        )
        self.assertEqual(payload["optional"]["record_sample_count"], "900")
        for logical in warned:
            self.assertNotIn(logical, {w.field for w in complete.quality_warnings})
        # Nothing carried over from the fully populated activity.
        for key, value in normalized.optional_keys.items():
            if value is not None:
                self.assertNotEqual(value, complete.optional_keys[key])
        self.assertEqual(
            [(w.field, w.code) for w in normalized.quality_warnings],
            [
                ("distance", "OPT_ABSENT"),
                ("gps", "OPT_ABSENT"),
                ("heart_rate", "OPT_ABSENT"),
                ("timer_duration", "OPT_ABSENT"),
            ],
        )

    def test_a_null_optional_value_always_has_a_warning_and_only_then(self) -> None:
        with network_disabled():
            normalized = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
        payload = _payload(normalized)
        warned = {w.field for w in normalized.quality_warnings}
        for logical, keys in OPTIONAL_PAYLOAD_KEYS.items():
            all_null = all(payload["optional"][key] is None for key in keys)
            self.assertEqual(all_null, logical in warned, logical)

    def test_invalid_optional_value_becomes_null_plus_a_warning(self) -> None:
        with network_disabled():
            normalized = normalize(
                RawActivityInput(
                    source_digest="sha256:" + "ab" * 32,
                    sport="running",
                    session_start_utc="2026-10-01T06:30:00Z",
                    elapsed_duration_seconds=3600,
                    gps_point_count="not-a-number",
                    record_sample_count=SYNTHETIC_POLICY.max_record_sample_count + 1,
                    heart_rate_value=150,
                ),
                SYNTHETIC_POLICY,
            )
        self.assertIsNone(normalized.gps_point_count)
        self.assertIsNone(normalized.record_sample_count)
        # No unit code was declared, so the heart rate cannot be used: assuming a
        # unit would be inventing a mapping (TK10).
        self.assertIsNone(normalized.heart_rate_value)
        self.assertIsNone(normalized.heart_rate_unit_code)
        self.assertEqual(
            [(w.field, w.code, w.detail) for w in normalized.quality_warnings],
            [
                ("distance", "OPT_ABSENT", "absent"),
                ("gps", "OPT_INVALID", "not_an_integer"),
                ("heart_rate", "OPT_UNIT_CODE_ABSENT", "unit_code_absent_for_supplied_value"),
                ("record_samples", "OPT_OUT_OF_RANGE", "above_policy_maximum"),
                ("timer_duration", "OPT_ABSENT", "absent"),
            ],
        )
        self.assertEqual(normalized.elapsed_duration_seconds, 3600)

    def test_zero_gps_point_count_is_treated_as_absent_not_as_data(self) -> None:
        with network_disabled():
            normalized = normalize(
                RawActivityInput(
                    source_digest="sha256:" + "ab" * 32,
                    sport="running",
                    session_start_utc="2026-10-01T06:30:00Z",
                    elapsed_duration_seconds=3600,
                    timer_duration_seconds=3540,
                    distance_value=500_000,
                    distance_unit_code="synthetic_distance_unit_a",
                    record_sample_count=1800,
                    gps_point_count=0,
                    heart_rate_value=150,
                    heart_rate_unit_code="synthetic_rate_unit_b",
                ),
                SYNTHETIC_POLICY,
            )
        self.assertIsNone(normalized.gps_point_count)
        self.assertEqual(
            [(w.field, w.code, w.detail) for w in normalized.quality_warnings],
            [("gps", "OPT_ABSENT", "zero_or_negative_point_count_reported")],
        )
        self.assertEqual(normalized.record_sample_count, 1800)

    def test_timer_duration_is_retained_separately_and_never_copies_elapsed(self) -> None:
        with network_disabled():
            differing = normalize(
                RawActivityInput(
                    source_digest="sha256:" + "ab" * 32,
                    sport="running",
                    session_start_utc="2026-10-01T06:30:00Z",
                    elapsed_duration_seconds=3600,
                    timer_duration_seconds=3540,
                ),
                SYNTHETIC_POLICY,
            )
        self.assertEqual(differing.elapsed_duration_seconds, 3600)
        self.assertEqual(differing.timer_duration_seconds, 3540)
        payload = _payload(differing)
        self.assertEqual(payload["required"]["elapsed_duration_seconds"], "3600")
        self.assertEqual(payload["optional"]["timer_duration_seconds"], "3540")
        self.assertNotIn("timer", payload["required"])

    def test_missing_elapsed_is_never_filled_from_the_timer(self) -> None:
        with self.assertRaises(NormalizationRejection) as caught:
            with network_disabled():
                normalize(
                    RawActivityInput(
                        source_digest="sha256:" + "ab" * 32,
                        sport="running",
                        session_start_utc="2026-10-01T06:30:00Z",
                        elapsed_duration_seconds=None,
                        timer_duration_seconds=3540,
                    ),
                    SYNTHETIC_POLICY,
                )
        self.assertEqual(caught.exception.reason_code, "REQ_ELAPSED_DURATION_MISSING")
        self.assertEqual(
            caught.exception.reason_detail, "absent_while_timer_present_not_substituted"
        )


class EligibilityTests(TestCase):
    """CUS05 / SR10-SR11: deterministic, explanatory, and model-free."""

    REQUIREMENTS = (
        EligibilityRequirement(
            requirement_id="REQ-AT-LEAST-ONE-ACTIVITY",
            description="the scope contains at least one accepted activity",
            source_key="activity_count",
            comparator="at_least",
            required_value=1,
        ),
        EligibilityRequirement(
            requirement_id="REQ-COVERAGE-DAYS",
            description="the scope covers at least the declared number of complete UTC days",
            source_key="covered_days",
            comparator="at_least",
            required_value=28,
        ),
    )

    def test_ineligible_scope_explains_every_unmet_requirement_and_calls_nothing(self) -> None:
        observations = {"activity_count": 0, "covered_days": 14}
        with network_disabled():
            decision = evaluate_eligibility(
                observations=observations,
                requirements=self.REQUIREMENTS,
                rule_set_version="synthetic-rule-set-1",
            )
        self.assertFalse(decision.eligible)
        self.assertEqual(
            [item["requirement_id"] for item in decision.unmet_requirements],
            ["REQ-AT-LEAST-ONE-ACTIVITY", "REQ-COVERAGE-DAYS"],
        )
        by_id = {item["requirement_id"]: item for item in decision.unmet_requirements}
        self.assertEqual(by_id["REQ-AT-LEAST-ONE-ACTIVITY"]["observed_value"], 0)
        self.assertEqual(by_id["REQ-COVERAGE-DAYS"]["observed_value"], 14)
        for item in decision.unmet_requirements:
            self.assertTrue(item["description"])
            self.assertEqual(
                set(item),
                {
                    "requirement_id",
                    "description",
                    "source_key",
                    "comparator",
                    "required_value",
                    "observed_value",
                },
            )
        self.assertEqual(decision.rule_version, "tk18-eligibility/1")

    def test_eligible_scope_is_a_boolean_and_stays_pure(self) -> None:
        observations = {"activity_count": 3, "covered_days": 28}
        with network_disabled():
            first = evaluate_eligibility(
                observations=observations,
                requirements=self.REQUIREMENTS,
                rule_set_version="synthetic-rule-set-1",
            )
            second = evaluate_eligibility(
                observations=observations,
                requirements=self.REQUIREMENTS,
                rule_set_version="synthetic-rule-set-1",
            )
        self.assertTrue(first.eligible)
        self.assertEqual(first.unmet_requirements, ())
        self.assertEqual(first, second)

    def test_unmet_requirements_are_explained_in_a_stable_order(self) -> None:
        shuffled = tuple(reversed(self.REQUIREMENTS))
        with network_disabled():
            first = evaluate_eligibility(
                observations={"activity_count": 0, "covered_days": 0},
                requirements=self.REQUIREMENTS,
                rule_set_version="synthetic-rule-set-1",
            )
            second = evaluate_eligibility(
                observations={"activity_count": 0, "covered_days": 0},
                requirements=shuffled,
                rule_set_version="synthetic-rule-set-1",
            )
        self.assertEqual(first.unmet_requirements, second.unmet_requirements)

    def test_decision_can_be_retained_and_still_names_no_skill_or_model(self) -> None:
        user = get_user_model().objects.create_user(username="tk18-elig", password="x")
        store = OwnerScopedStore.for_user(user)
        source = store.record_source_object(
            digest="sha256:" + "ab" * 32,
            byte_length=8,
            storage_reference="synthetic/owner-scoped/object-2",
            media_type="application/vnd.datara.synthetic",
        )
        import_record = store.record_import(source_digest="sha256:" + "ab" * 32, status="accepted")
        with network_disabled():
            normalized = normalize(SYNTHETIC_COMPLETE_RAW, SYNTHETIC_POLICY)
            preparation = prepare_snapshot(
                normalized=[normalized], excluded=[], policy=SYNTHETIC_POLICY, scope_kind="synthetic_single_activity"
            )
            decision = evaluate_eligibility(
                observations={"activity_count": 0},
                requirements=(self.REQUIREMENTS[0],),
                rule_set_version="synthetic-rule-set-1",
            )
        activity = store.record_normalized_activity(
            source_object=source, import_record=import_record, normalized=normalized
        )
        snapshot = store.record_snapshot(preparation, [activity.activity_id])
        record = store.record_eligibility(snapshot, decision)
        self.assertFalse(record.eligible)
        text = json.dumps(record.unmet_requirements).lower()
        for forbidden in ("skill", "model", "provider", "prompt", "connection"):
            self.assertNotIn(forbidden, text)


class ModelFreeTests(TestCase):
    """SR06, made checkable rather than asserted."""

    FORBIDDEN_IMPORT_ROOTS = {
        "anthropic",
        "certifi",
        "cohere",
        "genai",
        "google",
        "http",
        "httplib",
        "httpcore",
        "httpx",
        "litellm",
        "mistralai",
        "openai",
        "requests",
        "socket",
        "socketserver",
        "ssl",
        "transformers",
        "urllib",
        "urllib3",
        "websockets",
    }

    def test_no_package_module_imports_a_transport_or_model_sdk(self) -> None:
        package_dir = Path(__file__).resolve().parents[1]
        checked = 0
        for path in sorted(package_dir.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                roots: list[str] = []
                if isinstance(node, ast.Import):
                    roots = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    roots = [node.module.split(".")[0]]
                for root in roots:
                    self.assertNotIn(
                        root,
                        self.FORBIDDEN_IMPORT_ROOTS,
                        f"{path.name} imports {root}",
                    )
            checked += 1
        self.assertGreaterEqual(checked, 5)

    def test_normalization_succeeds_with_sockets_disabled(self) -> None:
        with network_disabled():
            normalized = normalize(SYNTHETIC_INDOOR_RAW, SYNTHETIC_POLICY)
            scope = prepare_snapshot(
                normalized=[normalized], excluded=[], policy=SYNTHETIC_POLICY, scope_kind="synthetic_indoor"
            )
            decision = evaluate_eligibility(
                observations={"activity_count": 1},
                requirements=ONE_ACTIVITY_REQUIREMENT,
                rule_set_version="synthetic-rule-set-1",
            )
        self.assertTrue(decision.eligible)
        self.assertTrue(scope.snapshot_digest.startswith("sha256:"))
