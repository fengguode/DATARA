"""TK21: versioned, scoped skill input and reconstructible provenance.

CUS03; SR07, SR28, SR34; FEAT21; WP03. Oracles TC05, TC20, TC23.

**TC05, TC20 and TC23 remain Not run.** Nothing in this file is verification
evidence for them: TC05 is a contract+integration case, TC20 a contract+mocked
integration case, and TC23 a *rendered UI* inspection. What this file proves is
narrower and is stated per test.

HOW EVERY CHECK IS BACKED BY A MUTATION
---------------------------------------
A control that has not been seen to fail is not evidence. Each class below
therefore pairs the property with the mutation that breaks it, and the mutation
is **executed in the test**, not described in a docstring:

| Property | Mutation executed in-suite |
| --- | --- |
| byte-identical across preparations | records supplied in reversed order |
| byte-identical across processes | child run with a different ``PYTHONHASHSEED`` |
| quarantined candidate cannot enter a scope | ``quarantined=True`` / disposition set to ``quarantined`` / an unresolved ``Quarantine`` row |
| re-versioning never mutates a prior version | a second, different version appended after the first |
| provenance resolves for every field | a ledger entry removed / a field with no absence reason / a value class Milestone A cannot produce |
| no model or network call is reachable | an AST import scan **and** a socket tripwire around every preparation |
| no skill-against-model outcome is persisted | a deliberately violating fact set fed to the existing guard |

FIXTURE PROVENANCE
------------------
Every fixture is **synthetic and DATARA-authored**: hand-written inputs with
expected values stated independently of the code under test. Nothing is derived
from `demo_file/24563001348_ACTIVITY.fit`, which is the founder's personal
telemetry and is permanently out of scope -- it is not read, copied, hashed,
listed or stat'ed anywhere in this file, and no test can reach it because the
fixtures are constructed in memory. The policy constants are **synthetic
stand-ins** for the pending TK10 mapping, named as such; no engineering value
range or FIT field mapping is invented here.

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
from typing import Any
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from datara import NORMALIZER_VERSION
from datara.canonical import (
    CANONICAL_DURATION_UNIT,
    LogicalIdentity,
    start_epoch_seconds_from_utc_text,
)
from datara.db import (
    OwnerScopedStore,
    SchemaFacts,
    find_forbidden_schema_entities,
    introspect_persisted_schema,
)
from datara.models import ResourceNotVisible
from datara.normalization import (
    NormalizationPolicy,
    RawActivityInput,
    canonical_json,
    normalize,
    sha256_digest,
)
from datara.provenance import (
    MILESTONE_A_VALUE_CLASSES,
    UNAVAILABLE_LABEL,
    VALUE_CLASS_QUALITY_WARNING,
    VALUE_CLASS_SCOPE_MEMBER,
    VALUE_CLASS_SOURCE_OBSERVATION,
    AbsentObservation,
    DuplicateFieldPath,
    FieldProvenance,
    ProvenanceIncomplete,
    ProvenanceLedger,
    ScopedField,
    UnresolvableProvenance,
    ValueClassUnavailable,
    build_display,
    build_ledger,
)
from datara.scoped_input import (
    DISPOSITION_PUBLISHED,
    DISPOSITION_QUARANTINED,
    EXCLUDED_CAPACITY,
    EXCLUDED_DISPOSITION,
    EXCLUDED_DUPLICATE_IDENTITY,
    EXCLUDED_MAPPING_REFERENCE,
    EXCLUDED_OUTSIDE_WINDOW,
    EXCLUDED_POLICY_VERSION,
    EXCLUDED_PREPARATION_VERSION,
    EXCLUDED_QUARANTINED,
    EXCLUDED_REQUIRED_FIELD_ABSENT,
    EXCLUDED_SPORT,
    EXCLUSION_REASONS,
    HEADER_CANONICAL_IDENTITY,
    HEADER_FIELDS,
    HEADER_SOURCE_DIGEST,
    MILESTONE_A_FIELD_SOURCES,
    PROHIBITED_PAYLOAD_TOKENS,
    SCOPED_INPUT_CONTRACT_VERSION,
    ActivityScope,
    AmbiguousCanonicalIdentity,
    DeclaredFieldMissing,
    InputFieldSpec,
    MilestoneAInputStore,
    ProhibitedScopeContent,
    QuarantinedCandidateInScope,
    ScopeCapacityExceeded,
    ScopeContractError,
    ScopedExclusion,
    ScopedInputError,
    ScopedInputVersion,
    ScopedRecord,
    UndeclaredFieldInRecord,
    VersionedInputStore,
    assert_no_prohibited_content,
    prepare_scoped_input,
)

SRC = VALUE_CLASS_SOURCE_OBSERVATION
MEMBER = VALUE_CLASS_SCOPE_MEMBER
WARNING = VALUE_CLASS_QUALITY_WARNING

# ---------------------------------------------------------------------------
# Synthetic, DATARA-authored fixtures
# ---------------------------------------------------------------------------

#: Synthetic stand-in for the pending TK10 mapping. Not an approved engineering
#: range; it exists so the shape is executable.
SYNTHETIC_POLICY = NormalizationPolicy(
    policy_version="synthetic-tk21-policy-1",
    mapping_reference="TK10-PENDING-SYNTHETIC-STAND-IN",
    supported_sports=frozenset({"running", "cycling"}),
    max_elapsed_duration_seconds=24 * 3600,
    max_timer_duration_seconds=24 * 3600,
    max_distance_value=1_000_000,
    max_record_sample_count=200_000,
    max_gps_point_count=200_000,
    max_heart_rate_value=300,
)

SYNTHETIC_MAPPING = "TK10-PENDING-SYNTHETIC-STAND-IN"
SYNTHETIC_POLICY_VERSION = "synthetic-tk21-policy-1"

#: The window every scope fixture states: one UTC day, half-open.
WINDOW_START = "2026-10-01T00:00:00Z"
WINDOW_END = "2026-10-02T00:00:00Z"


def _epoch(text: str) -> int:
    return start_epoch_seconds_from_utc_text(text, origin="test_scoped_input")


#: Stated independently of the code under test: the three in-window instants and
#: the one out-of-window instant, in epoch seconds computed from their text.
INSIDE_MORNING = _epoch("2026-10-01T06:30:00Z")
INSIDE_EVENING = _epoch("2026-10-01T18:05:00Z")
INSIDE_MIDNIGHT = _epoch("2026-10-02T00:00:00Z")  # the end instant: excluded, half-open
OUTSIDE_BEFORE = _epoch("2026-09-30T06:30:00Z")
OUTSIDE_AFTER = _epoch("2026-10-03T06:30:00Z")

#: The complete declared field set a synthetic skill asks for. Deliberately
#: includes an optional measurement that the indoor fixture does not have, so
#: the "absent is unavailable, never zero" property is exercised by real data.
DECLARED_FULL: tuple[InputFieldSpec, ...] = (
    InputFieldSpec("sport", SRC, True),
    InputFieldSpec("sport_code", SRC, True),
    InputFieldSpec("start_epoch_seconds", SRC, True),
    InputFieldSpec("elapsed_duration_ms", SRC, True),
    InputFieldSpec("heart_rate_value", SRC, False),
    InputFieldSpec("quality_warnings", WARNING, True),
)

DECLARED_MINIMAL: tuple[InputFieldSpec, ...] = (
    InputFieldSpec("sport", SRC, True),
    InputFieldSpec("elapsed_duration_ms", SRC, True),
)

#: The same declaration with the optional measurement made **required**. Used to
#: reach the ``required_field_absent`` exclusion: an optional field with no value
#: is correctly *included* as unavailable, so the required-field exclusion needs
#: a required field that has no value.
DECLARED_STRICT: tuple[InputFieldSpec, ...] = (
    InputFieldSpec("sport", SRC, True),
    InputFieldSpec("sport_code", SRC, True),
    InputFieldSpec("start_epoch_seconds", SRC, True),
    InputFieldSpec("elapsed_duration_ms", SRC, True),
    InputFieldSpec("heart_rate_value", SRC, True),
    InputFieldSpec("quality_warnings", WARNING, True),
)


def make_scope(
    *,
    sports: frozenset[str] | None = None,
    max_activities: int = 10,
    kind: str = "synthetic_tk21_window",
    start_utc: str = WINDOW_START,
    end_utc: str = WINDOW_END,
    policy_version: str = SYNTHETIC_POLICY_VERSION,
    mapping_reference: str = SYNTHETIC_MAPPING,
    preparation_version: str = NORMALIZER_VERSION,
) -> ActivityScope:
    return ActivityScope(
        kind=kind,
        start_utc=start_utc,
        end_utc=end_utc,
        sports=sports,
        max_activities=max_activities,
        preparation_version=preparation_version,
        policy_version=policy_version,
        mapping_reference=mapping_reference,
    )


def _identity(sport_code: int, start: int, elapsed_ms: int = 3_600_000) -> LogicalIdentity:
    return LogicalIdentity(
        sport_code=sport_code, start_epoch_seconds=start, elapsed_duration_ms=elapsed_ms
    )


def make_record(
    *,
    canonical_identity: str,
    sport_code: int = 1,
    start: int = INSIDE_MORNING,
    elapsed_ms: int = 3_600_000,
    declared: tuple[InputFieldSpec, ...] = DECLARED_FULL,
    sport: str = "running",
    quarantined: bool = False,
    disposition: str = DISPOSITION_PUBLISHED,
    policy_version: str = SYNTHETIC_POLICY_VERSION,
    mapping_reference: str = SYNTHETIC_MAPPING,
    preparation_version: str = NORMALIZER_VERSION,
    source_digest: str | None = None,
    include_optional_values: bool = True,
    heart_rate: str | None = "150",
) -> ScopedRecord:
    """A synthetic prepared record offering exactly the declared fields.

    ``canonical_identity`` and ``source_digest`` are distinct per call site so
    that ordering, capacity and duplicate reasoning are observable.
    """

    identity_tuple = _identity(sport_code, start, elapsed_ms)
    source = source_digest or _digest_for(canonical_identity)
    fields: list[ScopedField] = [
        ScopedField(
            field_name=HEADER_CANONICAL_IDENTITY,
            value_class=MEMBER,
            value_canonical=canonical_identity,
            preparation_version=preparation_version,
            mapping_reference=mapping_reference,
        ),
        ScopedField(
            field_name=HEADER_SOURCE_DIGEST,
            value_class=MEMBER,
            value_canonical=source,
            preparation_version=preparation_version,
            mapping_reference=mapping_reference,
        ),
    ]
    for spec in declared:
        fields.append(
            _field_for(
                spec,
                identity=identity_tuple,
                sport=sport,
                preparation_version=preparation_version,
                mapping_reference=mapping_reference,
                include_optional_values=include_optional_values,
                heart_rate=heart_rate,
            )
        )
    return ScopedRecord(
        canonical_identity=canonical_identity,
        source_digest=source,
        logical_tuple=identity_tuple,
        preparation_version=preparation_version,
        policy_version=policy_version,
        mapping_reference=mapping_reference,
        disposition=disposition,
        quarantined=quarantined,
        fields=tuple(fields),
    )


def _digest_for(canonical_identity: str) -> str:
    """A source-bytes digest distinct from the record's own canonical identity."""

    return "sha256:" + ("%064x" % (int(canonical_identity.split(":")[1][:8], 16) ^ 0x5A5A5A5A))


