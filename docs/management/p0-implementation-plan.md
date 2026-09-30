# First P0 milestone implementation roadmap and plan

Status: planning proposal; independent content review PASS, all238 Project records published with fresh authenticated readback PASS; independent publication QA PASS. Final candidate confirmation is reported on issue #277 and the linked pull request. Tracking: [issue #277](https://github.com/fengguode/DATARA/issues/277); Project: https://github.com/users/fengguode/projects/3. Baseline: merged main `cd6bbe807a539337b50b96fa02a883172a56bc3e`. Planning branch: `codex/p0-implementation-plan`. Coordinator: Yi Tang; planning contributor: Architect Feng Guo; quality lead/final process confirmer: Wang Xiaofeng; independent technical reviewer: Dennis Windmaier. All names identify AI roles. Founder owns CUS/material choices and final athlete acceptance.

## Target and readiness

The first milestone is the **complete P0 first usable athlete release**, the existing GitHub milestone #1: manual supported Garmin FIT uploads, persistent history, deterministic preparation, provider-independent evaluated baseline skills, deterministic eligibility, customer-selected model access/manual execution, saved result history, predefined dashboard, authorized read-only API and user isolation. It spans CUS01–CUS10 and WP01–WP06. W1 below is an intermediate data-home gate; it does not replace the complete milestone. P1, recommendations/routines, commercial mechanisms and source-to-skill automation remain excluded.

**Ready next:** assign existing TK09/STK001/STK002 for bounded source/fixture evidence inventory under WP01. **Product coding is not yet ready:** G0 requires approved TK01/TK02 contracts, D01–D05 decisions/approved applicability, pinned runtime/setup/check commands and lawful controlled fixture evidence. This plan orders the work to reach that gate; it does not approve a stack, provider, source mapping, threshold, legal duty or public interface. No coding, detailed architecture design, environment installation, deployment or product verification happens in this planning task.

Existing 64 P0 Tasks and 95 Subtasks are mapped exactly in [the machine-readable plan](p0-implementation-plan.json), reusing all existing issue/Project identities. All 238 P0 requirement records remain the single shared backlog. This document is a roadmap/content mirror, not a second status board. A Ready assignment means its bounded preparation can be assigned; it does not authorize coding or assert a resolved decision.

## Sequence and gate semantics

`Plan order` is a dependency-valid traversal and a sorting aid, not a date, duration, token estimate or forced serial schedule. `Plan wave` groups tasks; parallel execution is allowed only when all inputs are fixed and exclusive file ownership is recorded. Tasks and Subtasks retain canonical direct dependencies, source work-package assignments, decision references and original priority/acceptance. The JSON separately records `execution_work_package`/`execution_wp_dependencies` for the parent activity and `inherited_decision_ids` for parent topics. For example STK007/STK008 and STK015/STK016 retain their source WP01/WP02 while their verification activity executes with the parent WP06 task. Research topics do not imply prerequisite approval. The plan adds explicit package/verification completion prerequisites. Aggregate TK01–TK07 are completion gates, not duplicate implementation assignments and not prerequisite parents that prevent their own children from starting.

W0 gathers evidence and prepares contract/decision options across the original WPs before product execution. Some D02/D03 research is registered in WP03/WP04 but feeds WP01 approval. Scheduling that **pre-code decision preparation** early does not complete those product packages or waive their implementation gates. Similarly, WP06 tests can collect candidate-specific slice evidence as implementations land; final WP06 completion still waits for WP01–WP05 and the complete verification/athlete gates. The plan makes this scheduling interpretation explicit rather than deleting canonical package dependencies. Each cross-package preparation assignment must be identified as preparation in its issue; downstream implementation remains Backlog until approved prerequisites exist.

| Wave | Outcome | Existing Task IDs | Exit gate |
| --- | --- | --- | --- |
| W0 | Evidence, contracts and founder decisions | TK09, TK13, TK14, TK17, TK20, TK30, TK31, TK32, TK33, TK34, TK35, TK36, TK37, TK38, TK50, TK51, TK56, TK60, TK63, TK66, TK72, TK73, TK10, TK39, TK40, TK41, TK01, TK02 | G0 coding readiness: TK01/TK02 and D01–D05, runtime/fixtures/commands approved |
| W1 | Validated persistent data home and user isolation | TK11, TK15, TK18, TK67, TK12, TK16, TK19, TK03 | Supported import, immutable originals, dedup/conflicts, deterministic normalization, authorization; TK12/16/19 evidence |
| W2 | Provider-independent baseline skills and eligibility | TK21, TK42, TK44, TK22, TK43, TK45, TK04 | TK21/42/44 outcomes; TK22/43/45 evidence; D02 thresholds approved |
| W3 | Customer-selected connections and manual analysis | TK46, TK52, TK53, TK55, TK70, TK47, TK54, TK71, TK05 | TK46/52/53/55/70 outcomes; TK47/54/71 evidence; actual live model checks distinct from mocks |
| W4 | Saved result history, dashboard and read-only API | TK57, TK58, TK61, TK64, TK68, TK59, TK62, TK65, TK69, TK06 | TK57/58/61/64/68 outcomes; TK59/62/65/69 evidence |
| W5 | Fixed-candidate audit, athlete acceptance and release decision | TK74, TK07 | All P0 SRs/cases evidenced; TK74 QA, TK07/TC15/VAL-P0 founder validation and separate release gate |

