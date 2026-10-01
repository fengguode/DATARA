# Product baseline onboarding assessment — Yu Wang

**Assignment:** issue [#279](https://github.com/fengguode/DATARA/issues/279)
**Work package:** product/customer baseline and landing-page architecture handoff
**Affected needs:** CUS01–CUS10 for P0 expectation and workflow accuracy; CUS11–CUS13 for clear P1 boundary; applicable SR records, with no change to canonical scope.
**Coordinator:** Primary Coordinator — Yi Tang (Codex primary).
**Current status:** active documentation work; no product implementation or publication.

## Role and runtime

The Product Manager — Yu Wang role definition, roster entry and saved knowledge are added through the coordinator's integration branch. The role definition requests gpt-6.1-sol with medium reasoning effort. The present environment does not provide a control or attestation that activates a repository persona or proves a separate Yu Wang runtime. Therefore role configuration is recorded, but role activation and named-person contribution are unconfirmed. This Codex primary performs the assigned integration; no participation is attributed to Yu unless an actual bounded agent run is recorded later.

## Product purpose and users

DATARA's approved direction is a persistent personal data home that prepares supported sources with deterministic conventional software and turns them into useful outcomes through reusable expertise. P0 begins with athletes manually uploading supported Garmin FIT files. Users should retain training history, see data readiness, select eligible skills, choose their own supported model API access for manual analysis, revisit evidence-backed results, and retrieve saved data through a predefined dashboard and read-only API.

The product principles are source-first processing, no model use during ingestion/preprocessing, provider-independent skill definitions, deterministic eligibility with visible gaps, customer control of skill/model selections, persistent result history, and user isolation. A registry entry or design proposal is not evidence that any feature works.

## P0, deferred scope and maturity

P0 is the full first usable athlete workflow CUS01–CUS10 across WP01–WP06. P1 covers recommendations, routines and comparisons (CUS11–CUS13). Commercial mechanisms, source-to-skill automation, expert creator tooling and new data domains remain deferred. DATARA's own model is for P1 recommendations only; analysis uses customer-selected API access.

The implementation plan PR #278 merged on 1 October 2026 to main at merge commit ca689afccb9a6887e789b2975bd953e396b03eae. It sequences existing work and evidence gates. It does not implement product behavior. Its source issue #277 reports a successful planning/publication review and 3 Ready evidence-preparation records among 238 P0 records at that snapshot. The live board is authoritative and should be refreshed before a later status report. Product coding is gated by G0: approved TK01/TK02 contracts, D01–D05 decisions or applicability, fixture provenance/rights, and pinned runtime/setup/check evidence. Product test cases and final athlete journey remain Not run; there is no product candidate acceptance or release in the reviewed evidence.

## Open decisions and dependencies

- D01: authoritative FIT evidence/version, supported mappings/variants/limits, conflict rules, and fixture provenance/rights.
- D02: baseline skills, coverage and eligibility rules, evaluation rubric and thresholds.
- D03: supported customer-model connections, sequence, credential boundary and safe error behavior.
- D04: dashboard outcome and read-only API resources/details.
- D05: stack, deployment topology, operational/accessibility scope and evidence-based estimates.
- D06–D07 govern later P1/commercial and source-rights/source-to-skill concerns.

These remain open in the decision register. Product documents must not choose an option implicitly. Founder approval is required for material CUS-level changes and public commitments.

## Documentation gaps and contradictions

1. The initial shared checkout on another active task branch contained unresolved conflict markers in management records. The isolated onboarding branch is based on the latest merged main after PR #278 and does not carry those unrelated working-tree edits. This task leaves the other checkout untouched.
2. docs/project-brief-and-roadmap.md describes the desired staged product but does not state clearly in its opening section that the current product is planning-only and unavailable to customers. The new customer overview states maturity explicitly without changing the approved brief.
3. Customer documentation did not provide a single current-status explanation, public-safe progress format, or complete landing-page content/handoff. New drafts fill that gap.
4. The registry checker and planning review are easy to confuse with product verification. The new drafts explicitly separate planning evidence from implementation, verification, founder acceptance and release.
5. FIT/provider support, credential handling, retention, deployment environment, legal duties, supported models and evaluation thresholds are not settled. Public drafts identify these as undecided and avoid invented assurances.
6. The GitHub board is the status authority. Issue #279 is in the DATARA Project with In progress, P0, Requirements, and Primary Coordinator — Yi Tang. The coordinator read the fields back through the board UI and recorded the change on the issue.

## Proposals and approval boundary

Documentation-only changes preserve the approved direction and describe all product capabilities as intended or planned. Proposed changes are: add the Yu Wang role definition/roster/knowledge; provide the customer overview, roadmap/progress draft and landing-page brief; and maintain a claim-by-evidence cadence. No CUS/SR change, supported capability, date, provider, legal assertion, data retention term, material product promise, or publication is proposed as approved.

The landing page is in architecture/design handoff only. Page implementation is a separate gated task after UI design, feasibility, stack and hosting decisions. External publication requires the project's approval process and founder approval for material commitments.

## Maintenance and handover

Yu owns customer-facing product content, claim accuracy and landing-page content. Authoritative inputs: product brief and dated brainstorming record for intent/history; CUS/SR registry, decision register and traceability for requirements; P0 implementation plan and GitHub Project for sequence/live status; candidate-specific checks, founder decisions, release records for maturity claims. Review workflow, role-attribution policy and saved Yu knowledge govern how updates are assigned and evidenced.

Update affected documents after approved requirements or decisions change; task ownership/dependency/status changes; work begins, completes or blocks; implementation evidence, verification, founder acceptance or release status changes; or customer feedback is accepted as a change to direction. Record source links, candidate/version, actual result, reviewer, date, limits and any approval. Recheck the board before publishing counts. Keep issue/Project as status, not a duplicate backlog. Public announcement drafts remain internal until reviewed and approved.


## Customer-document traceability map

The table keeps requirement IDs out of customer copy while making each major claim traceable. SR ranges below mean the listed existing identifiers for those outcomes, not every ID in the numeric interval.

| Deliverable claims | CUS IDs | Applicable SR IDs | Authoritative source and evidence status |
| --- | --- | --- | --- |
| Product purpose, supported-source and preparation principles, retained history, model choice, manual execution, result views and isolation | CUS01–CUS10 | Source/data: SR01–SR07, SR27–SR28, SR32–SR34; skills/eligibility/model/execution: SR08–SR15, SR29–SR30, SR50–SR59, SR70, SR74, SR76; history/output/isolation: SR16–SR21, SR31, SR71–SR76 | Product brief and current CUS/SR registry define intent; decision register and WP01 package define open proposals; implementation plan and Project define sequence/status. No product implementation or verification is evidenced. |
| Deferred recommendations, routines, comparisons and later expansion boundaries | CUS11–CUS13 | SR22–SR26 | Product brief and requirements/registry; explicitly P1/deferred, not P0 availability. |
| Roadmap stages and progress labels | CUS01–CUS13 (scope boundaries) | Applicable P0/P1 SRs above | Merged PR #278 and issue #277 support completion of planning only; current task status belongs to Project #3; product maturity remains Not run for verification/acceptance/release per validation plan and lifecycle policy. |
| Landing-page workflow, feedback expectations, data/model limits and user journeys | CUS01–CUS10; feedback path is a proposed route, not an approved product channel | SR01–SR21, SR27–SR34, SR50–SR59, SR70–SR76 as applicable | Product brief and decision register for intended behavior/open choices; landing brief is a design/content proposal. WCAG 2.2 AA is proposed pending owner approval, not a compliance claim. |

## Review and candidate evidence

The initial read-only customer-comprehension, UI-design, feasibility, Reviewer and QM findings are recorded in docs/team/reviews/yu-wang-onboarding-review.md; each disposition is explicit. Candidate-SHA confirmations remain pending before draft-PR creation. Project fields are reconciled and read back on issue #279. Checks are documentation/configuration checks only; product verification, athlete validation, acceptance and release remain separate and not run.
