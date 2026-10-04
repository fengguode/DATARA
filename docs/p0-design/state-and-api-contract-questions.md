# State-transition and read-only API contract questions

Question material for the WP05 saved-history read contract. **This document contains no
contract.** It contains no route, no field name, no response wrapper, no version identifier and
no status-code mapping. Those belong to [discussion #369](https://github.com/fengguode/DATARA/discussions/369)
and, beneath it, to decision D04. This document exists so that whoever writes that contract does
not have to start from nothing.

Status: **question material only.** Nothing here is approved, implemented, verified, accepted or
released. No requirement status, readiness, priority or lifecycle field is changed by this file.
No registry file was edited; traceability changes are *reported* in section 9, not applied.

Work package WP01. Subtasks STK200, STK201, STK202, STK203, STK226, STK227 — all P0, all recorded
`Planned` / `Proposed`, therefore none is decision-blocked.

Author: System Architect — Feng Guo_space-bunny-free-xhigh_OpenCode (AI agent)

Assignment: issue [#383](https://github.com/fengguode/DATARA/issues/383). Base commit for every code
citation below: `9a1693b` (the commit this file was authored against, in a detached worktree).

---

## 1. What this document is, and what it deliberately refuses to be

| This document **does** | This document **does not** |
| --- | --- |
| List repository facts a contract author would otherwise have to re-derive | Select a resource, route, method or path |
| Record where the requirements and the code already disagree | Select a response shape, member name or content type |
| State each unresolved item as a question with a named decision owner | Select a version identifier or how it is declared |
| Record what the product code can and cannot currently produce | Select an outcome name, a state vocabulary or a status-code mapping |
| Point at existing precedent without restating a contract | Infer any legal, retention or period outcome |

Authority boundary for the material that is withheld here:

| Withheld artefact | Owner | Where |
| --- | --- | --- |
| Saved-history page and read-API detail, including every wire decision | Founder | discussion #369 (open, `need owner decision`) |
| Exact read-surface schemas, pagination and access direction | Founder | D04, `docs/management/decision-register.md:20` |
| Exact pagination, accessibility scope and operational evidence as accepted Milestone A risk | Founder | D04 disposition, `decision-register.md:62` |
| Run outcome vocabulary and provider failure/retention policy | Founder | D03, `decision-register.md:19` |

## 2. How to read a claim

Every substantive line is marked:

- **established** — followed by the requirement identifier plus `path:line`, or by the code path
  and line, that proves it. All code citations are at commit `9a1693b`.
- **unknown** — followed by the precise question and the accountable decision owner. The owner
  convention follows STK245: for each unresolved item, record either a source with its limits or
  an accountable owner decision, and infer no period or legal outcome
  (`docs/management/requirements-registry.json:13902`).
- **derived** — an inference I performed by exhaustive reading of a bounded set of code sites. The
  derivation is stated so a reviewer can re-perform it. Nothing here was executed; see section 10,
  finding F7.

Owner convention used throughout, per STK245 as referenced by the assignment:

- **Founder** — product outcome, scope, what a customer may see or retrieve, and any choice between
  observable customer behaviours.
- **System Architect** — structural mapping: how a chosen outcome is expressed, ordered, isolated
  and versioned, once the founder has chosen the outcome.

## 3. Repository facts that bound all six sections

These are the load-bearing facts. Everything in sections 4–8 either rests on them or is an
explicit question about them.

| # | Fact | Evidence |
| --- | --- | --- |
| E1 | No HTTP surface exists. There is no `datara/views.py` and no URL configuration module anywhere in the package. | Full recursive listing of tracked Python sources under `datara/` and `scripts/`; `datara/settings.py:71` sets `ROOT_URLCONF` to `None`, `:72` sets an empty template list, `:73` sets no WSGI application |
| E2 | No session or token identity source is installed. Only contenttypes, auth and the app are installed, with the in-code statement that no sessions, messages, admin or static surface is installed; the middleware list contains authentication but no session middleware. | `datara/settings.py:52-59`, `:64-69` |
| E3 | No run-lifecycle entity is persisted anywhere. The migrations create exactly `Import`, `SourceObject`, `Activity`, `Session`, `Snapshot`, `Eligibility`, `Evidence`, `Quarantine`, then `Metric`, `MetricOperand`, `MetricSeal`. | `datara/migrations/0001_initial.py:29,51,68,95,114,137,152,168`; `datara/migrations/0002_saved_metric_graph.py:218,242,253` |
| E4 | The only three closed vocabularies in code are the import disposition, the activity disposition and the quarantine state. None of them is a run lifecycle. | `datara/models.py:183-186`, `:279-281`, `:567-570` |
| E5 | Owner derivation exists in the data layer and is server-side. No client-supplied owner identifier is trusted. | `datara/db.py:76`, `:92`; `datara/metric_store.py:71` |
| E6 | Absent and foreign are already collapsed to one indistinguishable signal in the data layer. | `datara/db.py:114-116`, `:121-122`, `:126-129`, `:134-135`, `:143-144`; `datara/metric_store.py:80`, `:86`, `:377` |
| E7 | The recorded-metric read result carries the state as a plain string, not an enumeration. | `datara/metric_store.py:54`, built by the single helper at `:214-220` |
| E8 | **derived.** The closed set of states the read path can produce is five: the helper default, one explicit non-success state used at four sites, one propagated refusal reason, and two explicit non-success states. The only refusal reasons reachable through the read path are the corrupt-content, source-unavailable and incomplete-graph reasons. | Helper at `datara/metric_store.py:214-220`; its call sites at `:315`, `:337`, `:341`, `:344`, `:350`, `:355`, `:357`, `:359`, `:361`; reasons raised at `:96`, `:113`, `:117`, `:138`, `:147`, `:161`, `:166`, `:191`, `:195`, `:202`, `:212`, `:328` and consumed at `:356-357` |
| E9 | Refusals raised *out of* the read methods are a different vocabulary from the read states: a generic not-available reason, a retrieval-unavailable reason, plus four reasons reachable only on the save path. | `datara/metric_store.py:80`, `:86`, `:369`, `:377`, `:385`, `:393`, `:231`, `:257`, `:313`, `:245`, `:321` |
| E10 | The deterministic preparation layer raises roughly thirty distinct internal refusal reasons, far finer-grained than any observable state. The store collapses them. | `datara/recorded_metrics.py:208-522`; collapse at `datara/metric_store.py:356-357`, `:360-361` |
| E11 | List reads are complete, unfiltered and unpaged. There is no limit, offset, cursor or filter parameter anywhere in tracked source; the only count method returns one owner's activity total. | `datara/db.py:101-105`, `:146-152`, `:107-108`; `datara/metric_store.py:387-393` |
| E12 | The three existing orders are total and deterministic but are **not** insertion order. Activity order is by session start then activity identifier; eligibility order is by rule-set version then eligibility identifier; metric order is by a wall-clock insert timestamp then the metric identifier, and that identifier is randomly generated. A transaction-identity column exists as an append-order proxy but is not unique and no list method returns it. | `datara/db.py:104`, `:151`; `datara/metric_store.py:391`; `datara/models.py:521`, `:507`, `:522`; refresh at `datara/metric_store.py:311` |
| E13 | The evidence read surface is already split in two by design: the source-level reader deliberately excludes computed evidence, and the computed reader is a separate method on a separate store. | `datara/db.py:138`; `datara/metric_store.py:371-385` |
| E14 | Saved recorded graphs are immutable in both the ORM and the database, and the evidence set is closed once the graph is sealed. | `datara/models.py:487-488`, `:495-501`, `:483`; `datara/migrations/0002_saved_metric_graph.py:241` |
| E15 | Versioned *internal persisted* identifiers exist in code and are re-checked on every read. They are not a read-surface version, and no read-surface version identifier exists anywhere in the repository. | `datara/metric_projection.py:18-27`; `datara/recorded_metrics.py:28-31`; checks at `datara/metric_store.py:329-344` |
| E16 | No read-surface version identifier, route table or status-code mapping exists in tracked source. The two places that contain such material — the WP01 read-API proposal and discussion #369 — are both unapproved proposals. | `docs/management/wp01-requirements-package.md:149-168`; discussion #369 (open) |

---

## 4. STK200 — outcome-to-source list

**Subtask.** Registry statement, output and oracle: "List allowed transitions … the brief names its
observable state and the controlling source; oracle TC60"; declared output "Outcome-to-source list";
decisions D03; priority P0; readiness Proposed; owner System Architect; CUS07, FEAT07, SR14, SR15.
Evidence: `docs/management/requirements-registry.json:11165`, `:11187`, `:11193`. Issue
[#219](https://github.com/fengguode/DATARA/issues/219). **Oracle TC60**, expected states at
`docs/management/validation-plan.md:60`.

**Acceptance shape.** For every allowed run outcome: the observable state, and the controlling
source. "Allowed" is bounded by SR14 and SR15, which are the only run-lifecycle requirements that
exist (`registry:761`, `:800`).

| # | Outcome event | Observable state | Controlling source | Mark |
| --- | --- | --- | --- | --- |
| 1 | Run accepted, nothing dispatched yet | One of the four SR14 lifecycle states, first of them | SR14 text names four states: pending, running, succeeded, failed (`registry:761`) | **established** as requirement text. **unknown**: which of the four is the initial one, and whether the initial state is observable before any dispatch |
| 2 | At least one child execution nonterminal | The aggregate is held in the running state | `docs/p0-design/implementation-contracts.md:56` — the aggregate stays running while any child is nonterminal | **established** that a proposal exists; the proposal is not approved |
| 3 | Every child execution validates | Succeeded | `implementation-contracts.md:56` — succeeded when all children succeed | **established** that a proposal exists; not approved |
| 4 | No child succeeds and at least one fails | Failed | `implementation-contracts.md:56` — failed when none succeeds and at least one fails | **established** that a proposal exists; not approved |
| 5 | At least one succeeds and at least one fails | **No SR14 state exists for this** | `implementation-contracts.md:56` proposes a fifth aggregate state and states in the same sentence that it requires a synchronized SR/state contract decision before implementation; `decision-register.md:78` confirms SR14's four states do not yet admit the aggregate outcome a multi-skill combination needs | **unknown** — the fifth aggregate state. **Owner: founder** (it changes an SR's own text, D03) |
| 6 | Provider times out | SR15 requires an explicit failure **or** invalid-result state, and forbids persisting it as a successful assessment | SR15 (`registry:800`); TC60 lists timeout as its own expected item (`validation-plan.md:60`) | **unknown** — which of the two SR15 families, and whether it is one state or two. **Owner: founder** (D03) |
| 7 | Provider rejects the credential | as row 6 | SR15 (`registry:800`); TC60 lists an authentication-failure item (`validation-plan.md:60`) | **unknown**, **owner: founder** (D03) |
| 8 | Model response is malformed | as row 6 | SR15 (`registry:800`); SR70 (`registry:1952`) | **unknown**, **owner: founder** (D02/D03) |
| 9 | Provider error or rate limit | `implementation-contracts.md:23` lists both among the explicit states | TC60 lists a provider-error item (`validation-plan.md:60`) | **unknown**, **owner: founder** (D03) |
| 10 | User cancels | `implementation-contracts.md:23` lists cancellation as an explicit state; `implementation-contracts.md:56` keeps cancellation an explicit unresolved WP04/D03/D05 gate | — | **unknown**, **owner: founder** (D03) |
| 11 | Any selected skill is ineligible | No run may be created at all | `implementation-contracts.md:9` — eligibility completes before an execution request, and an ineligible selection produces zero provider calls; oracle TC07 (`registry:2333`) | **established** that no run exists. **unknown**: what the customer observes instead, and whether that observation belongs to the run contract or to the eligibility surface |
| 12 | Process restarts while a run is nonterminal | — | `implementation-contracts.md:56` keeps restart recovery an explicit gate | **unknown**, **owner: founder** (D03/D05) |

### 4.1 The controlling-source question STK200 actually turns on

TC60's procedure requires **two** separate observations per run — the persisted status and the
visible status — and then a comparison against the approved outcome
(`registry:2618`, `validation-plan.md:60`). So the contract author is not choosing one state; the
oracle is already written to require two, plus their agreement.

- **unknown.** When the persisted status and the visible status disagree, which one is
  authoritative, and is disagreement itself an observable outcome or an internal defect?
  **Owner: founder** for which behaviour the customer sees; **System Architect** for the structural
  mapping once the behaviour is chosen.
- **unknown.** Does the customer-visible surface project the run state at all, or only the terminal
  outcome? Nothing in SR14, SR15 or TC60 says. **Owner: founder.**
- **established** that no persisted state exists to project from at all (E3), so this is a contract
  about entities that have no schema. The aggregate/child decomposition in
  `implementation-contracts.md:38-41` is the only shape on record.
- **unknown.** Whether a customer sees the per-child decomposition or only the aggregate. **Owner:
  founder.**

---

## 5. STK201 — cases that must be refused

**Subtask.** Registry statement: "Add impossible transition cases. Given repeated submission and
retry are not resolved in D03, when those cases are reviewed, then each is recorded as an open
decision rather than silently selected; oracle TC60"; declared output "Explicit open retry/submission
questions"; decision D03; P0; Proposed; CUS07, FEAT07, SR14, SR15.
Evidence: `registry:11239`, `:11242`, `:11248`. Issue
[#220](https://github.com/fengguode/DATARA/issues/220).

The acceptance criterion is itself the instruction: **do not select a behaviour.** Each case below is
therefore recorded as a refusal obligation plus an open decision, never as a rule.

| # | Case that must be refused | Established constraint | Mark and open decision |
| --- | --- | --- | --- |
| R1 | A retry that changes the selected connection or the selected model | `implementation-contracts.md:40` — a retry never changes the selected provider or model; `:10` and `:23` — no silent fallback to another provider, model or platform-owned credential; `:23` — retry is only the same selected connection, and only if an approved policy permits | **established** that this must be refused. **unknown**: whether retry is permitted at all. **Owner: founder** (D03) |
| R2 | A retry that silently overwrites an earlier attempt | `implementation-contracts.md:40` — a retry is a separate attempt and cannot overwrite an earlier attempt | **established**. **unknown**: whether earlier attempts remain individually visible. **Owner: founder** |
| R3 | A second submission of the same selection while the first run is nonterminal | `implementation-contracts.md:56` — re-running the combination creates a new run | **established** that a new run is the shape. **unknown**: whether the second submission is refused, queued, or creates a parallel run. **Owner: founder** (D03) |
| R4 | Concurrent duplicate submission from two tabs or two clients | — | **unknown** entirely. No requirement, code path or proposal addresses it. **Owner: founder** for the customer-visible outcome, **System Architect** for the isolation mechanism |
| R5 | Aggregate promotion when child executions disagree | `implementation-contracts.md:56` gives the promotion conditions for the first three rows of section 4 and stops at the fifth aggregate state | **unknown** — the fifth aggregate state again. **Owner: founder** |
| R6 | Creating a run when any selected skill is ineligible, including dropping the ineligible member silently | `implementation-contracts.md:9` — zero provider calls; `implementation-contracts.md:56` — reject creation if any selected skill is not eligible and do not silently drop ineligible members | **established** |
| R7 | Persisted and visible status disagreeing with no approved mapping | TC60 compares both against the approved outcome (`registry:2618`) | **unknown** — the mapping does not exist. **Owner: founder** |
| R8 | Restart recovery re-dispatching work that already dispatched | `implementation-contracts.md:56` — restart recovery is an explicit gate | **unknown**. **Owner: founder** (D03/D05) |
| R9 | A duplicate saved recorded aggregate being written twice instead of reused | Already refused by the unique constraint at `datara/models.py:527`, enforced by the named constraint constant at `datara/metric_store.py:397`; an exact repeat reuses the saved graph (`datara/metric_store.py:265`, `:315`) | **established** for the deterministic graph only |

### 5.1 The precedent that cuts both ways

R9 is the **only** idempotence the product actually implements, and it is not a model run.

- **established.** The founder has already recorded, for the import chain, that one row per source
  digest is the intent, that the shipped unique constraint encodes that reading, and that a
  per-submission audit trail "would be a new entity" (`decision-register.md:102`). The constraint is
  explicitly not to be relaxed.
- **unknown.** Does that same "one row per digest, no per-submission trail" position extend to run
  attempts, or is a run attempt a genuinely different case because it is nondeterministic? The
  founder's recorded reasoning for the import case does not transfer on its own.
  **Owner: founder** (D03).
- **unknown.** Does an attempt record exist at all in P0? `implementation-contracts.md:40` describes
  one, and the binding architectural condition forbids persisting a skill-against-model outcome under
  Milestone A (`decision-register.md:70`), so the attempt entity is outside the authorised increment.
  **Owner: founder** (D03) for whether it is deferred, and **System Architect** for its shape if it
  is admitted.

---

## 6. STK202 — invalid response classes and the validation questions that stay open

**Subtask.** Acceptance: "Given the WP01 valid-output proposal, when invalid response classes are
reviewed, then each has a proposed non-success outcome or a recorded D02/D03 question; oracle TC61";
output "Invalid-output decision table"; decisions D02, D03; P0; Proposed; CUS07–CUS08, FEAT40,
SR15, SR70. Evidence: `registry:11295`, `:11298`, `:11304`. Issue
[#221](https://github.com/fengguode/DATARA/issues/221). **Oracle TC61**, procedure and expectation at
`registry:2627-2628`.

### 6.1 The classes the requirements already name

Each class below is named by an existing requirement or oracle. **None has a decided outcome**, and
none may be given one here.

| # | Class | Where the class is named | Required effect | Mark |
| --- | --- | --- | --- | --- |
| C1 | Response structure does not match the approved output schema | SR70 (`registry:1952`); TC61 (`registry:2627`) | Non-success; no finding exposed | **established** that it must be non-success. **unknown**: which non-success state. **Owner: founder** (D02) |
| C2 | Classification is not supported | TC61 (`registry:2627`) | Non-success; no finding exposed | as C1 |
| C3 | Response does not match the run's selected snapshot | SR70 (`registry:1952`); TC61 (`registry:2627`); STK203 (`registry:11352`) | Non-success; no finding exposed | as C1 |
| C4 | Response does not match the run's selected skill version | SR70 (`registry:1952`); TC61 (`registry:2627`); STK203 (`registry:11352`) | Non-success; no finding exposed | as C1 |
| C5 | Evidence references do not all resolve to the run snapshot | `implementation-contracts.md:11`; TC61 (`registry:2627`); STK203 (`registry:11352`) | Sanitized failure artefact, never an assessment | **established** that it must not be an assessment. **unknown**: whether the sanitized artefact is persisted at all |
| C6 | Response is structurally valid but partly unusable | `implementation-contracts.md:11` names "invalid **or partial** model responses" | Treated as failure artefact | **unknown** — partial is named but never defined. **Owner: founder** (D02) |

### 6.2 The validation questions that remain open

- **unknown.** Does one non-success state serve all six classes (C1–C6), or does each class get its own
  observable state? The store already collapses roughly thirty internal reasons into a handful of
  observable states (E10, E8), which is precedent for collapsing — but the deterministic path has no
  customer-visible failure surface, so the precedent does not transfer by itself. **Owner: founder**
  for granularity as a customer-visible choice; **System Architect** for the mapping.
- **unknown.** Does the contract author depend on the store's plain-string state (E7, `metric_store.py:54`)
  or on a declared closed set? Nothing in code prevents a future producer from widening the
  observable set. **Owner: System Architect** (structural), then **founder** for any widening that
  becomes customer-visible.
- **unknown.** What is the precedence when several classes apply at once — for example a response
  that is both malformed and snapshot-mismatched? **Owner: System Architect** for the ordering rule,
  **founder** for whether the precedence is customer-visible.
- **unknown.** Is validation performed before or after the response is persisted? SR70 says an
  invalid response is recorded as a non-success outcome (`registry:1952`), which implies something is
  persisted; the binding condition forbids persisting a skill-against-model outcome under Milestone A
  (`decision-register.md:70`). **These two cannot both hold for the authorised increment.**
  **Owner: founder** — this is a scope conflict, not an engineering choice.
- **unknown.** Does a non-success outcome retain the response at all, in sanitized form, and with
  what retention limit? `test-design-findings.md:61` records retention of sanitized failure evidence
  as unapproved, and TC63 (`registry:2642`) requires that sentinels not reappear in retrieved
  failure output. **Owner: founder** (D03), no legal or period outcome inferred.
- **unknown.** Is a version mismatch distinguishable from a content mismatch in the saved record?
  The recorded path already distinguishes them by comparing version constants before content
  (`datara/metric_store.py:329-336`). **Owner: System Architect.**

---

## 7. STK203 — negative examples and the unresolved ordering cases

**Subtask.** Acceptance: "Given malformed, mismatched-version, mismatched-snapshot, and
missing-evidence examples, when they are compared with the proposed contract, then unsupported
oracle details are labeled unresolved; oracle TC61"; output "Negative example and unresolved-oracle
list"; decisions D02, D03; P0; Proposed. Evidence: `registry:11352`, `:11355`. Issue
[#222](https://github.com/fengguode/DATARA/issues/222).

### 7.1 Negative examples that exist and have been executed

These are the real negative examples the repository has today. All are **deterministic-graph**
negatives, not model-response negatives — that limit matters and is stated.

| # | Negative example | Established evidence |
| --- | --- | --- |
| N1 | A foreign metric, foreign evidence and a foreign snapshot are all unavailable | `datara/tests/test_saved_metrics.py:89`, `:96` |
| N2 | A changed source makes saved history unavailable and the saved history is preserved | `datara/tests/test_saved_metrics.py:157`, `:161` |
| N3 | A sealed graph rejects update, delete and any additional evidence | `datara/tests/test_saved_metrics.py:128`; constraint at `datara/models.py:483` |
| N4 | Committing a new graph without its seal is rejected | `datara/tests/test_saved_metrics.py:145` |
| N5 | An outer-transaction rollback leaves no provisional graph | `datara/tests/test_saved_metrics.py:119` |
| N6 | A failure on the second computed evidence row rolls back the entire graph, and a retry then succeeds | `datara/tests/test_saved_metrics.py:99` |
| N7 | An exact repeat reuses one complete graph rather than writing a second | `datara/tests/test_saved_metrics.py:79`; `datara/metric_store.py:265`, `:315` |

- **established** that the model-response negative examples STK203 names — malformed,
  mismatched-version, mismatched-snapshot, missing-evidence — have **no** executed counterpart,
  because no run, attempt or assessment entity exists (E3) and Milestone A makes no provider call
  (`decision-register.md:53`, `datara/settings.py:1-7`).
- **unknown.** Which of the seven deterministic negatives is the right *shape* template for a
  run-lifecycle negative, given that a run is nondeterministic and the deterministic path's
  idempotence-by-content-digest has no run analogue. **Owner: System Architect** to propose the
  mapping; **founder** to confirm the customer-visible outcome.
- **unknown.** Whether N5's rollback semantics carry over: a run that has already dispatched cannot
  be rolled back the way a graph can. **Owner: founder** (D03).

### 7.2 The unresolved ordering cases

STK203 asks for unresolved oracle details to be labelled unresolved. These are the ordering cases I
could not resolve from any existing source.

| # | Ordering case | Mark and owner |
| --- | --- | --- |
| O1 | A collection is paged by a sort key, and a new row sorts *before* rows already read. Does the customer see a duplicate or an omission? This is unavoidable for any key-ordered paging, and the code already commits to key ordering (E12). | **unknown.** **Owner: System Architect** — structural; **founder** confirms whether the resulting observable is acceptable |
| O2 | Metric order ties on the wall-clock insert timestamp and resolves by a randomly generated identifier (E12). Is a randomly ordered tie-break acceptable as a contractual order? | **unknown.** **Owner: System Architect** |
| O3 | The order of a child execution list relative to its parent aggregate list. Neither entity exists (E3). | **unknown.** **Owner: System Architect** after the founder chooses whether children are customer-visible at all (section 4.1) |
| O4 | The order of the deterministic-observation list relative to the run-history list. Two independent lists, no shared order rule in any source. | **unknown.** **Owner: System Architect** |
| O5 | An item whose saved history has become unavailable (N2) — does it keep its position in the order, or is it removed from the collection? Removing it silently shortens the collection; keeping it exposes unavailability at a position. | **unknown.** **Owner: founder** for the customer-visible choice, **System Architect** for the mechanism |
| O6 | Page composition when availability changes between two requests on the same position, given a repeated position must preserve ordering (TC72, `registry:2727`). | **unknown.** **Owner: System Architect** |
| O7 | Whether the three existing code orders (E12) become the contractual orders, or whether a new order is introduced that the code must then be changed to match. | **unknown.** **Owner: founder** via D04 for the direction, **System Architect** for the expression |

---

## 8. STK226 — API purpose and access questions, without selecting routes

**Subtask.** Acceptance: "Given D04 and the read-only API outcome, when stakeholder retrieval needs
are collected, then resource purpose and unresolved version/access questions are listed without
selecting routes; oracle TC70-TC72"; output "API requirements question list"; decision D04; P0;
Proposed; CUS09, FEAT42, SR19, SR31, SR73. Evidence: `registry:12715`, `:12718`, `:12726`. Issue
[#245](https://github.com/fengguode/DATARA/issues/245). Oracles TC70–TC72 at `registry:2705`,
`:2714`, `:2723`.

### 8.1 Purpose questions

| # | Question | Mark and owner |
| --- | --- | --- |
| B1 | Which customer decision does each resource serve? One candidate outcome is stated at `docs/management/wp01-requirements-package.md:151`; three alternative scopes are offered at `docs/p0-design/decision-proposals.md:10`. | **unknown.** **Owner: founder** (D04) |
| B2 | Which of the four dashboard views at `wp01-requirements-package.md:153` does each resource back, and does every view need a resource at all? | **unknown.** **Owner: founder** with the UI Designer |
| B3 | Is the deterministic-observation family — the saved recorded aggregate, which has no model run (`decision-register.md:70`, `metric_store.py:1-5`) — in scope for a customer-facing resource, or internal only? | **unknown.** **Owner: founder.** This is the question that most directly determines whether #369 is a customer increment at all |
| B4 | Is external retrieval by the athlete's own browser session, or by a separate client application? | **unknown.** **Owner: founder** (D04/D05) |
| B5 | What may a client retain after a successful retrieval, and for how long? | **unknown.** **Owner: founder.** No period or legal outcome is inferred here, per STK245 (`registry:13902`) |
| B6 | Does the read surface expose anything the dashboard does not, or anything the dashboard does not expose? SR31 requires the dashboard to derive its displayed saved values from the same contracts (`registry:1292`), which constrains but does not answer this. | **unknown.** **Owner: System Architect** to state the constraint precisely; **founder** for any divergence |

### 8.2 Access questions

| # | Question | Mark and owner |
| --- | --- | --- |
| A1 | What authenticates a caller at all? **established**: nothing is installed — no sessions application, no session middleware, no URL configuration (E1, E2, `settings.py:52-59`, `:64-69`, `:71`). | **unknown.** **Owner: founder** (D05, identity integration) |
| A2 | Is a request identity the same identity as the athlete's browser session? | **unknown.** **Owner: founder** (D05) |
| A3 | Does an unauthenticated caller learn that the resource family exists? | **unknown.** **Owner: founder** |
| A4 | Can an operation-level policy denial precede object resolution? **established**: it must never depend on whether another owner's resource exists — SR73 (`registry:2095`); the data layer already collapses absent and foreign to one signal (E6). | **established** as a constraint. **unknown** as a gate ordering. **Owner: System Architect** |
| A5 | Does an authorized-but-denied operation differ observably from an absent resource? SR73 forbids the difference from revealing existence (`registry:2095`). | **unknown.** **Owner: founder** for the customer-visible outcome, **System Architect** for the mechanism |
| A6 | Is a per-owner secret for an external client ever issued in P0? **established**: the pilot is loopback-only and the deployment intent is explicitly not a production configuration (`settings.py:24-31`). | **unknown.** **Owner: founder** (D05) |
| A7 | Is there any rate limit? **established**: no limiter exists in tracked source, and rate limiting is recorded as unapproved (`test-design-findings.md:61`). | **unknown.** **Owner: founder** (D04) |
| A8 | Is the user interface in the authorization boundary? **established**: it is not — the API and internal component boundaries must enforce access themselves (`docs/p0-design/architecture-baseline.md:119`). | **established** |
| A9 | Does evidence dereferencing re-check both owner and snapshot boundary? **established**: it must, and snapshot-bound evidence resolution must not become an authorization bypass (`architecture-baseline.md:91`); the code already filters evidence by owner and metric kind before resolving the parent (`metric_store.py:374-379`). | **established** as a constraint. **unknown** whether the contract author states it explicitly or inherits it. **Owner: System Architect** |

### 8.3 Version questions

| # | Question | Mark and owner |
| --- | --- | --- |
| VN1 | What identifies a read-surface version, and where is it declared? **established**: internal persisted version identifiers exist and are re-checked on every read (E15, `metric_store.py:329-344`); no read-surface identifier exists anywhere (E16). | **unknown.** **Owner: System Architect** structurally; **founder** owns the wire choice in #369 |
| VN2 | May the read-surface version differ from the persisted graph version it renders? **established**: they are different concerns already — the persisted version is checked against the reader's expectations and a mismatch produces an explicit non-success state rather than a reinterpretation (`metric_store.py:329-350`, and the comment at `:352` states reconstruction is solely an equality oracle). | **unknown** whether that read-path behaviour becomes the contractual behaviour. **Owner: System Architect** |
| VN3 | What happens when a future reader meets a graph it cannot interpret? **established** precedent: return an explicit non-success state and never reinterpret history (`metric_store.py:337-350`). | **unknown** as a customer-visible contract. **Owner: founder** |
| VN4 | Is an unrecognised response member an error or ignored? Nothing in any source decides forward compatibility; the WP01 proposal requires an explicit schema version but does not decide compatibility (`wp01-requirements-package.md:166`). | **unknown.** **Owner: System Architect** |
| VN5 | Does a version change require a new resource family or a version negotiated inside one family? | **unknown.** **Owner: founder** via #369 |
| VN6 | Which internal persisted versions must the read surface expose, which must it hide, and which must it use only to decide an internal state? Exposing all of them would publish internal contract detail; exposing none would make an unrenderable graph indistinguishable from an absent one. | **unknown.** **Owner: System Architect** to propose, **founder** to confirm |

---

## 9. STK227 — mutation, query and pagination decisions still open

**Subtask.** Acceptance: "Given proposed read-only retrieval, when mutation and query scenarios are
reviewed, then required observable outcomes and unresolved pagination/error decisions are recorded
without inventing bounds or codes; oracle TC71/TC72"; output "Read-only and query decision gaps";
decision D04; P0; Proposed; CUS09, FEAT42, SR19, SR31, SR73. Evidence: `registry:12775`, `:12778`.
Issue [#246](https://github.com/fengguode/DATARA/issues/246). Oracles at `registry:2714`, `:2723`.

The acceptance criterion forbids inventing bounds and codes. No number, no bound and no mapping
appears in this section.

### 9.1 Mutation

| # | Question | Mark and owner |
| --- | --- | --- |
| M1 | What must an attempted mutation observably produce? **established**: SR19 requires the read-only API to reject attempts to mutate data through its read-only routes (`registry:958`); TC70 requires persisted state unchanged (`registry:2708`); TC71 requires the D04-approved outcome and states in terms that this case "does not select the operation or representation" (`registry:2717`). An existing proposal names an observable outcome for a mutation attempt at `implementation-contracts.md:24`; I cite the line and do not restate it. | **established** that rejection is required and state-unchanged is required. **unknown** as an observable outcome. **Owner: founder** (D04) |
| M2 | Which methods are refused, per resource? | **unknown.** **Owner: System Architect** after D04 |
| M3 | Does a refusal on a foreign identifier reveal that the resource exists? **established**: it must not (SR73, `registry:2095`). | **established** |
| M4 | Is a mutation attempt on a foreign identifier refused as a disallowed operation or as an unavailable resource? The answer depends on gate ordering, which is structural and not decided anywhere. | **unknown.** **Owner: System Architect** |
| M5 | Does a refused mutation attempt produce an audit record? **established**: the founder has recorded that a per-submission trail is a new entity and the constraint must not be relaxed (`decision-register.md:102`); TC63 (`registry:2642`) covers sanitized failure retrieval, not audit of refusals. | **unknown.** **Owner: founder** |
| M6 | Is a method refusal distinguishable by the client from an unavailable resource? | **unknown.** **Owner: founder** for whether the distinction is safe to expose; **System Architect** for the mechanism |

### 9.2 Query

| # | Question | Mark and owner |
| --- | --- | --- |
| Q1 | What is the query surface? **established**: it is nil — no list method accepts any filter (`datara/db.py:101-105`, `:146-152`, `metric_store.py:387-393`). An unapproved proposal lists query parameters at `wp01-requirements-package.md:159`, `:161`, `:162`. | **unknown.** **Owner: founder** (D04) |
| Q2 | On a detail read, are query parameters rejected or ignored? | **unknown.** **Owner: System Architect** |
| Q3 | Is an unrecognised query parameter an error, or ignored? | **unknown.** **Owner: System Architect** |
| Q4 | Are date bounds half-open? **established** for persisted scope semantics only: date scopes are half-open and instants are UTC, and a naive datetime is explicitly disallowed (`datara/settings.py:75-79`). Nothing states this at the read surface. | **unknown** at the read surface. **Owner: System Architect** |
| Q5 | Can a filter select an unresolved sport value? **established**: the sub-sport allowlist is frozen and an unknown, unassigned or cross-sport value is accepted with a disclosure and resolves to an absent label rather than being rejected (`decision-register.md:94`, `:98`). A filter over such values is therefore undefined. | **unknown.** **Owner: founder** |
| Q6 | Is a filter evaluated before or after owner scoping? **established**: authorization occurs before resolving a user-scoped identifier (`docs/p0-design/implementation-contracts.md:7`); the code does this at `datara/db.py:110-116` and `metric_store.py:250`. | **established** as a constraint. **unknown** whether it is stated in the contract. **Owner: System Architect** |
| Q7 | Can a filter widen visibility within one owner, e.g. across snapshots? **established**: every read is snapshot-bound for computed evidence (`metric_store.py:374-379`), and snapshot-bound evidence resolution must not become an authorization bypass (`architecture-baseline.md:91`). | **unknown** whether a cross-snapshot read is permitted at all. **Owner: founder** |

### 9.3 Pagination

| # | Question | Mark and owner |
| --- | --- | --- |
| P1 | Is any collection paginated? **established**: no paginated read exists (E11). TC72 requires successive pages, a repeated cursor and stable errors, and states that unresolved bounds remain blocked (`registry:2726`). | **unknown.** **Owner: founder** (D04) |
| P2 | What are the default and maximum page size? **established**: unapproved — pagination defaults and maxima are explicitly a D04/D03 decision (`wp01-requirements-package.md:166`) and API pagination limits are recorded as unapproved (`test-design-findings.md:61`); D04's exact pagination remains unmet accepted risk (`decision-register.md:62`). | **unknown.** **Owner: founder.** No bound is proposed here |
| P3 | What does a position marker contain, and is it integrity-protected? | **unknown.** **Owner: System Architect** after D04 |
| P4 | Is a position marker bound to the owner? **established**: it must be — SR73 states foreign identifiers **or cursors** must not reveal another user's data or existence (`registry:2095`). | **established** as a constraint. **unknown** as a mechanism. **Owner: System Architect** |
| P5 | Must a repeated position marker return an identical page? **established** as an oracle expectation only: repeated cursors preserve ordering (`registry:2727`). "Preserve ordering" does not say whether the page is identical. | **unknown.** **Owner: System Architect** to state precisely, **founder** to confirm |
| P6 | Is an exhausted position marker distinguishable from an invalid one without revealing existence? | **unknown.** **Owner: System Architect** |
| P7 | Does ordering follow the three orders the code already commits to (E12), or a new contractual order the code must be changed to match? This is the sharpest structural question in this section, because the code has already fixed three different orders and none of them is insertion order. | **unknown.** **Owner: founder** for direction, **System Architect** for expression |
| P8 | Does a collection disclose a total count? **established**: exactly one count method exists (`datara/db.py:107-108`). | **unknown** whether a total is exposed. **Owner: System Architect** |
| P9 | What happens when availability changes between two requests at the same position? See O5 and O6 in section 7.2. | **unknown.** **Owner: System Architect** |
| P10 | Does a position marker survive a new saved aggregate being appended for the same snapshot? The uniqueness constraint at `datara/models.py:527` makes the aggregate idempotent, but `metric_store.py:265`, `:315` show the reuse path returns the existing row rather than a new one — so append order is not the same as creation order. | **unknown.** **Owner: System Architect** |

---

## 10. Divergences and findings — reported, not fixed

Each is reported with evidence and an owner. **None was fixed; no code file was modified.**

**F1 — The run-state vocabulary diverges three ways.** SR14 names pending, running, succeeded and
failed (`registry:761`). TC60 expects pending, success, authentication-error, timeout and
provider-error (`registry:2619`, `validation-plan.md:60`). The combined-run proposal needs a fifth
aggregate state that no SR names (`implementation-contracts.md:56`, `decision-register.md:78`).
TC60 and SR14 share only one state name, and TC60 has no state for a nonterminal aggregate while
SR14 has two. **Owner: founder** (D03). **System Architect** to propose the mapping. Nothing in
section 4 selects a vocabulary.

**F2 — Two unapproved artefacts disagree on the read-surface error shape.** The WP01 proposal gives
the error object a request-correlation member and an optional free-form detail member
(`wp01-requirements-package.md:166`); the #369 candidate gives the error object exactly two members
and no correlation member. Neither is approved. I cite both and restate neither.
**Owner: founder** via D04.

**F3 — #369 names one more read state than the code can produce.** The candidate lists six; E8 shows
the read path produces five. The sixth has no producer in tracked source. This is not a defect — it
is a proposed catch-all — but the contract author should state which component produces it.
**Owner: System Architect** to answer for the existing code.

**F4 — `datara/settings.py:64-69` installs authentication middleware without session middleware, and
`:52-59` installs no sessions application.** This is consistent with the in-code intent stated at
`:54-55` and is not a defect while no view layer exists (E1). It is load-bearing: any read surface
that derives the owner from a request identity will receive an unauthenticated identity until both
are added. **Reported for the coordinator and the code owner.**

**F5 — The read state is an unconstrained string while the reachable set is closed at five.** E7
versus E8. Nothing in code prevents a future producer from widening the observable set.
**Owner: System Architect** (see question VN1/VN2 in section 8.3 and section 6.2).

**F6 — The only implemented idempotence is deterministic-graph reuse, and the founder has already
ruled against relaxing the equivalent import constraint** (`decision-register.md:102`). A run
attempt audit trail is therefore not implied by existing code and not authorised under Milestone A
(`decision-register.md:70`). **Owner: founder** (see R2 and section 5.1).

**F7 — Environment limitation affecting this deliverable.** The available interpreter is CPython
3.13.15 and **Django is not installed** in it (only `garmin-fit-sdk` 21.217.0, `pip` and `PyYAML`
are present). I could not run the product test suite, could not reproduce the stated 316/316
baseline, and could not confirm the schema at runtime against the PostgreSQL 17.5 instance at
`127.0.0.1:55432`; the `psql` client is also absent. Every claim in this document is source-read
evidence at commit `9a1693b`, and no claim here depends on runtime execution. The derived claims E8
and E12 are marked *derived* for that reason and are re-performable from the cited lines.

---

## 11. Traceability notes for the coordinator — reported, not applied

No registry file was edited, as the assignment requires. The following are proposals for the
coordinator to decide:

1. **Source links.** The `source` array of STK200, STK201, STK202, STK203, STK226 and STK227 does not
   list this file. Proposal: add `docs/p0-design/state-and-api-contract-questions.md` to each of the
   six `source` arrays (`registry:11198-11203`, `:11253-11258`, `:11310-11315`, `:11367-11372`,
   `:12733-12738`, `:12793-12798`).
2. **Evidence under-coverage in STK200 and STK201.** Both list only TC60 in `evidence_ids` and
   `verification_ids` (`registry:11189-11197`, `:11244-11252`), but this document also rests on
   SR70, SR73, TC07, TC61, TC63, TC70–TC72 and TC73/TC74. STK202, STK203, STK226 and STK227 already
   list their additional cases. Proposal: widen STK200/STK201, or record why they must stay narrow.
3. **No status change is proposed.** All six remain `Planned` / `Proposed` / P0. Nothing in this
   document is evidence of product behaviour, and the six subtasks are **not** closed by it: five of
   the six ask for recorded open questions, and this document records them without answering them.
4. **Package contents list.** `docs/p0-design/README.md:15-27` lists the package files and does not
   include this one. Proposal: add a contents line. Coordinator's call, and it is a sibling file
   this assignment does not own.
5. **D04 and D03 remain open** (`decision-register.md:19-20`). The unknowns in sections 4–9 are
   routed accordingly and none of them is resolved by this document.

---

## 12. Self-check record

Performed before commit, on this file only.

| Check | Result |
| --- | --- |
| No route or path written | pass — no path is given for any resource; proposal locations are cited by `path:line` only |
| No field or member name written | pass — members are described by role, e.g. "a request-correlation member", never named |
| No response wrapper described | pass — "response shape" and "error shape" are used only to point at where two artefacts disagree (F2) |
| No read-surface version identifier written | pass — the internal persisted identifiers at E15 are cited as internal and explicitly distinguished from a read-surface version |
| No status-code mapping written | pass — outcome requirements are stated as obligations, never as a mapping; `implementation-contracts.md:24` is cited by line without restating its outcome name |
| No product code modified | pass — one added file; `git status` clean otherwise |
| No registry modified | pass — traceability changes are proposals in section 11 |
| Forbidden file untouched | pass — `demo_file/24563001348_ACTIVITY.fit` was never opened, read, copied, hashed, listed or stat-ed |
| Nothing marked Done, Verified, Accepted or released | pass — stated in the header, section 10 and section 11.3 |
