# P0 traceability and readiness

Status: design mapping proposal; canonical traceability file remains untouched because it has pre-existing merge markers. Existing CUS/SR/TC/TK identifiers are referenced as found in the current user worktree. Feature IDs do not exist in the current canonical registry; none are invented here. `TC01`–`TC20` remain **Not run**.

## CUS → SR → implementation unit → design/decision → test → evidence gate

| CUS | Current SR | Existing implementation unit (WP/TK) | Design / decision | Designed tests | Evidence gate before Verified |
|---|---|---|---|---|---|
| CUS01 | SR01, SR02, SR27 | WP01/TK01 contract; WP02/TK03 implementation | Architecture boundary; FIT source contract; D01 | TC01, TC19; TC03 conflict; recovery candidates | D01 and independent official mapping/fixture evidence; unit + contract + integration results on fixed candidate |
| CUS02 | SR03, SR04 | WP02/TK03 | source/object/import model; original immutability and conflict contract; D01/D05 | TC02, TC03; restore candidate | approved identity/conflict policy; storage restart/recovery evidence and no duplicate/overwrite |
| CUS03 | SR05–SR07, SR28 | WP02/TK03, WP03/TK04 | deterministic snapshot/input envelope; D02 | TC04, TC05, TC20 | reproducible outputs with model disabled; scope/provenance/schema oracles |
| CUS04 | SR08, SR09, SR29 | WP03/TK04 | skill version/output contract; D02 | TC06, TC20 | approved skill versions, evaluation rubric and required live quality threshold evidence |
| CUS05 | SR10, SR11 | WP03/TK04 | deterministic eligibility rules; D02 | TC07; TC15 insufficient-data path | exact per-skill thresholds and unmet-input matrix approved; zero model-call proof |
| CUS06 | SR12, SR13, SR30 | WP04/TK05 | adapter/secret boundary; D03/D05 | TC08, TC09, TC10, TC14, TC20 | adapter mocks plus separate authorized live-model capability evidence; secret and owner-scope security evidence |
| CUS07 | SR14, SR15 | WP04/TK05 | run/attempt lifecycle; D03 | TC10, TC15 | state/error/retry policy approved; success only after schema/evidence validation; failure never success |
| CUS08 | SR16, SR17 | WP05/TK06 | result/finding/evidence model; D02/D04 | TC11, TC15, TC20 | persistence after restart, append-only rerun and resolved lineage on fixed candidate |
| CUS09 | SR18, SR19, SR31 | WP05/TK06 | dashboard contract; shared read resource contract; D04 | TC12, TC13, TC20; UI A1–A9 | real rendered browser evidence, API parity/read-only checks and explicit accessibility acceptance |
| CUS10 | SR20, SR21 | WP02/TK03, WP04/TK05, WP05/TK06 | identity boundary; secret/evidence isolation; D03/D04/D05 | TC09, TC14; deletion/restore/ops candidates | two-user service and UI race/security evidence across every resource; no cross-user reads or mutation |

## Existing package task mapping

`TK01` approves the source contract; `TK02` approves cross-package schemas and open decisions; `TK03` implements WP02; `TK04` WP03; `TK05` WP04; `TK06` WP05; `TK07` verifies and validates WP06. Their package links are WP01–WP06 issues #1–#6 with control issue #8. Dependencies remain sequential: TK01 → TK02 → TK03 → TK04 → TK05 → TK06 → TK07, with TK06 requiring TK03 and TK05. WP07/TK08 remains P1, explicitly excluded.

## Coverage audit: missing applicable SR/test coverage candidates

The current SR set does not establish all applicable legal, engineering, runtime, architecture, security, accessibility and operations perspectives. The current TCs do not give explicit recovery/retention/backup/monitoring/accessibility acceptance oracles. These are **candidate derived obligations**, not canonical requirements yet. Preserve the existing numbering while the registry is repaired; the Architect and Quality Manager should propose additions and links under the normal change process before the release baseline is frozen.

### CUS-by-perspective applicability assessment

This is a first-pass applicability assessment, not a declaration that a perspective is complete. “Applies” means the obligation/risk must be assessed; “gap” means the current registry lacks an approved testable obligation. No legal applicability or compliance is presumed.