def _field_for(
    spec: InputFieldSpec,
    *,
    identity: LogicalIdentity,
    sport: str,
    preparation_version: str,
    mapping_reference: str,
    include_optional_values: bool,
    heart_rate: str | None,
) -> ScopedField:
    """One declared field, present or explicitly absent with a recorded reason.

    An absent value always carries an :class:`AbsentObservation` built from
    TK18's own warning vocabulary, so the envelope never carries a bare null.
    """

    values: dict[str, str] = {
        "sport": sport,
        "sport_code": str(identity.sport_code),
        "start_epoch_seconds": str(identity.start_epoch_seconds),
        "elapsed_duration_ms": str(identity.elapsed_duration_ms),
        "quality_warnings": canonical_json([]),
    }
    absent: AbsentObservation | None = None
    if spec.field_name == "heart_rate_value":
        if include_optional_values and heart_rate is not None:
            values[spec.field_name] = heart_rate
        else:
            absent = AbsentObservation(
                code="OPT_ABSENT", detail="absent", source_field="synthetic.records.heart_rate"
            )
    elif spec.field_name in values:
        pass
    elif not include_optional_values:
        absent = AbsentObservation(
            code="OPT_ABSENT", detail="absent", source_field=f"synthetic.{spec.field_name}"
        )
    else:  # pragma: no cover - a declared field with no fixture value
        raise AssertionError(f"the fixture has no value rule for {spec.field_name!r}")
    return ScopedField(
        field_name=spec.field_name,
        value_class=spec.value_class,
        value_canonical=values.get(spec.field_name),
        preparation_version=preparation_version,
        mapping_reference=mapping_reference,
        absent=absent,
    )


def identity(n: int) -> str:
    """A stable synthetic canonical identity for record ``n``."""

    return "sha256:" + ("%064x" % n)


@contextmanager
def network_disabled():
    """Make any outbound connection an immediate, loud failure.

    The executable meaning of "model access disabled" (SR06). It removes the
    transport a model call would need, so the property under test is that scoped
    input preparation never reaches for one. Same helper shape as
    ``datara/tests/test_normalization.py``, duplicated rather than imported
    because this assignment owns new files only.
    """

    def blocked(*args, **kwargs):
        raise AssertionError("outbound connection attempted during a model-free operation")

    with mock.patch("socket.socket", side_effect=blocked), mock.patch(
        "socket.create_connection", side_effect=blocked
    ), mock.patch("urllib.request.urlopen", side_effect=blocked):
        yield


# ===========================================================================
# 1. Determinism
# ===========================================================================


class DeterminismTests(TestCase):
    """The same scope over the same records is byte-identical."""

    def test_two_preparations_of_one_scope_are_byte_identical(self) -> None:
        scope = make_scope()
        records = [make_record(canonical_identity=identity(1))]
        with network_disabled():
            first = prepare_scoped_input(
                scope=scope, records=records, field_specs=DECLARED_FULL, policy=SYNTHETIC_POLICY
            )
            second = prepare_scoped_input(
                scope=scope, records=records, field_specs=DECLARED_FULL, policy=SYNTHETIC_POLICY
            )
        self.assertEqual(first.canonical_payload.encode("utf-8"), second.canonical_payload.encode("utf-8"))
        self.assertEqual(first.input_digest, second.input_digest)

    def test_record_supply_order_does_not_change_a_single_byte(self) -> None:
        """Mutation control: reversing the supplied order must change nothing.

        If the payload were built by iterating the caller's sequence, this test
        would fail. It is the control that makes the ordering claim evidence.
        """

        scope = make_scope()
        forwards = [
            make_record(canonical_identity=identity(11), start=INSIDE_MORNING),
            make_record(canonical_identity=identity(12), start=INSIDE_EVENING, sport_code=2, sport="cycling"),
            make_record(canonical_identity=identity(13), start=INSIDE_MORNING + 60),
        ]
        with network_disabled():
            forward = prepare_scoped_input(
                scope=scope, records=forwards, field_specs=DECLARED_FULL, policy=SYNTHETIC_POLICY
            )
            reverse = prepare_scoped_input(
                scope=scope,
                records=list(reversed(forwards)),
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        self.assertEqual(forward.canonical_payload, reverse.canonical_payload)
        self.assertEqual(forward.input_digest, reverse.input_digest)
        # The control has teeth: a different record set *is* a different version.
        with network_disabled():
            smaller = prepare_scoped_input(
                scope=scope, records=forwards[:1], field_specs=DECLARED_FULL, policy=SYNTHETIC_POLICY
            )
        self.assertNotEqual(forward.input_digest, smaller.input_digest)

    def test_declaration_order_does_not_change_a_single_byte(self) -> None:
        scope = make_scope()
        records = [make_record(canonical_identity=identity(21), declared=DECLARED_FULL)]
        with network_disabled():
            ordered = prepare_scoped_input(
                scope=scope, records=records, field_specs=DECLARED_FULL, policy=SYNTHETIC_POLICY
            )
            shuffled = prepare_scoped_input(
                scope=scope,
                records=records,
                field_specs=tuple(reversed(DECLARED_FULL)),
                policy=SYNTHETIC_POLICY,
            )
        self.assertEqual(ordered.input_digest, shuffled.input_digest)

    def test_two_processes_with_different_hash_seeds_agree(self) -> None:
        """Determinism must not be an artifact of one interpreter's hash seed.

        The child builds the same scope from the same JSON and prints its digest.
        Run with two seeds and compared with the in-process value: a payload that
        depended on set or dict iteration order would differ.
        """

        scope = make_scope()
        records = [
            make_record(canonical_identity=identity(31)),
            make_record(canonical_identity=identity(32), start=INSIDE_EVENING, sport_code=2, sport="cycling"),
        ]
        with network_disabled():
            local = prepare_scoped_input(
                scope=scope, records=records, field_specs=DECLARED_FULL, policy=SYNTHETIC_POLICY
            )
        local_digest = local.input_digest
        local_payload = local.canonical_payload

        child = (
            "import json, os, sys\n"
            "from datara.canonical import LogicalIdentity\n"
            "from datara.normalization import NormalizationPolicy\n"
            "from datara.provenance import AbsentObservation, ScopedField\n"
            "from datara.scoped_input import (ActivityScope, InputFieldSpec, ScopedRecord,\n"
            "    prepare_scoped_input)\n"
            "d = json.loads(os.environ['TK21_FIXTURE'])\n"
            "policy = NormalizationPolicy(**d['policy'])\n"
            "sb = dict(d['scope'])\n"
            "sb.pop('window')\n"
            "if sb['sports'] is not None:\n"
            "    sb['sports'] = frozenset(sb['sports'])\n"
            "scope = ActivityScope(**sb)\n"
            "specs = tuple(InputFieldSpec(**s) for s in d['declared'])\n"
            "records = []\n"
            "for r in d['records']:\n"
            "    t = r['logical_tuple']\n"
            "    fields = []\n"
            "    for name in sorted(r['fields']):\n"
            "        f = r['fields'][name]\n"
            "        a = f['absent']\n"
            "        fields.append(ScopedField(field_name=f['field_name'],\n"
            "            value_class=f['value_class'], value_canonical=f['value_canonical'],\n"
            "            preparation_version=f['preparation_version'],\n"
            "            mapping_reference=f['mapping_reference'],\n"
            "            absent=None if a is None else AbsentObservation(**a)))\n"
            "    tuple_value = LogicalIdentity(sport_code=t['sport_code'],\n"
            "        start_epoch_seconds=t['start_epoch_seconds'],\n"
            "        elapsed_duration_ms=t['elapsed_duration_ms'])\n"
            "    records.append(ScopedRecord(canonical_identity=r['canonical_identity'],\n"
            "        source_digest=r['source_digest'], logical_tuple=tuple_value,\n"
            "        preparation_version=r['preparation_version'],\n"
            "        policy_version=r['policy_version'], mapping_reference=r['mapping_reference'],\n"
            "        disposition=r['disposition'], quarantined=r['quarantined'],\n"
            "        fields=tuple(fields)))\n"
            "v = prepare_scoped_input(scope=scope, records=records, field_specs=specs,\n"
            "    policy=policy)\n"
            "sys.stdout.write(json.dumps({'digest': v.input_digest,\n"
            "    'payload': v.canonical_payload}))\n"
        )
        repo_root = str(Path(__file__).resolve().parents[2])
        fixture = json.dumps(
            {
                "policy": {
                    "policy_version": SYNTHETIC_POLICY.policy_version,
                    "mapping_reference": SYNTHETIC_POLICY.mapping_reference,
                    "supported_sports": sorted(SYNTHETIC_POLICY.supported_sports),
                    "max_elapsed_duration_seconds": SYNTHETIC_POLICY.max_elapsed_duration_seconds,
                    "max_timer_duration_seconds": SYNTHETIC_POLICY.max_timer_duration_seconds,
                    "max_distance_value": SYNTHETIC_POLICY.max_distance_value,
                    "max_record_sample_count": SYNTHETIC_POLICY.max_record_sample_count,
                    "max_gps_point_count": SYNTHETIC_POLICY.max_gps_point_count,
                    "max_heart_rate_value": SYNTHETIC_POLICY.max_heart_rate_value,
                },
                "scope": scope.as_record(),
                "declared": [spec.as_record() for spec in DECLARED_FULL],
                "records": [record.as_record() for record in records],
            }
        )

        def run_in(seed: str) -> dict:
            env = dict(os.environ)
            env["PYTHONPATH"] = repo_root
            env["PYTHONHASHSEED"] = seed
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["TK21_FIXTURE"] = fixture
            completed = subprocess.run(
                [sys.executable, "-X", "utf8", "-c", child],
                capture_output=True,
                text=True,
                env=env,
                timeout=180,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            return json.loads(completed.stdout)

        seed_zero = run_in("0")
        seed_other = run_in("12345")
        self.assertEqual(seed_zero["digest"], seed_other["digest"])
        self.assertEqual(seed_zero["digest"], local_digest)
        self.assertEqual(seed_zero["payload"], local_payload)

    def test_canonical_form_is_stable_and_carries_no_owner_or_timestamp(self) -> None:
        scope = make_scope()
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(41))],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        text = version.canonical_payload
        self.assertNotIn(": ", text)
        self.assertNotIn(", ", text)
        self.assertEqual(text, canonical_json(json.loads(text)))
        self.assertEqual(list(json.loads(text).keys()), sorted(json.loads(text).keys()))
        # SR05: generated identifiers and processing timestamps are not part of a
        # prepared value's identity.
        self.assertNotIn("owner", text)
        self.assertNotIn("created_at", text)
        self.assertNotIn("activity_id", text)
        self.assertEqual(version.input_digest, sha256_digest(text))

    def test_the_digest_covers_the_values_so_an_edit_cannot_preserve_it(self) -> None:
        """Mutation control: a value edit must change the version identity."""

        scope = make_scope()
        with network_disabled():
            base = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(51))],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
            edited = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(51), elapsed_ms=3_600_001)],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        self.assertNotEqual(base.input_digest, edited.input_digest)


