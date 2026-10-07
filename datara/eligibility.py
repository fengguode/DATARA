"""Deterministic, model-free eligibility evaluation with unmet-requirement explanation.

TK04 / TK44 core engine; CUS05; SR10, SR11 (+ SR53 to the extent it concerns
identifying a unmet requirement rather than guessing one). GitHub issue #379.

WHAT THIS MODULE IS
-------------------

A pure function from

    (prepared observations, declared requirements)  ->  EligibilityDecision

and nothing else. It answers one question -- *is this scope eligible for this
declared rule set?* -- and, when the answer is no, it names every requirement
that is unmet, with the observed value, the required condition and a stable
reason code.

WHAT THIS MODULE IS NOT
-----------------------

It does not define any skill, threshold, rubric or evaluation anchor. D02's
evaluation anchors are an open founder decision, so **requirements arrive as
input**. This module owns the *evaluation procedure* and the *reason vocabulary*,
and nothing else. Every number in a requirement here came from the caller.

It does not compute observations. Eligibility *reads prepared state*: it never
recomputes, regenerates, imputes, aggregates or smooths a value. The module
imports no preparation module, which makes that structural rather than a promise
(asserted by an AST import check in ``datara/tests/test_eligibility.py``).

It does not talk to anything. No provider SDK, no socket, no credential, no
database, no clock, no randomness, no environment lookup, no filesystem. SR11
requires unmet requirements to be identified *without invoking a model*, and the
strongest available form of that statement is that nothing in this module's
import graph can open a connection.

IT DOES NOT REPLACE ``datara.normalization.evaluate_eligibility``
----------------------------------------------------------------

``datara/normalization.py`` already carries a four-comparator evaluator
(``present``/``at_least``/``at_most``/``equals``) introduced with TK18. That one
raises ``VocabularyError`` for an unknown comparator at construction time, so an
unevaluable requirement cannot reach it as data and be reported unmet; it also
has no notion of a declared value type or a permitted value domain, so it cannot
distinguish "absent" (E2) from "present but wrong type or out of domain" (E3),
collapsing both into ``observed is None``.

This engine adds exactly those things: a fail-closed unevaluable path, a declared
value type, a permitted domain, per-kind reason codes, a machine-checked
rule-set digest and a byte-stable canonical payload. Whether the two evaluators
are consolidated, and which version token owns the persisted ``Eligibility`` row,
is a coordinator/architect decision and is reported rather than assumed. This
module is additive: ``datara/normalization.py`` was read, never changed.

SR10 FAILURE MODES ARE ADDRESSED BY KIND, NOT BY COMPARATOR
-----------------------------------------------------------

A reason code must be stable and must mean one thing. Deriving it from the
comparator alone would give the same code to a coverage shortfall and to a
quality breach, and E4/E5 would be indistinguishable downstream. So the *kind* of
a requirement selects the code for a failed comparison:

* ``mandatory_field``   -> ``MANDATORY_FIELD_ABSENT`` / ``MANDATORY_FIELD_INVALID``
* ``history_coverage``  -> ``HISTORY_COVERAGE_NOT_MET``
* ``quality_limit``     -> ``QUALITY_LIMIT_NOT_MET``
* *anything unrecognised* -> ``REQUIREMENT_NOT_EVALUABLE``

The comparator decides only *whether* a requirement is met, never which code
reports it. Each code carries a closed set of ``reason_detail`` values, validated
on construction, so free text cannot leak into a stable code -- the same
construction convention as ``normalization.REASON_DETAILS``.

FAIL-CLOSED
-----------

Nothing is satisfied unless it is positively established:

* an unknown requirement kind, unknown comparator, unknown declared value type,
  missing or unusable ``required_value``, incomparable types, a null observation
  and a missing observation all produce an **unmet** outcome;
* an unexpected exception raised while evaluating one requirement produces
  ``REQUIREMENT_NOT_EVALUABLE`` -- never a satisfied outcome, and never a
  traceback that discards the other requirements' explanations;
* an **empty rule set is ineligible** (``RULE_SET_EMPTY``). A skill that declares
  no requirements has established nothing, and letting it through would be the
  implicit "probably fine" default SR11 forbids. This is a fail-closed reading of
  the requirement, not a product threshold, and it is flagged for the coordinator;
* an observation whose type cannot be compared is unmet, never coerced.

DETERMINISM
-----------

Every collection this module emits is ordered by an explicit sort key over
strings, compared by Unicode code point, and no output is produced by iterating a
``set``. No output can therefore depend on ``PYTHONHASHSEED``. The decision
re-derives its own rule-set digest and its own canonical payload from its own
content on every construction and on every ``as_record``, so a mutated or
hand-built decision cannot claim rules or bytes it was not decided under -- the
bypass-resistance convention already used by ``datara.recorded_metrics``.

Attribution: Worker — Torsten Maier_space-bunny-free-xhigh_OpenCode (AI agent)
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from datara.normalization import canonical_json, sha256_digest

# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------

#: Identity of this engine's *evaluation procedure*. Bumping it changes
#: ``rule_version`` and therefore every decision it produces. It is deliberately
#: NOT ``datara.ELIGIBILITY_RULE_VERSION`` (``"tk18-eligibility/1"``), which
#: belongs to the TK18 evaluator in ``datara.normalization``; which token owns the
#: persisted ``Eligibility`` row is a coordinator decision, reported not assumed.
ENGINE_VERSION = "tk04-eligibility-engine/1"

#: Identity of the canonical decision payload shape.
CONTRACT_VERSION = "datara/eligibility-engine/1"

# ---------------------------------------------------------------------------
# Requirement kinds -- the three things SR10 says eligibility must cover
# ---------------------------------------------------------------------------

KIND_MANDATORY_FIELD = "mandatory_field"
KIND_HISTORY_COVERAGE = "history_coverage"
KIND_QUALITY_LIMIT = "quality_limit"

#: The kinds this engine evaluates. A kind outside this set is *not* a
#: construction error: it is carried through and reported unmet, because an
#: unrecognised requirement must be explained, not refused (SR11).
SUPPORTED_KINDS: frozenset[str] = frozenset(
    {KIND_MANDATORY_FIELD, KIND_HISTORY_COVERAGE, KIND_QUALITY_LIMIT}
)

#: Declared report order, used only to break a complete tie on the sort key.
#: ``SUPPORTED_KINDS`` is a set and is never iterated to produce output.
KIND_ORDER: tuple[str, ...] = (
    KIND_MANDATORY_FIELD,
    KIND_HISTORY_COVERAGE,
    KIND_QUALITY_LIMIT,
)

# ---------------------------------------------------------------------------
# Comparators
# ---------------------------------------------------------------------------

COMPARATOR_PRESENT = "present"
COMPARATOR_AT_LEAST = "at_least"
COMPARATOR_AT_MOST = "at_most"
COMPARATOR_EQUALS = "equals"

SUPPORTED_COMPARATORS: frozenset[str] = frozenset(
    {COMPARATOR_PRESENT, COMPARATOR_AT_LEAST, COMPARATOR_AT_MOST, COMPARATOR_EQUALS}
)

#: Comparators that need a ``required_value`` to mean anything.
_COMPARATORS_NEEDING_VALUE = frozenset(
    {COMPARATOR_AT_LEAST, COMPARATOR_AT_MOST, COMPARATOR_EQUALS}
)

# ---------------------------------------------------------------------------
# Declared observation value types
# ---------------------------------------------------------------------------

#: The caller declares the type of observation a requirement reads. These are
#: Python-level structural types, not product units; a unit, if the caller has
#: one, is echoed in ``unit`` and never inferred here.
VALUE_INTEGER = "integer"
VALUE_NUMBER = "number"
VALUE_TEXT = "text"
VALUE_FLAG = "flag"

#: No type declared; only the comparator's own admissibility applies.
VALUE_ANY = "any"

SUPPORTED_VALUE_TYPES: frozenset[str] = frozenset(
    {VALUE_INTEGER, VALUE_NUMBER, VALUE_TEXT, VALUE_FLAG, VALUE_ANY}
)

_SCALARS = (str, int, float, bool)

# ---------------------------------------------------------------------------
# Reason codes and their closed detail vocabularies
# ---------------------------------------------------------------------------

REASON_REQUIREMENT_SATISFIED = "REQUIREMENT_SATISFIED"
REASON_MANDATORY_FIELD_ABSENT = "MANDATORY_FIELD_ABSENT"
REASON_MANDATORY_FIELD_INVALID = "MANDATORY_FIELD_INVALID"
REASON_HISTORY_COVERAGE_NOT_MET = "HISTORY_COVERAGE_NOT_MET"
REASON_QUALITY_LIMIT_NOT_MET = "QUALITY_LIMIT_NOT_MET"
REASON_REQUIREMENT_NOT_EVALUABLE = "REQUIREMENT_NOT_EVALUABLE"

#: Decision-level reason: nothing was declared, so nothing was established.
REASON_RULE_SET_EMPTY = "RULE_SET_EMPTY"

REASON_DETAILS: Mapping[str, frozenset[str]] = {
    REASON_REQUIREMENT_SATISFIED: frozenset({"present", "within_declared_domain"}),
    REASON_MANDATORY_FIELD_ABSENT: frozenset({"observation_not_supplied", "observation_is_null"}),
    REASON_MANDATORY_FIELD_INVALID: frozenset(
        {
            "type_mismatch",
            "outside_declared_domain",
            "non_finite_number",
            "unsupported_observed_type",
            "below_declared_minimum",
            "above_declared_maximum",
            "not_equal_to_declared_value",
            # _validate_observed's final `else` arm returns this for a declared
            # type it does not recognise, and routes it through
            # _INVALID_BY_KIND like every other detail it produces. Step 1 of
            # _evaluate_one rejects an unsupported declared type before
            # _validate_observed is called, so the arm is currently unreachable
            # from the public API -- but the pair must still be admissible, so
            # that a future change to that ordering yields an explanation rather
            # than a raise that discards every other requirement's reason. Found
            # by the second independent review of #385; the arm is deliberately
            # NOT deleted, because deleting it would let an unsupported type fall
            # through to the permitted_values check and return None, i.e. be read
            # as admissible and then satisfied.
            "unknown_declared_value_type",
            # The per-requirement exception handler reports through
            # _INVALID_BY_KIND, so a mandatory_field whose comparison raises
            # arrives here rather than at REQUIREMENT_NOT_EVALUABLE. Without
            # this entry the handler raised on construction instead of
            # isolating the failure, discarding every other requirement's
            # explanation -- the second violation of the same invariant, found
            # in independent review of #385. The vocabulary is the right place
            # to reconcile it: the codes are load-bearing and must not move.
            "evaluation_raised",
        }
    ),
    REASON_HISTORY_COVERAGE_NOT_MET: frozenset(
        {"below_required_window", "above_permitted_window", "not_equal_to_required"}
    ),
    REASON_QUALITY_LIMIT_NOT_MET: frozenset(
        {"above_permitted_limit", "below_required_minimum", "not_equal_to_required"}
    ),
    REASON_REQUIREMENT_NOT_EVALUABLE: frozenset(
        {
            "unknown_requirement_kind",
            "unknown_comparator",
            "unknown_declared_value_type",
            "missing_required_value",
            "required_value_type_mismatch",
            "observation_not_supplied",
            "observation_is_null",
            "observation_not_comparable",
            "non_finite_number",
            # ``_validate_observed`` returns "type_mismatch" for a wrong-typed
            # observation for EVERY kind, but only ``mandatory_field`` narrows to
            # REASON_MANDATORY_FIELD_INVALID, whose vocabulary already permitted
            # it. ``history_coverage`` and ``quality_limit`` report this code, so
            # without the entry below a wrong-typed observation against them made
            # __post_init__ raise EligibilityContractError and destroyed every
            # requirement's explanation instead of naming the unmet one. Found in
            # review of #379; see issue #385. The vocabulary stays closed: a
            # detail that is not listed here is still rejected on construction.
            "type_mismatch",
            # _validate_observed returns "outside_declared_domain" for every
            # kind that carries a permitted_values domain, not just
            # mandatory_field. See the note on "evaluation_raised" above.
            "outside_declared_domain",
            "unsupported_observed_type",
            "evaluation_raised",
        }
    ),
}

#: The code reported when a recognised requirement's comparison fails, by kind.
_NOT_MET_BY_KIND: Mapping[str, str] = {
    KIND_MANDATORY_FIELD: REASON_MANDATORY_FIELD_INVALID,
    KIND_HISTORY_COVERAGE: REASON_HISTORY_COVERAGE_NOT_MET,
    KIND_QUALITY_LIMIT: REASON_QUALITY_LIMIT_NOT_MET,
}

#: The code reported when a recognised requirement cannot be evaluated at all, by
#: kind. ``mandatory_field`` narrows to the absence code so E2 and E3 stay
#: distinguishable; every other kind reports the generic unevaluable code.
_ABSENCE_BY_KIND: Mapping[str, str] = {
    KIND_MANDATORY_FIELD: REASON_MANDATORY_FIELD_ABSENT,
    KIND_HISTORY_COVERAGE: REASON_REQUIREMENT_NOT_EVALUABLE,
    KIND_QUALITY_LIMIT: REASON_REQUIREMENT_NOT_EVALUABLE,
}

#: The code reported when an observed value is present but inadmissible.
_INVALID_BY_KIND: Mapping[str, str] = {
    KIND_MANDATORY_FIELD: REASON_MANDATORY_FIELD_INVALID,
    KIND_HISTORY_COVERAGE: REASON_REQUIREMENT_NOT_EVALUABLE,
    KIND_QUALITY_LIMIT: REASON_REQUIREMENT_NOT_EVALUABLE,
}

#: Exact keys of one unmet-requirement explanation. Asserted on every
#: construction, so a new field cannot appear in a persisted explanation without a
#: test noticing.
UNMET_KEYS: frozenset[str] = frozenset(
    {
        "requirement_id",
        "kind",
        "source_key",
        "comparator",
        "description",
        "unit",
        "declared_value_type",
        "required_value",
        "observed_value",
        "observed_supplied",
        "observed_present",
        "reason_code",
        "reason_detail",
    }
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class EligibilityContractError(ValueError):
    """A rule set that cannot be read as a rule set at all.

    Reserved for *structural* declaration defects: a non-ASCII or blank machine
    key, a duplicate ``requirement_id``, a non-mapping ``observations``, a
    non-finite ``required_value``. These carry no requirement semantics, so there
    is nothing to explain and returning a decision would imply the rule set was
    understood.

    A declaration that is well formed but that this engine does not implement is
    **not** this error. It is reported unmet with ``REQUIREMENT_NOT_EVALUABLE``,
    which is the substance of SR11's fail-closed requirement.
    """


class EligibilityRefusal(ValueError):
    """Execution refused because the scope is ineligible (SR11).

    Carries the decision, so a caller can surface the unmet requirements without
    re-evaluating them.
    """

    def __init__(self, decision: EligibilityDecision) -> None:
        self.decision = decision
        super().__init__("ineligible: " + ", ".join(unmet_codes(decision)))


# ---------------------------------------------------------------------------
# Requirement declaration
# ---------------------------------------------------------------------------

_MACHINE_KEY_FIELDS = ("requirement_id", "source_key", "comparator", "declared_value_type")


@dataclass(frozen=True)
class EligibilityRequirement:
    """One declared requirement, supplied by the caller.

    No skill definition, threshold, rubric or evaluation anchor is defined here or
    anywhere in this module: every bound arrives through ``required_value`` or
    ``permitted_values``, and every unit through ``unit``.

    This validator checks *structure only*. It deliberately does not reject an
    unknown ``kind``, ``comparator`` or ``declared_value_type``, because such a
    requirement must reach the evaluator and be reported unmet, rather than be
    refused at construction where it could not be explained.
    """

    requirement_id: str
    kind: str
    source_key: str
    description: str
    comparator: str
    required_value: int | float | str | bool | None = None
    declared_value_type: str = VALUE_ANY
    permitted_values: tuple[int | float | str | bool, ...] = ()
    unit: str = ""

    def __post_init__(self) -> None:
        for name in _MACHINE_KEY_FIELDS:
            _require_machine_key(getattr(self, name), name)
        _require_text(self.description, "description")
        _require_text(self.unit, "unit")
        value = self.required_value
        if value is not None:
            if not isinstance(value, _SCALARS):
                raise EligibilityContractError("required_value_not_a_scalar")
            if isinstance(value, float) and not math.isfinite(value):
                raise EligibilityContractError("required_value_not_finite")
        if type(self.permitted_values) is not tuple:
            raise EligibilityContractError("permitted_values_not_a_tuple")
        for member in self.permitted_values:
            if member is None or not isinstance(member, _SCALARS):
                raise EligibilityContractError("permitted_value_not_a_scalar")
            if isinstance(member, float) and not math.isfinite(member):
                raise EligibilityContractError("permitted_value_not_finite")

    def as_record(self) -> dict:
        """The declared requirement, exactly as supplied.

        Carried into the decision so that the decision records the rules it was
        decided under, not only its verdict.
        """

        return {
            "requirement_id": self.requirement_id,
            "kind": self.kind,
            "source_key": self.source_key,
            "description": self.description,
            "comparator": self.comparator,
            "required_value": self.required_value,
            "declared_value_type": self.declared_value_type,
            "permitted_values": list(self.permitted_values),
            "unit": self.unit,
        }


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EligibilityDecision:
    """A boolean, the unmet requirements that produced it, and the canonical bytes.

    ``eligible`` is ``True`` only when ``decision_reason_code`` is ``None`` **and**
    ``unmet_requirements`` is empty. That invariant, the ordering of every emitted
    collection, the rule-set digest and the canonical payload are all re-derived
    from this object's own content on construction and again on ``as_record``, so
    a mutated or hand-built decision cannot present itself as eligible, as
    correctly ordered, or as decided under rules it does not carry.
    """

    rule_set_version: str
    rule_version: str
    rule_set_digest: str
    rule_set: tuple[dict, ...]
    eligible: bool
    decision_reason_code: str | None
    unmet_requirements: tuple[dict, ...]
    satisfied_requirements: tuple[str, ...]
    observed_source_keys: tuple[str, ...]
    unused_observation_keys: tuple[str, ...]
    warnings: tuple[str, ...]
    canonical_payload: str

    def __post_init__(self) -> None:
        self._check()

    # -- verification --------------------------------------------------------

    def _check(self) -> None:
        _require_machine_key(self.rule_set_version, "rule_set_version")
        _require_machine_key(self.rule_version, "rule_version")
        _require_machine_key(self.rule_set_digest, "rule_set_digest")
        if type(self.eligible) is not bool:
            raise EligibilityContractError("eligible_not_a_boolean")
        if type(self.rule_set) is not tuple:
            raise EligibilityContractError("rule_set_not_a_tuple")
        if self.decision_reason_code not in (None, REASON_RULE_SET_EMPTY):
            raise EligibilityContractError("unknown_decision_reason_code")
        self._check_ordered("unmet_requirements")
        self._check_ordered("satisfied_requirements")
        self._check_ordered("observed_source_keys")
        self._check_ordered("unused_observation_keys")
        self._check_ordered("warnings")
        self._check_unmet()
        self._check_rule_set()
        expected_eligible = (
            bool(self.rule_set)
            and self.decision_reason_code is None
            and not self.unmet_requirements
        )
        if self.eligible != expected_eligible:
            raise EligibilityContractError("eligible_inconsistent_with_unmet_requirements")
        if self.canonical_payload != canonical_json(self._payload()):
            raise EligibilityContractError("canonical_payload_does_not_match_content")

    def _check_ordered(self, name: str) -> None:
        value = getattr(self, name)
        if type(value) is not tuple:
            raise EligibilityContractError(f"{name}_not_a_tuple")
        if name == "unmet_requirements":
            return
        if any(type(item) is not str for item in value):
            raise EligibilityContractError(f"{name}_not_a_tuple_of_text")
        if list(value) != sorted(value):
            raise EligibilityContractError(f"{name}_not_ordered")

    def _check_unmet(self) -> None:
        seen_ids: set[str] = set()
        order: list[tuple[str, str, str]] = []
        for item in self.unmet_requirements:
            if type(item) is not dict or set(item) != UNMET_KEYS:
                raise EligibilityContractError("unmet_requirement_shape")
            code, detail = item["reason_code"], item["reason_detail"]
            if code not in REASON_DETAILS or detail not in REASON_DETAILS[code]:
                raise EligibilityContractError("reason_code_detail_not_in_vocabulary")
            for flag in ("observed_supplied", "observed_present"):
                if type(item[flag]) is not bool:
                    raise EligibilityContractError(f"{flag}_not_a_boolean")
            if item["requirement_id"] in seen_ids:
                raise EligibilityContractError("requirement_id_repeated_in_decision")
            seen_ids.add(item["requirement_id"])
            order.append((item["requirement_id"], item["kind"], item["source_key"]))
        if order != sorted(order):
            raise EligibilityContractError("unmet_requirements_not_ordered")
        for identifier in self.satisfied_requirements:
            if identifier in seen_ids:
                raise EligibilityContractError("requirement_id_repeated_in_decision")

    def _check_rule_set(self) -> None:
        declared_ids = [item.get("requirement_id") for item in self.rule_set]
        if any(type(item) is not str for item in declared_ids):
            raise EligibilityContractError("rule_set_record_shape")
        if len(set(declared_ids)) != len(declared_ids):
            raise EligibilityContractError("rule_set_requirement_id_repeated")
        reported = sorted(
            list(self.satisfied_requirements)
            + [item["requirement_id"] for item in self.unmet_requirements]
        )
        if reported != sorted(declared_ids):
            raise EligibilityContractError("reported_requirements_differ_from_rule_set")
        expected = sha256_digest(
            canonical_json(_rule_set_payload(self.rule_set_version, self.rule_set, self.rule_version))
        )
        if self.rule_set_digest != expected:
            raise EligibilityContractError("rule_set_digest_mismatch")

    # -- projections ---------------------------------------------------------

    def _payload(self) -> dict:
        return _decision_payload(
            rule_set_version=self.rule_set_version,
            rule_version=self.rule_version,
            rule_set_digest=self.rule_set_digest,
            rule_set=self.rule_set,
            eligible=self.eligible,
            decision_reason_code=self.decision_reason_code,
            satisfied_requirements=self.satisfied_requirements,
            unmet_requirements=self.unmet_requirements,
            observed_source_keys=self.observed_source_keys,
            unused_observation_keys=self.unused_observation_keys,
            warnings=self.warnings,
        )

    def as_record(self) -> dict:
        """The projection matching the persisted ``datara.models.Eligibility`` row.

        Re-verifies the decision and returns a fresh deep copy of each nested
        dict, so a caller cannot mutate the stored explanation through it.
        """

        self._check()
        return {
            "rule_version": self.rule_version,
            "rule_set_version": self.rule_set_version,
            "eligible": self.eligible,
            "unmet_requirements": [dict(item) for item in self.unmet_requirements],
            "warnings": list(self.warnings),
        }

    def canonical_bytes(self) -> bytes:
        """The canonical payload as ASCII bytes, for byte-for-byte comparison."""

        self._check()
        return self.canonical_payload.encode("ascii")


# ---------------------------------------------------------------------------
# SR11 execution gate
# ---------------------------------------------------------------------------


def unmet_codes(decision: EligibilityDecision) -> tuple[str, ...]:
    """Each unmet requirement's identifier and reason code, in report order.

    Ordered, so a log line or refusal message built from it is stable. It names
    each failing requirement rather than only saying "ineligible".
    """

    decision._check()
    return tuple(
        f"{item['requirement_id']}:{item['reason_code']}" for item in decision.unmet_requirements
    )


def is_execution_available(decision: EligibilityDecision) -> bool:
    """True only where SR11 permits execution; an ineligible skill is unavailable."""

    decision._check()
    return decision.eligible


def require_eligible(decision: EligibilityDecision) -> EligibilityDecision:
    """Return the decision if execution may proceed, else raise :class:`EligibilityRefusal`.

    The mechanical half of "an ineligible skill shall be unavailable for
    execution": the refusal becomes a raised, unmissable value instead of a flag a
    caller may forget to test. No presentation is invented here -- TK35 is
    decision-blocked -- and the unmet requirements travel on the exception.
    """

    decision._check()
    if decision.eligible:
        return decision
    raise EligibilityRefusal(decision)


# ---------------------------------------------------------------------------
# Validation and ordering helpers
# ---------------------------------------------------------------------------


def _require_machine_key(value: object, name: str) -> None:
    """A machine key: a non-empty ASCII string with no surrounding whitespace.

    ASCII is required because these strings are canonical machine keys inside a
    digest-stable payload. Non-ASCII prose belongs in ``description``/``unit``,
    where canonical JSON escapes it portably.
    """

    if type(value) is not str or not value or not value.isascii() or value.strip() != value:
        raise EligibilityContractError(f"{name}_not_an_ascii_machine_key")


def _require_text(value: object, name: str) -> None:
    if type(value) is not str:
        raise EligibilityContractError(f"{name}_not_text")


def _sort_key(requirement: EligibilityRequirement) -> tuple[str, str, str]:
    """The total order of the unmet report.

    Strings only, compared by Unicode code point, so the order cannot depend on
    the order the caller supplied the requirements, on ``PYTHONHASHSEED``, or on a
    locale collation. The three components keep the order total even where two
    requirements share an id, which is refused separately.
    """

    return (requirement.requirement_id, requirement.kind, requirement.source_key)


def _decision_payload(
    *,
    rule_set_version: str,
    rule_version: str,
    rule_set_digest: str,
    rule_set: tuple,
    eligible: bool,
    decision_reason_code: str | None,
    satisfied_requirements: tuple,
    unmet_requirements: tuple,
    observed_source_keys: tuple,
    unused_observation_keys: tuple,
    warnings: tuple,
) -> dict:
    """The canonical payload of a decision, from its content.

    Free-standing so that the decision's own bytes can be computed *before* the
    decision object exists, rather than by constructing a placeholder that cannot
    pass its own validation.
    """

    return {
        "contract_version": CONTRACT_VERSION,
        "engine_version": ENGINE_VERSION,
        "rule_version": rule_version,
        "rule_set_version": rule_set_version,
        "rule_set_digest": rule_set_digest,
        "rule_set": [dict(item) for item in rule_set],
        "eligible": eligible,
        "decision_reason_code": decision_reason_code,
        "satisfied_requirements": list(satisfied_requirements),
        "unmet_requirements": [dict(item) for item in unmet_requirements],
        "observed_source_keys": list(observed_source_keys),
        "unused_observation_keys": list(unused_observation_keys),
        "warnings": list(warnings),
    }


def _rule_set_payload(
    rule_set_version: str, rule_set: tuple, rule_version: str
) -> dict:
    return {
        "contract_version": CONTRACT_VERSION,
        "engine_version": ENGINE_VERSION,
        "rule_set_version": rule_set_version,
        "rule_version": rule_version,
        "requirements": [dict(item) for item in rule_set],
    }


# ---------------------------------------------------------------------------
# Observation admissibility
# ---------------------------------------------------------------------------


def _portable(value: object) -> bool:
    """True when ``value`` can appear verbatim in the canonical payload.

    Checks exactly what :func:`datara.normalization.canonical_json` will accept,
    without serialising twice: a scalar, a finite float, and nothing the encoder
    would raise on. Without this an observation that cannot be represented would
    surface as a serialisation ``TypeError`` escaping the evaluator, replacing an
    explanation with a traceback.
    """

    if isinstance(value, bool) or isinstance(value, int) or isinstance(value, str):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    return False


def _validate_observed(requirement: EligibilityRequirement, observed: object) -> str | None:
    """Return a ``reason_detail`` if the observation is unusable, else ``None``.

    Strict on purpose. ``bool`` is a subclass of ``int``, so ``type(value) is int``
    rather than ``isinstance`` is what stops ``True`` from silently satisfying an
    ``at_least 1`` integer requirement; a float never satisfies an integer
    requirement, so nothing is coerced. A non-finite number is refused because it
    would otherwise serialise as a bare ``NaN``/``Infinity`` token and poison the
    canonical payload's meaning. Domain membership compares types as well as
    values, so ``True`` cannot pass a domain of ``(1,)``.
    """

    declared = requirement.declared_value_type
    if declared == VALUE_INTEGER:
        if type(observed) is not int:
            return "type_mismatch"
    elif declared == VALUE_NUMBER:
        if type(observed) is bool or not isinstance(observed, (int, float)):
            return "type_mismatch"
        if isinstance(observed, float) and not math.isfinite(observed):
            return "non_finite_number"
    elif declared == VALUE_TEXT:
        if type(observed) is not str or not observed:
            return "type_mismatch"
    elif declared == VALUE_FLAG:
        if type(observed) is not bool:
            return "type_mismatch"
    elif declared == VALUE_ANY:
        if not _portable(observed):
            return "unsupported_observed_type"
    else:
        return "unknown_declared_value_type"

    if requirement.permitted_values and not any(
        type(observed) is type(allowed) and observed == allowed
        for allowed in requirement.permitted_values
    ):
        return "outside_declared_domain"
    return None


def _direction_detail(kind: str, not_met_detail: str) -> str:
    """Name the shortfall in the detail vocabulary of the kind's own reason code."""

    if kind == KIND_HISTORY_COVERAGE:
        return not_met_detail
    if kind == KIND_QUALITY_LIMIT:
        if not_met_detail == "above_permitted_window":
            return "above_permitted_limit"
        if not_met_detail == "below_required_window":
            return "below_required_minimum"
        return "not_equal_to_required"
    if not_met_detail == "above_permitted_window":
        return "above_declared_maximum"
    if not_met_detail == "below_required_window":
        return "below_declared_minimum"
    return "not_equal_to_declared_value"


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