| CUS | Legal / rights | Engineering | Runtime / deployment | Architecture / interface | Security / data protection | Accessibility / usability | Operations / lifecycle | Athlete-domain correctness |
|---|---|---|---|---|---|---|---|---|
| CUS01 upload | Applies: source/fixture rights and customer disclosure; jurisdiction review | SR01–02/SR27; fixture/resource edge cases open | Upload limits, interruption and parser isolation: gap | WP01/TK01 source contract | Untrusted parser, owner scope and safe diagnostics: gap | Upload errors/status need accessible outcomes: gap | Abuse limits, cleanup and parser monitoring: gap | FIT mapping/units/timestamps require official verification; D01 open |
| CUS02 history | Applies: activity-data retention/deletion/export review | SR03–04; atomicity/conflict recovery open | Durability, backup/restore and deletion from backups: gap | Owner-scoped immutable source/history | Encryption, privileged access, deletion and audit: gap | History browsing/quality labels: acceptance absent | Restore, retention, migration and incident response: gap | Provenance/duplicate policy affects history accuracy |
| CUS03 preparation | Applies: purpose/minimization and source rights | SR05–07/SR28; determinism oracle proposed | Resource use and build/version consistency: gap | Versioned snapshots, provenance and schemas | Minimize data and exclude secrets; review incomplete | Understandable exclusions and quality findings: gap | Preparation monitoring and failure recovery: gap | Rounding, UTC/window and metric semantics need oracle |
| CUS04 skills | Applies: content rights and transparency review | SR08–09/SR29; schemas/evaluation open | Provider/runtime compatibility: gap | Immutable provider-independent versions | Input minimization/output evidence integrity: gap | Descriptions and limitations understandable: gap | Evaluated release/version lifecycle: gap | Rubric/claim boundaries/evidence quality: D02 |
| CUS05 eligibility | Applies: user-facing explanation obligations to review | SR10–11; thresholds open | Same-version decision consistency: gap | Deterministic eligibility before model | Zero call when ineligible; test needed | Unmet-input explanation accessibility: gap | Rule version/monitoring: gap | Coverage thresholds/abstention: D02 |
| CUS06 model access | Applies: provider terms/data disclosure and consent review | SR12–13/SR30; capabilities/errors open | Secure egress, secret provider/runtime config: D03/D05 | Common adapter/explicit selection; schemas open | Credential lifecycle, isolation, redaction and egress review | Connection selection/failure clarity: gap | Key rotation, quota, incident and cost monitoring: gap | Per-connection quality threshold: D02/D03 |
| CUS07 manual run | Applies: explain model use/failure/provider terms | SR14–15; combined-run lifecycle proposed | Async completion, restart and timeout behavior: gap | Run/attempt/selected-skill contracts open | Owner authorization, bounded input/sanitized output | Pending/partial/failure accessible: gap | Idempotency, cancellation, retry/recovery: gap | Invalid or unsupported outputs cannot become findings |
| CUS08 result history | Applies: retention, erasure and access review | SR16–17; immutable lineage tests planned | Durable evidence and deletion behavior: gap | Snapshot/skill/model version references | Evidence links cannot bypass owner access | Finding classes, limits and links need accessible rendering | Schema migration/evidence expiry: gap | Reproducible evidence resolution |
| CUS09 dashboard/API | Applies: privacy notice, provider/user rights and API terms | SR18–19/SR31; schemas/pagination open | Availability, rate limits and identity integration: gap | Shared read contracts proposed; D04 open | Authorization on resources; cache and audit gap | Monitoring, compatibility, incident policy: gap | No implied analysis; saved metrics/timezone transparency |
| CUS10 isolation | Applies: jurisdiction-specific obligations unknown | SR20–21; cross-user oracle needed | Tenant architecture/identity/operator roles: D05 | Authorization/service/repository boundary | Encryption, least privilege, audit, deletion and breach plan gaps | Sign-in/denial/identity-switch flows: gap | Access review, incident handling, recovery: gap | No cross-user source/credential/result/evidence/async state |

No perspective is marked not applicable in this pass. If review later determines non-applicability, the Architect must record the evidence and reason. This matrix leaves SR coverage open pending founder/owner and Quality Manager disposition.

| Candidate obligation needing derivation/approval | Affected CUS | Proposed design/test coverage | Start/release impact |
|---|---|---|---|
| Retention, deletion/export, backup and restore behavior for originals, normalized history, credentials, evidence and results | CUS02, CUS06, CUS08, CUS10 | data lifecycle in architecture; new disposable-data deletion and backup/restore cases | Open until founder sets data lifecycle and D05 selects storage/backup owner; blocks customer-data use/release |
| Encryption, key access, least privilege, audit-event content and security incident response | CUS02, CUS06, CUS09, CUS10 | data-flow diagram, secret boundary, TC09/TC14 plus security-review case | Open until D03/D05 and security owner define controls; blocks credential and hosted data release |
| Resource abuse limits, upload interruption/atomicity, provider timeout/rate limit, process restart, operational health and recovery | CUS01–03, CUS06–10 | failure/activity diagram; new interrupted-upload/run and restore scenarios | Open until numerical D01 limits, run semantics and D05 operations are set; blocks system readiness |
| Accessibility target and localization/time-zone comprehension | CUS01, CUS05, CUS09 | dashboard A8/A9; new screen-reader/browser acceptance | Open until target, owner and actual browser test environment are agreed; dashboard verification blocked |
| Applicable legal/consumer/privacy/provider contractual duties by intended jurisdiction and audience | CUS01, CUS06, CUS09, CUS10 | decision question list; qualified review evidence | Founder identifies markets/audience; legal review required before accepting real customer data or release |
| Database/API schema migration and rollback compatibility | CUS02, CUS08–10 | deployment diagram; add migration/rollback rehearsal | D05 topology/versioning and data-retention policy required before release |

## Overall readiness decision

| Unit | Status | Reason / gate to remove blocker |
|---|---|---|
| TK01 / WP01 FIT contract | **Blocked** | D01 and official version/mapping/rights/fixture evidence are open; registry is presently invalid in working tree. |
| TK02 / WP01 skills, adapter, dashboard/API contracts | **Blocked** | D02, D03, D04 remain open; operational/security/accessibility SR coverage gaps need disposition. |
| TK03 / WP02 data home | **Blocked** | depends on TK01/TK02 approvals and D05 storage/topology. |
| TK04 / WP03 skills and eligibility | **Blocked** | depends on TK03 and D02 approval/evaluation. |
| TK05 / WP04 connection and manual run | **Blocked** | depends on TK04, D03 and D05; live-model evidence remains separate. |
| TK06 / WP05 history/dashboard/API | **Blocked** | depends on TK03/TK05 and D04/D05 plus accessibility/security operational requirements. |
| TK07 / WP06 verification/athlete validation | **Blocked** | no product code/runtime exists, earlier units unapproved, and TC01–TC20 not run; needs fixed candidate, live model, browser, athlete journey and explicit founder acceptance. |

**No unit is Ready today.** Architecture/test planning is reviewable as a proposal; no product implementation unit has finalized approved decisions, valid canonical records, and complete operational/security acceptance criteria. Torsten can review the contract package for ambiguity now, but cannot start implementation under this assignment.