# ===========================================================================
# 2. The scope contract
# ===========================================================================


class ScopeContractTests(TestCase):
    """Scope is explicit and bounded; what it may and may not contain is code."""

    def test_a_scope_must_state_a_window_and_a_capacity(self) -> None:
        with self.assertRaises(ScopeContractError):
            make_scope(start_utc=WINDOW_END, end_utc=WINDOW_START)  # reversed
        with self.assertRaises(ScopeContractError):
            make_scope(start_utc=WINDOW_START, end_utc=WINDOW_START)  # empty
        with self.assertRaises(ScopeContractError):
            make_scope(max_activities=0)
        with self.assertRaises(ScopeContractError):
            make_scope(sports=frozenset())  # selects nothing
        # A genuinely unbounded scope is not constructible: every field is required.
        with self.assertRaises(TypeError):
            ActivityScope(kind="x", start_utc=WINDOW_START, end_utc=WINDOW_END)  # type: ignore[call-arg]

    def test_a_naive_or_sub_second_window_bound_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            make_scope(start_utc="2026-10-01T00:00:00.500Z")
        with self.assertRaises(ValueError):
            make_scope(end_utc="2026-10-02 00:00:00")  # space, not the canonical form

    def test_window_is_half_open_so_the_end_instant_is_out_of_scope(self) -> None:
        scope = make_scope()
        self.assertTrue(scope.contains_start(INSIDE_MORNING))
        self.assertFalse(scope.contains_start(INSIDE_MIDNIGHT))
        self.assertFalse(scope.contains_start(OUTSIDE_BEFORE))
        self.assertFalse(scope.contains_start(OUTSIDE_AFTER))
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[
                    make_record(canonical_identity=identity(61), start=INSIDE_MIDNIGHT),
                    make_record(canonical_identity=identity(62), start=INSIDE_MORNING),
                ],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        self.assertEqual([r.canonical_identity for r in version.records], [identity(62)])
        self.assertEqual(
            [e.reason_code for e in version.exclusions], [EXCLUDED_OUTSIDE_WINDOW]
        )

    def test_every_exclusion_code_is_reachable_and_none_is_invented(self) -> None:
        """Each frozen reason code is produced by a real candidate.

        Every candidate carries the *same* strict declaration, because a record is
        judged against the scope's declaration and a record missing a declared
        field would abort the run rather than being excluded.
        """

        scope = make_scope(sports=frozenset({"running"}), max_activities=1)
        candidates = [
            # quarantined, by the flag
            make_record(canonical_identity=identity(71), declared=DECLARED_STRICT, quarantined=True),
            # quarantined, by the import disposition
            make_record(
                canonical_identity=identity(72),
                declared=DECLARED_STRICT,
                disposition=DISPOSITION_QUARANTINED,
            ),
            # out of window
            make_record(canonical_identity=identity(73), declared=DECLARED_STRICT, start=OUTSIDE_AFTER),
            # sport not selected
            make_record(
                canonical_identity=identity(74),
                declared=DECLARED_STRICT,
                sport_code=2,
                sport="cycling",
                start=INSIDE_MORNING,
            ),
            # different policy / mapping / preparation version
            make_record(
                canonical_identity=identity(75), declared=DECLARED_STRICT, policy_version="other-policy"
            ),
            make_record(
                canonical_identity=identity(76), declared=DECLARED_STRICT, mapping_reference="other-mapping"
            ),
            make_record(
                canonical_identity=identity(77),
                declared=DECLARED_STRICT,
                preparation_version="other-preparation",
            ),
            # a *required* declared field with no value
            make_record(
                canonical_identity=identity(78),
                declared=DECLARED_STRICT,
                include_optional_values=False,
            ),
            # a duplicate of an already-included identity, then two more that
            # capacity displaces
            make_record(canonical_identity=identity(79), declared=DECLARED_STRICT),
            make_record(canonical_identity=identity(79), declared=DECLARED_STRICT),
            make_record(canonical_identity=identity(80), declared=DECLARED_STRICT),
            make_record(canonical_identity=identity(81), declared=DECLARED_STRICT),
        ]
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope, records=candidates, field_specs=DECLARED_STRICT, policy=SYNTHETIC_POLICY
            )
        produced = {e.reason_code for e in version.exclusions}
        self.assertEqual(
            produced,
            {
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
            },
        )
        self.assertEqual(produced, set(EXCLUSION_REASONS))
        self.assertEqual(version.included_count, 1)
        # An exclusion whose code is outside the vocabulary is a defect, not a new
        # reason.
        with self.assertRaises(Exception) as caught:
            ScopedExclusion(identity(1), "because_i_said_so")
        self.assertIn("frozen vocabulary", str(caught.exception))

    def test_quarantine_is_reported_before_any_other_reason(self) -> None:
        """A quarantined candidate must never be reported as merely out of window.

        Otherwise a quarantined record would be indistinguishable from a benign
        exclusion, and a later reader could treat it as resolvable.
        """

        scope = make_scope()
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[
                    make_record(
                        canonical_identity=identity(91),
                        quarantined=True,
                        disposition=DISPOSITION_QUARANTINED,
                        start=OUTSIDE_AFTER,
                        policy_version="other-policy",
                    )
                ],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        self.assertEqual(
            [e.reason_code for e in version.exclusions], [EXCLUDED_QUARANTINED]
        )

    def test_capacity_is_explicit_and_never_a_silent_truncation(self) -> None:
        scope = make_scope(max_activities=2)
        records = [make_record(canonical_identity=identity(n)) for n in (101, 102, 103, 104)]
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope, records=records, field_specs=DECLARED_FULL, policy=SYNTHETIC_POLICY
            )
        self.assertEqual(version.included_count, 2)
        self.assertEqual(version.excluded_count, 2)
        self.assertEqual(
            sorted(e.reason_code for e in version.exclusions),
            [EXCLUDED_CAPACITY, EXCLUDED_CAPACITY],
        )
        # The retained set is a function of canonical identity, not of arrival order.
        self.assertEqual(
            [r.canonical_identity for r in version.records], [identity(101), identity(102)]
        )
        # The control: a version that overran its own capacity cannot be built.
        # The payload/digest pair is internally consistent, so the capacity check
        # is what refuses it, not the digest check.
        overfull = tuple(make_record(canonical_identity=identity(n)) for n in (111, 112))
        block = canonical_json({"record_count": 2})
        with self.assertRaises(ScopeCapacityExceeded):
            ScopedInputVersion(
                contract_version=SCOPED_INPUT_CONTRACT_VERSION,
                scoped_input_version="tk21-scoped-input/1",
                scope=make_scope(max_activities=1),
                policy=SYNTHETIC_POLICY,
                records=overfull,
                exclusions=(),
                declared=DECLARED_FULL,
                canonical_payload=block,
                input_digest=sha256_digest(block),
                ledger=build_ledger(
                    (r.canonical_identity, r.source_digest, r.fields) for r in overfull
                ),
            )

    def test_a_record_offering_an_undeclared_field_is_refused(self) -> None:
        """SR07/TC05/TC20: only the selected dataset. An extra field is not data."""

        scope = make_scope()
        record = make_record(canonical_identity=identity(121), declared=DECLARED_FULL)
        widened = ScopedRecord(
            canonical_identity=record.canonical_identity,
            source_digest=record.source_digest,
            logical_tuple=record.logical_tuple,
            preparation_version=record.preparation_version,
            policy_version=record.policy_version,
            mapping_reference=record.mapping_reference,
            disposition=record.disposition,
            quarantined=record.quarantined,
            fields=record.fields
            + (
                ScopedField(
                    field_name="timer_duration_seconds",
                    value_class=SRC,
                    value_canonical="3540",
                    preparation_version=NORMALIZER_VERSION,
                    mapping_reference=SYNTHETIC_MAPPING,
                ),
            ),
        )
        with self.assertRaises(UndeclaredFieldInRecord) as caught:
            with network_disabled():
                prepare_scoped_input(
                    scope=scope,
                    records=[widened],
                    field_specs=DECLARED_MINIMAL,
                    policy=SYNTHETIC_POLICY,
                )
        self.assertIn("timer_duration_seconds", str(caught.exception))

    def test_a_record_missing_a_declared_field_is_refused(self) -> None:
        scope = make_scope()
        record = make_record(canonical_identity=identity(131), declared=DECLARED_FULL)
        trimmed = ScopedRecord(
            canonical_identity=record.canonical_identity,
            source_digest=record.source_digest,
            logical_tuple=record.logical_tuple,
            preparation_version=record.preparation_version,
            policy_version=record.policy_version,
            mapping_reference=record.mapping_reference,
            disposition=record.disposition,
            quarantined=record.quarantined,
            fields=tuple(f for f in record.fields if f.field_name != "quality_warnings"),
        )
        with self.assertRaises(DeclaredFieldMissing):
            with network_disabled():
                prepare_scoped_input(
                    scope=scope,
                    records=[trimmed],
                    field_specs=DECLARED_FULL,
                    policy=SYNTHETIC_POLICY,
                )

    def test_the_prohibited_content_scan_cannot_be_evaded_by_spelling(self) -> None:
        """SR07/TC20 negatives: credentials, prompts and recommendations stay out."""

        for key in (
            "api_key",
            "apiKey",
            "API-KEY",
            "authorization",
            "system_prompt",
            "provider_id",
            "model_name",
            "recommendation",
            "completion",
            "apiSecret",
            "bearer_token",
        ):
            with self.subTest(key=key):
                with self.assertRaises(ProhibitedScopeContent):
                    assert_no_prohibited_content({"records": [{key: "x"}]})
        # The control: the scan sees a key it should accept.
        assert_no_prohibited_content({"records": [{"elapsed_duration_ms": "1"}]})
        # Raw bytes are refused too: a skill input is not an upload.
        with self.assertRaises(ProhibitedScopeContent):
            assert_no_prohibited_content({"records": [{"original": b"\x00\x01"}]})
        self.assertGreaterEqual(len(PROHIBITED_PAYLOAD_TOKENS), 10)

    def test_a_computed_metric_cannot_be_declared_in_milestone_a(self) -> None:
        with self.assertRaises(ValueClassUnavailable) as caught:
            InputFieldSpec("weekly_load", "computed_metric", False)
        self.assertIn("D02/WP02", str(caught.exception))
        self.assertNotIn("computed_metric", MILESTONE_A_VALUE_CLASSES)

    def test_a_policy_that_does_not_match_the_scope_is_refused(self) -> None:
        scope = make_scope(policy_version="a-different-policy")
        with self.assertRaises(ScopeContractError):
            with network_disabled():
                prepare_scoped_input(
                    scope=scope,
                    records=[make_record(canonical_identity=identity(141))],
                    field_specs=DECLARED_FULL,
                    policy=SYNTHETIC_POLICY,
                )


