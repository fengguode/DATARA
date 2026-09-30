# P0 requirements engineering and breakdown plan

**Assignment:** Issue #28 / Work package: complete the P0 requirements breakdown — System Architect — Feng Guo (AI agent)  
**Scope:** Requirements engineering and traceability planning for CUS01–CUS10 only. No implementation or detailed technical architecture design is included in this assignment.  
**Status:** Proposal for Quality Manager audit and coordinator integration. D01–D05 remain open; no founder decision or acceptance is implied.

## 1. Milestone and acceptance

The first P0 product milestone remains the approved first-usable-release scope: CUS01–CUS10, as stated in the project brief. This work package prepares complete, traceable requirements for that milestone; it does not add a product promise, implement behavior, or verify the product. Preserve every P0 priority as recorded; sequence delivery by dependency in a separate field/plan, never by changing priority. P1 CUS11–CUS13 and SR22–SR26 remain unchanged and outside this breakdown.

Requirements completion is acceptable when:

- Existing CUS01–CUS10 identifiers, stories, outcomes, and P0 priority are preserved. No CUS-level change is proposed here.
- Every P0 CUS traces through one or more features to its applicable existing SRs and planned work. All existing P0 SRs remain traceable; each uncovered obligation is either a proposed derived SR or a decision/investigation task with rationale and source.
- Each CUS has an assessment of legal, engineering, runtime, architecture, privacy/security, accessibility, operations/backup/retention/recovery, and domain/provenance perspectives. Mark applicability, rationale, linked SRs/tasks, and open gaps. Do not invent legal duties or mark an unassessed perspective complete.
- Each future implementation and verification activity has a bounded task and actionable subtasks. These describe intended outcome, planned owner role, dependencies, relevant CUS/Feature/SR/TC references, and measurable acceptance criteria. They plan future work only; no implementation or verification has started.
- Proposed SRs are atomic, measurable `shall` obligations with source, acceptance criteria stating trigger/result/oracle, and planned verification reference. Existing SR statements and statuses are preserved when adding traceability links.
- Priority remains metadata, separate from titles. Requirement/backlog titles follow `[Type][area]content_of_title`. Feature/task identifiers are stable traceability labels, not system interfaces or architecture decisions.
- The Quality Manager can audit CUS/SR coverage, evidence planning, dependencies, open decisions, and distinct planned/implemented/verified/accepted/released states.

## 2. Requirements organization and decision handling

Organize the backlog and registry as **CUS → Feature → SR → Task → Subtask**, retaining work-package and planned verification references. Keep existing CUS/SR/TK/WP/TC/VAL identifiers and P1 records intact. Allocate new Feature/SR/Task/Subtask/TC identifiers from the reserved ranges in §4; identifiers are append-only and carry no technical meaning.

Use the registry’s existing record organization as the canonical requirements record. The breakdown may add the traceability and planning references needed for this hierarchy, but this assignment does not define a new application schema, persistence model, API, provider integration, FIT implementation, or registry-validation mechanism.

Retain TK01–TK07 as existing work-package aggregates. New bounded TK records point to the relevant aggregate and to one or more STK subtasks; each bounded task has at least one actionable subtask. Preserve TK08 and its P1 scope. Use the existing work-package dependency order. Do not introduce cycles or make a task depend on its aggregate parent.

For each planned item, use status for delivery state and readiness for whether work can proceed. Discovery and requirements drafting remain Proposed when they can proceed with available evidence. Only future work that depends on a founder decision is Blocked on decision. Decision IDs D01–D05 stay open until the founder resolves them; do not choose FIT mappings/limits/conflict tolerances, skill thresholds, providers/credential policies, output contracts, stack/topology, or estimates here. Material customer outcome, priority, supported-scope, public-interface, or data-contract changes go to the founder through the primary.

Future implementation and verification tasks record intended behavior, responsible role, dependencies, outputs, planned checks, and acceptance criteria. They must not prescribe low-level design or imply that work has started or passed. Verification plans identify evidence needed; actual results are recorded later against a fixed candidate and remain distinct from mocked checks, live-model integration, system verification, athlete validation, founder acceptance, and release.

## 3. Requirements completeness and evidence quality

Map existing P0 SR01–SR21 and SR27–SR31 to their relevant feature(s), CUS parent(s), work package, and existing verification cases. Preserve statements and statuses. Keep P1 SR22–SR26 linked to CUS11–CUS13/WP07.

Assess gaps per CUS. A proposed new SR must state its parent CUS, feature, source, applicability perspective, measurable acceptance criteria, and planned TC. Keep it draft/proposed. If the concern depends on external evidence or stakeholder direction, create a bounded investigation/decision task instead of guessing an obligation or threshold. Any applicable perspective left unknown must link to a specific investigation task. Non-applicability needs a reason.

