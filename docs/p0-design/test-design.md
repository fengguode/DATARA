# P0 comprehensive test design

Status: proposal only; no product validation has run. Existing test definitions and IDs remain in the [validation plan](../management/validation-plan.md), and the complete prospective oracles/fixtures/gates are in [test-design-findings.md](test-design-findings.md). Do not change canonical case statuses from `Not run` based on these documents.

**Addition, 2 October 2026:** the *Milestone A acceptance suite* below was authored for [TK12 #118](https://github.com/fengguode/DATARA/issues/118) from the twelve acceptance cases in [#305](https://github.com/fengguode/DATARA/issues/305). It is a **pre-implementation specification**: the code it tests does not exist. Nothing in it is a result.

## Scope and test levels

Designed coverage spans unit/deterministic transforms, component/schema contracts, disposable-database integration, mocked adapter integration, fixed-candidate system checks, actual rendered browser acceptance, live-model integration, and separate athlete/founder validation. Evidence at one level cannot substitute for another. Each case records its environment, fixture provenance/hash, commit, versions, command, observable result and sanitized evidence reference.

## Canonical cases

| IDs | Coverage | Applies to |
|---|---|---|
| TC01–TC05 | FIT acceptance, original preservation, duplicates/conflicts, reproducible preparation, scoped/provenance-bound skill inputs | WP01–WP03; CUS01–03, SR01–07/SR27–28 |
| TC06–TC07 | versioned skill quality/contract, deterministic ineligibility | WP03; CUS04–05, SR08–11/SR29 |
| TC08–TC10 | explicit selected connection, secret protection, run state and failures | WP04; CUS06–07/SR12–15/SR30 |
| TC11–TC14 | append-only lineage, dashboard saved reads, API contract, cross-user isolation | WP05; CUS08–10/SR16–21/SR31 |
| TC15 | full P0 user journey and separate final athlete validation | WP06; CUS01–10 |
| TC19–TC20 | official source evidence and cross-contract conformance | WP01–WP05; CUS01, CUS03–06, CUS09/SR27–31 |

TC16–TC18 cover P1 recommendations, routines and comparisons; they are out of this design baseline. Retain their planning records, but do not use them as P0 acceptance cases.

## Additional candidate coverage

The traceability audit identifies recovery, deletion, backup/restore, operations, migration/rollback, and expanded accessibility tests needed before final system acceptance. These should receive canonical SR and TC identifiers after the registry merge markers are reconciled. Until then they are gap candidates, not silently added verification cases. No candidate is run or passed.

---
---

# Milestone A acceptance suite — pre-implementation verification design

**Author:** User Tester — Abt Hermann_space-bunny-free-max_OpenCode (AI agent)
**Assignment:** TK12 [#118](https://github.com/fengguode/DATARA/issues/118), first Milestone A bounded assignment [#305](https://github.com/fengguode/DATARA/issues/305)
**Scope:** WP06 design work for WP02's TK11/TK15/TK18. CUS01, CUS02, CUS03, CUS10; SR01–SR06, SR20, SR27, SR32, SR33; D01.
**Status:** design only. **Zero product code exists.** Every case below is `NOT RUN`. No case is Done, Verified, Accepted or released, and nothing here changes a registry status.

## 1. Why this document, and what it is not

The purpose is to freeze the *oracles* before the Worker writes the implementation, so that TK12 verifies TK11/TK15/TK18 against a specification that already existed rather than one reverse-engineered from the delivered code.

This document is:

- a set of **preconditions, stimuli, expected observables, oracles and discrimination proofs**;
- a statement of what is **not yet decidable** and why;
- a list of **required changes in files this role does not own**.

This document is **not**: a test result, a conformance claim, a fixture I am permitted to commit today, an approved reason-code list, a schema, or a selection among the open decisions. Where a value is not approved, I name a **test-side alias** and mark the contract input as required. I do not invent normative values.

## 2. Sequencing: what cannot be verified yet

| Chain | State | Consequence for TK12 |
|---|---|---|
| TK09 (#115) rights/provenance | rights unresolved | No fixture binary may be committed; see §5 |
| TK10 (#116) FIT support/mapping matrix | proposed, blockers open | Reason-code strings, valid ranges and sport/subsport allowlist are **not frozen** |
| TK11 (#117) classification and diagnostics | not started | **MA-01…MA-07 cannot be executed** |
| TK14 (#120) duplicate/conflict policy | not started | **MA-03 conflict policy oracle is not fixed** |
| TK15 (#121) originals and duplicate-safe history | not started | **MA-02, MA-03 cannot be executed** |
| TK18 (#124) deterministic normalization | not started | **MA-08 cannot be executed** |
| D04/D05 UI + runtime | selected, no target | MA-12 and the TC21 rendered portion are **BLOCKED** |

`TK12 depends on TK11, which depends on TK10, which is not delivered.` I therefore **cannot verify anything in Milestone A today**, and I do not report any partial verification. What I can deliver is this specification, which is exactly the part that does not depend on the code.

## 3. Test-level labels used below

Every case carries one of these. They are not interchangeable and one never evidences another.

| Label | Meaning | Milestone A examples |
|---|---|---|
| `UNIT` | deterministic transform in-process, no persistence | elapsed/timer separation; sentinel → null+warning; reason-code stability |
| `CONTRACT` | schema/fixture-manifest agreement, no live service | reason-code family distinctness; snapshot digest projection |
| `INTEGRATION` | disposable PostgreSQL, real Django code, real byte storage | idempotence, quarantine, original round-trip, eligibility call count |
| `SYSTEM` | fixed candidate run end-to-end from a clean checkout | MA-12 pinned-command reproducibility |
| `RENDERED-UI` | actual rendered browser against an isolated target | TC21 rendered portion — **BLOCKED**, no target |
| `MOCKED` | provider transport faked | *not used in Milestone A*; no provider is in scope |
| `LIVE-MODEL` | real customer-owned provider call | *not authorized, not used*. This is TC08, a separate release gate |
| `ATHLETE-VALIDATION` | founder/athlete task completion | *not applicable in Milestone A*; this is TC15 |

**Inspection** is additionally used where the evidence is a document or schema read, and is always labelled as inspection, never as a passing test.

## 4. Result vocabulary

Every case yields exactly one of:

`PASS` · `FAIL (defect + severity)` · `BLOCKED (named blocker)` · `NOT RUN (not yet attempted)`

There is no "N/A", no blank, and **no case may be credited as passing because it produced no output**. A case whose oracle was never shown to be capable of failing is recorded as `NOT RUN — oracle discrimination unproven`, regardless of the green output around it.

## 5. Fixtures and the fixture supply chain

### 5.1 Hard prohibitions

- **Never** read, copy, hash, stat, enumerate or `dir` the founder's personal telemetry at `demo_file/24563001348_ACTIVITY.fit`. It is private, excluded by `.gitignore` (`*.fit`, `*.FIT`, `/demo_file/`), and must never enter this repository, a log, an evidence bundle or an API response.
- **Never** copy an upstream SDK sample binary. FIX02–FIX04 in [fixture-provenance.md](../management/source-evidence/fixture-provenance.md) carry unresolved redistribution rights; Explorer — Wang Licun is resolving them in parallel. An unresolved right is not a permission.
- Personal FIT files carry device serials, GPS traces, physiological values and exact timestamps. Any evidence bundle derived from one is personal data.

### 5.2 A blocking finding on fixture supply

`.gitignore` currently blocks `*.fit` **and** DATARA's own future synthetic fixtures. Its own comment states this is deliberate and that "when a fixture is cleared, this rule must be narrowed in the same change that adds the fixture, with the rights decision cited, rather than worked around with `git add -f`."

So even after rights are cleared, committing a binary fixture requires a coordinated `.gitignore` change this role does not own. **This is a required change (§13.2), not a workaround.**

### 5.3 Recommended approach: generate fixtures, do not commit them

**Recommendation to the Explorer and the Architect:** keep fixture *binaries* out of Git entirely. Commit instead (a) a deterministic fixture **generator** and (b) an **expected-value manifest** stated independently of the generator, then materialize binaries at test time into a disposable directory.

Why this is better than committing binaries:

1. it sidesteps `.gitignore` and the redistribution question completely, because no third-party artifact is copied;
2. it forces the separation [fixture-provenance.md:19](../management/source-evidence/fixture-provenance.md) already demands — "a generator and decoder sharing the same erroneous mapping cannot be the sole oracle";
3. it makes the generator's own determinism a testable property rather than an assumption.

Generator properties that must themselves be tested (`FXGEN`):

| ID | Check | Oracle |
|---|---|---|
| FXGEN-1 | generate each fixture twice in the same process | identical SHA-256 |
| FXGEN-2 | generate under `PYTHONHASHSEED=0` and `=1` | identical SHA-256 |
| FXGEN-3 | generate with `TZ=UTC` and `TZ=Asia/Shanghai` | identical SHA-256 |
| FXGEN-4 | generate on two platforms (host + pinned container) | identical SHA-256, or a recorded BLOCKED with the divergence named |
| FXGEN-5 | generated file passes the pinned decoder's integrity check | file CRC valid; a mutated copy does not |

FXGEN-4 is likely to be `BLOCKED` in this environment and must be reported as such, not assumed.

### 5.4 Fixture manifest — required entries

Each row must carry, per the existing manifest requirements: artifact id, generator version, creation date, source/profile identity, rights decision reference, intended supported/unsupported variant, **expected disposition**, **expected reason-code alias**, explicit expected normalized values with raw-integer provenance, and the independent expected-value reviewer.

The *expected normalized values* are stated as **exact decimals derived from raw integers by `raw/scale − offset`**, never as the SDK's already-transformed float. Using the decoder's output as the oracle is circular and is rejected here (§9, trap 2).

| Key | Intent | Expected disposition | Expected reason alias | Notes |
|---|---|---|---|---|
| `FX-OK-OUTDOOR-FULL` | single-session running, outdoor, all optionals present | accepted | — | baseline positive |
| `FX-OK-INDOOR-NOGPS` | indoor, **no position records**, no distance | accepted | — | missing GPS is **valid**, not an error |
| `FX-OK-ELAPSED-NE-TIMER` | elapsed 1800 s, timer 1742 s (58 s auto-pause gap) | accepted | — | the interchange detector, §8.2 |
| `FX-OK-TIMER-ABSENT` | elapsed present, `total_timer_time` absent/invalid | accepted | — | timer must be `null`, never back-filled from elapsed |
| `FX-REJ-TYPE` | not a FIT byte stream | rejected | `RC.TYPE_UNSUPPORTED` | |
| `FX-REJ-SPORT` | supported shape, unsupported sport enum | rejected | `RC.SPORT_UNSUPPORTED` | reason must **name the limitation** |
| `FX-REJ-CHAINED` | two FIT files concatenated | rejected | `RC.LAYOUT_CHAINED` | whole file, not the first segment |
| `FX-REJ-MULTISPORT` | `auto_multi_sport`, 2 sessions | rejected | `RC.LAYOUT_MULTISPORT` | distinct from chained |
| `FX-REJ-REQUIRED-ELAPSED` | `total_elapsed_time` = `0xFFFFFFFF` invalid sentinel | rejected | `RC.REQUIRED_INVALID` | whole-file |
| `FX-REJ-REQUIRED-START` | `start_time` absent | rejected | `RC.REQUIRED_MISSING` | |
| `FX-REJ-CRC` | one byte flipped after the header | rejected | `RC.INTEGRITY_CRC` | **never silently repaired** |
| `FX-REJ-HEADER` | header size / `.FIT` marker wrong | rejected | `RC.INTEGRITY_HEADER` | |
| `FX-REJ-UNKNOWN-REQUIRED` | required meaning depends on a native-override/developer field | rejected | `RC.SEMANTICS_UNVERIFIED` | D01 forbids this acceptance |
| `FX-OK-UNKNOWN-DEVELOPER` | unknown developer fields, structure independently verified | accepted + warning listing ignored fields | — | D01 permits ignore *and* reporting |
| `FX-COMPRESSED-TS` | compressed timestamp headers | see §10 | `RC.TIMESTAMP_COMPRESSED` | currently **rejection only** |
| `FX-DUP-SAME-BYTES` | byte-identical copy of `FX-OK-OUTDOOR-FULL` | accepted, idempotent reference | — | hash recorded |
| `FX-CONFLICT-A` / `-B` | **same** `(owner, sport, UTC start, elapsed)`; bytes differ **only in fields outside that tuple** | A accepted; B quarantined | `RC.CONFLICT_LOGICAL` | fixture-construction rule in §8.3 |
| `FX-NEAR-A` / `-B` | identical except elapsed differs by **1 second** | **both accepted**, no conflict | — | the no-tolerance discriminator |
| `FX-BATCH-MIX` | 5-file batch: 2 accepted, 2 rejected, 1 conflict | per-file outcomes | — | one rejection must not undo accepted siblings |
| `FX-LIMIT-*` | exactly-at and one-over for 16 MiB, 200 000 messages, 100 000 samples, 60 s, 512 MiB | at → accepted; over → rejected | `RC.LIMIT_*` | exactly-at/one-over is explicitly required by D01 |
| `FX-SNAPSHOT-CONFLICT` | owner A's accepted activity **plus** A's quarantined candidate | snapshot digest unchanged vs. without the candidate | — | cross-check of MA-03 × MA-08 |
| `FX-OWNER-A` / `FX-OWNER-B` | two disposable synthetic identities | — | — | D05 requires ≥ 2 identities |

**`FX-CONFLICT-A`/`-B` construction rule (normative for the generator):** the two files must differ **only** in fields that are *not* part of the logical tuple `(owner, sport, UTC start, elapsed duration)` — for example `manufacturer`, `serial_number`, `product`, or `total_distance`. If they differ in `sport`, `start_time` or `total_elapsed_time`, they are **not** a conflict fixture and the case is void. This is the single most common way a conflict test silently stops testing a conflict.

## 6. Required frozen inputs before any case can run

| ID | Required input | Owner | If absent |
|---|---|---|---|
| RI-1 | Approved sport/subsport allowlist and unknown-value handling | Architect, TK10 | MA-05 `BLOCKED` |
| RI-2 | Approved valid ranges, sentinel handling and required-relation rules | Architect, TK10 | MA-04 `BLOCKED` |
| RI-3 | Frozen stable reason-code enumeration; test aliases `RC.*` mapped to approved codes | Architect, TK10/TK11 | MA-04…MA-07 `BLOCKED` |
| RI-4 | Conflict policy option selected (exact-byte / documented-tolerance / none) | Architect, TK14 → D01 | MA-03 `BLOCKED` |
| RI-5 | Digest input projection: the exact declared set of fields a snapshot digest covers | Architect / Worker contract | MA-08 `BLOCKED` |
| RI-6 | Declared exclusion allowlist for generated identifiers and processing timestamps | Architect / Worker contract | MA-08 `BLOCKED` |
| RI-7 | Retention decision for rejected raw bytes | D01/D05 | MA-07 partial `BLOCKED` |
| RI-8 | Compressed-timestamp disposition (extend scope / substitute engine / reduce scope) | Founder, via #297 | §10 |
| RI-9 | Fixture rights decision and a lawful generator | Explorer, TK09 | all fixture cases `BLOCKED` |
| RI-10 | Supported browser/viewport/AT matrix and a runnable target | Designer + D04/D05 | TC21 rendered `BLOCKED` |

## 7. Evidence preconditions: the pinned command and environment identity

Constraint 5 of the assignment: evidence not reproducible from the pinned command's printed identity is not evidence.

**MA-12 requires** that `scripts/milestone_a.sh` (Worker-owned per #305) prints, **before any test result line**, a block of this shape:

```
DATARA-ENV
commit=<40-hex>
python=<implementation> <version>
django=<version>
postgres=<server_version()>
lock_sha256=<64-hex of the pinned dependency lock file>
fixture_manifest_sha256=<64-hex>
```

Pass oracle for MA-12, all four parts required:

1. **Ordering.** The block appears before the first result line in the captured output. Any result line preceding it is a defect.
2. **Agreement.** Each printed value equals a value queried **independently** of the script: `git rev-parse HEAD`, `python -VV`, `pip show django`, `psql -c 'SHOW server_version'`, `sha256sum <lock>`. The script's own output is never its own oracle.
3. **Sensitivity.** Re-running with a deliberately altered lock file changes `lock_sha256`. A hardcoded `echo` block fails this.
4. **Clean-checkout reproduction.** The run happens in a fresh `git clone` of the candidate SHA, not in a working tree with uncommitted files, and the reproduced identity matches the recorded identity exactly.

Discrimination proof for MA-12: mutant **M-12.1** (print a hardcoded block) must produce FAIL via parts 2 and 3. Mutant **M-12.2** (print the block after the results) must produce FAIL via part 1. Until both are demonstrated, MA-12 is `NOT RUN — oracle discrimination unproven`.

**Environment limitation, recorded honestly:** D05 selected Django/Python/PostgreSQL running locally in China and notes the supplied development environment is Windows with no assumed compatible runtime. I have **no preflighted Linux/container target and no PostgreSQL in this environment**, so the MA-12 preflight is itself `BLOCKED` here. What preflight would be required is listed in §12.

## 8. The twelve acceptance cases

Each case states precondition, stimulus, expected observable, oracle, discrimination proof and level. `TC` is the registry verification-case mapping where one exists.

### MA-01 — Synthetic valid file, single activity → accepted, original stored, SHA-256 recorded, four required inputs normalised

- **Trace:** TC01; SR01, SR02, SR27, SR03. **Level:** `UNIT` + `INTEGRATION`.
- **Precondition:** fresh disposable database at the candidate commit; `OWNER-A` exists; environment block printed and matching (§7); `FX-OK-OUTDOOR-FULL` materialized with its manifest SHA-256.
- **Stimulus:** submit `FX-OK-OUTDOOR-FULL` once as `OWNER-A` through the supported upload path.
- **Expected observable:** disposition `accepted`; exactly one `Import` row and one `SourceObject` row for `OWNER-A`; the stored original's independently re-computed SHA-256 equals the submitted digest; exactly one `Activity` and one `Session`; the four required normalised inputs present and exactly equal to the manifest values: source reference/digest, sport, session UTC start instant, elapsed duration.
- **Oracle:** four conjuncts, each a hard equality:
  1. `sha256(fetch_original_bytes_by_id(id)) == manifest.digest` — computed by the test with `hashlib`, **not** by calling the product's digest function (trap 1);
  2. `activity.sport == manifest.sport and activity.start_utc == manifest.start_utc and activity.elapsed_s == manifest.elapsed_s`, compared as exact `Decimal`, not float;
  3. row counts exactly `(1, 1, 1, 1)` for `(Import, SourceObject, Activity, Session)`;
  4. zero rows in any quarantine/conflict table.
- **Discrimination proof:** **M-01.1** store a re-serialized/decoded copy instead of the original bytes → conjunct 1 FAIL (this is the "we saved the decoded data, not the file" defect). **M-01.2** use the SDK's transformed float and the manifest's exact decimal differ by one ULP → conjunct 2 FAIL. **M-01.3** create the `Activity` inside a transaction that also writes a second `Import` → conjunct 3 FAIL. **M-01.4** an implementation that accepts and also quarantines → conjunct 4 FAIL. All four must be demonstrated failing before MA-01 is credited.
- **Not decidable now:** the exact expected values in RI-1/RI-2. Blocked until TK10 lands.

### MA-02 — Same owner, identical bytes, re-uploaded → idempotent, references existing history, no second original

- **Trace:** TC03; SR04, SR33. **Level:** `INTEGRATION`.
- **Precondition:** MA-01 has completed and passed. Full row counts and byte-store object count captured as the pre-state.
- **Stimulus:** submit the **same bytes**, same owner, as a **separate upload** (new request, new multipart body, possibly a different filename). Repeat once more for a third submission.
- **Expected observable:** the second and third submissions return references to the **same** `Import`, `SourceObject` and `Activity` identifiers returned by MA-01; no additional original byte object is stored; history shows one activity, not three.
- **Oracle:** byte-identical response bodies for submissions 2 and 3, and equality of their `activity_id`/`import_id`/`source_id` with submission 1's; `SELECT count(*)` unchanged for `Import`, `SourceObject`, `Activity`; stored-byte-object count unchanged; and **the same bytes re-submitted as `OWNER-B` must be accepted for B as a new activity** (see trap 6 — idempotence scoped to the owner, never global).
- **Discrimination proof:** **M-02.1** always create a new `Import` → count conjunct FAIL. **M-02.2** dedupe on the *logical tuple* instead of the digest → MA-02's own bytes pass, but the conflict fixture (MA-03) is then silently treated as a duplicate, so **MA-03 FAILs** — this proves the two cases discriminate different mutants rather than the same one twice. **M-02.3** a global unique constraint on `source_digest` → `OWNER-B`'s re-submission is rejected with a message implying an existing owner; both the "B accepted" conjunct and the non-disclosure conjunct of MA-10 FAIL. **M-02.4** dedupe on a whitespace-normalised digest → a one-byte mutation of an ignorable header byte is treated as duplicate; caught by MA-01's digest conjunct and by a dedicated mutation fixture.
- **Also required:** the idempotence check must be repeated **after a process restart** to catch same-process-only caching. An in-process cache that is not backed by persistence passes a same-process rerun and fails after restart.

### MA-03 — Different bytes, identical logical tuple → quarantined, excluded from normal history, no merge, no overwrite

- **Trace:** TC03 (+ TC22 rendered, separate unit); SR04, SR33. **Level:** `INTEGRATION`.
- **Gated on:** RI-4 (TK14 policy, D01 selection).
- **Precondition:** `FX-OK-OUTDOOR-FULL` accepted for `OWNER-A`. Capture: history activity count, weekly recorded-elapsed total, and the SHA-256 of the stored original as the pre-state.
- **Stimulus:** submit `FX-CONFLICT-B` for `OWNER-A`. Then submit `FX-NEAR-B` for `OWNER-A` (identical except elapsed differs by 1 second).
- **Expected observable:**
  1. `FX-CONFLICT-B` → quarantined; a conflict/quarantine record exists naming both digests; its normalised candidate is **not** in normal history;
  2. the pre-state history activity count and recorded-elapsed total are **numerically unchanged**;
  3. the stored original `A` still hashes to `A`'s digest (**no overwrite**), and B's bytes are separately retained for explicit resolution;
  4. both originals remain separately addressable by the owner;
  5. `FX-NEAR-B` → **accepted** as a second, distinct activity, with **no** conflict record.
- **Oracle:** numeric, not qualitative. Conjunct 2 is the decisive one: "excluded from history" is asserted by an unchanged count **and** an unchanged duration total, not by the absence of a UI label. Conjunct 5 is the no-tolerance oracle: exactly one conflict record exists after the second upload. Conjunct 3 is byte-level: `sha256(original_A) == manifest.digest_A` after B is quarantined.
- **Discrimination proof:** **M-03.1** silently merge B into A → conjuncts 2 and 3 FAIL. **M-03.2** overwrite A with B → conjunct 3 FAIL and `A`'s digest is destroyed. **M-03.3** apply a ±5 s or ±1 % tolerance window → `FX-NEAR-B` is quarantined, conjunct 5 FAIL. **M-03.4** include quarantined candidates in snapshots and history aggregates → conjunct 2 FAIL, **and** `FX-SNAPSHOT-CONFLICT`'s digest changes, so MA-08 also FAILs — a genuine cross-case discriminator. **M-03.5** quarantine without retaining B's bytes → conjunct 3 FAIL (resolution becomes impossible).
- **Open:** whether the quarantined candidate's normalised values are user-visible before resolution is a **D01 product decision** (keep existing / replace via auditable supersession / retain both). The test asserts *not in history* and *not in snapshots* unconditionally; it asserts the resolution affordance only once that decision is recorded. Asserting the presentation now would be inventing product behaviour.

### MA-04 — Missing a required field, e.g. no valid elapsed duration → whole file rejected with a stable reason code

- **Trace:** TC01; SR01, SR02. **Level:** `UNIT` + `CONTRACT`.
- **Stimulus:** `FX-REJ-REQUIRED-ELAPSED`, `FX-REJ-REQUIRED-START`.
- **Expected observable:** disposition `rejected`; reason code = the approved code for that cause; **no** `Activity`, `Session` or accepted `SourceObject` row; no partial normalised record survives; no quarantine row (a rejected file is not a conflict).
- **Oracle:** disposition equals the manifest's expected disposition **and** the reason code maps to the manifest's `RC.REQUIRED_INVALID` / `RC.REQUIRED_MISSING` alias; `count(Activity)==0 and count(Session)==0`; and the returned reason text contains **no** raw exception string, byte offset, hex dump or OS error message.
- **Discrimination proof:** **M-04.1** reject only the field, not the file, publishing a partial activity → row-count conjunct FAIL. **M-04.2** reason text = `str(exc)` → the text-content conjunct FAIL (and MA-07's stability conjunct FAIL, since equivalent inputs then produce different strings). **M-04.3** treat an invalid sentinel as zero and accept → disposition conjunct FAIL. **M-04.4** accept an absent required field as `null` → disposition FAIL.
- **Rule encoded (constraint 1):** required-missing/invalid → **whole-file rejection**; there is no path in which a required field becomes `null`.

### MA-05 — Unsupported sport → rejected with a stable explanation naming the limitation

- **Trace:** TC01, TC21 (text portion); SR01, SR02, SR27. **Level:** `UNIT` + `CONTRACT`.
- **Stimulus:** `FX-REJ-SPORT`; plus a variant with an **unknown/unmapped** sport enum and a variant with a sport/subsport pair outside the approved allowlist.
- **Expected observable:** rejected; reason names the limitation concretely — the supported scope (single-session running/cycling, indoor/outdoor) must be identifiable from the text, not merely "unsupported".
- **Oracle:** reason code equals the manifest alias; reason text contains an approved scope token (a test-side alias for the approved scope phrase, resolved from RI-1/RI-3 — **not** a phrase I invent here); and the unknown-enum variant is **not** silently mapped to running or cycling.
- **Discrimination proof:** **M-05.1** map unknown enum → running → disposition FAIL. **M-05.2** return the generic string "unsupported file" with no scope content → the naming conjunct FAIL. **M-05.3** rely on a device-model allowlist instead of file conformance (D01 explicitly forbids this) → a `FX-REJ-SPORT` with a device model that *is* in the allowlist must still be rejected; add that fixture.
- **Not decidable now:** the allowlist and the exact reason wording belong to TK10/TK11.

### MA-06 — CRC failure or malformed header → rejected, integrity failure reported, never silently repaired

- **Trace:** TC01; SR01, SR27. **Level:** `UNIT` + `CONTRACT`.
- **Stimulus:** `FX-REJ-CRC` (one byte flipped after the header, all lengths intact), `FX-REJ-HEADER`.
- **Expected observable:** rejected; integrity failure reported as the cause; the stored/derived content is **not** repaired.
- **Oracle:** disposition rejected; reason code aliases `RC.INTEGRITY_CRC` / `RC.INTEGRITY_HEADER`, which must be **distinct from each other** and from `RC.SEMANTICS_UNVERIFIED`; zero accepted rows; and — the decisive anti-repair check — **no persisted copy of the file exists whose CRC is valid**, i.e. the harness must not find a "fixed" version of the input anywhere in the store.
- **Discrimination proof:** **M-06.1** recompute and rewrite the CRC, then accept → the anti-repair conjunct FAIL (this is the exact defect D01 forbids: "never silently repaired"). **M-06.2** decode up to the corrupt point and accept what parsed → row-count FAIL. **M-06.3** collapse both integrity causes into one generic code → the distinctness conjunct FAIL.

### MA-07 — Optional field absent, e.g. indoor with no GPS → accepted, field null, quality warning recorded, no imputation

- **Trace:** TC01 (+ TC23 presentation, separate unit); SR01, SR02. **Level:** `UNIT` + `CONTRACT`.
- **Stimulus:** `FX-OK-INDOOR-NOGPS`; `FX-OK-TIMER-ABSENT`; and, for each optional, a second variant where the field is **present but an invalid sentinel**.
- **Expected observable:** accepted; the optional field is `null`; a quality warning naming the field and the cause (`absent` vs `invalid`) is recorded; no value is invented.
- **Oracle — the no-imputation rule, stated precisely:**
  1. assert `value is None`, **never** `value == 0`. Zero-fill is the classic silent imputation and an equality-to-zero assertion would pass on it;
  2. a warning exists for each nulled optional, distinguishing absent from invalid;
  3. **provenance closure:** every numeric value present in the normalised payload resolves to either a named source field reference or a declared arithmetic operation over named source fields. Any value with no resolvable source is a failure. This catches a fabricated value that is neither zero nor obviously wrong;
  4. for `FX-OK-INDOOR-NOGPS`, the file is **accepted**, `gps_available` is `false`, and no error or rejection is recorded — missing GPS for indoor activity is **valid**, not an error (constraint 3);
  5. `FX-REJ-TYPE` must **not** be the fixture used to express "no GPS".
- **Discrimination proof:** **M-07.1** zero-fill absent optionals → conjunct 1 FAIL (`0 is not None`) — this is precisely the case an equality-to-zero oracle would have passed. **M-07.2** copy elapsed into timer when timer is absent → conjunct 1 FAIL and §8.2's reverse-direction conjunct FAIL. **M-07.3** drop the warning → conjunct 2 FAIL. **M-07.4** derive distance by summing samples when `total_distance` is absent (D01: "No sample-derived fill") → conjunct 3 FAIL. **M-07.5** treat absent GPS as a rejection reason → conjunct 4 FAIL.
- **Retention sub-case, BLOCKED:** D01 says discard rejected raw bytes promptly; the implementation contract records that holding them for abuse analysis is an **open D01/D05 decision**. The test asserts unconditionally that rejected bytes are **not retrievable through any accepted-history or read path**. Whether they remain in a bounded quarantine store is asserted only after RI-7.

### MA-08 — Repeat preparation of the same accepted input → byte-identical normalised values and identical snapshot digest

- **Trace:** TC04 (+ TC27 inspection); SR05, SR06. **Level:** `INTEGRATION`, plus `UNIT` for the canonicalisation unit. Full design in §8b — this is the most heavily specified case because it is the easiest to pass accidentally.

### MA-09 — Scope failing eligibility → unexplained-reason list returned, zero model calls made

> Wording note: #305 row 9 says "Unexplained-reason list returned". Read against SR11 ("identify unmet requirements without invoking a model") and TC07/TC44 ("compare displayed reasons with the machine unmet-requirements result"), this is a typo for **explained**-reason list. I flag it rather than silently correcting a founder-facing assignment, and I test the SR11/TC44 reading. If the primary reads it literally, MA-09 is wrong and must be re-specified.

- **Trace:** TC07, TC43, TC44; SR10, SR11, SR06. **Level:** `UNIT` + `INTEGRATION`. Deterministic; **never** `LIVE-MODEL`.
- **Stimulus:** an otherwise-valid scope with one mandatory skill input removed, then evaluated twice (TC43 repeatability), with model access denied (see §8f).
- **Expected observable:** `eligible == false`; a list of unmet requirements in which **every** blocking rule names its required input and its observed gap; the ineligible scope is **not** submittable for execution; the reason list contains no other user's data.
- **Oracle:** (a) eligibility boolean and the **ordered set of unmet-requirement codes** identical across the two evaluations, and equal to the fixture manifest; (b) for each blocking code, the explanation contains both the required-input identifier and the observed value/gap — asserted by pattern against the manifest, not by string equality; (c) **zero egress attempts** by the instrumented network layer, with the detector proven live (§8f); (d) no execution/attempt row created; (e) a Postgres sequence check: `last_value` on any execution-sequence unchanged.
- **Discrimination proof:** **M-09.1** eligibility makes an HTTP call → (c) FAILs. **M-09.2** return a generic "insufficient data" with no named input/gap → (b) FAILs. **M-09.3** embed a non-deterministic timestamp or a random UUID in the unmet list → the TC43 repeat conjunct FAILs. **M-09.4** allow the ineligible scope to be submitted anyway → (d) FAILs. **M-09.5** an explanation that leaks another user's scope → (e)/non-disclosure FAIL.
- **Boundary (RI-2 dependent):** TC07 also requires the **boundary** case — coverage exactly at and one below/above the approved threshold. The expected boundary outcome is a D02 input; until it is frozen, the boundary row is `BLOCKED`, not passing.

### MA-10 — Owner A requests owner B's resource → denied at the authorisation layer, no data returned

Full design in §8e. **Trace:** TC14 (+ TC73, TC74); SR20, SR21. **Level:** `INTEGRATION` security.

### MA-11 — A record named `Assessment`, `Finding`, `Run` or `latest_result` exists in the schema → defect, the unit fails

- **Trace:** **no canonical SR or TC exists** — see §13.1. The requirement is the binding architectural condition recorded in the founder-authorised G0 replacement ([#298](https://github.com/fengguode/DATARA/issues/298), restated in #305): persist only `Import`, `SourceObject`, `Activity`, `Session`, `Snapshot` plus `Eligibility`, `Evidence` and the quarantined conflict; **no entity whose meaning is the outcome of executing a skill against a model**; **no mutable "latest result" or current-value pointer** on any entity. **Level:** `INTEGRATION` schema assertion + `CONTRACT`.
- **Stimulus:** after migrate, dump the live catalog; run the full unit; run the determinism battery.
- **Expected observable:** the persisted object set matches the approved enumeration exactly.
- **Oracle — an allowlist, never a denylist (trap 3):** query `pg_catalog`/`information_schema` for the live table and column set after migrate and require **set equality** with the approved enumeration. A denylist of `Assessment|Finding|Run|latest_result` is *insufficient*: a table named `Outcome`, `Insight` or `Result` satisfies a denylist while violating the condition, and a column named `current_value` is the same defect as `latest_result`. Set equality fails on **any** unexpected object, whatever it is called.
  - Second conjunct, the **pointer** check, behavioural rather than lexical: no column whose semantics is a mutable current-value pointer. The strongest available oracle is indirect and must be run: after preparing the same input twice (MA-08), all *content* fields of the persisted activity/session rows are equal, and re-running produces **new** rows rather than mutating old ones. A `latest_result` column fails this even if it is spelled acceptably.
  - Third conjunct: the explicit forbidden names in #305 are also checked literally, purely as a cheap supplementary signal.
- **Discrimination proof:** **M-11.1** add an `Assessment` table → set-equality FAIL. **M-11.2** add a `latest_result` column that the rerun updates → the pointer conjunct FAILs on MA-08's R1 while the denylist check alone would have passed — this mutant is exactly why the allowlist oracle is mandatory. **M-11.3** add a junction/audit table not in the enumeration → set-equality FAIL, and correctly so, because the enumeration is binding.
- **Rule:** set equality against an enumeration I do not own means the enumeration must be frozen first. Until then MA-11 is `BLOCKED`, and the *expected* enumeration is read from the approved contract, not from the implementation.

### MA-12 — Full unit run from a clean checkout using only the pinned command

Design in §7. **Trace:** no canonical SR/TC — §13.1. **Level:** `SYSTEM`.

### 8b. MA-08 / TC04 — the determinism battery in full

Requirement: repeat preparation of the same accepted input must yield **byte-identical normalised values and an identical snapshot digest**.

The naive form of this test — run twice, compare — passes in almost every implementation, including ones with real nondeterminism, because most nondeterminism is *silent*: it appears in one run out of many, or only under a different environment. The battery below is designed so that each named failure mode has a run in which it **must** appear.

**Comparison method (RI-6).** Normalised values are compared as a canonical serialisation: sorted keys, fixed decimal string formatting (never float repr), UTC `Z` timestamps, `null` for absent. The exclusion of generated identifiers and processing timestamps is a **declared allowlist of field paths**, not "ignore everything that differs" — an open-ended exclusion hides exactly the leaks this case exists to find.

**R1 — repeat in the same process.** Prepare twice. Canonical bytes and digest must be identical.
**R2 — repeat across fresh processes with different hash seeds.** `PYTHONHASHSEED` ∈ {0, 1, 42, random}. Identical. *This is the dict/set-iteration-order detector:* if field names, keys or tags are assembled through a `set`, iteration order changes with the seed and the digest changes.
**R3 — repeat under different local time zones.** `TZ=UTC` and `TZ=Asia/Shanghai` — the founder's machine is in China. Identical. *This is the local-time detector:* any `now()`/`localtime()`/naive-datetime use in a normalised value or in the digest changes here.
**R4 — repeat against a fresh database and against a populated one.** Same input file, same versions, same config; once on an empty schema, once on a database already containing `OWNER-B`'s activities and extra rows. The digest must be identical. *This is the row-order and sequence detector:* a digest computed over unordered query results without `ORDER BY`, or over a sequence that has advanced, changes here.
**R5 — clock-window scan (the silent-leak detector, and the reason R1–R4 are not enough).** Independently of the implementation's exclusion allowlist, scan **every** value in the normalised payload and in the digest input projection for an ISO-8601 instant falling within ±5 s of the run wall-clock. Any hit outside the declared generated-field allowlist is a leak and fails the case. This catches a timestamp that leaks into a *content* field where the implementation never intended one — a leak that R1–R4 would only catch by luck, if at all.
**R6 — source-order permutation.** Re-emit `FX-OK-OUTDOOR-FULL` with its `record` messages permuted. The per-activity canonical bytes must be **unchanged** if the contract declares order-insensitivity; if it declares order-sensitivity, the set of per-activity digests must be unchanged. Either way the *snapshot* digest must be unchanged. *This is the unordered-aggregate detector:* a snapshot digest built by hashing rows in arrival order changes here.
**R7 — quarantine-exclusion stability.** `FX-SNAPSHOT-CONFLICT`: the digest for `OWNER-A`'s accepted activity must equal the digest computed with `OWNER-A`'s quarantined candidate absent. *This is the cross-check with MA-03:* if quarantined rows leak into snapshot construction, this fails even though every individual preparation is perfectly deterministic.
**R8 — version binding.** The digest input projection is recorded and compared against RI-5. A change in `contract_version` or `preprocessing_version` must change the recorded version fields; it must **not** be silently absorbed.

**Zero model calls, as part of TC04.** SR06 requires ingestion and preprocessing to complete with model access disabled and to make no inference requests. This is instrumented as §8f and is a conjunct of R1–R7: any egress attempt fails the run.

**Discrimination proof — each run has a named mutant it must catch:**

| Run | Mutant that must produce FAIL |
|---|---|
| R1 | **M-08.1** inject `datetime.now(UTC)` into a normalised content field |
| R2 | **M-08.2** build a field-name list from a `set` and iterate it |
| R3 | **M-08.3** use `localtime()` or a naive `datetime` for the session instant |
| R4 | **M-08.4** hash query results without `ORDER BY`, or include `import_id`/sequence values in the digest projection |
| R5 | **M-08.5** place the import timestamp inside a content field the allowlist does not cover |
| R6 | **M-08.6** hash records in arrival order instead of sorted order |
| R7 | **M-08.7** include unresolved conflict candidates in the snapshot |
| R8 | **M-08.8** recompute a digest that omits the version fields |

**A battery is only credited when every one of M-08.1…M-08.8 has been observed to fail.** If a mutant survives, the battery is strengthened — the surviving mutant is a **real defect report against the design**, not a discardable experiment. Partial credit is recorded as `NOT RUN — oracle discrimination incomplete (n/8 demonstrated)`.

I cannot apply these mutants myself: they require editing application code, which is outside my file ownership and outside the Worker assignment's authorised paths. They are therefore **required experiments for the Worker branch under TK12's later execution**, and until they are run, MA-08 is `NOT RUN`, however green the ordinary run is.

### 8c. TC03 additional coverage — see MA-02/MA-03

Covered above. Two additions worth stating explicitly:

- **Idempotence across restart.** MA-02 repeated after a process restart against the same database. An in-process-only cache fails here.
- **Byte-level no-overwrite.** The stored original's SHA-256 is recomputed **after** every subsequent upload, not only at the end, so an overwrite-then-restore implementation cannot hide.

### 8d. TC21 — accessible file disposition and rejection reason

TC21's registry method is "Inspection and rendered UI test", and its expectation is that for every approved fixture the result identifies the file, the textual disposition and the approved reason, and **the outcome is not conveyed by colour or icon alone**. That splits cleanly into two levels with two different blockers.

**Level `CONTRACT` — machine-readable disposition (verifiable inside this unit once RI-3 lands).**

- Stimulus: every fixture row in §5.4, through the supported upload path.
- Oracle: for each row, the returned per-file result contains an identifier resolving to **that** submitted file, a disposition from the approved set, and a reason code that maps to the manifest's `RC.*` alias. Three additional conjuncts:
  1. **Family distinctness.** The aliases for unsupported type, unsupported sport, chained layout, multisport layout, missing/invalid required semantics and integrity failure are **pairwise distinct**. One generic `REJECTED_UNSUPPORTED` for everything fails this. This is the most likely real defect in a first implementation.
  2. **Instance-independence.** Two *different* instances of the same cause — e.g. `FX-REJ-CRC` and a second file truncated at a different offset — produce the **same** reason code. A code that varies per instance is not stable.
  3. **No raw leakage.** Reason text contains no byte offsets, hex dumps, file paths, SDK exception text or OS error strings.
- Discrimination proof: **M-21.1** single generic code → conjunct 1 FAIL. **M-21.2** `str(exc)` → conjuncts 2 and 3 FAIL. **M-21.3** reason attached to the batch instead of the file → the file-identification conjunct FAILs when a `FX-BATCH-MIX` batch contains two distinct rejection causes.
- Stability **across contract versions** cannot be tested yet: it needs two frozen contract versions and a recorded mapping. Recorded as an open item, not as passing.

**Level `RENDERED-UI` — BLOCKED, with the preflight specified.**

Milestone A #305 authorises no template, view or frontend path. There is no target. Per the shared lessons and D04, an API or assertion result is **not** rendered-UI evidence. When a target exists, the preflight and checks are:

- record browser name and version, OS, automation path, and the served commit/build identity;
- viewport coverage: 320 CSS-pixel reflow and 200 % zoom, plus one desktop viewport (D04);
- keyboard-only completion of upload → disposition, with focus perceivable after each state change and errors programmatically associated with the affected file;
- screen-reader evidence naming the **actual** tool and environment (D04 requires the tool be named, not assumed);
- **non-colour check:** with all colour and icon styling disabled, the disposition and reason remain fully readable; and a DOM/semantic inspection confirming the status is text, not only an `aria-label` on an unlabelled icon;
- async status announcement when disposition arrives after upload.

Browsers to cover: current stable Chrome and Edge, plus Firefox keyboard flows (D04). If no browser/target can be preflighted, the case stays `BLOCKED` and that fact is reported — it is never downgraded to the API level.

### 8e. Two-identity isolation — MA-10 in full

- **Trace:** TC14, TC73, TC74; SR20, SR21. **Level:** `INTEGRATION` security. `RENDERED-UI` race component (TC75) is **BLOCKED** — no target.
- **Precondition:** disposable database; `OWNER-A` and `OWNER-B`, each with distinct canary values in filename, sport, sport category and any stored metadata, so a leak is detectable by content and not only by count.
- **Stimulus, all as `OWNER-A`:** request B's `Import` by opaque ID; request B's `SourceObject` by ID; request B's `Activity` by ID; request B's `Snapshot` by ID; supply B's owner identifier in the request body; supply B's owner identifier as a query parameter; request B's id while authenticated as A with an otherwise valid shape; issue the same request unauthenticated; attempt to **write** into B's scope by supplying B's owner identifier on upload.
- **Expected observable:** denial at the authorisation layer, before any foreign data is read or any execution occurs; no state change anywhere.
- **Oracle, four conjuncts:**
  1. **Status** matches the approved non-disclosure contract (D04: unauthenticated `401`; inaccessible or missing owner resource → generic `404`; `403` reserved for operation-level denial that does not confirm another owner's object).
  2. **Indistinguishability.** The response for *B's real ID* is byte-identical to the response for a *syntactically valid but nonexistent ID*. This is the strong non-disclosure oracle: a `403 "belongs to another user"` response fails it, because it confirms existence. "Fail, not return the other identity's data" is satisfied by this only if the denial also reveals nothing.
  3. **No content.** No B canary value appears anywhere in the response body, headers or error text.
  4. **No effect.** Row counts for both owners are unchanged; no new `Import`; no execution record; the write attempt created nothing in B's scope.
- **Discrimination proof:** **M-10.1** authorise on a client-supplied owner ID → the body-supplied-owner probe returns B's data, conjunct 3 FAILs. **M-10.2** return `403` with an ownership message → conjunct 2 FAIL (existence disclosed). **M-10.3** filter by owner **after** fetching the row → conjunct 2 FAIL on the differing body/status; if the filter is applied after a fetch that also triggers side effects, conjunct 4 FAILs. **M-10.4** authorise in the view but not in the repository/query layer → the direct repository-path probe (below) FAILs, which is why the probe set includes a repository-layer call, not only HTTP. **M-10.5** a global `source_digest` unique constraint (shared with M-02.3) → B's upload is rejected with an existence signal, conjuncts 1–3 FAIL for the write probe.
- **Required beyond HTTP:** the repository/query layer must be probed directly with a forged owner/resource pair, because HTTP-only probes cannot detect an authorisation decision made only at the view. D05 additionally requires that the application DB role is neither table owner, superuser nor `BYPASSRLS`, and that forced RLS / owner-key constraints are treated as **additional** protection — not as the only check. The test asserts both application-level denial **and**, where RLS is claimed, a direct-SQL probe as the application role.
- **Out of scope here, stated so it is not assumed:** log-content inspection is an SR13/TC76 matter and is **not** claimed by this case.

### 8f. Zero model calls — a detector that can actually detect

Constraint: eligibility is a pure deterministic function. A test that asserts "the code contains no HTTP client" is not evidence: a function named `analyse()` can call `socket` without importing `requests`, and a source-grep is inspection, not a passing test.

Four layers, and the one that makes the others trustworthy is the second:

1. **Egress tripwire.** The whole suite runs with a patched socket layer (`socket.socket.connect`, `socket.create_connection`, plus `urllib`, `httpx`, `requests` and any provider-SDK client constructor) that records every attempted connection with host and port and raises. Any hit fails the case. Loopback is included on purpose: a call to a local model would also be a violation, because P0 eligibility must make **no** model call at all.
2. **Detector self-test — the negative control for the negative.** Before the suite runs, the harness performs one deliberate connection through the *same* instrumented stack (to a closed loopback port) and asserts the counter incremented to exactly 1. **If the self-test does not register, the run is void** and the model-call evidence for that run is recorded as `UNAVAILABLE`, not as zero. This is the specific discipline #297's neighbourhood keeps needing: a "zero" that cannot be shown non-zero is not evidence.
3. **Persistence-side check.** No execution/attempt row exists for an ineligible scope, and the Postgres `last_value` of any execution-related sequence is unchanged from before the eligibility call.
4. **Determinism cross-check.** The eligibility result is byte-identical across two evaluations (§8b's R1 method), which a model-backed implementation would not be.

Layers 1 and 2 are the oracle; layers 3 and 4 are corroborating and are labelled as such.

**Discrimination proof:** **M-MC.1** eligibility performs an outbound GET → layer 1 records a hit → FAIL. **M-MC.2** eligibility calls a loopback HTTP endpoint → layer 1 records a hit → FAIL. **M-MC.3** the tripwire is installed but the self-test cannot register it → the run is void, which is itself the correct outcome and must be reported as `UNAVAILABLE`, never `PASS`.

**Level label discipline:** this is `UNIT`/`INTEGRATION` determinism evidence. It is **not** `LIVE-MODEL` integration and establishes nothing about provider compatibility or model quality. Those are TC08 and a separate release gate, and no live call is authorized here.

### 8g. Encoded constraints — summary of how each is tested

| Constraint | Where enforced | Decisive oracle |
|---|---|---|
| 1. No imputation, ever | §MA-07, MA-04 | `value is None` never `== 0`; warning per nulled field; provenance closure over every numeric value |
| 2. Elapsed ≠ timer, never silently interchanged | §MA-07, MA-08 | see below |
| 3. Missing GPS is valid for indoor | MA-07 conjunct 4 | indoor fixture **accepted**, `gps_available == false`, no error |
| 4. Synthetic DATARA-authored fixture only | §5 | no personal file; no upstream binary; generator determinism FXGEN-1…5 |
| 5. Pinned command prints environment identity first | §7 | ordering + independent agreement + sensitivity + clean-checkout reproduction |

**Constraint 2, fully specified.** Fixture `FX-OK-ELAPSED-NE-TIMER`: `elapsed = 1800 s`, `timer = 1742 s` (a 58 s auto-pause gap, so the two values are unmistakably different).

- Oracle forward direction: `elapsed_s == 1800` exactly; `timer_s == 1742` exactly; both non-null; the P0 recorded-volume metric for this activity equals **1800**, never 1742.
- Oracle reverse direction, on `FX-OK-TIMER-ABSENT`: `timer_s is None`; `elapsed_s` unchanged; and `timer_s` is **not** back-filled from `elapsed_s`.
- Labelling: the stored/returned field for volume is explicitly the **recorded elapsed activity duration**, not a generic "duration" (D01). A field named `duration` populated from timer fails on naming even if the number is right.
- Discrimination proof: **M-02a** `elapsed = timer or elapsed` → forward FAIL. **M-02b** `timer = elapsed` when absent → reverse FAIL. **M-02c** a generic `duration` field sourced from timer → forward FAIL. **M-02d** use `total_timer_time` for the volume metric while everything else is correct → forward FAIL — and this is the one a visual check would miss, which is why the numeric conjunct is mandatory.

## 9. Oracles that cannot fail — traps found in the naive forms of these twelve cases

The team's recurring failure is a negative control that cannot return the other value. Each row below is a naive oracle that would have looked green, and the correction.

| # | Naive oracle | Why it cannot fail | Corrected oracle |
|---|---|---|---|
| 1 | Compare the product's stored digest to the product's own digest function | A wrong hash function is wrong on both sides identically | Test recomputes SHA-256 with `hashlib` over bytes it fetched itself |
| 2 | Compare normalised values to the SDK's decoded output | Generator and decoder share the same erroneous mapping — explicitly forbidden by `fixture-provenance.md:19` | Compare to manifest values stated as exact `Decimal`s from **raw integers** via `raw/scale − offset` |
| 3 | Denylist `Assessment\|Finding\|Run\|latest_result` in the schema | A table named `Outcome` passes and still violates the condition | **Allowlist**: set equality between the live catalog and the approved enumeration |
| 4 | Assert zero network calls | May mean the instrumentation is dead, not that no call happened | Detector **self-test** that must first show the counter can increment; otherwise `UNAVAILABLE` |
| 5 | Diff two runs ignoring whatever differs | An open-ended exclusion hides the very leaks the case exists to find | Declared field-path allowlist **plus** R5's independent clock-window scan |
| 6 | Duplicate test = "activity count did not grow" | An implementation that silently merges passes it | Count `Import`, `SourceObject` **and** stored byte objects; assert returned IDs are equal; **and** submit the same bytes as `OWNER-B` expecting acceptance |
| 7 | Conflict test = "a conflict was reported" | Says nothing about exclusion from history, nor about tolerance | Unchanged history count **and** duration total; **and** `FX-NEAR-B` (1 s apart) accepted with zero conflict records |
| 8 | Rejection-reason test = "reason is not empty" | A single generic string passes | Five cause families are pairwise distinct; equivalent instances share a code; no raw exception text |
| 9 | Idempotence tested in the same process only | An in-process cache passes | Repeat after a process restart |
| 10 | Isolation test asserts a `403` | A `403` discloses that the resource exists | Response for a real foreign ID is byte-identical to the response for a nonexistent ID |
| 11 | `assert "requests" not in source` | Source inspection is not runtime evidence; a socket call needs no `requests` | Runtime egress tripwire with a proven-live self-test |
| 12 | Environment block asserted to exist | A hardcoded `echo` passes | Values independently queried, **and** sensitivity to a changed lock hash |
| 13 | Optional-absent asserted as `value == 0` or falsy | Zero-fill **is** the imputation defect; `0` is falsy so it passes | Assert `value is None` |
| 14 | Snapshot digest compared across two empty-ish scopes | An always-constant digest passes | RI-5 declares the digest projection; R4/R7 prove the digest actually responds to input and to quarantine exclusion |

## 10. Compressed timestamps — the #297 blocker, designed for both states

[Discussion #297](https://github.com/fengguode/DATARA/discussions/297) records that the pinned Python FIT decoder cannot decode compressed timestamp records; `fit-support-matrix.md:58` records that the pinned SDK dispatches compressed headers and then explicitly raises an unsupported error, and the decode spike found 3880 records with **0** compressed timestamps. Two facts follow, and they are different in kind.

**State A — today, pinned SDK 21.217.0.** What *is* achievable today is the **rejection** branch:

- `FX-COMPRESSED-TS` → disposition `rejected`, reason code mapping to `RC.TIMESTAMP_COMPRESSED`, **distinct** from the generic unsupported-family code, so the athlete learns the actual limitation;
- **zero** accepted `Activity`/`Session` rows. This conjunct is essential, because the pinned decoder's `read` returns collected messages *plus* errors after an exception — an implementation that accepts the messages it managed to collect before hitting the compressed record would look like a partial success. The anti-partial-decode check is mandatory, not decorative;
- no reconstructed timestamps, no omitted affected samples, no "accepted with partial data".

**State B — only after a recorded decision.** If the founder selects extended scope or a reviewed engine substitution, the expectation becomes: `FX-COMPRESSED-TS` and its **uncompressed equivalent** must produce **identical normalised values and an identical snapshot digest**. That is a far stronger oracle than "it decoded": it proves the timestamps were reconstructed *correctly* rather than merely not-crashing. It also becomes the natural second member of the §8b determinism battery.

**Which expectations are currently unachievable, and why — stated plainly:**

1. **Any claim that the pinned engine decodes compressed timestamps.** This is an engine limitation, not a test-design gap. No test can be written that makes it true.
2. **Consequently, TC01's "timestamp fixtures receive specified outcomes"** can currently be satisfied for compressed timestamps only through the **rejection** branch. Treating acceptance as the oracle would be inventing capability.
3. **TC19 source conformance for compressed-timestamp decoding** stays open regardless of test execution.
4. **Generating `FX-COMPRESSED-TS` at all is currently blocked**, and this is the part most easily missed: [fixture-provenance.md](../management/source-evidence/fixture-provenance.md) forbids copying an upstream sample, so the fixture must be generated — but the byte layout of a compressed-timestamp record needs official protocol evidence, and `fit-support-matrix.md:19` records that the official protocol prose was **not** substantively captured (SRC05). I can specify the fixture's *intent*; I cannot specify its *bytes* from approved evidence. Specifying them from memory would be exactly the guessed mapping the matrix forbids.
5. **A real-file decode spike is a spike, never TC01/TC19 evidence** (#297). And because the only real file available is the founder's personal telemetry, even a spike requires his explicit authorization to process that file at all (FIX05), and its evidence must be sanitised — never the file, never a hash of it, never its contents in a log.

**What I am not doing:** I am not treating the compressed-timestamp disposition as a test-design decision, and I am not writing a "skip" that would later be read as a pass. `FX-COMPRESSED-TS` is `BLOCKED — RI-8`, with the State A rejection oracle already frozen so that the day the code lands, the branch is testable the same day.

## 11. Not-run and blocked register

| Case | Level | State | Blocker |
|---|---|---|---|
| MA-01…MA-07, MA-09 | UNIT/CONTRACT/INTEGRATION | `NOT RUN` | TK11 (#117) not delivered; RI-1…RI-3, RI-9 |
| MA-02, MA-03 | INTEGRATION | `NOT RUN` | TK15 (#121) not delivered; MA-03 additionally gated on RI-4 (TK14 #120) |
| MA-08 (incl. R1–R8) | INTEGRATION | `NOT RUN` | TK18 (#124) not delivered; RI-5, RI-6; and the eight mutants unapplied |
| MA-10 | INTEGRATION security | `NOT RUN` | TK15 (#121) not delivered; repository-layer probe needs the implemented query layer |
| MA-11 | INTEGRATION schema | `BLOCKED` | RI: approved enumeration not frozen; no canonical SR/TC (§13.1) |
| MA-12 | SYSTEM | `BLOCKED` | no committed `scripts/milestone_a.sh`; no PostgreSQL; Windows host with no assumed compatible runtime; pinned Linux/container target not preflighted |
| TC21 rendered portion | RENDERED-UI | `BLOCKED` | RI-10; no target, no browser preflight, no frontend in #305's authorised paths |
| TC22, TC23, TC25 rendered/inspection | — | out of this unit | assigned to TK15/TK16/TK20; not silently claimed here |
| TC15 athlete validation | ATHLETE-VALIDATION | not applicable | separate gate; no candidate exists |
| TC08 live-model | LIVE-MODEL | not authorized | separate release gate; no credentials, no spend cap, no approval |

## 12. Preflight that a future TK12 execution must record before any rendered or system case

Recorded now so it is not improvised later:

- **Runtime:** OS and version; Python implementation and version; Django version; PostgreSQL `server_version()`; container image digest if containerised; the pinned dependency lock file path and its SHA-256; the candidate commit SHA; whether the run is a clean `git clone`.
- **Browser (rendered cases only):** browser name and version, OS, viewport list including 320 CSS-pixel reflow and 200 % zoom, automation path (driver/tool and version), the served build/commit identity, and — for screen-reader evidence — the **actual** tool and environment named. If any element cannot be recorded, the case is `BLOCKED`.
- **Isolation:** two disposable synthetic identities, canary values, and a disposable database whose teardown is verified. Personal credentials are never used.
- **Honest note:** I have **no** browser or PostgreSQL preflight capability in this environment, so this list is a specification, not a report of a completed preflight.

## 13. Required changes outside my file ownership

I did not make these changes. Each needs its owning role.

### 13.1 Traceability gaps

| Gap | Detail | Requested owner |
|---|---|---|
| AC-11 has no canonical SR or TC | The binding persistence-scope condition exists only in the G0 record restated in #305. Nothing in `requirements-registry.json` requires it, so it cannot be *verified* against a requirement. Candidate SR text: "The system shall persist only the approved source, normalised, snapshot, eligibility, evidence and quarantined-conflict records, and shall not persist any entity whose meaning is the outcome of executing a skill against a model, nor any mutable current-value pointer." | System Architect (Feng Guo), registry owner; Quality Manager to audit |
| AC-12 has no canonical SR or TC | Reproducibility of the pinned command's printed environment identity is required by #305 but is not an SR. Candidate SR: "A single pinned command shall print Python, framework, database, dependency-lock and commit identity before any test result, and a full run shall reproduce that identity from a clean checkout." | System Architect; Quality Manager |
| "TC01–TC34" is not an accurate range | The registry contains TC01–TC27, TC40–TC51 and TC60–TC80. There is no TC28–TC34. TC16–TC18 are P1 and excluded from this baseline. This design therefore maps to the IDs that actually exist | Primary Coordinator (Yi Tang), for the record |
| Reason-code enumeration | Needed as an approved contract (RI-3) before MA-04…MA-07 and TC21's code-level oracle can be frozen | Architect (TK10/TK11) |

### 13.2 Fixture supply

- `.gitignore` currently blocks DATARA's own cleared synthetic fixtures (`*.fit`, `*.FIT`), and its own comment requires the rule to be narrowed **in the same change** that adds a cleared fixture, citing the rights decision. Owner: the lane that owns #300 / TK09. My recommendation (§5.3) is to avoid the problem entirely by committing a generator plus a manifest and materialising binaries at test time.
- A home for the fixture manifest and the generator. Requested path (not created by me): `datara/tests/fixtures/` with `manifest.json` and the generator, per #305's `datara/tests/` authorisation. Owner: Worker, under TK11/TK15/TK18.
- The compressed-timestamp disposition and, if extended scope is chosen, the official protocol evidence needed to generate `FX-COMPRESSED-TS` at all (§10.4). Owner: Architect; founder decision per #297.

### 13.3 Process

- `scripts/milestone_a.sh` must print the §7 environment block before any result line. Owner: Worker.
- Every case above needs its named mutants applied at least once before it can be credited as a discriminating test. Owner: Worker branch, under TK12's later execution, with me recording the results.

## 14. A self-reported process observation

While surveying the repository I ran a recursive file listing of `docs/` and a directory listing of the repository root, and in the same survey batch listed `demo_file/`, which printed the founder's personal file name. **I did not open, read, copy, hash or stat that file, and I did not do it again.** No byte of it was accessed and nothing derived from it appears in this document or in any commit.

I record it because it is exactly the discipline this design argues for: a control that depends on the operator not running a plausible command is not a control. The concrete implication for my design is that **no fixture-supply step in §5 may depend on enumerating `demo_file/`** — which is consistent with constraint 4 and with the `.gitignore` rule already in place.

---

## Assignment activity and validation

- **Runtime identity:** OpenCode sub-agent session, role **User Tester — Abt Hermann_space-bunny-free-max_OpenCode (AI agent)**. Model as configured in this harness: `space-bunny-free` (provider `opencode`), not independently verified by an external check. `Agent-run: unavailable (OpenCode runtime exposes no execution link to this session)`.
- **Files authored:** `docs/p0-design/test-design.md` (this file). Nothing else was created or edited.
- **Read for this assignment:** `AGENTS.md`; `docs/team/workflow.md`; `docs/team/attribution.md`; `docs/team/knowledge/user_tester.md`; `docs/team/knowledge/shared-lessons.md`; `docs/management/README.md` title convention; `docs/management/validation-plan.md`; `docs/management/p0-decision-baseline-2026-10-01.md`; `docs/management/p0-ui-requirements-review.md`; `docs/management/source-evidence/fixture-provenance.md`; `docs/p0-design/fit-support-matrix.md`; `docs/p0-design/implementation-contracts.md`; `docs/p0-design/README.md`; `docs/p0-design/test-design-findings.md`; `docs/management/requirements-registry.json`; `.gitignore`; and, live from GitHub, issue #305 and discussion #297. Issue #298 was requested but the API returned `403` on the second attempt; the binding condition is quoted from its authoritative restatement in #305.
- **Validation performed:** none of the product kind, because there is nothing to validate. What I did do: read the live issue and discussion rather than relying on local records; enumerated the registry's actual `verification_cases` and `tasks` and mapped to the IDs that exist rather than the range quoted in my assignment; confirmed from `fit-support-matrix.md` and #297 that the compressed-timestamp limitation is unresolved; confirmed from `fixture-provenance.md` and `.gitignore` that no fixture binary may be committed today; and checked `git status`/diff to confirm no file outside my two owned paths is touched by this commit.
- **Limitation:** `gh` CLI is not installed in this environment, so GitHub reads were made through the public REST API without authentication. Reads succeeded for #305 and #297; #298 failed with `403` and is disclosed above. Per the live-read rule, Project field values (priority, status, Agent) could not be read at all; I relied on the issue's own recorded `priority unknown / not set` statement and the registry's `priority: P0` for TK12, and I flag that as **unconfirmed against live Project state**.
- **What is explicitly not claimed:** no case is run, passing, Done, Verified, Accepted or released; no requirement status was changed; no fixture was generated; no application code exists to test; no environment was preflighted; no browser was used; no model call was made or is authorised.