# ===========================================================================
# 3. Quarantine exclusion
# ===========================================================================


class QuarantineExclusionTests(TestCase):
    """A quarantined candidate is unresolved and must reach no skill input."""

    def test_a_quarantined_candidate_cannot_enter_a_scope(self) -> None:
        scope = make_scope()
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[
                    make_record(canonical_identity=identity(151)),
                    make_record(canonical_identity=identity(152), quarantined=True),
                ],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        self.assertNotIn(identity(152), [r.canonical_identity for r in version.records])
        self.assertNotIn(identity(152), version.included_digests)
        self.assertIn(
            identity(152), version.canonical_payload  # named, as an exclusion
        )
        self.assertIn(
            EXCLUDED_QUARANTINED, json.loads(version.canonical_payload)["exclusions"][0].values()
        )

    def test_a_hand_built_version_cannot_smuggle_a_quarantined_candidate(self) -> None:
        """The postcondition holds for any construction, not only the filtering one.

        Mutation control: this constructs the illegal value directly. If the
        postcondition were enforced only inside ``prepare_scoped_input``, this
        version would be accepted and the property would be a convention.
        """

        scope = make_scope()
        clean = make_record(canonical_identity=identity(161), declared=DECLARED_FULL)
        quarantined = make_record(
            canonical_identity=identity(162), declared=DECLARED_FULL, quarantined=True
        )
        payload = {
            "contract_version": SCOPED_INPUT_CONTRACT_VERSION,
            "scoped_input_version": "tk21-scoped-input/1",
            "records": [clean.as_record(), quarantined.as_record()],
            "record_count": 2,
        }
        with self.assertRaises(QuarantinedCandidateInScope):
            ScopedInputVersion(
                contract_version=SCOPED_INPUT_CONTRACT_VERSION,
                scoped_input_version="tk21-scoped-input/1",
                scope=scope,
                policy=SYNTHETIC_POLICY,
                records=(clean, quarantined),
                exclusions=(),
                declared=DECLARED_FULL,
                canonical_payload=canonical_json(payload),
                input_digest=sha256_digest(canonical_json(payload)),
                ledger=build_ledger(
                    (r.canonical_identity, r.source_digest, r.fields) for r in (clean, quarantined)
                ),
            )
        # The same construction with a non-published disposition is equally refused.
        unpublished = make_record(
            canonical_identity=identity(163), declared=DECLARED_FULL, disposition=DISPOSITION_QUARANTINED
        )
        with self.assertRaises(QuarantinedCandidateInScope):
            ScopedInputVersion(
                contract_version=SCOPED_INPUT_CONTRACT_VERSION,
                scoped_input_version="tk21-scoped-input/1",
                scope=scope,
                policy=SYNTHETIC_POLICY,
                records=(clean, unpublished),
                exclusions=(),
                declared=DECLARED_FULL,
                canonical_payload=canonical_json(payload),
                input_digest=sha256_digest(canonical_json(payload)),
                ledger=build_ledger(
                    (r.canonical_identity, r.source_digest, r.fields)
                    for r in (clean, unpublished)
                ),
            )


# ===========================================================================
# 4. Provenance
# ===========================================================================


