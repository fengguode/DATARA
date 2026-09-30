# P0 requirement breakdown plan

**Assignment:** Issue #28 — System Architect — Feng Guo (AI agent)  
**Scope:** Design/schema plan only. This document proposes a registry-v3 contract and drafting sequence; it does not edit the registry, human-readable requirement records, checker, or product scope.  
**Affected scope:** CUS01–CUS10 (P0); existing CUS11–CUS13 and SR22–SR26 remain P1 and out of this P0 decomposition.  
**State:** Proposal for Quality Manager review and coordinator approval. Founder decisions D01–D05 remain open.

## 1. Outcome and invariants

Represent the full traceable work hierarchy as **CUS → Feature → SR → Task → Subtask**, with work package and verification links retained. Every P0 CUS has one or more bounded features; every applicable existing P0 SR maps to a feature; missing system obligations are recorded as proposed derived SRs or explicit decision tasks before implementation planning is complete; every bounded Task has one or more actionable STK subtasks. No hierarchy row implies approval, implementation, verification, acceptance, or release.

Preserve all current identifiers and meanings: CUS01–CUS13, SR01–SR31, TK01–TK08, WP01–WP07, TC01–TC20, VAL-P0. Keep P1 records intact and linked as they are. New identifiers are append-only, never recycled, and stored as data fields rather than inferred from titles or array order.

## 2. Frozen registry schema v3 contract

This contract is frozen for the three drafting fragments. Keep current top-level arrays and add `features`, `subtasks`, and `perspective_assessments`. Preserve all legacy fields and IDs. New fields are additive; do not rename or renumber legacy records. JSON fragments must conform to these fields and enums before Worker integration.

### Record shapes

