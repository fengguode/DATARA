# Source record and evidence map — STK001, STK002, STK003, STK004, STK011, STK012

Status: **evidence mapping only. Nothing here is Done, Verified, Accepted or released.**
`TC01`, `TC03`, `TC19` and `TC24` all remain **Not run** in
`docs/management/requirements-registry.json` (verified by reading that file at
`9a1693b`), and this document changes no registry status.

Assignment: [issue #384](https://github.com/fengguode/DATARA/issues/384), WP01, subtasks
STK001 (#173), STK002 (#174), STK003 (#175), STK004 (#176), STK011 (#183), STK012 (#184).
Requirements in scope: **SR27** (pin official FIT source evidence), **SR01**, **SR02**,
**SR04**, and **SR03** where a persistence fact is cited. Decisions **D01** and **D02**
are cited as recorded decisions, never as authority I may extend.

Base commit: `9a1693b`. Every code line reference below was read in this worktree at that
commit. Nothing was inferred from a name or a docstring.

---

## Standing of the records cited here — read this before any "divergence" row

`docs/p0-design/README.md:3` records the package as *"engineering proposal; not approved,
implemented, verified, accepted, or released"*, and `:11` states the rule this document
depends on: **"Contracts are proposals unless a founder decision record says otherwise."**
`fit-support-matrix.md:1` titles itself *"**Proposed** FIT support and mapping matrix"* and
`:3` states it is *"not an approved implementation/source contract or conformance result."*
`duplicate-conflict-options.md:3` is likewise *"proposed research output … No new policy,
schema freeze or implementation evidence."*

So those records are **proposals**, and this document does not call them approved anywhere.

**The binding authority it does cite is `docs/management/decision-register.md`, whose §3
(3 October 2026, Author: **System Architect — Feng Guo**, `:90`–`:92`) records five
architecture decisions D-A1 … D-A5 (`:94`, `:96`, `:98`, `:100`, `:102`).** Those are
recorded decisions, and they are what the implementation is obliged to satisfy. Where a
finding here says *implementation gap against an authoritative record*, it means **one of
these decisions**, cited by its D-number.

Where the same rule is *also* carried by a proposal record, this document cites the
decision first and names the proposal only as corroboration. The two are not merged: a
proposal can be wrong and a decision can be unimplemented, and those are different
findings with different owners.

**An earlier revision of this document got this wrong in a way worth naming.** It called
`fit-support-matrix.md` *"the approved record"* in twelve places while that file disclaims
approved status in its own first three lines, and it never once cited
`decision-register.md`. The conclusions survive, and C6's obligation in fact rests on a
*stronger* basis than the document then claimed. But an obligation asserted on a record
that denies being approved is an unsupported obligation, and the correct authority was
uncited while sitting in the same repository. Corrected throughout below.

---

## How to read this document

Every claim carries one of two marks.

- **established** — a requirement ID plus the file and line that proves it. The line is
  what the code *does*, not what a comment says it does.
- **unknown** — the precise open question and its decision owner.

Two boundaries apply throughout and are not restated in every row:

1. **No threshold, tolerance, policy or protocol version is invented here.** Where the
   code enforces a number whose provenance is not in this repository, that is recorded as
   an **unknown routed to the founder**, not endorsed.
2. **A pinned dependency is not a protocol version.** `garmin-fit-sdk==21.217.0`
   (`requirements-milestone-a.txt:39`) is a fact about the installed package. It is not
   evidence of a FIT protocol version, and the SDK's own generated profile identity is not
   a FIT file-header profile number. `fit-source-inventory.md` already draws this
   distinction; §1 below keeps it.

Owner routing used in this document:

- **Founder** — product decisions: accepted scope, thresholds, tolerances, protocol
  version selection, fixture rights.
- **System Architect — Feng Guo** — architectural findings: where the implementation and a
  recorded decision in `decision-register.md` disagree about structure, vocabulary, or
  evidence discipline.

I am not deciding any of these. Each is a question, not a recommendation.

---

## 1. STK001 — official FIT protocol and profile reference inventory

Parent: [TK09 #115](https://github.com/fengguode/DATARA/issues/115), STK001 #173.
Requirement: **SR27**, oracle **TC19** (inspection) and **TC24** (inspection).

### 1.1 References already recorded with a location and an identity

These are established *as records*. I did not re-retrieve any of them; I read the
repository record of the retrieval. That distinction matters: a recorded retrieval is
evidence that a reference was identified, not evidence that its content is correct.

| ID | Location recorded | Version / identity recorded | State here | Record |
| --- | --- | --- | --- | --- |
| SRC01 | Official Python release tag page and tag API for `garmin/fit-python-sdk` | tag `21.217.0`; commit `6db34d7958dce3cef89194e82d6bdc9437c810de` | **established** (as a recorded reference) | `docs/management/source-evidence/fit-source-inventory.md:14` |
| SRC02 | Generated `garmin_fit_sdk/profile.py` at that commit | declares `21.217.0` `Release`; generation tag `production/release/21.217.0-0-g248b1c46`; recorded SHA-256 `cfc27376…865c` | **established** (as a recorded reference) | `fit-source-inventory.md:16` |
| SRC03 | Pinned `pyproject.toml` at that commit | project `garmin-fit-sdk 21.217.0`; requires Python `>=3.6` | **established** (as a recorded reference) | `fit-source-inventory.md:17` |
| SRC04 | Pinned `README.md` at that commit | recorded SHA-256 `1ca50152…9ae6` | **established** (as a recorded reference) | `fit-source-inventory.md:18` |
| SRC05 | Garmin FIT protocol landing page | **no pinned document revision obtained**; substantive protocol text not captured | **unknown** — see §1.3 | `fit-source-inventory.md:19` |
| SRC06 | Current-`main` SDK `LICENSE.txt` | blob `18f524ce…69fb`; recorded SHA-256 `6cc7ff94…428cf` | **established as a recorded reference**; applicability to the selected commit is **unknown** — see §1.4 | `fit-source-inventory.md:20` |
| SRC07 | Version-specific PyPI JSON metadata for `garmin-fit-sdk/21.217.0` | `garmin-fit-sdk 21.217.0`; license metadata `null` | **established** (as a recorded reference) | `fit-source-inventory.md:21` |

Five additional pinned-content rows exist in the mapping matrix and are cited in §3 and §4
below as MAP01–MAP05: `fit-support-matrix.md:13`–`:17`.

### 1.2 What the code actually pins, and what that does not license

| Fact | State | Evidence |
| --- | --- | --- |
| The dependency pin is `garmin-fit-sdk==21.217.0` | **established** | `requirements-milestone-a.txt:39` |
| The pin is deliberate and is a *file-format decoder*, not a model-provider SDK | **established** (as the recorded rationale) | `requirements-milestone-a.txt:22`–`:37` |
| The classification module names `21.217.0` and the generation tag as its SDK identity, and asserts the profile version `{major 21, minor 217, patch 0, type Release}` | **established** | `datara/classification.py:65`–`:66`, `:285`–`:290`, `:312`–`:315` |
| The module treats a profile **mismatch** as distinct from a profile **absence**, with separate exception types | **established** | `datara/classification.py:260`–`:279`, `:343`–`:358`, `:393`–`:397` |
| **The FIT *protocol* version the product supports** | **unknown** — the code accepts protocol major `1` or `2` (`datara/classification.py:81`, enforced at `:955`–`:963`), but the authoritative protocol *document* that defines those majors was never captured (SRC05, `fit-source-inventory.md:19`). Owner: **founder**, for the selection; **System Architect — Feng Guo** for the evidence requirement. | — |
| **The FIT file-header profile version the product accepts** | **unknown** — see §1.3 | — |
| Whether the **installed** package bytes are the pinned artifact | **unknown** — see §1.5 | — |

### 1.3 The header profile version is read and never checked

This is the sharpest gap between SR27 and the code, so it is stated plainly rather than
buried in a table.

- The header's `profile_version` field is read from bytes 2–4 (`datara/classification.py:633`).
- It is carried on every disposition as `profile_version_raw` (`datara/classification.py:918`, `:927`, `:1006`).
- **It is never compared to anything.** No minimum, no maximum, no allowlist, no
  equivalence class. `verify_pinned_profile` (`datara/classification.py:296`–`:340`)
  checks the *SDK's own* profile version and several enum values; it does not receive, or
  check, the file's header profile version.
- It is not persisted: `Import.profile_reference` exists (`datara/models.py:205`) but the
  duplicate/conflict write path sets it to `None` unconditionally
  (`datara/dedup.py:861`), and `OwnerScopedStore.record_import`
  (`datara/db.py:209`–`:230`) only forwards a caller-supplied value, which no production
  caller supplies.

**established:** the read, the carry, the absence of any comparison, and the `None` write —
`datara/classification.py:633`, `:1006`, `datara/dedup.py:861`.

**unknown:** *What is the authoritative FIT file-header profile version (or version set)
that DATARA accepts, and which official document fixes it?* SR27 requires the source
contract to "identify the authoritative official FIT protocol/profile version … for every
accepted variant". Until that version is selected by the founder and evidenced, every
accepted file is accepted with an unchecked header version, and the accepted variant
cannot be named. Owner: **founder** (selection), **System Architect — Feng Guo**
(evidence record). I am not proposing a number.

### 1.4 Terms for the pinned SDK artifact

**established:** `fit-source-inventory.md:20` records that at the selected commit neither
`LICENSE.txt` nor `LICENSE` was present in the recursive tree, that the current-`main`
text cannot stand in for the artifact, and that no acceptance, rights conclusion or
inquiry was performed.

**unknown:** *Which licence and use/redistribution conditions apply to
`garmin-fit-sdk==21.217.0` as distributed, and is DATARA's intended use — install,
import, and internal processing of athlete files — permitted?* Owner: **founder**. This
blocks an acceptance conclusion, not this inventory; `fixture-provenance.md:25` already
records the same block.

### 1.5 Installed-artifact identification

The task environment for this work has `garmin_fit_sdk` importable. Observed by me in this
worktree, at runtime:

- `Profile['version']` == `{'major': 21, 'minor': 217, 'patch': 0, 'type': 'Release'}`.
- `Profile['types']['date_time']` == `{268435456: 'min'}`.
- `Profile['types']['file'][4]` == `'activity'`; `[15]` == `'monitoring_a'`; `[32]` ==
  `'monitoring_b'`; `[11]` == `'goals'`; `[20]` == `'activity_summary'`.
- `Profile['types']['sub_sport'][254]` == `'all'`.
- `fit.BASE_TYPE_DEFINITIONS` has 17 entries.
- `garmin_fit_sdk/util.py:18` declares `FIT_EPOCH_S = 631065600`, and `util.py:25` adds it
  to the raw value.
- `garmin_fit_sdk/decoder.py:347`–`:348` raises
  `"Compressed timestamp messages are not currently supported"`.

These observations match the literals the code asserts
(`datara/classification.py:285`–`:293`, `:856`, `:1018`–`:1025`), which is why the code's
own assertions pass here.

**unknown:** *Is the installed package byte-identical to the published artifact for
`21.217.0`?* I did not hash the installed files, and
`fit-source-inventory.md:21` and `:29`–`:30` record that the published wheel and sdist
hashes are **publisher-index declarations**, not verified bytes. The two values cannot be
compared until someone installs and hashes. Owner: **System Architect — Feng Guo** to
schedule the check; no product decision is involved.

### 1.6 What this section does not claim

No conformance claim, no coverage claim, and no claim that any supported population has
been exercised. `fit-support-matrix.md:491` already records that coverage of the supported
population is unproven; nothing here improves that.

---

## 2. STK002 — fixture provenance and terms

Parent: TK09 #115, STK002 #174. Requirement: **SR27**, oracle **TC24**.

### 2.1 Fixtures that exist in this repository

Every fixture used by the test suite is **DATARA-authored and synthetic**. There is no
binary FIT fixture in the repository and none is reachable from a test.

| Fixture set | Location | Generator / identity recorded | Terms state | State |
| --- | --- | --- | --- | --- |
| Synthetic FIT byte encoder for the classifier | `datara/tests/test_classification.py:161` (`_build_fit`), version string `TK11-FIXTURE-1` at `:84` | header block `:14`–`:33` records author, generator, mapping reference and that no upstream sample is used | upstream sample rights explicitly cited as unresolved and therefore avoided (`:18`–`:19`) | **established** |
| Synthetic original bytes for storage/dedup | `datara/tests/test_storage.py:47` (`synthetic_original`), version `datara-synthetic-original/1` at `:44` | `:13`, `:41`–`:44` | founder's private export named as out of scope | **established** |
| Normalized-activity fixtures | `datara/tests/test_normalization.py` provenance block `:11`–`:25` | policy constants declared **synthetic stand-ins**, `mapping_reference` naming them as such (`:22`–`:25`) | not derived from the founder's file; not upstream samples | **established** |
| Scoped-input fixtures | `datara/tests/test_scoped_input.py` provenance block `:26`–`:35` | constructed in memory; synthetic stand-ins for the pending mapping | same | **established** |

Two further properties are established by test assertion rather than by prose:

- `datara/tests/test_storage.py:335`–`:345` asserts the fixture generator is
  deterministic and byte-stable, so a fixture hash is reproducible.
- `datara/tests/test_scoped_input.py:2055` asserts that **no** scoped-input module text
  contains the substring `demo_file`, so the excluded path cannot leak into that lane.

**The founder's personal telemetry is out of scope by construction.** The directory
`/demo_file/` is excluded at `.gitignore:31`. I did **not** open, read, copy, hash,
stat or list any file under it, and I did not run any command that would have. Nothing in
this document describes that file's size, hash, contents or field values.

### 2.2 Candidate fixture sources and their terms

Recorded in `docs/management/source-evidence/fixture-provenance.md:9`–`:13` (FIX01 at `:9`
through FIX05 at `:13`).

| ID | Candidate | Provenance recorded | Terms | State |
| --- | --- | --- | --- | --- |
| FIX01 | Future DATARA-authored synthetic running/cycling activities | authorship/generator **proposed**; no generator or binary existed at recording | determine SDK-derived conditions before generation/publication | **unknown** — owner question recorded at `fixture-provenance.md:9` |
| FIX02 | Upstream `tests/fits/ActivityDevFields.fit` at commit `6db34d7…` | path confirmed in the official tree; **binary not downloaded** | redistribution rights **unresolved** | **unknown** — owner: **founder** |
| FIX03 | Upstream `tests/fits/HrmPluginTestActivity.fit` | same | same | **unknown** — owner: **founder** |
| FIX04 | Upstream `tests/fits/WithGearChangeData.fit` | same | same | **unknown** — owner: **founder** |
| FIX05 | Separately permissioned controlled athlete example, private | no file, owner or permission supplied | needs explicit owner authorization; must never be inferred from an upload | **unknown** — owner: **founder** |

### 2.3 What remains open, precisely

- **unknown:** *Who is the independent expected-value reviewer, and by what method, for
  each generated fixture?* `fixture-provenance.md:19` requires an independent reviewer and
  warns that "a generator and decoder sharing the same erroneous mapping cannot be the sole
  oracle". The suites satisfy the *separation* requirement — expected values in
  `datara/tests/test_classification.py` are authored as literals independent of the
  decoder (`:27`–`:29`) — but **no reviewer is named anywhere in this repository**.
  Owner: **User Tester — Abt Hermann** with **System Architect — Feng Guo**.
- **unknown:** *Do any recorded fixture hashes exist?* `fixture-provenance.md:9`–`:13`
  records "artifact hash unavailable" for every row. The synthetic generators are
  byte-deterministic (`datara/tests/test_storage.py:335`), so a hash *could* now be
  recorded, but recording one is a registry-adjacent change and is not mine.
- **unknown:** *Is the FIX02–FIX04 upstream sample family usable at all?* Owner:
  **founder**. Until answered, no upstream binary may be copied into the repository, and
  the suite's current all-synthetic posture is the correct one.

**No fixture oracle exists for any range in the mapping matrix.** This is
`fit-support-matrix.md:228` and it is the single largest obstacle to TC19: a range with no
fixture has no independent check that the code's reading of it is right.

---

## 3. STK003 — records and fields the code reads, mapped to evidence

Requirement: **SR01**, **SR02**, **SR27**. Oracle: **TC01**, **TC19**.

### 3.1 Messages and field definition numbers the code names

All literals below are in `datara/classification.py:84`–`:107`. The "profile agrees"
column is my runtime observation of the pinned profile in this environment (§1.5), which
is why it is separated from the "evidenced by" column.

| Message / field | Constant | Literal | Consumed at | Evidenced by | Profile agrees |
| --- | --- | --- | --- | --- | --- |
| `file_id` (0) `type` (0) | `MESG_NUM_FILE_ID`, `FILE_ID_TYPE` | 0 / 0 | `:1043` | MAP01 (`fit-support-matrix.md:100`); pinned enum check `classification.py:316`–`:321` | yes — `file[4]=='activity'` |
| `activity` (34) `num_sessions` (1) | `ACTIVITY_NUM_SESSIONS` | 1 | `:1084` | MAP01 (`fit-support-matrix.md:110`) | yes |
| `activity` (34) `type` (2) | `ACTIVITY_TYPE` | 2 | `:1085`, used `:1110` | MAP01 (`fit-support-matrix.md:111`) | yes — `0 manual`, `1 auto_multi_sport` |
| `session` (18) `start_time` (2) | `SESSION_START_TIME` | 2 | `:1183` | MAP01, MAP04 (`fit-support-matrix.md:103`) | yes — `date_time`, scale 1 |
| `session` (18) `sport` (5) | `SESSION_SPORT` | 5 | `:1156` | MAP01 (`fit-support-matrix.md:101`) | yes |
| `session` (18) `sub_sport` (6) | `SESSION_SUB_SPORT` | 6 | `:1242` | MAP01 (`fit-support-matrix.md:102`) | yes |
| `session` (18) `total_elapsed_time` (7) | `SESSION_TOTAL_ELAPSED_TIME` | 7 | `:1204` | MAP01, scale 1000, units `s` (`fit-support-matrix.md:104`) | yes |
| `session` (18) `total_timer_time` (8) | `SESSION_TOTAL_TIMER_TIME` | 8 | `:1230` | MAP01, scale 1000, units `s` (`fit-support-matrix.md:105`) | yes |
| `session` (18) `total_distance` (9) | `SESSION_TOTAL_DISTANCE` | 9 | `:1236` | MAP01, scale 100, units `m` (`fit-support-matrix.md:106`) | yes |
| `record` (20) — **no field is read** | `MESG_NUM_RECORD` | 20 | counting only, `:804`–`:805` | MAP01 | yes |
| header `size` / `protocol_version` / `profile_version` / `data_size` / signature | — | byte offsets 0,1,2–4,4–8,8–12 | `:631`–`:635` | MAP03 (`fit-support-matrix.md:15`) | n/a |

### 3.2 The `record` message: captured wider than it is read

**established:** `_scan` captures a raw value for any field whose definition number is in
`(0, 1, 2, 3, 5, 6, 7, 8, 9, 253)` — `datara/classification.py:793`. Applied to message
20 that captures `position_lat` (0), `position_long` (1), `altitude` (2), `heart_rate` (3),
`distance` (5), `speed` (6), and `timestamp` (253), and — for whatever messages define
those numbers — fields 7, 8, 9.

**established:** **none of those captured `record` values is ever read.** `_field()` is
called only for `(0,0)`, `(34,1)`, `(34,2)`, `(18,2)`, `(18,5)`, `(18,6)`, `(18,7)`,
`(18,8)`, `(18,9)` — `datara/classification.py:1043`, `:1084`, `:1085`, `:1156`, `:1183`,
`:1204`, `:1230`, `:1236`, `:1242`. The captured `record` values are therefore written
into `StructureScan.raw_fields` and discarded.

Two consequences, both stated as findings rather than fixes:

- The capture list at `:793` is broader than any read. Field 4 (`cadence`) is the one
  `record` field the capture list omits. Whether that omission is deliberate is not
  recorded anywhere. **unknown:** *is the `:793` capture list intended to enumerate the
  supported `record` fields, or is it an over-broad placeholder?* Owner: **System
  Architect — Feng Guo**. It changes no behaviour today, because nothing reads the values.
- Because no `record` field is read, `Activity.heart_rate_value`, `Activity.gps_point_count`
  and `Activity.record_sample_count` **cannot** be derived from a FIT file by this code.
  They are written only from a caller-supplied normalized object
  (`datara/db.py:256`–`:261`), and `datara/normalization.py` does not read FIT either — it
  validates a supplied shape. This is consistent with `fit-support-matrix.md:107`–`:119`,
  which defers every `record`-derived cell, so it is **not** a divergence. It does mean
  the persisted optional columns have no FIT-derived producer, which is worth stating.

### 3.3 The decoded record count is a message count, and it does not reach persistence

**established:** `record_sample_count` is the number of messages whose global number is 20
(`datara/classification.py:804`–`:805`, carried at `:813`). It is **not** a count of samples
in any other sense, and the field name is the only thing suggesting otherwise.

**established:** it is used only for the per-file sample limit (`:1034`), the
no-samples warning (`:1250`) and the reason text (`:1265`). It is **not** passed into any
persistence call.

**established:** `Activity.record_sample_count` is written from
`normalized.record_sample_count` (`datara/db.py:258`), i.e. from a caller-supplied value,
and `datara/intake.py:225` sets its own `record_sample_count=0` on the resource-limit
outcome. No production path connects the classifier's count to the column.

**unknown:** *Should the FIT-decoded `record` message count be the value persisted as
`Activity.record_sample_count`, and if so under what name and unit?* Owner: **System
Architect — Feng Guo**. This matters because the persisted column currently cannot be
traced back to the source file.

### 3.4 Canonical forms the code produces, against the matrix's declared canonical fields

This is where the code and the recorded canonical forms diverge most, so every divergence is
stated rather than reconciled.

| Source field | Matrix canonical field and type (`fit-support-matrix.md`) | What the code actually produces | Agreement |
| --- | --- | --- | --- |
| `session` 18/2 `start_time` | `start_utc_seconds`, **integer** epoch seconds, `:103` | `start_time_utc`: an **ISO-8601 string**, `datara/classification.py:1275` via `:848`–`:858` | **Divergence in form.** The integer form exists, but only later and separately, inside the tuple: `canonical.py:241`–`:256` converts the string to integer epoch seconds. The persisted form is a `DateTimeField` (`datara/models.py:361`), not an integer. |
| `session` 18/7 `total_elapsed_time` | `elapsed_ms`, **integer** milliseconds, `:104` | `elapsed_duration_ms`: the raw value passed through `require_elapsed_duration_ms` (`:1281`–`:1285`), **and** `elapsed_duration_seconds`: a decimal **string** (`:1286`) | **Agreement on the integer millisecond form.** The string form is additional, not contradictory, but it is what `ImportPlan.accepted()` reports (`datara/intake.py:189`). |
| `session` 18/8 `total_timer_time` | `timer_ms`, **integer** milliseconds, `:105` | `timer_duration_seconds`: `_exact_scaled(timer.raw, 1000)` — a **decimal seconds string**, `:1287` | **Divergence, and a persistence-blocking one.** `Session.timer_duration_seconds` is an integer column (`datara/models.py:363`). `_exact_scaled` renders the exact quotient to three decimal places, so a raw `1800500` yields `"1800.500"` (verified at runtime), which cannot be written to an integer column without a conversion that **no recorded decision specifies** — I checked `decision-register.md` §3 (`:90`–`:110`) and the proposal matrix declares only the source-typed form, not a persisted one. **unknown:** *What is the canonical form and integer representation of `total_timer_time` for persistence?* Owner: **System Architect — Feng Guo**. |
| `session` 18/9 `total_distance` | `distance_cm`, **integer** centimetres, `:106` | `total_distance_metres`: `_exact_scaled(distance.raw, 100)` — a **decimal metres string**, `:1288`–`:1290` | **Divergence.** Units differ (metres vs centimetres) and representation differs (decimal string vs integer). `Activity.distance_value` is an integer column with a separate `distance_unit_code` (`datara/models.py:298`–`:299`), so the mapping is undefined. **unknown:** *Which integer representation and unit code does `total_distance` persist as?* Owner: **System Architect — Feng Guo**. |
| `session` 18/5 `sport` | integer enum `{1,2}`, `:101` | `sport_name` is the **string** name (`classification.py:1171`); `sport_raw` keeps the integer | **Divergence in what is carried.** `Session.sport` stores the string (`datara/dedup.py:876` uses `sport_name(...)`), and the tuple converts back via `canonical_sport_code` (`datara/canonical.py:178`–`:203`). `fit-support-matrix.md:101` types the canonical value as *"integer enum"* and `:96` states *"Canonical types are integers by design"*. The integer comparison is correct; the persisted column is a display string. **unknown:** *Is a display string acceptable in `Session.sport`, given the matrix names the integer as canonical?* Owner: **System Architect — Feng Guo**. |
| `session` 18/6 `sub_sport` | integer enum plus `indoor_outdoor`, `:102` | `sub_sport_raw` and `sub_sport_name` are carried (`:1270`–`:1271`); **no indoor/outdoor value is computed anywhere** | **Required but absent** — see §3.5. |

### 3.5 Sub-sport: **D-A1 and D-A3 are not implemented**, and the gap is larger than "absent"

**D-A1** (`decision-register.md:94`, Author: **System Architect — Feng Guo**, recorded
3 October 2026) freezes the sub-sport allowlist and **D-A3** (`:98`) requires that an
unknown, unassigned or **cross-sport** sub-sport is *"accepted with disclosure and never
rejected"*, under four stable codes including `SUBSPORT_SPORT_MISMATCH`. **D-A2** (`:96`)
adds `SUBSPORT_ALL_GOALS_ONLY` and `SPORT_ALL_GOALS_ONLY` for `254 all`. **None of that
exists in the code.** I verified this at runtime, not by grep alone:

- `datara.classification` has **no** `REASON_SUBSPORT_ALL_GOALS_ONLY`,
  **no** `REASON_SPORT_ALL_GOALS_ONLY` and **no** `WARN_SESSION_COUNT_UNDECLARED`
  attributes. (`decision-register.md:96` requires the first two; `SESSION_COUNT_UNDECLARED`
  is required by the proposed matrix at `fit-support-matrix.md:477`, so that one is a
  proposal-stage item, not a decision-stage one.)
- The literal `254` appears **nowhere** in `datara/`.
- The only sub-sport warning is `WARN_SUB_SPORT_NOT_IN_SCOPE`, raised at
  `datara/classification.py:1247`–`:1248` when `sub_sport_name(raw) is None`.

That last point is the substantive finding, and it is **a missing-evidence gap rather
than a wrong-but-fixable predicate**. The predicate is *"the pinned profile has no
name for this value"*. D-A3's rule is *"this value is not assigned to this
sport"*. Those are different predicates, and the second is strictly broader.
Concretely: for `sport = running` with `sub_sport = 7 road`, the pinned profile **does**
name `7` as `road` (verified at runtime), so `sub_sport_name(7)` is not `None` and **no
warning is emitted at all**. The athlete's activity is accepted with a road sub-sport on
a running activity and no disclosure. **D-A3 names this exact case and gives it a code.**

**Where the relation comes from — corrected twice.** An earlier revision of this section
said the rule was **not implementable from available evidence** and re-owned the
item to the founder. **That was wrong, and it deleted the evidence that made the
original finding correct.** The revision after that asserted the relation on
`fit-support-matrix.md` as *"the approved record"*, which that file denies at `:1` and
`:3`. **The authority is D-A1.**

The pinned SDK profile's `sub_sport` map is indeed **112 entries, all plain strings,
carrying no sport association** — that part is verified and still stands. But the
relation **is** available, in this repository, under a recorded decision:

- **`decision-register.md:94` (D-A1)** states the partition as **9** assigned to `sport`
  1 `running`, **19** to `sport` 2 `cycling`, one shared (`0 generic`), **84** to
  neither, and `254`, on pinned `profile.py` bytes **SHA-256-verified against MAP01
  before any value was read** (`cfc2737…865c`, 967399 bytes, match), with the enums
  **parsed, never imported**. That is the authoritative assignment, and its evidence
  basis is stated in the decision itself.
- D-A1 also **corrects the proposal record** where they differ: the matrix *"had
  approved only 6 cycling values and had silently dropped 11 cycling-tagged
  sub-sports"* the publisher assigns to cycling, `track_cycling` 13, `bmx` 29,
  `commuting` 48 and `e_bike_enduro` 127 among them. Where the two disagree, **D-A1
  governs and the matrix is the superseded draft.**
- The proposed matrix's §12.2 (`fit-support-matrix.md:318`–`:371`) tabulates the same
  partition — 9 running (`:322`–`:334`), 19 cycling (`:336`–`:358`), 84 to neither
  (`:369`), completeness identity `9 + 19 − 1 + 84 + 1 = 112` (`:371`) — and `:223`
  marks it *"Authoritative for Milestone A"*, `:487` permits implementing it *"without
  inventing anything"*. **These are corroboration, not the authority**, and the matrix's
  own title says **"Proposed"**.

So `sub_sport = 7 road` is in the cycling set and not the running set, and the
cross-sport case is **directly decidable** from D-A1's recorded partition.
**This is an implementation gap against a recorded architecture decision, not a
capability gap and not a founder question.** Owner: **System Architect — Feng Guo**
as code owner. The gap is in code this document's author is not permitted to edit.

The precise, narrower statement: the relation is **not derivable from the SDK
profile alone** — the profile carries no sport association — but it **is** supplied
by D-A1's frozen partition. Both halves are needed; either alone would
mislead.

- **established:** the predicate, its location, the absence of the three codes; that
  the pinned profile carries no sport↔sub_sport relation; **and** that D-A1 supplies
  that relation as a recorded decision on SHA-256-verified bytes.
- **Implementation gap against a recorded decision:** `decision-register.md:98` (D-A3)
  requires disclosure for exactly the cross-sport case — *"Four distinct causes, four
  stable codes, all resolving to `null` with the raw value retained:
  `SUBSPORT_ABSENT`, `SUBSPORT_INVALID`, `SUBSPORT_SPORT_MISMATCH`,
  `SUBSPORT_UNMAPPED`"* — and `:96` (D-A2) requires `SUBSPORT_ALL_GOALS_ONLY` for
  `sub_sport = 254`. Neither happens. `SUBSPORT_SPORT_MISMATCH` has **zero occurrences**
  in `datara/`. The proposed matrix states the same requirement at
  `fit-support-matrix.md:412`–`:414` and `:415`. On the decision register as it stands
  this is an **implementation gap, not an open product question**. Owner:
  **System Architect — Feng Guo**. The separate question of
  whether `sport = 254` and `sub_sport = 254` each deserve a dedicated rejection code
  is unaffected and remains as recorded below, owned by **founder** for the codes.

### 3.6 Session cardinality: three of the four matrix outcomes are not distinguishable today

- **established:** observed count `0` → `missing_session` (`datara/classification.py:1089`–`:1098`); count `> 1` and `activity.type == 1` **both** → the single code `multisport_or_chained_layout` (`:1099`–`:1122`).
- **Divergence, already reported by the matrix and still open:** `fit-support-matrix.md:483` states the collapse explicitly, and `:481` marks `MULTISESSION_UNSUPPORTED` as "**split required**". The code still collapses multisession count with declared multisport type. Owner: **System Architect — Feng Guo**.
- **established:** the declared/observed cross-check is `declared_sessions != 1` (`:1123`), which `fit-support-matrix.md:461` correctly notes is equivalent only because the observed count is already forced to 1. The matrix's own preferred form is `declared == observed`.
- **Divergence:** `fit-support-matrix.md:453`–`:454` defines two distinct uncorroborated states (activity message absent vs `activity` present with `num_sessions` absent or `0xFFFF`), requiring `ACTIVITY_MESSAGE_ABSENT` and `SESSION_COUNT_UNDECLARED`. The code emits **one** warning, and only when *both* `activity.num_sessions` and `activity.type` are absent (`datara/classification.py:1138`–`:1144`). A file carrying `activity.type = manual` with no `num_sessions` produces no disclosure at all. This is the disclosure gap `fit-support-matrix.md:459` already recorded and called "in code that is not mine to change". It is still open.
- **unknown:** *Should `num_sessions == 0` be treated as undeclared (matrix case B) or as a contradiction (matrix case C)?* The matrix's case-C row reads "present, valid, and not equal to the observed count", and `0` is present and valid, so it reads as a contradiction today. Owner: **System Architect — Feng Guo**.

### 3.7 File-type exclusions: incomplete against the matrix's own correction

- **established:** `FILE_TYPE_EXCLUSIONS` has exactly six keys — `workout`, `course`,
  `schedules`, `monitoring_daily`, `weight`, `blood_pressure`
  (`datara/classification.py:446`–`:457`; verified at runtime).
- **established:** the pinned profile defines `15 monitoring_a` and `32 monitoring_b`
  (verified at runtime), plus `11 goals` and `20 activity_summary`.
- **Divergence, already reported by the matrix and still open:**
  `fit-support-matrix.md:425` requires **all five** monitoring/wellness categories to map to
  the wellness reason and names `monitoring_a` and `monitoring_b` as the two missing. They
  are still missing, so those two file types fall through to the generic
  `unsupported_file_type` — same rejection, wrong explanation. Owner: **System Architect —
  Feng Guo**.
- **unknown, and correctly left open by the matrix:** *Which reason should `goals` (11) and
  `activity_summary` (20) receive?* `fit-support-matrix.md:427` records both as open rather
  than decided, and no code or record decides them. Owner: **founder**.

### 3.8 Reason and warning code vocabulary: two vocabularies coexist

The matrix publishes uppercase codes (`fit-support-matrix.md:182`–`:212`:
`SESSION_ABSENT`, `CHAINED_FILE_UNSUPPORTED`, `DECODER_UNSUPPORTED_COMPRESSED_TIMESTAMP`,
`FILE_TYPE_UNDETERMINED`, `REQUIRED_FIELD_*`, `OPTIONAL_FIELD_*`, `LIMIT_*`). The code
publishes lowercase snake codes (`datara/classification.py:117`–`:231`:
`missing_session`, `chained_file_layout`, `compressed_timestamp_unsupported`,
`missing_file_id`, `missing_required_*`, `file_size_limit_exceeded`, …). I listed the
live set at runtime; it has 34 rejection codes and 10 warning codes.

- **established:** the two vocabularies differ in case *and* in membership. Comparing the
  matrix's §5 code list against the live code set, **26 of the 29 uppercase matrix codes
  have no name-level counterpart at all** in the code, including `SESSION_ABSENT`,
  `MULTISESSION_UNSUPPORTED`, `MULTISPORT_UNSUPPORTED`, `FILE_TYPE_UNDETERMINED`,
  `CHAINED_FILE_UNSUPPORTED`, `DECODER_UNSUPPORTED_COMPRESSED_TIMESTAMP`, the whole
  `REQUIRED_FIELD_*` family, the whole `OPTIONAL_FIELD_*` family, the whole
  `SUBSPORT_*` family and the whole `LIMIT_*` family. Cases such as `MALFORMED_FIT` and
  `INTEGRITY_FAILED` are also split differently: the matrix has two codes, the code has
  `malformed_file_header`, `malformed_structure`, `undefined_base_type`,
  `header_crc_invalid`, `file_crc_invalid`.
- **established:** two of the matrix's `LIMIT_*` codes describe limits that the code
  declares but never enforces. `fit-support-matrix.md:205`–`:206` name
  `LIMIT_WALL_TIME_EXCEEDED` (60 s) and `LIMIT_MEMORY_EXCEEDED` (512 MiB);
  `datara/intake.py:72`–`:73` declare `MAX_FILE_WALL_SECONDS = 60` and
  `MAX_FILE_MEMORY_MIB = 512`, and `datara/tests/test_classification.py:904`–`:905` assert
  the two constant values — but a repository-wide search finds **no use of either constant
  as a limit**. `plan_import` (`datara/intake.py:240`–`:250`) accepts byte, file-count,
  batch-byte, message and sample-record limits only; there is no wall-time or memory
  parameter, and neither string appears anywhere in `datara/classification.py`. The only
  enforced limits are file bytes, batch file count, batch bytes, message count and sample
  record count (`datara/intake.py:319`, `:333`, `:294`, and `classification.py:1027`,
  `:1034`). **Required but absent.**
- **unknown:** *Which vocabulary is the public diagnostic contract that TC01 and SR32 oracles
  assert against?* `datara/classification.py:112`–`:116` states the code's set is a frozen
  contract, and `datara/tests/test_classification.py:516`–`:529` asserts every reason
  produced is in the frozen set — so the **code's** vocabulary is the one with a test. But
  TC01 and TC21 are written against the matrix. Owner: **System Architect — Feng Guo**. I am
  not proposing a rename; renaming would break the suite and the frozen-code claim.
- **unknown:** *Should the wall-time and memory limits be enforced, and if so by what
  mechanism?* The byte and count limits are declared (`datara/intake.py:29`–`:31`) and the
  wall-time and memory limits are declared as bare constants (`datara/intake.py:72`–`:73`,
  under no stated policy prose), asserted as
  constants (`datara/tests/test_classification.py:904`–`:905`) but never applied, and
  `datara/classification.py:986`–`:988` states the design intent that such limits belong to
  "a resource-isolated worker" that enforces them separately. No such worker exists in this
  repository. Owner: **System Architect — Feng Guo**.

---

## 4. STK004 — timestamps, units, null handling and integrity, as implemented

Requirement: **SR02**, **SR27**. Oracle: **TC01**, **TC19**.

This section records what the code does. Where a bound's *provenance* is not in this
repository, that is a separate **unknown** with a founder owner.

### 4.1 Timestamp handling

| Step | Behaviour | Evidence |
| --- | --- | --- |
| Raw `start_time` is a `date_time` | compared against the pinned minimum `268435456`; a value below it is rejected | `datara/classification.py:107`, `:1194`–`:1202` |
| Raw → UTC | `raw + 631065600`, integer arithmetic, rendered with `datetime.fromtimestamp(..., tz=utc)` and a `Z` suffix | `datara/classification.py:848`–`:858` |
| Offset provenance | the constant `631065600` is present in the pinned SDK at `util.py:18` and used at `util.py:25` (verified at runtime, §1.5) | also recorded in the proposed matrix at `fit-support-matrix.md:16`, `:53` and `:103` |
| String → canonical integer | `start_epoch_seconds_from_utc_text` parses the `…Z` form; `start_epoch_seconds_from_datetime` **refuses a non-zero microsecond rather than truncating** | `datara/canonical.py:241`–`:273` |
| Persisted form | `Session.session_start_utc` is a `DateTimeField` | `datara/models.py:361` |
| Snapshot scope form | half-open `[start, end)`, both bounds must be aware | `datara/dedup.py:1301`–`:1306` |

**established:** the sub-second refusal is real and tested
(`datara/tests/test_conflict.py:465`, `datara/canonical.py:251`–`:255`).

**Divergence, and it is a missed check rather than an extra one:** the matrix gives
`start_time` a valid range of `899501056` – `4926032894`
(`fit-support-matrix.md:103`). `899501056` is `268435456 + 631065600`, i.e. the same lower
bound in epoch seconds, so the lower bound agrees. **The upper bound is not enforced.**
`datara/classification.py:1194` tests only `start.invalid or start.raw < DATE_TIME_MIN`.
There is no upper-bound test anywhere. **Required but absent.** Owner: **System Architect —
  Feng Guo**. Note that the matrix itself labels these bounds "**Derived, not
  protocol-evidenced**" (`fit-support-matrix.md:226`) and instructs that they be treated as
  engineering validation, never as conformance — so enforcing the upper bound is an
  engineering-validation choice, not a protocol claim.

### 4.2 Duration units

| Fact | State | Evidence |
| --- | --- | --- |
| The one canonical comparison unit is `integer_milliseconds` | **established** | `datara/canonical.py:66` |
| `require_elapsed_duration_ms` refuses a wrong declared unit, a `bool`/`float`/`str`, and out-of-domain values | **established** | `datara/canonical.py:86`–`:137` |
| The unit is **declared by the caller and checked, never inferred** | **established** | `datara/canonical.py:26`–`:43` (prose) with the enforcement at `:108`, `:117`, `:124`, `:131` |
| `elapsed_duration_ms_from_seconds` is the only sanctioned seconds→ms crossing | **established** | `datara/canonical.py:140`–`:164`; used at `datara/db.py:278`–`:291` and `datara/normalization.py` |
| The raw FIT value is already the millisecond count (scale 1000), so no rescaling happens | **established** | `datara/classification.py:1276`–`:1285`; profile agrees (`total_elapsed_time`, scale 1000, units `s`) |
| Elapsed and timer are never written from one another | **established** | `datara/models.py:331`–`:334` (prose) with separate columns at `:297`, `:363` and separate write sites `datara/db.py:255`, `:292`, `datara/dedup.py:879` |

### 4.3 The duration bounds: enforced in code and in the database, provenance not in this repository

This is the most important STK004 finding, because it is an enforced threshold whose origin
I cannot trace.

- **established:** the accepted domain is `1000 … 86_400_000` ms.
  `datara/canonical.py:75` (`MIN_ELAPSED_DURATION_MS = 1000`) and `:79`
  (`MAX_ELAPSED_DURATION_MS = 86_400_000`).
- **established:** the same domain is a **database** `CheckConstraint` on
  `Session.elapsed_duration_ms` — `datara/models.py:378`–`:384`, materialised in the
  migration at `datara/migrations/0001_initial.py:111`.
- **established, and this contradicts the comment above it:** `datara/canonical.py:77`–`:78`
  justifies the maximum as *"matching the normalization policy default of 24 hours
  expressed in milliseconds"*. I searched `datara/normalization.py` for `86400`, `86_400`
  and "24 hour": **no match.** The policy's `max_elapsed_duration_seconds` is a
  caller-supplied field (`datara/normalization.py:265`, `:277`, `:452`, validated only for
  positivity at `:461`). **There is no 24-hour default in this repository.** The stated
  justification for an enforced database constraint is therefore unsupported.
- **Divergence from the proposed matrix, twice over — proposal stage, not a decision-stage
  obligation.** `fit-support-matrix.md:104` gives the Milestone A valid range as
  `1` – `4294967294`, and `:279` explicitly records the lower bound of `1` as "an
  engineering decision, not profile-derived … recorded as my decision for escalation".
  **That matrix is a proposal** (`:1`, `:3`), and `decision-register.md` records no
  decision fixing this domain, so this is **not** an implementation gap against a binding
  record — it is a divergence from a draft that the Architect may revise. The code enforces
  **1000** as the lower bound, not `1`. And the code enforces an **upper** bound of
  `86_400_000` that the matrix does not state at all; the matrix's upper bound is the full
  uint32 domain.

- **unknown:** *What is the accepted elapsed-duration domain, and what evidence or founder
  decision fixes it?* Three sub-questions, all for the **founder**:
  1. Is the lower bound 1 ms (matrix `:279`) or 1000 ms (code `canonical.py:75`)? The code
     comment at `:72`–`:74` argues 1000 on the grounds that "D01 requires a session's
     elapsed duration to be a positive whole number of seconds". That argument is about a
     *normalization contract in seconds*, not about the FIT raw field, which is
     millisecond-scaled and can legitimately be sub-second. **I am not asserting which is
     right.**
  2. Is there an upper bound at all, and if so what is it and on what evidence? A 24-hour
     cap on a single activity is a plausible engineering bound, but it is currently
     undocumented as a decision and its code comment cites a default that does not exist.
  3. Does the matrix's uint32 upper bound govern instead?

  I flag one further consequence for the same owner: because the lower bound is 1000 ms,
  a conforming FIT file with a sub-second `total_elapsed_time` is rejected outright, and
  because the upper bound is 24 h, a longer recording is rejected. Both are accept/reject
  outcomes that follow from numbers with no recorded provenance.

**Note on what I am not doing.** I have not proposed a value, and I have not changed the
code. The mismatch between the code's stated justification and the code's surrounding
repository is reported because it is an evidence defect under SR27, which requires every
"unit conversion, timestamp rule, integrity rule" to be traceable to pinned evidence.

### 4.4 Null handling

| Rule | Behaviour | Evidence |
| --- | --- | --- |
| Absent and present-but-invalid are **distinct causes** | tracked separately by `FieldValue.present` / `.invalid` | `datara/classification.py:463`–`:473` |
| The invalid sentinel is detected by **field size**, not by base-type name | `_is_invalid` compares against `0xFF` / `0xFFFF` / `0xFFFFFFFF` for sizes 1/2/4 and returns `False` for any other size | `datara/classification.py:824`–`:834` |
| Absent optional → null **plus a distinct warning**, never imputation | timer, distance, sub-sport each get absent/invalid warnings | `datara/classification.py:1229`–`:1248` |
| Null on a persisted column means "absent or invalid", never "imputed", and every null has a matching `quality_warnings` entry | **established as the stated contract** | `datara/models.py:294`–`:305` |
| The first occurrence of a `(message, field)` pair is kept, so a later session cannot overwrite the first | `_scan` guards with `not in raw_fields`; `_field` documents it | `datara/classification.py:793`–`:801`, `:837`–`:845` |
| An accepted classification with no logical tuple is an explicit raise, not an `assert` | `datara/intake.py:405`–`:411`; also `datara/classification.py:997`–`:1001`, `:603`–`:608` | — |

**unknown:** *Should a field whose declared size is not 1, 2 or 4 bytes be treated as
"not an invalid sentinel" or as "cannot be interpreted"?* `_is_invalid` returns `False` for
such sizes (`datara/classification.py:834`), i.e. the value is treated as valid. In
practice every field the code reads is `uint8`, `uint16` or `uint32`, so the branch is
unreached today. It is a latent behaviour with no recorded decision. Owner: **System
Architect — Feng Guo**.

### 4.5 Integrity rules, in the order the code applies them

Order is itself part of the contract and is stated at `datara/classification.py:876`–`:877`.

1. Decoder availability → `decoder_unavailable` (`:878`–`:883`)
2. Empty file → `empty_file` (`:884`–`:885`)
3. Shorter than a 12-byte header → `not_a_fit_file` (`:887`–`:891`)
4. `header_size` not 12 or 14 → `not_a_fit_file` (`:893`–`:898`)
5. Signature not `b".FIT"` → `not_a_fit_file` (`:899`–`:903`)
6. Structural walk (`_scan`) (`:905`)
7. Header CRC mismatch, **only when `header_size == 14`** → `header_crc_invalid` (`:910`–`:919`)
8. Declared content longer than the file → `malformed_file_header` (`:921`–`:928`)
9. File CRC mismatch → `file_crc_invalid` (`:930`–`:941`)
10. Bytes remaining after one segment → `chained_file_layout` (`:946`–`:953`)
11. Protocol major not in `(1, 2)` → `unsupported_protocol_version` (`:955`–`:963`)
12. Structural error from the walk → that error (`:965`–`:971`)

Then, in `classify_bytes`: compressed timestamp → whole-file rejection (`:1018`–`:1025`);
message and sample limits (`:1027`–`:1040`); then file category, cardinality, and required
semantics.

**established, integrity is reported and never repaired:** each CRC message says so in
place (`datara/classification.py:916`, `:938`), and no branch rewrites a byte.

**established, chained detection is byte-derived, not flag-derived:** the code deliberately
declines to use the protocol's header-level chained flag and derives a chain from trailing
bytes (`datara/classification.py:641`–`:653`). `fit-support-matrix.md:429`–`:431` confirms
this is correct and must not change, and records the residual limit: the rule "cannot speak
to a declared chain with no continuation". That limit is **still unclosed** and needs the
protocol document under §1.3.

**established, compressed timestamps reject the whole file:** `datara/classification.py:1018`
–`:1025`, and the pinned decoder genuinely raises (`decoder.py:347`–`:348`, verified at
runtime). Tested at `datara/tests/test_classification.py:404`–`:422`.

**Divergence from the proposed record, and it is a *missing* integrity rule — proposal
stage:** `fit-support-matrix.md:174`–`:175` lists "Integrity — whole-file integrity under
the pinned rules". `decision-register.md` records no decision requiring whole-file
integrity, so this rests on a proposal, not a binding record. The code verifies the **header** CRC only when the header carries one, and the
**file** CRC always. It does **not** verify that a 12-byte (no-CRC) header is legal in the
pinned profile beyond the size-byte check, and it does not apply any profile-level integrity
concept beyond CRC. **unknown:** *Is header-CRC-absent (12-byte header) unconditionally
acceptable, or does the pinned profile permit it only in defined circumstances?* The
protocol prose was never captured (§1.3), so this cannot be answered from the repository.
Owner: **System Architect — Feng Guo** for the evidence gap.

**established, and worth stating because it is easy to over-claim:** decoder success is
recorded as evidence only and can never lift a rejection
(`datara/classification.py:1311`–`:1318`, and `verify_with_pinned_decoder` is called *after*
every accept/reject branch has been decided, at `:1259`).

### 4.6 Integrity assumptions at the persistence layer

- **established:** original bytes are immutable in the accessor —
  `SourceObject.IMMUTABLE_FIELDS = ("digest", "byte_length", "storage_reference",
  "media_type")`, enforced in `save()` (`datara/models.py:242`, `:252`–`:261`),
  raising `ImmutabilityViolation`.
- **established:** the source chain has **no database trigger**. `datara/migrations/0001_initial.py`
  creates no trigger; `0002_saved_metric_graph.py:49`, `:70` and `:146` create triggers for
  the `Metric` graph only. So original-byte immutability is **application-enforced only**,
  while computed-metric immutability is **trigger-enforced**.
- **unknown:** *Is application-only enforcement sufficient for original bytes under SR03, or
  must the source chain carry database triggers like the metric graph does?* This is an
  architectural consistency question, not a product decision. Owner: **System Architect —
  Feng Guo**.
- **established:** `media_type` is in the immutable set (`datara/models.py:242`). Re-importing
  the same bytes with a *different* declared media type therefore raises
  `ImmutabilityViolation` at `save()` rather than being reported as a duplicate. Whether
  that is the intended behaviour for the exact-byte case is not recorded. Owner: **System
  Architect — Feng Guo**.

---

## 5. STK011 — exact-byte duplicate behaviour, traced through the implementation

Requirement: **SR04**. Oracle: **TC03**. Contract: `duplicate-conflict-options.md` §5
precedence table, `fit-support-matrix.md` §5 dispositions.

### 5.1 Already implemented

| # | Mechanism | State | Evidence |
| --- | --- | --- | --- |
| 1 | `Import` is unique on `(owner, source_digest, contract_version)` | **established** | `datara/models.py:214`–`:219`; `datara/migrations/0001_initial.py:48` |
| 2 | `SourceObject` is unique on `(owner, digest)` | **established** | `datara/models.py:247`–`:249`; `datara/migrations/0001_initial.py:65` |
| 3 | The digest is **claimed by inserting**, and the constraint arbitrates; the loser reads the winner's row inside a savepoint | **established** | `datara/dedup.py:658`–`:686` |
| 4 | P1 then P2 dispatch on an already-held original: published activity → `duplicate_of_existing`; quarantined candidate → `duplicate_of_quarantined` | **established** | `datara/dedup.py:689`–`:710` |
| 5 | On a repeat, `ingest` returns early with `created_original=False`, `created_activity=False`, and creates **no** `Import` row | **established** | `datara/dedup.py:754`–`:789`, returning at `:765` |
| 6 | An original with no activity and no quarantine (crash residue) is reported `duplicate_of_existing` with `UNREFERENCED_ORIGINAL`, creating nothing | **established** | `datara/dedup.py:712`–`:715`, `:760`–`:776` |
| 7 | The pure planner has the same rule, and treats an in-batch repeat as a duplicate | **established** | `datara/intake.py:384`–`:398` (`decided_by="exact_digest_duplicate"`), `:439` |
| 8 | After a lost response, the path **re-queries and never resubmits** | **established** | `datara/dedup.py:1160`–`:1210` |
| 9 | The byte layer is write-once and verified; a repeat writes nothing | **established** | `datara/dedup.py:748`–`:751`; `datara/storage.py:319` (`_read_and_verify`), `:338`, `:346` |
| 10 | P7 reports a superseded/deleted/unavailable reference and resurrects nothing, with wording identical to the cross-owner case | **established** | `datara/dedup.py:1213`–`:1230` |
| 11 | P6 needs no implementation, because rejected bytes leave no digest — stated as a boundary | **established as a documented boundary** | `datara/dedup.py:44`–`:51`, `:128`–`:134`; P6 is reachable only via `resolve_uncertain` at `:1176`–`:1185` |
| 12 | No cross-owner disclosure: every lookup is `for_owner(owner_id)` scoped | **established** | `datara/dedup.py:685`, `:695`, `:704`, `:1174`, `:1223`; tested `datara/tests/test_conflict.py:499` |
| 13 | Idempotence under concurrency is enforced by the constraint, not a read-then-write | **established in code** | `datara/dedup.py:666`–`:671`; **see §5.3 for what is not exercised** |

### 5.2 Required but absent

**This is the finding that matters most in STK011, and it is structural.**

- **established:** the two halves of intake are not connected. `SessionFacts` — the type
  `dedup.ingest` requires (`datara/dedup.py:723`) — is **constructed nowhere in
  `datara/`**. The only construction in the repository is a test helper at
  `datara/tests/test_conflict.py:85`.
- **established:** the only production importer of `datara.classification` is
  `datara/intake.py:50`. `datara/dedup.py` imports `datara.models`, `datara.storage` and
  `datara.canonical` (`datara/dedup.py:82`–`:108`) and **never imports the classifier**.
- **established:** `datara.intake` is a pure planner — it performs no I/O and persists
  nothing (`datara/intake.py:267`–`:268`). `datara.dedup` is the persisting state machine.

Consequence: **there is no end-to-end path from submitted bytes to a persisted duplicate or
conflict disposition.** A real file would go `classify_bytes` → `FileClassification`
(`datara/classification.py:976`), and then nothing converts that into `SessionFacts` for
`ingest`. The exact-byte duplicate rules in §5.1 are implemented and unit-tested, but
they are tested against hand-constructed facts, not against decoded bytes.

- **unknown:** *What is the contract for converting an accepted `FileClassification` into
  the persistence input — specifically, which representation of `total_timer_time` and
  `total_distance` crosses the boundary, given §3.4 found no integer form for either?*
  Owner: **System Architect — Feng Guo**.
- **unknown:** *Which layer owns the byte→disposition composition — `datara.intake`'s plan,
  `datara.dedup`'s state machine, or a third coordinator?* Owner: **System Architect —
  Feng Guo**.
- **established, and worth flagging as a boundary risk:** `OwnerScopedStore.record_import`
  (`datara/db.py:209`–`:230`) takes a caller-supplied `source_digest` and forwards it
  straight to `Import.objects.create` with no uniqueness handling. A caller using that
  method directly, rather than `dedup.ingest`, meets the unique constraint as an
  unhandled `IntegrityError`. Whether that is acceptable depends on the composition
  question above. Owner: **System Architect — Feng Guo**.
- **Divergence in owner representation, minor but real:** the planner's owner component is a
  `str` (`owner_key`, `datara/intake.py:240`, `:270`) while the persisting state machine's
  is an `int` id (`datara/canonical.py:373`–`:384`). Two representations of the scoping
  component of the same key. Owner: **System Architect — Feng Guo**.
- **unknown:** *Must a repeat submission with a different declared `media_type` be a
  duplicate or an error?* See §4.6. Owner: **System Architect — Feng Guo**.

### 5.3 What the tests do and do not establish about concurrency

- **established, declared by the suite itself:** `datara/tests/test_conflict.py:11`–`:18`
  records that the suite ran on SQLite as a declared deviation, that PostgreSQL 17 was
  absent from that host, that the *concurrent* interleaving section 8.1 describes depends on
  MVCC and on the constraint being immediate, and that **the multi-connection race is not
  exercised and is not claimed**.
- **established:** the single-writer path is covered, including replay after a simulated
  lost response (`datara/tests/test_conflict.py:171`), lookup of uncommitted bytes (`:204`),
  and "never accepted twice" (`:740`).
- **unknown:** *Does the `(owner, digest)` constraint arbitrate correctly under two
  concurrent PostgreSQL connections?* This needs a two-connection test on PostgreSQL 17.5
  and is not a product decision. Owner: **User Tester — Abt Hermann** with **System
  Architect — Feng Guo**.

I could not execute the suite in this environment: `psycopg` and `django` are not importable
under this interpreter, and `scripts/milestone_a.ps1` cannot run because it requires Python
3.12.14 exactly, which has no official Windows build. **No test result is claimed anywhere
in this document.** The 316/316 baseline at `9a1693b` on PostgreSQL 17.5 is the
coordinator's recorded baseline, not something I reproduced.

---

## 6. STK012 — unresolved logical-conflict examples against what the code does today

Requirement: **SR04**, **SR33**. Oracle: **TC03**. Contract: `duplicate-conflict-options.md`
§5–§9; examples at `duplicate-conflict-options.md:31`–`:42`.

### 6.1 The conflict key, as implemented

- **established:** the tuple is `(owner_id, sport_code, start_epoch_seconds,
  elapsed_duration_ms)` — `datara/canonical.py:219`–`:227`
  (`IDENTITY_COMPONENTS`, `TUPLE_COMPONENTS`), and `datara.dedup.assert_no_tolerance_parameters`
  re-checks the key against `TUPLE_COMPONENTS` so it cannot be widened
  (`datara/dedup.py:487`–`:527`, key check at `:518`).
- **established:** `sub_sport` is deliberately **not** a component, so a re-export that
  changed only sub-sport still conflicts (`datara/canonical.py:216`–`:223`, persisted at
  `:346`; `datara/dedup.py:124`–`:126`).
- **established:** comparison is exact — an exact aware-datetime equality in the database
  plus integer sport and integer millisecond equality in Python, with no range predicate
  and no rounding (`datara/dedup.py:560`–`:617`, specifically `:583`–`:603`).
- **established:** there is no tolerance parameter to configure, and that is machine-checked
  by introspecting every public callable and by scanning this module's own AST for
  ordering or approximation operators (`datara/dedup.py:398`–`:527`).
- **established:** P4 is tested **before** P3, deliberately, and the reason is recorded:
  otherwise a re-export would create a fresh candidate every time
  (`datara/dedup.py:802`–`:820`).
- **established:** a quarantined candidate is excluded from history by construction, not by
  a filter a caller might forget (`datara/dedup.py:1238`–`:1253`), and from snapshots with a
  visible exclusion entry naming the reason (`datara/dedup.py:1314`–`:1319`, `:1346`–`:1355`).
- **established:** no merge is an outcome of the state machine at all — no branch combines
  fields of two originals (`datara/dedup.py:29`–`:31`).
- **Divergence from the proposed record:** `duplicate-conflict-options.md:120` records
  **OQ-1**: "P3 fires against an accepted activity even after a 'retain both'
  resolution." That record is *"proposed research output"* (`:3`) and it records an
  **open question**, so it binds nothing.
  Since no resolution can be recorded (§6.2), this is currently unreachable rather than
  wrong. It becomes live the moment a resolution is implemented.

### 6.2 Resolution: required by the contract, entirely absent from the code

This is the clearest "required but absent" in STK012.

- **established, required:** three explicit owner resolutions — keep existing, replace via
  auditable supersession, retain both — are specified as the only authorized state changes
  at `duplicate-conflict-options.md:158`, with supersession lineage at `:159`, and as
  worked examples in the STK012 table at `:37`–`:39`.
- **established, the schema anticipates it:** `Quarantine.RESOLUTION_CHOICES` has the three
  values and `resolution` / `resolved_at` are nullable columns
  (`datara/models.py:571`–`:575`, `:592`–`:593`; `datara/migrations/0001_initial.py:177`–`:178`).
- **established, no code ever writes one:** the only two writes of a `Quarantine` row set
  `resolution=None, resolved_at=None` — `datara/dedup.py:1001`–`:1002` (P3) and
  `datara/dedup.py:1103`–`:1104` (P4). A repository-wide search for `STATE_RESOLVED`
  returns **no assignment anywhere**: the constant is declared
  (`datara/models.py:569`) and used only in a `choices` list.
- **established, supersession has no representation:** searching `datara/` for "supersed"
  returns only docstring prose (`datara/dedup.py:23`, `datara/storage.py:14`,
  `datara/dedup.py:1214`) and the *string* `replace_via_supersession` in the choices tuple.
  There is no supersession entity, no lineage column, no transition, and no function.
- **established, "retain both" has no semantics:** with no resolution record there is
  nothing that would stop P3 re-firing, which is exactly the risk
  `duplicate-conflict-options.md:39` flags ("prevent unchanged repeated submissions from
  silently creating more accepted copies").

So the three STK012 resolution examples — keep existing, replace, retain both
(`duplicate-conflict-options.md:37`–`:39`) — are **entirely unimplemented**, and OQ-1,
supersession lineage, interrupted-resolution recovery and the `Quarantine` state machine
are consequently **unreachable**. This is a large, coherent gap rather than a set of small
defects, and it is the honest answer to "what does the code do today": it creates a
quarantine and stops.

- **unknown:** *What is the authorized resolution contract — the transition set, the
  atomicity boundary, what happens to snapshots that referenced the superseded activity,
  and what a repeat submission does after each resolution?* The record asks the question
  (`duplicate-conflict-options.md:37`–`:40`, `:156`–`:159`) and does not answer it. Owner:
  **founder** for the resolution outcomes a user may choose; **System Architect — Feng Guo**
  for the transaction and lineage mechanism.
- **unknown:** *Is `Quarantine.state = 'resolved'` reachable by any path at all today?* No
  writer exists (§above), so the state is declared and unreachable. Whether the field
  should exist before a resolution contract does is an architectural question. Owner:
  **System Architect — Feng Guo**.

### 6.3 The unresolved conflict examples, compared against the code

The examples at `duplicate-conflict-options.md:35`–`:40`, each compared with what the code
does now.

| Example | Selected direction | What the code does today | State |
| --- | --- | --- | --- |
| A/X and A/Y differ in bytes, exact tuple equal | quarantine Y; exclude from normal history and skill snapshots | `find_exact_tuple_matches` → P3 → new `SourceObject` + `Activity(disposition=quarantined)` + `Quarantine` row in one transaction; excluded from `history()` and from `build_snapshot_scope` with a named exclusion | **already implemented** (`datara/dedup.py:941`–`:1026`, `:1238`–`:1253`, `:1314`–`:1355`); tested `datara/tests/test_conflict.py:223`, `:254` |
| Tuple differs | no match from this heuristic; import only if other checks pass; no comprehensive dedup claim | P5 accepts, with detail text stating that no duplicate claim is made | **already implemented** (`datara/dedup.py:892`–`:939`, detail at `:936`); tested `datara/tests/test_conflict.py:125` |
| Keep existing | owner explicitly resolves for existing history | **no resolution path exists** | **required but absent** |
| Replace | auditable supersession, preserve originals and lineage | **no supersession representation exists** | **required but absent** |
| Retain both | owner explicitly chooses both; repeats must not silently multiply | **no resolution path; P3 re-fires on every re-export** | **required but absent** |
| Concurrent / interrupted resolution | only authorized owner actions alter state; interruption must be recoverable | **no resolution state to interrupt**; concurrency beyond the byte layer is not exercised (§5.3) | **required but absent** |

**STK012's own acceptance criterion is satisfied by the above:** each example's competing
outcomes are stated and none is resolved here, and **no tolerance threshold is encoded** —
the tolerance key is empty and machine-checked (`datara/dedup.py:442`–`:527`).

### 6.4 Presentation: partially implemented

- **established:** `outcome_text` exists (`datara/dedup.py:1383`) and there is a test
  asserting the three states carry required content and no prohibited wording
  (`datara/tests/test_conflict.py:573`).
- **unknown:** *Is `outcome_text` the complete athlete-facing contract for TC22 / SR33, and
  is it wired to any presentation surface?* `duplicate-conflict-options.md:161`–`:186`
  assigns wording to TC22/UI-SR02 and leaves layout to UI Designer and User Tester. No
  dashboard or API module exists in this repository to consume it. Owner: **User Tester —
  Abt Hermann** with **UI Designer — Wu Yunzhou**.

---

## 7. Contradictions between the code and the existing documentation

Reported, not reconciled. Each is a finding for the named owner; none was fixed.

| # | Contradiction | Established by | Diverges from | Owner |
| --- | --- | --- | --- | --- |
| C1 | The 24 h duration maximum is justified as "matching the normalization policy default of 24 hours"; no such default exists in `datara/normalization.py` | `datara/canonical.py:77`–`:79` vs. `datara/normalization.py:265`, `:277`, `:452` (caller-supplied, positivity-only) | SR27 (every conversion/limit traceable) | **founder** (the bound), **System Architect — Feng Guo** (the comment) |
| C2 | Enforced elapsed domain `1000 … 86_400_000` ms | `datara/canonical.py:75`, `:79`; `datara/models.py:378`–`:384`; `datara/migrations/0001_initial.py:111` | `fit-support-matrix.md:104` (`1` – `4294967294`) and `:279` (lower bound of 1, recorded as an engineering decision) | **founder** |
| C3 | `total_timer_time` is produced as a decimal seconds string; the matrix's canonical form is integer milliseconds; the column is an integer | `datara/classification.py:1287`; `datara/models.py:363`; `fit-support-matrix.md:105` | matrix §2 | **System Architect — Feng Guo** |
| C4 | `total_distance` is produced as a decimal metres string; the matrix's canonical form is integer centimetres | `datara/classification.py:1288`–`:1290`; `datara/models.py:298`–`:299`; `fit-support-matrix.md:106` | matrix §2 | **System Architect — Feng Guo** |
| C5 | `start_time` has a matrix upper bound of `4926032894`; no upper-bound check exists | `datara/classification.py:1194`; `fit-support-matrix.md:103` | matrix §2 | **System Architect — Feng Guo** |
| C6 | **Implementation gap against recorded decisions D-A1 and D-A3.** `sport = running` with `sub_sport = 7 road` produces **no** warning, while `decision-register.md:98` (D-A3) requires disclosure and names the code `SUBSPORT_SPORT_MISMATCH` for exactly a cross-sport sub-sport, and `:96` (D-A2) requires `SUBSPORT_ALL_GOALS_ONLY` for `254`. The relation needed to decide it is **not in the SDK profile** — its `sub_sport` map is 112 plain strings with no sport association — but it **is** in **D-A1** (`:94`), which freezes the partition as 9 running / 19 cycling / one shared / 84 to neither on SHA-256-verified pinned bytes. `7 road` is in the cycling set and not the running set, so the cross-sport case is directly decidable today. `SUBSPORT_SPORT_MISMATCH` has **zero occurrences** in `datara/`. The proposed matrix tabulates the same partition at §12.2 (`fit-support-matrix.md:318`–`:371`, `:223`, `:487`) and states the same requirement at `:412`–`:415` — corroboration, **not** the authority | `datara/classification.py:1247`–`:1248`; `decision-register.md:94` (D-A1), `:96` (D-A2), `:98` (D-A3); corroborating `fit-support-matrix.md:318`–`:371`, `:223`, `:412`, `:487` | matrix §12.5, §12.2 (corroborating) | **System Architect — Feng Guo** (implementation gap in code this document does not edit; author of the decisions) |
| C7 | `sub_sport = 254` is not rejected; the literal `254` appears nowhere in `datara/`; `SPORT_ALL_GOALS_ONLY` and `SUBSPORT_ALL_GOALS_ONLY` do not exist | verified at runtime; `fit-support-matrix.md:415`, `:475`–`:476` | matrix §12.4, §12.8 | **founder** (codes), **System Architect — Feng Guo** (gap) |
| C8 | `monitoring_a` (15) and `monitoring_b` (32) fall through to the generic unsupported-type reason | `datara/classification.py:446`–`:457`; `fit-support-matrix.md:425` | matrix §12.6 | **System Architect — Feng Guo** |
| C9 | Multisession count and declared `auto_multi_sport` share one reason code; the matrix marks the split "required" | `datara/classification.py:1099`–`:1122`; `fit-support-matrix.md:481`, `:483` | matrix §12.8 | **System Architect — Feng Guo** |
| C10 | "activity present, `num_sessions` absent" produces no disclosure at all | `datara/classification.py:1138`–`:1144`; `fit-support-matrix.md:454`, `:459` | matrix §12.7 case B | **System Architect — Feng Guo** |
| C11 | Two reason-code vocabularies coexist (uppercase matrix, lowercase code); the code's set is the one with a test | `fit-support-matrix.md:182`–`:212` vs `datara/classification.py:117`–`:231`; `datara/tests/test_classification.py:516` | matrix §5, and TC01/TC21 oracle wording | **System Architect — Feng Guo** |
| C12 | Original-byte immutability is application-enforced; the metric graph has database triggers | `datara/models.py:252`–`:261`; `datara/migrations/0002_saved_metric_graph.py:49`, `:70`, `:146` vs. no trigger in `0001_initial.py` | SR03 (stated intent), architectural consistency | **System Architect — Feng Guo** |
| C13 | No production path converts decoded bytes into the duplicate/conflict state machine's input; `SessionFacts` is test-only | `datara/dedup.py:723`; `datara/dedup.py:82`–`:108`; `datara/tests/test_conflict.py:85` | SR04 end-to-end | **System Architect — Feng Guo** |
| C14 | Conflict resolution, supersession and retain-both are declared in the schema and required by the contract, with no writer | `datara/models.py:571`–`:575`, `:592`–`:593`; `datara/dedup.py:1001`–`:1002`, `:1103`–`:1104`; `duplicate-conflict-options.md:158`–`:159`, `:37`–`:39` | `duplicate-conflict-options.md` §5, §8 | **founder** (outcomes), **System Architect — Feng Guo** (mechanism) |
| C15 | The FIT file-header profile version is read and reported but never validated, and `Import.profile_reference` is always `None` | `datara/classification.py:633`, `:1006`; `datara/dedup.py:861` | SR27 (authoritative profile version per accepted variant) | **founder** (selection), **System Architect — Feng Guo** (evidence) |
| C16 | Wall-time and memory limits are declared as bare constants and test-asserted, and required as reject codes by the matrix, but never enforced anywhere. **No policy prose states them as policy**: `:29`–`:31` are byte and count limits, and the wall-time and memory constants at `:72`–`:73` sit under none | `datara/intake.py:29`–`:31` (byte/count), `:72`–`:73` (wall-time, memory); `datara/tests/test_classification.py:904`–`:905`; `datara/classification.py:986`–`:988`; `fit-support-matrix.md:205`–`:206` | matrix §5 `LIMIT_*` codes | **System Architect — Feng Guo** |

C6, C7, C8, C9 and C10 were already reported by `fit-support-matrix.md` itself
(`:412`, `:415`, `:425`, `:459`, `:481`, `:483`) and are reproduced here because the
assignment asks for the current state, and because each was confirmed still open at
`9a1693b`.

---

## 8. Unknowns register

Every open question from this document, with its owner. No threshold, tolerance, policy or
protocol version is proposed for any of them.

**Reading the count.** Rows U1–U24 are live questions. **U25 is a withdrawn row, retained
rather than erased** so that the correction is visible — it records a question that was
already answered by a recorded decision and should not have been raised. A parser counting
live rows must exclude it; a reader counting table rows will see 25 rows and 24 questions.

| # | Question | Owner | Blocks |
| --- | --- | --- | --- |
| U1 | Which official FIT protocol document and revision is authoritative, and which protocol versions does DATARA accept? | **founder** (selection); **System Architect — Feng Guo** (evidence) | SR27, TC19 |
| U2 | Which FIT file-header profile version (or set) is accepted, and which document fixes it? | **founder**; **System Architect — Feng Guo** | SR27, C15 |
| U3 | Which licence and use conditions apply to `garmin-fit-sdk==21.217.0`, and is DATARA's intended use permitted? | **founder** | §1.4, FIX02–FIX04 |
| U4 | Is the installed package byte-identical to the published `21.217.0` artifact? | **System Architect — Feng Guo** | §1.5 |
| U5 | Who is the independent expected-value reviewer for each generated fixture, by what method? | **User Tester — Abt Hermann** with **System Architect — Feng Guo** | TC19, TC24 |
| U6 | May the upstream `tests/fits/*` sample family be used at all? | **founder** | §2.2 |
| U7 | What is the accepted elapsed-duration domain — lower bound 1 ms or 1000 ms, and is there an upper bound? | **founder** | C1, C2, TC01 |
| U8 | What integer representation and unit code does `total_timer_time` persist as? | **System Architect — Feng Guo** | C3 |
| U9 | What integer representation and unit code does `total_distance` persist as — centimetres, or metres with a unit code? | **System Architect — Feng Guo** | C4 |
| U10 | Should the classifier's `record` message count be the value persisted as `Activity.record_sample_count`? | **System Architect — Feng Guo** | §3.3 |
| U11 | Is the `:793` field-capture list an enumeration of supported `record` fields, or an over-broad placeholder? | **System Architect — Feng Guo** | §3.2 |
| U12 | Is a display string acceptable in `Session.sport`, given the matrix names the integer as canonical? | **System Architect — Feng Guo** | §3.4 |
| U13 | Should `num_sessions == 0` be undeclared (case B) or a contradiction (case C)? | **System Architect — Feng Guo** | §3.6, C10 |
| U14 | Which reason-code vocabulary is the public contract that TC01/SR32 assert against? | **System Architect — Feng Guo** | C11 |
| U14a | Should the wall-time and memory limits be enforced, and by what mechanism? | **System Architect — Feng Guo** | C16 |
| U15 | Should `goals` (11) and `activity_summary` (20) get their own reasons? | **founder** | §3.7 |
| U16 | Should `sport = 254` / `sub_sport = 254` each get a dedicated rejection code? | **founder** | C7 |
| U17 | Is a 12-byte (no-CRC) header unconditionally acceptable? | **System Architect — Feng Guo** | §4.5 |
| U18 | Must the source chain carry database immutability triggers, as the metric graph does? | **System Architect — Feng Guo** | C12 |
| U19 | Must a repeat submission with a different `media_type` be a duplicate or an error? | **System Architect — Feng Guo** | §4.6 |
| U20 | What is the byte→persistence composition contract, and which layer owns it? | **System Architect — Feng Guo** | C13 |
| U21 | Does `(owner, digest)` arbitrate correctly under two concurrent PostgreSQL connections? | **User Tester — Abt Hermann** with **System Architect — Feng Guo** | §5.3, TC03 |
| U22 | What are the authorized conflict-resolution outcomes and their mechanism — keep existing, replace, retain both? | **founder** (outcomes); **System Architect — Feng Guo** (mechanism) | C14, STK012 |
| U23 | Is `Quarantine.state = 'resolved'` meant to be reachable before a resolution contract exists? | **System Architect — Feng Guo** | §6.2 |
| U24 | Is `outcome_text` the complete TC22/SR33 presentation contract, and what consumes it? | **User Tester — Abt Hermann** with **UI Designer — Wu Yunzhou** | §6.4 |
| U25 | **WITHDRAWN — not a live question.** Asked whether the sport↔sub-sport relation existed and who owned it. It does exist, as a recorded architecture decision: `decision-register.md:94` (D-A1) freezes the partition on SHA-256-verified pinned bytes, and `:98` (D-A3) requires the cross-sport disclosure. (An earlier revision cited `fit-support-matrix.md`§12.2 as *"the approved record"*; that file is titled **"Proposed"** and disclaims approved status at `:1` and `:3`, so it corroborates but does not bind. Corrected in review of #391.) Asking this of the founder registered a settled matter as open. The live gap is C6, an implementation task owned by **System Architect — Feng Guo** | **System Architect — Feng Guo** | C6 |

---

## 9. Method, limits and what this document is not

**Method.** I read, in this worktree at `9a1693b`: `datara/models.py`, `datara/metric_store.py`,
`datara/db.py`, `datara/canonical.py`, `datara/classification.py`, `datara/intake.py`,
`datara/dedup.py`, `datara/storage.py`, `datara/normalization.py`, `datara/scoped_input.py`,
`datara/migrations/0001_initial.py`, `datara/migrations/0002_saved_metric_graph.py`,
the SR14/SR15/SR27 and SR01–SR04 registry entries, the STK001–STK004 and STK011–STK012
subtask entries, the TC01/TC03/TC19/TC24 verification-case entries, and the existing
`docs/p0-design/`, `docs/management/source-evidence/` and `docs/management/p0-decision-baseline-2026-10-01.md`
records.

**`docs/management/decision-register.md` is in that list, and its omission was a defect in
an earlier revision of this document.** I read it specifically: §2 at `:86`–`:88`, and §3
at `:90`–`:110` — the five architecture decisions **D-A1** (`:94`), **D-A2** (`:96`),
**D-A3** (`:98`), **D-A4** (`:100`), **D-A5** (`:102`), plus `:104` (what §3 routed rather
than decided), `:106` (divergences reported to their owners, not fixed), `:108` (what
stays open) and `:110` (the evidence basis and its limits). Those lines are the authority
for §3.5, for C6, and for the standing rules at the head of this document. Where a claim is about runtime behaviour rather than source text, I confirmed it
by importing the module in this environment; those confirmations are labelled "verified at
runtime" at the point of use.

**Files I did not modify.** Exactly one file was created:
`docs/p0-design/source-record-and-evidence-map.md`. No Python file, no migration, no
requirements registry, no existing design or management record, and no other agent's file
was touched. `demo_file/` was never opened, read, copied, hashed, stat-ed or listed, and no
command capable of doing so was run.

**Limits, stated rather than glossed.**

1. **No test or check was executed in this environment.** `django` and `psycopg` are not
   importable under this interpreter, and `scripts/milestone_a.ps1` requires Python 3.12.14
   exactly, which has no official Windows build. PostgreSQL 17.5 is running at
   `127.0.0.1:55432`, but no `psql` client and no `psycopg` driver were available to me, so
   **I read no live schema facts.** Every database claim in this document is a claim about
   `datara/models.py` and the migration source, and is labelled as such.
2. **Line references are to `9a1693b`.** They will drift as the code changes.
3. **The pinned SDK was read at runtime, not audited against SRC02's recorded hash.** See U4.
4. **I did not re-retrieve any web reference.** §1.1 reports what the repository records
   about a retrieval that someone else performed.
5. **I have not verified the TC01/TC03/TC19/TC24 oracles against the code.** They remain
   Not run, and nothing here changes that.
6. **Nothing here is a conformance, coverage or acceptance claim.** `fit-support-matrix.md:491`
   already records that coverage of the supported population is unproven; this document does
   not improve it.

**Registry impact — reported, not applied, as the assignment requires.** No registry status
was changed. The following are the traceability observations this document produces, for the
coordinator to action:

- `STK001`, `STK002`, `STK003`, `STK004`, `STK011`, `STK012` remain `Planned` /
  `readiness: Proposed` in `docs/management/requirements-registry.json`. This document
  supplies the per-row evidence-or-unknown structure their acceptance criteria ask for, but
  **it does not satisfy them on its own**: STK001 needs U1–U4, STK002 needs U5–U6, STK003
  and STK004 need U7–U17, and STK011/STK012 need U20–U23 plus the C13/C14 gaps, which are
  implementation work, not evidence work.
- `TC19` and `TC24` cannot become Verified on this document. Both need fixture oracles and
  an installed-artifact check that do not exist.
- `SR27` cannot be marked satisfied: U1, U2, U7 and U18 are each a required element of its
  own statement.

**Attribution.** Authored by
**Worker — Torsten Maier_space-bunny-free-xhigh_OpenCode (AI agent)** under issue #384.
Runtime execution link: unavailable in this runtime. Behaviour claims were read from the
implementation at `9a1693b`; where the implementation and a recorded decision in
`decision-register.md` disagree, §7
says so rather than choosing between them.