class _NotSupplied:
    """Sentinel for "no observation was read at all".

    Distinct from ``None``, because an unsupplied key and a supplied null are two
    different explanations and E2 must tell them apart.
    """

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return "<observation_not_supplied>"


_NOT_SUPPLIED = _NotSupplied()


@dataclass(frozen=True)
class _Outcome:
    """One requirement's verdict, before it is projected into the report."""

    requirement: EligibilityRequirement
    satisfied: bool
    reason_code: str
    reason_detail: str
    observed: object
    observed_supplied: bool


def _evaluate_one(
    requirement: EligibilityRequirement, observations: Mapping[str, object]
) -> _Outcome:
    """Evaluate one requirement, in one fixed order of checks.

    The order is deliberate:

    1. Can this engine recognise the requirement at all? (kind, comparator, type)
    2. Was an observation supplied for it, and is it non-null?
    3. Is the observation admissible against the declared type and domain?
    4. Is the comparator applicable to this pair of values?
    5. Only then, the comparison itself.

    Steps 1, 2 and 4, and the inadmissible cases of step 3, all yield an unmet
    outcome. Nothing here raises, and nothing is satisfied by default.
    """

    # 1. Recognisability. An unknown kind, comparator or declared type is unmet.
    if type(requirement.kind) is not str or requirement.kind not in SUPPORTED_KINDS:
        return _unevaluable(requirement, "unknown_requirement_kind")
    if requirement.comparator not in SUPPORTED_COMPARATORS:
        return _unevaluable(requirement, "unknown_comparator")
    if requirement.declared_value_type not in SUPPORTED_VALUE_TYPES:
        return _unevaluable(requirement, "unknown_declared_value_type")

    # 2. Presence. `mandatory_field` reports its narrower absence code (E2);
    #    every other kind reports the generic unevaluable code.
    if requirement.source_key not in observations:
        return _unevaluable(requirement, "observation_not_supplied")
    observed = observations[requirement.source_key]
    if observed is None:
        return _unevaluable(requirement, "observation_is_null", supplied=True, observed=None)

    # 3. Admissibility against the declared type and permitted domain (E3).
    inadmissible = _validate_observed(requirement, observed)
    if inadmissible is not None:
        code = _INVALID_BY_KIND[requirement.kind]
        return _Outcome(
            requirement=requirement,
            satisfied=False,
            reason_code=code,
            reason_detail=inadmissible,
            observed=observed,
            observed_supplied=True,
        )

    # 4. Comparator applicability. A required_value that cannot support the
    #    comparator, or an observation it cannot be compared with, is unmet.
    if requirement.comparator in _COMPARATORS_NEEDING_VALUE:
        required = requirement.required_value
        if required is None:
            return _unevaluable(requirement, "missing_required_value")
        if requirement.comparator in (COMPARATOR_AT_LEAST, COMPARATOR_AT_MOST):
            if isinstance(required, bool) or not isinstance(required, (int, float)):
                return _unevaluable(requirement, "required_value_type_mismatch")
            if type(observed) is bool or not isinstance(observed, (int, float)):
                return _unevaluable(requirement, "observation_not_comparable")

    # 5. The comparison itself.
    comparator = requirement.comparator
    if comparator == COMPARATOR_PRESENT:
        met, not_met_detail = True, None
    elif comparator == COMPARATOR_AT_LEAST:
        met = observed >= requirement.required_value
        not_met_detail = "below_required_window"
    elif comparator == COMPARATOR_AT_MOST:
        met = observed <= requirement.required_value
        not_met_detail = "above_permitted_window"
    else:
        required = requirement.required_value
        met = type(observed) is type(required) and observed == required
        not_met_detail = "not_equal_to_required"

    if met:
        return _Outcome(
            requirement=requirement,
            satisfied=True,
            reason_code=REASON_REQUIREMENT_SATISFIED,
            reason_detail=(
                "within_declared_domain" if requirement.permitted_values else "present"
            ),
            observed=observed,
            observed_supplied=True,
        )
    return _Outcome(
        requirement=requirement,
        satisfied=False,
        reason_code=_NOT_MET_BY_KIND[requirement.kind],
        reason_detail=_direction_detail(requirement.kind, not_met_detail),
        observed=observed,
        observed_supplied=True,
    )