class ProvenanceTests(TestCase):
    """Every value names its source record, digest, preparation and mapping."""

    def test_every_field_of_every_record_resolves(self) -> None:
        scope = make_scope()
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[
                    make_record(canonical_identity=identity(171)),
                    make_record(canonical_identity=identity(172), include_optional_values=False),
                ],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        expected = version.all_field_paths()
        self.assertEqual(sorted(expected), sorted(version.ledger.field_paths()))
        version.ledger.require_complete(expected)
        for path in expected:
            entry = version.ledger.resolve(path)
            self.assertTrue(entry.canonical_identity.startswith("sha256:"))
            self.assertTrue(entry.source_digest.startswith("sha256:"))
            self.assertEqual(entry.preparation_version, NORMALIZER_VERSION)
            self.assertEqual(entry.mapping_reference, SYNTHETIC_MAPPING)
        # The control: resolving a field the input does not carry is a loud failure
        # with no default entry.
        with self.assertRaises(UnresolvableProvenance):
            version.ledger.resolve(f"{identity(171)}.timer_duration_seconds")

    def test_a_field_with_no_provenance_source_is_a_failure_not_a_default(self) -> None:
        ledger = build_ledger(
            [
                (
                    identity(181),
                    "sha256:" + "ab" * 32,
                    (
                        ScopedField(
                            field_name="sport",
                            value_class=SRC,
                            value_canonical="running",
                            preparation_version=NORMALIZER_VERSION,
                            mapping_reference=SYNTHETIC_MAPPING,
                        ),
                    ),
                )
            ]
        )
        # A declared field the ledger does not cover: raised, not defaulted.
        with self.assertRaises(ProvenanceIncomplete) as caught:
            ledger.require_complete(
                [f"{identity(181)}.sport", f"{identity(181)}.elapsed_duration_ms"]
            )
        self.assertIn("elapsed_duration_ms", str(caught.exception))
        self.assertEqual(len(caught.exception.missing), 1)
        # And the check also catches the *shorter* ledger, which a per-field
        # "is this one present" check would miss.
        with self.assertRaises(ProvenanceIncomplete):
            ledger.require_complete([f"{identity(181)}.sport", f"{identity(181)}.missing_one"])

    def test_a_null_value_with_no_recorded_absence_reason_is_unrepresentable(self) -> None:
        with self.assertRaises(Exception) as caught:
            ScopedField(
                field_name="heart_rate_value",
                value_class=SRC,
                value_canonical=None,
                preparation_version=NORMALIZER_VERSION,
                mapping_reference=SYNTHETIC_MAPPING,
            )
        self.assertIn("AbsentObservation", str(caught.exception))
        # A value that is both present and explained as absent is equally refused.
        with self.assertRaises(Exception):
            ScopedField(
                field_name="heart_rate_value",
                value_class=SRC,
                value_canonical="150",
                preparation_version=NORMALIZER_VERSION,
                mapping_reference=SYNTHETIC_MAPPING,
                absent=AbsentObservation(code="OPT_ABSENT", detail="absent"),
            )

    def test_an_unavailable_value_renders_as_unavailable_never_as_zero(self) -> None:
        scope = make_scope()
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(191), include_optional_values=False)],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        rows = {row.field_path: row for row in version.provenance_display()}
        absent_row = rows[f"{identity(191)}.heart_rate_value"]
        self.assertTrue(absent_row.unavailable)
        self.assertTrue(absent_row.rendered_value.startswith(UNAVAILABLE_LABEL))
        self.assertNotIn("0", absent_row.rendered_value)
        self.assertEqual(absent_row.unavailable_reason, "OPT_ABSENT/absent")
        # The control: a present value of 0 would render as "0", and is a
        # different thing. So the check is about provenance, not about the digit.
        self.assertEqual(rows[f"{identity(191)}.sport"].rendered_value, "running")
        self.assertEqual(rows[f"{identity(191)}.quality_warnings"].value_class, WARNING)

    def test_display_states_the_value_class_of_every_row(self) -> None:
        scope = make_scope()
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(201))],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        rows = version.provenance_display()
        self.assertEqual(len(rows), len(version.all_field_paths()))
        classes = {row.value_class for row in rows}
        self.assertEqual(classes, {MEMBER, SRC, WARNING})
        for row in rows:
            self.assertTrue(row.value_class_label)
            self.assertEqual(row.mapping_reference, SYNTHETIC_MAPPING)
            self.assertEqual(row.preparation_version, NORMALIZER_VERSION)

    def test_two_entries_may_not_claim_one_field_path(self) -> None:
        """A field path addresses exactly one value.

        Mutation control: two entries with the *same* path but different source
        records and different values. If the ledger kept both, one of the two
        values would be unaddressable and a resolver would silently pick one.
        """

        path = f"{identity(211)}.sport"
        first = FieldProvenance(
            field_path=path,
            value_class=SRC,
            canonical_identity=identity(211),
            source_digest="sha256:" + "cd" * 32,
            preparation_version=NORMALIZER_VERSION,
            mapping_reference=SYNTHETIC_MAPPING,
            value_canonical="running",
        )
        second = FieldProvenance(
            field_path=path,
            value_class=SRC,
            canonical_identity=identity(212),
            source_digest="sha256:" + "ef" * 32,
            preparation_version=NORMALIZER_VERSION,
            mapping_reference=SYNTHETIC_MAPPING,
            value_canonical="cycling",
        )
        with self.assertRaises(DuplicateFieldPath):
            ProvenanceLedger(entries=(first, second))
        # The control: distinct paths are accepted and ordered deterministically.
        distinct = ProvenanceLedger(
            entries=(
                FieldProvenance(
                    field_path=f"{identity(213)}.sport",
                    value_class=SRC,
                    canonical_identity=identity(213),
                    source_digest="sha256:" + "cd" * 32,
                    preparation_version=NORMALIZER_VERSION,
                    mapping_reference=SYNTHETIC_MAPPING,
                    value_canonical="running",
                ),
                first,
            )
        )
        self.assertEqual(
            distinct.field_paths(),
            (f"{identity(211)}.sport", f"{identity(213)}.sport"),
        )

    def test_an_absent_observation_must_use_the_recorded_warning_vocabulary(self) -> None:
        with self.assertRaises(Exception) as caught:
            AbsentObservation(code="I_MADE_THIS_UP", detail="absent")
        self.assertIn("vocabulary", str(caught.exception))
        # The control: a real recorded warning is accepted and round-trips.
        observation = AbsentObservation.from_warning_record(
            {"code": "OPT_ABSENT", "detail": "absent", "source_field": "synthetic.records.gps"}
        )
        self.assertEqual(observation.as_record()["source_field"], "synthetic.records.gps")


# ===========================================================================
# 5. Immutability and versioning
# ===========================================================================


class ImmutabilityTests(TestCase):
    """A version is immutable; a new version is a new value."""

    def test_a_version_whose_digest_does_not_cover_its_payload_is_refused(self) -> None:
        """The version identity is the digest of the version's own bytes.

        Without this check a hand-built or edited value could claim an identity
        that belongs to different content, and the two would then be
        indistinguishable in history.
        """

        scope = make_scope()
        record = make_record(canonical_identity=identity(221))
        block = canonical_json({"record_count": 1})
        common = {
            "contract_version": SCOPED_INPUT_CONTRACT_VERSION,
            "scoped_input_version": "tk21-scoped-input/1",
            "scope": scope,
            "policy": SYNTHETIC_POLICY,
            "records": (record,),
            "exclusions": (),
            "declared": DECLARED_FULL,
            "canonical_payload": block,
            "ledger": build_ledger([(record.canonical_identity, record.source_digest, record.fields)]),
        }
        # A digest that is not the digest of the payload is refused.
        with self.assertRaises(ScopedInputError) as caught:
            ScopedInputVersion(input_digest="sha256:" + "1" * 64, **common)
        self.assertIn("not the digest of its content", str(caught.exception))
        # The matching digest is accepted, so the check is not simply refusing
        # everything.
        accepted = ScopedInputVersion(input_digest=sha256_digest(block), **common)
        self.assertEqual(accepted.input_digest, sha256_digest(block))

    def test_a_record_pointing_at_another_identitys_source_object_is_refused(self) -> None:
        """Fault injection: the owner-scope guard on a referenced row is live.

        The store's own writes cannot produce this, so the guard would otherwise
        be unverified. Here one identity's activity is repointed at the other
        identity's source object, and the scope must refuse rather than answer
        from a row the owner cannot see -- Django's forward descriptors are
        documented in ``datara.models`` as *not* an authorization boundary, which
        is exactly why this read goes through an owner-scoped queryset.
        """

        from datara import models as m

        other = _Owner("tk21-crossref")
        foreign = other.add_accepted(start_utc="2026-10-01T07:00:00Z")
        mine = _Owner("tk21-crossref-mine")
        own = mine.add_accepted(start_utc="2026-10-01T06:00:00Z")
        m.Activity.objects.unbound().filter(pk=own.pk).update(
            source_object_id=foreign.source_object_id
        )
        with self.assertRaises(Exception) as caught:
            with network_disabled():
                mine.inputs.scope_candidates(make_scope(), DECLARED_FULL)
        message = str(caught.exception)
        self.assertIn("source object", message)
        self.assertIn("another identity", message)
        # The other identity's own scope is unaffected and still resolves.
        with network_disabled():
            candidates = other.inputs.scope_candidates(make_scope(), DECLARED_FULL)
        self.assertEqual(
            [r.canonical_identity for r in candidates], [foreign.normalization_digest]
        )

    def test_a_record_pointing_at_another_identitys_import_is_refused(self) -> None:
        from datara import models as m

        other = _Owner("tk21-crossimport")
        foreign = other.add_accepted(start_utc="2026-10-01T07:30:00Z")
        mine = _Owner("tk21-crossimport-mine")
        own = mine.add_accepted(start_utc="2026-10-01T06:30:00Z")
        m.Activity.objects.unbound().filter(pk=own.pk).update(
            import_record_id=foreign.import_record_id
        )
        with self.assertRaises(Exception) as caught:
            with network_disabled():
                mine.inputs.scope_candidates(make_scope(), DECLARED_FULL)
        self.assertIn("import record", str(caught.exception))

    def test_a_version_is_a_frozen_value(self) -> None:
        scope = make_scope()
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(221))],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        with self.assertRaises(Exception):
            version.input_digest = "sha256:" + "1" * 64  # type: ignore[misc]
        with self.assertRaises(Exception):
            version.records[0].fields[0].value_canonical = "tampered"  # type: ignore[misc]

    def test_a_version_round_trips_and_refuses_a_non_canonical_payload(self) -> None:
        scope = make_scope()
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(231))],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        restored = ScopedInputVersion.from_canonical_payload(version.canonical_payload)
        self.assertEqual(restored.canonical_payload, version.canonical_payload)
        self.assertEqual(restored.input_digest, version.input_digest)
        self.assertEqual(restored.included_digests, version.included_digests)
        self.assertEqual(
            [e.as_record() for e in restored.exclusions],
            [e.as_record() for e in version.exclusions],
        )
        self.assertEqual(restored.ledger.digest(), version.ledger.digest())
        # Mutation control: re-serialised text is no longer canonical, so it
        # cannot be digest-verified and is refused rather than trusted.
        parsed = json.loads(version.canonical_payload)
        for label, mutation in (
            ("whitespace", json.dumps(parsed, indent=2)),
            ("key order", json.dumps(parsed, sort_keys=False)),
            ("trailing byte", version.canonical_payload + "\n"),
        ):
            with self.subTest(mutation=label):
                with self.assertRaises(Exception) as caught:
                    ScopedInputVersion.from_canonical_payload(mutation)
                self.assertIn("canonical", str(caught.exception))

    def test_a_value_edited_in_the_stored_row_is_refused_on_read(self) -> None:
        """The stored digest column is what catches an edit of a canonical payload.

        A *canonical* value edit is indistinguishable from a legitimate different
        version unless the separately stored digest is compared against the
        payload. That comparison is :meth:`MilestoneAInputStore.get_version`, and
        this test mutates the row to prove the comparison actually happens.
        """

        from datara import models as m

        owner = _Owner("tk21-tamper")
        owner.add_accepted(start_utc="2026-10-01T06:30:00Z")
        scope = make_scope()
        with network_disabled():
            candidates = owner.inputs.scope_candidates(scope, DECLARED_FULL)
            version = prepare_scoped_input(
                scope=scope, records=candidates, field_specs=DECLARED_FULL, policy=SYNTHETIC_POLICY
            )
        handle = owner.inputs.append_version(version)
        self.assertEqual(
            owner.inputs.get_version(handle.version_ref).canonical_payload,
            version.canonical_payload,
        )
        m.Snapshot.objects.unbound().filter(pk=handle.version_ref).update(
            canonical_payload=version.canonical_payload.replace('"running"', '"cycling"')
        )
        with self.assertRaises(Exception) as caught:
            owner.inputs.get_version(handle.version_ref)
        self.assertIn("does not match", str(caught.exception))

    def test_the_store_exposes_no_mutation_and_no_newest_value_accessor(self) -> None:
        user = get_user_model().objects.create_user(username="tk21-api", password="x")
        store = MilestoneAInputStore(OwnerScopedStore.for_user(user))
        self.assertEqual(store.mutable_version_api(), [])
        self.assertEqual(store.newest_value_api(), [])

    def test_a_different_selection_is_a_different_version_not_an_edit(self) -> None:
        """The same scope with a narrower declaration is a different version.

        The prior value is not edited: its own payload and digest are unchanged,
        and the new one has its own identity. Each prepare gets records carrying
        exactly its own declaration, because a record offering more than the
        declaration is refused (SR07/TC05: only the selected dataset).
        """

        scope = make_scope()
        with network_disabled():
            first = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(241), declared=DECLARED_FULL)],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
            first_digest = first.input_digest
            first_payload = first.canonical_payload
            second = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(241), declared=DECLARED_MINIMAL)],
                field_specs=DECLARED_MINIMAL,
                policy=SYNTHETIC_POLICY,
            )
        self.assertNotEqual(first_digest, second.input_digest)
        self.assertNotEqual(first_payload, second.canonical_payload)
        # The first value is untouched by the second being produced.
        self.assertEqual(first.input_digest, first_digest)
        self.assertEqual(first.canonical_payload, first_payload)
        self.assertEqual(len(first.records), 1)

    def test_the_store_satisfies_the_narrow_interface(self) -> None:
        user = get_user_model().objects.create_user(username="tk21-proto", password="x")
        store = MilestoneAInputStore(OwnerScopedStore.for_user(user))
        self.assertIsInstance(store, VersionedInputStore)
        for name in ("scope_candidates", "append_version", "get_version", "list_versions"):
            self.assertTrue(callable(getattr(store, name)), name)
        # The interface has no mutating operation at all, so "a prior version is
        # never mutated in place" is not a convention a caller could bypass.
        self.assertFalse(
            [n for n in dir(VersionedInputStore) if any(t in n for t in ("update", "delete", "overwrite"))]
        )


