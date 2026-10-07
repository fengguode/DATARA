# DATARA takeover handover — 4 October 2026

Prepared by Primary Coordinator — Yi Tang_model-unconfirmed-variant-unconfirmed_Codex (AI agent).
Model used: model=model-unconfirmed variant=variant-unconfirmed harness=Codex.

## 1. Read this first

This is a takeover package requested by the founder, who is **considering** returning execution to OpenCode. It does not declare that OpenCode accepted ownership or that the founder appointed a successor. Record the actual successor and exclusive work ownership in [control issue #8](https://github.com/fengguode/DATARA/issues/8) before overlapping implementation. The first complete P0 athlete outcome is **unfinished, not accepted and not released**.

Repository: https://github.com/fengguode/DATARA. Shared backlog: https://github.com/users/fengguode/projects/3. Baseline refreshed at approximately 09:50–09:53 UTC on 4 October 2026: `main=11650a4b01f4efacd90d0976a9be2c09f0166894`. The repository had **zero open pull requests** before this handover publication. Refresh all values at takeover; this dated document is evidence, not a second backlog.

The practical next outcome is an owner-authorized page and API for already saved deterministic metrics. Its exact public contract is reviewed but **not approved**: [owner Discussion #369](https://github.com/fengguode/DATARA/discussions/369), [technical Discussion #367](https://github.com/fengguode/DATARA/discussions/367). A fresh read during handover found zero comments in #369; its reaction is not approval. Do not infer approval from this handover request.

## 2. Canonical documentation and reading order

Read these from live main, then the affected issues and discussion replies:

1. [Code of Conduct](../../CODE_OF_CONDUCT.md), [AGENTS.md](../../AGENTS.md), [team workflow](../team/workflow.md), [roster](../team/roster.md), [attribution](../team/attribution.md), [PR confirmation](../team/pull-request-confirmation.md), and [shared knowledge](../team/knowledge/shared-lessons.md).
2. [Management index](README.md), [project brief](../project-brief-and-roadmap.md), [CUS](product-requirements.md), [SR](system-requirements.md), [traceability](traceability.md), [registry](requirements-registry.json), and [GitHub requirement mapping](github-requirements-map.json).
3. [Selected D01–D05 baseline](p0-decision-baseline-2026-10-01.md), [decision register including the approved G0 replacement](decision-register.md), [ordered implementation plan](p0-implementation-plan.md), and [design index](../p0-design/README.md).
4. [Validation plan](validation-plan.md), [lifecycle/release gates](lifecycle-and-releases.md), [Windows command contract](../p0-design/windows-command-contract.md), and the committed tests for each delivered increment.
5. Live [cross-platform routing topic #292](https://github.com/fengguode/DATARA/discussions/292); use separate topics for substantive work. Read comments **and nested replies**, not only descriptions.

Older design and issue descriptions sometimes say no coding or tests exist. Those are historical planning statements: subsequent PRs and candidate-specific evidence below supersede them only within their actual scope. Conversely, a merged PR does not close a whole work package or verify every linked SR. Preserve the distinction and correct misleading current summaries through normal review.

## 3. Product target and decisions that remain binding

P0 is a repeatable manual athlete journey: supported FIT upload and reupload; visible quality/duplicate/conflict handling; deterministic preparation and eligibility; user-selected supported skill/model execution using customer-owned API access; saved findings with evidence; matching dashboard/API retrieval; explicit unsupported-input and model-failure states; two-user isolation; final athlete validation.

The founder selected a local browser pilot in China, Django 5.2/Python/PostgreSQL 17, FIT SDK 21.217.0, OpenAI and DeepSeek as initial provider directions. Exact provider models, real account/region/capability evidence and paid-call authority are not supplied by that selection. No silent provider/model fallback. Automatic routines, recommendations using DATARA's model, commercial mechanisms and source-to-skill automation remain later scope.

The approved **Milestone A G0 replacement** permits bounded source acceptance, immutable originals, deterministic preparation/eligibility, saved history/read surface and isolation without closing all G0. It does not waive provenance, immutable history, privacy, rights, user isolation, provider integration gates, TC15 or release. Accepted risks are not verified requirements. Consult the decision register's exact disposition table rather than repeating the old all-G0 prohibition or claiming universal G0 closure.

## 4. Live work-package checkpoint

Project fields observed during this handover, not inferred from code or agent runtime:

| Record | Priority / status / lifecycle | Delivered or remaining |
| --- | --- | --- |
| [Control #8](https://github.com/fengguode/DATARA/issues/8) | P0 / In progress / Requirements | Shared delivery control; no successor recorded by this package |
| [WP01 #1](https://github.com/fengguode/DATARA/issues/1) | P0 / In progress / Requirements | Selected directions and bounded replacement exist; full contract/rights/operations evidence remains |
| [WP02 #2](https://github.com/fengguode/DATARA/issues/2) | P0 / Backlog / Development | Data-home and saved-metric increments implemented; full package not confirmed complete |
| [WP03 #3](https://github.com/fengguode/DATARA/issues/3) | P0 / Backlog / Requirements | Source-bound summary/trend and pure consistency exist; full evaluated library/model-facing execution remains |
| [WP04 #4](https://github.com/fengguode/DATARA/issues/4) | P0 / Backlog / Development | Customer connections, safe credentials, run lifecycle, output validation and real-provider evidence remain |
| [WP05 #5](https://github.com/fengguode/DATARA/issues/5) | P0 / Backlog / Development | Internal saved history exists; public page/API, sessions and browser evidence remain |
| [WP06 #6](https://github.com/fengguode/DATARA/issues/6) | P0 / Backlog / Verification | Full SR verification, TC15, founder athlete acceptance and release decision remain |

The Agent field was not exposed in this Project view. Do not invent current runtime participation from ownership. Delivery PRs can be Done while their parent package remains Backlog. The handover documentation is bounded under control #8's recorded P0; no priority, no start applies to subsequent work.

## 5. Delivered code and integration map

Start new work from current main, not an old stacked draft. Original stage branches/commits are retained for provenance.

| Increment | PR and exact identity | What it establishes |
| --- | --- | --- |
| Atomic scoped snapshot persistence and Windows phase commands | [#342](https://github.com/fengguode/DATARA/pull/342), [#344](https://github.com/fengguode/DATARA/pull/344) | Reviewed corrections/launcher subsequently integrated; source and runtime evidence are separate |
| Consolidated saved-metric source and tests | [#357](https://github.com/fengguode/DATARA/pull/357), head `c32333362ab57e05d2eb08b70e3710173591e9bf`, merge `0535254afc712a2048b7c425356321b2abc6e9c9` | Consolidation tree equals original tested `5d04a37c4879dc5424b20881d665416d4a2a4a64`; independent metadata review preserved original stages |
| Synthetic concurrency | [#359](https://github.com/fengguode/DATARA/pull/359), head `9785ec4ad45a74fc31b18ff4430ac976b04fe877`, merge `46d4be223d7589d85098dc2475017c278ab81145` | Saved-metric and scoped-version competing-write regressions |
| Graph integrity negatives | [#360](https://github.com/fengguode/DATARA/pull/360), head `2a37368243b8d22b82b4ed3c9722710c2f1e87a1`, merge `627b24504da94f9ec7eaef8cd7bd8cd49ddcbfbc` | Deferred FK/operand/seal/immutability rejection and rollback controls |
| Read-only preserved-schema preflight | [#361](https://github.com/fengguode/DATARA/pull/361), head `3a8c9f90e6a2790094459eed0fa555b71b0048e1`, merge `3976ecb321d2c86e88b9ec0896b3af8db62c0add` | Synthetic catalog diagnostics and refusal; **not approval or execution of preserved DB adoption** |
| Independent-process saved history | [#362](https://github.com/fengguode/DATARA/pull/362), head `473f12ddf26d9473b84c3d4e63ae0bcb2922da9d`, merge `c1f243904d7df38dd2057643c4c9ee1571efc998` | Retrieval and rollback checks from another interpreter, not server restart/restore proof |
| Authorized snapshot-to-metric operation | [#365](https://github.com/fengguode/DATARA/pull/365), head `530bd26881e6da9e038f05c4487388c5197f1db0`, merge `9421e8ad83e83c02624c06a570bc903413dce64b` | `prepare_and_save_metric` derives supported metrics from saved owner snapshots |
| Complete UTC-day consistency | [#372](https://github.com/fengguode/DATARA/pull/372), head `76c207c7a2de9c66ff89dc12a6d0b1f0762bb237`, merge `2e516b0d5928481f17b08252f0719c29992f6f25` | Pure counts/streaks under approved option A; **not persisted consistency or public UI/API** |
| Essential agent skill discovery | [#374](https://github.com/fengguode/DATARA/pull/374), head `923f2f21455351d63819ef357e8605fdbd6b6386`, merge `11650a4b01f4efacd90d0976a9be2c09f0166894` | `find-skills` in roster/workflow; not an athlete elemental skill |

Superseded drafts **#346, #349, #351, #352, #353, #354, #355** were closed without merging individually after their source inclusion was confirmed in #357. Do not reopen/remerge them. #342/#344 and #357/#359/#360/#361/#362/#365/#372/#374 are merged history. The public history contract has no implementation PR yet. Verify fresh PR state before any action.

Key source paths:

- `datara/intake.py`, `classification.py`, `canonical.py`, `normalization.py`, `dedup.py`, `storage.py`, `provenance.py`, `db.py`: source acceptance, data home and owner-scoped storage services.
- `datara/scoped_input.py`: frozen owner-scoped input versions/snapshots and source evidence. Compatibility floor excludes computed metrics from source-only readers.
- `datara/recorded_metrics.py`: exact source-bound elapsed/count summary and complete-week overall trend; canonical carrier and digest validation. This increment does not implement distance/timer/model outcomes.
- `datara/metric_projection.py`, `models.py`, `metric_store.py`, migrations `0001_initial.py`/`0002_saved_metric_graph.py`: immutable saved computed graph, source operands, owner/snapshot constraints, seals and deterministic retries. `SavedMetricStore.get_metric`, `get_metric_evidence`, `list_metrics_for_snapshot` and `prepare_and_save_metric` are internal services.
- `datara/recorded_consistency.py`: pure complete-UTC-day policy; its registry/persistence extension is not silently approved by the summary/trend registry.
- `datara/preflight/*`, `scripts/syncdb_preflight.py`: read-only catalog/schema/data-equivalence diagnostics. Actual preserved-database adoption remains blocked/ineligible.
- `datara/settings.py` at this baseline has `ROOT_URLCONF=None`, `TEMPLATES=[]`, `WSGI_APPLICATION=None`. An authentication middleware entry alone is **not a runnable login/page/API journey**.

## 6. Candidate-specific evidence ledger

These are executed synthetic tests reported and audited during Codex delivery. They are not production/app-role isolation, full SR acceptance, live model integration or athlete validation.

| Candidate / delivered increment | Targeted result | Full PostgreSQL suite | Limit / source |
| --- | --- | --- | --- |
| `5d04a37…` consolidated as `c323333…` | Saved graph/pure regressions included | 260/260 PASS, 34.108 s | Fresh disposable DB cleanup; migration state check no changes; collision probe preserved existing OID/owner/marker; [#341](https://github.com/fengguode/DATARA/discussions/341), [#356](https://github.com/fengguode/DATARA/discussions/356) |
| `9785ec4…` | 4/4 PASS, 6.602 s | 264/264 PASS, 40.759 s | Fresh DB cleanup; exact-head technical/affected architecture and QA completed; #341/#359 |
| `2a37368…` | 5/5 PASS, 8.179 s | 269/269 PASS, 56.239 s | Cardinality/canonical rollback controls are scoped, not all possible tampering proof; #341/#360 |
| `3a8c9f9…` | 24/24 PASS, 0.774 s | 293/293 PASS, 60.636 s | Read-only synthetic preflight; no preserved DB access/adoption; [#348](https://github.com/fengguode/DATARA/discussions/348)/#361 |
| `473f12d…` | 3/3 PASS, 5.571 s | 296/296 PASS, 54.678 s | New interpreter/PID, same saved content and foreign denial/rollback; #341/#362 |
| `530bd26…` | 8/8 PASS, 10.980 s | 304/304 PASS, 78.568 s | Internal preparation/storage operation; [owner #364](https://github.com/fengguode/DATARA/discussions/364), #348/#365 |
| `76c207c…` | 12/12 PASS, 0.090 s | 316/316 PASS, 75.563 s | Pure consistency only; [technical #370](https://github.com/fengguode/DATARA/discussions/370), [owner #371](https://github.com/fengguode/DATARA/discussions/371)/#372 |

Latest product candidate `76c207c…` and merged `2e516b0…` were confirmed tree-identical. Later #374 changes only team documentation; no fresh 316-test run on the later documentation SHA is claimed. Native GitHub check success is a separate signal. No new product tests are required or claimed merely to prepare this handover.

Failed history must remain failed: early 243-test PostgreSQL baseline had three stale allowlist failures; corrected tests preceded the 260-pass candidate. Initial pure candidate `7282e45…` had source integrity findings and was superseded. Some QA runs were interrupted by usage/tool access and did not constitute approval. Preflight initially had a privacy finding and an incomplete stderr run (`full08`); corrected target07/full09 evidence superseded these without erasing them. Consistency target01–03 failures were corrected before the final exact candidate. Review records are attributed source/evidence audits, not independent runtime reruns unless explicitly stated.

Sanitized results, full commit identities and test sources are public through the linked PRs/topics and this document. Detailed local logs/screenshots are retained as historical supplements; they contain host-specific context and are not blindly uploaded. The receiving team can reproduce evidence from committed sources under the authorized disposable environment. Credentials, account usage, real FIT data and connection configuration are deliberately absent from this public package.

## 7. Approvals, unresolved decisions and access boundaries

**Already approved — do not reask:**

- Bounded saved-metrics persistence contract: [#348 comment 18724283](https://github.com/fengguode/DATARA/discussions/348#discussioncomment-18724283), source-only reader clarification [18724345](https://github.com/fengguode/DATARA/discussions/348#discussioncomment-18724345); direct founder approval relayed [18725770](https://github.com/fengguode/DATARA/discussions/348#discussioncomment-18725770). Contract artifact SHA256 `4014fbbba72e1f1bc691fe9b0bfbe109b89a70270c89a025d365f6e5db5483f9`.
- Targeted regressions and existing suite on fresh disposable **synthetic PostgreSQL**, with the existing restricted test role: [#341 comment 18726169](https://github.com/fengguode/DATARA/discussions/341#discussioncomment-18726169), direct founder confirmation retained. No real-data or preserved-database testing follows from it.
- Founder direct instruction: **“Merge reviewed PRs, then close superseded drafts.”** Applied to the delivered chain. Review/architecture/QA and head identity still precede merges; merge is not release.
- Complete UTC-day consistency **option A**: [#366 comment 18737403](https://github.com/fengguode/DATARA/discussions/366#discussioncomment-18737403); concrete source permission [#371 comment 18739916](https://github.com/fengguode/DATARA/discussions/371#discussioncomment-18739916) plus direct Codex A. #372 delivered this bounded pure result.
- Assumed-inactive OpenCode bounded-task takeover was approved historically in [#309 comment 18714740](https://github.com/fengguode/DATARA/discussions/309#discussioncomment-18714740). Inactivity was an assumption, not a partner acknowledgement. A return to OpenCode requires current ownership reconciliation before overlapping writes.

**Current material owner decision:** #369 public saved-history detail contract, artifact SHA256 `04ab57bfc3ca9f45ec4f1f69bde86b9bd51b18d4cabd9f1025bb1ba0689ed5a0`. Full candidate is published there; independent technical/affected architecture and final QA passed after three corrections. It proposes a distinct recorded-metrics family, GET/HEAD detail page/API, exact saved carrier strings, evidence disclosure, server-derived session owner, generic inaccessible/missing denial, explicit error version and no-store behavior. Approving this does not approve history lists, external read-token issuance, model assessments, provider use or release. Do not substitute a model-assessment envelope for deterministic observations.

**Engineering/operational gates:** runnable session/login lifecycle and auth boundary; actual same-origin page/API identity; two-identity application-role evidence; frontend rendering/accessibility; exact approved consistency persistence extension if selected; lawful/representative fixture coverage; backup/restore/deletion controls; actual runtime/incident ownership; Linux/reference-topology evidence; provider accounts/capability/egress/spend approval; full P0 and athlete acceptance. Preserved syncdb adoption requires a reviewed strict-equivalence/operator/backup/disposition path and applicable authorization; preflight diagnostics alone do not supply it.

No authority in this package for runtime provisioning/reset, grants, credentials, broader access, provider spending, deployment or release. Automatic approval-review failures were preserved. Earlier GitHub-only merge approval caused a platform authorization rejection; direct founder clarification resolved the reviewed-merge scope. A later extra control-issue backlink was rejected as redundant/wrong-tool-target after #374; the separate owner notice succeeded. Never route around an approval rejection.

## 8. Reproduction entry points and environment limits

Observed past test environment: native Windows, Python 3.12.14, Django 5.2.17, PostgreSQL 17.11, restricted existing test role. Committed `requirements-milestone-a.txt` pins the decoder and all distributions. Read the command contract and `scripts/milestone_a_runner.py` before use; runtime availability at takeover is unknown until checked. Do not publish authentication or read private password files into logs.

> **SUPERSEDED IN PART — 2026-10-05.** The Python 3.12.14 pin recorded above no
> longer applies. 3.12.14 has no official Windows build, so it was unsatisfiable
> on this platform, and the pin is now **3.12.10** by recorded founder decision.
> The parity break on the `test` phase, and the newly pinned
> `typing_extensions==4.16.0` which changes `lock_sha256`, are both recorded in
> [the pinned-environment decision record](pinned-environment-decisions-2026-10-05.md).
> Everything else on this line — Django 5.2.17, PostgreSQL 17.11, the restricted
> existing test role, and the no-credentials rule — still stands. The original
> text is preserved above rather than edited, because this handover is a dated
> record and the correction belongs beside it, not inside it.

From a clean, fixed candidate with privately supplied, already authorized environment:

```powershell
# Documentation/identity checks, when applicable; not product verification:
python -X utf8 scripts/check_identity_labels.py
# Registry changes only:
python -X utf8 scripts/check_requirements.py
# Existing native launcher; one phase per process:
powershell -NoProfile -File scripts/milestone_a.ps1 -Phase inspect -Python <absolute-python-path> -Venv <absolute-venv-path>
powershell -NoProfile -File scripts/milestone_a.ps1 -Phase test -Python <absolute-python-path> -Venv <absolute-venv-path>
```

Placeholders must be resolved privately; these examples are not executable credentials or permission to install/provision. The test phase requires explicit allowlisted fresh `DATARA_TEST_DB_NAME`, PostgreSQL engine and the exact phase-role/base-database tuple defined in the source contract. Runner refuses collisions, reuse, clones and preserved targets; teardown is bound to created OID/owner. Retain the chosen target privately before execution. A residual or failed teardown is a failure, not permission for prefix cleanup or automatic DROP. No `migrate` invocation against a preserved database is authorized here. `app-check` metadata is not isolation proof. Linux/Bash/SQLite deviations are separate; SQLite green tests are not PostgreSQL evidence.

Record SHA, clean/dirty state, OS/shell/runtime/dependency identity, command, synthetic fixture version, actual result, exit and cleanup. A checker exit2 for skipped identity scan is not PASS. Never substitute source review, screenshots of a mock, or the test-role suite for a working athlete journey.

## 9. Local preservation and portability

Original `C:/Users/guofe/DATARA` is **not a clean release checkout**. Fresh status confirms eight tracked modifications: management README, decision register, registry, system requirements, traceability, WP01 issue handoff, WP01 requirements package, and `scripts/check_requirements.py`; plus untracked `mobile-architecture-site/`. Historical conflict markers exist in local management documents. Preserve all of this. No reset, pull, blanket cleanup or deletion. Treat it as unintegrated local work requiring a separately scoped review, not as authoritative main.

Managed isolated checkouts `windows-phase-command/DATARA` and `p0-decision-baseline/DATARA` under the user's `.codex/worktrees/` retain branches/stage history. The current handover baseline is remote main; receiving OpenCode should use its own clean isolated checkout. Do not assume Codex filesystem permissions, tool handles or private environments transfer to another harness.

Historical sanitized local checkpoint: `coordination-checkpoint-recorded-metrics.md` and detailed artifacts in the Codex visualization workspace. That local chronology contains superseded restrictions and must not be copied wholesale as current authority. This public package carries the necessary latest state, exact IDs and reproducible source links. Do not transfer private credentials, raw FIT data or account telemetry through GitHub. Actual environment/key custody is a private owner/operator handoff if needed.

`find-skills` is installed in this Codex user's catalog, and #374 records its essential workflow use. OpenCode must check its own skill/runtime availability; no installation or invocation in OpenCode is claimed. Read [roster essential skills](../team/roster.md#essential-agent-skill-set) before declaring a tooling gap.

## 10. Team, communication and takeover sequence

At the preparation checkpoint, product implementation/review assignments are completed or historically interrupted; no product-writing agent is claimed running. Dedicated Codex roles requested/configured `gpt-6.1-sol` with low reasoning; primary effective model/backend remains unconfirmed. OpenCode must report its actual configuration/loading limitations and conforming identity rather than copy a Codex label. Supported concurrency was four including primary; observe actual receiving-runtime limits.

The native Codex goal currently reports **BLOCKED** with an outdated objective text mentioning old pending tests/merges. The explicit approvals above supersede those stale descriptions; no native resume or completion is claimed. A 15-minute owner-reply monitor remains active outside ongoing pursuit. It checks unresolved owner comments and nested replies; during actual pursuit defer the regular monitor to avoid overlapping work, while dependent execution still refreshes authority/ownership privately. This handover does not silently pause/cancel automation or appoint the receiving coordinator.

Owner notices must be separate **Announcements** per topic, outside agent communication, with `#Report_to_Owner @fengguode`; add `#DATARA-Blocked` for active holds. Meaningful decisions, achievements, failures and resolved blockers need notices. Stay quiet for unchanged nonactionable polls. Do not bundle everything into #358. Technical reports stay in their relevant topics with issue/PR/control links, canonical identity and `Model used:` keys. Read reactions as reactions, never votes approving a contract unless the founder explicitly defines that decision mechanism.

Recommended first receiving-session sequence:

1. Read this package and live main; verify SHA and clean checkout. Read Project3, control8, affected WP/CUS/Feature/SR/task records, #292, #369/#367 and all nested replies. Establish priority, dependencies and current executor before starting.
2. Record proposed OpenCode coordinator identity, actual runtime state/model evidence, branch and exclusive paths in the control record; obtain/record the founder's actual transfer direction and avoid overlapping Codex writes. Handover preparation is not acceptance of ownership.
3. If #369 receives applicable approval, implement only the exact approved saved-detail surface and session/auth dependency, using existing `SavedMetricStore` retrieval and no recomputation/model call. Name WP05/CUS08–10/SR16–21/SR31/SR73 and the applicable existing tasks. Freeze exact paths and synthetic two-user acceptance oracles before assignment.
4. If #369 remains unresolved, preserve that hold, answer any clarification with concrete options in the same owner topic, and select another genuinely approved P0 item from the live backlog. Do not create repeat contract/review cycles without a delivery need or silently persist new consistency outputs.
5. Primary inspects every changed tracked/untracked path; independent exact-head technical/affected architecture review and QA follow actual candidates. Run authorized relevant synthetic checks and same-origin rendered evidence when the surface exists; preserve failures and cleanup proof. Merge reviewed PRs under standing authority, close only truly superseded drafts after inclusion proof, then notify the owner.
6. Complete remaining Milestone A outcome and then the broader first P0 journey. Keep Done/Verified/Accepted/released separate. Provider integration, TC15, founder acceptance and release need their actual applicable evidence/authority; this package does not waive them.

## 11. Handover completeness and acceptance

GitHub carries the canonical instructions, requirements/plan, source/tests/migrations/launchers, merged integration chain, public exact pending contract, decision and review topics, sanitized evidence ledger, boundaries, preservation instructions and next steps. Raw host artifacts and secrets are not required to understand the public implementation state. Reproducing the runtime still requires an authorized private environment, and that availability is deliberately not asserted.

Receiver acknowledgement should state: baseline read, successor/ownership record, unresolved decisions understood, private runtime availability or absence, first eligible bounded task, and actual next report. Only the founder decides the transfer; only observed receiver acknowledgement establishes acceptance. No acknowledgement, execution continuity, package-wide verification or full P0 delivery is invented by publishing this handover.