```json
{
  "feature": {
    "id": "FEAT01",
    "title": "[Feature][backend]Validate supported source files",
    "statement": "Proposed bounded capability statement",
    "priority": "P0",
    "status": "Proposed",
    "readiness": "Proposed",
    "parent_cus_ids": ["CUS01"],
    "sr_ids": ["SR01"],
    "work_package": "WP01",
    "dependencies": [],
    "owner_role": "System Architect — Feng Guo",
    "acceptance_criteria": ["Given ... when ... then ...; oracle: ..."],
    "outputs": ["Reviewable contract artifact or observable behavior"],
    "evidence_ids": ["TC21"],
    "decision_ids": ["D01"],
    "source": ["docs/project-brief-and-roadmap.md"],
    "notes": "Proposal; not approved"
  },
  "system_requirement": {
    "id": "SR32",
    "title": "[SR][backend]Classify supported source records",
    "cus_ids": ["CUS01"],
    "feature_ids": ["FEAT01"],
    "priority": "P0",
    "statement": "The system shall ...",
    "acceptance_criteria": ["Trigger, observable result, and oracle; include explicit negative cases where applicable."],
    "source": ["docs/project-brief-and-roadmap.md"],
    "perspective_tags": ["engineering", "runtime"],
    "verification_ids": ["TC21"],
    "work_package": "WP01",
    "decision_ids": ["D01"],
    "status": "Draft derived requirement"
  },
  "task": {
    "id": "TK09",
    "parent_task_id": "TK01",
    "title": "[Task][backend]Draft supported record matrix",
    "priority": "P0",
    "status": "Planned",
    "readiness": "Proposed",
    "work_kind": "contract_design",
    "work_package": "WP01",
    "cus_ids": ["CUS01"],
    "feature_ids": ["FEAT01"],
    "sr_ids": ["SR32"],
    "requirement_ids": ["CUS01", "SR32"],
    "dependencies": [],
    "owner_role": "System Architect — Feng Guo",
    "child_task_ids": [],
    "subtask_ids": ["STK001"],
    "acceptance_criteria": ["Trigger, observable result, and oracle."],
    "outputs": ["Versioned source matrix draft"],
    "evidence_ids": ["TC21"],
    "decision_ids": ["D01"],
    "verification_ids": ["TC21"],
    "source": ["docs/management/wp01-requirements-package.md"]
  },
  "subtask": {
    "id": "STK001",
    "task_id": "TK09",
    "title": "[Task][backend]List source record categories",
    "statement": "Bounded actionable subtask",
    "priority": "P0",
    "status": "Planned",
    "readiness": "Proposed",
    "work_package": "WP01",
    "cus_ids": ["CUS01"],
    "feature_ids": ["FEAT01"],
    "sr_ids": ["SR32"],
    "dependencies": [],
    "owner_role": "System Architect — Feng Guo",
    "acceptance_criteria": ["Trigger, observable result, and oracle; include explicit negative cases where applicable."],
    "outputs": ["Reviewable JSON fragment section"],
    "evidence_ids": ["TC21"],
    "decision_ids": ["D01"],
    "verification_ids": ["TC21"],
    "source": ["docs/management/wp01-requirements-package.md"]
  },
  "perspective_assessment": {
    "cus_id": "CUS01",
    "perspectives": {
      "legal": {"applicability": "unknown", "rationale": "Evidence not yet assessed", "sr_ids": [], "task_ids": ["TK09"]},
      "engineering": {"applicability": "applicable", "rationale": "Source classification is required", "sr_ids": ["SR32"], "task_ids": ["TK09"]},
      "runtime": {"applicability": "unknown", "rationale": "Limits require D01 evidence", "sr_ids": [], "task_ids": ["TK09"]},
      "architecture": {"applicability": "applicable", "rationale": "Versioned source boundary", "sr_ids": ["SR32"], "task_ids": ["TK09"]},
      "privacy_security": {"applicability": "unknown", "rationale": "Assessment open", "sr_ids": [], "task_ids": ["TK09"]},
      "accessibility": {"applicability": "unknown", "rationale": "Error presentation to assess", "sr_ids": [], "task_ids": ["TK09"]},
      "operations_backup_retention_recovery": {"applicability": "unknown", "rationale": "Operational lifecycle to assess", "sr_ids": [], "task_ids": ["TK09"]},
      "domain_provenance": {"applicability": "applicable", "rationale": "FIT source evidence and athlete-domain limits", "sr_ids": ["SR32"], "task_ids": ["TK09"]}
    }
  }
}
```

### IDs, status, readiness and links

