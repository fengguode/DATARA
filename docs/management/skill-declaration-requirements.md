# Provider-independent skill declaration requirements — proposal

**Status:** Requirements proposal for TK31 / STK102, WP03 W0, P0. This document does not approve a product contract, select a technical schema or architecture, or claim evaluation, verification, acceptance, or release.

**Traceability:** CUS04 → FEAT04 → SR08, SR09, SR29, SR50, SR51; decision gate D02. Planned review cases: TC40 and TC51.

## Purpose and authority

CUS04 asks athletes to choose among evaluated expertise options. FEAT04 frames the P0 baseline as a small Datara-created library whose inputs, applicability, method, outputs, version, and evaluation references are explicit. SR08 and SR50 require declarations and immutable versions for released skills; SR09 keeps credentials and provider transport out of skill definitions; SR29 requires evidence-resolvable outputs that distinguish observations, computed metrics, and assessments, reject unapproved classifications or unresolved evidence references, and exclude P0 recommendations; SR51 separates the approved evaluation gate from retained evaluation evidence. These are the governing outcomes for this proposal ([product requirements](product-requirements.md), [system requirements](system-requirements.md)).

The 1 October D02 record selects `activity-summary`, `training-volume-trend`, and `training-consistency`, with deterministic metric calculation and eligibility, descriptive model findings, UTC scope conventions, and an initial evaluation direction. Recording that direction here does not freeze its implementation contract or establish that any skill has passed evaluation ([D02 baseline](p0-decision-baseline-2026-10-01.md); [decision register](decision-register.md)).

The field expectations below describe what a user or reviewer must be able to understand from a proposed skill declaration. They intentionally leave representation, storage, identifiers, serialization, and execution architecture open.

## Proposed user-facing declaration expectations

Each candidate declaration should let a user or reviewer answer the following questions before choosing or relying on the skill:

| Concern | Information the declaration is expected to make understandable |
| --- | --- |
| Identity and state | The skill's stable human-readable name and purpose; whether it is proposed, eligible for a particular dataset, evaluated for stated conditions, or released. A planned or schema-valid candidate must not be labelled evaluated. |
| Applicability | What activity and time scope the skill addresses; the required coverage or history; the conditions under which it applies; and material exclusions or quality limits. Eligibility is determined before any model request and must be reproducible for the same declared dataset, skill version, and rules. |
| Inputs | Which prepared observations or computed metrics are mandatory or optional; their meaning, units, time basis, and relevant coverage; and how required values are linked to the selected prepared dataset. A missing optional value remains unavailable and is not silently imputed. |
| Method and provenance | Which parts are deterministic calculations and which, if any, are descriptive model interpretation; the user-relevant method in plain language; the basis and version of each method claim; and resolvable source or rationale references for review. Provenance does not assert that third-party rights have been cleared. |
| Outputs | What the user can expect to receive, the required output schema, and what each result means. The declaration and result must keep source observations, computed metrics, and model assessments distinguishable; explain limitations; and provide resolvable evidence for findings as required by SR29. A result with an unapproved classification or unresolved evidence reference cannot be presented as a finding or successful result. The required schema is a user-facing contract expectation; its technical encoding and format remain open. |
| Version | An immutable version for each released definition, with enough information for a saved run to resolve the exact definition it used. Updating a definition creates a distinguishable version and does not rewrite a prior run's reference (SR08, SR50). |
| Evaluation | Which cases, deterministic checks, output-contract checks, substantive review, and applicable supported model/skill conditions support any evaluation claim; the D02-approved gate and its outcome; the distinct evaluation evidence retained; and known limits. A candidate cannot be labelled evaluated or released before the applicable gate is approved. The evidence categories remain separate. Evaluation is not implied by a complete declaration, a passing schema check, or mocked adapter behavior. This states SR51's gate/evidence distinction without claiming that approval or evidence exists. |
| Provider independence | The declared expertise describes inputs, applicability, method, and outputs without embedding a provider credential, endpoint, or transport instruction. A customer's explicit model choice and adapter capability are execution concerns outside the skill definition (SR09). |

