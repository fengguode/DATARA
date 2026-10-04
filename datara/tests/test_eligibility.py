"""Deterministic, model-free eligibility engine: E1-E8 with mutation controls.

TK04 / TK44 core; CUS05; SR10, SR11. GitHub issue #379.

WHAT THESE TESTS ARE FOR
------------------------

Each acceptance case E1-E8 from the assignment has at least one test whose name
states the mutation that makes it fail. A case never seen failing is not
evidence, so the mutation is documented in the test docstring and was executed
against this file during the assignment; the recorded results are in the Worker's
report to the Primary Coordinator.

E7 is the one that cannot be faked inside a single interpreter: two calls in one
process cannot distinguish true determinism from interpreter state, so the
cross-process case spawns real subprocesses with different ``PYTHONHASHSEED``
values and compares canonical **bytes**.

E8 is machine-checked rather than asserted in prose, by two independent means:
an AST import allowlist over the module's own source, and a runtime socket patch
around every evaluation path. The import allowlist is the stronger of the two,
because it inspects what the module *can* reach rather than what it did.

These tests need no database, no server and no provider. They are pure logic,
which is the point of the engine: SR11 requires unmet requirements to be
identified without invoking a model, so the path that decides eligibility must be
runnable and checkable with nothing else present.

Attribution: Worker — Torsten Maier_space-bunny-free-xhigh_OpenCode (AI agent)
"""

from __future__ import annotations

import ast
import dataclasses
import json
import os
import pathlib
import subprocess
import sys
import unittest
from contextlib import contextmanager
from unittest import mock

from datara.eligibility import (
    CONTRACT_VERSION,
    COMPARATOR_AT_LEAST,
    COMPARATOR_AT_MOST,
    COMPARATOR_EQUALS,
    COMPARATOR_PRESENT,
    ENGINE_VERSION,
    KIND_HISTORY_COVERAGE,
    KIND_MANDATORY_FIELD,
    KIND_QUALITY_LIMIT,
    KIND_ORDER,
    REASON_DETAILS,
    REASON_MANDATORY_FIELD_ABSENT,
    REASON_MANDATORY_FIELD_INVALID,
    REASON_HISTORY_COVERAGE_NOT_MET,
    REASON_QUALITY_LIMIT_NOT_MET,
    REASON_REQUIREMENT_NOT_EVALUABLE,
    REASON_REQUIREMENT_SATISFIED,
    REASON_RULE_SET_EMPTY,
    SUPPORTED_COMPARATORS,
    SUPPORTED_KINDS,
    SUPPORTED_VALUE_TYPES,
    UNMET_KEYS,
    VALUE_ANY,
    VALUE_FLAG,
    VALUE_INTEGER,
    VALUE_NUMBER,
    VALUE_TEXT,
    EligibilityContractError,
    EligibilityDecision,
    EligibilityRefusal,
    EligibilityRequirement,
    evaluate_eligibility,
    is_execution_available,
    require_eligible,
    rule_set_digest,
    unmet_codes,
)

RULE_SET = "synthetic-rule-set/1"

#: Modules the engine is permitted to import. Every entry is inert: a pure
#: computation helper or an existing canonical serializer. Anything absent from
#: this set that could open a socket, read a credential, touch a clock or reach a
#: model is an E8 failure, and the test asserts this set exactly rather than
#: testing a denylist that a new import could slip past.
#: The top-level module names the engine is permitted to import. Every entry is
#: inert: a pure computation helper, or the canonical serializer. The check is on
#: module *roots*, because that is the granularity at which a capability is
#: acquired -- ``from datara.normalization import x`` acquires the ``datara``
#: package, and the allowed member is asserted separately below.
PERMITTED_IMPORTS = frozenset(
    {
        "__future__",
        "math",
        "collections",
        "dataclasses",
        "datara",
    }
)

#: The exact DATARA members the engine may import. Anything that computes
#: observations or touches persistence is absent by construction.
PERMITTED_DATARA_IMPORTS = frozenset({"datara.normalization"})

#: Substrings that must not appear as an imported module or imported name. A
#: second, independent check: the allowlist above is the precise one, and this one
#: fails loudly if someone adds `import requests` and also relaxes the allowlist.
FORBIDDEN_IMPORT_TOKENS = (
    "socket",
    "urllib",
    "http",
    "requests",
    "httpx",
    "aiohttp",
    "ssl",
    "ftplib",
    "smtplib",
    "telnetlib",
    "asyncio",
    "subprocess",
    "os",
    "sys",
    "random",
    "time",
    "datetime",
    "openai",
    "anthropic",
    "boto",
    "google",
    "cohere",
    "mistral",
    "ollama",
    "litellm",
    "credential",
    "secret",
    "token",
    "api_key",
    "django",
    "psycopg",
)

#: A requirement kind that is deliberately absent from ``SUPPORTED_KINDS``. Used
#: for E6: it names a capability this engine has never implemented, so it must be
#: reported unmet rather than quietly satisfied.
UNSEEN_KIND = "model_derived_readiness_index"

#: A comparator that is deliberately absent from ``SUPPORTED_COMPARATORS``, for
#: the same reason. Note it must be constructible: the declaration validator
#: deliberately does not reject it, because a requirement the engine cannot
#: evaluate must still be *reported*, not refused where it cannot be explained.
UNSEEN_COMPARATOR = "approximately_equal_within_tolerance"

#: A declared value type that is deliberately absent from
#: ``SUPPORTED_VALUE_TYPES``.
UNSEEN_VALUE_TYPE = "iso8601_instant"

REQUIREMENTS = (
    EligibilityRequirement(
        requirement_id="REQ-MANDATORY-SPORT",
        kind=KIND_MANDATORY_FIELD,
        source_key="sport",
        description="the scope has one recognised sport",
        comparator=COMPARATOR_PRESENT,
        declared_value_type=VALUE_TEXT,
        permitted_values=("running", "cycling"),
        unit="sport_code",
    ),
    EligibilityRequirement(
        requirement_id="REQ-MANDATORY-HEART-RATE",
        kind=KIND_MANDATORY_FIELD,
        source_key="heart_rate",
        description="the scope has a recorded heart rate",
        comparator=COMPARATOR_PRESENT,
        declared_value_type=VALUE_INTEGER,
        unit="beats_per_minute",
    ),
    EligibilityRequirement(
        requirement_id="REQ-COVERAGE-DAYS",
        kind=KIND_HISTORY_COVERAGE,
        source_key="covered_days",
        description="the scope covers the declared number of complete UTC days",
        comparator=COMPARATOR_AT_LEAST,
        required_value=28,
        declared_value_type=VALUE_INTEGER,
        unit="day_count",
    ),
    EligibilityRequirement(
        requirement_id="REQ-QUALITY-INVALID-RECORDS",
        kind=KIND_QUALITY_LIMIT,
        source_key="invalid_record_count",
        description="no more than the permitted number of invalid records",
        comparator=COMPARATOR_AT_MOST,
        required_value=5,
        declared_value_type=VALUE_INTEGER,
        unit="count",
    ),
)

SATISFIED_OBSERVATIONS = {
    "sport": "running",
    "heart_rate": 150,
    "covered_days": 28,
    "invalid_record_count": 0,
}


def decide(observations, requirements=REQUIREMENTS, rule_set_version=RULE_SET, rule_version=ENGINE_VERSION):
    return evaluate_eligibility(
        observations=observations,
        requirements=requirements,
        rule_set_version=rule_set_version,
        rule_version=rule_version,
    )


def only(decision):
    """The single unmet explanation, asserting there is exactly one."""

    assert len(decision.unmet_requirements) == 1, decision.unmet_requirements
    return decision.unmet_requirements[0]


