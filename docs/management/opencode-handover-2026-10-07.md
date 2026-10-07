# DATARA handover for a possible OpenCode return — 7 October 2026

**Prepared:** 2026-10-07 15:03 UTC by Primary Coordinator — Yi Tang_model-unconfirmed-variant-unconfirmed_Codex (AI agent). Effective model/backend evidence for this writer is unavailable.
**Purpose:** Put a usable, current-enough transfer map and execution instructions in GitHub. The founder says OpenCode is no longer actively working on the project and is considering handing execution back. This document and its PR do not, by themselves, record a new appointment or acceptance by OpenCode. Do not wait for an inactive OpenCode acknowledgement before continuing work already authorized by the founder. If OpenCode returns, reconcile ownership and exclusive paths with it before overlapping edits.

## Start here

1. Read this handover and the [copy-ready OpenCode continuation prompt](opencode-continuous-execution-prompt.md).
2. Refresh live main, [AGENTS.md](../../AGENTS.md), the [management index](README.md), [project brief](../project-brief-and-roadmap.md), [team workflow](../team/workflow.md), [roster](../team/roster.md), [attribution](../team/attribution.md), [PR confirmation policy](../team/pull-request-confirmation.md), saved team knowledge, requirements/traceability, [decision register](decision-register.md), [D01–D05 baseline](p0-decision-baseline-2026-10-01.md), [P0 plan](p0-implementation-plan.md), [validation plan](validation-plan.md), and [release lifecycle](lifecycle-and-releases.md).
3. Refresh [Project 3](https://github.com/users/fengguode/projects/3), control [issue #8](https://github.com/fengguode/DATARA/issues/8), each affected package/task/bug, PRs and reviews, and relevant owner Discussions including nested replies. Project fields are the shared status authority; issue-body prose may be historical. Record disagreements and read back mutations.
4. Confirm actual receiving-runtime model, available skills, permissions, and tool limits. Requested configuration is not evidence that a model loaded. Establish the actual coordinator, owner, branch/head and exclusive paths in #8 before a new overlapping write.
5. Start from the latest main in a clean isolated checkout. **Do not reset, pull, clean, or reuse the original dirty Codex checkout** at C:/Users/guofe/DATARA; it has eight tracked changes plus untracked mobile-architecture-site/ and local worktree data. Preserve historical task branches and failed evidence. None of those local paths transfers automatically to OpenCode.

## Authority and coordination

- Repository: [fengguode/DATARA](https://github.com/fengguode/DATARA). One shared backlog: [DATARA Development and Lifecycle, Project 3](https://github.com/users/fengguode/projects/3). Control: [issue #8](https://github.com/fengguode/DATARA/issues/8).
- Project priority/status/lifecycle/ownership/dependencies are the board record. Requirement docs, registry and traceability describe content and planned coverage; they are not competing status boards. Preserve historical outcomes; Done, Verified, Accepted and Released mean different things.
- No priority / no start. Do not infer scope approval from silence, emoji, a merged neighboring PR, a source review, or this handover. Founder owns product decisions and final athlete acceptance.
- User notification for material decisions, an important achievement, a delivery, failure or a blocker becoming unblocked belongs in a **separate Announcements Discussion per topic**, with #Report_to_Owner @fengguode; use #DATARA-Blocked for an active hold. Do not bury an owner message in an agent technical thread or bundle unrelated topics. Keep technical exchanges in their own Discussion with issue/PR/control links and canonical attribution.
- The founder stopped the recurring Codex coordination task. **Do not restart it, create a replacement monitor, or run a parallel 15-minute periodic check.** The 15-minute owner-reply check applies only when pursuit is inactive or blocked, per the founder's clarification. During active pursuit, check actual authority/ownership and owner replies as needed before dependent action, after interruption/scope change and at work checkpoints; this is execution work, not a recurring monitor.
- Before substantive execution or delegation, use available private supported usage telemetry under the founder's current guard: ordinary usage allowed and more than 5% remaining in every applicable window. Unknown telemetry is not clearance. Stop new substantive work strictly below 3% and preserve an exact checkpoint. Keep account telemetry private; no spending or reset-credit use.
- New non-Feng agent configuration requested by the founder: gpt-6-luna, medium reasoning (“6 Luna Mid”). Feng Guo stays gpt-6.1-sol, low. Check OpenCode's provider/model identifiers and effective loading; do not claim the Codex TOML setting proves an OpenCode backend. Preserve role permissions and independent review; report actual running/completed/failed states.
- [Essential agent skills](../team/roster.md#essential-agent-skill-set) include find-skills; [workflow](../team/workflow.md) requires checking the catalog and reading the skill for a concrete discovery need. The installed Codex skill catalog does not establish OpenCode availability. Check the receiving environment before relying on a skill; do not install unrelated skills.
- Never publish credentials, private FIT data, runtime data or private usage. No provider spending, broader access/grants, preserved-database adoption/provision/reset, deployment or release without the applicable explicit authority.

## Product target and binding constraints

Deliver the first complete P0 athlete journey: supported source upload/re-upload, visible quality/duplicate/conflict handling, deterministic preprocessing and eligibility, explicit customer selection of supported skill/model, manual execution with clear failure states, saved outputs/evidence and lineage, matching dashboard and read-only API, two-user isolation, and the required final athlete validation/acceptance.

Binding constraints include source-first supported ingestion; immutable originals and persistent history; deterministic eligibility before recommendation/execution; provider-independent elemental skills; customer-owned API access for analysis; explicit model/skill selection with no silent fallback; Datara's own model is P1 recommendations only. Commercial mechanisms and source-to-skill automation are deferred. Do not invent provider/model outcome, metric schema, public route/envelope/version, or latest-result pointer.

D01–D05 and the approved Milestone A G0 replacement are in the linked decision records. The replacement permits bounded Milestone A source acceptance, deterministic preparation/eligibility, saved history/read surface and isolation without closing all G0. It does not waive provenance, immutable history, privacy/rights, user isolation, provider gates, TC15 or release. Accepted risks are not verified.

## Current checkpoint (last reviewed 7 October 2026, approximately 09:34 UTC)

A later REST issue/comment read attempted during preparation returned 404 for issues despite successful repository-file access. The following is a **last-observed checkpoint, not a claim of live synchronization**. Refresh affected issue threads and Project before acting. Discussion #369 was directly visible in the browser during handover: it has one founder reply (#18745667), saying the proposed saved-history contract artifact was not on main and offering three ways to unblock; no later textual reply was visible. Its thumbs-up reaction is not approval.

| Record | Last observed status | Last known gate |
|---|---|---|
| Control #8 / WP control | P0, In progress | Reconcile coordinator, priority, owner and exact authorized next item. |
| WP01 #1 | In progress | Source contract, evidence, rights/operations and package gates remain. |
| WP02 #2 | Backlog | Depends on WP01; broader persistence/preprocessing and required evidence are not complete. |
| WP03 #3 | Backlog | Depends on WP01/#1 and WP02/#2; some bounded documents delivered, package/evidence gates remain. |
| WP04 #4 | Backlog | Depends on WP03/#3; customer connection, safe credential, run lifecycle, output and live-provider evidence remain. |
| WP05 #5 | Backlog | Depends on WP02/#2 and WP04/#4; public page/API, session-backed success and browser evidence remain. |
| WP06 #6 | Backlog | Depends on WP01–WP05; fixed-candidate verification, TC15 and founder acceptance remain. |
| TK35 / issue #134 | Project Done; issue closed | Requirements-design note only. TC45, product implementation, rendered accessibility checks and full D02 evidence are not verified. |
| STK110 / issue #206 | Project Done; issue closed | Requirements-design note only; same distinction as TK35. |
| WP03 TK04 / issue #379 | Project In progress | PR #393 was merged at founder-confirmed head dbb4f3bf15a6e766411647abe104950337d0841b, merge f4c1eb3…; exact-head tests/verification remain open. |
| WP05 TK64 / issue #378 | Project In progress | PR #394 was open at an older base and requires fresh head/base/review/ownership checks. Public contract and session-backed working success remain gates. |
| Defect #385 | Project Backlog, no assigned agent in last board read | Wrong-type history_coverage/quality_limit observation raised rather than returning an explanatory ineligible decision. Resolve/assign before treating the engine as accepted. |
| WP01 evidence-map issue #384 | Backlog/open in last read | PR #391 merged the C6 evidence map; exact QA and C6 A/B decision are still separate. |
| C6 decision #387 | No priority / no start | Discussion #412 captured the evidence conflict; no founder textual decision was present in the last read. |

### Concrete public decision/test holds

- **Saved-history public contract:** [owner Announcement #369](https://github.com/fengguode/DATARA/discussions/369), technical [#367](https://github.com/fengguode/DATARA/discussions/367). The proposed detail-only contract SHA256 is 04ab57bfc3ca9f45ec4f1f69bde86b9bd51b18d4cabd9f1025bb1ba0689ed5a0. Founder comment [#18745667](https://github.com/fengguode/DATARA/discussions/369#discussioncomment-18745667) says the artifact cannot be approved while absent from main and offers: land readable artifact on main then approve; point to its actual location; or approve a narrower increment executable from committed source. No approval is inferred. Keep contract-dependent public route/field/disclosure changes blocked. An independently scoped identity-bound read path may proceed only within committed source and its approved limits: existing saved retrieval services, no invented route/fields/version, no model/provider/network, no recomputation, generic missing/non-owned denial.
- **PR #393 verification scope:** [Discussion #411](https://github.com/fengguode/DATARA/discussions/411). A request for targeted synthetic verification was tied to an earlier head; it was superseded at dbb4f3bf…. The later report confirms merge, not exact-head test authorization or verification. Last known status: no explicit fresh textual approval for the superseding head. Re-read the complete thread; do not run tests for that head without the applicable approval. Earlier synthetic test authorization in #341 is a separate scope.
- **C6 decision:** [Discussion #412](https://github.com/fengguode/DATARA/discussions/412) / issue #387. The last known disagreement is implementation-gap vs. absence of association-table evidence. PR #391's evidence map does not resolve the owner choice; preserve no-priority/no-start.
- The no-priority rule and these holds apply only to affected actions; continue independent eligible work.

## Delivered code and integration history

The latest main observed for this handover is d393680ad83f8ec25f3ff43a881d1a8430a0dfa9, merging PR #416's documentation-only TK35/STK110 outcome matrix. It preserves TC45 and product/accessibility evidence as open. Confirm main before action.

Useful merged increments in the history include:
- PR #372 complete-UTC-day consistency, merge 2e516b0d5928481f17b08252f0719c29992f6f25; 12 targeted and 316 full synthetic PostgreSQL checks passed on that candidate. This is pure calculation, not persistence/UI/API.
- PR #365 saved-metric preparation operation, merge 9421e8ad83e83c02624c06a570bc903413dce64b.
- PR #362 independent-process saved history, merge c1f243904d7df38dd2057643c4c9ee1571efc998.
- PR #361 read-only preserved-schema preflight, merge 3976ecb321d2c86e88b9ec0896b3af8db62c0add. This is a synthetic/read-only diagnostic, not approval or execution of preserved database adoption.
- PRs #357, #359 and #360 consolidated saved-metric source/concurrency/graph-integrity history; PR #374 records skill discovery in roster/workflow; PR #391 adds a WP01 evidence map; PR #393 merges bounded WP03 engine work; PR #414 aligns WP01 evidence map to D01; PR #416 documents catalog acceptance states. Refresh all exact PR states/heads before relying on them.

Important source map (confirm against current main):
- datara/intake.py, classification.py, canonical.py, normalization.py, dedup.py, storage.py, provenance.py, db.py: source acceptance and owner-scoped data-home services.
- datara/scoped_input.py: frozen owner-scoped input versions/snapshots and source evidence.
- datara/recorded_metrics.py, datara/metric_projection.py, datara/models.py, datara/metric_store.py, migrations: pure source-bound summary/trend, projection and immutable persisted metric graph; existing internal reads include get_metric, get_metric_evidence, list_metrics_for_snapshot. Do not infer that a user-facing page is runnable from these internal services.
- datara/recorded_consistency.py: pure complete-UTC-day calculation; persistence and public presentation are separate decisions/gates.
- datara/preflight/ and scripts/syncdb_preflight.py: read-only catalog/equivalence diagnostics, not DB adoption.

## Execution rules and gates

- Work one backlog item at a time. Name WP/CUS/SR/feature/task IDs, acceptance criteria, dependencies, branch/head and exclusive files. Preserve source and failed histories. Primary inspects every changed tracked and untracked path.
- Run bounded assignments with independent technical review and evidence-backed QA appropriate to the candidate. Review the exact head. Do not reuse a test/review result from another SHA.
- Tests: founder-approved synthetic disposable PostgreSQL scope in [#341](https://github.com/fengguode/DATARA/discussions/341) applies only to that recorded scope. It does not grant arbitrary tests, current #393 verification, preserved DB access, grants or production data. Read #411 for its separate current-head decision. Never run product tests absent applicable user authorization.
- Distinguish mocked tests, synthetic PostgreSQL evidence, real application-role isolation, rendered same-origin browser behavior, live customer-selected provider/model integration and final athlete validation. No one category substitutes for another.
- WP06 requires candidate-specific applicable SR evidence, required TCs including TC15 athlete journey, defect disposition, founder acceptance, and separate release readiness/authority. A merged PR, passing tests or Project Done is not full P0 acceptance.

## Transfer report

At the point of handover, report in a separate owner-facing Announcement: receiving coordinator and effective model/runtime status (or unknown), control #8 ownership readback, chosen WP/task, exact main/base/head, exclusivity, completed and remaining evidence, holds, and next action. Do not report OpenCode as active until it actually acknowledges/acts. This document is a dated map; refresh it when work is accepted or materially changes.