### G0: before the first product coding assignment

1. D01: pinned official protocol/profile/decoder evidence, supported variant/field/unit/time/integrity matrix, approved resource limits and conflict policy; fixture origin/terms, hashes, intended oracles and rights/unknowns recorded. TK09→TK10 plus TK13/TK14/TK17/TK20 supply evidence; TK01 closes the source baseline after independent review and founder approval.
2. D02: shortlist and exclusions, eligibility/coverage/trend rules, evaluation layers/rubric/thresholds and source applicability approved. TK30–TK35 supply options; TC80 inspects completeness only. No schema/mock check substitutes for substantive live-model evaluation.
3. D03: selected connection sequence, supported capabilities, customer credential boundary/lifecycle/retention and safe errors approved from official evidence. TK36–TK38 then TK39–TK41; TK50/TK51 and TK66/TK72 cover run/output/security questions. Capability spikes may only be executed in a separately authorized bounded assignment after necessary credentials/budget/scope approval; this plan runs none.
4. D04: dashboard outcome and authorized read-only resource/evidence/pagination/access behavior approved, using TK56/TK60/TK63/TK66/TK72/TK73. A proposal in WP01 is not founder approval.
5. D05: minimal stack and deployment topology, supported platform/browser/accessibility scope and operational ownership approved after D01–D04; future technical work supplies pinned install/run/test commands and estimates based on approved scope. No calendar dates or precise effort numbers are fabricated here. Primary records the decision with its source, affected IDs, alternatives and approval link; Architect prepares choices, Designer covers accessibility, QM audits evidence, Nils checks assumptions.
6. TK02 completes the accepted cross-cutting baseline; Reviewer/QM inspect it, and the founder's material decisions are recorded. The first coding assignment specifies concrete file paths on an isolated branch, disposable approved fixtures, command/environment identity, acceptance cases, owner and independent reviewer. Until those details exist, code-path ownership and product commands are **unassigned**, not guessed.

The register's D05 label originally lists stack/topology/estimates. Its linked TK73/TC78 accessibility scope and TK72 operational gaps are also prerequisites to their affected tasks; the plan exposes those existing gaps without inventing a standard, numerical target, law or architecture.

## First execution queue and handoffs

### First bounded preparation: TK09 (issue #115), STK001 (#173), STK002 (#174)

Owner: Explorer — Wang Licun. Coordinator/integrator/publisher: Yi Tang. Branch proposed for that future assignment: `codex/wp01-fit-evidence`; pull request and execution link will be recorded when available. Scope: inspect supplied official references/version metadata and fixture provenance/terms, name unknowns; no decoder implementation, fixture publication, rights conclusion or product choice. Acceptance remains the canonical TK09/STK criteria: every source has a provenance/version/location row or explicit unknown and no legal conclusion is inferred. Planned TC19/TC24 inspections become evidence only if actually performed and recorded.

Explorer stays read-only and does not contact external services. Yi Tang retrieves authorized official references and writes the eventual inventory under `docs/management/source-evidence/fit-source-inventory.md` and `fixture-provenance.md`; Explorer returns the independent investigation handoff. These are proposed exclusive output paths for that future assignment, not files created or tasks completed here. Source evidence must pin an artifact/version/hash where applicable, retrieval date/status, terms location and unresolved owner decisions; no personal FIT telemetry or credentials go into the public repository.

After TK09: Architect TK10 consumes its accepted inventory. In parallel within W0, TK13/TK14 assess intake/security and conflict choices; the D02/D03/D04 lanes prepare their bounded decision briefs. One owner controls each file; same-role tasks run sequentially if paths overlap. Controller recommends 3–5 dependency-related subtasks per handoff, each retaining its owner and observable acceptance. Delegations stay within the available concurrency limit; nine roles do not imply nine simultaneous writers.

### First product coding bundle, after G0 only

WP02/TK03: Worker Torsten Maier implements TK11, TK15, TK18 and TK67 with their existing leaves and requirements. Order their interfaces so owner authorization is present before protected use; isolated fixture operations must not expose unauthenticated storage. Parallel work is permitted only after agreed source/security boundaries, runtime and distinct file ownership. The first user-visible slice covers supported disposition, immutable originals, duplicate/conflict behavior, model-free normalization/provenance and isolation (CUS01–CUS03/CUS10).