An ineligible declaration must make the unmet conditions understandable and must not invite execution as if the skill were available. A declaration is not a promise that an analysis has run or a result exists. Existing user authorization and isolation obligations continue to apply to data selection, eligibility, execution, and result access; this proposal does not change them.

## Illustrative examples (requirements-level only)

These examples explain expected information, not approved field names, schemas, or final product copy.

**Positive example — candidate trend skill, eligible dataset.** A user can tell that the proposed skill summarizes *recorded* training volume across a stated UTC period, requires enough complete history and recorded activity in the required weeks, compares deterministic duration totals, and may return a constrained descriptive interpretation. The user can see that a result refers to the selected prepared dataset, its exact skill version, and evidence for the displayed totals. Any evaluation label identifies the reviewed cases and supported model/skill conditions; the example itself is not evidence that those checks have passed.

**Negative example — candidate consistency skill, insufficient history.** If the selected dataset does not meet the declaration's required history, deterministic eligibility explains the unmet coverage and blocks execution before a model request. The system does not infer inactive days beyond what the selected data supports, fabricate a zero for unavailable input, or show a successful finding. A catalog may explain the unmet requirement, but must not call the skill evaluated or available for this dataset.

## D02 status and unresolved details

The D02 decision record is evidence of selected direction, not complete conformance evidence. It selects the three named skills and states UTC week boundaries, activity attribution, initial applicability rules, an evaluation suite direction, and a substantive scoring threshold. This proposal neither reopens those recorded selections nor freezes them into a technical contract.

**Resolved D02 detail — consistency partial days.** The founder approved option A: consistency day counts and streaks use only complete UTC days wholly within the selected period. Partial-day activities at the selected-period edges remain included in the selected-period summary and activity-presence eligibility; they do not count as consistency days or toward the minimum of 28 complete days. The declaration/result must disclose the selected bounds and the effective complete-day bounds, including when edge partial days affect eligibility. This records the founder's reply and the coordinator's resolution in [D02 Decision #366](https://github.com/fengguode/DATARA/discussions/366#discussioncomment-18737403) ([resolution](https://github.com/fengguode/DATARA/discussions/366#discussioncomment-18739166)); it is no longer an open choice.

The following remain open for the D02 contract/evidence work and require explicit resolution or evidence before they can support a release claim:

1. **Per-skill declarations:** the final user-facing declaration for each selected skill and any applicability boundaries not already set by approved D02 choices.
2. **Contract artifacts:** final input/output definitions and positive/negative fixtures with independently reviewed expected values. No technical encoding is selected by this document.
3. **Method provenance:** a reviewable source/rationale inventory for each proposed method and disposition of any source-rights questions, without implying legal clearance (see FEAT30/SR52 and [TC42](validation-plan.md)).
4. **Evaluation anchors and evidence:** independent review of rubric anchors and expected examples, then separate deterministic, output-contract, and substantive evaluation records. The selected D02 criteria are target criteria, not observed results. Real evaluation for each applicable released provider/model/skill combination remains distinct from mocked or schema-only checks.
5. **Version-to-run evidence:** the contract-level retention behavior described by SR50 remains to be demonstrated with the planned version-history case TC51; no passing result is asserted.

The repository lists TC40 and TC51 as planned and Not run; they are acceptance evidence to collect after a contract is agreed, not evidence supplied by this proposal ([validation plan](validation-plan.md)).

## Acceptance questions for this requirements proposal

Reviewers can determine whether this proposal is ready for the next contract step when:

- every declaration concern in the table is addressed as a user-understandable outcome;
- both examples include a clear eligibility/evidence result and avoid implying unsupported capability;
- provider-specific access and transport remain outside skill definitions;
- version identity, evaluation state, and run binding remain explicit without choosing their technical representation; and
- each D02 open item above has an owner or decision/evidence path, with no unresolved item presented as approved or verified.