def _unevaluable(
    requirement: EligibilityRequirement,
    detail: str,
    *,
    supplied: bool = False,
    observed: object = _NOT_SUPPLIED,
) -> _Outcome:
    """An unmet outcome for a requirement this engine cannot establish.

    ``mandatory_field`` narrows to its absence code when the observation is
    missing or null, so "absent" (E2) stays distinct from "present but invalid"
    (E3); for the other two kinds the absence is reported as unevaluable, which
    is still unmet and never satisfied.
    """

    if detail in ("observation_not_supplied", "observation_is_null"):
        code = _ABSENCE_BY_KIND.get(requirement.kind, REASON_REQUIREMENT_NOT_EVALUABLE)
    else:
        code = REASON_REQUIREMENT_NOT_EVALUABLE
    return _Outcome(
        requirement=requirement,
        satisfied=False,
        reason_code=code,
        reason_detail=detail,
        observed=observed,
        observed_supplied=supplied,
    )


def _explain(outcome: _Outcome) -> dict:
    """Project one unmet outcome into the persisted explanation shape.

    The key set is exactly :data:`UNMET_KEYS`; the decision constructor rejects
    anything else, so a new field cannot appear in a stored explanation unnoticed.
    ``observed_value`` is ``None`` for an unsupplied observation, and
    ``observed_supplied`` distinguishes that from a supplied null.
    """

    requirement = outcome.requirement
    # An inadmissible value is still echoed, because "the value was 150, of the
    # wrong type" is more useful than "the value was missing". But only a value
    # that can be serialised may be echoed: carrying a non-portable object into
    # the canonical payload would turn an explanation into a serialisation error.
    # The explanation records that a value existed via `observed_present`, and
    # that it could not be reported via `observed_supplied` staying true with a
    # null `observed_value`.
    if outcome.observed is _NOT_SUPPLIED or outcome.observed is None:
        reported = None
    elif _portable(outcome.observed):
        reported = outcome.observed
    else:
        reported = None
    return {
        "requirement_id": requirement.requirement_id,
        "kind": requirement.kind,
        "source_key": requirement.source_key,
        "comparator": requirement.comparator,
        "description": requirement.description,
        "unit": requirement.unit,
        "declared_value_type": requirement.declared_value_type,
        "required_value": requirement.required_value,
        "observed_value": reported,
        "observed_supplied": outcome.observed_supplied,
        "observed_present": reported is not None,
        "reason_code": outcome.reason_code,
        "reason_detail": outcome.reason_detail,
    }