- Preserve CUS01–CUS13, SR01–SR31, TK01–TK08, WP01–WP07, TC01–TC20, and VAL-P0 exactly. CUS records gain `feature_ids[]`; existing SRs gain `feature_ids[]`, `source[]` if absent, and `perspective_tags[]` when relevant. Existing P0 SR statements and status are not rewritten by mapping. Existing P1 records remain unchanged.
- New Feature IDs use the non-overlapping FEAT ranges reserved in §3; FEAT01–FEAT10 are initial candidates; new derived SR IDs use the group reservations in §3. New aggregate-child task IDs use the reserved `TKnn` ranges. New actionable leaves use `STKnnn`. New planned verification cases use `TCnn`. IDs are globally unique and append-only; do not recycle unused reservations without coordinator approval.
- Feature and new SR titles use `[Feature][area]content_of_title` and `[SR][area]content_of_title`; Task and Subtask titles use `[Task][area]content_of_title`. Keep IDs and priority out of titles. Existing CUS/SR/TK titles retain their current IDs and wording unless separately authorized. `priority` is separate metadata; new records inherit linked CUS priority. Cross-priority records require rationale and must not pull P1 behavior into P0.
- Allowed new-record `status`: Feature=`Proposed`; new SR=`Draft derived requirement`; new child Task/Subtask=`Planned`. Preserve legacy status values exactly. Status is delivery/requirement state, not readiness or evidence. Every new Task has `work_kind` exactly one of `decision_research`, `contract_design`, `implementation`, `verification`, `quality_audit`, or `release_review`; use `decision_research` for bounded perspective/gap investigations.
- Allowed `readiness`: `Proposed`, `Blocked on decision`, `Ready for implementation`. It says whether direction/dependencies are clear enough to start; it never means approved, implemented, or verified. `decision_ids[]` lists D01–D07 gates; unresolved required decisions set dependent work to `Blocked on decision`. For records with no open decision, use `Ready for implementation` only when all scope and dependencies are resolved, otherwise `Proposed`.
- `evidence_ids[]` contains planned TC identifiers only. It is a plan link, not real test evidence. `verification_ids[]` is preserved for compatibility and must match the same planned TC references. Actual evidence remains in the designated evidence records and may not be invented in fragments.
- Every new SR has a compliant title, one or more atomic measurable `acceptance_criteria[]`, `source[]`, and at least one `verification_ids[]`/`evidence_ids[]` planned TC. Each criterion states trigger, observable result, and oracle and includes relevant negative cases. If an oracle/threshold depends on D01–D05, state the decision dependency, leave the threshold unresolved, and keep status draft/readiness blocked.
- `owner_role` is the exact configured role/name from `docs/team/roster.md`; it is a planned owner, not evidence the role/person actually participated. Each task and subtask has outputs, measurable acceptance, upward CUS/feature/SR links, WP, TC IDs, dependencies, owner, and decision IDs. Each new child Task has a `parent_task_id` pointing to existing aggregate TK01–TK07. Existing TK01–TK07 preserve their aggregate meaning and gain `child_task_ids[]`; TK08 is P1 and unchanged. Every leaf is an STK record: new child TKs must have at least one child STK; do not declare an un-subtasked small-leaf exception.
- The per-CUS `perspective_assessments` array contains exactly one record for each CUS01–CUS10, with eight perspective entries: `legal`, `engineering`, `runtime`, `architecture`, `privacy_security`, `accessibility`, `operations_backup_retention_recovery`, `domain_provenance`. Each entry has `applicability` (`applicable`, `N/A`, `unknown`), a rationale, `sr_ids[]`, and `task_ids[]`. N/A requires a reason; unknown requires a bounded task/gap. Perspective assessment is once per CUS, not duplicated as eight mandatory fields on every SR. SR `perspective_tags[]` are optional tags for traceability.

Checker requirements for later integration: unique stable IDs; every reference resolves; reciprocal CUS-feature-SR links; each P0 SR maps to at least one feature; every P0 CUS has a feature and one eight-entry assessment; all task/subtask references resolve upward to CUS/feature/SR/WP/TC; child-task parent/children links are reciprocal; every new bounded child Task has one or more STK leaves; each P0 Feature and each P0 SR links at least one bounded `implementation` Task and one bounded `verification` Task with STK leaves; dependency graph is acyclic; evidence IDs are valid planned TCs; and priority inheritance is consistent. Registry validation proves structure/planned coverage only, never requirement approval or product evidence.
## 3. Identifier allocation and P0 feature map

### Reserved ID ranges

These exact reservations supersede earlier drafts. Gaps are allowed; do not renumber or use IDs outside the assigned group range. Feature ranges include expansion IDs after the initial one-per-CUS proposal.

| Record IDs | Group A | Group B | Group C |
| --- | --- | --- | --- |
| Features | FEAT01–FEAT03, FEAT21–FEAT29 | FEAT04–FEAT06, FEAT30–FEAT39 | FEAT07–FEAT10, FEAT40–FEAT49 |
| New derived SRs | SR32–SR49 | SR50–SR69 | SR70–SR89 |
| Bounded child Tasks | TK09–TK29 | TK30–TK49 | TK50–TK79 |
| Subtask leaves | STK001–STK099 | STK100–STK199 | STK200–STK299 |
| New planned TCs | TC21–TC39 | TC40–TC59 | TC60–TC79 |

The initial feature map below uses the first ID in each CUS reservation; additional reserved features may split a CUS only when the fragment explains the distinct boundary. These are proposals, not approved functionality.

