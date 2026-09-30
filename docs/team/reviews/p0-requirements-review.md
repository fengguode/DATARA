# P0 requirements engineering review

## Scope and evidence identity

Assignment: [#28](https://github.com/fengguode/DATARA/issues/28); coordinator **Primary Coordinator — Yi Tang**; quality lead **Quality Manager — Wang Xiaofeng**. This record relays actual AI-role findings; persona names do not establish human participation. GitHub publisher is fengguode. Execution links are unavailable; runtime paths identify the actual delegated runs. Native automatic role activation remains unconfirmed.

Scope: CUS01–CUS10 requirements engineering supporting the existing P0 first-usable-release milestone. Deliverables are aligned, prioritized CUS → Feature → SR → Task → Subtask requirements, perspective assessments, decision/dependency planning and planned verification. Coding and detailed architecture design are excluded. Future implementation/verification assignments describe outcomes only and have not started.

Review baseline: main commit `4cd839bcedea6d6370a3e0ec50a4f49e476fc8a7`; latest published planning head during initial review `48e004190ca936d0fe8cde4c9a103dc14d7f44cd`. Group B/C were uncommitted draft fragments when reviewed; that SHA does not contain those files. Initial findings below refer to those pre-correction drafts, not to a confirmed final candidate. Required review must be refreshed after integration.

## Initial review findings and corrective handoffs

### Quality Manager — Wang Xiaofeng

Runtime `/root/roundtable_quality`; read-only full requirement-content audit, in progress.

- **High — Group C feature and subtask acceptance:** ten features and 48 subtasks used boilerplate that did not define record-specific outcomes. All must state bounded CUS-derived behavior or an explicit investigation deliverable with observable acceptance.
- **High — Group C sequencing:** features depended on aggregate task IDs including their own package; future verification tasks did not depend on the relevant implementation tasks. Feature dependencies and package prerequisites must be separated; bounded task dependencies must sequence the actual preceding work without cycles.
- **High — Cross-CUS ancestry:** FEAT34/SR58, FEAT42/SR73 and several privacy/accessibility matrix links did not share the claimed CUS scope. Resolve proposed cross-cutting ancestry consistently or remove wrong links and state investigation gaps; preserve legacy SR parents.
- **High — Premature design and incorrect delivery outputs:** several tasks prescribed detailed schemas/resource maps or described implementation plans as future implementation outcomes. Replace with requirements/open-decision work and separately planned observable product behavior. No detailed design is authorized now.
- **Medium — CUS08 privacy:** lineage SR16 alone does not establish access protection; provide a valid cross-cutting obligation or explicit investigation gap.
- Parent task/work-package associations were checked and found consistent. WP03 is a work-package identifier, not a priority-token violation. Validation-case titles are not automatically governed by the backlog/requirement title convention.

### User Tester — Abt Hermann

Runtime `/root/roundtable_tester`; independent read-only acceptance/oracle audit. No product tests or file edits.

- **Group A:** reviewed FEAT01/02/03/21, SR32–34, TK09–22, STK001–028 and TC21–27. Positive/negative outcomes or artifact-oracle criteria are present; D01/D02 remain unresolved. No critical acceptance defect found in this scope. This is document review, not product acceptance.
- **High — Group C SR70–76:** identical generic criteria must become obligation-specific oracles: valid matching response only becomes a finding; old-identity responses do not render; evidence is authorized and bound to the saved snapshot; owner retrieval succeeds while foreign references disclose nothing; secrets are absent from visible outputs; keyboard/focus/error association works; statuses use semantic/text cues and accessible asynchronous feedback. Contract values remain open under relevant decisions.
- **High — All Group C feature/task/subtask criteria:** separate requirements/research artifact completeness from future implementation behavior and candidate-specific verification evidence. Avoid blended “reviewed or exercised” completion criteria and subjective “reviewable result” language.
- **Medium — TC79:** a coverage audit is not the end-to-end athlete journey. TC15 remains the existing P0 journey and founder-validation gate, Not run.
- **Medium — SR74/TC76 scope:** log inspection belongs to the applicable credential-log obligation (existing SR13); do not silently broaden an output-only SR or duplicate scope without traceability.

### Worker — Torsten Maier

Runtime `/root/roundtable_worker`; exclusive Group B repair handoff after the Architect's initial draft.

- Found **High** malformed SR51–59 acceptance/link fields: null criteria and normative text in TC-reference fields. Repaired using the existing planned TC definitions and intended obligations; re-audit is required.
- Removed FEAT34 → SR58 while retaining SR58 under CUS04/FEAT31, without expanding its scope.
- Replaced premature adapter/transport order, event-field and selected-secret-boundary wording with outcome-based requirements and explicit D03-dependent questions.
- Linked TCs remain Not run with empty evidence; no product evidence was added.

## Correction and review status

| Scope | Author/integrator | Current gate |
| --- | --- | --- |
| Requirements-only plan and milestone alignment | System Architect — Feng Guo, `/root/roundtable_architect` | Published; integrated record review pending |
| Group A | System Architect — Feng Guo | Tester document review has no critical finding; QM full audit pending |
| Group B | Architect draft; Worker bounded repairs | Repair handoff completed; QM/Tester re-audit pending |
| Group C | System Architect — Feng Guo, `/root/system_architect_group_c` | Changes requested; author correction in progress |
| Canonical integration and independent Reviewer review | To follow corrected fragment quality gate | Not started |

## Checks and limits

Author JSON/reference checks are document-integrity evidence only. They did not establish semantic adequacy and did not detect all acceptance/link defects. No product tests, rendered UI acceptance, live-model integration, system verification or user validation were performed.

Earlier uncommitted checker/builder/test experiments were stopped following the founder's requirements-only clarification. They were preserved locally with matching file hashes and excluded from this deliverable; the existing tracked checker was restored unchanged. Historical GitHub activity/test comments remain records of the excluded experiment, not requirements acceptance. No new code, tests or validation-tool implementation belongs in this requirements delivery.

Existing supported registry checking may be used after integration within its documented scope; unsupported additive-layer checks require explicit audit evidence and an honest limitation. Do not extend tooling under this assignment.

D01–D05 remain open. All P0 priorities and original product constraints are preserved. Requirements completion supports the first P0 milestone and does not deliver, verify, accept or release the product. Founder baseline/product confirmation and subsequent delivery/release gates remain separate.
## Consolidated initial quality audit and post-repair findings

Quality Manager Wang Xiaofeng audited 23 Features, 20 proposed SRs, 56 bounded Tasks, 112 Subtasks, ten CUS perspective matrices (80 entries), and 39 new planned cases. This covers the initial fragments, not the current corrected candidate. No duplicate IDs or missing source paths were found. New cases were Not run; source existence is not proof that a claim is approved or that a product works.

Post-repair Group B SR fields were reviewed by QM and Tester and found materially improved: actual acceptance criteria and TC references are present; the FEAT34/SR58 link was removed. Remaining changes requested:

- STK100–135 need case/action-specific measurable acceptance; the full QM rubric controls the quality gate even where the focused Tester review found earlier artifact criteria generally adequate.
- TK42–47 must specify future actual behavior or candidate-specific results, not recording an oracle/implementation-evidence plan.
- TK30 requires a self-checkable shortlist completeness/rationale criterion; TC40/TC51 do not validate that artifact.
- CUS05 legal unknown must map to sourced legal-applicability investigation, not UI accessibility TK35.
- SR58 must align its eligibility/accessibility scope with CUS04/CUS05 and applicable TC44/TC45 evidence, without returning it to the unrelated CUS06-only feature.
- CUS04/CUS06 accessibility applicability and investigation outcomes need explicit criteria; unspecified formal targets remain open.
- TK36 security/credential/legal requirements investigation belongs to a qualified Architect role; QM audits the evidence without becoming the analysis author.
- TC48/TC49 must distinguish deterministic/mock routing/error checks from actual supported customer-model integration required by existing TC08. All remain Not run.
- Definition matrices, eligibility schemas and state specifications must be reframed to requirements questions/outcomes or deferred design, consistent with the founder's scope.

Correction ownership: Worker Torsten Maier owns Group B and the limited Group A accessibility-gap clarification; Architect Feng Guo owns Group C. Feature dependencies use Feature IDs consistently; legacy work-package prerequisites remain separate. After author handoffs, full QM correction audit and independent Reviewer review are required before confirmation. This record grants no requirement or product approval.
## Corrected fragment gates and quota policy (30 September 2026)

Quality Manager — Wang Xiaofeng (AI agent) reported final fragment gates PASS: Group A 4 Features/3 new SR/14 Tasks/28 Subtasks/7 planned cases; Group B 9/10/18/18/12; Group C 10/7/25/49/20. Total 23 Features, 20 proposed SR, 57 bounded Tasks, 95 Subtasks and 39 planned cases, with 80 perspective entries. These are fragment-quality outcomes, not final canonical acceptance or product evidence.

Canonical integration uncovered a real omission: TK30 shortlist acceptance explicitly excludes adjacent TC40/TC51 as its verification, but initially had no planned inspection case. Worker Torsten adds TC80 for that artifact and links TK30/STK100; it remains Not run with empty evidence. Full integrated review and fragment-to-canonical reconciliation remain pending. The unchanged registry checker previously reported `TK30: no planned verification`; do not report that failed check as passing.

Controller — Nils Traeger (AI agent), runtime `/root/roundtable_controller`, checked fresh account usage at 2026-09-30 15:32:51 UTC: five-hour 28% remaining, weekly 89% remaining, ordinary usage allowed. Neither meets the strictly below-3% pause condition. These are shared account quotas, not task context or billing.

Reviewer — Dennis Windmaier (AI agent), runtime `/root/reviewer`, independently reviewed the three quota-policy diffs and found no critical findings. TOML parsing and exact assertions confirmed unchanged Nils name, gpt-6-luna model, medium reasoning and read-only sandbox. Policy was published in commit 574401c. Later GitHub centralization prose is subject to the full requirements review, not this narrow result.

Supported automation create/view/update confirmed the active `nils-datara-usage-guard` heartbeat at a 15-minute cadence in the primary task. Goal pause is supported; the available goal update tool cannot set active. Scheduled/follow-up continuation must be checked for actual execution and goal state. No complete live pause/reset/resume cycle has been observed; local runs require the computer on and app running. Manual pause/cancel and completed work take precedence.

Pull request #33 was merged externally on GitHub; continuation draft [pull request #35](https://github.com/fengguode/DATARA/pull/35) carries remaining work. [Issue #34](https://github.com/fengguode/DATARA/issues/34) records Nils ownership and policy review. All 10 P0 CUS and 23 Features were published to Project as separate linked issues (#36–68); an independent API readback matched issue identity, Backlog, Requirements, Priority P0 and Architect ownership for all 33 items. P0 SR/Task/Subtask publication and dependency-link reconciliation remain incomplete. Native automatic role activation remains unconfirmed (#18); explicit role runs are distinct evidence.