def _checked_requirements(requirements: Sequence[EligibilityRequirement]) -> tuple:
    """Validate the declared sequence structurally; return it as a tuple.

    A duplicated ``requirement_id`` is refused because it makes the report
    ambiguous: two requirements would share one identifier, so one of them could
    not be named in an explanation.
    """

    if isinstance(requirements, (str, bytes)) or not isinstance(requirements, Sequence):
        raise EligibilityContractError("requirements_not_a_sequence")
    seen: set[str] = set()
    for item in requirements:
        if type(item) is not EligibilityRequirement:
            raise EligibilityContractError("unsupported_requirement_type")
        if item.requirement_id in seen:
            raise EligibilityContractError("duplicate_requirement_id")
        seen.add(item.requirement_id)
    return tuple(requirements)


def rule_set_digest(
    rule_set_version: str,
    requirements: Sequence[EligibilityRequirement],
    *,
    rule_version: str = ENGINE_VERSION,
) -> str:
    """The digest of a declared rule set alone, independent of any observation.

    Lets two decisions be compared for rule equality as well as output equality,
    and lets an ineligible outcome be attributed to the exact rules that produced
    it. Ordered by the same total sort key as the report.
    """

    _require_machine_key(rule_set_version, "rule_set_version")
    _require_machine_key(rule_version, "rule_version")
    ordered = sorted(_checked_requirements(requirements), key=_sort_key)
    return sha256_digest(
        canonical_json(
            _rule_set_payload(
                rule_set_version, tuple(item.as_record() for item in ordered), rule_version
            )
        )
    )