@contextmanager
def network_disabled():
    """Make any outbound connection an immediate, loud failure.

    The executable meaning of "model access disabled" for SR11. It removes the
    transport a model call would need, so the property under test is that
    eligibility never reaches for one. Same helper shape as
    ``datara/tests/test_normalization.py`` and ``test_scoped_input.py``,
    duplicated rather than imported because this assignment owns new files only.
    """

    def blocked(*args, **kwargs):
        raise AssertionError("outbound connection attempted on a model-free path")

    with mock.patch("socket.socket", side_effect=blocked), mock.patch(
        "socket.create_connection", side_effect=blocked
    ), mock.patch("socket.getaddrinfo", side_effect=blocked), mock.patch(
        "urllib.request.urlopen", side_effect=blocked
    ), mock.patch("http.client.HTTPConnection.connect", side_effect=blocked):
        yield


# ===========================================================================
# E1 -- every requirement satisfied
# ===========================================================================


class E1SatisfiedTests(unittest.TestCase):
    """E1: every requirement satisfied -> eligible, with the satisfied set reported."""

    def test_all_requirements_satisfied_is_eligible_and_reports_the_satisfied_set(self) -> None:
        """Mutation: drop the ``satisfied_requirements`` projection.

        Fails here on ``KeyError``/empty tuple. Without this assertion an engine
        that returned ``eligible=True`` while silently discarding which
        requirements were met would still pass every other case.
        """

        with network_disabled():
            decision = decide(SATISFIED_OBSERVATIONS)

        self.assertTrue(decision.eligible)
        self.assertIsNone(decision.decision_reason_code)
        self.assertEqual(decision.unmet_requirements, ())
        self.assertEqual(
            decision.satisfied_requirements,
            ("REQ-COVERAGE-DAYS", "REQ-MANDATORY-HEART-RATE", "REQ-MANDATORY-SPORT",
             "REQ-QUALITY-INVALID-RECORDS"),
        )
        self.assertEqual(unmet_codes(decision), ())
        self.assertTrue(is_execution_available(decision))
        self.assertIs(require_eligible(decision), decision)

    def test_each_requirement_reports_satisfied_independently(self) -> None:
        """The satisfied set is per-requirement, not a single all-or-nothing flag.

        Mutation: report only the *first* satisfied requirement, or report the
        satisfied set as the requirement count. Fails here.
        """

        for requirement in REQUIREMENTS:
            with self.subTest(requirement_id=requirement.requirement_id):
                single = decide(SATISFIED_OBSERVATIONS, requirements=[requirement])
                self.assertTrue(single.eligible)
                self.assertEqual(single.satisfied_requirements, (requirement.requirement_id,))


# ===========================================================================
# E2 -- one mandatory field absent
# ===========================================================================


class E2AbsentMandatoryFieldTests(unittest.TestCase):
    """E2: a mandatory field absent -> ineligible, naming that requirement and field."""

    def test_absent_mandatory_field_names_the_requirement_and_the_field(self) -> None:
        """Mutation: make an unsupplied source key read as ``None``-but-present.

        The engine already treats both as unmet, so this case is additionally
        guarded by the distinct ``reason_detail`` assertion below. Mutating the
        *code* selection in ``_ABSENCE_BY_KIND`` back to the generic unevaluable
        code makes this fail, which is what pins E2's code.
        """

        observations = dict(SATISFIED_OBSERVATIONS)
        del observations["heart_rate"]

        with network_disabled():
            decision = decide(observations)

        self.assertFalse(decision.eligible)
        self.assertFalse(is_execution_available(decision))
        self.assertEqual(unmet_codes(decision), ("REQ-MANDATORY-HEART-RATE:MANDATORY_FIELD_ABSENT",))
        item = only(decision)
        self.assertEqual(item["requirement_id"], "REQ-MANDATORY-HEART-RATE")
        self.assertEqual(item["reason_code"], REASON_MANDATORY_FIELD_ABSENT)
        self.assertEqual(item["reason_detail"], "observation_not_supplied")
        self.assertEqual(item["source_key"], "heart_rate")
        self.assertEqual(item["kind"], KIND_MANDATORY_FIELD)
        self.assertFalse(item["observed_supplied"])
        self.assertFalse(item["observed_present"])
        self.assertIsNone(item["observed_value"])
        self.assertEqual(item["description"], "the scope has a recorded heart rate")
        self.assertEqual(item["unit"], "beats_per_minute")

    def test_supplied_null_is_absent_but_a_different_explanation(self) -> None:
        """Mutation: collapse ``observation_is_null`` into ``observation_not_supplied``.

        E2 must distinguish "the key was never there" from "the key was there and
        its value is null"; a caller needs to know which, to know whether the
        source or the value is missing.
        """

        observations = dict(SATISFIED_OBSERVATIONS, heart_rate=None)

        with network_disabled():
            decision = decide(observations)

        item = only(decision)
        self.assertFalse(decision.eligible)
        self.assertEqual(item["reason_code"], REASON_MANDATORY_FIELD_ABSENT)
        self.assertEqual(item["reason_detail"], "observation_is_null")
        self.assertTrue(item["observed_supplied"])
        self.assertFalse(item["observed_present"])

    def test_refusal_carries_the_unmet_requirements_and_blocks_execution(self) -> None:
        """SR11's "unavailable for execution" is a raised value, not a flag."""

        observations = dict(SATISFIED_OBSERVATIONS)
        del observations["sport"]
        decision = decide(observations)

        with self.assertRaises(EligibilityRefusal) as caught:
            require_eligible(decision)

        self.assertIs(caught.exception.decision, decision)
        self.assertIn("REQ-MANDATORY-SPORT:MANDATORY_FIELD_ABSENT", str(caught.exception))
        self.assertEqual(
            [item["requirement_id"] for item in caught.exception.decision.unmet_requirements],
            ["REQ-MANDATORY-SPORT"],
        )


# ===========================================================================
# E3 -- present but invalid, distinguished from E2 by a stable reason code
# ===========================================================================