For every P0 feature and every P0 SR, plan at least one future implementation task and one future verification task, each with bounded subtasks. These are traceability and backlog outcomes, not authority to begin implementation. Use the named role roster for planned ownership; a role label is not evidence of participation or execution. Worker owns future implementation; User Tester owns future candidate-specific testing; specialists contribute within their defined role and edit limits.

The existing `scripts/check_requirements.py` may be run after registry integration if the current registry is within its supported scope. Do not add code or extend the checker in this requirements assignment. If the existing check cannot understand the added hierarchy, record its actual result and limitation; do not treat partial checking as complete coverage or product verification. Any subsequent tooling work requires a separate bounded assignment.

## 4. Requirements baseline deliverables, sequencing, and exit criteria

The actionable requirements baseline package consists of: (1) a CUS-to-Feature-to-SR-to-Task-to-Subtask traceability view for all ten existing P0 CUS; (2) a complete map of all existing P0 SRs, with any uncovered obligation identified as a proposed SR or sourced decision/investigation task; (3) eight-perspective applicability/gap assessments per CUS; (4) bounded future delivery and verification tasks with owners, dependencies, acceptance outcomes and planned evidence; (5) the open-decision and dependency sequence; and (6) a Quality Manager audit record with limitations. These are requirements and backlog artifacts, not product implementation or new user-facing capability commitments.

Preserve the existing roadmap sequence and its dependencies. Resolve or explicitly gate source-contract decisions before source-dependent implementation (D01); skill scope/evaluation decisions before dependent skill and eligibility delivery (D02); customer-connection and credential-boundary decisions before model-connection delivery (D03); dashboard/API outcome and contract decisions before dependent output delivery (D04); and stack/topology/estimates only after D01–D04 (D05). These decision relationships determine readiness and delivery order only. They do not change the existing P0 priority of CUS01–CUS10 and do not select a technical design.

Requirements-baseline exit requires all of the following:

- The full CUS/Feature/SR/Task/Subtask links and applicable WP/TC references are present; every existing P0 SR is covered; gaps, sources, assumptions, and open decisions are explicit.
- Quality Manager — Wang Xiaofeng completes the full coverage/evidence/decision/dependency audit against the agreed rubric and records findings and limits.
- Reviewer — Dennis Windmaier independently reads the integrated requirements diff and confirms traceability and scope preservation, or records findings for correction.
- The founder resolves the open product-contract decisions required to freeze the P0 baseline and explicitly confirms the baseline. No exchange among agents substitutes for this confirmation.
- No CUS or SR is labeled Verified or Accepted by this requirements-planning work. Verification requires candidate-specific product evidence; acceptance remains a separate founder decision. Release remains a separate authorized gate.
## 5. Drafting boundaries and stable ID reservations

Three independent drafting groups own non-overlapping CUS scopes. Reserved IDs are administrative traceability labels only; gaps are allowed and do not encode an architecture or implementation order.

| Group | CUS scope | Feature IDs | New derived SRs | Bounded Task IDs | Subtask IDs | Planned TC IDs |
| --- | --- | --- | --- | --- | --- | --- |
| A | CUS01–CUS03 | FEAT01–FEAT03, FEAT21–FEAT29 | SR32–SR49 | TK09–TK29 | STK001–STK099 | TC21–TC39 |
| B | CUS04–CUS06 | FEAT04–FEAT06, FEAT30–FEAT39 | SR50–SR69 | TK30–TK49 | STK100–STK199 | TC40–TC59 |
| C | CUS07–CUS10 | FEAT07–FEAT10, FEAT40–FEAT49 | SR70–SR89 | TK50–TK79 | STK200–STK299 | TC60–TC79 |

Groups provide registry fragments only within the agreed requirements fields and IDs. Each fragment maps existing SRs by reference without changing their statements/statuses; proposed SRs and future tasks include only requirements-level acceptance/outcomes, owners, dependencies, decision links and planned evidence references. Cross-CUS requirements are proposed once and referenced by other groups. The primary resolves genuine overlap before integration.

Quality Manager — Wang Xiaofeng audits the complete breakdown against the agreed rubric before integration. The Worker then integrates approved requirements content into the canonical registry and synchronized requirements documents under a separate explicit assignment. The primary coordinates, resolves review findings, and records GitHub status. No agent exchange substitutes for founder decision or acceptance.

## 6. Open decisions and completion boundaries

D01–D05 remain open as recorded in the decision register. D06–D07 and CUS11–CUS13 remain P1/later scope. The founding product constraints remain in force: source-first supported data; deterministic ingestion/preparation; provider-independent skills; customer-owned model access for analysis; deterministic eligibility; explicit unsupported-demand explanations; user-selected skill/model combinations; persistent history; and dashboard/database plus read-only API at P0.

This package is complete only as requirements planning once traceability and quality review pass. That state does not mean any product behavior is implemented, system-verified, accepted, or released. The first P0 product milestone still requires its separate evidence and founder gates under the validation and lifecycle plans.

