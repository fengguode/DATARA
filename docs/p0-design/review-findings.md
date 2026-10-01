# Review findings and disposition

Status: review evidence for candidate commit `968b37b29716cf84741160036704b22adbfc1039` on `codex/p0-architecture-test-design` (base `33f173b`). The technical, worker and quality reviews cover the exact candidate commit; release and controller notes are proposal-scope assessments. None are product tests or runtime checks. Runtime identities are recorded separately from role labels.

## Independent technical review — Dennis Windmaier role

Runtime identity: `/root/technical_review`. Read-only review of diagrams and package contracts.

| Finding | Disposition in current draft | Remaining limitation |
|---|---|---|
| Component diagram did not show authorization on preparation, eligibility, run and secret paths. | **Corrected:** diagram 02 now states authorization wraps every entry and propagates server-verified owner context; it shows gated routes for prepare, eligibility, run, secrets, validation and read. Diagram 05/08 retain the same owner boundary. | Exact identity mechanism and session/capability contract remain D03/D04/D05 blockers. |
| Diagrams stored one SkillVersion per Run while product direction permits selected skill combinations. | **Corrected as proposal:** class/ER diagrams now use a Run with one or more `SelectedSkillExecution` children, each with its own eligibility, attempts, result or failure. Contracts propose reject-if-any-ineligible and aggregate `partial` status for mixed outcomes. | Aggregate `partial` requires SR14/TC10 registry synchronization and approval before implementation; exact retry/cancel/restart behavior is open. |
| ER diagram claimed tenant constraints but did not show owner-safe references on child/join tables. | **Corrected logically:** owner-owned records now show composite `(owner_id, resource_id)` keys and owner context on provenance, snapshots, metrics, eligibility, attempts, results, findings and evidence. | Mermaid ER syntax cannot fully express composite foreign-key enforcement. D05 must select physical schema; TC14 needs persistence-level cross-tenant reference rejection. |
| Sequence diagram showed one run-level result instead of per-skill outcomes and aggregation. | **Corrected:** sequence 05 creates one child per selected skill, validates/persists each child result/failure, then derives the aggregate state. | Exact retry, cancellation and async/restart semantics remain open; no renderer was available. |

**Re-review status:** Dennis confirmed the four corrections in a read-only review of exact candidate commit `968b37b29716cf84741160036704b22adbfc1039` (runtime `/root/technical_review`). He found the proposal technically consistent and suitable for a draft PR, with no product verification implied. Torsten independently confirmed the commit boundary and that all TK01–TK07 remain Blocked (runtime `/root/worker_review`). No approval is inferred for D01–D05 or product implementation.

## Worker implementability review — Torsten Maier role

Runtime identity: `/root/worker_review`. Read-only review found no Ready unit and the following ambiguity classes:

- Canonical registry/checker contains unresolved conflict markers; CUS/SR/task/test references cannot be accepted as canonical until the owner reconciles and validates them.
- Proposed contracts have not been approved JSON/API schemas, canonicalization/nullability/cardinality/enumeration, diagnostics, compatibility or scope rules (TK02).
- D01 lacks pinned FIT evidence, field/time/unit/integrity mapping, source/fixture rights, quantitative limits and conflict/supersession policy (TK01).
- WP02 needs approved batch/partial commit, interrupted upload, idempotency, cross-store reconciliation/orphan cleanup, conflict workflow, lifecycle and restore behavior (TK03).
- WP03 needs selected skills/method versions, exact eligibility thresholds, metric/window/timezone semantics, evaluation rubric and result/evidence schema (TK04).
- WP04 needs capability matrix, credential lifecycle and data disclosure/retention, timeout/rate/cost/error mapping, and retry/cancel/late response/restart behavior (TK05).
- WP05 needs exact resource schemas, cursor/order/page limits, filter/date/error semantics, evidence dereference/expiry, authentication/cache behavior and accessibility conformance target (TK06).
- WP06 has no implementation/runtime/candidate; all canonical checks remain Not run and athlete/founder acceptance is absent (TK07).

**Disposition:** all remain **Blocked**. The current draft adds transaction and multi-skill proposals but does not close required founder/owner decisions. Torsten must re-review the final candidate and confirm no unlisted ambiguity before any future unit is marked Ready.

## Quality Manager audit — Wang Xiaofeng role

Runtime identity: `/root/quality_audit`. Read-only audit confirmed the package keeps planned cases `Not run`, distinguishes mock/live/system/rendered UI/athlete/founder gates, avoids a second backlog, and reports no product verification. At the time of the initial audit, the audit found current canonical source edits invalid due to conflict markers, perspective coverage not fully approved, additional lifecycle/security/operations/accessibility cases not yet canonical IDs, and named reviews/commit pending.

**Disposition:** added a CUS-by-perspective applicability matrix in [traceability readiness](traceability-readiness.md). It marks no perspective not applicable, identifies evidence gaps, and does not claim legal coverage. The follow-up audit confirmed this is accurate and that TC14 remains designed/Not run. Before a canonical baseline, the Architect/QM and owner must derive or disposition SR/TC additions in the registry after it is repaired. Final diff and candidate-specific checks remain pending; no QA approval or requirement verification is inferred.

## Release and Controller reviews

- **Release Manager role (Wang Bingshan), runtime `/root/release_review`:** confirms D05 is open; no release artifact/runtime/build ID exists; deployment, migration/rollback, backup restore objectives, monitoring and named incident ownership are incomplete. Current project lifecycle gates still require fixed commit, reproducible SR evidence, separate live-model integration, TC15 and founder acceptance, defect triage, release notes, deployment and rollback plan. No deployment or experience evidence exists.
- **Controller role (Nils Traeger), runtime `/root/controller_review`:** no usage/billing/runtime telemetry exists, so spend is unmeasured. Before a provider choice/live spike, pin provider/model/API docs and dated price/rate schedule; record usage per attempt, request ID and retry/failure cost; separate customer provider charges from DATARA infrastructure cost. One-provider-first reduces evaluation/quota burden but narrows customer choice; it does not support a multi-provider claim. Pause live tests if provider, data/fixture provenance, credential authorization, spend ceiling, or required evidence fields are missing; resume only after owner approval and preserve prior failure evidence.

**Disposition:** material release/controller recommendations are added to D03/D05 proposals and remain blockers, not approved policies. These role reviews do not replace fixed-candidate release evidence.

## Review control

The four technical corrections are confirmed in candidate commit `968b37b29716cf84741160036704b22adbfc1039`; worker and quality reviews also checked that exact candidate. These reviews support presenting a draft documentation PR only. Any later edit touching diagrams, schemas, decision status, traceability or test claims requires refreshed review for affected scope. If an issue remains unresolved, disposition it explicitly and keep dependent units blocked.