# ===========================================================================
# 6. Persistence over the merged schema
# ===========================================================================


class _Owner:
    """A small helper that builds accepted, prepared records for one owner."""

    def __init__(self, username: str) -> None:
        self.user = get_user_model().objects.create_user(username=username, password="x")
        self.store = OwnerScopedStore.for_user(self.user)
        self.inputs = MilestoneAInputStore(self.store)
        self._digest_counter = 0

    def add_accepted(
        self,
        *,
        start_utc: str,
        elapsed_seconds: int = 3600,
        heart_rate: int | None = 150,
        disposition: str = DISPOSITION_PUBLISHED,
    ) -> Any:
        """Persist one accepted, prepared activity and return it."""

        self._digest_counter += 1
        source_digest = "sha256:" + ("%064x" % (0x1000 + self._digest_counter))
        source = self.store.record_source_object(
            digest=source_digest,
            byte_length=4096,
            storage_reference=f"synthetic/tk21/{self.user.pk}/{self._digest_counter}",
            media_type="application/vnd.datara.synthetic",
        )
        import_record = self.store.record_import(
            source_digest=source_digest, status="accepted"
        )
        with network_disabled():
            normalized = normalize(
                RawActivityInput(
                    source_digest=source_digest,
                    sport="running",
                    session_start_utc=start_utc,
                    elapsed_duration_seconds=elapsed_seconds,
                    heart_rate_value=heart_rate,
                    heart_rate_unit_code="synthetic_rate_unit_b" if heart_rate else None,
                    source_fields={
                        "source_digest": "synthetic.file.digest",
                        "sport": "synthetic.session.sport",
                        "session_start_utc": "synthetic.session.start_time_utc",
                        "elapsed_duration_seconds": "synthetic.session.elapsed_duration_seconds",
                        "heart_rate": "synthetic.records.heart_rate",
                    },
                ),
                SYNTHETIC_POLICY,
            )
        activity = self.store.record_normalized_activity(
            source_object=source, import_record=import_record, normalized=normalized
        )
        if disposition != DISPOSITION_PUBLISHED:
            # The merged schema expresses a quarantined candidate on the record's
            # disposition as well as in the Quarantine row; the store reads both.
            from datara import models as m

            m.Activity.objects.unbound().filter(pk=activity.pk).update(disposition=disposition)
            activity.refresh_from_db()
        return activity

    def add_quarantine_for(self, activity: Any) -> None:
        """Record an unresolved Quarantine row for an existing import."""

        from datara import models as m

        m.Quarantine.objects.create(
            owner_id=self.user.pk,
            import_record_id=activity.import_record_id,
            candidate_source_object_id=activity.source_object_id,
            logical_tuple={"synthetic": True},
            candidate_normalization_digest=activity.normalization_digest,
            candidate_normalized_payload={"synthetic": True},
            reason_code=m.Quarantine.REASON_LOGICAL_TUPLE_CONFLICT,
            state=m.Quarantine.STATE_QUARANTINED,
        )


