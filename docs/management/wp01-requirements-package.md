# WP01 proposed requirements baseline

Status: **proposed for founder and engineering review; not approved, implemented, verified, or accepted**  
Package: WP01 ([issue #1](https://github.com/fengguode/DATARA/issues/1)); control hub: [issue #8](https://github.com/fengguode/DATARA/issues/8)  
Affected Customer-User-Stories: CUS01–CUS10. P1 boundaries preserved: CUS11–CUS13.

## 1. Authority and decision labels

This package turns the confirmed product direction into testable proposals without selecting an application stack or beginning WP02.

| Label | Meaning in this document |
| --- | --- |
| **Confirmed** | Founder direction already recorded in the project brief: manual Garmin `.fit` upload; source-first deterministic preparation; persistent history; provider-independent skills; customer-owned model access; deterministic eligibility; manual P0 execution; predefined dashboard and authorized read-only API; user isolation. Datara's model, recommendations, and routines are P1. Commercialization and source-to-skill automation are deferred. |
| **Proposed** | Engineering contract or shortlist that needs approval. It may be revised without changing founder intent. |
| **Pending official verification** | A FIT- or provider-specific fact that must be checked against an official source before approval or implementation. |

Official-source web attempts on 30 September 2026 were denied by the environment (HTTP 401 from search and HTTP 403 from a direct Garmin request). Consequently, this package does **not** assert FIT wire encodings, Garmin message/field numbers, enumerations, epoch, semicircle conversion, CRC behavior, developer-field semantics, or device-specific availability. D01 cannot close until a reviewer records the official Garmin FIT SDK/protocol/profile version, permitted use, source URL or controlled artifact reference, and the mappings below. Examples use Datara's proposed normalized semantics, not claims about the FIT specification.

## 2. Proposed Garmin FIT source contract v0.1

### 2.1 Envelope and disposition

The P0 source is one manually uploaded file, associated with the authenticated user. A submission receives one terminal disposition:

* `accepted`: the whole file satisfies an approved FIT profile and yields at least one supported activity with its required normalized fields;
* `rejected`: no records are persisted as accepted history; return stable reason codes and safe locations/details; or
* `conflict`: valid content collides with existing logical history but is not byte-identical; retain it for explicit resolution without silently replacing either version.

Original bytes are immutable and addressed by `sha256` after upload completion. The accepted normalized result records `source_contract_version`, `fit_profile_version`, `parser_name_version`, `preprocessing_version`, ingestion time, file digest, warnings, and source references. Partial salvage is **not proposed for P0**: a fatal file or required-activity error rejects the file. Non-fatal optional-field problems produce warnings and nulls; they never invent values.

### 2.2 Supported normalized records

These are proposed Datara records. Their exact mapping to official FIT messages and units is pending official verification.

| Record | Cardinality | Required normalized fields | Optional normalized fields | Source reference |
| --- | --- | --- | --- | --- |
| `activity` | one or more per file | `activity_source_id`, `sport`, `start_time`, `end_time`, `elapsed_duration_s` | `local_start_offset_min`, `distance_m`, `active_duration_s`, `device_product`, `device_serial_hash` | file digest plus source message occurrence(s) |
| `session` | one or more per activity | `session_source_id`, `activity_source_id`, `sport`, `start_time`, `end_time`, `elapsed_duration_s` | `subsport`, `distance_m`, `active_duration_s`, `calories_kcal`, `avg_heart_rate_bpm`, `max_heart_rate_bpm` | source message occurrence |
| `lap` | zero or more per session | `lap_source_id`, `session_source_id`, `start_time`, `end_time`, `elapsed_duration_s` | `distance_m`, `active_duration_s`, heart-rate summaries | source message occurrence |
| `sample` | zero or more per session | `session_source_id`, `timestamp` | `heart_rate_bpm`, `distance_m`, `speed_mps`, `cadence_rpm`, `altitude_m`, `latitude_deg`, `longitude_deg` | source message occurrence and field |
| `event` | zero or more per session | `session_source_id`, `timestamp`, `event_type_raw` | `event_value_raw` | source message occurrence |

`*_source_id` values are deterministic identifiers derived from the file digest, record kind, and stable source occurrence; they are not device identifiers. P0 analysis uses `activity` and `session`; lap, sample, and event support provenance and later approved skills. Unknown messages and developer fields are preserved only in a bounded, non-executable diagnostic manifest if approved; they do not silently enter skill inputs.

### 2.3 Canonical types, units, and time

* Durations are decimal seconds (`_s`), distance and altitude are decimal metres (`_m`), speed is metres/second (`_mps`), energy is kilocalories (`_kcal`), heart rate is beats/minute (`_bpm`), cadence is revolutions/minute (`_rpm`), and coordinates are WGS84 decimal degrees (`_deg`). These are **Datara canonical output units**; official source-unit conversions remain pending verification.
* Instants are RFC 3339 UTC strings with a `Z` suffix, ordered by the decoded source instant. Datara must not infer an offset. A separately decoded source offset may populate `local_start_offset_min`; absent offset is null.
* The official FIT timestamp epoch, valid ranges, local timestamp relationship, compressed timestamp handling, and precision are acceptance blockers under D01.
* Decimal conversion and aggregation rules must be versioned. No display rounding is stored as normalized truth.
* Missing optional values are JSON null or omitted according to the consuming schema; `0`, empty string, and a sentinel are never substituted. Non-finite numbers are forbidden.

### 2.4 Validation and rejection matrix

Limits shown as symbolic policy names are deliberately not invented. Approval must assign values from official constraints and fixture evidence.

| Code | Condition | Outcome |
| --- | --- | --- |
| `FILE_NOT_FIT` | Official identification rules fail | reject |
| `FIT_PROFILE_UNSUPPORTED` | Decoded protocol/profile or required feature is outside the approved matrix | reject |
| `FILE_INTEGRITY_FAILED` | An official integrity check required for this variant fails | reject |
| `FILE_TRUNCATED_OR_MALFORMED` | Decoder cannot consume the complete declared structure | reject |
| `RESOURCE_LIMIT_EXCEEDED` | approved file-byte, record-count, nesting, or decode-time limit exceeded | reject |
| `NO_SUPPORTED_ACTIVITY` | no supported activity/session can be produced | reject |
| `REQUIRED_FIELD_MISSING` | required record field cannot be decoded | reject with record/field reference |
| `TIME_INVALID` | instant is undecodable, outside approved range, or required start/end ordering fails | reject |
| `VALUE_OUT_OF_RANGE` | required value violates approved physical/source range | reject; optional value becomes null plus warning if the approved field policy permits |
| `ENUM_UNSUPPORTED` | required sport/activity enumeration has no approved mapping | reject; preserve safe raw code in diagnostic metadata |
| `RECORD_RELATION_INVALID` | session/activity ownership or approved time containment is inconsistent | reject |
| `OPTIONAL_FIELD_INVALID` | optional value cannot be safely normalized | accept with warning and null/omission |
| `EXACT_DUPLICATE` | same user and same SHA-256 digest already exist | idempotent success referencing the existing import/activity; no duplicate history |
| `LOGICAL_CONFLICT` | different digest matches the approved logical-identity key but normalized material fields differ | quarantine as conflict; do not overwrite or merge |

The proposed logical-identity key is `(user, sport, start_time, elapsed_duration_s)` with approved tolerances initially **exact**. This is an engineering heuristic, not a FIT identity claim. D01 must choose: **A (recommended)** exact key plus manual conflict resolution; B a documented tolerance window; or C no logical detection beyond byte duplicates. Resolution creates an auditable supersession/link record; it never mutates original bytes. Identical activities contained in different file bytes therefore surface as a conflict until policy is approved.

### 2.5 Explicit fixture plan

No personal telemetry is permitted. Store synthetic fixture manifests and expected normalized JSON in the repository; store binaries only when their creation and redistribution are permitted. Every fixture records generator/tool version, approved FIT profile version, SHA-256, intent, expected disposition/codes, and license/provenance.

| Fixture family | Minimum cases | Planned case |
| --- | --- | --- |
| Official conformance | smallest supported official sample plus each approved supported variant | TC01 |
| Synthetic happy path | single activity; multi-session/file if officially valid; optional fields present/absent; boundary timestamps/values | TC01 |
| Structure/integrity negatives | non-FIT, empty, truncated, malformed definition/data, integrity failure, unsupported profile/feature | TC01 |
| Semantic negatives | no activity, missing required field, invalid ordering, out-of-range required/optional value, unsupported enumeration, broken relation | TC01 |
| Units/time | one independently calculated conversion per approved source unit; UTC/offset/precision/compressed timestamp cases after official confirmation | TC01, TC04 |
| Idempotency/conflict | same bytes twice; different bytes/same normalized activity; same key/different material value; near-time non-conflict | TC03 |
| Resource limits | exactly at and one over each approved byte/record/time limit | TC01 |
| Provenance/reproducibility | repeat normalization, reordered batch, warning/null lineage | TC02, TC04, TC05 |

Fixture expected values require independent review against the pinned official SDK/profile; parser output cannot be its own oracle.

## 3. Proposed baseline elemental skills v0.1

All candidates are Datara-authored, provider-independent, non-medical, versioned contracts. They analyze only an eligible immutable input snapshot. The shortlist is intentionally small; founder approval under D02 is required before WP03 publication.

| Skill | Athlete question / output | Mandatory input and eligibility | Evaluation criteria |
| --- | --- | --- | --- |
| `activity-summary` | “What training is in this selected period?” Structured totals by sport, activity count, duration and distance; flags data limitations. | Selected UTC interval; accepted activities; `sport`, `start_time`, `elapsed_duration_s`; distance reported only for records where `distance_m` is present. At least 1 activity. | Exact fixture-grounded counts/sums; no unsupported distance imputation; every numeric claim cites input IDs; schema validity; limitation recall 100% on designed negative cases. |
| `training-volume-trend` | “How has recorded training volume changed?” Weekly duration series and evidence-bound descriptive direction (`increased`, `decreased`, `stable`, `insufficient`). | At least 28 elapsed days spanning 4 distinct UTC calendar weeks; at least 1 accepted activity in 3 weeks; mandatory activity-summary fields. Distance is optional and sport-specific. Threshold for direction is an open D02 value. | Exact buckets and totals; expected direction at approved threshold; abstains when coverage fails; no causal, injury, or medical claims; all findings cite weeks/activity IDs. |
| `training-consistency` | “How regularly did I record training?” Active-day count by UTC date, longest active/inactive streak in scope, and descriptive distribution. | At least 28 elapsed days; mandatory summary fields. A day is active iff at least one accepted activity starts in that UTC day (proposed rule). | Exact boundary/streak cases; deterministic multi-activity-day handling; transparent UTC limitation; abstention and citations correct; schema valid. |

Evaluation has four separate layers: deterministic input/metric oracle, schema/contract validation, mocked adapter behavior, and substantive outputs across every supported live model connection. Mocked or schema-valid results do not establish skill quality. Proposed release threshold: all deterministic assertions and safety/unsupported-claim checks pass, all required citations resolve, and an approved rubric reaches a founder-approved score on every connection. Numeric rubric score and trend threshold remain D02 options: **A (recommended)** establish them through a blinded pilot fixture set; B approve fixed thresholds now; C release only `activity-summary` until evidence exists.

## 4. Proposed common skill and model-adapter contracts

### 4.1 `SkillInputEnvelope` v1

Required fields:

* `contract_version`, `snapshot_id`, `snapshot_digest`, `created_at`;
* `scope: {start_time, end_time, timezone_basis: "UTC", activity_ids}`;
* `preprocessing: {source_contract_version, preprocessing_version}`;
* `skill: {skill_id, skill_version}`;
* `observations[]`: typed normalized records with source references;
* `computed_metrics[]`: `{metric_id, value, unit, method_version, input_refs}`;
* `quality`: warnings, excluded-record counts/reasons, coverage values; and
* `user_context`: only fields explicitly declared by the skill and confirmed by the user, each labelled `user_confirmed`.

The deterministic packager canonicalizes ordering and representation before hashing. It includes no credentials, provider prompt syntax, records outside scope, or recommendation metadata. Eligibility returns `{eligible, rule_version, unmet_requirements[], warnings[]}` before an envelope or model request is created.

### 4.2 `SkillOutputEnvelope` v1

Required fields:

* `contract_version`, `skill_id`, `skill_version`, `snapshot_id`;
* `status`: `completed` or `insufficient` (transport/authentication/timeout/schema failures belong to the run, not a successful output);
* `summary` and typed `findings[]` containing `finding_id`, `category`, `statement`, `classification` (`observation`, `computed_metric`, or `assessment`), `evidence_refs[]`, and optional structured `value`/`unit`;
* `limitations[]` and `unmet_inputs[]`; and
* `schema_validation_version`.

P0 outputs cannot use the `recommendation` classification. Every finding requires at least one resolvable evidence reference. Unknown properties, non-finite values, unresolved references, wrong snapshot/skill versions, and unapproved classifications invalidate the result. An invalid result is retained as sanitized failure evidence but never as an assessment.

### 4.3 `ModelAdapter` v1

The execution layer calls a provider adapter with `{run_id, selected_connection_id, model_id, skill_definition, input_envelope, output_schema, timeout_policy}`. The adapter returns a normalized result:

```
{ adapter_version, provider_request_id?, model_id, started_at, completed_at,
  outcome: "response" | "authentication_failed" | "rate_limited" |
           "timeout" | "provider_error" | "cancelled",
  response_payload?, usage?, safe_error? }
```

Adapters own endpoint/transport/authentication and provider response translation; skill definitions own no provider details. The selected connection and model are immutable for a run. There is no fallback, retry to another model/provider, or Datara-owned analysis credential. Same-connection retries, if later approved, create distinct attempts under the run and obey a documented policy. Secrets enter only the adapter's approved secret boundary and must never be serialized in these envelopes, logs, evidence, dashboard, or API.

Initial providers, model identifiers, request parameters, tool/schema features, error mapping, credential store, and retention are **not selected**. They require official provider documentation and D03. Options: **A (recommended)** approve one connection only after a capability spike against this contract, then add a second for portability evidence; B approve two up front; C mock-only (insufficient for P0 release).

## 5. Proposed dashboard outcome and read-only API v1

The predefined outcome is: **an athlete can determine whether the selected period contains sufficient, trustworthy history and understand recorded training volume and its descriptive trend, with evidence and saved run failures visible.** It does not diagnose health, prescribe training, or make P0 recommendations.

The dashboard has four read-only views plus manual controls owned by later packages: (1) readiness/quality and rejected/conflicting imports; (2) weekly activity count, duration and available distance by sport; (3) eligible/ineligible skills with exact reasons; and (4) saved run detail/history with skill/model versions, findings, evidence, limitations and failure state. Viewing saved data makes zero model calls.

Proposed authenticated base path: `/api/v1`. JSON responses include `api_version`; timestamps follow the normalized contract. Collection order and cursor are stable and documented. Resource identifiers are opaque and user-scoped.

| Method/path | Read-only outcome |
| --- | --- |
| `GET /activities?from=&to=&sport=&cursor=&limit=` | normalized activity summaries, source/quality references |
| `GET /activities/{activity_id}` | one activity and authorized provenance |
| `GET /data-readiness?from=&to=` | coverage, warnings, conflicts, eligible skills and unmet rules |
| `GET /analysis-runs?from=&to=&status=&cursor=&limit=` | immutable run history summaries |
| `GET /analysis-runs/{run_id}` | selected snapshot/skill/model, attempts, result or safe failure |
| `GET /analysis-runs/{run_id}/result` | validated output envelope and resolvable evidence links |

All other methods on these routes return `405 METHOD_NOT_ALLOWED`; no create/update/delete endpoint exists under this output API. `401` means unauthenticated, `403` authorized identity lacks access without confirming another user's resource, `404` absent/undisclosable resource, `409` unresolved data conflict where relevant, `422` invalid query, and `429` rate limit. Errors use `{api_version, error:{code,message,request_id,details?}}` and never include credentials or unsafe provider payloads. Responses use an explicit schema/content type version and do not expose original file bytes by default. Pagination defaults/maxima, evidence representation, authorization mechanism, and retention remain D04/D03 decisions.

D04 options: **A (recommended)** approve this training-volume/readiness outcome and endpoints; B limit P0 to activity summary/readiness; C choose a different athlete decision and repeat impact analysis before WP05.

## 6. Dependency-based implementation and validation plan

The identifiers below provide product → system → task → validation traceability. “Planned” is not passed evidence.

| Task | Package / dependency | Deliverable | Requirements | Planned validation |
| --- | --- | --- | --- | --- |
| TK01 | WP01 / none | approve official FIT evidence matrix, source contract, limits, conflict policy and licensed fixture manifest | CUS01–CUS03; SR01, SR02, SR27 | TC01, TC19 |
| TK02 | WP01 / TK01 | approve shortlist, schemas, adapter boundary, dashboard outcome/API and open-decision resolutions | CUS04–CUS09; SR28–SR31 | TC20 |
| TK03 | WP02 / WP01 approved | implement isolated immutable originals, normalization, dedup/conflicts and deterministic history | CUS01–CUS03, CUS10; SR01–SR06, SR20, SR27 | TC01–TC05, TC14, TC19 |
| TK04 | WP03 / WP02 | implement envelopes, baseline skills and deterministic eligibility | CUS03–CUS05; SR07–SR11, SR28, SR29 | TC05–TC07, TC20 |
| TK05 | WP04 / WP03 | implement approved customer connection(s), secret boundary and manual run lifecycle | CUS06–CUS07; SR12–SR15, SR30 | TC08–TC10, TC20 |
| TK06 | WP05 / WP02 and WP04 | persist immutable results; deliver approved dashboard and read-only API | CUS08–CUS10; SR16–SR21, SR31 | TC11–TC14, TC20 |
| TK07 | WP06 / WP01–WP05 | verify a fixed candidate, then conduct separate athlete validation and founder acceptance | CUS01–CUS10; all P0 SRs | TC01–TC15, TC19, TC20 |
| TK08 | WP07 / WP06 acceptance | P1 recommendations, routines, comparison and feedback; no silent changes | CUS11–CUS13; SR22–SR26 | TC16–TC18 |

WP02 must not start until TK01/TK02 contracts needed for implementation are approved. Stack/topology selection and estimates remain D05, after contract approval. WP07 cannot supply P0 behavior. Deferred commercialization and source-to-skill automation have no implementation task in this plan.

## 7. Baseline gate and open decisions

WP01 is ready for stakeholder review—not complete or accepted—when the registry integrity check passes and reviewers can resolve:

1. **D01:** official FIT version/evidence, accepted variant matrix, mappings, numerical/resource limits, exact-vs-tolerant conflicts, and fixture redistribution;
2. **D02:** skill shortlist, trend method/threshold, minimum coverage and substantive rubric/score;
3. **D03:** first connection strategy, supported capabilities, credential boundary and retention;
4. **D04:** dashboard outcome, endpoint surface, pagination/evidence/auth details;
5. **D05:** stack, topology, owners and estimates only after D01–D04.

The registry check is management-record validation only. TC01–TC20 and VAL-P0 remain not run; there is no product, live-model, system, athlete-validation, or stakeholder-acceptance evidence in WP01.
