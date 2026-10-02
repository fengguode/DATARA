# Proposed FIT support and mapping matrix — SDK 21.217.0

Status: evidence-backed preparation under FIT-MAP-20261001, not an approved implementation/source contract or conformance result. [TK10 #116](https://github.com/fengguode/DATARA/issues/116), [STK003 #175](https://github.com/fengguode/DATARA/issues/175), [STK004 #176](https://github.com/fengguode/DATARA/issues/176); WP01/CUS01/FEAT01/SR01/SR02/SR27/D01. TC01/TC19/TC25 remain product unrun. TK09 inventory delivered in merged PR285; rights/fixtures remain open. Project W0 order2300/2301/2302, Agent Feng Guo, prerequisite TK09; this is contract preparation, not coding. Base main `2660c20171997350b87d064f860967257d21d346`; branch `codex/wp01-fit-mapping`.

[Selected D01](../management/p0-decision-baseline-2026-10-01.md) limits semantic scope to single-session running/cycling, indoor/outdoor. It supersedes broader multi-session positive fixtures/cardinality in the older [WP01 proposal](../management/wp01-requirements-package.md). This matrix does not add an independently required source end time: the proposal's end_time rule still needs reconciliation with selected required start+elapsed. No guessed device allowlist, sport alias, timestamp, duration or distance fallback.

## Source identity and actual inspection

Pinned official commit `6db34d7958dce3cef89194e82d6bdc9437c810de`. Primary retrieved source text in memory on 1 October 2026 05:35–38 UTC, parsed literal profile metadata with Python AST, inspected text/line locations and hashed actual retrieved bytes. Vendor modules were not imported or executed; source/packages/fixtures were not saved into DATARA. This is static source evidence, not a decoded-file check. Package checksums in [source inventory](../management/source-evidence/fit-source-inventory.md) are publisher declarations, not downloaded package verification. No terms acceptance or rights conclusion.

| ID | Official pinned source | Retrieved SHA-256 / byte count | Evidence role |
| --- | --- | --- | --- |
| MAP01 | [profile.py](https://github.com/garmin/fit-python-sdk/blob/6db34d7958dce3cef89194e82d6bdc9437c810de/garmin_fit_sdk/profile.py) | cfc2737638285d1ec09d2972e4bc88b30b4b5a5bc07bfcd843669e7c92cb865c / 967399 | Literal Profile.version 21.217.0 Release; messages, fields, types. This is not a required file-header version. |
| MAP02 | [fit.py](https://github.com/garmin/fit-python-sdk/blob/6db34d7958dce3cef89194e82d6bdc9437c810de/garmin_fit_sdk/fit.py#L87) | 935b1cc046e0118d7c6aa2f2a019fefee0b3cc1b4cec87abeca1a9123b77297b / 6259 | Base-type invalid bit patterns. |
| MAP03 | [decoder.py](https://github.com/garmin/fit-python-sdk/blob/6db34d7958dce3cef89194e82d6bdc9437c810de/garmin_fit_sdk/decoder.py) | afed5ac1876cfe19949c4e0bce24c7fcdb31f72752db79d757be2da59fc23675 / 35012 | Header/integrity, raw invalid handling, scale/offset and explicit compressed timestamp limitation. |
| MAP04 | [util.py](https://github.com/garmin/fit-python-sdk/blob/6db34d7958dce3cef89194e82d6bdc9437c810de/garmin_fit_sdk/util.py#L18) | 10f0ff3068d79013d366fd8addb5aabe9e0acafa1609a3f9fd617ecd885ac106 / 2275 | UTC conversion adds Unix offset631065600 seconds. |
| MAP05 | [crc_calculator.py](https://github.com/garmin/fit-python-sdk/blob/6db34d7958dce3cef89194e82d6bdc9437c810de/garmin_fit_sdk/crc_calculator.py) | df264b09a584c53478894a8dd24547bb4e1b21b8a5e5076142158d37b3daf43e / 2303 | CRC routines used by MAP03; inspected only. |

Official protocol prose was not substantively captured in SRC05. Source implementation observations below do not establish complete FIT protocol conformance. Artifact licence linkage, lawful synthetic generator and independent oracles remain missing.

## Semantic mapping candidates

Notation: global message number / field definition number. Every metadata row cites MAP01's literal message/field entry; scalar transformation observed in MAP03 lines602–629 is raw/scale minus offset, after invalid handling. Candidate canonical decimal values must derive from raw integers with exact arithmetic; applying the conversion twice or treating decoder floats as proof of canonical precision is prohibited. Exact adapter/settings and conformance fixtures remain to freeze.

| Source entry (MAP01) | Base/type; scale, offset, unit | Proposed role and disposition | Missing conformance/contract evidence |
| --- | --- | --- | --- |
| file_id 0/0 type | enum/file; 1,0 | Profile file enum4 is activity; other file categories outside D01. | Required file_id cardinality and conflicting identification rules; fixture oracle. |
| session18/5 sport | enum/sport;1,0 | Required sport: profile1 running,2 cycling. Unknown/other values cannot silently map to either. | Exact allowed sport/subsport pair matrix and mismatch fixtures. |
| session18/6 sub_sport | enum/sub_sport;1,0 | Profile identifies generic0, treadmill1, street2, trail3, track4, spin5, indoor_cycling6, road7, mountain8, indoor_running45, gravel_cycling46. These names are evidence, not a complete approved allowlist. | Missing/unknown handling and indoor/outdoor classification must freeze; no inference from GPS absence. Other entries remain unresolved until mapped. |
| session18/2 start_time | uint32/date_time;1,0 | Required source UTC start candidate. MAP04 UTC conversion; do not substitute local_timestamp, file creation or first sample. | Valid date_time range/reserved semantics, cardinality and independently expected UTC instant. |
| session18/7 total_elapsed_time | uint32;1000,0,s | Required recorded elapsed duration candidate, exact raw/1000 seconds. P0 volume uses this value. | Valid duration/range/required relation rules, sentinel/zero/boundary fixtures. |
| session18/8 total_timer_time | uint32;1000,0,s | Optional separate timer seconds, never fallback for elapsed. | Timer/elapsed consistency rule and null/warning oracle. |
| session18/9 total_distance | uint32;100,0,m | Optional exact raw/100 metres. No sample-derived fill. | Valid range, missing/sentinel/null/warning oracle. |
| session18/253 timestamp | uint32/date_time;1,0,s | Source timestamp available, not automatically a required end-time field or duration substitute. | Meaning/relation and proposal end_time reconciliation before retention/use. |
| activity34/1 num_sessions;34/2 type | uint16; enum/activity | Profile count and type exist; activity enum0 manual,1 auto_multi_sport. D01 single-session acceptance is application scope, not implied by enum0 alone. | Exact session/activity cardinality, omitted/count-mismatch and chained-layout rejection. |
| activity34/5 local_timestamp | uint32/local_date_time;1,0 | Does not supply the required UTC start; no implicit timezone guess. | Local epoch/offset/ambiguity rules not established; normalized use unresolved. |
| record20/253 timestamp | uint32/date_time;1,0,s | Optional sample UTC time candidate; no sample required solely to import a D01 activity. | Ordering/duplicate time, valid ranges, session membership and independent sample oracle. |
| record20/3 heart_rate;20/5 distance | uint8 bpm; uint32 scale100 m | Optional native sample candidates; invalid/missing may be null under final warning rule. | Ranges, sample validity and no imputation fixtures. |
| record20/4 cadence | uint8;1,0,rpm | Profile unit only; no invented sport-specific conversion or normalized retention promise. | Retention/applicability and fractional/component rules unresolved. |
| record20/6 speed;20/73 enhanced_speed | uint16 / uint32;1000,0,m/s | Profile metadata exists; native speed has component expansion. | Native/enhanced precedence, expansion/accumulation and conflict oracle unresolved; no silent fallback. |
| record20/2 altitude;20/78 enhanced_altitude | uint16 / uint32;5,500,m | Formula raw/5−500 is source-supported; native altitude has component expansion. | Exact retention/precedence and expansion oracle unresolved. |
| record20/0 position_lat;20/1 position_long | sint32;1,0,semicircles | Profile unit exists; GPS optional and excluded from model egress. | Geographic conversion/ranges and normalized retention unresolved; do not invent degrees conversion from memory. |
| session18/11 total_calories;18/16 avg_heart_rate;18/17 max_heart_rate | uint16 kcal;uint8 bpm | Available optional source definitions, not required inputs or evaluated-skill promises. | Retention/ranges/oracles unresolved. |
| lap19/event21 and developer/native overrides | Profile entries exist but full semantics not mapped here. | No required value may depend on unmapped semantics; unverified structural feature blocks acceptance. | Relation, event/native override/developer definition validation and independent fixture evidence unresolved. |

All rows need lawful fixture hash/generator version plus independent expected values before conformance claims. FIX01/FIX05 and upstream candidate samples in the inventory are not executable approved oracles.

## Unit, null, time and integrity observations

| Rule area | Exact evidence inspected | Candidate outcome / unresolved gate |
| --- | --- | --- |
| Scalar invalid values | MAP02 lines87–103; MAP03 lines350–407 skips scalar invalid values before profile transforms. enum/uint8 invalid0xFF; uint16 0xFFFF; uint32 0xFFFFFFFF; sint32 0x7FFFFFFF. Zero-invalid base types have separate sentinels. | Missing and omitted-invalid are distinct source causes even when normalized null. Required invalid/missing rejects whole file; optional null+warning requires field contract and raw-presence diagnostics. No numeric zero-fill. |
| UTC date_time | MAP03 lines446–447 converts only date_time, MAP04 lines18–30 adds631065600 Unix seconds with UTC. Profile types.date_time lists minimum268435456. | Epoch arithmetic observed; valid minimum/reserved/date precision semantics and independent oracle still pending. local_date_time is not treated as date_time by this code path. Reject unknown required interpretation, never infer timezone from device/GPS/browser. |
| Scale/offset | MAP03 lines602–629 applies raw/scale−offset; errors can return raw unchanged. | Exact adapter validation must reject unresolved transform conditions instead of accepting returned raw as canonical units. Multi-scale/component rules remain unresolved. |
| Enum conversion | MAP03 lines583–600 retains unknown raw enum when mapping missing. | Decoder string conversion success is not valid sport/file classification; validate approved raw enum explicitly. |
| Signature/header shape | MAP03 is_fit lines70–88 checks12/14-byte header lengths, minimum length and .FIT marker; FileHeader lines752–761 reads protocol/profile/data size and optional header CRC. | Static behavior observed, not a full header/protocol acceptance oracle. Preserve raw protocol/profile bytes; do not derive them from SDK21.217.0 or trust the displayed profile-version conversion as a conformance rule. |
| Integrity | MAP03 check_integrity lines90–112 checks declared end is within stream, header CRC when14-byte header and file CRC; normal read lines160–182 checks file CRC. | Require whole-file integrity under D01, but exact header-zero CRC exceptions, trailing/chained layouts, protocol major checks and definition/size validation still need official protocol evidence and fixtures. check_integrity alone does not prove single-file cardinality or semantic validity. |
| Compressed timestamp records | MAP03 lines184–188 dispatches compressed headers; lines347–348 explicitly raises unsupported error. | Named blocker: current pinned Python decoder cannot satisfy a claim of compressed timestamp support. Do not reconstruct timestamps by guess, omit affected samples or label partial decoded data accepted. Preserve selected SDK version and target; engine/coverage decision remains open before G0. |
| Partial messages/errors | MAP03 read lines153–158 returns collected messages plus errors after an exception. | Any decode/integrity error prevents accepted partial activity. Safe failure classification and supported/unsupported distinction must freeze; raw exception text is not a public diagnostic contract. |
| Chained files | MAP03 read lines147–148 loops until stream end; is_fit line80 contains chained-offset TODO. | D01 excludes chained/multisport layouts. Decoder looping is not permission to accept them; detection/whole-file rejection needs independent fixtures. |
| Resource controls | D01 application choices16MiB/file,50files/128MiBbatch,200k messages/100k samples,60s/512MiB,one worker. | Not protocol/profile limits or measured enforcement. Existing TK13/TK20 and actual limit/isolation tests remain required. |

## Gaps, ownership and confirmation boundary

1. Yi with Yu owns any delegated D01 product clarification; no silent SDK downgrade, engine substitution or supported-scope reduction. Compressed timestamp incompatibility must be resolved in an evidenced engine/coverage contract before claiming support.
2. Existing architecture contract work must freeze source cardinality, supported sport/subsport pairs, valid time/duration ranges and relation rules. This draft intentionally exposes remaining unknowns; it is not permission to implement against them.
3. Source/rights lane establishes applicable artifact terms, package-byte verification and lawful fixture generator/examples. Official source inspection does not accept terms or prove redistribution rights.
4. Worker/Tester only start under later eligible assignments: pinned adapter/runtime/settings, exact decimal path, boundary/error/unknown-field, CRC, compressed/chained, two-identity and repeatability cases. Mock/source inspection does not replace actual decode/system evidence.

Yi is sole matrix author/integrator; Licun supplied read-only requirements/evidence checklist before integration. Independent final architecture confirmer Feng Guo, technical reviewer Dennis Windmaier, evidence audit Wang Xiaofeng; exact head confirmations will be recorded on issue116 and [review record](../team/reviews/fit-mapping-review-2026-10-01.md). Their approval of a traceable proposed matrix cannot clear its explicit G0 blockers, verified status, founder acceptance, merge permission or deployment.

---

## 2 October 2026 increment — authoritative FIT acceptance and mapping matrix

Status: **authoritative for Milestone A implementation**, issued under the reopened TK10/STK003/STK004 increment (System Architect — Feng Guo). This section **supersedes** the 1 October "Semantic mapping candidates", "Unit, null, time and integrity observations" and parts of "Gaps, ownership" above for every cell it names; where the two differ, this section governs. The 1 October sections are preserved unchanged as historical evidence, and their line numbers are deliberately not shifted — `decision-register.md:72` cites line 58 and discussion #297 cites lines 46, 58 and 65.

Nothing here is a conformance result, a verified requirement, an acceptance or a release. `TC01`, `TC19`, `TC25`, `SR01`, `SR02` and `SR27` remain **Not run / unverified**. Engineering value ranges and enumerations below are the authoritative answer to the TK11/TK15 question "what must we not invent"; where this section says a value is derived rather than evidenced, that distinction is deliberate and load-bearing.

### 1. Scope, restated as acceptance rules

From `p0-decision-baseline-2026-10-01.md:33`, restated so that each clause becomes a testable rule rather than an intention:

| Selected clause | Acceptance rule it produces |
| --- | --- |
| Protocol coverage target is FIT 1.0 and 2.0 using the official decoder | A target, **not** a verified capability. The pinned decoder's actual coverage is bounded by §8, which records a known gap. Do not describe 1.0/2.0 coverage as met. |
| Single-session running and cycling, indoor and outdoor | Exactly one `session` message, `sport` in `{running, cycling}`. Indoor/outdoor is a *label*, never an import condition — see §4. |
| Exact sport/sub-sport enumerations mapped from the pinned profile | §3 is that mapping. It is derived from the profile enum names recorded at MAP01; it is not a device list and not a convention. |
| A device-model allowlist is **not** an acceptable substitute for file conformance | Conformance is decided per file, from file structure and field values only. No product model, family or serial is read, stored or matched anywhere in this contract. |
| New device fields require no new analysis promise | Original bytes are preserved. Any field absent from this matrix is **ignored for normalisation** with an `IGNORED_UNKNOWN_FIELD` warning and its bytes retained. Ignorance never blocks an import; a **required** value that depends on an unmapped field **rejects** the file (`p0-decision-baseline-2026-10-01.md:37`). |
| Unsupported file types, sports, multisport/chained layouts and required-but-missing semantics each get a stable explanation | §5 and §6 give one stable code per case. Codes are identifiers, not sentences; the athlete-facing text is a separate presentation contract. |
| P0 excludes wellness, planned workout/course and arbitrary archive imports | Any `file.type` other than `activity` rejects. This is a single check that excludes all three categories at once — see §5. |

### 2. The field matrix

Notation: `message/field` is the FIT global message number and field definition number. `Milestone A` states whether the field is normalised in the authorised increment (`decision-register.md:41`: "deterministic normalisation of the four P0 required inputs with no imputation"). Canonical types are integers by design: D02 requires canonical fixed precision and forbids floating-point near-equality, and the conflict tuple compares these exact values (`duplicate-conflict-options.md` §6).

| Source entry | Profile base type, scale/offset, unit | Raw domain and invalid sentinel | Canonical normalized field | Type | Req/Opt | Milestone A valid range | Reject code | Warning code | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `file` 0/0 `type` | `enum/file`, 1, 0 | uint8 0–254; invalid `0xFF` | `file_type_raw` | integer enum | Required (structural) | Exactly `4` | `UNSUPPORTED_FILE_TYPE` | — | MAP01 profile `file` enum activity = 4 |
| `session` 18/5 `sport` | `enum/sport`, 1, 0 | uint8 0–254; invalid `0xFF` | `sport` | integer enum | **Required** | `{1, 2}` per §3 | `UNSUPPORTED_SPORT` | — | MAP01; D01 semantic scope |
| `session` 18/6 `sub_sport` | `enum/sub_sport`, 1, 0 | uint8 0–254; invalid `0xFF` | `sub_sport`, `indoor_outdoor` | integer enum, enum or null | Optional | Approved pair set per §3, else null | — | `SUBSPORT_ABSENT`, `SUBSPORT_UNMAPPED`, `SUBSPORT_SPORT_MISMATCH` | MAP01 sub-sport names |
| `session` 18/2 `start_time` | `date_time` (uint32), 1, 0 | uint32 0–4294967294; invalid `0xFFFFFFFF` | `start_utc_seconds` | **integer** seconds since Unix epoch | **Required** | `899501056` – `4926032894` | `REQUIRED_FIELD_ABSENT`, `REQUIRED_FIELD_CARDINALITY`, `REQUIRED_FIELD_INVALID`, `REQUIRED_FIELD_OUT_OF_RANGE` | — | MAP01 `types.date_time` minimum 268435456; MAP04 offset 631065600; type domain upper bound |
| `session` 18/7 `total_elapsed_time` | uint32, 1000, 0, s | uint32 0–4294967294; invalid `0xFFFFFFFF` | `elapsed_ms` | **integer** milliseconds | **Required** | `1` – `4294967294` | as above, plus `REQUIRED_FIELD_OUT_OF_RANGE` at 0 | — | MAP01 scale 1000 / unit s; upper bound from type domain; lower bound is an engineering decision, see §9 |
| `session` 18/8 `total_timer_time` | uint32, 1000, 0, s | uint32 0–4294967294; invalid `0xFFFFFFFF` | `timer_ms` | integer milliseconds | Optional | `0` – `4294967294` | — | `OPTIONAL_FIELD_ABSENT`, `OPTIONAL_FIELD_INVALID` | MAP01 |
| `session` 18/9 `total_distance` | uint32, 100, 0, m | uint32 0–4294967294; invalid `0xFFFFFFFF` | `distance_cm` | **integer** centimetres | Optional | `0` – `4294967294` | — | `OPTIONAL_FIELD_ABSENT`, `OPTIONAL_FIELD_INVALID` | MAP01 scale 100 / unit m |
| `session` 18/11 `total_calories` | uint16, 1, 0, kcal | uint16 0–65534; invalid `0xFFFF` | — | — | Optional | Deferred | — | — | MAP01 |
| `session` 18/16, 18/17 `avg_heart_rate`, `max_heart_rate` | uint8, 1, 0, bpm | uint8 0–254; invalid `0xFF` | — | — | Optional | Deferred | — | — | MAP01 |
| `session` 18/253 `timestamp` | `date_time` (uint32), 1, 0, s | uint32 domain | — | — | Optional | Deferred | — | — | MAP01 |
| `activity` 34/1 `num_sessions` | uint16, 1, 0 | uint16 0–65534; invalid `0xFFFF` | `session_count_declared` | integer | Required **relation**, optional presence | Must equal the decoded `session` message count when present | `SESSION_COUNT_MISMATCH` | — | MAP01; D01 single-session scope |
| `activity` 34/2 `type` | `enum/activity`, 1, 0 | uint8 0–254; invalid `0xFF` | `activity_type_raw` | integer enum | Optional | Reject when `1` (`auto_multi_sport`) | `MULTISPORT_UNSUPPORTED` | — | MAP01 activity enum manual 0, auto_multi_sport 1 |
| `activity` 34/5 `local_timestamp` | `local_date_time` (uint32), 1, 0 | uint32 domain | — | — | **Not normalised** | — | — | — | MAP01; see §9 |
| `record` 20/253 `timestamp` | `date_time` (uint32), 1, 0, s | uint32 domain | — | — | Optional | Deferred | — | — | MAP01; **CT-affected**, §8 |
| `record` 20/3 `heart_rate` | uint8, 1, 0, bpm | uint8 0–254; invalid `0xFF` | — | — | Optional | Deferred | — | — | MAP01; CT-affected |
| `record` 20/5 `distance` | uint32, 100, 0, m | uint32 domain | — | — | Optional | Deferred | — | — | MAP01; CT-affected |
| `record` 20/4 `cadence` | uint8, 1, 0, rpm | uint8 0–254; invalid `0xFF` | — | — | Optional | Deferred | — | — | MAP01; CT-affected; no sport-specific conversion is selected |
| `record` 20/6 `speed`, 20/73 `enhanced_speed` | uint16 / uint32, 1000, 0, m/s | uint16 / uint32 domains | — | — | Optional | Deferred | — | — | MAP01; CT-affected; native has component expansion, precedence unresolved |
| `record` 20/2 `altitude`, 20/78 `enhanced_altitude` | uint16 / uint32, 5, 500, m | uint16 / uint32 domains | — | — | Optional | Deferred | — | — | MAP01; CT-affected; `raw/5 − 500` is source-supported, precedence unresolved |
| `record` 20/0, 20/1 `position_lat`, `position_long` | `sint32`, 1, 0, semicircles | sint32 −2147483647–2147483647; invalid `0x7FFFFFFF` | — | — | Optional | **Not normalised** | — | — | MAP01; see §9; CT-affected |
| `lap` 19/*, `event` 21/*, developer / native-override messages | — | — | — | — | — | Not normalised | — | — | Profile entries exist; semantics unmapped, so no **required** value may depend on them |

**Two columns carry the weight.** *Raw domain and invalid sentinel* is why there is no numeric zero-fill anywhere: the decoder skips a value equal to the base-type invalid marker, so a decoded field is either present and meaningful or absent (`MAP02` lines 87–103, `MAP03` lines 350–407 as recorded at line 52 above). Missing and omitted-invalid are **distinct source causes** that may normalise to the same null; the warning code distinguishes them, and no imputation is applied.

### 3. Sport and sub-sport enumerations

This is the mapping D01 requires to come from the pinned profile. Every value below is a profile enum name recorded at MAP01.

**`sport` — the approved set is exactly two values.**

| Raw | Profile name | Disposition |
| --- | --- | --- |
| 1 | `running` | Accepted |
| 2 | `cycling` | Accepted |
| anything else | any other `sport` value | Whole-file `UNSUPPORTED_SPORT` |

The full `sport` enum is **not** enumerated anywhere in this repository's evidence. That is deliberate and safe: the policy is a whitelist by exclusion — accept exactly `{1, 2}`, reject everything else — so the missing list is never needed to make a decision, and no unknown value can be silently mapped to running or cycling. Do not add values to this set without new profile evidence and a recorded decision.

**`sub_sport` — approved pairs.**

| `sport` | Approved `sub_sport` raw values | Profile names |
| --- | --- | --- |
| `running` (1) | 0, 1, 2, 3, 4, 45 | `generic`, `treadmill`, `street`, `trail`, `track`, `indoor_running` |
| `cycling` (2) | 0, 5, 6, 7, 8, 46 | `generic`, `spin`, `indoor_cycling`, `road`, `mountain`, `gravel_cycling` |
| any other `sub_sport` value for that sport | — | Mapped to null with `SUBSPORT_UNMAPPED` |
| a value belonging to the other sport, e.g. `cycling` with `treadmill` | — | Mapped to null with `SUBSPORT_SPORT_MISMATCH` |

A pair outside the approved matrix does **not** reject the file. Rationale: `sport` is the required, profile-authoritative value; `sub_sport` is optional. Rejecting a whole file over an optional taxonomy edge case would silently reduce the supported population beyond what D01 selected, whereas nulling the optional field with an explicit warning is exactly D01's rule for an absent or invalid optional value. The athlete keeps the activity and sees that the indoor/outdoor label is unavailable.

**Indoor/outdoor classification.**

| Class | `sub_sport` raw values | Basis |
| --- | --- | --- |
| `indoor` | 1 `treadmill`, 6 `indoor_cycling`, 45 `indoor_running` | The profile **names** denote an indoor location. |
| `outdoor` | 2 `street`, 3 `trail`, 4 `track`, 7 `road`, 8 `mountain`, 46 `gravel_cycling` | The profile names denote an outdoor location. |
| `null` — unclassified | 0 `generic`, 5 `spin` | The names carry no location. `generic` says nothing; `spin` names an activity style, not a place. |

`spin` is the contested cell and the reason for this table's conservative shape. Classifying it as indoor would import a cycling convention from outside the profile — exactly the kind of inference this matrix exists to prevent. The consequence is stated plainly: **a spin ride imports normally, and its indoor/outdoor label is `null`.** The dashboard's indoor/outdoor split therefore has no row for such activities. That is a labelling limit, not an import limit, and it is the honest outcome until profile evidence or real data supports a change.

Two prohibitions that follow directly and that Worker must not relax:

- **Absence of GPS never implies indoor.** Indoor classification comes from `sub_sport` only.
- **No device or product model is consulted**, so no file can be rejected because of what device produced it.

### 4. Structural rules

| Rule | Test | Outcome on failure |
| --- | --- | --- |
| Single session | Count decoded `session` messages | 0 → `SESSION_ABSENT`; more than 1 → `MULTISESSION_UNSUPPORTED` |
| Session count relation | If `activity.num_sessions` is present and decodes, it must equal the decoded session count | `SESSION_COUNT_MISMATCH` |
| Multisport | `activity.type`, if present | `1` → `MULTISPORT_UNSUPPORTED` |
| `activity` message absent | Permitted | No cross-check possible; the four required inputs do not depend on it |
| `file` message absent | **Rejected** | `FILE_TYPE_UNDETERMINED` — conformance cannot be established, and SR27 requires unverified variants to reject as unsupported |
| `file.type` != 4 | Rejected | `UNSUPPORTED_FILE_TYPE` — this single rule excludes wellness, planned workout/course and archive imports |
| Chained file | More than one file header in the stream | `CHAINED_FILE_UNSUPPORTED`. **The detection mechanism is an open contract, not established** — see §7 |
| Integrity | Whole-file integrity under the pinned rules | `INTEGRITY_FAILED` |
| Any decode or integrity error | — | `DECODER_ERROR`; **no partial accepted activity** |

### 5. Reason-code taxonomy

Stable codes, not sentences. One code per cause; a file reports the **first** matching rule in the order of this table, so a rejected file has exactly one explanation and diagnostics stay deterministic.

| Code | Kind | Meaning |
| --- | --- | --- |
| `MALFORMED_FIT` | reject | Not a readable FIT stream: header shape, length or truncation |
| `INTEGRITY_FAILED` | reject | Header or file CRC, or declared-size inconsistency |
| `UNSUPPORTED_FILE_TYPE` | reject | `file.type` present and not `activity` |
| `FILE_TYPE_UNDETERMINED` | reject | No `file` message, so conformance cannot be established |
| `CHAINED_FILE_UNSUPPORTED` | reject | More than one file header in the stream |
| `DECODER_UNSUPPORTED_COMPRESSED_TIMESTAMP` | reject | A compressed-timestamp message was encountered — see §8 |
| `DECODER_ERROR` | reject | Any other decode failure, sanitised |
| `MULTISPORT_UNSUPPORTED` | reject | `activity.type` is `auto_multi_sport` |
| `MULTISESSION_UNSUPPORTED` | reject | More than one `session` message |
| `SESSION_ABSENT` | reject | No `session` message |
| `SESSION_COUNT_MISMATCH` | reject | `activity.num_sessions` disagrees with the decoded count |
| `UNSUPPORTED_SPORT` | reject | `sport` outside `{running, cycling}` |
| `REQUIRED_FIELD_ABSENT` | reject | A required field was not present |
| `REQUIRED_FIELD_CARDINALITY` | reject | A required field occurred more than once |
| `REQUIRED_FIELD_INVALID` | reject | A required field carried its base-type invalid sentinel |
| `REQUIRED_FIELD_OUT_OF_RANGE` | reject | A required field was outside its §2 range |
| `LIMIT_FILE_BYTES_EXCEEDED` | reject | 16 MiB per file, inclusive |
| `LIMIT_BATCH_FILES_EXCEEDED` | reject | 50 files per batch, inclusive |
| `LIMIT_BATCH_BYTES_EXCEEDED` | reject | 128 MiB submitted bytes per batch, inclusive |
| `LIMIT_MESSAGES_EXCEEDED` | reject | 200,000 decoded messages per file |
| `LIMIT_SAMPLES_EXCEEDED` | reject | 100,000 sample records per file |
| `LIMIT_WALL_TIME_EXCEEDED` | reject | 60 s wall time per file |
| `LIMIT_MEMORY_EXCEEDED` | reject | 512 MiB worker memory per file |
| `IGNORED_UNKNOWN_FIELD` | warning | A field outside this matrix was ignored for normalisation; its bytes are retained |
| `OPTIONAL_FIELD_ABSENT` | warning | An optional field was not present; normalised to null |
| `OPTIONAL_FIELD_INVALID` | warning | An optional field carried its invalid sentinel; normalised to null |
| `SUBSPORT_ABSENT` | warning | No `sub_sport`; indoor/outdoor is `null` |
| `SUBSPORT_UNMAPPED` | warning | `sub_sport` outside the approved set; indoor/outdoor is `null` |
| `SUBSPORT_SPORT_MISMATCH` | warning | `sub_sport` belongs to the other sport; `sub_sport` is `null` |

Per-file **dispositions** are `accepted`, `rejected`, `duplicate_of_existing`, `duplicate_of_quarantined` and `quarantined_conflict`, specified in `duplicate-conflict-options.md` §5. A resource-limit rejection names the specific dimension rather than collapsing all seven into one code, because "file too big" and "decoder ran out of time" call for different athlete actions.

Two presentation rules bind these codes to SR32 and SR01: the code is an identifier and **raw decoder exception text is never the user-visible diagnostic**, and every rejection reason must be stated as text associated with the specific file.

### 6. What is now authoritative, and what is still pending

| Cell group | State |
| --- | --- |
| The four required inputs: names, canonical types, units, integer representations, cardinality, ranges, reject codes | **Authoritative for Milestone A.** This is the answer Worker must not invent. |
| `sport` / `sub_sport` enumerations, approved pairs, indoor/outdoor classification | **Authoritative for Milestone A**, derived from MAP01 profile names as recorded |
| Structural rules §4, reason codes §5, warning codes §5 | **Authoritative for Milestone A** |
| Explicit non-decisions §9 | **Authoritative** — these are prohibitions, not gaps to be filled in later by implementation judgement |
| Date-time valid bounds | **Derived, not protocol-evidenced.** The lower bound comes from the profile's own declared `types.date_time` minimum; the upper bound is the uint32 type domain. The FIT protocol document was never captured (`fit-source-inventory.md:19`, SRC05), so reserved values and the protocol's own valid range are unconfirmed. Treat the bounds as *engineering validation*, never as protocol conformance. |
| Header CRC exception rules, chained-layout definition, compressed-timestamp specification | **Pending TK09** — protocol prose was not captured |
| Fixture oracles for every range above | **Pending TK09** — no lawful fixture and no independent oracle exists (`fit-source-inventory.md:36`) |
| SDK licence applicability and permitted use | **Pending TK09** — the selected commit has no `LICENSE.txt` or `LICENSE`; current-`main` text cannot stand in for the artifact (`fit-source-inventory.md:20`) |
| Installed package byte verification | **Pending** — published hashes are publisher declarations, not verified bytes (`fit-source-inventory.md:25`) |
| Whether any cell is reachable for files using compressed timestamps | **Pending the CT defect decision** — §8 |

**Consequence for Worker:** cells in the "Authoritative" rows may be implemented. Cells in the "Pending" rows may not be implemented as conformance, because implementing them would require inventing the missing evidence. In particular, do not treat the date-time bounds as a protocol rule, and do not treat any cell as covered by a compressed-timestamp file.

### 7. Chained-file detection — an open implementation contract

The rule is settled (`CHAINED_FILE_UNSUPPORTED`): a stream with more than one file header is rejected. The **mechanism** is not. The pinned decoder loops the read until stream end and carries a chained-offset `TODO` in `is_fit` (recorded at line 60 above), so it will decode a chained file as one continuous message stream without complaining — decoder looping is not permission to accept.

A candidate mechanism is derivable from what the decoder already reads: the file header declares `data_size`, so if `header_size + data_size` (plus CRC where present) is smaller than the stream, the file is chained. That candidate is **not** confirmed here, because confirming it requires the protocol document that TK09 has not yet captured. Worker must not ship chained-file acceptance on a guess. This is recorded as an open contract rather than left silent, because a chained file accepted as single-session would silently violate the scope D01 selected.

### 8. The compressed-timestamp defect — which cells are actually affected

Reported honestly, per discussion #297 and `decision-register.md:70-72`.

**The observed defect.** The pinned Python decoder dispatches compressed headers and then explicitly raises an unsupported error (MAP03 lines 347–348, recorded at line 58 above). The decode spike against one real Garmin Connect export completed with CRC verification enabled and reported **zero** compressed-timestamp definitions.

**What that spike does and does not show.** It shows that *that one file* does not exercise the path. It does not show that no file in the supported population does. A single successful decode is not coverage evidence, and this matrix does not treat it as such.

**Why the blast radius is the whole file, not one field.** The decoder *raises* rather than skipping. A single compressed-timestamp message anywhere in the stream therefore aborts the decode, and D01 requires that a file contribute no partial accepted activity. So:

> **Any file containing at least one compressed-timestamp message is rejected whole, with `DECODER_UNSUPPORTED_COMPRESSED_TIMESTAMP`.**

**Affected cells, stated exactly.**

| Cells | Affected? | Reason |
| --- | --- | --- |
| `record` 20/* sample-derived optionals — timestamp, heart rate, distance, cadence, speed, enhanced speed, altitude, enhanced altitude, position | **Yes** | Compression exists to shrink `record` messages. These cells are unobtainable whenever the file uses the encoding. |
| `session` 18/* **required** inputs — `sport`, `start_time`, `total_elapsed_time` | **Possibly, and I cannot bound this** | Whether a compressed-timestamp header can legally appear on a `session` message is **not established by any evidence in this repository** — the protocol text was never captured (SRC05 gap). If it can, the required inputs are unobtainable and the file rejects. I will not assert that it cannot. |
| Structural rules, `file.type`, session count, multisport detection | **Unaffected**, but unreachable in practice | These are decided from messages that precede any record data; however, a file rejected at decode never reaches them. |

**What is not permitted, and why.** Reconstructing timestamps by guess, dropping the affected samples and accepting the rest, or labelling partial decoded data as accepted are all prohibited: the first invents data, and the other two create a silent data loss that D01's "no partial accepted activity" rule exists to prevent. **No cell in this matrix is marked supported for compressed-timestamp files**, and no cell was quietly upgraded on the strength of the spike.

**What would close it.** A recorded D01 engine and coverage decision: extend supported scope, substitute an engine under a reviewed compatibility change, or reduce supported scope explicitly. All three are legitimate; silence is not. Reopen triggers: any fixture in the supported population carrying a compressed-timestamp header, or any proposal to change the engine or the scope. Until that decision exists, the honest statement of coverage is the one in §6 — several cells authoritative for Milestone A, **coverage of the supported population unproven**.

### 9. Explicit non-decisions

Each of these is a place where a plausible engineering convenience would be an invention. All are deliberate.

| Not done | Why |
| --- | --- |
| No GPS conversion to degrees | `position_lat`/`position_long` are **not normalised** in Milestone A. The semicircles conversion is not in this repository's evidence, GPS is optional, excluded from model egress, and its retention is unresolved. Converting it would be exactly the guess this matrix exists to prevent. |
| No `local_timestamp` normalisation | It cannot supply the required UTC start, and no implicit timezone inference from device, GPS or browser is permitted. Its epoch and offset semantics are not established. |
| No plausibility bands on optional numerics | Only the type domain and the invalid sentinel are checked. A narrower band requires evidence and a decision. A band chosen by intuition is a fabricated limit. |
| No `cadence` sport-specific conversion | The profile gives unit rpm; whether component or fractional values apply depends on the source message, which is unmapped. |
| No native/enhanced precedence rule for speed or altitude | Native messages carry component expansion; the precedence and accumulation rules are unresolved. Deferred, not guessed. |
| No imputation anywhere | Absent or invalid optional values become null with a warning code that distinguishes the two causes. |
| No fallbacks | `timer_ms` never substitutes for `elapsed_ms`; samples never synthesise distance; GPS absence never implies indoor; decoder success alone never implies conformance. |
| No device-model allowlist | Conformance is a property of the file, decided from structure and field values. |
| `elapsed_ms` lower bound of 1 | An engineering decision, not profile-derived: a zero-elapsed session carries no volume and would make the conflict tuple degenerate, colliding every zero-duration activity sharing a sport and start second. Recorded as my decision for escalation, not as official evidence. |

### 10. What this matrix may cause to be persisted

The binding architectural condition (`decision-register.md:58-64`) constrains the storage consequences of everything above, and is restated here so that no implementation lane reads this matrix without it.

Milestone A persists only `Import`, `SourceObject`, `Activity`/`Session` and `Snapshot`, and **none of them stores a skill-against-model outcome**. Three records are explicitly in scope and are not findings: `Eligibility`, which records a rule version and a boolean; `Evidence`, which with no Milestone A run can resolve only to a source record or a computed metric; and the quarantine record, which is a disposition state on the source chain.

The exclusion is **semantic**: no entity whose meaning is *the outcome of executing a skill against a model* may be persisted, under this name or any other. A deterministic **data-quality** observation — an out-of-range field, a decode warning, a quarantined conflict, an ignored unknown field — is *not* that meaning. It is reproducible from stored inputs by a versioned method, names no model, and is permitted. What governs is the meaning, not the word. And **no mutable latest-result or current-value pointer may exist on any entity.**

Applied to this matrix specifically:

- The reason codes and warning codes in §5 are deterministic data-quality observations and may be persisted on `Import` and on the normalised records.
- The field values in §2 are normalised observations about source data, not classifications of what an activity *means*.
- **No cell in this matrix may be extended into a quality or recommendation judgement about the athlete's activity.** An out-of-range duration produces a code, not advice. A missing GPS record produces a code, not an inference about fitness.
- `Metric` is retained in the chain as a deterministic observation with a stated limit: the contracts reference computed metrics but define no schema of their own (`decision-register.md:64`). Milestone A must not invent that schema, and any metric persisted before it exists is provisional.

### 11. Trace and evidence boundary

TK10/STK003/STK004, WP01, CUS01, FEAT01, SR01, SR02, SR27, SR32, D01; TC01, TC19, TC25; downstream TK11 (#117), TK12 (#118), TK13 (#119). Source evidence MAP01–MAP05 and SRC01–SRC07 remain as recorded above and in `fit-source-inventory.md`. Every range in §2 is **derived from the pinned profile's declared types** or is an explicitly labelled engineering decision — no range is asserted as protocol conformance, and no fixture oracle exists yet. No SDK was installed or executed, no sample or fixture was acquired, no terms were accepted, and no rights conclusion is drawn. Nothing here is Done, Verified, Accepted or released.