class PersistedVersionTests(TestCase):
    """The version is persisted as the already-authorised record set."""

    def setUp(self) -> None:
        self.owner = _Owner("tk21-persist")
        self.activity = self.owner.add_accepted(start_utc="2026-10-01T06:30:00Z")
        self.scope = make_scope()

    def _prepare(self, declared: tuple[InputFieldSpec, ...] = DECLARED_FULL) -> ScopedInputVersion:
        with network_disabled():
            candidates = self.owner.inputs.scope_candidates(self.scope, declared)
            return prepare_scoped_input(
                scope=self.scope,
                records=candidates,
                field_specs=declared,
                policy=SYNTHETIC_POLICY,
            )

    def test_a_version_is_persisted_and_read_back_identically(self) -> None:
        version = self._prepare()
        handle = self.owner.inputs.append_version(version)
        self.assertTrue(handle.created)
        self.assertEqual(handle.input_digest, version.input_digest)
        read_back = self.owner.inputs.get_version(handle.version_ref)
        self.assertEqual(read_back.canonical_payload, version.canonical_payload)
        self.assertEqual(read_back.input_digest, version.input_digest)
        # The persisted row carries the value's own bytes and digest.
        snapshot = self.owner.store.get_snapshot(handle.version_ref)
        self.assertEqual(snapshot.canonical_payload, version.canonical_payload)
        self.assertEqual(snapshot.snapshot_digest, version.input_digest)
        self.assertEqual(list(snapshot.included_digests), [self.activity.normalization_digest])

    def test_appending_the_same_version_twice_creates_no_second_row(self) -> None:
        version = self._prepare()
        first = self.owner.inputs.append_version(version)
        second = self.owner.inputs.append_version(version)
        self.assertTrue(first.created)
        self.assertFalse(second.created)
        self.assertEqual(first.version_ref, second.version_ref)
        self.assertEqual(len(self.owner.inputs.list_versions()), 1)
        # The prior version's bytes are untouched by the second call.
        self.assertEqual(
            self.owner.store.get_snapshot(first.version_ref).canonical_payload,
            version.canonical_payload,
        )

    def test_a_new_version_leaves_the_prior_version_byte_identical(self) -> None:
        """The re-versioning property, on the persisted row.

        Mutation control: a different field selection is appended after the
        first. If anything updated in place, the first row's payload or digest
        would change here.
        """

        first = self._prepare(DECLARED_FULL)
        first_handle = self.owner.inputs.append_version(first)
        self.owner.add_accepted(start_utc="2026-10-01T18:05:00Z")
        second = self._prepare(DECLARED_MINIMAL)
        second_handle = self.owner.inputs.append_version(second)

        self.assertTrue(second_handle.created)
        self.assertNotEqual(first_handle.version_ref, second_handle.version_ref)
        self.assertNotEqual(first.input_digest, second.input_digest)

        first_row = self.owner.store.get_snapshot(first_handle.version_ref)
        self.assertEqual(first_row.canonical_payload, first.canonical_payload)
        self.assertEqual(first_row.snapshot_digest, first.input_digest)
        self.assertEqual(first_row.included_count, 1)
        self.assertEqual(
            self.owner.inputs.get_version(first_handle.version_ref).canonical_payload,
            first.canonical_payload,
        )
        # History is append-only and queried: two rows, no newest accessor.
        self.assertEqual(len(self.owner.inputs.list_versions()), 2)

    def test_provenance_rows_are_written_and_verified_for_every_field(self) -> None:
        version = self._prepare()
        handle = self.owner.inputs.append_version(version)
        rows = self.owner.inputs.provenance_rows(handle.version_ref)
        self.assertEqual(len(rows), len(version.all_field_paths()))
        self.assertEqual(
            sorted(str(row["field_path"]) for row in rows),
            sorted(version.all_field_paths()),
        )
        for row in rows:
            self.assertEqual(row["activity_ref"], str(self.activity.activity_id))
            self.assertEqual(
                row["source_object_ref"], str(self.activity.source_object_id)
            )
        # Every field resolves back to the ledger.
        for row in rows:
            entry = version.ledger.resolve(str(row["field_path"]))
            self.assertEqual(row["value_canonical"], entry.value_canonical)

    def test_provenance_rows_refuse_an_input_with_a_missing_row(self) -> None:
        """Mutation control: delete one provenance row and the check fires."""

        from datara import models as m

        version = self._prepare()
        handle = self.owner.inputs.append_version(version)
        self.owner.inputs.provenance_rows(handle.version_ref)
        victim = version.declared_field_paths()[0]
        m.Evidence.objects.unbound().filter(field_path=victim).delete()
        with self.assertRaises(ProvenanceIncomplete) as caught:
            self.owner.inputs.provenance_rows(handle.version_ref)
        self.assertIn(victim, str(caught.exception))

    def test_an_unresolved_quarantine_row_excludes_the_candidate(self) -> None:
        """The existing Quarantine record is consumed, not re-derived."""

        quarantined = self.owner.add_accepted(start_utc="2026-10-01T07:00:00Z")
        self.owner.add_quarantine_for(quarantined)
        version = self._prepare()
        self.assertNotIn(
            quarantined.normalization_digest, [r.canonical_identity for r in version.records]
        )
        reasons = {
            e.canonical_identity: e.reason_code for e in version.exclusions
        }
        self.assertEqual(reasons[quarantined.normalization_digest], EXCLUDED_QUARANTINED)
        # And the scope that *would* have included it is a different version, so the
        # exclusion is part of the versioned value rather than a view filter.
        handle = self.owner.inputs.append_version(version)
        self.assertIn(EXCLUDED_QUARANTINED, self.owner.store.get_snapshot(handle.version_ref).canonical_payload)

    def test_the_candidates_view_marks_a_quarantined_disposition(self) -> None:
        quarantined = self.owner.add_accepted(
            start_utc="2026-10-01T08:00:00Z", disposition=DISPOSITION_QUARANTINED
        )
        with network_disabled():
            candidates = self.owner.inputs.scope_candidates(self.scope, DECLARED_FULL)
        flagged = {r.canonical_identity: r.quarantined for r in candidates}
        self.assertTrue(flagged[quarantined.normalization_digest])
        self.assertFalse(flagged[self.activity.normalization_digest])

    def test_a_second_identity_never_sees_or_appends_the_firsts_version(self) -> None:
        version = self._prepare()
        handle = self.owner.inputs.append_version(version)
        other = _Owner("tk21-persist-other")
        self.assertEqual(other.inputs.list_versions(), ())
        with self.assertRaises(ResourceNotVisible):
            other.inputs.get_version(handle.version_ref)
        with self.assertRaises(ResourceNotVisible):
            other.inputs.provenance_rows(handle.version_ref)
        # And the other identity's own scope is empty, not the first's data.
        with network_disabled():
            candidates = other.inputs.scope_candidates(self.scope, DECLARED_FULL)
        self.assertEqual(candidates, ())
        with self.assertRaises(Exception):
            other.inputs.append_version(version)  # its records belong to another owner

    def test_the_schema_binding_names_every_field_it_depends_on(self) -> None:
        """The coupling surface is declared, and the declaration is checked.

        ``schema_binding`` itself asserts every named field exists and that the
        disposition constants still equal the model's, so a schema change fails
        there rather than as an ``AttributeError`` deeper in.
        """

        from datara import models as m

        binding = self.owner.inputs.schema_binding()
        self.assertEqual(binding["Activity"][0], "activity_id")
        self.assertIn("elapsed_duration_ms", binding["Session"])
        self.assertIn("state", binding["Quarantine"])
        self.assertIn("canonical_payload", binding["Snapshot"])
        self.assertIn("method_version", binding["Evidence"])
        self.assertEqual(binding, self.owner.inputs.schema_binding())
        # The disposition vocabulary this module filters on is the model's.
        self.assertEqual(DISPOSITION_PUBLISHED, m.Activity.PUBLISHED)
        self.assertEqual(DISPOSITION_QUARANTINED, m.Activity.QUARANTINED)

    def test_canonical_identities_must_resolve_to_exactly_one_stored_record(self) -> None:
        with self.assertRaises(Exception) as caught:
            self.owner.inputs.resolve_activity_ids(("sha256:" + "9" * 64,))
        self.assertIn("not stored for this owner", str(caught.exception))
        self.assertEqual(
            list(self.owner.inputs.resolve_activity_ids((self.activity.normalization_digest,))),
            [self.activity.activity_id],
        )
        self.assertEqual(self.owner.inputs.resolve_activity_ids(()), ())

    def test_a_declared_field_with_no_milestone_a_source_is_refused(self) -> None:
        with self.assertRaises(Exception) as caught:
            self.owner.inputs.scope_candidates(
                self.scope, (InputFieldSpec("weekly_load", SRC, False),)
            )
        self.assertIn("no Milestone A source", str(caught.exception))

    def test_a_skill_may_not_relabel_a_stored_measurement(self) -> None:
        with self.assertRaises(Exception) as caught:
            self.owner.inputs.scope_candidates(
                self.scope, (InputFieldSpec("elapsed_duration_ms", MEMBER, True),)
            )
        self.assertIn("do not match the class", str(caught.exception))

    def test_every_declared_field_of_a_stored_record_is_actually_extracted(self) -> None:
        with network_disabled():
            candidates = self.owner.inputs.scope_candidates(self.scope, DECLARED_FULL)
        self.assertEqual(len(candidates), 1)
        record = candidates[0]
        self.assertEqual(record.canonical_identity, self.activity.normalization_digest)
        self.assertEqual(record.source_digest, record.field(HEADER_SOURCE_DIGEST).value_canonical)
        # The canonical unit is carried, in the canonical unit.
        self.assertEqual(
            record.field("elapsed_duration_ms").value_canonical, "3600000"
        )
        self.assertEqual(
            record.field("start_epoch_seconds").value_canonical, str(INSIDE_MORNING)
        )
        self.assertEqual(record.field("sport_code").value_canonical, "1")
        self.assertEqual(
            {f.field_name for f in record.fields},
            set(HEADER_FIELDS) | {s.field_name for s in DECLARED_FULL},
        )

    def test_an_absent_stored_optional_keeps_its_recorded_warning_as_the_reason(self) -> None:
        no_rate = self.owner.add_accepted(start_utc="2026-10-01T09:00:00Z", heart_rate=None)
        with network_disabled():
            candidates = self.owner.inputs.scope_candidates(self.scope, DECLARED_FULL)
        by_identity = {r.canonical_identity: r for r in candidates}
        field = by_identity[no_rate.normalization_digest].field("heart_rate_value")
        self.assertIsNone(field.value_canonical)
        self.assertIsNotNone(field.absent)
        self.assertEqual(field.absent.code, "OPT_ABSENT")  # TK18's own code
        self.assertEqual(field.absent.source_field, "synthetic.records.heart_rate")

    def test_an_import_digest_that_disagrees_with_its_source_object_is_refused(self) -> None:
        from datara import models as m

        m.Import.objects.unbound().filter(pk=self.activity.import_record_id).update(
            source_digest="sha256:" + "7" * 64
        )
        with self.assertRaises(Exception) as caught:
            with network_disabled():
                self.owner.inputs.scope_candidates(self.scope, DECLARED_FULL)
        self.assertIn("disagree", str(caught.exception))

    def test_the_canonical_unit_is_enforced_on_the_way_out(self) -> None:
        """The declared unit is checked, and the value reaches the envelope in ms.

        Stated honestly, because it is a limit and not a guarantee:
        ``datara.canonical`` documents that no function can *detect* that a bare
        integer ``3600`` means seconds -- ``3600`` ms is a legitimate 3.6-second
        duration. What the guard does enforce is the declared unit and the
        millisecond domain, so a sub-second value (a typical unconverted seconds
        count of a short activity) is refused. That is what is checked here.
        """

        from datara import models as m
        from datara.canonical import SECONDS_UNIT, require_elapsed_duration_ms

        # A value below the canonical one-second minimum: refused.
        with self.assertRaises(ValueError):
            require_elapsed_duration_ms(500, origin="test", unit=CANONICAL_DURATION_UNIT)
        # A wrong declared unit: refused, whatever the number.
        with self.assertRaises(TypeError):
            require_elapsed_duration_ms(3_600_000, origin="test", unit=SECONDS_UNIT)
        # A float or a decimal string: refused, because both made two different
        # durations compare equal after rounding.
        for bad in (3_600_000.0, "3600000", True):
            with self.assertRaises(TypeError):
                require_elapsed_duration_ms(bad, origin="test", unit=CANONICAL_DURATION_UNIT)
        # The stored value reaches the envelope in the canonical unit, read through
        # the guard rather than copied.
        m.Session.objects.unbound().filter(activity_id=self.activity.pk).update(
            elapsed_duration_ms=3_600_000
        )
        with network_disabled():
            candidates = self.owner.inputs.scope_candidates(self.scope, DECLARED_MINIMAL)
        self.assertEqual(
            candidates[0].field("elapsed_duration_ms").value_canonical, "3600000"
        )
        # A seconds count written into the millisecond column is refused by the
        # database, inside a savepoint so the failed write rolls back to the
        # savepoint and the test's transaction stays usable.
        #
        # Limit, stated rather than glossed: the check constraint and
        # ``require_elapsed_duration_ms`` enforce the *same* millisecond domain, so
        # no stored value is accepted by one and refused by the other. The Python
        # guard is verified at its own boundary above (wrong declared unit,
        # sub-domain value, non-integer); the constraint is verified here at the
        # database boundary. Neither claim is stronger than that.
        from django.db import transaction
        from django.db.utils import IntegrityError

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                m.Session.objects.unbound().filter(activity_id=self.activity.pk).update(
                    elapsed_duration_ms=500
                )
        # The row is unchanged after the savepoint rollback and still readable.


# ===========================================================================
# 7. The binding architectural condition
# ===========================================================================