| CUS | Proposed feature record(s) | Initial feature boundary |
| --- | --- | --- |
| CUS01 | FEAT01 | Publish supported FIT source contract and acceptance/rejection diagnostics. D01 gate. |
| CUS02 | FEAT02 | Preserve original uploads, normalized history, duplicate and conflict handling. D01 identity/conflict policy gate. |
| CUS03 | FEAT03 | Deterministic normalization, quality processing, metrics and versioned skill-input preparation. |
| CUS04 | FEAT04 | Specify and evaluate the baseline provider-independent skill library. D02 gate. |
| CUS05 | FEAT05 | Deterministic eligibility and visible unmet-input explanations before execution. |
| CUS06 | FEAT06 | Protect customer credentials and execute through explicitly selected supported model connections. D03 gate. |
| CUS07 | FEAT07 | Manual run lifecycle, output validation and explicit failure recording. |
| CUS08 | FEAT08 | Immutable, evidence-linked result history and run provenance. |
| CUS09 | FEAT09 | Predefined saved-results dashboard and authorized read-only output API. D04 gate. |
| CUS10 | FEAT10 | Enforce user isolation across files, credentials, execution and result access. |

This is a starting partition only. During drafting, preserve CUS statements and make additional features where a distinct, independently testable outcome or architecture boundary warrants it. Features do not replace CUS as the customer-outcome level. Avoid new feature scope that alters founder-approved outcomes.

## 4. Completeness and perspective audit

First map every existing P0 SR exactly at least once to its relevant FEAT record, retaining all original parent CUS IDs and verification IDs. Existing P0 set: SR01–SR21 and SR27–SR31. Do not drop or rewrite their obligations while remapping. The P1 SR set SR22–SR26 stays linked to CUS11–CUS13 and WP07 and is not converted to P0.

Then audit each of CUS01–CUS10 across the applicable perspectives, using the schema field above. Areas to explicitly assess include source rights and lawful data handling (without asserting conclusions absent evidence); engineering correctness and deterministic behavior; runtime limits/configuration/observability/backup and recovery; architecture and versioned interfaces; data security, authorization, secret handling and isolation; accessibility for dashboard states and errors; operations, retention, support and failure recovery; and athlete-domain limitations/evidence. Link a covered concern to an existing SR, a proposed derived SR, or a decision task. Record non-applicability with rationale. Record unassessed areas as `unknown` and create a bounded investigation/decision task; do not silently call the SR set complete.

A gap is handled in one of two ways: (a) propose a new SR with explicit CUS parent, feature link, verification case proposal, evidence source, and proposal status; or (b) create a decision/investigation task if the obligation depends on missing stakeholder direction or external evidence. Do not convert an open decision into an approved SR. Any change to the CUS outcome, audience, priority, supported scope, public interface, or material data contract is routed to the founder through the primary before dependent implementation.

## 5. Task and subtask decomposition method

Preserve existing TK01–TK07 as WP-level aggregate records, keeping their IDs, package, requirement coverage, dependencies, and statuses. Add reciprocal `child_task_ids[]` to each aggregate. Add bounded child Task records TK09–TK29 with `parent_task_id` to one of TK01–TK07; do not redefine aggregate meaning. Keep TK08 as P1 unchanged. Every child Task must have one or more actionable STK leaf subtasks; no task-leaf exception is allowed in this decomposition. Each STK is bounded to one reviewable output, with input/action/output, dependencies, owner, acceptance, decision IDs, and planned TC. Use ranges below; allocate only as many IDs as needed and never renumber.

Preserve package dependencies: WP01 contract/decision work precedes dependent WP02–WP05 implementation; WP02 precedes WP03; WP03 precedes WP04; WP05 depends on WP02 and WP04; WP06 depends on all P0 packages. Link all tasks/subtasks upward to CUS, feature, and SR IDs, and downward to planned TC IDs. Decision research and drafting tasks remain runnable at readiness `Proposed`; only dependent implementation is `Blocked on decision` until D01–D05 resolves. Represent needed stakeholder/external research as a task rather than selecting values. New task and STK priorities inherit linked P0 CUS/SR priority. Do not add CUS11–CUS13 or P1 behavior to P0 tasks.