class E3InvalidMandatoryFieldTests(unittest.TestCase):
    """E3: present-but-invalid is a different stable code from E2's absence."""

    def test_wrong_type_is_invalid_not_absent(self) -> None:
        """Mutation: treat a type mismatch as absence.

        Changing ``_INVALID_BY_KIND[KIND_MANDATORY_FIELD]`` to
        ``MANDATORY_FIELD_ABSENT`` fails here, and E2's cases keep passing. That
        separation is the whole content of E3.
        """

        with network_disabled():
            decision = decide(dict(SATISFIED_OBSERVATIONS, heart_rate="150"))

        self.assertFalse(decision.eligible)
        item = only(decision)
        self.assertEqual(item["reason_code"], REASON_MANDATORY_FIELD_INVALID)
        self.assertNotEqual(item["reason_code"], REASON_MANDATORY_FIELD_ABSENT)
        self.assertEqual(item["reason_detail"], "type_mismatch")
        self.assertTrue(item["observed_supplied"])
        self.assertTrue(item["observed_present"])
        self.assertEqual(item["observed_value"], "150")

    def test_out_of_domain_is_invalid_with_its_own_detail(self) -> None:
        """Mutation: drop the ``permitted_values`` check from ``_validate_observed``.

        Fails here; every other E3 case still passes, because a type mismatch is
        caught earlier. The domain is a separate control from the type.
        """

        with network_disabled():
            decision = decide(dict(SATISFIED_OBSERVATIONS, sport="swimming"))

        item = only(decision)
        self.assertEqual(item["reason_code"], REASON_MANDATORY_FIELD_INVALID)
        self.assertEqual(item["reason_detail"], "outside_declared_domain")
        self.assertEqual(item["observed_value"], "swimming")
        self.assertEqual(item["unit"], "sport_code")

    def test_boolean_does_not_satisfy_an_integer_requirement(self) -> None:
        """Mutation: use ``isinstance`` instead of ``type(...) is int``.

        ``bool`` is a subclass of ``int``, so an ``isinstance`` check lets
        ``True`` satisfy ``heart_rate`` as the value 1. This test is the only one
        that catches that substitution, and it is why the engine compares exact
        types rather than nominal ones.
        """

        with network_disabled():
            decision = decide(dict(SATISFIED_OBSERVATIONS, heart_rate=True))

        item = only(decision)
        self.assertEqual(item["reason_code"], REASON_MANDATORY_FIELD_INVALID)
        self.assertEqual(item["reason_detail"], "type_mismatch")
        self.assertIs(item["observed_value"], True)

    def test_non_finite_number_is_invalid_rather_than_serialised(self) -> None:
        """Mutation: allow NaN through ``VALUE_NUMBER``.

        ``json.dumps(..., allow_nan=False)`` would then raise inside the canonical
        payload, so the decision would be replaced by a serialisation traceback
        rather than an explanation.
        """

        requirement = EligibilityRequirement(
            requirement_id="REQ-NUMERIC",
            kind=KIND_QUALITY_LIMIT,
            source_key="ratio",
            description="a finite ratio",
            comparator=COMPARATOR_AT_LEAST,
            required_value=0.0,
            declared_value_type=VALUE_NUMBER,
        )

        with network_disabled():
            decision = decide({"ratio": float("nan")}, requirements=[requirement])

        item = only(decision)
        self.assertEqual(item["reason_code"], REASON_REQUIREMENT_NOT_EVALUABLE)
        self.assertEqual(item["reason_detail"], "non_finite_number")

    def test_each_declared_value_type_accepts_its_own_and_rejects_its_neighbours(self) -> None:
        """Each declared type rejects the neighbouring type, and accepts its own.

        Mutation: widen any single check in ``_validate_observed``. The rejection
        half is asserted per neighbouring type, so a widened ``isinstance`` is
        caught even when the acceptance half still passes.
        """

        # `False` is a valid `flag` value and `0` is a valid `integer`; each case
        # lists only the neighbouring types, which must be rejected.
        cases = (
            (VALUE_INTEGER, 7, ("7", True, 7.0)),
            (VALUE_TEXT, "running", (7, "", b"running")),
            (VALUE_FLAG, True, (1, 0, "true")),
        )
        for declared, good, bad_values in cases:
            requirement = EligibilityRequirement(
                requirement_id="REQ-TYPED",
                kind=KIND_MANDATORY_FIELD,
                source_key="observed",
                description="a typed observation requirement",
                comparator=COMPARATOR_PRESENT,
                declared_value_type=declared,
            )
            with self.subTest(declared=declared, value=repr(good)):
                with network_disabled():
                    self.assertTrue(decide({"observed": good},
                                           requirements=[requirement]).eligible)
            for bad in bad_values:
                with self.subTest(declared=declared, value=repr(bad)):
                    with network_disabled():
                        decision = decide({"observed": bad}, requirements=[requirement])
                    self.assertFalse(decision.eligible, f"{declared} accepted {bad!r}")
                    self.assertEqual(decision.unmet_requirements[0]["reason_detail"],
                                     "type_mismatch")


# ===========================================================================
# E4 -- coverage below the required window
# ===========================================================================


class E4CoverageTests(unittest.TestCase):
    """E4: coverage below the window -> ineligible, reporting observed and required."""

    def test_short_coverage_reports_observed_and_required(self) -> None:
        """Mutation: map ``at_least`` onto the quality-limit code.

        Coverage and quality would become indistinguishable to a caller, and E4
        would silently become E5. The code is chosen by *kind*, never by
        comparator, which is exactly what this test pins.
        """

        with network_disabled():
            decision = decide(dict(SATISFIED_OBSERVATIONS, covered_days=14))

        self.assertFalse(decision.eligible)
        item = only(decision)
        self.assertEqual(item["requirement_id"], "REQ-COVERAGE-DAYS")
        self.assertEqual(item["kind"], KIND_HISTORY_COVERAGE)
        self.assertEqual(item["reason_code"], REASON_HISTORY_COVERAGE_NOT_MET)
        self.assertNotEqual(item["reason_code"], REASON_QUALITY_LIMIT_NOT_MET)
        self.assertEqual(item["reason_detail"], "below_required_window")
        self.assertEqual(item["observed_value"], 14)
        self.assertEqual(item["required_value"], 28)
        self.assertEqual(item["comparator"], COMPARATOR_AT_LEAST)
        self.assertEqual(item["unit"], "day_count")

    def test_coverage_exactly_at_the_window_is_eligible(self) -> None:
        """Mutation: use ``>`` instead of ``>=``.

        The boundary is where an off-by-one hides, so it is asserted directly at
        the requirement's own declared value rather than at an arbitrary number.
        """

        boundary = REQUIREMENTS[2].required_value
        with network_disabled():
            self.assertTrue(decide(dict(SATISFIED_OBSERVATIONS, covered_days=boundary)).eligible)
            self.assertFalse(
                decide(dict(SATISFIED_OBSERVATIONS, covered_days=boundary - 1)).eligible)

    def test_coverage_absent_is_unmet_not_silently_satisfied(self) -> None:
        """A missing coverage observation is unmet, whatever its kind.

        Mutation: return ``True`` for a non-mandatory unevaluable requirement.
        E6 covers the same control for an unknown kind; this case proves it for a
        *recognised* kind whose observation is simply absent, which is the common
        real-world case.
        """

        observations = dict(SATISFIED_OBSERVATIONS)
        del observations["covered_days"]

        with network_disabled():
            decision = decide(observations)

        item = only(decision)
        self.assertEqual(item["reason_code"], REASON_REQUIREMENT_NOT_EVALUABLE)
        self.assertEqual(item["reason_detail"], "observation_not_supplied")
        self.assertFalse(decision.eligible)


# ===========================================================================
# E5 -- quality limit breached
# ===========================================================================


class E5QualityLimitTests(unittest.TestCase):
    """E5: quality limit breached -> ineligible, reporting the limit and the value."""

    def test_breached_quality_limit_reports_limit_and_observed(self) -> None:
        """Mutation: invert ``at_most`` to ``at_least``.

        A breach would become satisfied. The observed value (9) is above the
        declared limit (5), so the direction of the comparison is what the test
        actually observes.
        """

        with network_disabled():
            decision = decide(dict(SATISFIED_OBSERVATIONS, invalid_record_count=9))

        self.assertFalse(decision.eligible)
        item = only(decision)
        self.assertEqual(item["requirement_id"], "REQ-QUALITY-INVALID-RECORDS")
        self.assertEqual(item["kind"], KIND_QUALITY_LIMIT)
        self.assertEqual(item["reason_code"], REASON_QUALITY_LIMIT_NOT_MET)
        self.assertNotEqual(item["reason_code"], REASON_HISTORY_COVERAGE_NOT_MET)
        self.assertEqual(item["reason_detail"], "above_permitted_limit")
        self.assertEqual(item["observed_value"], 9)
        self.assertEqual(item["required_value"], 5)
        self.assertEqual(item["comparator"], COMPARATOR_AT_MOST)

    def test_quality_boundary_is_inclusive(self) -> None:
        """Mutation: use ``<`` instead of ``<=`` on ``at_most``.

        Asserted at the requirement's own declared limit, so the test cannot pass
        by accident on an arbitrary number.
        """

        boundary = REQUIREMENTS[3].required_value
        with network_disabled():
            self.assertTrue(
                decide(dict(SATISFIED_OBSERVATIONS, invalid_record_count=boundary)).eligible)
            self.assertFalse(
                decide(dict(SATISFIED_OBSERVATIONS, invalid_record_count=boundary + 1)).eligible)

    def test_lower_bound_quality_requirement_reports_below_required_minimum(self) -> None:
        """A quality limit may also be a minimum; the detail must name the direction.

        Mutation: reuse ``above_permitted_limit`` for every quality failure. A
        caller reading "above the permitted limit" for a value that fell *below*
        the minimum would be told the opposite of what happened.
        """

        requirement = EligibilityRequirement(
            requirement_id="REQ-QUALITY-MIN-COVERAGE",
            kind=KIND_QUALITY_LIMIT,
            source_key="gps_ratio",
            description="at least the permitted GPS sample ratio",
            comparator=COMPARATOR_AT_LEAST,
            required_value=80,
            declared_value_type=VALUE_INTEGER,
            unit="percent",
        )

        with network_disabled():
            decision = decide({"gps_ratio": 40}, requirements=[requirement])

        item = only(decision)
        self.assertEqual(item["reason_code"], REASON_QUALITY_LIMIT_NOT_MET)
        self.assertEqual(item["reason_detail"], "below_required_minimum")
        self.assertEqual(item["observed_value"], 40)
        self.assertEqual(item["required_value"], 80)