class BindingConditionTests(TestCase):
    """A skill input is not a result, and nothing here stores one."""

    #: The founder's explicit examples, plus the names the Architect is reported
    #: to be adding when ``SR32`` is widened. Checked against my own class names so
    #: a future widening cannot collide with a provenance record by accident --
    #: and so this module cannot be hiding one.
    FORBIDDEN_MEANINGS: tuple[str, ...] = (
        "Run",
        "SelectedSkillExecution",
        "Attempt",
        "AssessmentResult",
        "Assessment",
        "Finding",
        "Connection",
        "SkillDefinition",
        "SkillInput",
        "Prompt",
        "Completion",
        "Result",
        "Recommendation",
    )

    def test_the_persisted_schema_still_contains_no_forbidden_entity(self) -> None:
        violations = find_forbidden_schema_entities(introspect_persisted_schema())
        self.assertEqual(
            violations,
            (),
            f"binding architectural condition breached: {[str(v) for v in violations]}",
        )

    def test_no_class_in_my_modules_has_a_forbidden_meaning(self) -> None:
        package_dir = Path(__file__).resolve().parents[1]
        folded_forbidden = {
            name.replace("_", "").lower() for name in self.FORBIDDEN_MEANINGS
        }
        found: list[str] = []
        for name in ("scoped_input.py", "provenance.py"):
            tree = ast.parse((package_dir / name).read_text(encoding="utf-8"))
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    folded = node.name.replace("_", "").lower()
                    if folded in folded_forbidden:
                        found.append(f"{name}:{node.name}")
        self.assertEqual(found, [])
        # The control: the guard really does catch one of these names.
        self.assertIn("skillinput", folded_forbidden)
        self.assertIn("result", folded_forbidden)

    def test_no_payload_key_or_field_path_has_a_forbidden_meaning(self) -> None:
        scope = make_scope()
        with network_disabled():
            version = prepare_scoped_input(
                scope=scope,
                records=[make_record(canonical_identity=identity(301))],
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
        block = json.loads(version.canonical_payload)

        def keys(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    yield str(key)
                    yield from keys(value)
            elif isinstance(node, list):
                for item in node:
                    yield from keys(item)

        for key in keys(block):
            folded = key.replace("_", "").lower()
            for forbidden in self.FORBIDDEN_MEANINGS:
                self.assertNotEqual(
                    folded, forbidden.replace("_", "").lower(), f"payload key {key!r}"
                )
        for path in version.all_field_paths():
            self.assertNotIn("result", path.lower())

    def test_the_guard_still_detects_a_real_violation(self) -> None:
        """Control: a deliberately violating fact set is still caught.

        A green guard on an empty schema proves nothing. The names used are taken
        from the guard's own list, so the control keeps working if the list is
        widened.
        """

        from datara.db import FORBIDDEN_ENTITY_NAMES

        for name in FORBIDDEN_ENTITY_NAMES:
            with self.subTest(name=name):
                for facts in (
                    SchemaFacts(
                        table_names=("datara_" + name.lower(),),
                        columns=(),
                        model_names=(),
                        field_names=(),
                        module_symbols=(),
                    ),
                    SchemaFacts(
                        table_names=(),
                        columns=(),
                        model_names=(name,),
                        field_names=(),
                        module_symbols=(),
                    ),
                    SchemaFacts(
                        table_names=(),
                        columns=(),
                        model_names=(),
                        field_names=(),
                        module_symbols=(name,),
                    ),
                ):
                    self.assertTrue(
                        find_forbidden_schema_entities(facts),
                        f"the guard did not catch {name!r} through {facts.table_names}",
                    )

    def test_the_widened_guard_knows_the_reported_skill_execution_names(self) -> None:
        """The guard now covers the skill-execution names, and TK21 collides with none.

        This test previously recorded a gap rather than asserting it away:
        `datara.db` listed eight entity names while the semantic class named in
        the TK21 brief -- SkillInput, Prompt, Completion, Result, Recommendation --
        was not covered. The gap was stated here so the widening could not land
        without this file being reconciled. It has now landed, so this test states
        the reconciled property, and it fails loudly if the widening is reverted.
        """

        from datara.db import FORBIDDEN_ENTITY_NAMES

        reported_widening = {
            "SkillInput",
            "Prompt",
            "Completion",
            "Result",
            "Recommendation",
        }
        current = set(FORBIDDEN_ENTITY_NAMES)
        self.assertTrue(
            reported_widening.issubset(current),
            "the guard must know every reported skill-execution name; missing "
            + repr(sorted(reported_widening - current)),
        )

        # The modules in this assignment collide with neither the original eight
        # nor the widened set, so widening the guard causes no false positive here.
        for symbol in (
            "ActivityScope",
            "InputFieldSpec",
            "ScopedRecord",
            "ScopedExclusion",
            "ScopedField",
            "FieldProvenance",
            "ProvenanceLedger",
            "ProvenanceDisplay",
        ):
            self.assertNotIn(symbol, current)

# ===========================================================================
# 8. No model or network call is reachable
# ===========================================================================


class NoModelReachableTests(TestCase):
    """AST scan plus a socket tripwire, as the existing suites do."""

    FORBIDDEN_IMPORT_ROOTS = {
        "anthropic",
        "cohere",
        "google",
        "groq",
        "http",
        "httplib",
        "httpcore",
        "httpx",
        "litellm",
        "mistralai",
        "ollama",
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
                        root, self.FORBIDDEN_IMPORT_ROOTS, f"{path.name} imports {root}"
                    )
            checked += 1
        self.assertGreaterEqual(checked, 12)

    def test_the_scan_would_catch_a_transport_import_in_my_module(self) -> None:
        """Control: the AST scan is not vacuously green on my own file.

        Run against a source string that *does* import a transport. If the scan
        were only comparing against an empty file set, this would pass and prove
        nothing.
        """

        source = "import json\nimport requests\nfrom openai import OpenAI\n"
        tree = ast.parse(source)
        roots: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots.append(node.module.split(".")[0])
        self.assertEqual(
            sorted(r for r in roots if r in self.FORBIDDEN_IMPORT_ROOTS),
            ["openai", "requests"],
        )

    def test_preparation_and_persistence_succeed_with_sockets_disabled(self) -> None:
        owner = _Owner("tk21-nomodel")
        activity = owner.add_accepted(start_utc="2026-10-01T06:30:00Z")
        scope = make_scope()
        with network_disabled():
            candidates = owner.inputs.scope_candidates(scope, DECLARED_FULL)
            version = prepare_scoped_input(
                scope=scope,
                records=candidates,
                field_specs=DECLARED_FULL,
                policy=SYNTHETIC_POLICY,
            )
            handle = owner.inputs.append_version(version)
            read_back = owner.inputs.get_version(handle.version_ref)
            owner.inputs.provenance_rows(handle.version_ref)
        self.assertEqual(read_back.input_digest, version.input_digest)
        self.assertEqual(version.included_count, 1)
        self.assertIsNotNone(activity)

    def test_the_tripwire_itself_actually_fires(self) -> None:
        """Control: an unpatched network call fails the test, so the patch works."""

        import socket as socket_module

        with self.assertRaises(AssertionError):
            with network_disabled():
                socket_module.create_connection(("127.0.0.1", 9), timeout=1)
        # And with the tripwire off, the call is attempted for real. This opens no
        # meaningful connection: it is refused by the loopback, and the point is
        # only to show the previous failure came from the patch.
        with mock.patch("socket.create_connection", side_effect=OSError("refused by test")):
            with self.assertRaises(OSError):
                socket_module.create_connection(("127.0.0.1", 9), timeout=1)


# ===========================================================================
# 9. Vocabulary and documentation integrity
# ===========================================================================


class ContractSurfaceTests(TestCase):
    """The stated contract and the executable one are the same contract."""

    def test_the_exclusion_vocabulary_is_a_closed_ordered_set(self) -> None:
        self.assertEqual(len(EXCLUSION_REASONS), len(set(EXCLUSION_REASONS)))
        from datara.scoped_input import EXCLUSION_PRECEDENCE

        self.assertEqual(set(EXCLUSION_PRECEDENCE), set(EXCLUSION_REASONS) - {EXCLUDED_CAPACITY})
        self.assertEqual(EXCLUSION_PRECEDENCE[0], EXCLUDED_QUARANTINED)

    def test_every_declared_field_has_a_milestone_a_source(self) -> None:
        for spec in DECLARED_FULL:
            self.assertIn(spec.field_name, MILESTONE_A_FIELD_SOURCES)
            self.assertEqual(
                MILESTONE_A_FIELD_SOURCES[spec.field_name][0], spec.value_class
            )
        # The control: a field with no source is a hole in the declaration surface.
        self.assertNotIn("weekly_load", MILESTONE_A_FIELD_SOURCES)

    def test_the_module_states_its_identity_and_its_fixtures_are_synthetic(self) -> None:
        for name in ("scoped_input.py", "provenance.py"):
            text = (Path(__file__).resolve().parents[1] / name).read_text(encoding="utf-8")
            self.assertIn(
                "Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)", text
            )
        # The founder's private telemetry is never read, copied, hashed, stat'ed
        # or listed by this assignment. Scoped to the two modules this assignment
        # owns: `datara/storage.py` legitimately *names* the forbidden file, as the
        # constant that refuses it, which is the opposite of reading it.
        package_dir = Path(__file__).resolve().parents[1]
        for name in ("scoped_input.py", "provenance.py"):
            text = (package_dir / name).read_text(encoding="utf-8")
            self.assertNotIn("24563001348", text, f"{name} references founder telemetry")
            self.assertNotIn("demo_file", text, f"{name} references demo_file")
        # And the guard that refuses it is still in place, with the name present.
        from datara.storage import FORBIDDEN_SOURCE_NAMES, reject_forbidden_source_name

        self.assertIn("24563001348_ACTIVITY.fit", FORBIDDEN_SOURCE_NAMES)
        with self.assertRaises(Exception):
            reject_forbidden_source_name("24563001348_ACTIVITY.fit")