def evaluate_eligibility(
    *,
    observations: Mapping[str, object],
    requirements: Sequence[EligibilityRequirement],
    rule_set_version: str,
    rule_version: str = ENGINE_VERSION,
) -> EligibilityDecision:
    """Decide eligibility deterministically and explain every unmet requirement.

    Pure: the only inputs are the arguments. No clock, no randomness, no
    environment lookup, no database, no network, no model, so an ineligible scope
    cannot become a provider request on this path (SR11).

    The unmet report is ordered by ``(requirement_id, kind, source_key)`` compared
    by Unicode code point, so it does not depend on the order in which the caller
    supplied the requirements.
    """

    if not isinstance(observations, Mapping):
        raise EligibilityContractError("observations_not_a_mapping")
    _require_machine_key(rule_set_version, "rule_set_version")
    _require_machine_key(rule_version, "rule_version")
    ordered = sorted(_checked_requirements(requirements), key=_sort_key)
    rule_set = tuple(item.as_record() for item in ordered)
    digest = sha256_digest(canonical_json(_rule_set_payload(rule_set_version, rule_set, rule_version)))

    outcomes: list[_Outcome] = []
    for requirement in ordered:
        try:
            outcomes.append(_evaluate_one(requirement, observations))
        except Exception:
            # Fail-closed. One requirement's evaluation raising must not discard
            # the other requirements' explanations, and must never read as
            # satisfied. `mandatory_field` reports the invalid code because the
            # value it was handed could not be used.
            outcomes.append(
                _Outcome(
                    requirement=requirement,
                    satisfied=False,
                    reason_code=(
                        _INVALID_BY_KIND.get(
                            requirement.kind, REASON_REQUIREMENT_NOT_EVALUABLE
                        )
                        if type(requirement.kind) is str
                        else REASON_REQUIREMENT_NOT_EVALUABLE
                    ),
                    reason_detail="evaluation_raised",
                    observed=_NOT_SUPPLIED,
                    observed_supplied=False,
                )
            )

    unmet = tuple(_explain(item) for item in outcomes if not item.satisfied)
    satisfied = tuple(item.requirement.requirement_id for item in outcomes if item.satisfied)

    referenced = sorted({item.source_key for item in ordered})
    observed_keys = tuple(key for key in referenced if key in observations)
    referenced_set = set(referenced)
    unused = tuple(sorted(key for key in observations if key not in referenced_set))
    warnings = tuple(sorted(
        f"no declared requirement reads observation key {key!r}" for key in unused
    ))

    return _finish(
        rule_set_version=rule_set_version,
        rule_version=rule_version,
        digest=digest,
        rule_set=rule_set,
        unmet=unmet,
        satisfied=satisfied,
        observed_keys=observed_keys,
        unused=unused,
        warnings=warnings,
        has_requirements=bool(ordered),
    )