# ===========================================================================
# E6 -- unknown or unevaluable requirement is unmet, never assumed satisfied
# ===========================================================================


class E6FailClosedTests(unittest.TestCase):
    """E6: the fail-closed core. Every case here names something never seen."""

    def test_unknown_requirement_kind_is_unmet(self) -> None:
        """E6's central case: a requirement kind this engine has never seen.

        Proven with ``UNSEEN_KIND``, asserted absent from ``SUPPORTED_KINDS`` so
        the test cannot rot into testing nothing. Mutation: treat an unrecognised
        kind as satisfied, or drop the ``kind not in SUPPORTED_KINDS`` guard. Both
        make this fail while every other case still passes.
        """

        self.assertNotIn(UNSEEN_KIND, SUPPORTED_KINDS)

        requirement = EligibilityRequirement(
            requirement_id="REQ-MODEL-DERIVED-INDEX",
            kind=UNSEEN_KIND,
            source_key="readiness_index",
            description="a requirement this engine has never seen",
            comparator=COMPARATOR_PRESENT,
        )

        with network_disabled():
            decision = decide({"readiness_index": 1}, requirements=[requirement])

        self.assertFalse(decision.eligible)
        self.assertEqual(decision.satisfied_requirements, ())
        item = only(decision)
        self.assertEqual(item["reason_code"], REASON_REQUIREMENT_NOT_EVALUABLE)
        self.assertEqual(item["reason_detail"], "unknown_requirement_kind")
        self.assertEqual(item["kind"], UNSEEN_KIND)
        self.assertFalse(is_execution_available(decision))
        with self.assertRaises(EligibilityRefusal):
            require_eligible(decision)

    def test_unknown_comparator_is_unmet(self) -> None:
        """Mutation: move the ``comparator not in SUPPORTED_COMPARATORS`` guard
        after the comparison, so an unknown comparator falls through to a
        comparison that happens to pass.
        """

        self.assertNotIn(UNSEEN_COMPARATOR, SUPPORTED_COMPARATORS)

        requirement = EligibilityRequirement(
            requirement_id="REQ-APPROXIMATE",
            kind=KIND_QUALITY_LIMIT,
            source_key="ratio",
            description="a requirement using an unrecognised comparator",
            comparator=UNSEEN_COMPARATOR,
            required_value=1,
        )

        with network_disabled():
            decision = decide({"ratio": 1}, requirements=[requirement])

        item = only(decision)
        self.assertEqual(item["reason_code"], REASON_REQUIREMENT_NOT_EVALUABLE)
        self.assertEqual(item["reason_detail"], "unknown_comparator")

    def test_unknown_declared_value_type_is_unmet(self) -> None:
        """Mutation: remove the ``declared_value_type`` membership guard."""

        self.assertNotIn(UNSEEN_VALUE_TYPE, SUPPORTED_VALUE_TYPES)

        requirement = EligibilityRequirement(
            requirement_id="REQ-INSTANT",
            kind=KIND_MANDATORY_FIELD,
            source_key="started_at",
            description="a requirement declaring a type this engine cannot check",
            comparator=COMPARATOR_PRESENT,
            declared_value_type=UNSEEN_VALUE_TYPE,
        )

        with network_disabled():
            decision = decide({"started_at": "2026-01-01T00:00:00Z"},
                              requirements=[requirement])

        self.assertFalse(decision.eligible)
        self.assertEqual(only(decision)["reason_code"], REASON_REQUIREMENT_NOT_EVALUABLE)
        self.assertEqual(only(decision)["reason_detail"], "unknown_declared_value_type")

    def test_missing_required_value_is_unmet_rather_than_assumed(self) -> None:
        """Mutation: treat a missing ``required_value`` as zero.

        ``at_least`` with an absent bound silently becomes ``>= 0``, which every
        non-negative observation satisfies. The declaration validator deliberately
        does not refuse this, because a requirement the engine cannot evaluate must
        be reported, not rejected where it cannot be explained.
        """

        requirement = EligibilityRequirement(
            requirement_id="REQ-NO-BOUND",
            kind=KIND_HISTORY_COVERAGE,
            source_key="covered_days",
            description="a bound this engine was not given",
            comparator=COMPARATOR_AT_LEAST,
            required_value=None,
        )

        with network_disabled():
            decision = decide({"covered_days": 28}, requirements=[requirement])

        self.assertFalse(decision.eligible)
        self.assertEqual(only(decision)["reason_detail"], "missing_required_value")

    def test_equals_comparing_across_types_is_not_satisfied(self) -> None:
        """Mutation: drop the ``type(observed) is type(required)`` guard.

        ``1 == True`` and ``1 == 1.0`` in Python, so a typed requirement could be
        satisfied by a different type that merely compares equal.
        """

        for observed, required, label in ((1, True, "int_vs_bool"), (1, 1.0, "int_vs_float")):
            with self.subTest(label):
                requirement = EligibilityRequirement(
                    requirement_id="REQ-EXACT",
                    kind=KIND_MANDATORY_FIELD,
                    source_key="value",
                    description="an exact match requirement",
                    comparator=COMPARATOR_EQUALS,
                    required_value=required,
                    declared_value_type=VALUE_ANY,
                )
                with network_disabled():
                    decision = decide({"value": observed}, requirements=[requirement])
                self.assertFalse(decision.eligible, label)

    def test_empty_rule_set_is_ineligible(self) -> None:
        """Mutation: compute ``eligible`` as ``not unmet`` without the
        ``has_requirements`` term, so an empty rule set reads as eligible.

        This is the "no implicit probably-fine" control in its purest form: no
        requirement was declared, so nothing was established.
        """

        with network_disabled():
            decision = decide({}, requirements=())

        self.assertFalse(decision.eligible)
        self.assertEqual(decision.decision_reason_code, REASON_RULE_SET_EMPTY)
        self.assertEqual(decision.unmet_requirements, ())
        self.assertEqual(decision.satisfied_requirements, ())
        self.assertFalse(is_execution_available(decision))
        self.assertEqual(decision.rule_set, ())
        with self.assertRaises(EligibilityRefusal):
            require_eligible(decision)

    def test_an_exception_while_evaluating_one_requirement_is_unmet_and_isolated(self) -> None:
        """Mutation: let the exception propagate out of ``evaluate_eligibility``.

        Then one hostile observation destroys the explanations of every *other*
        requirement too, which is the opposite of "identify unmet requirements".
        The second requirement here is satisfied, and must still be reported as
        satisfied after its neighbour raised.
        """

        class HostileInt(int):
            """A portable scalar whose comparison raises.

            An ``int`` subclass, so it passes every type and portability check and
            reaches the *comparison*, which is what must be guarded. A plainly
            non-scalar object would be refused earlier as
            ``unsupported_observed_type`` and would never exercise this path.
            """

            def __ge__(self, other):
                raise RuntimeError("observation refuses to be compared")

        hostile = EligibilityRequirement(
            requirement_id="REQ-HOSTILE",
            kind=KIND_QUALITY_LIMIT,
            source_key="hostile",
            description="an observation that raises when compared",
            comparator=COMPARATOR_AT_LEAST,
            required_value=1,
            declared_value_type=VALUE_ANY,
        )
        fine = EligibilityRequirement(
            requirement_id="REQ-FINE",
            kind=KIND_HISTORY_COVERAGE,
            source_key="covered_days",
            description="an ordinary coverage requirement",
            comparator=COMPARATOR_AT_LEAST,
            required_value=28,
            declared_value_type=VALUE_INTEGER,
        )

        with network_disabled():
            decision = decide({"hostile": HostileInt(5), "covered_days": 28},
                              requirements=(hostile, fine))

        self.assertFalse(decision.eligible)
        self.assertEqual(decision.satisfied_requirements, ("REQ-FINE",))
        item = only(decision)
        self.assertEqual(item["requirement_id"], "REQ-HOSTILE")
        self.assertEqual(item["reason_code"], REASON_REQUIREMENT_NOT_EVALUABLE)
        self.assertEqual(item["reason_detail"], "evaluation_raised")


