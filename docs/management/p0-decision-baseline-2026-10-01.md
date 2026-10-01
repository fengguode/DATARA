# P0 decision selections — 1 October 2026

Status: selected product and engineering direction under founder delegation; detailed contracts, source rights, capability evidence and G0 remain pending. This is a decision record, not implemented or verified software.

Tracking: [WP01 #1](https://github.com/fengguode/DATARA/issues/1), [control #8](https://github.com/fengguode/DATARA/issues/8). Scope: WP01–WP06, CUS01–CUS10, SR01–SR21/SR27–SR31. No P1 scope or requirement identifier is added. Base: `0bf60cb4d1da2f41cf4aa3a11ff71fb17cc8f80b`; branch: `codex/p0-decision-baseline`.

## Authority and evidence state

The founder selected FIT SDK 21.217.0 in [the D01 decision](https://github.com/fengguode/DATARA/issues/1#issuecomment-5924582523), then instructed Yi to make D01–D05 decisions with Yu and ask for support only where needed. [Assignment and delegated authority](https://github.com/fengguode/DATARA/issues/1#issuecomment-5924622504) records that instruction. The founder subsequently explicitly selected **OpenAI and DeepSeek as the first integrations**, recorded in [D03 steering](https://github.com/fengguode/DATARA/issues/1#issuecomment-5924686899).

Yi selects the choices below with [Yu's product review](https://github.com/fengguode/DATARA/issues/1#issuecomment-5924661831) and [Feng's feasibility advice](https://github.com/fengguode/DATARA/issues/1#issuecomment-5924677207). These are selections within existing P0 scope under the current delegation, rather than fabricated individual founder endorsements. They supersede the *undecided option selection* in earlier proposals only where explicitly stated here. Preserve earlier reports and failures as historical evidence. Detailed schemas and source mappings do not become approved merely by linking this record.

Runtime contributors: Yi `/root`, Yu `/root/yu_product`, Feng `/root/feng_decisions`. Yu and Feng performed real separate read-only runs; requested role settings were selected through the runtime, but automatic native repository configuration loading is unconfirmed. GitHub publisher: `fengguode`. Final nonauthor documentation/evidence confirmer: Quality Manager Wang Xiaofeng; independent technical review: Dennis Windmaier. See [candidate review evidence](../team/reviews/p0-decision-baseline-review-2026-10-01.md). Exact-head PR confirmation, merge authorization, TC15 founder acceptance and named deployment authorization remain separate.

## Selected choices and remaining gates

| Decision | Selected direction | Remaining evidence or factual input |
| --- | --- | --- |
| D01 | Official Garmin FIT SDK 21.217.0; activity imports initially single-session running/cycling, indoor/outdoor; explicit supported mappings, immutable bytes, exact duplicate/conflict handling and pilot limits below. | Exact artifact/profile/hash and permitted use; field/unit/time/integrity matrix and independent lawful fixture oracles. |
| D02 | All three existing skills: activity summary, recorded volume trend, recorded consistency. UTC deterministic metrics and mandatory per-connection evaluation below. | Frozen schemas/fixtures and independently reviewed substantive rubric; real-model quality evidence before release. |
| D03 | Both OpenAI and DeepSeek in the initial provider target; explicit selected supported model, encrypted server-side customer keys, validated results, no fallback or automatic retry. | Exact model/capability matrix, provider/account/region suitability, retention disclosure and bounded authorized live evaluation. |
| D04 | Recorded-volume and data-readiness dashboard plus the existing read-only resource family; owner authorization, evidence and stable cursor behavior below. | Exact schemas, access/retention review, UI specifications and rendered/API consistency evidence. |
| D05 | Django 5.2 LTS/Python, PostgreSQL 17, private original-file storage, app session identity, OpenBao Transit for credentials, Linux container reference topology. | Actual pilot location/audience/operator; exact dependency pins/setup evidence, operational/security review and measured estimates. |

A decision can be selected while its conformance evidence remains pending. **G0 is not satisfied**. Keep aggregate TK01/TK02 and downstream product work gated on the [existing implementation plan](p0-implementation-plan.md). No task, SR or case is marked Done, Verified, Accepted or Released by this document.

## D01 — FIT source and persistent intake

Selected source: manually supplied original `.fit` activity files, including files obtained using Garmin Connect's Export File option. SDK baseline is 21.217.0, also available as the official [Python release](https://github.com/garmin/fit-python-sdk/releases/tag/21.217.0), dated 22 September 2026. Use the associated official profile from the exact chosen artifact; do not infer its numeric header version solely from the SDK version. Pin package checksum, release commit, profile identifier and dependency/license inventory in TK09/TK10. Updates require a reviewed compatibility change and affected fixture checks before changing the baseline.

Protocol coverage target is FIT 1.0 and 2.0 using the official decoder. Initial semantic support is single-session running and cycling, indoor and outdoor. Exact sport/subsport enumerations must be mapped from the pinned profile. Do not use a device-model allowlist as a substitute for file conformance. New device fields need no new analysis promise: original bytes are preserved, while normalized/skill data use only approved mappings. Unsupported file types, sports, multisport/chained layouts and required semantics receive a stable explanation. P0 source scope excludes wellness, planned workout/course and arbitrary archive imports.

Required normalized activity inputs: source reference/digest, sport, session UTC start instant and valid elapsed duration. Retain official timer duration as a separate optional metric. Duration-based P0 volume means **recorded elapsed activity duration**, explicitly labelled; do not silently switch between elapsed and timer time. Distance, record samples, GPS and heart rate are optional. Missing GPS is valid for indoor activities. Absent/invalid optional values become null with a quality warning under the field contract; no imputation. Reject missing/invalid required fields, broken required relations, malformed structure or failed integrity for the whole file. Validate FIT invalid sentinels, scales/offsets, compressed timestamps, header and CRC through pinned official rules. Engineering mappings and ranges belong to TK10; this record does not invent them.

Unknown optional/developer fields may be ignored for normalization only when the supported file structure is independently verified; report the ignored data and retain the original. Reject a required interpretation that depends on an unknown field, native override or unverified feature. Decoder success alone is insufficient evidence under SR27.

Chosen pilot resource limits, inclusive when every other check passes:

- 16 MiB per file; 50 files and 128 MiB of submitted bytes per batch.
- 200,000 decoded messages and 100,000 sample records per file.
- 60 seconds wall time and 512 MiB worker memory per file; one parser worker per host initially.
- Enforce byte limits while receiving and resource limits in an isolated worker. A timeout/limit failure creates no accepted activity. Exactly-at/one-over and cleanup are required tests.

These are conservative application policy choices, not Garmin limits or measured capacity claims. TK13 and the runtime spike must validate enforcement and realistic fixture fit; any adjustment must be recorded before freezing conformance or promising import coverage.

Same owner + same SHA-256 bytes is idempotent and references existing history. Different bytes with the exact logical tuple `(owner, sport, UTC start, elapsed duration)` are quarantined as a possible conflict. This is a conservative application heuristic, not comprehensive duplicate detection or authoritative FIT identity. User resolution offers keep existing, replace via an auditable supersession, or retain both explicitly; preserve both valid originals and lineage. Never silently merge, use tolerance or overwrite. Normal history and skill snapshots exclude unresolved candidates.

Commit an accepted original and normalized relations as one visible operation using durable staging/reconciliation across file/DB stores. A batch reports per-file outcomes; one rejected file does not undo independently accepted files. A file contributes no partial accepted activity. Discard rejected raw bytes promptly; remove abandoned temporary uploads within 24 hours. Keep safe disposition metadata, not raw telemetry in logs.

Fixtures: choose DATARA-authored synthetic data plus separately permissioned controlled examples. Preserve generator version, official mapping reference, independent expected values and hash. Publish synthetic binaries or official samples only after documented creation/distribution rights review. Garmin's [SDK licence](https://github.com/garmin/fit-python-sdk/blob/main/LICENSE.txt) was located; its existence is not owner acceptance or a conclusion about redistribution. This assignment does not accept binding terms or copy SDK/source/sample files into DATARA.

Trace: CUS01–CUS03/CUS10; SR01–SR06/SR20/SR27; TK09/TK10/TK13/TK14/TK17/TK20, aggregate TK01; TC01–TC04/TC19 and existing detailed cases.

## D02 — elemental skills and evaluation

Select `activity-summary`, `training-volume-trend` and `training-consistency` as the P0 library target. No candidate is described as evaluated/released until its evidence passes. Numeric calculation and eligibility belong to conventional software; the model produces constrained descriptive findings and limitations tied to prepared evidence.

Time policy: UTC instants; date scopes are half-open `[start, end)`; UTC calendar weeks begin Monday 00:00. Keep that basis visible to users. A recorded activity belongs to its start date/week; no redistribution across midnight. Metric arithmetic uses canonical fixed precision, not a floating-point near-equality threshold.

- Summary: at least one accepted, nonconflicting activity. Count and elapsed duration totals by sport; report distance only for activities with valid distance and disclose distance coverage. Every number is a prepared metric with activity references.
- Trend: use the last four complete UTC calendar weeks wholly inside the selected scope (at least 28 days); require at least one accepted activity in at least three of those weeks. Other selected activities remain visible in summary but outside this comparison. Compare elapsed-duration totals of the earlier two weeks against the later two; report exact absolute difference, percentage when earlier total is positive, and increased/decreased/equal according to the difference's sign. Zero denominator means percentage unavailable. A week with no uploaded activity contributes zero **recorded** duration, with a missing-records limitation; it does not prove no training or complete coverage.
- Consistency: selected scope covers at least 28 complete UTC days and includes an accepted activity. An active day has at least one included activity starting that UTC day; count it once. Show active-day count and longest consecutive runs of recorded-active days and days with no recorded activity within the scope, including leading/trailing gaps. No activity across the selected scope makes the skill ineligible. Missing uploads and the UTC basis are explicit limitations.

No medical, injury-risk, physiological significance, prescription or P0 recommendation claim is supported. No uploaded activity means no record in the selected snapshot. It is not evidence that training did not happen.

Choose an initial evaluation suite of at least ten distinct cases per skill, including positive, insufficient, missing optional, conflict-exclusion, UTC boundary and arithmetic/zero-baseline cases. For every released provider/model pair, evaluate each applicable skill on the frozen suite with at least three independent attempts per case. Numerical accuracy, resolvable evidence, limitation disclosure, schema/version binding and prohibited-claim checks must all pass in every accepted output. Five substantive dimensions—faithful interpretation, clarity, relevance, limitation explanation and useful organization—score 0/1/2 each. Every accepted case needs at least 8/10 and no zero dimension. Independent reviewers freeze anchors and expected examples before evaluation; revise an inadequate rubric through a recorded change rather than tuning it to failed outputs. These are selected initial quality criteria, not observed results or a statistical performance guarantee.

Trace: CUS03–CUS05; SR07–SR11/SR28–SR29; TK30–TK35/TK21/TK42/TK44 and existing evaluation tasks; TC05–TC07/TC20.

## D03 — two customer model integrations

The founder explicitly selected **OpenAI and DeepSeek**. Both are in the initial P0 target. Implement/spike adapters sequentially if practical; do not silently reduce the provider target to one. Skills share a provider-independent input/output contract. Only evaluated provider/model/skill combinations are executable; unsupported choices show a reason. Exact model IDs, available snapshots/aliases, endpoint and adapter versions are frozen in the capability matrix during TK36–TK38, using actual account access and fresh official documentation. Record requested and returned model identifiers; disclose mutable aliases and never claim deterministic model answers or silently replace a model.

Use nonstreaming, text-only, stateless requests for the first capability contract; no external tools, file/image uploads or conversation service. OpenAI adapter target: Responses API with supported schema output and `store:false`. DeepSeek adapter target: its documented Responses format with supported schema output; translate only documented supported parameters. Reject incompatible capability manifests before execution. App-side schema, snapshot/skill version, evidence resolution and numeric checks run independently for both. Refusal, truncation, empty payload or invalid output is a visible failure, never a successful assessment.

Official [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) documents schema restrictions; [data controls](https://developers.openai.com/api/docs/guides/your-data) describe retention. `store:false` is not proof of zero data retention. DeepSeek's [Responses guide](https://api-docs.deepseek.com/guides/responses_api/) documents differences including unsupported/ignored parameters, stateless response handling and `text.format` support. Statelessness is not a general assurance about provider logging, training or caching. Endpoint-specific terms, retention and regional/account eligibility must be reviewed before real athlete data. Provider selection creates no service entitlement.

Egress allowlist: selected prepared metrics, relevant dates/sport categories, quality/limitations and snapshot-local opaque evidence IDs needed by the skill. Exclude original FIT bytes, GPS, device serials, account identity, unrelated activities and keys. No raw provider reasoning text is needed for the result/evidence record. Use the minimum fields each skill declares.

Credentials: owner submits through the authenticated app over TLS; encryption and storage occur server-side through OpenBao Transit. Store ciphertext and owner-scoped secret references in PostgreSQL; the runtime retrieves only the selected owner's key for the adapter call. Transit access/key material is supplied outside Git/repository/telemetry, and application logs/errors/UI/API never expose keys. Separate runtime and migration/admin permissions. Freeze provisioning, restricted decryption access, rotation, recovery and key-version policy in TK39–TK41/TK66/TK72. App deletion disables connection use immediately and removes live ciphertext within 24 hours; instruct the owner to revoke the provider key separately. Key removal in DATARA cannot imply revocation at the provider.

Runs bind one immutable snapshot, the user-chosen model/connection and one or more skill versions. Reject creation if any selected member is ineligible; no silent dropped skill. One attempt per child, 120-second deadline, no automatic transport/model retry in P0. Authentication, rate limit, timeout, cancellation/interruption, provider/server, refusal, incomplete and validation failures have separate safe outcome codes. An explicit rerun creates a new run. A process interruption marks unfinished attempts interrupted/failed and performs no automatic paid redispatch. Successful child outputs remain inspectable when another child fails. Select aggregate `partial` for mixed child outcomes; synchronize SR14/state schemas and recovery cases in TK50/TK51 before coding—this document does not silently modify the registry.

Real calls require available customer-owned accounts/credentials, provider/location eligibility and a named spend cap. No call or budget is authorized or executed here. Release targets both providers with separate real-model evidence; mocks do not replace either gate.

Trace: CUS06–CUS07/CUS10; SR12–SR15/SR20–SR21/SR30; TK36–TK41/TK50/TK51/TK66/TK70/TK72 and aggregate TK02; TC08–TC10/TC14/TC20.

## D04 — dashboard, read API and retained evidence

Choose recorded training volume and **data readiness for the selected analysis**. The dashboard contains imported history/quality/conflicts, weekly recorded volume by sport, eligibility reasons, and saved run/results/failures with evidence. It also connects the existing manual upload, connection selection and execution controls. All views use saved/prepared values; viewing or retrying a failed read makes no model call.

Retain the existing `/api/v1` GET families: activities and detail; data-readiness; analysis-runs and detail; analysis-runs/{run_id}/result. A multi-skill result resource contains child skill results and their statuses, with distinct failure metadata; it never flattens partial failure into a successful combined assessment. Exact response and error JSON Schemas remain TK56/TK60/TK63 work.

Choose opaque, owner-scoped IDs; authenticated server-derived owner on every resource/evidence access. Lists default to 50, maximum 200. Cursor is signed and bound to owner, filters, stable order and the first page's high-water mark; newest-first ordering uses creation/start instant plus opaque ID as deterministic tie-breaker. Concurrent later inserts stay outside that pagination traversal. Freeze deletion/filter/cursor-expiry behavior with contract fixtures, rather than promising consistency from an unspecified cursor.

Response/error version is explicit JSON `api_version`. Unauthenticated is 401; inaccessible/missing owner resource is generic 404; 403 is for operation-level denial without confirming another owner's object; invalid query 422; rate limit 429; methods other than GET/HEAD on output resources 405 with approved Allow semantics (transport-only OPTIONS is handled separately). App mutations remain separate authenticated/CSRF-protected routes. No output-API token can mutate data, run a model or access credentials.

API read tokens are random, owner-bound, read-scope-only, hash-stored, displayed once on issuance, revocable and expire after 90 days. Issuance is a user action inside the app, not performed by this assignment. Sessions serve the browser; provider keys never double as output-API tokens. Evidence returns authorized structured references/metric lineage; originals are accessed only through the authorized app's explicit original-file path, not by public/static URLs or the output API.

Choose persistent account-lifetime originals, normalized history and saved results until owner-requested deletion, with no silent ageing out. Connections/tokens disable immediately on revocation; owner deletion removes live target data within 24 hours, and encrypted backups expire within seven days. Restores must reapply a separately retained deletion ledger before serving data. Operational metadata logs retain 30 days with no secrets/raw telemetry; evidence references disclose deleted/unavailable items instead of inventing values. Deletion, export and audit controls require explicit SR/contract traceability through existing security/operations tasks before a real-data pilot; selecting the policy is not claiming those controls exist or meet an unknown jurisdiction's duties.

Choose WCAG 2.2 AA as the accessibility design target, keyboard and screen-reader journeys, text/table equivalents for charts, 320 CSS-pixel reflow, 200% zoom and reduced-motion support. Desktop/mobile web layouts; no native mobile app. Verify current stable Chrome and Edge plus Firefox keyboard flows; screen-reader evidence must name the actual tool/environment. This is a selected target awaiting UI design/checks, not a conformance claim.

Trace: CUS08–CUS10; SR16–SR21/SR31; TK56/TK60/TK63/TK66/TK72/TK73; TC11–TC14/TC20 and current accessibility cases.

## D05 — reference implementation and operations

Select Django 5.2 LTS on a supported Python release compatible with FIT SDK 21.217.0, PostgreSQL 17 and server-rendered responsive dashboard with small progressive UI components. Keep API, session identity, authorization and upload/run orchestration in one application. Use private owner-scoped file storage for immutable originals and durable DB-backed job records. A separate bounded worker executes parsing/model jobs without adding a message broker to the initial pilot. Pin exact patch/runtime/image/dependency hashes after the setup/security spike, before G0; major-version selection is insufficient reproducibility evidence.

Use built-in Django authentication/session primitives for an operator-provisioned private pilot, secure HttpOnly/SameSite session cookies, CSRF for app mutations and login/rate-limit/session invalidation contracts. No mandatory external OIDC service or public self-registration in this pilot. User isolation remains required with at least two disposable identities; a private pilot does not waive CUS10. Public onboarding, federation or a later public-service operating scope needs its own reviewed extension.

Reference topology: Linux containers on one operator-controlled host; HTTPS reverse proxy; private network for app/worker/PostgreSQL/OpenBao; no publicly exposed database or secret store; encrypted host/storage/backups with keys outside the repository. Windows/macOS development may use a reviewed compatible container environment, without requiring installation on the founder's machine in this assignment. Actual pilot hosting country, operator and audience remain pending factual inputs; synthetic development can proceed when technical G0 inputs are ready. No infrastructure is provisioned here.

Application DB role is neither table owner, superuser nor BYPASSRLS. Owner-scoped service checks are mandatory; use carefully reviewed forced RLS/owner-key constraints as additional protection. Every job and transaction must bind its owner and prevent leaked connection-pool context. Separate schema migration/admin roles. Recovery must preserve source/normalized/result relationships and immutable versions.

Choose encrypted daily backups, seven-day retention and initial **RPO 24 hours / RTO 4 hours** objectives. These are pilot objectives to verify by restore, not proven guarantees. Record startup/migrations/health, storage capacity, pending-job recovery, deletion-ledger reapplication, credential/key recovery, incident contact, version compatibility, rollout and rollback. Runtime operator and incident owner must be named before real data or deployment.

Alternative considered: ASP.NET Core 10 + PostgreSQL is viable with equivalent storage/identity/secret controls. Django is selected for direct official FIT Python integration and consolidated app/auth/file patterns, avoiding an additional frontend/backend platform split in P0. This is a design choice under delegation, not an assertion about the founder's existing framework expertise. No Kubernetes or recommendation service is required.

Estimate after approved schemas, lawful synthetic fixtures and representative import/run/persistence/security spikes. Separate measured build/operator effort from forecast ranges and customer provider charges. No dates, precise person-days, provider prices or infrastructure spend are fabricated. Decision to use a topology is not permission to purchase, deploy, accept terms or send athlete data.

Official feasibility references: [Django 5.2](https://docs.djangoproject.com/en/5.2/), [Django authentication](https://docs.djangoproject.com/en/5.2/topics/auth/), [file management](https://docs.djangoproject.com/en/5.2/topics/files/), [PostgreSQL row security](https://www.postgresql.org/docs/17/ddl-rowsecurity.html), [OpenBao Transit](https://openbao.org/docs/secrets/transit/), [.NET lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/microsoft-net-and-net-core), [WCAG 2.2](https://www.w3.org/TR/WCAG22/). Framework facts support feasibility, not an executed DATARA runtime.

## Next authorized work and founder support

Use existing backlog records; do not create a duplicate assignment tree. Continue W0 source/rights inventory and contract/schema/test design, incorporating these selections after independent review. Start with TK09/STK001/STK002 source evidence, then TK10 supported mappings. Parallel W0 preparation may freeze skill/input/output/adapter/dashboard/auth/retention contracts in the existing lanes. Add or adjust derived SR and verification coverage through the usual synchronized change process for resource/recovery/accessibility/retention details and aggregate partial state. Do not implement against unresolved wire details.

Only factual or separately authorized inputs go back to the founder:

1. Pilot users, hosting/operating country and the actual runtime/incident owner.
2. Available customer-owned OpenAI/DeepSeek access and a bounded spend authorization when real capability/quality tests are prepared.
3. SDK/provider/hosting terms acceptance by the authorized owner if required for actual use, and qualified jurisdiction/rights review where applicable.

Founder final athlete validation and release/deployment approval remain the later lifecycle gates. Product selection work and independent document review require no repeated approval poll.