def _finish(
    *,
    rule_set_version: str,
    rule_version: str,
    digest: str,
    rule_set: tuple,
    unmet: tuple,
    satisfied: tuple,
    observed_keys: tuple,
    unused: tuple,
    warnings: tuple,
    has_requirements: bool,
) -> EligibilityDecision:
    """Assemble the decision and stamp its canonical payload onto it.

    The payload is produced from the decision's own content and re-verified by the
    constructor, so a decision and its bytes cannot drift apart. An empty rule set
    is ineligible: nothing was declared, so nothing was established.
    """

    eligible = has_requirements and not unmet
    reason_code = None if has_requirements else REASON_RULE_SET_EMPTY
    payload = canonical_json(
        _decision_payload(
            rule_set_version=rule_set_version,
            rule_version=rule_version,
            rule_set_digest=digest,
            rule_set=rule_set,
            eligible=eligible,
            decision_reason_code=reason_code,
            satisfied_requirements=satisfied,
            unmet_requirements=unmet,
            observed_source_keys=observed_keys,
            unused_observation_keys=unused,
            warnings=warnings,
        )
    )
    return EligibilityDecision(
        rule_set_version=rule_set_version,
        rule_version=rule_version,
        rule_set_digest=digest,
        rule_set=rule_set,
        eligible=eligible,
        decision_reason_code=reason_code,
        unmet_requirements=unmet,
        satisfied_requirements=satisfied,
        observed_source_keys=observed_keys,
        unused_observation_keys=unused,
        warnings=warnings,
        canonical_payload=payload,
    )


