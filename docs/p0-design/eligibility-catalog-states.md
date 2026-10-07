# Eligibility catalog state and accessibility acceptance note

Status: requirements-design proposal for TK35 / STK110. It is not a product decision, UI design, implementation contract, verification result, acceptance, or release.

Work package: WP03 — baseline skills and eligibility pipeline  
Affected stories/features/requirements: CUS04, CUS05; FEAT31; SR11, SR58.  
Parent task: [TK35 / #134](https://github.com/fengguode/DATARA/issues/134).  
Subtask: [STK110 / #206](https://github.com/fengguode/DATARA/issues/206).  
Planned verification: TC45.  
Open decision: D02.  
Coordinator: Primary Coordinator — Yi Tang. GitHub publisher: fengguode.

## Scope and boundaries

This note translates the existing acceptance criteria for four catalog conditions—eligible, ineligible, empty, and error—into reviewable outcome questions. It does not choose the baseline skill shortlist, skill declarations, input thresholds, history coverage, quality limits, reason-code vocabulary, UI layout, control pattern, exact user-facing copy, or an accessibility conformance target. D02 remains open.

The catalog communicates deterministic eligibility before any analysis. An eligible entry is not a completed assessment or recommendation. An ineligible entry cannot be submitted for execution. Viewing or explaining eligibility makes no model call. No UI state may imply a result that the available source data and approved skill contract do not support.

The state names below are review labels for the acceptance cases, not proposed API values, database enums, or required literal strings.

## Outcome matrix

| Case | Observable condition to distinguish | Information that must be understandable | Candidate action question (not selected) |
| --- | --- | --- | --- |
| Eligible | The approved eligibility contract reports the skill as eligible for the current selected data scope. | The skill is available for the user's explicit choice. The state must not imply that a model was called, that analysis ran, or that an outcome is guaranteed. | Which explicit selection action is appropriate, and what confirmation is required before any later run? |
| Ineligible | The approved contract reports at least one unmet mandatory requirement or other approved blocking rule. | The skill is unavailable for execution; the user can identify each applicable unmet requirement using the approved reason vocabulary. Do not imply that an optional warning is a blocker. | Which remediation, if any, is supported by the source/skill contract? If none is established, what non-misleading next step is available? |
| Empty | A successful catalog read returns no entries for the requested context. This is distinct from a read/eligibility error. | The user can tell that no catalog entries were returned for this context. Do not claim that no skills exist globally or that the data is ineligible unless the approved contract supports that explanation. | Should the state explain a missing catalog, a scope with no matching entries, or another approved cause? What action is actually available? |
| Error | The system cannot obtain a trustworthy catalog or eligibility response. | The error is distinguishable from an empty catalog and from an ineligible skill. No unresolved entry is represented as eligible. Error details must not expose credentials, raw provider payloads, or unrelated user data. | Is retry available for this error class, and what safe recovery or support action is approved? |

The current CUS/SR records do not establish the causes of an empty response, complete remediation actions, retry policy, or exact error taxonomy. These remain questions for the applicable contract owners.

## Text and keyboard review questions

- Can a user identify the skill name, choice state, eligibility state, and any blocking reason from text without relying on color, icon, position, or hover?
- Can eligible choices and any permitted recovery/selection actions be reached and operated using a keyboard?
- Is ineligibility communicated without presenting an executable action for that entry?
- When the catalog is empty or fails, is the condition identifiable as a status/error and is focus behavior understandable after recovery?
- Which additional text alternatives, focus behavior, status announcements, responsive checks, or formal conformance target apply to TC45? The current SR58 requires text and keyboard operation but does not set those detailed criteria or a conformance level.

These questions invite review; they do not silently extend SR58 or adopt a WCAG conformance target. Any new normative obligation must follow the project change process and founder confirmation where CUS scope changes.

## Acceptance review checklist for TK35 / STK110

A reviewer can determine from this note whether it:

1. Covers eligible, ineligible, empty, and error cases separately.
2. Identifies the information the user needs to understand in each case.
3. Keeps missing-input explanations tied to approved requirement/reason data rather than inventing thresholds or codes.
4. Identifies a candidate action question for each case without approving a UI interaction or workflow.
5. Separately records text and keyboard accessibility questions.
6. Names D02 and TC45 as unresolved decision/evidence references.
7. Avoids product code, detailed architecture, schema choices, test execution, verification, acceptance, and release claims.

## Traceability and remaining gates

| Record | Relation | Current limit |
| --- | --- | --- |
| CUS04 / CUS05 | Skill choice and data-dependent eligibility outcome | D02 shortlist, applicability, thresholds, and evaluation remain open. |
| FEAT31 | Explain eligibility and operable catalog states | Proposed capability grouping; does not approve a presentation design. |
| SR11 | Block execution and identify unmet requirements for an ineligible skill | Reason identifiers and exact unmet-input matrix depend on approved skill contracts. |
| SR58 | Make eligible/ineligible choices and reasons clear through text and keyboard operation | The requirement does not establish visual design or a formal conformance target. |
| TC45 | Planned catalog and accessibility verification | Not run. Requires an approved contract and a runnable candidate for product-level checks. |
| D02 | Skills, applicability, coverage/trend rules, evaluation thresholds | Open; this note does not resolve it. |

No product tests, imports, runtime checks, database operations, model calls, rendered-browser checks, or athlete validation are claimed. This document is an acceptance-specification proposal only.