User Tester Abt Hermann verifies TK12/TK16/TK19 against fixed candidates as they land; early two-user file/history probes are collected under the existing WP06/TC14/TK07 evidence record without claiming complete cross-system TC14 or TK69 coverage. Reviewer Dennis reviews each implementation diff; QM Wang Xiaofeng audits candidate identity and case evidence. G1 requires these checks plus the applicable isolation evidence before TK03 is treated complete and W2 begins. A data-home success is not overall P0 acceptance.

### Later bundles

- W2: after TK03/G1, implement scoped inputs, skill definitions/evaluation and eligibility; separate parallel skill and eligibility tracks only after common inputs are approved. TK04 exit includes TK22/TK43/TK45 evidence.
- W3: after TK04/G2, selected customer connections plus run binding/state/output validation and safe outputs. TK05 exit includes TK47/TK54/TK71. Mock routing, schema checks and actual live customer-model integration remain separate; release cannot use mock-only evidence.
- W4: after TK03 and TK05, saved history/evidence, dashboard/API and identity-bound UI. TK06 exit includes TK59/TK62/TK65/TK69 and accessibility checks with D04/D05-approved setup.
- W5: QM TK74 audits final traceability/evidence; Primary TK07 integrates all P0 SR/case results for one fixed candidate. User Tester performs TC15 with the athlete; founder confirms final acceptance. Release Manager Wang Bingshan prepares release notes, compatibility/version, defect disposition, rollout/rollback and an explicit release decision under existing WP06 issue #6 and validation/lifecycle rules. Deployment is a separate authorization; Nils's advice cannot waive a quality gate.

## Evidence, start readiness and reporting

Every execution assignment identifies agent, issue, CUS/Feature/SR, scope and exclusive files, dependencies/decision approvals, acceptance, branch, pull request, runtime/execution link when available and actual validation evidence. Future code/test commands are established in the approved D05/assignment; no nonexistent command is reported as run. Credentials/private fixtures and live integration use an authorized controlled environment; public evidence is sanitized. Record candidate SHA/environment/version/fixture hashes/results and missing evidence; all current product cases remain Not run.

GitHub Project holds live status, Priority, Agent, Dependencies plus Plan wave/order/Start gate and existing milestone #1. Primary publishes meaningful changes with role/name, old/new fields and readback; runtime is explicit, not automatic. Requirement readiness/approval is distinct from execution status. Planned code stays Backlog; initial source inventory may become Ready after its scope/input checks. A failed report is retained locally and announced as out of sync.

## Complete ordered Task map

Task acceptance, detailed outputs and verification IDs are copied without semantic changes into the linked JSON plan; legacy aggregate planning acceptance is explicitly added without changing its requirement contract. Each row links the original issue. Aggregate completion rows are visibly distinct from bounded assignments. TK11/TK15 additionally wait for TK67 so protected intake/persistence cannot precede authorization; TK18/STK019/STK025 and repeat checks TK19/STK021/STK026 can run before TK67 only as isolated pure transformations on approved disposable fixtures, with no protected user storage/service reads or writes; their JSON execution_scope/start_gate makes that restriction explicit. Integrated user-facing use waits for TK67 authorization.

