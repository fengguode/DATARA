# Eligibility outcomes and blocking rules — TK34 / STK108

**Status:** Proposed behavioral requirement contract for independent review. It defines eligibility semantics only. It is not an implementation, database or wire schema, public API, evaluation result, or product acceptance.

**Traceability:** WP03 W0 contract preparation; TK34 / STK108; CUS05; FEAT05; SR10, SR11 and SR53; D02; TC07 and TC43. The GitHub Project is the live status record. Current main baseline at preparation: `dc28d05c69d9f8bf708aa8931a29a3a62356a628`.

## Purpose and boundary

Before execution, conventional application logic decides whether a selected skill can be run against the athlete's selected data. The decision is deterministic and explainable. It does not call a model, estimate missing data, or turn an unavailable result into a positive outcome.

This contract uses the three P0 skills and their selected eligibility thresholds recorded in the [D02 decision baseline](p0-decision-baseline-2026-10-01.md#d02--elemental-skills-and-evaluation). The thresholds below restate those choices so the eligibility decision can be reviewed; they do not evaluate or release any skill.

## Eligibility decision inputs

An evaluation is bound to:

- one immutable prepared-data snapshot;
- one explicit selected activity/date scope within that snapshot;
- one immutable skill version, including its declared mandatory inputs and applicability rules; and
- one eligibility-rule version.

For the same four inputs, evaluation must return the same outcome and same set of unmet-requirement identifiers. Changes to the snapshot, selected scope, skill version, or rule version are distinct evaluations and may produce different results. Wall-clock time, model output, provider state, or mutable data outside the bound snapshot must not alter an eligibility result.

The rule checks the requirements declared by the selected skill version against evidence in the bound scope. It must not treat absent, invalid, unresolved-conflict, or out-of-scope data as satisfying a mandatory requirement. Optional absence does not block unless the skill version explicitly declares that input mandatory. A missing value is never silently replaced with zero or inferred by a model.

## Per-skill outcomes

| Outcome | Meaning | Execution behavior |
| --- | --- | --- |
| **Eligible** | Every mandatory input, history-coverage condition, and permitted quality limit declared by this skill version is satisfied in the selected scope. | The skill may be offered for user selection, subject to all other applicable gates. |
| **Ineligible** | At least one declared mandatory requirement is not satisfied. Return every unmet mandatory requirement that the evaluation can establish, each with its stable requirement identifier and an explanation of what is missing or unsatisfied. | Do not allow execution and do not invoke a model. |
| **Evaluation error** | The system could not defensibly evaluate the bound inputs (for example, it could not resolve the requested immutable versions). This is an operational failure, not evidence that the athlete's data itself is ineligible. | Fail closed: do not allow execution or invoke a model; surface the failure through the applicable UI/error contract. Do not record it as Eligible. |

An empty catalog or an unavailable skill definition is not a per-skill Ineligible result. Catalog and accessible error states are covered separately by TK35 / TC45. This contract does not define how any outcome is serialized or rendered.

## Stable unmet-requirement identity

Each ineligible reason refers to the stable identity of a mandatory requirement declared by the applicable skill version. The identity must be reproducible for repeated evaluations of that same skill version and must not depend on localized explanation text, database row IDs, evaluation order, or generated timestamps. Explanations must make the unmet requirement understandable; they may be localized without changing the identity.

A requirement identity may be retired when the skill contract changes, but it must not be silently reused for a different meaning. The exact identifier vocabulary, syntax, serialization, ordering, and compatibility rules belong to the later skill-definition and interface contracts; this document does not create those values or a data schema. A stable identifier must not be invented when the skill version has not declared one: that condition is a contract defect to resolve before the affected skill can be represented as fully specified.

## D02 eligibility rules restated

| P0 skill | Minimum eligibility conditions from the selected D02 direction |
| --- | --- |
| `activity-summary` | At least one accepted, nonconflicting activity exists in the selected scope. |
| `training-volume-trend` | The scope contains the last four complete UTC calendar weeks wholly inside it (at least 28 days), and at least one accepted activity occurs in at least three of those weeks. Week boundaries are Monday 00:00 UTC. Other selected activities remain visible in the summary but outside this comparison. |
| `training-consistency` | The scope covers at least 28 complete UTC days and contains at least one accepted activity. An active day is a UTC start-date with at least one included activity. |

These conditions are minimums, not substitutes for each skill's complete declared inputs or any approved quality limits. A week without an uploaded activity contributes zero **recorded** duration only where D02 specifies that calculation; it does not establish that the athlete did no training or that uploads are complete. No distance, GPS, heart-rate, medical, injury-risk, prescription, or recommendation capability is inferred here.

## Failure and safety behavior

- Evaluate eligibility before any model request. Ineligible and evaluation-error outcomes make no inference request.
- When multiple mandatory requirements are unmet, do not stop at the first if the remaining unmet requirements can be determined from the same snapshot. Return all established unmet requirement identities.
- Do not treat a model failure as an eligibility decision, or a successful eligibility result as proof that a later model run succeeded.
- Do not equate an empty or incomplete snapshot with proof that an activity did not happen.
- Apply user authorization to every scope/snapshot read; this contract does not replace CUS10, SR20 or SR21.
- Eligibility proves only that the declared inputs and constraints are available for the selected scope. It does not establish substantive skill quality, medical suitability, a provider/model capability, or fitness of an analysis result.

## Evidence plan

TC43 remains **Not run**. Its candidate-specific checks should at minimum establish:

1. The same snapshot, scope, skill version, and rule version evaluated twice yields the same outcome and unmet-requirement identifiers.
2. An unmet mandatory input blocks eligibility, returns its stable identity and explanation, and results in zero inference calls.
3. Multiple independently unmet mandatory requirements are all reported when determinable.
4. A different scope or changed snapshot is treated as a different evaluation; it does not inherit a prior outcome without reevaluation.
5. Each D02 skill boundary is checked against the approved skill declarations and controlled expected values, including UTC week/day boundaries for trend and consistency.

TC07 also remains **Not run** and covers rejection/blocking behavior. TC45 separately covers catalog states and accessibility; neither test is passed by this proposal. Record the fixed candidate, skill/rule versions, controlled fixture identity, commands, actual outcomes and evidence before changing any case to Pass. Synthetic and source tests cannot substitute for real-model evaluation, system verification or final athlete acceptance.

## Open implementation and contract inputs

The following remain explicit; this proposal does not settle them:

- The final mandatory/optional input declarations and stable requirement identities for each skill must agree with the reviewed skill definitions (TK31 and the relevant D02 contract work).
- Any additional permitted data-quality limits or coverage cutoffs must be declared per skill and approved through the existing requirements process; no new threshold is introduced here.
- Identifier syntax, schema fields, API representation, localization details, and catalog rendering remain in their applicable skill-definition, interface, and TK35 contracts.
- Operational causes, retry affordances, and user-facing wording for evaluation errors remain UI/runtime details; an error must still fail closed.

Routine implementation details may proceed within these boundaries. A change to the athlete outcome, a new eligibility threshold, a public data/API shape, or a broader skill claim requires the applicable founder decision before dependent work.

## References

- [CUS05](../../issues/63) · [SR10](../../issues/78) · [SR11](../../issues/79) · [SR53](../../issues/101)
- [TK34](../../issues/133) · [STK108](../../issues/205) · [TK31](../../issues/130) · [TK35](../../issues/134)
- [D02 selected baseline](p0-decision-baseline-2026-10-01.md#d02--elemental-skills-and-evaluation)