# ===========================================================================
# E7 -- determinism across separate processes with different PYTHONHASHSEED
# ===========================================================================


_CHILD = """
import json, os, sys
from datara.eligibility import (
    EligibilityRequirement, evaluate_eligibility, rule_set_digest,
)
payload = json.loads(os.environ['TK04_INPUT'])
requirements = []
for item in payload['requirements']:
    item = dict(item)
    item['permitted_values'] = tuple(item['permitted_values'])
    requirements.append(EligibilityRequirement(**item))
decision = evaluate_eligibility(
    observations=payload['observations'],
    requirements=requirements,
    rule_set_version=payload['rule_set_version'],
)
print(json.dumps({
    'canonical': decision.canonical_bytes().decode('ascii'),
    'digest': decision.rule_set_digest,
    'rule_set_digest': rule_set_digest(payload['rule_set_version'], requirements),
    'eligible': decision.eligible,
    'unmet_ids': [item['requirement_id'] for item in decision.unmet_requirements],
}))
"""


class E7DeterminismTests(unittest.TestCase):
    """E7: byte-identical across separate processes with different hash seeds.

    A single-process repeat cannot distinguish true determinism from interpreter
    state, so this spawns real subprocesses. The child is given its requirements
    in a *different order* from the parent as well, so hash-order dependence and
    caller-order dependence would both show up.
    """

    def _child_input(self, observations):
        return {
            "observations": observations,
            "rule_set_version": RULE_SET,
            "requirements": [
                {
                    "requirement_id": item.requirement_id,
                    "kind": item.kind,
                    "source_key": item.source_key,
                    "description": item.description,
                    "comparator": item.comparator,
                    "required_value": item.required_value,
                    "declared_value_type": item.declared_value_type,
                    "permitted_values": list(item.permitted_values),
                    "unit": item.unit,
                }
                # Reversed, so a report ordered by caller input would differ.
                for item in reversed(REQUIREMENTS)
            ],
        }

    def _run_child(self, payload, seed):
        repo_root = str(pathlib.Path(__file__).resolve().parents[2])
        env = dict(os.environ)
        env["PYTHONPATH"] = repo_root
        env["PYTHONHASHSEED"] = seed
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["TK04_INPUT"] = json.dumps(payload, sort_keys=True)
        completed = subprocess.run(
            [sys.executable, "-X", "utf8", "-c", _CHILD],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=180,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout.strip().splitlines()[-1])

    def _assert_agrees_across_processes(self, observations):
        with network_disabled():
            local = decide(observations)

        local_payload = {
            "canonical": local.canonical_bytes().decode("ascii"),
            "digest": local.rule_set_digest,
            "rule_set_digest": rule_set_digest(RULE_SET, REQUIREMENTS),
            "eligible": local.eligible,
            "unmet_ids": [item["requirement_id"] for item in local.unmet_requirements],
        }

        for seed in ("0", "1", "424242"):
            with self.subTest(seed=seed):
                child = self._run_child(self._child_input(observations), seed)
                self.assertEqual(child, local_payload)

    def test_ineligible_output_is_byte_identical_across_processes_and_hash_seeds(self) -> None:
        """Mutation: order the unmet report by caller input order.

        The parent and the child supply the same requirements in opposite orders,
        so the two canonical payloads diverge and the byte comparison fails. This
        is the ordering half of E7 and it is only observable across processes.
        """

        self._assert_agrees_across_processes(
            dict(SATISFIED_OBSERVATIONS, covered_days=14, invalid_record_count=9,
                 heart_rate="150"))

    def test_eligible_output_is_byte_identical_across_processes_and_hash_seeds(self) -> None:
        """The same control for the eligible path, where the report is empty.

        An eligible decision still emits a rule-set digest and a satisfied set, so
        it is just as exposed to a hash-order or input-order dependence.
        """

        self._assert_agrees_across_processes(dict(SATISFIED_OBSERVATIONS))

    def test_requirement_supply_order_does_not_change_a_single_byte(self) -> None:
        """Mutation: sort by caller input order instead of the declared sort key.

        In-process, so it fails fast and isolates the ordering contract from the
        subprocess machinery.
        """

        forward = decide(SATISFIED_OBSERVATIONS, requirements=REQUIREMENTS)
        backward = decide(SATISFIED_OBSERVATIONS, requirements=tuple(reversed(REQUIREMENTS)))

        self.assertEqual(forward.canonical_bytes(), backward.canonical_bytes())
        self.assertEqual(forward.rule_set_digest, backward.rule_set_digest)

    def test_canonical_payload_is_ascii_and_sorted_keys(self) -> None:
        """Mutation: emit ``json.dumps`` without ``sort_keys``.

        A dict literal's insertion order would then determine the bytes, which
        differs between two constructions of the same decision in different
        versions of the code.
        """

        decision = decide(dict(SATISFIED_OBSERVATIONS, covered_days=14))
        text = decision.canonical_bytes().decode("ascii")
        payload = json.loads(text)

        self.assertEqual(
            text,
            json.dumps(payload, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False),
        )
        self.assertEqual(payload["contract_version"], CONTRACT_VERSION)

    def test_unused_observation_keys_and_warnings_are_deterministic(self) -> None:
        """Mutation: drop the ``sorted()`` from the unused-key derivation.

        ``observations`` is a ``dict``, so unsorted iteration would follow the
        caller's insertion order rather than a declared order. That is invisible
        in a single test that passes the same mapping twice, and visible only
        when the keys are supplied in a different order.
        """

        forward = decide(dict(SATISFIED_OBSERVATIONS, extra_a=1, extra_b=2, extra_c=3))
        shuffled = decide({"extra_c": 3, "extra_b": 2, "extra_a": 1,
                           **SATISFIED_OBSERVATIONS})

        self.assertEqual(forward.unused_observation_keys, ("extra_a", "extra_b", "extra_c"))
        self.assertEqual(forward.unused_observation_keys, shuffled.unused_observation_keys)
        self.assertEqual(forward.warnings, shuffled.warnings)
        self.assertEqual(forward.canonical_bytes(), shuffled.canonical_bytes())

    def test_reported_identifiers_are_in_the_declared_total_order(self) -> None:
        """Mutation: sort only by ``requirement_id``, dropping the other components.

        With the current fixtures the order is already ascending by id, so this
        test pins the *documented* order rather than an accident of the data. A
        requirement whose id sorts differently from its tuple is what would expose
        the weaker key.
        """

        decision = decide(dict(SATISFIED_OBSERVATIONS, covered_days=14, invalid_record_count=9))
        order = [
            (item["requirement_id"], item["kind"], item["source_key"])
            for item in decision.unmet_requirements
        ]
        self.assertEqual(order, sorted(order))


# ===========================================================================
# E8 -- no provider SDK, socket or network egress on any path
# ===========================================================================