| Order | ID / issue | Wave | Work kind | Owner | Prerequisites in this plan | Decision IDs |
| --- | --- | --- | --- | --- | --- | --- |
| 100 | [TK09](https://github.com/fengguode/DATARA/issues/115) | W0 | decision_research | Explorer — Wang Licun | None | D01 |
| 200 | [TK13](https://github.com/fengguode/DATARA/issues/119) | W0 | decision_research | System Architect — Feng Guo | None | D01 |
| 300 | [TK14](https://github.com/fengguode/DATARA/issues/120) | W0 | decision_research | System Architect — Feng Guo | None | D01 |
| 400 | [TK17](https://github.com/fengguode/DATARA/issues/123) | W0 | decision_research | System Architect — Feng Guo | None | Inherited gate/applicability |
| 500 | [TK20](https://github.com/fengguode/DATARA/issues/126) | W0 | decision_research | Explorer — Wang Licun | None | D01, D05 |
| 600 | [TK30](https://github.com/fengguode/DATARA/issues/129) | W0 | decision_research | System Architect — Feng Guo | None | D02 |
| 700 | [TK31](https://github.com/fengguode/DATARA/issues/130) | W0 | contract_design | System Architect — Feng Guo | None | D02 |
| 800 | [TK32](https://github.com/fengguode/DATARA/issues/131) | W0 | contract_design | System Architect — Feng Guo | None | D02 |
| 900 | [TK33](https://github.com/fengguode/DATARA/issues/132) | W0 | decision_research | System Architect — Feng Guo | None | D02 |
| 1000 | [TK34](https://github.com/fengguode/DATARA/issues/133) | W0 | contract_design | System Architect — Feng Guo | None | D02 |
| 1100 | [TK35](https://github.com/fengguode/DATARA/issues/134) | W0 | contract_design | UI Designer — Wu Yunzhou | None | D02 |
| 1200 | [TK36](https://github.com/fengguode/DATARA/issues/135) | W0 | decision_research | System Architect — Feng Guo | None | D03 |
| 1300 | [TK37](https://github.com/fengguode/DATARA/issues/136) | W0 | decision_research | System Architect — Feng Guo | None | D03 |
| 1400 | [TK38](https://github.com/fengguode/DATARA/issues/137) | W0 | contract_design | System Architect — Feng Guo | None | D03 |
| 1500 | [TK50](https://github.com/fengguode/DATARA/issues/148) | W0 | decision_research | System Architect — Feng Guo | None | D03 |
| 1600 | [TK51](https://github.com/fengguode/DATARA/issues/149) | W0 | decision_research | System Architect — Feng Guo | None | D02, D03 |
| 1700 | [TK56](https://github.com/fengguode/DATARA/issues/154) | W0 | decision_research | System Architect — Feng Guo | None | D04 |
| 1800 | [TK60](https://github.com/fengguode/DATARA/issues/158) | W0 | decision_research | System Architect — Feng Guo | None | D04 |
| 1900 | [TK63](https://github.com/fengguode/DATARA/issues/161) | W0 | decision_research | System Architect — Feng Guo | None | D04 |
| 2000 | [TK66](https://github.com/fengguode/DATARA/issues/164) | W0 | decision_research | System Architect — Feng Guo | None | D03, D04 |
| 2100 | [TK72](https://github.com/fengguode/DATARA/issues/170) | W0 | decision_research | System Architect — Feng Guo | None | D03, D04, D05 |
| 2200 | [TK73](https://github.com/fengguode/DATARA/issues/171) | W0 | decision_research | UI Designer — Wu Yunzhou | None | D04, D05 |
| 2300 | [TK10](https://github.com/fengguode/DATARA/issues/116) | W0 | contract_design | System Architect — Feng Guo | TK09 | D01 |
| 2400 | [TK39](https://github.com/fengguode/DATARA/issues/138) | W0 | contract_design | UI Designer — Wu Yunzhou | TK36, TK37, TK38 | D03 |
| 2500 | [TK40](https://github.com/fengguode/DATARA/issues/139) | W0 | contract_design | System Architect — Feng Guo | TK36, TK37, TK38 | D03 |
| 2600 | [TK41](https://github.com/fengguode/DATARA/issues/140) | W0 | contract_design | System Architect — Feng Guo | TK36, TK37, TK38 | D03 |
| 2700 | [TK01](https://github.com/fengguode/DATARA/issues/268) | W0 | aggregate | Primary Coordinator — Yi Tang | TK09, TK10, TK13, TK14, TK17, TK20 | Inherited gate/applicability |
| 2800 | [TK02](https://github.com/fengguode/DATARA/issues/269) | W0 | aggregate | Primary Coordinator — Yi Tang | TK01, TK30, TK31, TK32, TK33, TK34, TK35, TK36, TK37, TK38, TK39, TK40, TK41, TK50, TK51, TK56, TK60, TK63, TK66, TK72, TK73 | Inherited gate/applicability |
| 2900 | [TK18](https://github.com/fengguode/DATARA/issues/124) | W1 | implementation | Worker — Torsten Maier | TK01, TK02 | D01, D05 |
| 3000 | [TK67](https://github.com/fengguode/DATARA/issues/165) | W1 | implementation | Worker — Torsten Maier | TK01, TK02, TK66 | D03, D04 |
| 3100 | [TK11](https://github.com/fengguode/DATARA/issues/117) | W1 | implementation | Worker — Torsten Maier | TK01, TK02, TK10, TK67 | D01, D05 |
| 3200 | [TK15](https://github.com/fengguode/DATARA/issues/121) | W1 | implementation | Worker — Torsten Maier | TK01, TK02, TK14, TK67 | D01, D05 |
| 3300 | [TK19](https://github.com/fengguode/DATARA/issues/125) | W1 | verification | User Tester — Abt Hermann | TK18 | D01 |
| 3400 | [TK12](https://github.com/fengguode/DATARA/issues/118) | W1 | verification | User Tester — Abt Hermann | TK11 | D01 |
| 3500 | [TK16](https://github.com/fengguode/DATARA/issues/122) | W1 | verification | User Tester — Abt Hermann | TK15 | D01 |
| 3600 | [TK03](https://github.com/fengguode/DATARA/issues/270) | W1 | aggregate | Primary Coordinator — Yi Tang | TK01, TK02, TK11, TK12, TK15, TK16, TK17, TK18, TK19, TK20, TK67 | Inherited gate/applicability |
| 3700 | [TK21](https://github.com/fengguode/DATARA/issues/127) | W2 | implementation | Worker — Torsten Maier | TK03, TK18 | D01, D02, D05 |
| 3800 | [TK42](https://github.com/fengguode/DATARA/issues/141) | W2 | implementation | Worker — Torsten Maier | TK03, TK31, TK32, TK33 | D02 |
| 3900 | [TK44](https://github.com/fengguode/DATARA/issues/143) | W2 | implementation | Worker — Torsten Maier | TK03, TK34, TK35 | D02 |
| 4000 | [TK22](https://github.com/fengguode/DATARA/issues/128) | W2 | verification | User Tester — Abt Hermann | TK21 | D01, D02 |
| 4100 | [TK43](https://github.com/fengguode/DATARA/issues/142) | W2 | verification | User Tester — Abt Hermann | TK42 | D02 |
| 4200 | [TK45](https://github.com/fengguode/DATARA/issues/144) | W2 | verification | User Tester — Abt Hermann | TK44 | D02 |
| 4300 | [TK04](https://github.com/fengguode/DATARA/issues/271) | W2 | aggregate | Primary Coordinator — Yi Tang | TK03, TK21, TK30, TK31, TK32, TK33, TK34, TK35, TK42, TK43, TK44, TK45 | Inherited gate/applicability |
| 4400 | [TK46](https://github.com/fengguode/DATARA/issues/146) | W3 | implementation | Worker — Torsten Maier | TK04, TK36, TK38, TK39, TK40, TK41 | D03 |
| 4500 | [TK52](https://github.com/fengguode/DATARA/issues/150) | W3 | implementation | Worker — Torsten Maier | TK04, TK50, TK51 | D03 |
| 4600 | [TK53](https://github.com/fengguode/DATARA/issues/151) | W3 | implementation | Worker — Torsten Maier | TK04, TK50, TK51 | D03 |
| 4700 | [TK55](https://github.com/fengguode/DATARA/issues/153) | W3 | implementation | Worker — Torsten Maier | TK04, TK50, TK51 | D02, D03 |
| 4800 | [TK70](https://github.com/fengguode/DATARA/issues/168) | W3 | implementation | Worker — Torsten Maier | TK04, TK51 | D03 |
| 4900 | [TK47](https://github.com/fengguode/DATARA/issues/147) | W3 | verification | User Tester — Abt Hermann | TK46 | D03 |
| 5000 | [TK54](https://github.com/fengguode/DATARA/issues/152) | W3 | verification | User Tester — Abt Hermann | TK52, TK53, TK55 | D02, D03 |
| 5100 | [TK71](https://github.com/fengguode/DATARA/issues/169) | W3 | verification | User Tester — Abt Hermann | TK70 | D03 |
| 5200 | [TK05](https://github.com/fengguode/DATARA/issues/272) | W3 | aggregate | Primary Coordinator — Yi Tang | TK04, TK36, TK37, TK38, TK39, TK40, TK41, TK46, TK47, TK52, TK53, TK54, TK55, TK70, TK71 | Inherited gate/applicability |
| 5300 | [TK57](https://github.com/fengguode/DATARA/issues/155) | W4 | implementation | Worker — Torsten Maier | TK03, TK05, TK56 | D04 |
| 5400 | [TK58](https://github.com/fengguode/DATARA/issues/156) | W4 | implementation | Worker — Torsten Maier | TK03, TK05, TK56 | D04 |
| 5500 | [TK61](https://github.com/fengguode/DATARA/issues/159) | W4 | implementation | Worker — Torsten Maier | TK03, TK05, TK60, TK73 | D04, D05 |
| 5600 | [TK64](https://github.com/fengguode/DATARA/issues/162) | W4 | implementation | Worker — Torsten Maier | TK03, TK05, TK63, TK66 | D04 |
| 5700 | [TK68](https://github.com/fengguode/DATARA/issues/166) | W4 | implementation | Worker — Torsten Maier | TK03, TK05, TK66 | D04 |
| 5800 | [TK59](https://github.com/fengguode/DATARA/issues/157) | W4 | verification | User Tester — Abt Hermann | TK57, TK58 | D04 |
| 5900 | [TK62](https://github.com/fengguode/DATARA/issues/160) | W4 | verification | User Tester — Abt Hermann | TK61 | D04, D05 |
| 6000 | [TK65](https://github.com/fengguode/DATARA/issues/163) | W4 | verification | User Tester — Abt Hermann | TK64 | D04 |
| 6100 | [TK69](https://github.com/fengguode/DATARA/issues/167) | W4 | verification | User Tester — Abt Hermann | TK67, TK68 | D03, D04 |
| 6200 | [TK06](https://github.com/fengguode/DATARA/issues/273) | W4 | aggregate | Primary Coordinator — Yi Tang | TK03, TK05, TK57, TK58, TK59, TK61, TK62, TK64, TK65, TK68, TK69 | Inherited gate/applicability |
| 6300 | [TK74](https://github.com/fengguode/DATARA/issues/172) | W5 | quality_audit | Quality Manager — Wang Xiaofeng | TK54, TK59, TK62, TK65, TK69, TK71, TK72, TK73 | D02, D03, D04, D05 |
| 6400 | [TK07](https://github.com/fengguode/DATARA/issues/274) | W5 | aggregate | Primary Coordinator — Yi Tang | TK01, TK02, TK03, TK04, TK05, TK06, TK12, TK16, TK19, TK22, TK54, TK59, TK62, TK65, TK69, TK71, TK74 | Inherited gate/applicability |

## Complete Subtask map

| Order | Subtask / issue | Parent | Wave | Source WP / activity WP | Owner |
| --- | --- | --- | --- | --- | --- |
| 101 | [STK001](https://github.com/fengguode/DATARA/issues/173) | TK09 | W0 | WP01 / WP01 | Explorer — Wang Licun |
| 102 | [STK002](https://github.com/fengguode/DATARA/issues/174) | TK09 | W0 | WP01 / WP01 | Explorer — Wang Licun |
| 201 | [STK009](https://github.com/fengguode/DATARA/issues/181) | TK13 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 202 | [STK010](https://github.com/fengguode/DATARA/issues/182) | TK13 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 301 | [STK011](https://github.com/fengguode/DATARA/issues/183) | TK14 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 302 | [STK012](https://github.com/fengguode/DATARA/issues/184) | TK14 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 401 | [STK017](https://github.com/fengguode/DATARA/issues/189) | TK17 | W0 | WP02 / WP02 | System Architect — Feng Guo |
| 402 | [STK018](https://github.com/fengguode/DATARA/issues/190) | TK17 | W0 | WP02 / WP02 | System Architect — Feng Guo |
| 501 | [STK023](https://github.com/fengguode/DATARA/issues/195) | TK20 | W0 | WP02 / WP02 | Explorer — Wang Licun |
| 502 | [STK024](https://github.com/fengguode/DATARA/issues/196) | TK20 | W0 | WP02 / WP02 | Explorer — Wang Licun |
| 601 | [STK100](https://github.com/fengguode/DATARA/issues/201) | TK30 | W0 | WP03 / WP03 | System Architect — Feng Guo |
| 701 | [STK102](https://github.com/fengguode/DATARA/issues/202) | TK31 | W0 | WP03 / WP03 | System Architect — Feng Guo |
| 801 | [STK104](https://github.com/fengguode/DATARA/issues/203) | TK32 | W0 | WP03 / WP03 | System Architect — Feng Guo |
| 901 | [STK106](https://github.com/fengguode/DATARA/issues/204) | TK33 | W0 | WP03 / WP03 | System Architect — Feng Guo |
| 1001 | [STK108](https://github.com/fengguode/DATARA/issues/205) | TK34 | W0 | WP03 / WP03 | System Architect — Feng Guo |
| 1101 | [STK110](https://github.com/fengguode/DATARA/issues/206) | TK35 | W0 | WP03 / WP03 | UI Designer — Wu Yunzhou |
| 1201 | [STK112](https://github.com/fengguode/DATARA/issues/207) | TK36 | W0 | WP04 / WP04 | System Architect — Feng Guo |
| 1301 | [STK114](https://github.com/fengguode/DATARA/issues/208) | TK37 | W0 | WP04 / WP04 | System Architect — Feng Guo |
| 1401 | [STK116](https://github.com/fengguode/DATARA/issues/209) | TK38 | W0 | WP04 / WP04 | System Architect — Feng Guo |
| 1501 | [STK200](https://github.com/fengguode/DATARA/issues/219) | TK50 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 1502 | [STK201](https://github.com/fengguode/DATARA/issues/220) | TK50 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 1601 | [STK202](https://github.com/fengguode/DATARA/issues/221) | TK51 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 1602 | [STK203](https://github.com/fengguode/DATARA/issues/222) | TK51 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 1701 | [STK212](https://github.com/fengguode/DATARA/issues/231) | TK56 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 1702 | [STK213](https://github.com/fengguode/DATARA/issues/232) | TK56 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 1801 | [STK220](https://github.com/fengguode/DATARA/issues/239) | TK60 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 1802 | [STK221](https://github.com/fengguode/DATARA/issues/240) | TK60 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 1901 | [STK226](https://github.com/fengguode/DATARA/issues/245) | TK63 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 1902 | [STK227](https://github.com/fengguode/DATARA/issues/246) | TK63 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 2001 | [STK232](https://github.com/fengguode/DATARA/issues/251) | TK66 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 2002 | [STK233](https://github.com/fengguode/DATARA/issues/252) | TK66 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 2101 | [STK244](https://github.com/fengguode/DATARA/issues/263) | TK72 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 2102 | [STK245](https://github.com/fengguode/DATARA/issues/264) | TK72 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 2201 | [STK246](https://github.com/fengguode/DATARA/issues/265) | TK73 | W0 | WP01 / WP01 | UI Designer — Wu Yunzhou |
| 2202 | [STK247](https://github.com/fengguode/DATARA/issues/266) | TK73 | W0 | WP01 / WP01 | UI Designer — Wu Yunzhou |
| 2301 | [STK003](https://github.com/fengguode/DATARA/issues/175) | TK10 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 2302 | [STK004](https://github.com/fengguode/DATARA/issues/176) | TK10 | W0 | WP01 / WP01 | System Architect — Feng Guo |
| 2401 | [STK118](https://github.com/fengguode/DATARA/issues/210) | TK39 | W0 | WP04 / WP04 | UI Designer — Wu Yunzhou |
| 2501 | [STK120](https://github.com/fengguode/DATARA/issues/211) | TK40 | W0 | WP04 / WP04 | System Architect — Feng Guo |
| 2601 | [STK122](https://github.com/fengguode/DATARA/issues/212) | TK41 | W0 | WP04 / WP04 | System Architect — Feng Guo |
| 2901 | [STK019](https://github.com/fengguode/DATARA/issues/191) | TK18 | W1 | WP02 / WP02 | Worker — Torsten Maier |
| 2902 | [STK025](https://github.com/fengguode/DATARA/issues/197) | TK18 | W1 | WP02 / WP02 | Worker — Torsten Maier |
| 3001 | [STK234](https://github.com/fengguode/DATARA/issues/253) | TK67 | W1 | WP02 / WP02 | Worker — Torsten Maier |
| 3002 | [STK235](https://github.com/fengguode/DATARA/issues/254) | TK67 | W1 | WP02 / WP02 | Worker — Torsten Maier |
| 3101 | [STK005](https://github.com/fengguode/DATARA/issues/177) | TK11 | W1 | WP02 / WP02 | Worker — Torsten Maier |
| 3102 | [STK006](https://github.com/fengguode/DATARA/issues/178) | TK11 | W1 | WP02 / WP02 | Worker — Torsten Maier |
| 3201 | [STK013](https://github.com/fengguode/DATARA/issues/185) | TK15 | W1 | WP02 / WP02 | Worker — Torsten Maier |
| 3202 | [STK014](https://github.com/fengguode/DATARA/issues/186) | TK15 | W1 | WP02 / WP02 | Worker — Torsten Maier |
| 3301 | [STK021](https://github.com/fengguode/DATARA/issues/193) | TK19 | W1 | WP06 / WP06 | User Tester — Abt Hermann |
| 3302 | [STK026](https://github.com/fengguode/DATARA/issues/198) | TK19 | W1 | WP06 / WP06 | User Tester — Abt Hermann |
| 3401 | [STK007](https://github.com/fengguode/DATARA/issues/179) | TK12 | W1 | WP01 / WP06 | User Tester — Abt Hermann |
| 3402 | [STK008](https://github.com/fengguode/DATARA/issues/180) | TK12 | W1 | WP01 / WP06 | User Tester — Abt Hermann |
| 3501 | [STK015](https://github.com/fengguode/DATARA/issues/187) | TK16 | W1 | WP02 / WP06 | User Tester — Abt Hermann |
| 3502 | [STK016](https://github.com/fengguode/DATARA/issues/188) | TK16 | W1 | WP02 / WP06 | User Tester — Abt Hermann |
| 3701 | [STK020](https://github.com/fengguode/DATARA/issues/192) | TK21 | W2 | WP03 / WP03 | Worker — Torsten Maier |
| 3702 | [STK027](https://github.com/fengguode/DATARA/issues/199) | TK21 | W2 | WP03 / WP03 | Worker — Torsten Maier |
| 3801 | [STK124](https://github.com/fengguode/DATARA/issues/213) | TK42 | W2 | WP03 / WP03 | Worker — Torsten Maier |
| 3901 | [STK128](https://github.com/fengguode/DATARA/issues/215) | TK44 | W2 | WP03 / WP03 | Worker — Torsten Maier |
| 4001 | [STK022](https://github.com/fengguode/DATARA/issues/194) | TK22 | W2 | WP06 / WP06 | User Tester — Abt Hermann |
| 4002 | [STK028](https://github.com/fengguode/DATARA/issues/200) | TK22 | W2 | WP06 / WP06 | User Tester — Abt Hermann |
| 4101 | [STK126](https://github.com/fengguode/DATARA/issues/214) | TK43 | W2 | WP03 / WP03 | User Tester — Abt Hermann |
| 4201 | [STK130](https://github.com/fengguode/DATARA/issues/216) | TK45 | W2 | WP03 / WP03 | User Tester — Abt Hermann |
| 4401 | [STK132](https://github.com/fengguode/DATARA/issues/217) | TK46 | W3 | WP04 / WP04 | Worker — Torsten Maier |
| 4501 | [STK204](https://github.com/fengguode/DATARA/issues/223) | TK52 | W3 | WP04 / WP04 | Worker — Torsten Maier |
| 4502 | [STK205](https://github.com/fengguode/DATARA/issues/224) | TK52 | W3 | WP04 / WP04 | Worker — Torsten Maier |
| 4601 | [STK206](https://github.com/fengguode/DATARA/issues/225) | TK53 | W3 | WP04 / WP04 | Worker — Torsten Maier |
| 4602 | [STK207](https://github.com/fengguode/DATARA/issues/226) | TK53 | W3 | WP04 / WP04 | Worker — Torsten Maier |
| 4701 | [STK210](https://github.com/fengguode/DATARA/issues/229) | TK55 | W3 | WP04 / WP04 | Worker — Torsten Maier |
| 4702 | [STK211](https://github.com/fengguode/DATARA/issues/230) | TK55 | W3 | WP04 / WP04 | Worker — Torsten Maier |
| 4801 | [STK240](https://github.com/fengguode/DATARA/issues/259) | TK70 | W3 | WP04 / WP04 | Worker — Torsten Maier |
| 4802 | [STK241](https://github.com/fengguode/DATARA/issues/260) | TK70 | W3 | WP04 / WP04 | Worker — Torsten Maier |
| 4901 | [STK134](https://github.com/fengguode/DATARA/issues/218) | TK47 | W3 | WP04 / WP04 | User Tester — Abt Hermann |
| 5001 | [STK208](https://github.com/fengguode/DATARA/issues/227) | TK54 | W3 | WP06 / WP06 | User Tester — Abt Hermann |
| 5002 | [STK209](https://github.com/fengguode/DATARA/issues/228) | TK54 | W3 | WP06 / WP06 | User Tester — Abt Hermann |
| 5101 | [STK242](https://github.com/fengguode/DATARA/issues/261) | TK71 | W3 | WP06 / WP06 | User Tester — Abt Hermann |
| 5102 | [STK243](https://github.com/fengguode/DATARA/issues/262) | TK71 | W3 | WP06 / WP06 | User Tester — Abt Hermann |
| 5301 | [STK214](https://github.com/fengguode/DATARA/issues/233) | TK57 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5302 | [STK215](https://github.com/fengguode/DATARA/issues/234) | TK57 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5401 | [STK216](https://github.com/fengguode/DATARA/issues/235) | TK58 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5402 | [STK217](https://github.com/fengguode/DATARA/issues/236) | TK58 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5501 | [STK222](https://github.com/fengguode/DATARA/issues/241) | TK61 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5502 | [STK223](https://github.com/fengguode/DATARA/issues/242) | TK61 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5601 | [STK228](https://github.com/fengguode/DATARA/issues/247) | TK64 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5602 | [STK229](https://github.com/fengguode/DATARA/issues/248) | TK64 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5701 | [STK236](https://github.com/fengguode/DATARA/issues/255) | TK68 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5702 | [STK237](https://github.com/fengguode/DATARA/issues/256) | TK68 | W4 | WP05 / WP05 | Worker — Torsten Maier |
| 5801 | [STK218](https://github.com/fengguode/DATARA/issues/237) | TK59 | W4 | WP06 / WP06 | User Tester — Abt Hermann |
| 5802 | [STK219](https://github.com/fengguode/DATARA/issues/238) | TK59 | W4 | WP06 / WP06 | User Tester — Abt Hermann |
| 5901 | [STK224](https://github.com/fengguode/DATARA/issues/243) | TK62 | W4 | WP06 / WP06 | User Tester — Abt Hermann |
| 5902 | [STK225](https://github.com/fengguode/DATARA/issues/244) | TK62 | W4 | WP06 / WP06 | User Tester — Abt Hermann |
| 6001 | [STK230](https://github.com/fengguode/DATARA/issues/249) | TK65 | W4 | WP06 / WP06 | User Tester — Abt Hermann |
| 6002 | [STK231](https://github.com/fengguode/DATARA/issues/250) | TK65 | W4 | WP06 / WP06 | User Tester — Abt Hermann |
| 6101 | [STK238](https://github.com/fengguode/DATARA/issues/257) | TK69 | W4 | WP06 / WP06 | User Tester — Abt Hermann |
| 6102 | [STK239](https://github.com/fengguode/DATARA/issues/258) | TK69 | W4 | WP06 / WP06 | User Tester — Abt Hermann |
| 6301 | [STK248](https://github.com/fengguode/DATARA/issues/267) | TK74 | W5 | WP06 / WP06 | Quality Manager — Wang Xiaofeng |

## Review and current limitations

Review evidence is recorded in [the implementation-plan review](../team/reviews/implementation-plan-review.md). Native automatic role loading is unconfirmed (#18); actual explicit role runs are identified in that record. D01–D05 stay open. An ordered planning artifact and successful registry checks do not establish coding readiness, product verification, founder acceptance or release readiness. The bounded TK09 evidence assignment can begin first; coding waits for G0.
