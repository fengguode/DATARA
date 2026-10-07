# Eligibility catalog state and accessibility acceptance note

Status: requirements-design proposal for TK35 / STK110. It is not a product decision, UI design, implementation contract, verification result, acceptance, or release.

Work package: WP03 — baseline skills and eligibility pipeline  
Affected stories/features/requirements: CUS04, CUS05; FEAT31; SR11, SR58.  
Parent task: [TK35 / #134](https://github.com/fengguode/DATARA/issues/134).  
Subtask: [STK110 / #206](https://github.com/fengguode/DATARA/issues/206).  
Planned verification: TC45.  
D02 status: selected P0 skill direction; remaining contract and evaluation-evidence gates stay open.  
Coordinator: Primary Coordinator — Yi Tang. GitHub publisher: fengguode.

## Scope and boundaries

This note translates the existing acceptance criteria for four catalog conditions—eligible, ineligible, empty, and error—into reviewable outcomes. The dated D02 baseline already selects the P0 target skills (`activity-summary`, `training-volume-trend`, and `training-consistency`) and records their descriptive metric and UTC calculation direction. This note does not change that selected scope or those rules. D02 still has open engineering and evidence work: frozen schemas and fixtures, independently reviewed rubric anchors, and live evaluation. The dated D04 baseline separately selects WCAG 2.2 AA as the accessibility design target and identifies keyboard/screen-reader journeys and other design checks; that target remains subject to design and evidence checks and is not a conformance claim. This note does not choose additional skill declarations, input thresholds, reason-code vocabulary, UI layout, control pattern, exact user-facing copy, or a new accessibility target.

The catalog communicates deterministic eligibility before any analysis. An eligible entry is not a completed assessment or recommendation. An ineligible entry cannot be submitted for execution. Viewing or explaining eligibility makes no model call. No UI state may imply a result that the available source data and approved skill contract do not support. The action column records only an action already supported by current requirements, or explicitly says that no action is currently specified or approved; it does not create recovery behavior.

The state names below are review labels for the acceptance cases, not proposed API values, database enums, or required literal strings.

## Outcome matrix

| Case | Observable condition to distinguish | Information that must be understandable | Current action, or explicit absence of one |
| --- | --- | --- | --- |
| Eligible | The approved eligibility contract reports the skill as eligible for the current selected data scope. | The skill is available for the user's explicit choice. The state must not imply that a model was called, that analysis ran, or that an outcome is guaranteed. | The user may explicitly select this eligible option for later consideration, consistent with CUS04. Selection alone does not run analysis, invoke a model, or authorize execution; this note defines no run control or confirmation flow. |
| Ineligible | The approved contract reports at least one unmet mandatory requirement or other approved blocking rule. | The skill is unavailable for execution; the user can identify each applicable unmet requirement using the approved reason vocabulary. Do not imply that an optional warning is a blocker. | No execution action is available. The user is shown the approved unmet requirement(s); no remediation action is specified here unless the approved skill/source contract defines it. |
| Empty | A successful catalog read returns no entries for the requested context. This is distinct from a read/eligibility error. | The user can tell that no catalog entries were returned for this context. Do not claim that no skills exist globally or that the data is ineligible unless the approved contract supports that explanation. | No entry can be selected from this response. No recovery action or cause is specified or approved here; do not suggest changing scope or retrying. |
| Error | The system cannot obtain a trustworthy catalog or eligibility response. | The error is distinguishable from an empty catalog and from an ineligible skill. No unresolved entry is represented as eligible. Error details must not expose credentials, raw provider payloads, or unrelated user data. | No entry can be selected or run from an unresolved response. Retry and other recovery/support actions are not specified or approved here. |

The current records do not establish empty-response causes, a complete remediation workflow, retry policy, or exact error taxonomy. The matrix therefore records those actions as unspecified instead of proposing behavior. Applicable contract owners must resolve them before a more specific action is claimed.

## Text and keyboard review questions

- Can a user identify the skill name, choice state, eligibility state, and any blocking reason from text without relying on color, icon, position, or hover?
- Can eligible choices and any permitted recovery/selection actions be reached and operated using a keyboard?
- Is ineligibility communicated without presenting an executable action for that entry?
- When the catalog is empty or fails, is the condition identifiable as a status/error and is focus behavior understandable after recovery?
- How should the selected D04 WCAG 2.2 AA design target and named keyboard/screen-reader checks be applied to these catalog states, and what case-specific evidence belongs in TC45? SR58 requires text and keyboard operation; the selected target does not by itself establish implementation or conformance.

These questions invite design and evidence review; they do not change SR58 or D04's selected accessibility target and do not claim conformance. Any new normative obligation must follow the project change process and founder confirmation where CUS scope changes.

## Acceptance review checklist for TK35 / STK110

A reviewer can determine from this note whether it:

1. Covers eligible, ineligible, empty, and error cases separately.
2. Identifies the information the user needs to understand in each case.
3. Keeps missing-input explanations tied to approved requirement/reason data rather than inventing thresholds or codes.
4. Names the current action for each case or explicitly records that no action is specified/approved, without creating a UI interaction or recovery workflow.
5. Separately records text and keyboard accessibility questions.
6. Describes D02's selected direction and remaining contract/evidence gates accurately, and names TC45 as a planned, not-run evidence reference.
7. Avoids product code, detailed architecture, schema choices, test execution, verification, acceptance, and release claims.

## Traceability and remaining gates

| Record | Relation | Current limit |
| --- | --- | --- |
| CUS04 / CUS05 | Skill choice and data-dependent eligibility outcome | The D02 baseline selects three P0 skills and UTC metric direction. Frozen schemas/fixtures, rubric review, live evaluation, and any remaining applicability or input-contract details stay open. |
| FEAT31 | Explain eligibility and operable catalog states | Proposed capability grouping; does not approve a presentation design. |
| SR11 | Block execution and identify unmet requirements for an ineligible skill | Reason identifiers and exact unmet-input matrix depend on approved skill contracts. |
| SR58 | Make eligible/ineligible choices and reasons clear through text and keyboard operation | SR58 sets text/keyboard behavior; D04 separately selects WCAG 2.2 AA and named accessibility design checks, whose catalog mapping and evidence remain open. |
| TC45 | Planned catalog and accessibility verification | Not run. Requires an approved contract and a runnable candidate for product-level checks. |
| D02 | Skills, applicability, coverage/trend rules, evaluation thresholds | The target skills and core UTC calculation direction are selected in the dated baseline; schemas, fixtures, independently reviewed rubric anchors, and live evaluation remain open. This note does not resolve those gates. |

No product tests, imports, runtime checks, database operations, model calls, rendered-browser checks, or athlete validation are claimed. This document is an acceptance-specification proposal only.