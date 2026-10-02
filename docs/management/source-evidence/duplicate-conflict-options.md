# Duplicate and conflict policy comparison

Status: proposed research output, 1 October 2026. DUPLICATE-OPTIONS-20261001 / WP01 / TK14 #120 / STK011 #183 / STK012 #184 / CUS02 / FEAT02 / SR04 / D01 / TC03. No new policy, schema freeze or implementation evidence.

[Selected D01](../p0-decision-baseline-2026-10-01.md) governs the choice. Older [WP01 alternatives](../wp01-requirements-package.md) preserve historical rationale; their undecided choice wording does not reopen the delegation. [Feng's attributed handoff](https://github.com/fengguode/DATARA/issues/120#issuecomment-5926831364) and [authoring assignment](https://github.com/fengguode/DATARA/issues/120#issuecomment-5926886049) supply scope. Fresh Project 07:35 UTC: TK14/STK011/STK012 In progress, Architect Feng Guo, W0 orders300–302, no direct prerequisites. Native configuration loading unconfirmed; primary publisher fengguode.

## Historical options and selected behavior

Examples below are conceptual policy examples, not actual telemetry, FIT artifacts or independent test oracles. X and Y denote otherwise valid file bytes; A and B denote authenticated owners.

| Option | Observable example/outcome | Limits and status |
| --- | --- | --- |
| Exact bytes only | A submits X twice: second submission refers to existing history. Different Y, even if it represents the same activity, proceeds as a separate import. | Detects identical re-import; can leave duplicates from changed exports. This is the selected idempotency layer, not the full D01 policy. |
| Documented tolerance key | Different X/Y within a hypothetical sport/start/duration tolerance would flag a possible conflict. | Historical option. No thresholds are evidenced or selected; approximate matching could flag different activities. No tolerance is invented here. |
| No logical detection | Identical bytes still follow exact-byte idempotency; different bytes are separate imports even with the same logical activity. | Historical option, not selected. Changed exports can duplicate recorded history. |
| Selected exact tuple with explicit resolution | A submits different Y matching X's exact `(owner, sport, UTC start, elapsed duration)`: quarantine Y as a possible conflict. A mismatch in any tuple component does not match this heuristic; other conformance checks still apply. | Selected application heuristic, not authoritative FIT identity. Can flag legitimate coincident activities and miss the same activity with changed tuple fields. User resolves surfaced conflicts explicitly. |

The founder delegated the D01–D05 selection to Yi/Yu; the recorded selection supersedes the old task text requesting an undecided founder choice. No additional founder endorsement is inferred from this comparison. Changing the outcome remains a separately recorded product decision.

## STK011 — owner-scoped exact-byte trace

| Conceptual scenario | Selected observable result | Contract/test gaps |
| --- | --- | --- |
| A submits accepted X again | Same owner and SHA-256 references existing history, no duplicate accepted activity. | Lost-response replay, repeated rejected/staged bytes, concurrent arrival and exact transaction outcome need frozen rules. |
| B submits the same X | Owner-scoped handling; no access to A's original, digest match or history. | Isolation and lookup responses must prove no cross-owner disclosure with two disposable users. |
| A submits a changed export Y | Exact-byte idempotency does not match; evaluate the selected logical tuple and other validity checks. | Canonical sport/start/duration representations and precision need approved field/schema mappings. |
| Concurrent A/X requests | Final accepted history must remain owner-idempotent. | Lock/constraint/job/staging semantics, conflict disposition and crash recovery are unresolved; no implementation prescribed here. |

Raw originals are immutable. Accepted original/normalized relations appear as one visible operation under D01; file/DB staging reconciliation must prevent a retry from creating a second accepted activity after a partial commit. The exact byte idempotency outcome is selected, but storage and race mechanics still require contracts and actual checks.

## STK012 — logical conflicts and resolution

| Conceptual scenario | Selected direction | Explicit remaining work |
| --- | --- | --- |
| A/X and A/Y differ in bytes, equal exact tuple | Quarantine Y as a possible conflict; exclude unresolved candidates from normal history and skill snapshots. | Quarantine state, visible explanation and permitted fields/IDs; no hidden auto-merge. |
| Tuple differs | No match from this heuristic; import only if every other conformance/eligibility check passes. | Explain that the heuristic misses changed tuple values; no comprehensive deduplication claim. |
| Keep existing | User explicitly resolves in favor of existing history. | Candidate lineage/state, visibility and lifecycle/deletion behavior must be specified. |
| Replace | Auditable supersession; preserve valid originals and lineage. | Atomic transition, interrupted resolution and references from old snapshots/results must remain historical and resolvable. |
| Retain both | User explicitly chooses both. | Record the resolution and prevent unchanged repeated submissions from silently creating more accepted copies. Exact re-import semantics after resolution need contract examples. |
| Concurrent/interrupted resolution | Only authorized owner actions may alter conflict state. | Version/race response, durable recovery and safe retry; no silently lost resolution or supersession. |

Owner identity comes from authenticated server context. Conflict reads, resolution targets and source references require authorization. Existing [intake gap evidence](fit-intake-operations-gaps.md) identifies file/DB reconciliation, logging and access questions; this comparison does not implement those controls. D04's selected retention/deletion policy must be reconciled with conflicts, supersession, backup recovery and immutable historical references; this document assigns no new retention period.

## Trace and remaining evidence

[SR04 and system requirements](../system-requirements.md) require owner-scoped repeat import without duplicate accepted activity and visible conflicts without silent overwrite. TC03's historical undecided-choice oracle needs reconciliation against the selected D01 behavior before implementation/verification, including changed bytes/equal tuple, changed tuple, separate users, explicit resolutions and races. Conceptual examples above are not frozen fixture oracles. TC03 and SR04 remain **Not run / unverified**.

Next contract work must settle mapping precision, staged/concurrent imports, authorized atomic resolution, supersession lineage, snapshot/result references, cleanup/crash/retry and deletion/backup behavior. Follow the existing backlog and [implementation plan](../p0-implementation-plan.md); this research output does not clear G0 or authorize coding. [Review record](../../team/reviews/duplicate-options-review-2026-10-01.md) holds documentation evidence separately from product checks.

---

## 2 October 2026 increment — options comparison, precedence and athlete presentation

Status: proposed architecture for the reopened TK14/STK011/STK012 increment under the founder's parallel working mode. It **extends** the 1 October comparison above; where the two differ, the section below governs. Line numbers in the section above are deliberately unchanged, because `decision-register.md:66` cites this file at lines 37 and 48. The document's 1 October header line is therefore dated-incomplete; refreshing it is a Primary Coordinator action because any inserted line breaks those citations.

Nothing here is a product selection, a schema freeze, a test result, an acceptance or a release. `TC03`, `SR04`, `TC22` and `SR33` remain **Not run / unverified**. D01's selected policy is not reopened: the founder selected it at `p0-decision-baseline-2026-10-01.md:48`, and this increment specifies the parts of it that were left open — *precedence*, *cost*, and *presentation* — so that TK15 can implement without inventing them.

Trace: WP01, TK14 (#120), STK011 (#183), STK012 (#184), CUS02, FEAT02, SR04, SR33, D01, TC03, TC22; downstream TK15 (#121), TK16 (#122).

### 1. The actual decision being made

D01 already selected the *shape* of the policy: owner-scoped exact-byte idempotence, exact-tuple quarantine, explicit resolution, no silent merge, no tolerance, no overwrite. What D01 did **not** select, and what TK15 would otherwise have to invent, is:

1. which of four candidate policy structures actually delivers that shape, and what each rejected structure costs;
2. the **precedence order** when several rules match the same submission;
3. what happens under concurrency and after a lost response;
4. how a conflict is presented to the athlete in words (TC22 / SR33 / UI-SR02, owned by User Tester).

Those four are answered below. The following are explicitly **not** answered here and remain open: any deletion/retention period, any tolerance, any automatic resolution, any aggregate deduplication claim.

### 2. The four options compared

Each option is described by what it decides, what an athlete observes, what it structurally cannot do, and what choosing it costs. X and Y are otherwise valid distinct file bytes; A and B are authenticated owners.

| Option | What it decides | Observable outcome for A | What it structurally cannot do | Cost if chosen alone | Verdict |
| --- | --- | --- | --- | --- | --- |
| **A. Content-digest-only dedup** (owner-scoped SHA-256) | Only "are these the same bytes?" | Submitting X twice returns the existing activity and a `duplicate_of_existing` file outcome. Submitting Y — the same activity re-exported — creates a second activity. | Cannot ever raise a conflict, so SR33's "unresolved conflict" state, SR32's per-file conflict outcome, UI-SR02/UI-ST06 and TC22's conflict oracle are all unimplementable. It answers *file identity*, not *activity identity*. | Silent double counting of volume, driven by an export behaviour nobody has measured: this repository holds **no evidence** that a Garmin Connect re-export of one activity is byte-stable. The athlete sees two activities from one session and nothing anywhere says otherwise. | Necessary but insufficient. Rejected as a complete policy. |
| **B. Logical-tuple quarantine** — different bytes, exact `(owner, sport, UTC start instant, elapsed duration)` | Only "might these be the same activity?" | Submitting Y equal-tuple with X gives A a quarantined candidate. Submitting Y with a differing tuple silently accepts it as a second activity. | A classifier, not a policy. It cannot release its own output. Any automatic exit is either "keep existing" (the new export is silently discarded — lossy) or "keep new" (overwrite — prohibited) or "keep both" (which is not automatic deduplication at all). Without C, quarantine is a permanent dead end the athlete cannot leave. | Locks the athlete out of their own data with no exit. Worse than A: A at least shows the duplicate; B hides both records until an exit exists. | Rejected as a complete policy. Retained as the classifier layer inside D. |
| **C. Explicit user resolution** — keep existing / replace via auditable supersession / retain both | Only "who decides, and what is recorded?" | Nothing, until something detects a conflict. It never triggers on its own. | Requires the full state machine, owner authorization, atomicity, interrupted-resolution recovery, supersession lineage and a UI state (UI-ST06). That surface is exactly what TK15 must not invent. It also carries D04's deletion-ledger and reapply-on-restore interaction, which `implementation-contracts.md:58-63` still heads *not yet implementable*. | Large contract surface built on an empty trigger set; every one of its state transitions would be unverified until B exists. | Necessary but insufficient. Retained as the exit layer inside D. |
| **D. Hybrid precedence** — A detects replay, B classifies, C resolves, in that order, with explicit precedence | All three questions, with one defined winner per submission | See the precedence table in §4. One outcome per file, every outcome textual and stable. | It does not claim comprehensive deduplication. Tuple mismatch still admits a genuine duplicate; tuple equality can still raise a false conflict. Both limits are stated to the athlete rather than hidden. | Costs the implementation of B **and** C, and requires accepting a deliberate residual: a false conflict is possible and costs the athlete one explicit decision. | **Recommended.** See §3. |

### 3. Options explicitly rejected, and what each rejection costs

| Rejected option | Why rejected | What the rejection costs |
| --- | --- | --- |
| **Tolerance / fuzzy tuple matching** (e.g. "within 5 seconds and 1%") | Prohibited by `p0-decision-baseline-2026-10-01.md:48` and by the product rule against silent merging. Independently: no threshold value is evidenced anywhere in this repository, so any number would be invention, and an approximate match that is wrong **destroys information** — it merges two real activities or discards one. Every other failure mode in this document is recoverable by an explicit user action; an incorrect automatic merge is not. | A permanent, unrequested blind spot: distinct activities inside any chosen tolerance are never surfaced, so the athlete is never told their two sessions may have been conflated. Retaining this cost is the point. |
| **No logical detection at all** (strict A) | Recorded historically at line 15 above. It is option A restated. | Silent double counting, per A's cost. |
| **Automatic resolution** (quarantine auto-releases to "keep both" after N days, or resolves on a score) | Would require a similarity judgement with no evidence behind it, and "keep both" is not deduplication. | The athlete's history silently grows a value they never chose, and the "unresolved" state that TC22 asserts would never be observable. |
| **Suppressing future quarantines after a "retain both" resolution** | A recorded resolution is a statement about two specific originals, not a standing waiver. Suppressing would create a permanent blind spot for that tuple. | Retaining it costs the athlete a repeated explicit decision for each *newly exported* variant of the same activity. That is the visible, correct cost of never guessing. Flagged as open product question **OQ-1** below. |

### 4. Recommendation and rationale

**Recommend Option D, hybrid precedence, in the order A → B → C.**

Rationale, in the order the arguments actually hold:

1. **The three options answer three different questions and no single one answers all of them.** A answers "same file?"; B answers "same activity, maybe?"; C answers "who decides?". Collapsing them into one option either loses a question or invents an answer. The product requires all three answers, so the structure must carry all three layers.
2. **Only D can fail safely.** A's failure is invisible (a duplicate the athlete never sees). B's failure is a dead end. C's failure is undefined behaviour. D's failures — a missed duplicate and a false conflict — are both **visible and explicitly resolved by a human**, which is the only failure posture consistent with "never silently merge, never overwrite".
3. **D is what D01 already selected**, so recommending it does not reopen a founder decision; §4 supplies the precedence the selection omitted. Recommending a different structure would be a scope change requiring the founder, which is not mine to make.
4. **D's residual cost is bounded and honest.** Two known limits (tuple mismatch admits a duplicate; tuple equality can raise a false conflict) are stated in §7 and shown to the athlete in words, rather than engineered away with an invented threshold.

**Options B and C are not rejected; they are demoted from *policies* to *layers*.** That is the whole substance of the recommendation: the earlier comparison presented B and C as alternatives, which invited the question "which one?", when the correct answer is "B without C is unusable and C without B never fires".

### 5. Authoritative precedence table

For one submission from an authenticated owner, exactly one outcome applies. The first matching rule wins. This is the rule set TK15 implements; it is not a description of what a reasonable implementation might do.

| # | Precondition | Outcome | Effect on persisted state |
| --- | --- | --- | --- |
| P1 | SHA-256 equals an **accepted** original owned by this owner | `duplicate_of_existing`, referencing the existing original | **No** new `SourceObject`, **no** new `Activity`, and **no new `Import` row**. The `Import` row already existing for that `(owner, source_digest, contract_version)` *is* the record of this digest; the reference is reported on the per-file outcome and is derivable from the digest. Idempotent. **Wording corrected 3 October 2026 — see §13; the previous text required an `Import` row that the unique constraint makes impossible.** |
| P2 | SHA-256 equals a **quarantined** original owned by this owner | `duplicate_of_quarantined` | No new original; the candidate stays quarantined. A retry cannot flip a quarantine into acceptance. |
| P3 | Bytes differ; tuple equals that of an **accepted** activity of this owner | `quarantined_conflict` | New valid original + normalised candidate retained in quarantined owner scope (`implementation-contracts.md:62`). **Excluded from normal history and from every snapshot** (D01:48). |
| P4 | Bytes differ; tuple equals that of an **already quarantined** candidate of this owner | `quarantined_conflict`, linked to the existing candidate | A second candidate is **not** created for the same tuple. Prevents unbounded candidate fan-out from repeated re-exports. |
| P5 | Bytes differ; tuple differs | `accepted`, **if and only if** every other conformance and eligibility check passes | New original + activity. No deduplication claim is made and none is implied to the athlete. |
| P6 | Bytes equal a **previously rejected** submission | `rejected`, re-evaluated from scratch | D01:50 discards rejected raw bytes promptly, so no digest entry exists to match and P1 cannot apply. A rejection is not a history record. The same bytes may legitimately succeed later if the rejection was a resource limit. |
| P7 | Bytes equal an existing original that has since been superseded or deleted | Outcome text reports the referenced original as **unavailable** | Nothing is resurrected; D04's evidence-unavailable semantics apply. |

Two consequences worth stating because Worker will otherwise have to choose:

- **P3 fires against an accepted activity even after a "retain both" resolution.** See OQ-1.
- **P5 is where the false negative lives.** A re-export that changes `sport`, `start_time` or `total_elapsed_time` in any component produces a different tuple and is accepted as a separate activity. This is not a defect to be fixed inside this policy; it is the stated limit of an exact heuristic.

### 6. Canonical comparison values

The tuple is compared on **canonical normalized integers**, never on display strings, floats or raw file fields. This binds TK14 to the TK10 matrix (`fit-support-matrix.md`, 2 October section) and satisfies D02's canonical-fixed-precision rule at `p0-decision-baseline-2026-10-01.md:60`.

| Tuple component | Canonical value used for comparison | Basis |
| --- | --- | --- |
| `owner` | Server-derived authenticated owner id. Never client-supplied. | `implementation-contracts.md:7`; CUS10, SR20 |
| `sport` | The required normalised enum integer (approved set `{1 running, 2 cycling}`) | Profile `session` 18/5; D01 scope |
| `UTC start instant` | Exact integer seconds since the Unix epoch, `raw + 631065600` | MAP04 (`util.py` UTC offset 631065600) |
| `elapsed duration` | Exact integer **milliseconds**, equal to the raw `session` 18/7 value (scale 1000, unit s) | Profile `session` 18/7; exact integer arithmetic, no float |

Because elapsed duration is compared in integer milliseconds and start time in integer seconds, **equality is exact and no tolerance, epsilon or fuzzy comparison exists anywhere in the path.** A worker looking for a threshold to configure will not find one, and must not add one.

`sub_sport` is deliberately **not** a tuple component. A re-export that changed only the sub-sport classification therefore still conflicts, which is the conservative direction.

### 7. Hard prohibitions as testable invariants

These are not cautions. Each is a property of the state machine or a testable assertion; "we were careful" is not a passing state.

| Prohibition | Enforcement form |
| --- | --- |
| Never silently merge | **Merge is not an outcome of the state machine at all.** No transition combines fields from two distinct originals. This is stronger than a prohibition and is preferred, because a prohibition can still be violated by a new transition. |
| Never tolerance / fuzzy matching | Tuple comparison is integer equality on the §6 values. There is no configurable threshold parameter anywhere in the intake contract, so there is nothing to set incorrectly. |
| Never overwrite | Originals are immutable. Supersession is an append-only lineage record; the superseded original and its normalised records are retained, never mutated. |
| Never partial acceptance | A file contributes no partial accepted activity. Any decode, integrity, limit or required-field failure rejects the whole file. |
| No cross-owner disclosure | P1 is owner-scoped. An identical digest belonging to another owner is **not** a duplicate and must produce no hit, no count, no timing signal and no distinct error. |

### 8. Concurrency, staging and lost responses

STK011's recorded open items, decided here so that TK15 does not invent them.

1. **Idempotence under concurrency is enforced by a database unique constraint** over `(owner_id, sha256)` on non-rejected originals, not by application read-then-write. Application-level checking is not sufficient; two concurrent identical submissions must not both insert. This is a routine derived engineering detail within selected scope, not a new product decision.
2. **Conflict detection happens inside the same transaction that would insert the `Activity`.** Two concurrent differing-byte submissions with an equal tuple must not both reach an accepted state; one accepts and the other quarantines, deterministically.
3. **Uncertain commit is resolved by lookup, not by retry.** After any lost response or ambiguous outcome, the intake path re-queries `(owner_id, sha256)` and reports P1/P2/P3 rather than resubmitting.
4. **File store and database are not one transaction.** A durable staging marker plus owner-scoped reconciliation follows `implementation-contracts.md:61`. While a submission is unreconciled it is not visible in normal history and cannot be counted.
5. **Only an authenticated, authorized owner action may change conflict state** (keep existing / replace / retain both). Interruption mid-resolution must leave a recoverable state, never a silently lost resolution.
6. **Supersession is append-only and lineage-preserving.** Any snapshot that previously included the superseded activity retains its historical reference; nothing rewrites history.

### 9. How a conflict is presented to the athlete

This answers SR33, UI-SR02 and the presentation half of TC22. It states the required information and the required and prohibited wording; it does not specify layout, component structure or test steps, which remain with UI Designer and User Tester.

**Three distinct textual states, never merged into one visual treatment:**

| State | Where it appears | Required content |
| --- | --- | --- |
| `activity` | The history list | The activity as normally presented |
| `duplicate_of_existing` | **Attached to the existing activity**, never as its own activity-shaped row | That another submission referenced this same original, when it was submitted, the submitted file name, and a link to the activity it references. It must not increment any count, total, or date scope. |
| `quarantined_conflict` | A **separate conflicts area**, never inside the activity list | That an unresolved candidate exists; both affected records identified; that it *may* be the same activity; the three resolution options offered; and that it is excluded from volume until resolved |

**Required wording rules:**

1. The conflict text must say the candidate **may** be the same activity. The tuple is a heuristic (`p0-decision-baseline-2026-10-01.md:48`), and asserting identity would be a claim the system cannot support.
2. State the resolution options by their effect: keep the existing activity, replace it with an auditable supersession, or keep both. Each must state what happens to the other original.
3. A quarantined candidate must never be counted, totalled, or included in a date scope anywhere in the product.
4. The duplicate reference must read as a reference to an existing activity, not as an additional activity.

**Prohibited wording** (these imply a merge, an overwrite, or a certainty the system does not have): "merged", "replaced automatically", "overwritten", "duplicate activity", "double counted", or any phrasing that states the two files are certainly the same session.

**Accessibility:** the three states must be distinguishable by text alone, never by colour or icon alone, and must be keyboard reachable — consistent with the selected WCAG 2.2 AA target at `p0-decision-baseline-2026-10-01.md:104` and TC21/TC22's "not by colour or icon alone".

**Privacy:** the presentation must never reveal whether another owner holds the same bytes, nor anything about another owner's conflicts. Identical wording and timing apply whether or not a foreign duplicate exists.

### 10. Disposition vocabulary, and a required change I cannot make

The per-file outcomes in §5 are **`accepted`, `rejected`, `duplicate_of_existing`, `duplicate_of_quarantined`, `quarantined_conflict`** — five states. Two record-level gaps follow, and I am not permitted to edit the registry:

1. **`SR32` currently admits only two outcomes.** Its text reads "present its accepted or rejected disposition". A duplicate reference and a quarantine are neither accepted nor rejected, and collapsing them into one of those two words would be actively misleading — exactly what `p0-ui-requirements-review.md:21` forbids ("never imply unsupported files were imported"). **Required change to SR32**: admit the duplicate-reference and quarantine dispositions explicitly. Registry edit is not mine.
2. **`SR33` covers the history view but not the per-file upload outcome.** A conflict discovered during upload needs its own SR or an extension of SR32 so that TK11 (per-file diagnostics) and TK15 (history) are covered by the same vocabulary.

Both are proposals for the Primary Coordinator to route through the synchronized registry process. Until then, this section is the architecture's proposed vocabulary and the SR text and the implementation will disagree.

### 11. Open items and the residual costs I am accepting

| ID | Open item | Owner |
| --- | --- | --- |
| OQ-1 | Should a "retain both" resolution suppress future quarantines for that tuple? **Recommendation: no.** Suppression converts one visible decision into a permanent blind spot, and the athlete never chose it. Cost of the recommendation: a repeated explicit decision per newly exported variant. | Product decision — founder via Primary Coordinator |
| OQ-2 | False-positive frequency. A tuple collision requires two genuinely different activities of the same owner and sport sharing an exact UTC start second and an exact elapsed millisecond. Device clock reset/rollback is the plausible mechanism. **This repository holds no frequency evidence, and none is claimed.** The founder's decode spike is the natural place to observe whether it occurs in real data. | Observed evidence — pending spike |
| OQ-3 | Byte-stability of a Garmin Connect re-export. Option A's residual double counting depends entirely on this, and it is unmeasured. | Observed evidence — pending spike |
| OQ-4 | Deletion, quarantine retention and backup interaction with supersession lineage remain **unselected** (`decision-register.md:66`). This section assigns no retention period. | TK17 / D04 — open |
| OQ-5 | `Metric` schema does not exist (`decision-register.md:64`). Any metric persisted before that contract is provisional. | D02 / WP02 — open |

**Binding architectural condition, restated.** The quarantined original and its normalised candidate are a **disposition state on the source chain**, not a finding and not an assessment (`decision-register.md:60`). No entity created by this policy may store the outcome of executing a skill against a model, under any name, and no mutable latest-result pointer may exist on any of them. That is why §5's outcomes are states of `Import` and `SourceObject`, not new analytical records.

### 12. Trace and evidence boundary

TK14/STK011/STK012, CUS02, FEAT02, SR04, SR33, D01, TC03, TC22; downstream TK15, TK16. Every option and precedence rule above is **proposed architecture**, not an observed result. All examples remain conceptual and are not telemetry, fixtures or test oracles. No conflict fixture exists in this repository; `fit-source-inventory.md:36` records that lawful fixtures are still an open gate. `TC03` and `TC22` are Not run. Nothing here is Done, Verified, Accepted or released.

---

## 3 October 2026 increment — P1 conformance defect, and the closure of §10

Status: **two decisions that close an unimplementable contract and an expressible requirement gap** (System Architect — Feng Guo). Sections 1–12 above are preserved unchanged as historical evidence; only the P1 row of §5 is corrected in place, because that cell was the defect, and its line number was not cited anywhere (only lines 37 and 48 are cited externally). Nothing here is a test result, a verified requirement, an acceptance or a release. `TC03`, `TC21`, `TC22` remain **Not run / unverified**.

### 13. P1 could not be implemented, and the defect is in the contract wording, not the schema

**The verified defect, in three parts.** Precedence rule P1 (§5, as originally worded) required that "a new `Import` row records the attempt and the reference". The implementation cannot do this, and could not be made to:

1. **The implementation returns without creating a row.** `datara/dedup.py:756-777`: when the digest is already claimed, `ingest` returns a `DispositionOutcome` immediately. No `Import` is created on that path. The `Import` row is only created on the accepting path, via `_create_import` at `datara/dedup.py:844`, reached from `_p5_accept` at `:892`.
2. **A second row is impossible, not merely skipped.** `datara/models.py:216-219` declares `UniqueConstraint(fields=["owner", "source_digest", "contract_version"], name="datara_import_owner_digest_contract_uniq")`. One `Import` row per `(owner, digest, contract)` is a database invariant, not a convention.
3. **There is no column for "the reference" either.** The `Import` model (`datara/models.py:176-221`) holds `source_digest`, `status`, `reason_code`, `reason_detail`, `warnings`, provenance fields and an owner — and **no foreign key to any `SourceObject`, `Activity` or `Quarantine`**. So even a nullable reference column would have had nowhere to point under the current constraint.

**So: is one `Import` per digest the intent, or is the constraint wrong?** The decision is **one `Import` row per `(owner, source_digest, contract_version)` is the intent. P1's wording was wrong. No schema change is required, and the constraint must not be relaxed.**

Four pieces of evidence fix the intent, and three of them are internal to this document:

- **P1 itself says "Idempotent."** A per-submission `Import` row is a state change on every resubmission, so under that reading "idempotent" would be false. The word only means what it means under one row per digest.
- **P6 depends on it.** P6 (§5) says that bytes matching a previously *rejected* submission have "no digest entry", so P1 cannot apply — which is exactly why the same bytes may legitimately succeed later. Under a per-attempt-row reading, a rejected attempt *would* leave an `Import` row carrying that digest, P1 would match it, and **P6 would be unreachable**. P6 is only coherent if a rejected attempt leaves no retained `Import` row.
- **The unique constraint matches the one-row reading exactly**, and it is already the shipped schema.
- **The `Import` docstring is the only artefact that disagrees**, and it disagrees ambiguously: "One occurrence of submitted bytes" (`datara/models.py:177`) can be read as one row per *byte string* or one per *upload event*. Under the decision it means the former.

**The exact change required, which is documentation and contract wording only — zero migration, zero schema change, zero data change:**

| # | File and line | Change |
| --- | --- | --- |
| 1 | `docs/management/source-evidence/duplicate-conflict-options.md:110` (P1 row) | **Applied** in this increment: "A new `Import` row records the attempt and the reference" replaced with the corrected effect cell quoted above. |
| 2 | `datara/models.py:176-177` (`Import` docstring) | For the code owner: replace "One occurrence of submitted bytes" with wording that states the invariant — one row per `(owner, source_digest, contract_version)`, recording that digest's terminal state, **not** one row per submission attempt. |
| 3 | `datara/models.py:184-191` (`STATUS_CHOICES`) | For the code owner and the Coordinator: no change to the three statuses, but the relationship must be documented so Worker does not try to store a duplicate disposition here. See below. |
| 4 | A test asserting the invariant | For the code owner: a test that a second submission of identical bytes creates **no** second `Import` row and raises no `IntegrityError`, and that the per-file outcome is `duplicate_of_existing`. |

**Two vocabularies, and they must not be conflated.** The **five per-file dispositions** of §5 are submission-time *outcomes*, returned to the athlete and required by `SR32`. The **three `Import` statuses** (`accepted`, `rejected`, `conflict`) are the *persisted terminal state of a digest*. A duplicate is an outcome, not a status: under this decision a duplicate submission leaves the existing row's status untouched at `accepted`. `duplicate_of_existing`, `duplicate_of_quarantined` and `quarantined_conflict` are therefore **not** persistable in `Import.status` and must not be forced into it. The reference the athlete is shown is carried on the outcome object, which already has the fields for it — `DispositionOutcome` carries the activity and quarantine references, and `describe_reference(owner, digest)` at `datara/dedup.py:1213` exists precisely to render the human-readable reference.

**Why the reference needs no column.** Under one row per digest, the reference is *derivable from the row itself*: the row names the digest, the digest identifies the `SourceObject`, and the published `Activity` is the one with that `source_object`. Adding a nullable reference column would store a second, redundant copy of a relationship that is already exact, and would need a new migration to maintain.

**What the rejected branch would have cost, stated so the choice is visible.** Relaxing the constraint to `(owner, source_digest, contract_version, submitted_at)` and adding a nullable `duplicate_of` self-reference would make P1's original sentence literally true, at the price of: breaking the idempotence P1 asserts; making P6 unreachable, because every rejected attempt would leave a matching digest row; and turning a per-submission audit trail into a *side effect* of a duplicate check. **If the founder later wants a per-submission audit trail, that is a new entity — a `SubmissionAttempt` — not a relaxation of this constraint.** This section does not decide that question and does not need to; nothing in Milestone A's authorised scope or in `SR32` requires a stored per-submission record, because `SR32` is satisfied by the presentation of the disposition at submission time.

**Consequence for TK15.** With P1 corrected, the implementation and the contract agree, and **TK15 can claim P1 conformance for the duplicate path** once the invariant test in change 4 exists. It cannot claim it today, and nothing in this section should be read as evidence that it does.

### 14. §10 is closed at the architecture level; the registry edit is not mine

§10 recorded that `SR32` admits only two dispositions and that the registry edit is not mine. That remains true of the registry, and it is now **decided** at the architecture level, with exact text routed for registry synchronization:

- **Corrected `SR32` statement and acceptance criteria**: in [`decision-proposals.md`](../../p0-design/decision-proposals.md), "Routed requirement changes — 3 October 2026", covering all **five** dispositions.
- **The `SR32`/`SR33` relationship** is fixed there too: `SR32` is per submission and obligatory for every file; `SR33` is the history view and applies only to what persists. `rejected` produces no `SR33` history row at all, which is what D01's prompt-discard of rejected raw bytes already implies.

The proposed text changes `docs/management/system-requirements.md:49-50`, `docs/management/p0-breakdown.md:311-312` and the `SR32`/`SR33` entries of `docs/management/requirements-registry.json` (`system_requirements[31]` and `[32]`). **All four are the registry owner's change and need review; this section edits none of them.** Until that synchronization lands, `SR32`'s text and the implementation still disagree, and `TC21` cannot pass.

### 15. Trace and evidence boundary

TK14 (#120), TK15 (#121), STK011 (#183), STK012 (#184); #329, #330, #316. WP01, WP02, CUS01, CUS02, FEAT01, FEAT02, SR04, SR32, SR33, D01. TC03, TC21, TC22 — all **Not run / unverified**. Claims about `datara/dedup.py`, `datara/models.py` and `datara/normalization.py` are **verified by reading the merged source at `8acccbf`**; §13's recommendation is architecture, not an observed conformance result. No conflict fixture exists (`fit-source-inventory.md:36`). Nothing here is Done, Verified, Accepted or released.