## 6. Independent drafting and integration sequence

The coordinator allocates one JSON fragment per group using the exact frozen shape below. Groups own only their reserved IDs and CUS scope; cross-CUS requirements are proposed by one owning group and referenced (not duplicated) by others. The primary reconciles any genuine cross-group overlap before integration.

```json
{
  "group": "A",
  "cus_ids": ["CUS01"],
  "features": [],
  "existing_sr_links": [],
  "system_requirements": [],
  "tasks": [],
  "subtasks": [],
  "perspective_assessments": [],
  "verification_cases": [],
  "notes": []
}
```

Each array entry must use the record shape in §2. `features` contain FEAT IDs; `existing_sr_links` only add `feature_ids[]`, `source[]`, and optional `perspective_tags[]` to existing SR records, without changing their statement/status; `system_requirements` contain only new SRs; `tasks` contain bounded TK children of legacy aggregates; `subtasks` contain all leaf work as STK records; `perspective_assessments` contain exactly one eight-entry matrix per owned CUS; `verification_cases` contain only reserved new TC records; `notes` record assumptions/open questions, never duplicate backlog items. Existing CUS/SR/TK/TC rows are referenced by ID, never copied as duplicate records into fragments. The fragment may include a `coverage`/`open_questions` object only if the coordinator asks for it; traceability lives in fields, not a second competing backlog.

| Group | CUS ownership | Feature IDs | New SR IDs | Child Task IDs | STK leaf IDs | New TC IDs |
| --- | --- | --- | --- | --- | --- | --- |
| A | CUS01–CUS03 | FEAT01–FEAT03, FEAT21–FEAT29 | SR32–SR49 | TK09–TK29 | STK001–STK099 | TC21–TC39 |
| B | CUS04–CUS06 | FEAT04–FEAT06, FEAT30–FEAT39 | SR50–SR69 | TK30–TK49 | STK100–STK199 | TC40–TC59 |
| C | CUS07–CUS10 | FEAT07–FEAT10, FEAT40–FEAT49 | SR70–SR89 | TK50–TK79 | STK200–STK299 | TC60–TC79 |

Before drafting, Quality Manager — Wang Xiaofeng supplies/aligns the traceability and evidence completeness rubric. The received rubric is reflected in §2: each CUS receives all eight perspective assessments; each new SR has a title, measurable `shall` acceptance, source, and planned TC; every task/STK has upward links, WP, TC, owner, dependencies, acceptance and outputs; priority inherits; unresolved thresholds remain proposals/D gates. No group edits the shared registry or human-readable requirement files.

After fragment reviews, assigned Worker integrates fragments into `requirements-registry.json`, synchronizes requirement/management docs and checker in the explicit scope, and preserves legacy IDs/statuses. System Architect reconciles traceability; specialists review applicable domain claims; Quality Manager audits against the rubric; Reviewer inspects the final diff. Primary integrates and reports. Run `python scripts/check_requirements.py` after registry integration and report its actual result; it checks structure/planned coverage only, not product verification.
## 7. Decision and evidence guardrails

D01–D05 remain open as recorded. In particular, do not select FIT mappings/limits/conflict tolerances, skill thresholds/rubrics, providers/credential retention, API pagination/auth details, stack/topology, or estimates in this plan. Proposed options stay proposals until founder resolution. D06–D07 and CUS11–CUS13 remain P1/later scope.

All newly proposed SRs remain draft derived requirements until the normal approval path resolves applicable contracts and stakeholder decisions. No requirement is marked verified based on task completion, schema/checker results, mock tests, or review comments alone. Live model integration, system verification, rendered UI checks, athlete validation, founder acceptance, and release each remain distinct gates with candidate-specific evidence.