class E8ModelFreeTests(unittest.TestCase):
    """E8: machine-checked absence of any egress path, by two independent means."""

    def test_module_imports_exactly_the_permitted_allowlist(self) -> None:
        """E8's strongest form: inspect what the module *can* reach.

        Mutation: add ``import requests`` or ``import os`` to the engine. This
        fails immediately, without running any code, because the allowlist is
        asserted exactly rather than checked as a denylist.
        """

        source_path = pathlib.Path(__file__).resolve().parents[1] / "eligibility.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

        # Module roots and imported names are collected separately: the allowlist
        # constrains which *modules* the engine can reach, while the token check
        # also considers the names it binds.
        roots: set[str] = set()
        bound: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    roots.add(alias.name.split(".")[0])
                    bound.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                module = "." * node.level + (node.module or "")
                roots.add(module.lstrip(".").split(".")[0])
                bound.add(module.lstrip("."))
                for alias in node.names:
                    bound.add(alias.name)

        self.assertLessEqual(roots, PERMITTED_IMPORTS, sorted(roots - PERMITTED_IMPORTS))

        datara_members = {
            name for name in bound if name.startswith("datara.") or name == "datara"
        }
        self.assertLessEqual(
            datara_members, PERMITTED_DATARA_IMPORTS, sorted(datara_members - PERMITTED_DATARA_IMPORTS)
        )

        for token in FORBIDDEN_IMPORT_TOKENS:
            with self.subTest(token=token):
                self.assertFalse(
                    any(token in name for name in (n.lower() for n in bound)),
                    f"eligibility.py imports something named {token!r}",
                )

    def test_evaluating_eligibility_opens_no_socket(self) -> None:
        """Mutation: add any transport call to an evaluation path.

        ``socket.socket``, ``socket.create_connection``, ``socket.getaddrinfo``,
        ``urllib.request.urlopen`` and ``http.client.HTTPConnection.connect`` are
        all patched to raise, so any attempt fails loudly rather than passing
        because nothing was listening.
        """

        with network_disabled():
            decide(SATISFIED_OBSERVATIONS)
            decide(dict(SATISFIED_OBSERVATIONS, covered_days=1))
            decide({}, requirements=())
            decide({"x": 1}, requirements=[EligibilityRequirement(
                requirement_id="REQ-UNSEEN", kind=UNSEEN_KIND, source_key="x",
                description="unseen", comparator=COMPARATOR_PRESENT)])
            rule_set_digest(RULE_SET, REQUIREMENTS)
            is_execution_available(decide(SATISFIED_OBSERVATIONS))

    def test_every_public_path_runs_with_the_transport_removed(self) -> None:
        """The gate functions too, including the refusing one."""

        ineligible = decide(dict(SATISFIED_OBSERVATIONS, covered_days=14))
        with network_disabled():
            self.assertFalse(is_execution_available(ineligible))
            with self.assertRaises(EligibilityRefusal):
                require_eligible(ineligible)

    def test_no_provider_sdk_is_imported_as_a_consequence(self) -> None:
        """Mutation: import a provider SDK anywhere in the engine's import graph.

        Checked against ``sys.modules`` after evaluation, so a transitive import
        is caught as well as a direct one. The list is empty for Milestone A by
        design (SR06); nothing in this assignment may change that.
        """

        decide(SATISFIED_OBSERVATIONS)
        provider_prefixes = (
            "openai", "anthropic", "google", "cohere", "mistral", "ollama",
            "litellm", "boto3", "botocore", "httpx", "requests", "aiohttp",
            "openai_api", "groq", "replicate",
        )
        loaded = sorted(
            name for name in sys.modules
            if any(name == prefix or name.startswith(prefix + ".") for prefix in provider_prefixes)
        )
        self.assertEqual(loaded, [])

    def test_engine_reads_observations_and_never_recomputes_them(self) -> None:
        """Mutation: compute an observation inside the engine.

        Proven by checking that the engine imports no preparation or metric
        module: eligibility must read prepared state, so the only DATARA module it
        may depend on is the canonical serializer.
        """

        source_path = pathlib.Path(__file__).resolve().parents[1] / "eligibility.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

        # Only the canonical serializer may be imported from this package. Every
        # other datara module either computes observations or touches persistence,
        # and importing one would mean eligibility stopped being a pure read.
        # Checked over the AST rather than the text, because the module's
        # docstring *names* these modules precisely in order to say it does not
        # import them; a substring scan would flag its own explanation.
        datara_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                if node.module == "datara" or node.module.startswith("datara."):
                    datara_imports.add(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "datara" or alias.name.startswith("datara."):
                        datara_imports.add(alias.name)

        self.assertEqual(datara_imports, {"datara.normalization"}, sorted(datara_imports))


# ===========================================================================
# Declaration contract and decision integrity
# ===========================================================================


class DeclarationContractTests(unittest.TestCase):
    """A rule set that cannot be read as a rule set is refused, loudly."""

    def test_duplicate_requirement_id_is_refused(self) -> None:
        """Mutation: allow a duplicate id through.

        Two requirements would then share one identifier and one of them could not
        be named in an explanation, so an ineligibility would be unnameable.
        """

        duplicated = (REQUIREMENTS[0], EligibilityRequirement(
            requirement_id=REQUIREMENTS[0].requirement_id,
            kind=KIND_MANDATORY_FIELD,
            source_key="other",
            description="a different requirement with the same id",
            comparator=COMPARATOR_PRESENT,
        ))
        with self.assertRaises(EligibilityContractError):
            decide(SATISFIED_OBSERVATIONS, requirements=duplicated)

    def test_non_ascii_or_blank_machine_keys_are_refused(self) -> None:
        """Mutation: drop the ``isascii``/non-blank checks on machine keys.

        Machine keys sit inside a digest-stable canonical payload, so a
        non-ASCII or whitespace-padded key is a portability defect, not a label.
        """

        for field, value in (
            ("requirement_id", ""),
            ("requirement_id", " padded"),
            ("requirement_id", "REQ-\u2014"),
            ("source_key", ""),
            ("comparator", " "),
            ("declared_value_type", ""),
        ):
            with self.subTest(field=field, value=repr(value)):
                with self.assertRaises(EligibilityContractError):
                    _replace_field(REQUIREMENTS[0], field, value)

    def test_non_finite_required_value_is_refused(self) -> None:
        """A NaN bound could not be serialised into the canonical payload."""

        with self.assertRaises(EligibilityContractError):
            EligibilityRequirement(
                requirement_id="REQ-NAN",
                kind=KIND_QUALITY_LIMIT,
                source_key="ratio",
                description="a non-finite bound",
                comparator=COMPARATOR_AT_LEAST,
                required_value=float("inf"),
            )

    def test_non_mapping_observations_are_refused(self) -> None:
        for observations in ([("a", 1)], "a", 7, None):
            with self.subTest(observations=repr(observations)):
                with self.assertRaises(EligibilityContractError):
                    evaluate_eligibility(
                        observations=observations,
                        requirements=REQUIREMENTS,
                        rule_set_version=RULE_SET,
                    )

    def test_non_ascii_description_is_allowed_and_escaped_portably(self) -> None:
        """Prose may be non-ASCII; the payload escapes it, so the bytes stay ASCII."""

        requirement = EligibilityRequirement(
            requirement_id="REQ-PROSE",
            kind=KIND_MANDATORY_FIELD,
            source_key="sport",
            description="\u8dd1\u6b65\u6570\u636e",
            comparator=COMPARATOR_PRESENT,
        )
        with network_disabled():
            decision = decide({"sport": "running"}, requirements=[requirement])

        self.assertTrue(decision.eligible)
        self.assertEqual(decision.canonical_bytes().decode("ascii"), decision.canonical_payload)
        self.assertIn("\\u8dd1", decision.canonical_payload)


class DecisionIntegrityTests(unittest.TestCase):
    """A decision cannot be mutated into claiming something it is not."""

    def _bypass(self, decision, **changes):
        """Rebuild a decision with forged fields, bypassing the frozen dataclass.

        ``dataclasses.replace`` re-runs ``__post_init__``, so the forgery is made
        by writing the object's ``__dict__`` directly, which is what an attacker
        or a careless caller inside the process would actually do.
        """

        forged = object.__new__(EligibilityDecision)
        forged.__dict__.update(decision.__dict__)
        forged.__dict__.update(changes)
        return forged

    def test_forged_eligibility_is_refused_on_as_record(self) -> None:
        """Mutation: return the forged object without re-verifying.

        ``as_record`` re-runs the invariant, so a decision claiming
        ``eligible=True`` while carrying unmet requirements cannot be persisted.
        """

        decision = decide(dict(SATISFIED_OBSERVATIONS, covered_days=14))
        forged = self._bypass(decision, eligible=True)
        self.assertTrue(forged.eligible)
        with self.assertRaises(EligibilityContractError):
            forged.as_record()
        with self.assertRaises(EligibilityContractError):
            is_execution_available(forged)
        with self.assertRaises(EligibilityContractError):
            forged.canonical_bytes()

    def test_forged_unmet_reason_code_outside_the_vocabulary_is_refused(self) -> None:
        """Mutation: let free text into a reason code.

        Every code must be a key of ``REASON_DETAILS`` and every detail a member of
        that code's closed vocabulary, so downstream consumers can switch on the
        code without parsing prose.
        """

        decision = decide(dict(SATISFIED_OBSERVATIONS, covered_days=14))
        forged_item = dict(decision.unmet_requirements[0], reason_detail="because I said so")
        forged = self._bypass(decision, unmet_requirements=(forged_item,))
        with self.assertRaises(EligibilityContractError):
            forged.as_record()

    def test_forged_canonical_payload_is_refused(self) -> None:
        """Mutation: attach bytes that do not match the content."""

        decision = decide(SATISFIED_OBSERVATIONS)
        forged = self._bypass(decision, canonical_payload='{"eligible":true}')
        with self.assertRaises(EligibilityContractError):
            forged.as_record()

    def test_forged_rule_set_digest_is_refused(self) -> None:
        """A decision cannot claim to have been decided under rules it does not carry."""

        decision = decide(SATISFIED_OBSERVATIONS)
        forged = self._bypass(
            decision, rule_set_digest="sha256:" + "0" * 64)
        with self.assertRaises(EligibilityContractError):
            forged.as_record()

    def test_reordered_unmet_requirements_are_refused(self) -> None:
        """The declared ordering is enforced, not merely documented."""

        observations = dict(SATISFIED_OBSERVATIONS, covered_days=14, invalid_record_count=9)
        decision = decide(observations)
        self.assertEqual(len(decision.unmet_requirements), 2)
        forged = self._bypass(
            decision,
            unmet_requirements=tuple(reversed(decision.unmet_requirements)),
        )
        with self.assertRaises(EligibilityContractError):
            forged.as_record()

    def test_as_record_matches_the_persisted_eligibility_shape(self) -> None:
        """The projection must fit ``datara.models.Eligibility`` unchanged.

        That model has ``rule_version``, ``rule_set_version``, ``eligible``,
        ``unmet_requirements`` (JSON) and ``warnings`` (JSON). This test reads the
        model's field names rather than restating them, so if the model changes the
        test fails instead of drifting.
        """

        from datara import models as models_module

        decision = decide(dict(SATISFIED_OBSERVATIONS, covered_days=14))
        record = decision.as_record()
        persisted = {
            "rule_version",
            "rule_set_version",
            "eligible",
            "unmet_requirements",
            "warnings",
        }
        declared = {
            field.name
            for field in models_module.Eligibility._meta.get_fields()
            if hasattr(field, "attname")
        }
        self.assertTrue(persisted.issubset(declared), sorted(persisted - declared))
        self.assertEqual(set(record), persisted)
        for item in record["unmet_requirements"]:
            self.assertEqual(set(item), UNMET_KEYS)


class VocabularyTests(unittest.TestCase):
    """The reason vocabulary is closed and complete, and used as declared."""

    def test_every_reason_code_detail_pair_emitted_is_in_the_vocabulary(self) -> None:
        """A sweep over all four acceptance cases, so no path escapes the vocabulary."""

        hostile = EligibilityRequirement(
            requirement_id="REQ-HOSTILE", kind=KIND_MANDATORY_FIELD, source_key="hostile",
            description="raises when compared", comparator=COMPARATOR_PRESENT)
        unseen = EligibilityRequirement(
            requirement_id="REQ-UNSEEN", kind=UNSEEN_KIND, source_key="unseen",
            description="unknown kind", comparator=COMPARATOR_PRESENT)
        observation_sets = (
            SATISFIED_OBSERVATIONS,
            dict(SATISFIED_OBSERVATIONS, heart_rate=None),
            dict(SATISFIED_OBSERVATIONS, heart_rate="150"),
            dict(SATISFIED_OBSERVATIONS, sport="swimming"),
            dict(SATISFIED_OBSERVATIONS, covered_days=14),
            dict(SATISFIED_OBSERVATIONS, invalid_record_count=9),
            # Wrong-typed observations for the two NON-mandatory kinds. These were
            # absent from this sweep, which is how #385 shipped: heart_rate is a
            # mandatory_field, the one kind whose invalid-value vocabulary already
            # permitted "type_mismatch", so the sweep passed while
            # history_coverage and quality_limit raised on construction.
            dict(SATISFIED_OBSERVATIONS, covered_days=28.5),
            dict(SATISFIED_OBSERVATIONS, invalid_record_count="0"),
            dict(SATISFIED_OBSERVATIONS, covered_days=True),
            dict(SATISFIED_OBSERVATIONS, invalid_record_count=[0]),
            dict(SATISFIED_OBSERVATIONS, covered_days="28"),
            dict(SATISFIED_OBSERVATIONS, invalid_record_count={"n": 0}),
            {},
            {"hostile": _Exploding(), "unseen": 1, "covered_days": 1},
        )
        for observations in observation_sets:
            for requirements in (REQUIREMENTS, (hostile, unseen)):
                with self.subTest(observations=sorted(observations), requirements=len(requirements)):
                    decision = decide(observations, requirements=requirements)
                    for item in decision.unmet_requirements:
                        self.assertIn(item["reason_code"], REASON_DETAILS)
                        self.assertIn(item["reason_detail"], REASON_DETAILS[item["reason_code"]])
                        self.assertNotEqual(item["reason_code"], REASON_REQUIREMENT_SATISFIED)
                    self.assertEqual(
                        decision.eligible, not decision.unmet_requirements and bool(requirements))

    def test_declared_vocabularies_match_the_module_constants(self) -> None:
        """Kinds, comparators and value types are the ones SR10 names, no more."""

        self.assertEqual(
            set(KIND_ORDER),
            {KIND_MANDATORY_FIELD, KIND_HISTORY_COVERAGE, KIND_QUALITY_LIMIT},
        )
        self.assertEqual(set(SUPPORTED_KINDS), set(KIND_ORDER))
        self.assertEqual(
            SUPPORTED_COMPARATORS,
            {COMPARATOR_PRESENT, COMPARATOR_AT_LEAST, COMPARATOR_AT_MOST, COMPARATOR_EQUALS},
        )
        self.assertEqual(
            SUPPORTED_VALUE_TYPES, {VALUE_INTEGER, VALUE_NUMBER, VALUE_TEXT, VALUE_FLAG, VALUE_ANY}
        )
        for code, details in REASON_DETAILS.items():
            with self.subTest(code=code):
                self.assertIsInstance(details, frozenset)
                self.assertTrue(details)
                for detail in details:
                    self.assertRegex(detail, r"\A[a-z0-9_]+\Z")

    def test_a_new_detail_cannot_be_invented_at_the_call_site(self) -> None:
        """A reason code's detail vocabulary is closed, so codes stay comparable."""

        with self.assertRaises(EligibilityContractError):
            EligibilityDecision(
                rule_set_version=RULE_SET,
                rule_version=ENGINE_VERSION,
                rule_set_digest=rule_set_digest(RULE_SET, ()),
                rule_set=(),
                eligible=False,
                decision_reason_code="SOMETHING_ELSE",
                unmet_requirements=(),
                satisfied_requirements=(),
                observed_source_keys=(),
                unused_observation_keys=(),
                warnings=(),
                canonical_payload="",
            )


class _Exploding:
    """An observation that raises on any comparison."""

    def __eq__(self, other):
        raise RuntimeError("no")

    def __hash__(self):
        return 0



# ===========================================================================
# E9 -- a wrong-typed observation is explained, never raised  (#385)
# ===========================================================================


#: Every reason_detail string this engine may ever emit, enumerated by hand.
#: Deliberately NOT derived from REASON_DETAILS: deriving it would make the
#: closed-vocabulary assertion circular. If a future change adds a detail to the
#: engine but not to this set, the assertion below fails, which is the point.
KNOWN_DETAILS = frozenset({
    # satisfied
    "present",
    "within_declared_domain",
    # absence
    "observation_not_supplied",
    "observation_is_null",
    # invalid observed value
    "type_mismatch",
    "outside_declared_domain",
    "non_finite_number",
    "unsupported_observed_type",
    "below_declared_minimum",
    "above_declared_maximum",
    "not_equal_to_declared_value",
    # comparison not met
    "below_required_window",
    "above_permitted_window",
    "above_permitted_limit",
    "below_required_minimum",
    "not_equal_to_required",
    # not evaluable
    "unknown_requirement_kind",
    "unknown_comparator",
    "unknown_declared_value_type",
    "missing_required_value",
    "required_value_type_mismatch",
    "observation_not_comparable",
    "evaluation_raised",
})


class E9WrongTypedObservationTests(unittest.TestCase):
    """SR11: an ineligible skill identifies its unmet requirements.

    Regression cover for #385. ``_validate_observed`` returns the detail
    ``"type_mismatch"`` for a wrong-typed observation for *every* kind, but only
    ``mandatory_field`` narrows to a vocabulary that permitted it. For
    ``history_coverage`` and ``quality_limit`` the pair was rejected on
    construction, so ``evaluate_eligibility`` raised
    ``EligibilityContractError`` and every requirement's explanation was lost --
    the opposite of the module's own isolation claim. These tests hold the fixed
    behaviour: an observation of the wrong type yields an *ineligible decision
    that names the unmet requirement*, for every kind, without raising.
    """

    #: Observations whose type cannot satisfy the declared type.
    WRONG_TYPED = ("28.5", 28.5, True, [0], {"n": 0})

    def _requirement(self, kind, source_key):
        """One requirement of ``kind``, numeric, so a non-number is wrong-typed."""

        return EligibilityRequirement(
            requirement_id="REQ-WRONG-TYPED",
            kind=kind,
            source_key=source_key,
            description="declared numeric, observed otherwise",
            comparator=COMPARATOR_AT_LEAST,
            required_value=28,
            declared_value_type=VALUE_INTEGER,
        )

    def test_a_fractional_observation_against_an_integer_requirement_is_explained(self) -> None:
        """The realistic case: 28.5 days of coverage where an integer was declared.

        This is ordinary data, not an adversarial input, and it is the case the
        original 48 tests never exercised.
        """

        requirement = self._requirement(KIND_HISTORY_COVERAGE, "covered_days")
        with network_disabled():
            decision = decide({"covered_days": 28.5}, requirements=[requirement])

        self.assertFalse(decision.eligible)
        item = only(decision)
        self.assertEqual(item["reason_code"], REASON_REQUIREMENT_NOT_EVALUABLE)
        self.assertEqual(item["reason_detail"], "type_mismatch")
        self.assertEqual(item["observed_value"], 28.5)
        self.assertIn(item["reason_detail"], REASON_DETAILS[item["reason_code"]])

    def test_every_kind_explains_a_wrong_typed_observation_instead_of_raising(self) -> None:
        """Sweep every kind against every wrong-typed observation.

        Mutation: revert the #385 vocabulary entry and this raises
        EligibilityContractError for two of the three kinds, failing here.
        """

        for kind, source_key in (
            (KIND_MANDATORY_FIELD, "heart_rate"),
            (KIND_HISTORY_COVERAGE, "covered_days"),
            (KIND_QUALITY_LIMIT, "invalid_record_count"),
        ):
            requirement = self._requirement(kind, source_key)
            for observed in self.WRONG_TYPED:
                with self.subTest(kind=kind, observed=repr(observed)):
                    with network_disabled():
                        decision = decide({source_key: observed}, requirements=[requirement])

                    self.assertFalse(decision.eligible)
                    self.assertIsNone(decision.decision_reason_code)
                    item = only(decision)
                    self.assertIn(item["reason_code"], REASON_DETAILS)
                    self.assertIn(item["reason_detail"], REASON_DETAILS[item["reason_code"]])
                    self.assertNotEqual(item["reason_code"], REASON_REQUIREMENT_SATISFIED)
                    self.assertFalse(is_execution_available(decision))
                    with self.assertRaises(EligibilityRefusal):
                        require_eligible(decision)

    def test_a_wrong_typed_requirement_does_not_discard_the_other_explanations(self) -> None:
        """Requirements are independent: one bad value must not lose the rest.

        The candidate commit claimed an exception during one requirement's
        evaluation is "isolated rather than discarding the other requirements'
        explanations". That was false: the whole call raised. This test is the
        executable meaning of the claim -- a second, evaluable requirement keeps
        its own explanation alongside the wrong-typed one.
        """

        wrong = self._requirement(KIND_HISTORY_COVERAGE, "covered_days")
        short = EligibilityRequirement(
            requirement_id="REQ-SHORT",
            kind=KIND_QUALITY_LIMIT,
            source_key="invalid_record_count",
            description="more invalid records than permitted",
            comparator=COMPARATOR_AT_MOST,
            required_value=5,
            declared_value_type=VALUE_INTEGER,
        )
        satisfied = EligibilityRequirement(
            requirement_id="REQ-OK",
            kind=KIND_MANDATORY_FIELD,
            source_key="heart_rate",
            description="a recorded heart rate",
            comparator=COMPARATOR_PRESENT,
            declared_value_type=VALUE_INTEGER,
        )

        with network_disabled():
            decision = decide(
                {"covered_days": 28.5, "invalid_record_count": 9, "heart_rate": 150},
                requirements=[wrong, short, satisfied],
            )

        codes = unmet_codes(decision)
        self.assertEqual(
            codes,
            (
                "REQ-SHORT:QUALITY_LIMIT_NOT_MET",
                "REQ-WRONG-TYPED:REQUIREMENT_NOT_EVALUABLE",
            ),
        )
        # The evaluable requirement still reports itself as satisfied.
        self.assertEqual(decision.satisfied_requirements, ("REQ-OK",))
        self.assertFalse(decision.eligible)

    def test_widening_the_unevaluable_vocabulary_did_not_open_it(self) -> None:
        """The vocabulary is still closed: #385 added one detail to one code.

        ``type_mismatch`` is now permitted under REASON_REQUIREMENT_NOT_EVALUABLE
        in addition to REASON_MANDATORY_FIELD_INVALID, which already had it. It
        must still be rejected under every other code -- otherwise the fix would
        have converted a closed vocabulary into a loose one.
        """

        for code, details in REASON_DETAILS.items():
            with self.subTest(code=code):
                self.assertIsInstance(details, frozenset)
                self.assertNotIn("not_a_real_detail", details)
                self.assertLessEqual(
                    details, KNOWN_DETAILS,
                    f"{code} admits unknown detail(s): {sorted(details - KNOWN_DETAILS)}",
                )

        # Exactly the two codes whose engine paths emit this detail may carry it.
        permitting = {c for c, d in REASON_DETAILS.items() if "type_mismatch" in d}
        self.assertEqual(
            permitting,
            {REASON_MANDATORY_FIELD_INVALID, REASON_REQUIREMENT_NOT_EVALUABLE},
        )

def _replace_field(requirement, field, value):
    """``dataclasses.replace`` with one field overridden."""

    return dataclasses.replace(requirement, **{field: value})