__all__ = [
    "CONTRACT_VERSION",
    "ENGINE_VERSION",
    "KIND_MANDATORY_FIELD",
    "KIND_HISTORY_COVERAGE",
    "KIND_QUALITY_LIMIT",
    "KIND_ORDER",
    "SUPPORTED_KINDS",
    "COMPARATOR_PRESENT",
    "COMPARATOR_AT_LEAST",
    "COMPARATOR_AT_MOST",
    "COMPARATOR_EQUALS",
    "SUPPORTED_COMPARATORS",
    "VALUE_INTEGER",
    "VALUE_NUMBER",
    "VALUE_TEXT",
    "VALUE_FLAG",
    "VALUE_ANY",
    "SUPPORTED_VALUE_TYPES",
    "REASON_REQUIREMENT_SATISFIED",
    "REASON_MANDATORY_FIELD_ABSENT",
    "REASON_MANDATORY_FIELD_INVALID",
    "REASON_HISTORY_COVERAGE_NOT_MET",
    "REASON_QUALITY_LIMIT_NOT_MET",
    "REASON_REQUIREMENT_NOT_EVALUABLE",
    "REASON_RULE_SET_EMPTY",
    "REASON_DETAILS",
    "UNMET_KEYS",
    "EligibilityContractError",
    "EligibilityRefusal",
    "EligibilityRequirement",
    "EligibilityDecision",
    "evaluate_eligibility",
    "rule_set_digest",
    "require_eligible",
    "is_execution_available",
    "unmet_codes",
]
