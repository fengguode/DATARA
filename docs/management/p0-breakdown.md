# P0 requirement breakdown

**Status:** Proposed requirements and planned work; no product verification or founder acceptance is claimed. The GitHub Project is the shared central backlog/status record. This document and the local JSON registry mirror requirement content and traceability.

**Coordination:** [Issue #28](https://github.com/fengguode/DATARA/issues/28) owns the breakdown; [PR #33](https://github.com/fengguode/DATARA/pull/33) and continuation [PR #35](https://github.com/fengguode/DATARA/pull/35) have merged; [pull request #275](https://github.com/fengguode/DATARA/pull/275) also merged externally at checkpoint 24925be; the final evidence continuation is linked from [issue #28](https://github.com/fengguode/DATARA/issues/28). Assignment issues [#29](https://github.com/fengguode/DATARA/issues/29), [#30](https://github.com/fengguode/DATARA/issues/30), [#31](https://github.com/fengguode/DATARA/issues/31), and [#32](https://github.com/fengguode/DATARA/issues/32) identify bounded role work. All 238 P0 records are published as linked issues and Project items: 10 CUS, 23 Features, 46 SR, 64 Tasks and 95 Subtasks. All 228 primary child-parent relationships and the complete content/field/dependency/link snapshot have passed primary audit. Independent Quality Manager publication QA passes for all 238 records, 228 primary parents and 1,481 linked requirement references. Founder confirmation and product evidence remain separate gates. See the [GitHub mapping](github-requirements-map.json) for exact identities and captured fields.

## Requirement hierarchy and interpretation

CUS records state customer outcomes. Feature records group proposed product capabilities under one or more CUS outcomes. SR records state verifiable obligations that derive from CUS and apply across relevant perspectives. Task records identify bounded work; STK leaves refine a task for planning, but inherit its parent task dependencies and WP prerequisites even when their own `dependencies` array is empty. Verification cases state planned checks. None is evidence until run on a fixed candidate.

Feature, STK, and perspective-assessment arrays, `.github` readback metadata, plus the `feature_ids` and `child_task_ids` links are additive planning extensions to registry schema 2.0. The existing checker validates only the legacy CUS/SR/TK/WP/TC core; these extension layers receive direct traceability and independent QM/Reviewer audit.

Requirement status (`Draft derived requirement`, `Proposed`, `Planned`, `Blocked on decision`) describes planning state. It does not mean implemented, verified, accepted, or released. The GitHub Project is the authoritative shared status record; the JSON and these documents are synchronized mirrors, not a second backlog.

## First P0 delivery sequence

| Order | Work package | Dependency | Issue | Package outcome |
| --- | --- | --- | --- | --- |
| 1 | WP01 | None | [Issue #1](https://github.com/fengguode/DATARA/issues/1) | Approve source evidence, supported-file outcomes, skill/model/output contracts, and open decisions needed to start implementation. |
| 2 | WP02 | WP01 | [Issue #2](https://github.com/fengguode/DATARA/issues/2) | Implement persistent original/history handling and deterministic preprocessing. |
| 3 | WP03 | WP01, WP02 | [Issue #3](https://github.com/fengguode/DATARA/issues/3) | Implement approved provider-independent skills and eligibility outcomes. |
| 4 | WP04 | WP03 | [Issue #4](https://github.com/fengguode/DATARA/issues/4) | Implement selected customer model connections and manual run outcomes. |
| 5 | WP05 | WP02, WP04 | [Issue #5](https://github.com/fengguode/DATARA/issues/5) | Deliver persistent results, dashboard, and authorized read-only output. |
| 6 | WP06 | WP01–WP05 | [Issue #6](https://github.com/fengguode/DATARA/issues/6) | Verify a fixed candidate, then separately conduct TC15 athlete validation and founder acceptance. |

The first P0 release milestone requires the WP01–WP06 gates, passing evidence for applicable P0 SRs, and separate TC15 athlete validation/founder acceptance. Finishing this requirements breakdown is a planning deliverable only; it does not mean the P0 product is implemented or release-ready. WP07 and CUS11–CUS13 remain P1 and are not expanded here.

## P0 customer outcomes and features

### [CUS][frontend]Upload supported activity files — CUS01

**Story:** As an athlete, I want to upload supported activity files so that I can rely on the imported data.

**Outcome:** Accept manually uploaded Garmin .fit files only through a published source specification.

**Features:** FEAT01

#### [Feature][backend]Define supported activity source and file disposition — FEAT01

Priority: P0; status: Proposed; readiness: Proposed; work package: WP01; parents: CUS01; SR links: SR01, SR02, SR27, SR32; feature dependencies: none asserted; WP prerequisites: none listed.

Define the supported FIT source boundary and classify submitted files with explicit outcomes under an approved source contract.
### [CUS][frontend]Return to uploads and training history — CUS02

**Story:** As an athlete, I want my uploads and training history retained so that I can return to earlier activities.

**Outcome:** Preserve original uploads and normalized history, with explicit duplicate and conflict handling.

**Features:** FEAT02

#### [Feature][database]Preserve original uploads and conflict-aware history — FEAT02

Priority: P0; status: Proposed; readiness: Proposed; work package: WP02; parents: CUS02; SR links: SR03, SR04, SR33; feature dependencies: FEAT01; WP prerequisites: none listed.

Preserve accepted source bytes and provenance while handling repeated uploads and logical conflicts without silent overwrite.
### [CUS][backend]Prepare activity data consistently — CUS03

**Story:** As an athlete, I want activity data prepared consistently so that analyses are repeatable.

**Outcome:** Validate, normalize, calculate, and package skill inputs without AI.

**Features:** FEAT03, FEAT21

#### [Feature][backend]Prepare activity data deterministically — FEAT03

Priority: P0; status: Proposed; readiness: Proposed; work package: WP02; parents: CUS03; SR links: SR05, SR06; feature dependencies: FEAT01, FEAT02; WP prerequisites: none listed.

Normalize supported activity data reproducibly using conventional processing without inference.

#### [Feature][backend]Package scoped skill inputs with provenance — FEAT21

Priority: P0; status: Proposed; readiness: Proposed; work package: WP03; parents: CUS03; SR links: SR07, SR28, SR34; feature dependencies: FEAT03; WP prerequisites: none listed.

Package only selected, provenance-linked prepared data required by a skill in a versioned envelope.
### [CUS][frontend]Choose evaluated expertise options — CUS04

**Story:** As an athlete, I want evaluated expertise options so that I can choose a useful analysis.

**Outcome:** Offer a small evaluated Datara-created library with explicit inputs, methods, outputs, and versions.

**Features:** FEAT04, FEAT30, FEAT31

#### [Feature][backend]Define the baseline skill library — FEAT04

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP03; parents: CUS04; SR links: SR08, SR09, SR29, SR50, SR51; feature dependencies: none asserted; WP prerequisites: WP01, WP02.

Specify a small Datara-created set of provider-independent elemental skills with explicit inputs, applicability, method, outputs, version and evaluation references; the actual shortlist and release threshold remain subject to D02.

#### [Feature][backend]Trace skill methods and evaluation evidence — FEAT30

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP03; parents: CUS04; SR links: SR51, SR52; feature dependencies: none asserted; WP prerequisites: WP01, WP02.

Keep proposed skill methods connected to reviewed source references and separate deterministic, contract and substantive evaluation evidence before release.

#### [Feature][frontend]Explain eligibility and skill choices — FEAT31

Priority: P0; status: Proposed; readiness: Proposed; work package: WP03; parents: CUS04, CUS05; SR links: SR53, SR58; feature dependencies: none asserted; WP prerequisites: WP01, WP02.

Present skill declarations and eligibility gaps as understandable text and provide operable catalog states without implying unsupported analysis.
### [CUS][frontend]Understand unavailable analyses — CUS05

**Story:** As an athlete, I want unavailable analyses explained so that I know which inputs are missing.

**Outcome:** Exclude skills whose required inputs are unavailable and explain the missing requirements.

**Features:** FEAT05, FEAT31

#### [Feature][backend]Determine skill eligibility — FEAT05

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP03; parents: CUS05; SR links: SR10, SR11, SR53; feature dependencies: none asserted; WP prerequisites: WP01, WP02.

Evaluate declared mandatory inputs, history coverage and approved quality rules deterministically for a selected dataset and skill version before execution.

#### [Feature][frontend]Explain eligibility and skill choices — FEAT31

Priority: P0; status: Proposed; readiness: Proposed; work package: WP03; parents: CUS04, CUS05; SR links: SR53, SR58; feature dependencies: none asserted; WP prerequisites: WP01, WP02.

Present skill declarations and eligibility gaps as understandable text and provide operable catalog states without implying unsupported analysis.
### [CUS][backend]Use selected customer model access — CUS06

**Story:** As an athlete, I want to use my chosen model account so that I control access for my analyses.

**Outcome:** Use the customer's own API access for analysis; keep skills independent of model interfaces.

**Features:** FEAT06, FEAT32, FEAT33, FEAT34, FEAT35

#### [Feature][backend]Use customer-selected model connections — FEAT06

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS06; SR links: SR12, SR13, SR30, SR54, SR55, SR56, SR57, SR59; feature dependencies: none asserted; WP prerequisites: WP01, WP02, WP03.

Support analysis through an explicitly selected customer model connection while protecting customer credentials and preventing silent connection substitution.

#### [Feature][backend]Declare connection capabilities — FEAT32

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS06; SR links: SR55, SR57; feature dependencies: none asserted; WP prerequisites: WP01, WP03.

Represent supported model-connection capabilities and block execution when the selected connection cannot meet a skill's declared needs.

#### [Feature][security]Protect selected connection credentials — FEAT33

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS06; SR links: SR13, SR54, SR59; feature dependencies: none asserted; WP prerequisites: WP01, WP02.

Keep credential handling confined to a documented customer-scoped protection boundary and exclude secrets from skill, output, log and evidence surfaces.

#### [Feature][frontend]Select a supported customer model — FEAT34

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS06; SR links: SR12, SR56; feature dependencies: none asserted; WP prerequisites: WP01, WP03.

Require an explicit user selection of a supported connection and model for analysis, and show unavailable/unsupported states without changing that selection.

#### [Feature][operations]Bound model request lifecycle evidence — FEAT35

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS06; SR links: SR57, SR59; feature dependencies: none asserted; WP prerequisites: WP01, WP03.

Specify the outcome information needed to diagnose customer model connection failures without exposing credentials, and identify unresolved lifecycle questions.
### [CUS][frontend]Run analyses and see failures — CUS07

**Story:** As an athlete, I want to run selected analyses and see failures clearly so that I can trust the outcomes.

**Outcome:** Execute selected eligible skills against a defined dataset and report failures explicitly.

**Features:** FEAT07, FEAT40, FEAT44, FEAT46

#### [Feature][backend]Manual run lifecycle — FEAT07

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS07; SR links: SR14, SR15, SR70, SR74; feature dependencies: FEAT05, FEAT06; WP prerequisites: none listed.

The user can submit an eligible manual run using the explicitly selected dataset, skill, and customer model and see the actual terminal outcome.

#### [Feature][backend]Validated output boundary — FEAT40

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS07, CUS08; SR links: SR15, SR70, SR72; feature dependencies: FEAT07; WP prerequisites: none listed.

Only a valid response matching the approved result contract and requested snapshot/skill may be presented as a finding; invalid responses remain explicit failures.

#### [Feature][security]Safe credential and failure outputs — FEAT44

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS07, CUS10; SR links: SR74; feature dependencies: FEAT06, FEAT07; WP prerequisites: none listed.

Saved user-visible run outcomes omit credential material and unredacted provider payloads while preserving explicit failure status.

#### [Feature][frontend]Accessible run and result interactions — FEAT46

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS07, CUS08, CUS09, CUS10; SR links: SR75, SR76; feature dependencies: FEAT09, FEAT43; WP prerequisites: none listed.

The approved P0 run, history, denial, and retrieval interactions remain keyboard operable and communicate errors/status semantically.
### [CUS][database]Revisit analyses with evidence — CUS08

**Story:** As an athlete, I want to revisit analyses with their evidence so that I can understand my history.

**Outcome:** Persist results with evidence, input references, skill version, model, and run date.

**Features:** FEAT40, FEAT08, FEAT41, FEAT46

#### [Feature][backend]Validated output boundary — FEAT40

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS07, CUS08; SR links: SR15, SR70, SR72; feature dependencies: FEAT07; WP prerequisites: none listed.

Only a valid response matching the approved result contract and requested snapshot/skill may be presented as a finding; invalid responses remain explicit failures.

#### [Feature][backend]Immutable result lineage — FEAT08

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS08; SR links: SR16, SR17, SR72; feature dependencies: FEAT07, FEAT40; WP prerequisites: none listed.

The owner can revisit each saved assessment with its input, preprocessing, skill/model, run-time, and evidence references while earlier runs remain intact.

#### [Feature][backend]Snapshot-bound evidence links — FEAT41

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS08; SR links: SR16, SR72; feature dependencies: FEAT08; WP prerequisites: none listed.

An owner can resolve finding evidence to the assessment input snapshot; broken, foreign, or mismatched references are visibly unavailable.

#### [Feature][frontend]Accessible run and result interactions — FEAT46

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS07, CUS08, CUS09, CUS10; SR links: SR75, SR76; feature dependencies: FEAT09, FEAT43; WP prerequisites: none listed.

The approved P0 run, history, denial, and retrieval interactions remain keyboard operable and communicate errors/status semantically.
### [CUS][frontend]Use saved results in dashboard and API — CUS09

**Story:** As an athlete, I want saved results in a dashboard and output API so that I can use them elsewhere.

**Outcome:** Present saved results through a predefined dashboard and authorized read-only API.

**Features:** FEAT09, FEAT42, FEAT46

#### [Feature][frontend]Saved results dashboard — FEAT09

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS09; SR links: SR18, SR31; feature dependencies: FEAT08, FEAT41; WP prerequisites: none listed.

The owner can view approved saved readiness, results, evidence, and failures without invoking a model.

#### [Feature][backend]Read-only output API — FEAT42

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS09, CUS10; SR links: SR19, SR31, SR73; feature dependencies: FEAT09; WP prerequisites: none listed.

An authenticated owner can retrieve saved outputs through the approved read-only API, with values consistent with the dashboard and foreign data withheld.

#### [Feature][frontend]Accessible run and result interactions — FEAT46

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS07, CUS08, CUS09, CUS10; SR links: SR75, SR76; feature dependencies: FEAT09, FEAT43; WP prerequisites: none listed.

The approved P0 run, history, denial, and retrieval interactions remain keyboard operable and communicate errors/status semantically.
### [CUS][security]Isolate data and credentials — CUS10

**Story:** As a customer, I want my data and credentials isolated so that other users cannot access them.

**Outcome:** Isolate user files, credentials, and results across all access paths.

**Features:** FEAT42, FEAT10, FEAT43, FEAT44, FEAT46

#### [Feature][backend]Read-only output API — FEAT42

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS09, CUS10; SR links: SR19, SR31, SR73; feature dependencies: FEAT09; WP prerequisites: none listed.

An authenticated owner can retrieve saved outputs through the approved read-only API, with values consistent with the dashboard and foreign data withheld.

#### [Feature][security]Cross-user isolation — FEAT10

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP02; parents: CUS10; SR links: SR20, SR21, SR73; feature dependencies: FEAT02, FEAT06, FEAT07, FEAT08, FEAT42; WP prerequisites: none listed.

User files, credentials, manual runs, and saved results remain separated across supported access paths.

#### [Feature][frontend]Identity-bound interface state — FEAT43

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS10; SR links: SR21, SR71; feature dependencies: FEAT10, FEAT09; WP prerequisites: none listed.

Changing the active account cannot display a delayed or cached result belonging to the prior account.

#### [Feature][security]Safe credential and failure outputs — FEAT44

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP04; parents: CUS07, CUS10; SR links: SR74; feature dependencies: FEAT06, FEAT07; WP prerequisites: none listed.

Saved user-visible run outcomes omit credential material and unredacted provider payloads while preserving explicit failure status.

#### [Feature][frontend]Accessible run and result interactions — FEAT46

Priority: P0; status: Proposed; readiness: Blocked on decision; work package: WP05; parents: CUS07, CUS08, CUS09, CUS10; SR links: SR75, SR76; feature dependencies: FEAT09, FEAT43; WP prerequisites: none listed.

The approved P0 run, history, denial, and retrieval interactions remain keyboard operable and communicate errors/status semantically.

## P0 system requirements

| ID | Title | Parent CUS | Features | Priority | Obligation | Acceptance | Planned verification | WP | Status / decisions | Perspectives |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SR01 | [SR][backend]Classify submitted files and explain rejection | CUS01 | FEAT01 | P0 | The system shall classify every submitted file as accepted or rejected using the versioned source specification and return a reason for every rejection. |  | TC01 | WP01 | Draft derived requirement /  | engineering, architecture |
| SR02 | [SR][backend]Define supported source contract | CUS01 | FEAT01 | P0 | The source specification shall define supported records, timestamp interpretation, units, null values, required fields, and validation limits before import implementation is accepted. |  | TC01 | WP01 | Draft derived requirement /  | engineering, runtime, architecture |
| SR03 | [SR][database]Preserve source bytes and normalized lineage | CUS02 | FEAT02 | P0 | The system shall preserve original file bytes with an integrity identifier and retain normalized records linked to their original source. |  | TC02 | WP02 | Draft derived requirement /  | engineering, architecture, domain_provenance |
| SR04 | [SR][database]Prevent duplicates and surface conflicts | CUS02 | FEAT02 | P0 | Re-importing the same accepted file for the same user shall not create a duplicate activity; conflict cases shall be surfaced and not silently overwrite history. |  | TC03 | WP02 | Draft derived requirement /  | engineering, runtime, architecture, domain_provenance |
| SR05 | [SR][backend]Prepare repeatable normalized records | CUS03 | FEAT03 | P0 | For the same source bytes, configuration, and preprocessing version, preparation shall produce semantically identical normalized records and metrics, excluding generated identifiers and processing timestamps. |  | TC04 | WP02 | Draft derived requirement /  | engineering, runtime, architecture, operations_backup_retention_recovery |
| SR06 | [SR][runtime]Run preparation without model access | CUS03 | FEAT03 | P0 | Ingestion and preprocessing shall complete with model access disabled and shall make no inference requests. |  | TC04 | WP02 | Draft derived requirement /  | engineering, runtime |
| SR07 | [SR][backend]Limit skill inputs and retain provenance | CUS03 | FEAT21 | P0 | Prepared skill inputs shall contain only the selected dataset and context required by the selected skill, with provenance for computed metrics. |  | TC05 | WP03 | Draft derived requirement /  | engineering, architecture, privacy_security, domain_provenance |
| SR08 | [SR][backend]Declare immutable skill versions and requirements | CUS04 | FEAT04 | P0 | Each published skill shall declare an immutable version, mandatory inputs, applicability rules, method, output schema, and evaluation cases. |  | TC06 | WP03 | Draft derived requirement /  | engineering, architecture, domain_provenance |
| SR09 | [SR][security]Keep skills independent of provider logic | CUS04 | FEAT04 | P0 | Skill definitions shall not embed provider credentials or provider-specific endpoint and transport logic; such logic shall reside in model adapters. |  | TC06 | WP03 | Draft derived requirement /  | engineering, architecture, privacy_security |
| SR10 | [SR][backend]Evaluate eligibility before execution | CUS05 | FEAT05 | P0 | The system shall evaluate eligibility deterministically for the selected dataset before execution, including mandatory fields, history coverage, and permitted quality limits specified by the skill. |  | TC07 | WP03 | Draft derived requirement /  | engineering, architecture, runtime |
| SR11 | [SR][frontend]Explain and block ineligible skills | CUS05 | FEAT05 | P0 | An ineligible skill shall be unavailable for execution and shall identify unmet requirements without invoking a model. |  | TC07 | WP03 | Draft derived requirement /  | engineering, architecture, privacy_security |
| SR12 | [SR][backend]Use explicitly selected customer models | CUS06 | FEAT06, FEAT34 | P0 | Analysis requests shall use the user's explicitly selected supported model connection and shall never silently fall back to Datara-owned analysis credentials. |  | TC08 | WP04 | Draft derived requirement /  | engineering, architecture |
| SR13 | [SR][security]Protect credentials | CUS06 | FEAT06, FEAT33 | P0 | Credentials shall not appear in repository files, dashboard or API responses, or application logs; credential handling shall follow a documented access and protection design. |  | TC09 | WP04 | Draft derived requirement /  | privacy_security, architecture, operations_backup_retention_recovery |
| SR14 | [SR][backend]Record run selections and states | CUS07 | FEAT07 | P0 | A manual analysis run shall record its dataset scope, selected skill versions, and model before execution and expose pending, running, succeeded, and failed states. |  | TC10 | WP04 | Draft derived requirement /  | engineering, architecture, domain_provenance |
| SR15 | [SR][runtime]Reject invalid run outcomes | CUS07 | FEAT07, FEAT40 | P0 | Timeouts, authentication failures, and malformed model responses shall result in explicit failure or invalid-result states; they shall not be persisted as successful assessments. |  | TC10 | WP04 | Draft derived requirement /  | engineering, architecture, domain_provenance |
| SR16 | [SR][database]Retain assessment lineage and evidence | CUS08 | FEAT08, FEAT41 | P0 | Each stored assessment shall reference the input snapshot or immutable source records, preprocessing version, skill version, model identifier, execution time, and supporting evidence. |  | TC11 | WP05 | Draft derived requirement /  | engineering, architecture, domain_provenance |
| SR17 | [SR][database]Preserve rerun history | CUS08 | FEAT08 | P0 | A re-run shall create a new assessment without overwriting the previous one; observations, computed metrics, assessments, and recommendations shall remain distinguishable. |  | TC11 | WP05 | Draft derived requirement /  | engineering, architecture, domain_provenance |
| SR18 | [SR][frontend]Display saved dashboard outcomes | CUS09 | FEAT09 | P0 | The predefined dashboard shall display data readiness, selected analysis scope, saved findings, evidence, and failures without requiring a new model call for viewing. |  | TC12 | WP05 | Draft derived requirement /  | engineering, architecture, domain_provenance |
| SR19 | [SR][backend]Provide authorized read-only results | CUS09 | FEAT42 | P0 | The read-only API shall return versioned structured records and results consistent with the dashboard and shall reject attempts to mutate data through its read-only routes. |  | TC13 | WP05 | Draft derived requirement /  | engineering, architecture, domain_provenance |
| SR20 | [SR][security]Enforce user authorization | CUS10 | FEAT10 | P0 | Every upload, data query, analysis run, credential operation, and result query shall enforce user authorization. |  | TC14 | WP02 | Draft derived requirement /  | engineering, architecture, privacy_security |
| SR21 | [SR][security]Prevent cross-user access | CUS10 | FEAT10, FEAT43 | P0 | One user shall not read or execute against another user's files, credentials, or results by changing identifiers in supported UI or API requests. |  | TC14 | WP05 | Draft derived requirement /  | engineering, architecture, privacy_security |
| SR27 | [SR][backend]Pin official FIT source evidence | CUS01 | FEAT01 | P0 | The approved source contract shall identify the authoritative official FIT protocol/profile version and evidence used for every accepted variant, field mapping, unit conversion, timestamp rule, integrity rule, and fixture oracle; unverified variants shall be rejected as unsupported. |  | TC19 | WP01 | Proposed derived requirement /  | engineering, architecture, domain_provenance |
| SR28 | [SR][backend]Bind skill inputs to snapshots and provenance | CUS03 | FEAT21 | P0 | The skill input envelope shall be schema-versioned, deterministically canonicalized, bound to one immutable snapshot, and carry source or calculation provenance and data-quality metadata without credentials or out-of-scope records. |  | TC05, TC20 | WP03 | Proposed derived requirement /  | engineering, architecture, privacy_security, domain_provenance |
| SR29 | [SR][backend]Validate skill output and evidence | CUS04 | FEAT04 | P0 | The skill output envelope shall distinguish observations, computed metrics, and assessments; require resolvable evidence for every finding; reject unapproved classifications or unresolved references; and prohibit P0 recommendation outputs. |  | TC06, TC20 | WP03 | Proposed derived requirement /  | engineering, architecture, domain_provenance |
| SR30 | [SR][backend]Normalize selected model outcomes | CUS06 | FEAT06 | P0 | Each supported model adapter shall accept the common provider-independent execution request and return normalized outcomes for responses and declared failure classes while keeping credentials and provider transport outside skill definitions. |  | TC08, TC10, TC20 | WP04 | Proposed derived requirement /  | engineering, architecture, runtime |
| SR31 | [SR][backend]Align API and dashboard saved values | CUS09 | FEAT09, FEAT42 | P0 | The versioned output API shall expose only authorized read-only activity, readiness, run-history, and validated-result resources using stable error and pagination contracts, and the predefined dashboard shall derive its displayed saved values from the same contracts. |  | TC12, TC13, TC20 | WP05 | Proposed derived requirement /  | engineering, architecture, domain_provenance |
| SR32 | [SR][frontend]Present file disposition with textual reason | CUS01 | FEAT01 | P0 | For each submitted file, the system shall present its accepted or rejected disposition as text associated with that file and include the applicable approved rejection reason. | Given each approved accepted/rejected fixture, the interface identifies file and textual disposition; oracle: rendered result matches TC21 and is understandable without color/icon alone.<br>Given a rejected fixture, displayed reason matches the approved contract reason; oracle: compare displayed reason/code to the approved matrix. | TC21 | WP01 | Draft derived requirement / D01 | accessibility, engineering |
| SR33 | [SR][frontend]Distinguish duplicate imports and unresolved conflicts | CUS02 | FEAT02 | P0 | The history view shall distinguish persisted activities, exact duplicate imports, and unresolved conflicts according to the approved persistence contract. | Given identical bytes are imported twice, history does not show a second activity and identifies the duplicate import reference; oracle: TC22 agrees with persisted activity count.<br>Given an approved conflict fixture, history identifies affected records and unresolved status without implying merge or overwrite; oracle: TC22 matches the approved conflict policy. | TC22 | WP02 | Draft derived requirement / D01 | accessibility, engineering, domain_provenance |
| SR34 | [SR][frontend]Label prepared data scope and provenance | CUS03 | FEAT21 | P0 | Readiness presentation shall label selected data scope, source observations, computed metrics, and quality warnings according to their contract provenance. | Given a prepared fixture, interface displays scope and distinguishes observations, computed metrics and warnings; oracle: displayed labels and values map to prepared provenance in TC23.<br>Given an absent optional value, presentation identifies it as unavailable/unknown and does not render zero or infer a value; oracle: TC23 negative fixture. | TC23 | WP03 | Draft derived requirement / D02 | accessibility, domain_provenance, engineering |
| SR50 | [SR][backend]Version released skill definitions | CUS04 | FEAT04 | P0 | The system shall assign each released skill definition an immutable version identifier and retain the version referenced by any run. | Given two versions of a skill and a run referencing the earlier version, when the definition history is retrieved, then both versions remain distinguishable and the run resolves to its original version; oracle: a version-history contract fixture. | TC51 | WP03 | Draft derived requirement / D02 | engineering, architecture |
| SR51 | [SR][backend]Separate skill evaluation evidence | CUS04 | FEAT04, FEAT30 | P0 | The system shall prevent a candidate skill from receiving an evaluated or released label until the applicable D02 evaluation gate is approved and shall retain distinct evaluation evidence. | Given a candidate skill with deterministic-input, output-contract and substantive-evaluation records, when its state is reviewed before D02 approval, then the evaluation categories remain distinct and it is not labeled evaluated or released; oracle: TC41. | TC41 | WP03 | Draft derived requirement / D02 | engineering, architecture, domain_provenance |
| SR52 | [SR][backend]Record skill method provenance | CUS04 | FEAT30 | P0 | The system shall record source provenance for each proposed skill-method claim and expose unresolved source-rights questions without asserting a legal conclusion. | Given a proposed skill-method claim and its source inventory, when provenance is reviewed, then the source reference is resolvable and unresolved rights questions remain open without implying permission; oracle: TC42. | TC42 | WP03 | Draft derived requirement / D02 | domain_provenance |
| SR53 | [SR][backend]Return deterministic eligibility reasons | CUS05 | FEAT05, FEAT31 | P0 | The system shall produce repeatable eligibility results and reason identifiers for the same snapshot, skill and rule versions, and shall block eligibility when a mandatory input is unmet. | Given identical skill, snapshot and rule versions, when eligibility is evaluated twice, then the result and reason identifiers match; an unmet mandatory input blocks eligibility without an inference request; oracle: TC43. | TC43 | WP03 | Draft derived requirement / D02 | engineering, architecture |
| SR54 | [SR][security]Keep credentials outside skill and run payloads | CUS06 | FEAT06, FEAT33 | P0 | The system shall protect customer credentials according to the documented access and protection design and exclude them from skill definitions, user-visible outputs and operational evidence. | Given a test credential used for a selected connection, when the documented protection design and declared response, log and evidence surfaces are reviewed, then no credential value is exposed and any D03-dependent control remains marked open; oracle: TC46. | TC46 | WP04 | Draft derived requirement / D03 | privacy_security, architecture |
| SR55 | [SR][backend]Reject unsupported connection capabilities | CUS06 | FEAT06, FEAT32 | P0 | The system shall block execution when the explicitly selected connection lacks a required capability and shall explain the missing capability. | Given a selected connection that lacks a required capability, when execution is requested, then execution is blocked, the missing capability is explained and no analysis request is issued; oracle: TC47. | TC47 | WP04 | Draft derived requirement / D03 | engineering, architecture |
| SR56 | [SR][backend]Bind analysis to explicit model choice | CUS06 | FEAT06, FEAT34 | P0 | The system shall address only the explicitly selected connection and report its unavailable or failed outcome without fallback. | Given connection A is selected and unavailable, when the user runs an analysis, then the result identifies A and records a blocked or failed state without using connection B or Datara-owned analysis credentials; oracle: TC48. | TC48 | WP04 | Draft derived requirement / D03 | engineering, architecture |
| SR57 | [SR][runtime]Bound and normalize connection outcomes | CUS06 | FEAT06, FEAT32, FEAT35 | P0 | The system shall normalize success, authentication, temporary, timeout and malformed-response outcomes to their declared result classes. | Given successful, authentication, temporary, timeout and malformed-response cases, when outcomes are recorded, then each is distinguishable as a declared connection outcome; timeout bounds remain unresolved pending D03 evidence; oracle: TC49. | TC49 | WP04 | Draft derived requirement / D03 | engineering, runtime |
| SR58 | [SR][frontend]Make skill choice states operable and clear | CUS04 | FEAT31 | P0 | The system shall present eligible and ineligible catalog states so that actions and missing inputs are identifiable through text and keyboard operation. | Given eligible and ineligible skill states, when the catalog is inspected and operated, then names, selection state and eligibility reasons are available as text through operable controls and do not rely on color alone; oracle: TC45. | TC45 | WP03 | Draft derived requirement / D02 | engineering, accessibility |
| SR59 | [SR][operations]Exclude secrets from model-operation evidence | CUS06 | FEAT33, FEAT35 | P0 | The system shall provide enough operational evidence to distinguish customer model connection outcomes without exposing credential values, and shall identify unresolved credential lifecycle controls before release. | Given successful and failed model connection cases, when operational evidence is reviewed, then it distinguishes the declared outcome without credential values and lists any unresolved D03 credential lifecycle controls; oracle: TC50. | TC50 | WP04 | Draft derived requirement / D03 | privacy_security, runtime, operations_backup_retention_recovery |
| SR70 | [SR][backend]Reject invalid model output before assessment persistence | CUS07, CUS08 | FEAT40 | P0 | The system shall accept a model response as an assessment only when it validates against the approved output contract and matches the run's selected snapshot and skill version; otherwise it shall record a non-success outcome and shall not expose it as a finding. | Given a response matching the approved output contract, snapshot, and skill version, when validation completes, then a finding may be presented. Given a malformed response or mismatch, then the run is non-success and no finding is exposed. Oracle: TC61 and TC66; contract specifics remain gated by D02/D03. | TC61, TC66 | WP04 | Draft derived requirement / D02, D03 | engineering, runtime, architecture, domain_provenance |
| SR71 | [SR][frontend]Discard stale identity-bound responses | CUS10 | FEAT43 | P0 | The dashboard shall not render an identity-scoped response initiated for a prior authenticated user after the active identity changes; it shall discard or reauthorize the response before rendering. | Given a request for user A is delayed, when the active identity changes to user B before the response arrives, then user A values do not render for user B; the response is discarded or authorized for user B before use. Oracle: TC75; identity behavior remains unresolved under D04. | TC75 | WP05 | Draft derived requirement / D04 | engineering, privacy_security, accessibility |
| SR72 | [SR][backend]Bind finding evidence to its saved input snapshot | CUS08 | FEAT40, FEAT41 | P0 | Every resolvable evidence reference returned for a saved finding shall identify evidence bound to that result's input snapshot; broken or unauthorized references shall be unavailable and never replaced with unrelated evidence. | Given a saved finding with valid evidence for its snapshot, when its owner opens the evidence, then the evidence resolves to that snapshot. Given broken, cross-snapshot, or unauthorized evidence, then it is marked unavailable and no substitute is shown. Oracle: TC66/TC67; representation remains subject to D04. | TC66, TC67 | WP05 | Draft derived requirement / D04 | engineering, architecture, privacy_security, domain_provenance |
| SR73 | [SR][backend]Prevent cross-user resource disclosure in retrieval | CUS09, CUS10 | FEAT42, FEAT10 | P0 | Every collection and direct read of user-scoped output resources shall authorize against the current user before returning values; foreign identifiers or cursors shall not reveal another user's data or resource existence. | Given an authenticated owner, when the owner retrieves a saved output, then the authorized value is returned. Given another user valid identifier or cursor, when it is queried, then no foreign value or resource-existence signal is returned. Oracle: TC73/TC74; exact error behavior remains open under D04. | TC73, TC74 | WP05 | Draft derived requirement / D03, D04 | engineering, architecture, privacy_security, runtime |
| SR74 | [SR][security]Exclude credentials and unsafe provider payloads from outputs | CUS07, CUS10 | FEAT07, FEAT44 | P0 | The system shall omit credential material and unredacted provider request or response payloads from saved run outcomes and their dashboard/API representations, including failures, while preserving an explicit safe failure status. | Given a run result or failure containing unique credential/provider-payload sentinels, when the owner views the saved run, dashboard, or API representation, then no sentinel or raw provider payload is present and the actual failure status remains visible. Oracle: TC63/TC76. Log handling remains governed by existing SR13 and is not broadened here. | TC63, TC76 | WP04 | Draft derived requirement / D03 | engineering, runtime, architecture, privacy_security |
| SR75 | [SR][frontend]Operate run and result interactions by keyboard | CUS07, CUS08, CUS09, CUS10 | FEAT46 | P0 | Every interactive control in approved P0 run, saved-result, and retrieval flows shall be keyboard operable with perceivable focus; validation errors shall be associated with affected controls. | Given an owner using the approved run/result/retrieval flows, when each action is performed using keyboard only, then every control can be reached and operated and focus remains perceivable after state changes; each validation error identifies its control. Oracle: TC78; D04/D05 must set the test target. | TC78 | WP05 | Draft derived requirement / D04, D05 | engineering, accessibility |
| SR76 | [SR][frontend]Expose run states without color alone | CUS07, CUS08, CUS09, CUS10 | FEAT46 | P0 | The dashboard shall communicate success, failure, evidence availability, and access denial using text/semantic state as well as color, and expose asynchronous changes through the declared accessible status mechanism. | Given pending, succeeded, failed, evidence-unavailable, and access-denied states, when shown in an approved P0 view, then each state is identified by text/semantic output as well as color and asynchronous changes are announced through the approved accessibility mechanism. Oracles: TC69/TC78; target remains open under D04/D05. | TC69, TC78 | WP05 | Draft derived requirement / D04, D05 | engineering, accessibility |

## P0 work tasks and subtasks

Bounded owner labels identify planned responsibility only. Leaf tasks inherit the parent task and work-package gates. Project lifecycle status and runtime ownership must be synchronized in the GitHub Project; no requirement row here claims execution.

### [Task][management]Approve source evidence and release baseline — TK01

#### [Task][management]Approve source evidence and release baseline — TK01

Priority: ; requirement status: Proposed; readiness: ; work kind: ; planned owner: Primary Coordinator — Yi Tang (planned aggregate coordination); parent: ; WP: WP01; CUS: ; features: ; SR: ; dependencies: ; decisions: ; planned cases: TC01, TC19.

  #### [Task][legal]Inventory FIT source and fixture terms — TK09

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: Explorer — Wang Licun; parent: TK01; WP: WP01; CUS: CUS01; features: FEAT01; SR: SR27; dependencies: ; decisions: D01; planned cases: TC19, TC24.

  Acceptance: For each candidate official reference/fixture, provenance and terms or unresolved rights questions are recorded; oracle: every source has a provenance row or explicit gap and no legal conclusion is invented.

  Outputs: Evidence-indexed FIT source and fixture provenance inventory

  Sources: docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][legal]Identify official FIT source references — STK001** (; Planned; Proposed; owner Explorer — Wang Licun). Locate candidate official FIT protocol/profile references and record their source/version labels. Acceptance: Reference inventory contains a location and version for each candidate reference or labels it unknown; oracle: each matrix row is traceable to source metadata.. Output: Official FIT reference inventory. Cases: TC19, TC24; decisions: D01; source: docs/management/wp01-requirements-package.md.

  - **[Task][legal]Record fixture provenance and terms — STK002** (; Planned; Proposed; owner Explorer — Wang Licun). Inventory proposed fixture origin and usage terms without copying material whose terms are unresolved. Acceptance: Every candidate fixture has a provenance/terms row or explicit unknown and owner question; oracle: TC24 inspection list contains no unsupported rights conclusion.. Output: Fixture provenance and open terms table. Cases: TC19, TC24; decisions: D01; source: docs/management/wp01-requirements-package.md.

  #### [Task][architecture]Draft FIT support and mapping matrix — TK10

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: contract_design; planned owner: System Architect — Feng Guo; parent: TK01; WP: WP01; CUS: CUS01; features: FEAT01; SR: SR01, SR02, SR27; dependencies: TK09; decisions: D01; planned cases: TC01, TC19, TC25.

  Acceptance: Each proposed FIT variant, record, mapping, unit, timestamp, integrity and rejection rule cites official evidence or remains explicitly unsupported/unresolved; oracle: traceable matrix, with no guessed mapping or numeric limit.

  Outputs: Traceable proposed FIT acceptance/rejection matrix

  Sources: docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][architecture]Map records and fields to evidence — STK003** (; Planned; Proposed; owner System Architect — Feng Guo). Compare candidate record/field coverage with official FIT profile evidence and identify unsupported entries. Acceptance: Each proposed record/field mapping cites evidence or is marked unresolved/unsupported; oracle: matrix rows satisfy TC19 traceability.. Output: Evidence-linked record and field matrix. Cases: TC01, TC19; decisions: D01; source: docs/management/wp01-requirements-package.md.

  - **[Task][architecture]Document timestamp unit null and integrity rules — STK004** (; Planned; Proposed; owner System Architect — Feng Guo). Record source-supported timestamp, unit conversion, null and integrity behavior and leave unsupported values open. Acceptance: Rule table cites evidence for every specified behavior and flags unresolved choices; oracle: no unmapped value is silently assigned a conversion or fallback.. Output: Timestamp/unit/null/integrity rule table. Cases: TC01, TC19; decisions: D01; source: docs/management/wp01-requirements-package.md.

  #### [Task][security]Assess FIT intake data flow and operational gaps — TK13

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK01; WP: WP01; CUS: CUS01; features: FEAT01; SR: SR01, SR27; dependencies: ; decisions: D01; planned cases: TC14, TC25.

  Acceptance: Map source bytes, identifiers and diagnostics across intake; identify access, logging and recovery questions; oracle: each concern links an existing SR or explicit evidence gap, without assuming security controls or service targets.

  Outputs: FIT intake data-flow and operations gap report

  Sources: docs/management/system-requirements.md, docs/management/wp01-requirements-package.md

  - **[Task][security]Trace source bytes and metadata through intake — STK009** (; Planned; Proposed; owner System Architect — Feng Guo). List source data, identifiers and diagnostics crossing the FIT intake boundary. Acceptance: Each identified data item has purpose and CUS/SR trace or explicit open question; oracle: data-flow inventory is reviewable and makes no unsupported control claim.. Output: FIT intake data-flow inventory. Cases: TC14, TC25; decisions: D01; source: docs/management/system-requirements.md.

  - **[Task][operations]Map intake failure recovery questions — STK010** (; Planned; Proposed; owner System Architect — Feng Guo). Record operational questions for decoder rejection/failure, diagnostics and recovery. Acceptance: Every failure category has a reason/recovery note or an explicit gap owner; oracle: no unapproved service target or numeric limit is stated.. Output: Source intake operational gap list. Cases: TC01, TC25; decisions: D01; source: docs/management/wp01-requirements-package.md.

  #### [Task][architecture]Compare duplicate and conflict policy options — TK14

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK01; WP: WP01; CUS: CUS02; features: FEAT02; SR: SR04; dependencies: ; decisions: D01; planned cases: TC03.

  Acceptance: Compare only exact-byte, documented-tolerance and no-logical-detection options from WP01; oracle: each describes observable duplicate/conflict outcomes and leaves D01 choice to founder.

  Outputs: Decision-ready duplicate/conflict options table

  Sources: docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][architecture]Trace exact-byte duplicate behavior — STK011** (; Planned; Proposed; owner System Architect — Feng Guo). Map same-user same-byte re-import behavior to SR04 and the planned duplicate fixture. Acceptance: Exact-byte case points to current SR04 and TC03; oracle: no logical identity or tolerance policy is added by this trace.. Output: Exact duplicate trace row. Cases: TC03; decisions: D01; source: docs/management/wp01-requirements-package.md.

  - **[Task][architecture]Compare unresolved logical conflict examples — STK012** (; Planned; Proposed; owner System Architect — Feng Guo). List different-byte candidate records whose logical identity outcome depends on D01. Acceptance: Each example states competing outcomes and remains unresolved; oracle: no tolerance threshold is encoded before founder D01 decision.. Output: Conflict fixture decision table. Cases: TC03; decisions: D01; source: docs/management/wp01-requirements-package.md.
### [Task][architecture]Approve skill and result contracts — TK02

#### [Task][architecture]Approve skill and result contracts — TK02

Priority: ; requirement status: Proposed; readiness: ; work kind: ; planned owner: Primary Coordinator — Yi Tang (planned aggregate coordination); parent: ; WP: WP01; CUS: ; features: ; SR: ; dependencies: TK01; decisions: ; planned cases: TC20.

  #### [Task][backend]Identify unresolved manual-run outcome questions — TK50

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK02; WP: WP01; CUS: CUS07; features: FEAT07; SR: SR14, SR15; dependencies: ; decisions: D03; planned cases: TC60.

  Acceptance: Given SR14-SR15 and the project brief, when run outcomes are reviewed, then the decision brief lists each supported outcome and unresolved retry or repeated-submission question without selecting behavior; oracle TC60.

  Outputs: Decision questions for manual run outcomes

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]List allowed transitions — STK200** (decision_research; Planned; Proposed; owner System Architect — Feng Guo). List allowed transitions. Given SR14-SR15 and TC10, when each allowed run outcome is considered, then the brief names its observable state and the controlling source; oracle TC60. Acceptance: Given SR14-SR15 and TC10, when each allowed run outcome is considered, then the brief names its observable state and the controlling source; oracle TC60.. Output: Outcome-to-source list. Cases: TC60; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Add impossible transition cases — STK201** (decision_research; Planned; Proposed; owner System Architect — Feng Guo). Add impossible transition cases. Given repeated submission and retry are not resolved in D03, when those cases are reviewed, then each is recorded as an open decision rather than silently selected; oracle TC60. Acceptance: Given repeated submission and retry are not resolved in D03, when those cases are reviewed, then each is recorded as an open decision rather than silently selected; oracle TC60.. Output: Explicit open retry/submission questions. Cases: TC60; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][backend]Investigate output-validity obligations and open decisions — TK51

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK02; WP: WP01; CUS: CUS07, CUS08; features: FEAT40; SR: SR15, SR70; dependencies: ; decisions: D02, D03; planned cases: TC61.

  Acceptance: Given the WP01 output envelope proposal, when valid and invalid response classes are reviewed, then D02/D03 questions are recorded and invalid responses remain non-success proposals; no schema is invented; oracle TC61.

  Outputs: Output-validation decision questions and evidence gaps

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]List invalid response classes and open validity questions — STK202** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][backend]List invalid response classes and open validity questions Acceptance: Given the WP01 valid-output proposal, when invalid response classes are reviewed, then each has a proposed non-success outcome or a recorded D02/D03 question; oracle TC61.. Output: Invalid-output decision table. Cases: TC61; decisions: D02, D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Record negative examples and unresolved oracle evidence — STK203** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][backend]Record negative examples and unresolved oracle evidence Acceptance: Given malformed, mismatched-version, mismatched-snapshot, and missing-evidence examples, when they are compared with the proposed contract, then unsupported oracle details are labeled unresolved; oracle TC61.. Output: Negative example and unresolved-oracle list. Cases: TC61; decisions: D02, D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][backend]Investigate result-lineage and evidence obligations — TK56

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK02; WP: WP01; CUS: CUS08; features: FEAT08; SR: SR16, SR17; dependencies: ; decisions: D04; planned cases: TC64, TC65.

  Acceptance: Given SR16-SR17 and the D04 proposal, when history obligations are reviewed, then a sourced question brief identifies lineage facts users must revisit and unresolved evidence/retention choices; no record schema is selected; oracle TC64/TC65.

  Outputs: Result-lineage and rerun decision questions

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Identify lineage facts needed to revisit results — STK212** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][backend]Identify lineage facts needed to revisit results Acceptance: Given SR16 and D04, when historical assessments are reviewed, then required revisit facts and their sources are listed while unresolved representation choices remain open; oracle TC64.. Output: Lineage fact and decision register. Cases: TC64, TC65; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Record unresolved rerun/history decisions — STK213** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][backend]Record unresolved rerun/history decisions Acceptance: Given SR17, when repeat-run examples are compared, then prior-result preservation and separate assessment identity are captured as observable outcomes; oracle TC65.. Output: Rerun outcome questions. Cases: TC64, TC65; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][frontend]Investigate dashboard outcome choices — TK60

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK02; WP: WP01; CUS: CUS09; features: FEAT09; SR: SR18, SR31; dependencies: ; decisions: D04; planned cases: TC68, TC69.

  Acceptance: Given D04 and CUS09, when dashboard outcome questions are reviewed, then a decision brief states what saved information the athlete needs and which views/states require founder choice; no screens are designed; oracle TC68-TC70.

  Outputs: D04 dashboard outcome questions and open choices

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][frontend]Record dashboard outcome questions for decision — STK220** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][frontend]Record dashboard outcome questions for decision Acceptance: Given D04 open questions, when the proposed dashboard outcome is reviewed, then required saved information and unresolved athlete choices are recorded without screen composition; oracle TC68-TC70.. Output: Dashboard decision questions. Cases: TC68, TC69; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][frontend]Separate approved saved-data needs from undecided views — STK221** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][frontend]Separate approved saved-data needs from undecided views Acceptance: Given model access is disabled and saved data exists, when dashboard behavior is defined from the approved contract, then viewing history requires no inference and values remain retrievable; oracle TC68.. Output: Offline viewing outcome. Cases: TC68, TC69; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][backend]Investigate read-only API scope decisions — TK63

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK02; WP: WP01; CUS: CUS09; features: FEAT42; SR: SR19, SR31, SR73; dependencies: ; decisions: D04; planned cases: TC70, TC71, TC72.

  Acceptance: Given D04 and the proposed read-only API outcome, when retrieval needs are reviewed, then the brief lists unresolved questions about resources, access, errors, versioning and pagination without choosing routes, bounds or codes; oracle TC70-TC72.

  Outputs: API-scope decisions and unresolved questions

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]List API purpose and access questions — STK226** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][backend]List API purpose and access questions Acceptance: Given D04 and the read-only API outcome, when stakeholder retrieval needs are collected, then resource purpose and unresolved version/access questions are listed without selecting routes; oracle TC70-TC72.. Output: API requirements question list. Cases: TC70, TC71, TC72; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Record mutation, query, and pagination decisions still open — STK227** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][backend]Record mutation, query, and pagination decisions still open Acceptance: Given proposed read-only retrieval, when mutation and query scenarios are reviewed, then required observable outcomes and unresolved pagination/error decisions are recorded without inventing bounds/codes; oracle TC71/TC72.. Output: Read-only and query decision gaps. Cases: TC70, TC71, TC72; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][security]Investigate user-authorization scope and evidence — TK66

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK02; WP: WP01; CUS: CUS08, CUS09, CUS10; features: FEAT08, FEAT41, FEAT42, FEAT10; SR: SR16, SR19, SR20, SR21, SR73; dependencies: ; decisions: D03, D04; planned cases: TC73, TC74.

  Acceptance: Given CUS08-CUS10 and their current access obligations, when history/evidence/output access paths are reviewed, then a sourced investigation lists where authorization applies, missing evidence and owner decisions without choosing a mechanism or response code; oracle TC73/74.

  Outputs: Authorization obligation questions and evidence gaps

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][security]Identify history and output access paths needing assessment — STK232** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][security]Identify history and output access paths needing assessment Acceptance: Given history, evidence and result access for CUS08-CUS10, when owner boundaries are reviewed, then each access path needing authorization and each missing decision/evidence item is documented; oracle TC73/TC74.. Output: Scoped access obligations and gaps. Cases: TC73, TC74; decisions: D03, D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][security]Record unresolved authorization evidence and decision owners — STK233** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). [Task][security]Record unresolved authorization evidence and decision owners Acceptance: Given foreign identifiers/cursors and the D04 error decision, when denial behavior is reviewed, then the questions needed to prevent data/existence disclosure are listed without choosing codes; oracle TC73.. Output: Foreign-resource nondisclosure questions. Cases: TC73, TC74; decisions: D03, D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][operations]Investigate history operations and legal-duty questions — TK72

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK02; WP: WP01; CUS: CUS07, CUS08, CUS09, CUS10; features: FEAT07, FEAT08, FEAT09, FEAT10; SR: SR14, SR15, SR16, SR18, SR19, SR20; dependencies: ; decisions: D03, D04, D05; planned cases: TC77.

  Acceptance: Given management sources and authoritative evidence available to reviewers, when history retention, backup/restore, access and applicable legal questions are assessed, then each item is cited with limits or recorded as an open decision with an owner; no legal conclusion, retention period or recovery target is invented; oracle TC77.

  Outputs: Evidence-indexed history operations and legal-duty gaps

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]List unknowns — STK244** (decision_research; Planned; Proposed; owner System Architect — Feng Guo). List unknowns. Given the project sources, when history lifecycle questions are enumerated, then retention, backup/restore, access and legal applicability unknowns are separated from established facts; oracle TC77. Acceptance: Given the project sources, when history lifecycle questions are enumerated, then retention, backup/restore, access and legal applicability unknowns are separated from established facts; oracle TC77.. Output: Evidence question inventory. Cases: TC77; decisions: D03, D04, D05; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Record source or decision owner — STK245** (decision_research; Planned; Proposed; owner System Architect — Feng Guo). Record source or decision owner. Given each unresolved item, when the decision brief is completed, then a source with its limits or an accountable owner decision is recorded, and no period/legal outcome is inferred; oracle TC77. Acceptance: Given each unresolved item, when the decision brief is completed, then a source with its limits or an accountable owner decision is recorded, and no period/legal outcome is inferred; oracle TC77.. Output: Sourced gaps and decision owners. Cases: TC77; decisions: D03, D04, D05; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][accessibility]Investigate P0 accessibility applicability and open targets — TK73

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: UI Designer — Wu Yunzhou; parent: TK02; WP: WP01; CUS: CUS07, CUS08, CUS09, CUS10; features: FEAT46, FEAT43; SR: SR71, SR75, SR76; dependencies: ; decisions: D04, D05; planned cases: TC78.

  Acceptance: Given the UI review and P0 interactive states, when accessibility obligations are assessed, then keyboard/focus/error/status concerns and required owner decisions are listed with evidence gaps; no standard, viewport, browser or assistive-technology matrix is chosen; oracle TC78.

  Outputs: Accessibility obligation questions and evidence gaps

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][accessibility]Assess accessibility applicability for P0 interactions — STK246** (decision_research; Planned; Proposed; owner UI Designer — Wu Yunzhou). [Task][accessibility]Assess accessibility applicability for P0 interactions Acceptance: Given proposed P0 interactions, when accessibility applicability is reviewed, then keyboard/focus/error/status concerns and known evidence gaps are recorded without choosing conformance targets; oracle TC78.. Output: Accessibility obligation inventory. Cases: TC78; decisions: D04, D05; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][accessibility]Record unselected accessibility targets and owners — STK247** (decision_research; Planned; Proposed; owner UI Designer — Wu Yunzhou). [Task][accessibility]Record unselected accessibility targets and owners Acceptance: Given each needed test target, when the assessment is reviewed, then unresolved formal standard/browser/viewport/AT choices are explicitly assigned for decision; oracle TC78.. Output: Open accessibility target decisions. Cases: TC78; decisions: D04, D05; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.
### [Task][backend]Implement persistent data and preparation — TK03

#### [Task][backend]Implement persistent data and preparation — TK03

Priority: ; requirement status: Planned; readiness: ; work kind: ; planned owner: Primary Coordinator — Yi Tang (planned aggregate coordination); parent: ; WP: WP02; CUS: ; features: ; SR: ; dependencies: TK01, TK02; decisions: ; planned cases: TC01, TC02, TC03, TC04, TC05, TC14, TC19.

  #### [Task][backend]Implement approved file classification and diagnostics — TK11

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK03; WP: WP02; CUS: CUS01; features: FEAT01; SR: SR01, SR02, SR27, SR32; dependencies: TK10; decisions: D01, D05; planned cases: TC01, TC19, TC21.

  Acceptance: Given an approved-matrix fixture, classification and textual per-file outcome match its expected disposition/reason; oracle: unsupported/malformed cases reject and approved accepted cases import without silent fallback.

  Outputs: Implemented contract-versioned classification and accessible per-file diagnostics

  Sources: docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md

  - **[Task][backend]Implement source-matrix classification — STK005** (; Planned; Blocked on decision; owner Worker — Torsten Maier). Implement deterministic accepted/rejected classification from the approved source matrix and contract version. Acceptance: For each approved fixture, classification equals the expected matrix result; oracle: TC01/TC19 accepted cases succeed and unsupported/malformed cases reject.. Output: Versioned deterministic file classification. Cases: TC01, TC19; decisions: D01, D05; source: docs/management/system-requirements.md, docs/management/wp01-requirements-package.md.

  - **[Task][frontend]Render textual file status and reason — STK006** (; Planned; Blocked on decision; owner Worker — Torsten Maier). Render each file result with file identity, textual disposition and approved rejection reason. Acceptance: Rendered accepted/rejected fixtures identify file, status and reason without color-only meaning; oracle: TC21.. Output: Accessible per-file disposition display. Cases: TC21; decisions: D01; source: docs/management/p0-ui-requirements-review.md.

  #### [Task][database]Implement immutable originals and duplicate-safe history — TK15

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK03; WP: WP02; CUS: CUS02; features: FEAT02; SR: SR03, SR04, SR33; dependencies: TK14; decisions: D01, D05; planned cases: TC02, TC03, TC22.

  Acceptance: Given the approved storage/identity contract, accepted bytes retain an integrity identifier and normalized records link to source; identical re-import is idempotent and a conflict is never silently overwritten; oracle: TC02/03/22.

  Outputs: Immutable source lineage and duplicate/conflict-safe history behavior

  Sources: docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md

  - **[Task][database]Persist original bytes with integrity reference — STK013** (; Planned; Blocked on decision; owner Worker — Torsten Maier). Implement approved original-byte retention and integrity identifier without selecting a stack outside D05. Acceptance: Reloaded original bytes match the submitted digest and each normalized record resolves to source; oracle: TC02.. Output: Integrity-identified original and source link. Cases: TC02; decisions: D01, D05; source: docs/management/system-requirements.md.

  - **[Task][database]Implement approved duplicate and conflict disposition — STK014** (; Planned; Blocked on decision; owner Worker — Torsten Maier). Apply the approved same-byte duplicate and logical conflict policies without overwrite or unapproved merge. Acceptance: Repeated identical bytes create no additional activity and an approved conflict is surfaced unresolved; oracle: TC03/TC22.. Output: Duplicate-safe history and visible conflict behavior. Cases: TC03, TC22; decisions: D01, D05; source: docs/management/system-requirements.md, docs/management/p0-ui-requirements-review.md.

  #### [Task][management]Investigate history rights and lifecycle policy gaps — TK17

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK03; WP: WP02; CUS: CUS02, CUS03; features: FEAT02, FEAT03; SR: SR03, SR28; dependencies: ; decisions: ; planned cases: TC24, TC26.

  Acceptance: Record sourced rights, retention, backup/recovery and privacy questions for retained and prepared user data; oracle: each issue has a source or explicit unknown/owner question; no legal duty, duration, RPO or RTO is invented.

  Outputs: Evidence-linked persistent-data lifecycle gap report

  Sources: docs/management/decision-register.md, docs/management/wp01-requirements-package.md

  - **[Task][legal]Separate source terms from user data questions — STK017** (; Planned; Proposed; owner System Architect — Feng Guo). Identify source-term questions for the official specification, uploaded files and derived records, without deciding legal rights. Acceptance: Each data class has a cited term or explicit unknown and owner question; oracle: TC24 has no fabricated legal conclusion.. Output: Source/user/derived-data rights question inventory. Cases: TC24; decisions: ; source: docs/management/decision-register.md.

  - **[Task][operations]List history retention backup and privacy gaps — STK018** (; Planned; Proposed; owner System Architect — Feng Guo). Document open retention, access/privacy, backup and recovery choices for persistent source and prepared data. Acceptance: Each missing lifecycle policy is an explicit sourced or owner-assigned gap; oracle: TC26 identifies questions without duration, duty, RPO or RTO assumptions.. Output: Persistent-data lifecycle policy gap register. Cases: TC26; decisions: ; source: docs/management/decision-register.md, docs/management/wp01-requirements-package.md.

  #### [Task][backend]Implement deterministic model-free normalization — TK18

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK03; WP: WP02; CUS: CUS03; features: FEAT03; SR: SR05, SR06; dependencies: ; decisions: D01, D05; planned cases: TC04.

  Acceptance: Given approved source/configuration/version, repeat preparation produces semantically identical normalized output and no inference request; oracle: TC04.

  Outputs: Deterministic model-free normalization

  Sources: docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md

  - **[Task][backend]Implement deterministic model-free normalization — STK019** (; Planned; Blocked on decision; owner Worker — Torsten Maier). Implement approved normalization with conventional deterministic processing and no inference calls. Acceptance: Given approved source rules, normalizer emits expected values; oracle: independent fixture values match TC04.. Output: Deterministic inference-free normalization. Cases: TC04; decisions: D01, D05; source: docs/management/system-requirements.md, docs/management/wp01-requirements-package.md.

  - **[Task][backend]Execute preprocessing with model access disabled — STK025** (; Planned; Blocked on decision; owner Worker — Torsten Maier). Ensure ingestion/preparation path completes without creating or calling an inference adapter. Acceptance: Preparation succeeds with model access disabled and observable inference call count is zero; oracle: TC04.. Output: Model-free preprocessing control flow. Cases: TC04; decisions: D01, D05; source: docs/management/system-requirements.md.

  #### [Task][runtime]Assess preprocessing runtime and operations gaps — TK20

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: Explorer — Wang Licun; parent: TK03; WP: WP02; CUS: CUS03; features: FEAT03; SR: SR05, SR06, SR28; dependencies: ; decisions: D01, D05; planned cases: TC25, TC27.

  Acceptance: Identify source-backed resource dimensions and run-version/configuration diagnostics needed to interpret repeat preparation; oracle: proposed bounds cite evidence or remain open, and no service target is fabricated.

  Outputs: Preprocessing resource and reproducibility operations gap report

  Sources: docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][runtime]List preprocessing resource dimensions — STK023** (; Planned; Proposed; owner Explorer — Wang Licun). Identify file/record/compute dimensions relevant to deterministic preprocessing and their measurement method. Acceptance: Each candidate dimension has a measurement method and source or an explicit evidence gap; oracle: no unsupported limit is stated in TC25/TC27.. Output: Preprocessing resource-variable inventory. Cases: TC25, TC27; decisions: D01, D05; source: docs/management/wp01-requirements-package.md.

  - **[Task][operations]Specify repeat-run diagnostic fields — STK024** (; Planned; Proposed; owner Explorer — Wang Licun). List source, configuration and version fields needed to interpret preparation results and failures. Acceptance: Repeat-run record identifies source/configuration/preprocessing version or flags the missing field; oracle: TC27 can establish whether two runs are comparable.. Output: Reproducibility diagnostic field checklist. Cases: TC27; decisions: D05; source: docs/management/wp01-requirements-package.md.

  #### [Task][security]Implement authorization before protected use — TK67

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK03; WP: WP02; CUS: CUS10; features: FEAT10; SR: SR20, SR21, SR73; dependencies: TK66; decisions: D03, D04; planned cases: TC73, TC74.

  Acceptance: Given an authenticated owner and a second user, when either requests the other user file, run, or result, then own access works and foreign access is denied before data is used or returned; oracle TC73/74.

  Outputs: User-scoped access behavior at protected boundaries

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][security]Implement file/run checks — STK234** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Implement file/run checks. Given a user requesting their own file/run, when authorization is checked, then their permitted operation completes; oracle TC74. Acceptance: Given a user requesting their own file/run, when authorization is checked, then their permitted operation completes; oracle TC74.. Output: Owner access behavior. Cases: TC73, TC74; decisions: D03, D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][security]Implement history/API checks — STK235** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Implement history/API checks. Given a user requesting another users file/run/result, when authorization is checked before use, then the operation is denied and no foreign value is returned; oracle TC73/TC74. Acceptance: Given a user requesting another users file/run/result, when authorization is checked before use, then the operation is denied and no foreign value is returned; oracle TC73/TC74.. Output: Foreign access denial behavior. Cases: TC73, TC74; decisions: D03, D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.
### [Task][backend]Implement skills and deterministic eligibility — TK04

#### [Task][backend]Implement skills and deterministic eligibility — TK04

Priority: ; requirement status: Planned; readiness: ; work kind: ; planned owner: Primary Coordinator — Yi Tang (planned aggregate coordination); parent: ; WP: WP03; CUS: ; features: ; SR: ; dependencies: TK03; decisions: ; planned cases: TC05, TC06, TC07, TC20.

  #### [Task][backend]Implement versioned scoped skill input and provenance display — TK21

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK04; WP: WP03; CUS: CUS03; features: FEAT21; SR: SR07, SR28, SR34; dependencies: TK18; decisions: D01, D02, D05; planned cases: TC05, TC20, TC23.

  Acceptance: Given approved input contract, package only selected declared inputs with snapshot/source or calculation lineage and display scope/value classes; oracle: TC05/20/23, including out-of-scope/secret and absent-value negatives.

  Outputs: Scoped versioned skill-input envelope and provenance/readiness display

  Sources: docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md

  - **[Task][backend]Implement scoped versioned input and provenance presentation — STK020** (; Planned; Blocked on decision; owner Worker — Torsten Maier). Package declared selected-scope inputs with snapshot/source or calculation lineage, exclude credentials/out-of-scope records, and show provenance labels. Acceptance: Valid scoped envelope citations resolve, and missing optional values are labeled unavailable/unknown; oracle: TC05/20/23 and negative cases reject credentials/out-of-scope values.. Output: Versioned scoped skill-input envelope and provenance labels. Cases: TC05, TC20, TC23; decisions: D01, D02, D05; source: docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md.

  - **[Task][backend]Implement versioned scoped input envelope — STK027** (; Planned; Blocked on decision; owner Worker — Torsten Maier). Bind input envelope to snapshot/scope and include only skill-declared records, context and provenance. Acceptance: Envelope validates selected snapshot/scope and each computed metric has source/calculation lineage; oracle: TC05/20, with credentials/out-of-scope negative cases rejected.. Output: Versioned skill input envelope. Cases: TC05, TC20; decisions: D01, D02, D05; source: docs/management/system-requirements.md, docs/management/wp01-requirements-package.md.

  #### [Task][backend]Propose baseline elemental skill shortlist — TK30

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK04; WP: WP03; CUS: CUS04; features: FEAT04; SR: SR08, SR50; dependencies: ; decisions: D02; planned cases: TC80.

  Acceptance: The shortlist has a row per proposed skill and records candidate, intended outcome, in/out scope, origin, input needs, evidence, exclusion rationale, and unresolved D02 choice; the review checklist records each required field as present, missing, or open. TC80 inspects this artifact and does not imply product verification.

  Outputs: Reviewable shortlist with explicit candidate scope and unresolved decision items

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][backend]Collect candidate skill outcomes and exclusions — STK100** (decision_research; Planned; Proposed; owner System Architect — Feng Guo). Produce candidate inventory for Propose baseline elemental skill shortlist. Use only the assigned DATARA scope; label unverified evidence and unresolved decisions explicitly. Acceptance: Given the shortlist review is complete, each proposed skill has a candidate name, intended user outcome, scope, source/origin, input needs, evidence, exclusions, and unresolved D02 decision recorded; the reviewer can identify any missing column.. Output: candidate inventory. Cases: TC80; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][backend]Identify provider-independent skill declaration requirements — TK31

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: contract_design; planned owner: System Architect — Feng Guo; parent: TK04; WP: WP03; CUS: CUS04; features: FEAT04; SR: SR08, SR09, SR29, SR50; dependencies: ; decisions: D02; planned cases: TC40, TC51.

  Acceptance: The requirements record states the user-relevant declaration expectations for applicability, inputs, method provenance, outputs, version, and evaluation; it lists unresolved D02 decisions and does not select a technical schema or architecture.

  Outputs: Versioned skill definition contract and positive/negative examples

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][backend]List model-independent skill declaration fields — STK102** (contract_design; Planned; Blocked on decision; owner System Architect — Feng Guo). Identify provider-independent skill declaration requirements and unresolved choices for the future contract. Acceptance: Given each proposed skill declaration, the requirements record states provider-independent input, applicability, method, output, version, provenance, and evaluation expectations as outcomes, and marks unresolved D02 choices without prescribing a technical schema.. Output: Provider-independent declaration requirements and open decisions. Cases: TC40, TC51; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][backend]Define layered skill evaluation protocol — TK32

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: contract_design; planned owner: System Architect — Feng Guo; parent: TK04; WP: WP03; CUS: CUS04; features: FEAT30; SR: SR51; dependencies: ; decisions: D02; planned cases: TC41.

  Acceptance: The proposed evidence rubric defines separate observable pass/fail/blocked outcomes for deterministic behavior, contract conformance, mocked interactions, and substantive evaluation; it states which evidence is required before a skill can be called evaluated/released and leaves thresholds requiring D02 approval open.

  Outputs: Evaluation protocol separating deterministic, schema, mocked and substantive evidence

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][backend]Separate deterministic and schema checks from substantive assessment — STK104** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). Produce layered evidence rubric for Define layered skill evaluation protocol. Use only the assigned DATARA scope; label unverified evidence and unresolved decisions explicitly. Acceptance: Given deterministic, contract, mocked, and substantive evaluation evidence, the proposed protocol keeps each evidence class distinct and prevents a weaker class from being reported as substantive evaluation; unresolved release thresholds remain open under D02.. Output: layered evidence rubric. Cases: TC41; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][architecture]Assess method provenance, rights and eligibility applicability — TK33

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK04; WP: WP03; CUS: CUS04, CUS05; features: FEAT30, FEAT05; SR: SR52; dependencies: ; decisions: D02; planned cases: TC42.

  Acceptance: The candidate-method source inventory identifies resolvable origins and open attribution/use questions; it explicitly asks whether method provenance affects proposed eligibility use, records applicability as unknown until evidence is assessed, and makes no legal conclusion. D02 remains open.

  Outputs: Source inventory and unresolved rights questions for candidate methods

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][backend]Inventory proposed source references per candidate method — STK106** (decision_research; Planned; Proposed; owner System Architect — Feng Guo). Produce source-to-method map for Assess baseline method provenance and rights gaps. Use only the assigned DATARA scope; label unverified evidence and unresolved decisions explicitly. Acceptance: Given every candidate method claim, the source inventory includes a resolvable source reference and links it to the claim; unresolved rights and attribution questions are recorded without a legal conclusion.. Output: source-to-method map. Cases: TC42; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][backend]Define eligibility outcomes and blocking requirements — TK34

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: contract_design; planned owner: System Architect — Feng Guo; parent: TK04; WP: WP03; CUS: CUS05; features: FEAT05; SR: SR10, SR11, SR53; dependencies: ; decisions: D02; planned cases: TC43.

  Acceptance: The requirements record states repeatability for an unchanged snapshot and rule version, identifies mandatory unmet-input blocking with an explanation, and lists open policy decisions without defining a data schema.

  Outputs: Eligibility rule/result contract with stable unmet-requirement identifiers

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][backend]Translate declared requirements into snapshot-bound rule inputs — STK108** (contract_design; Planned; Blocked on decision; owner System Architect — Feng Guo). Identify eligibility outcomes, repeatability expectations, and blocking rules for the future requirement contract. Acceptance: Given the eligibility requirements review, identical snapshot, skill, and rule versions produce repeatable eligibility and reason outcomes, and every mandatory unmet input blocks eligibility; unresolved policy choices are explicit.. Output: Eligibility outcomes and open policy questions. Cases: TC43; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][frontend]Specify eligibility explanation and catalog states — TK35

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: contract_design; planned owner: UI Designer — Wu Yunzhou; parent: TK04; WP: WP03; CUS: CUS04, CUS05; features: FEAT31; SR: SR11, SR58; dependencies: ; decisions: D02; planned cases: TC45.

  Acceptance: The requirements note covers eligible, ineligible, empty and error catalog cases, and for each names the user-visible state, eligibility or missing-input reason, and available action; it separately lists text/keyboard accessibility questions and D02 decisions without selecting a UI design or standard.

  Outputs: Catalog state and accessibility acceptance specification

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][frontend]Map catalog eligible, ineligible, empty and error states — STK110** (contract_design; Planned; Blocked on decision; owner UI Designer — Wu Yunzhou). Identify user-facing catalog outcome and accessibility criteria for the eligibility explanation requirement. Acceptance: Given eligible, ineligible, empty, and error catalog cases, the outcome criteria specify visible state, missing-input explanation, and available action for each; unresolved applicability questions remain assigned for review.. Output: Catalog outcome and accessibility criteria. Cases: TC45; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][backend]Implement approved skill definitions and evaluation — TK42

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK04; WP: WP03; CUS: CUS04; features: FEAT04, FEAT30; SR: SR08, SR09, SR29, SR50, SR51, SR52; dependencies: TK31, TK32, TK33; decisions: D02; planned cases: TC40, TC41, TC42, TC51.

  Acceptance: For an authorized candidate SHA and named environment, the future implementation demonstrates declarations conforming to the approved provider-independent requirements, links versioned method provenance, and keeps evaluation/release labels blocked until D02 approval; attach positive/negative fixture pass/fail, blocked cases, defects, and evidence.

  Outputs: Future implementation outcome and candidate-specific verification record

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md

  - **[Task][backend]Implement versioned provider-independent skill declarations — STK124** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Prepare the bounded implement versioned provider-independent skill declarations output for the future approved product workflow. Acceptance: On a future authorized candidate revision, required skill declarations satisfy the approved provider-independent contract, link their method provenance and version, and cannot be labeled evaluated or released before the D02 gate; record candidate SHA, environment, fixture results, blocked cases, and defect evidence.. Output: Implement versioned provider-independent skill declarations. Cases: TC40, TC41, TC42, TC51; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md.

  #### [Task][backend]Verify approved skill definitions and evaluation — TK43

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK04; WP: WP03; CUS: CUS04; features: FEAT04, FEAT30; SR: SR08, SR09, SR29, SR50, SR51, SR52; dependencies: TK42; decisions: D02; planned cases: TC40, TC41, TC42, TC51.

  Acceptance: On the named candidate SHA and environment, the tester runs positive/negative declaration and provenance fixtures plus the D02 release-block case, records each pass/fail/blocked result and defect/evidence link, and reports implementation readiness without claiming provider integration.

  Outputs: Candidate-specific fixture results, defects, and verification report

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md

  - **[Task][backend]Verify positive and negative skill-definition fixtures — STK126** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Prepare the bounded verify positive and negative skill-definition fixtures output for the future approved product workflow. Acceptance: On a future authorized candidate SHA, run positive and negative declaration fixtures and D02-blocking cases; record environment, fixture-by-fixture pass/fail, blocked cases, defects, and evidence links, and keep the result Not run until executed.. Output: Verify positive and negative skill-definition fixtures. Cases: TC40, TC41, TC42, TC51; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md.

  #### [Task][backend]Implement snapshot-bound eligibility and explanations — TK44

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK04; WP: WP03; CUS: CUS05; features: FEAT05, FEAT31; SR: SR10, SR11, SR53, SR58; dependencies: TK34, TK35; decisions: D02; planned cases: TC43, TC44, TC45.

  Acceptance: For an authorized candidate SHA and named environment, the future implementation returns repeatable eligibility and reason outcomes for identical snapshots/rule versions, explains each unmet mandatory input, and makes zero model calls for ineligible cases; attach fixture results and defects.

  Outputs: Future eligibility behavior and candidate-specific verification record

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md

  - **[Task][backend]Implement deterministic snapshot-bound eligibility checks — STK128** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Prepare the bounded implement deterministic snapshot-bound eligibility checks output for the future approved product workflow. Acceptance: On a future authorized candidate revision, eligibility is repeatable for the same snapshot and rule versions, every unmet mandatory input has an explained blocking reason, and ineligible cases issue zero model calls; record candidate SHA and environment.. Output: Implement deterministic snapshot-bound eligibility checks. Cases: TC43, TC44, TC45; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md.

  #### [Task][backend]Verify snapshot-bound eligibility and explanations — TK45

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK04; WP: WP03; CUS: CUS05; features: FEAT05, FEAT31; SR: SR10, SR11, SR53, SR58; dependencies: TK44; decisions: D02; planned cases: TC43, TC44, TC45.

  Acceptance: On the named candidate SHA and environment, the tester repeats eligibility fixtures and inspects call evidence for deterministic results/reasons and zero calls on ineligible cases, then records each pass/fail/blocked result, defect, and evidence link.

  Outputs: Candidate-specific eligibility fixture results and verification report

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md

  - **[Task][backend]Verify repeatable eligibility and zero-call ineligible behavior — STK130** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Prepare the bounded verify repeatable eligibility and zero-call ineligible behavior output for the future approved product workflow. Acceptance: On a future authorized candidate SHA, repeat eligibility fixtures and inspect call evidence to confirm identical results/reasons and zero calls for every ineligible case; record fixture pass/fail, blocked cases, defects, and evidence links.. Output: Verify repeatable eligibility and zero-call ineligible behavior. Cases: TC43, TC44, TC45; decisions: D02; source: docs/management/product-requirements.md, docs/management/system-requirements.md.
### [Task][backend]Implement customer models and manual execution — TK05

#### [Task][backend]Implement customer models and manual execution — TK05

Priority: ; requirement status: Planned; readiness: ; work kind: ; planned owner: Primary Coordinator — Yi Tang (planned aggregate coordination); parent: ; WP: WP04; CUS: ; features: ; SR: ; dependencies: TK04; decisions: ; planned cases: TC08, TC09, TC10, TC20.

  #### [Task][architecture]Identify credential protection outcomes and D03 questions — TK36

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK05; WP: WP04; CUS: CUS06; features: FEAT33; SR: SR13, SR54, SR59; dependencies: ; decisions: D03; planned cases: TC46.

  Acceptance: The requirements note lists credential-protection outcomes and relevant user-visible/operational surfaces linked to SR54/SR59. For any candidate provider/service it records cited source facts about terms and data handling, applicability questions, unknown facts, and the qualified review needed; access, retention, deletion, rotation, tenancy and provider obligations remain open for D03 owner decision. It makes no legal conclusion and prescribes no dataflow or internal boundary.

  Outputs: Credential, provider-term and data-handling applicability facts/questions; unresolved D03 owner decisions

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][architecture]Assess credential, provider-term and data-handling questions — STK112** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). Collect requirements and source facts needed to assess credential and provider data-handling applicability; keep unresolved questions open. Acceptance: For each candidate provider/service, the note cites available term/data-handling facts or labels them unavailable, identifies relevant data categories and applicability questions, lists unknown facts and the qualified review needed, and records D03 owner decisions still required; it makes no legal conclusion and designs no dataflow or boundary.. Output: Credential and provider data-handling applicability inventory and open D03 questions. Cases: TC46; decisions: D03; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][backend]Research model connection capabilities — TK37

  Priority: P0; requirement status: Planned; readiness: Proposed; work kind: decision_research; planned owner: System Architect — Feng Guo; parent: TK05; WP: WP04; CUS: CUS06; features: FEAT32; SR: SR30, SR55, SR57; dependencies: ; decisions: D03; planned cases: TC47.

  Acceptance: For each required connection capability, the research record gives an authoritative source or marks the fact unknown, records the source date and support claim, and identifies portability cases without inferring unsupported provider capabilities; evidence gaps and D03 decisions are listed.

  Outputs: Evidence-backed capability matrix format with provider facts left pending until official source review

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][backend]Define capability evidence fields and official-source citation needs — STK114** (contract_design; Planned; Proposed; owner System Architect — Feng Guo). Produce capability matrix template for Research model connection capabilities. Use only the assigned DATARA scope; label unverified evidence and unresolved decisions explicitly. Acceptance: Given each capability claim, the evidence matrix names the official source needed, records verified facts separately from unknowns, and does not assert unsupported provider capability.. Output: capability matrix template. Cases: TC47; decisions: D03; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][backend]Specify model connection request and outcome expectations — TK38

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: contract_design; planned owner: System Architect — Feng Guo; parent: TK05; WP: WP04; CUS: CUS06; features: FEAT06, FEAT32; SR: SR30, SR55, SR57; dependencies: ; decisions: D03; planned cases: TC49.

  Acceptance: The requirements note lists user-relevant request inputs, explicit selected-connection/model choice, declared success/failure outcomes and no-fallback behavior; every unsupported fact and compatibility/D03 decision is marked open, with no internal request design selected.

  Outputs: Shared model connection expectations and capability/failure cases

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][backend]Draft shared model request expectations — STK116** (contract_design; Planned; Blocked on decision; owner System Architect — Feng Guo). Produce shared model request expectations for Specify model connection request and outcome expectations. Use only the assigned DATARA scope; label unverified evidence and unresolved decisions explicitly. Acceptance: Given a declared skill request and selected connection, the shared expectations identify required request content and user-visible outcomes while leaving unresolved compatibility and D03 choices open.. Output: Shared request and outcome expectations with open decisions. Cases: TC49; decisions: D03; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][frontend]Specify explicit connection and model selection — TK39

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: contract_design; planned owner: UI Designer — Wu Yunzhou; parent: TK05; WP: WP04; CUS: CUS06; features: FEAT34; SR: SR12, SR56; dependencies: TK36, TK37, TK38; decisions: D03; planned cases: TC48.

  Acceptance: The proposed user-facing requirements cover selected choice, confirmation, unavailable/failed state, recovery, and accessible text/keyboard operation; unresolved accessibility applicability and D03 choices are explicit, with no automatic substitution.

  Outputs: Selection, unavailable, and no-fallback interaction states

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][frontend]Specify selected connection/model display and confirmation states — STK118** (contract_design; Planned; Blocked on decision; owner UI Designer — Wu Yunzhou). Identify user-visible selection, unavailable, and recovery outcomes without choosing an internal design. Acceptance: Given available and unavailable selected-connection cases, the user-facing requirements identify the displayed selection, confirmation, blocked or failed outcome, and recovery action without substitution.. Output: Selected-connection user outcome requirements. Cases: TC48; decisions: D03; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][backend]Define selected-connection capability checks — TK40

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: contract_design; planned owner: System Architect — Feng Guo; parent: TK05; WP: WP04; CUS: CUS06; features: FEAT32; SR: SR55; dependencies: TK36, TK37, TK38; decisions: D03; planned cases: TC47.

  Acceptance: For each required skill capability and selected-connection case, the criteria state whether execution is eligible, the user-facing missing-capability reason when blocked, and that no analysis request occurs while blocked; each capability fact is cited or explicitly unknown.

  Outputs: Capability needs, unsupported-execution result and explanation

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][backend]Define required capability versus selected connection comparison — STK120** (contract_design; Planned; Blocked on decision; owner System Architect — Feng Guo). Produce compatibility rule for selected-connection capability checks. Use only the assigned DATARA scope; label unverified evidence and unresolved decisions explicitly. Acceptance: Given each required skill capability and selected connection, the compatibility criteria state when execution is eligible and when it must be blocked with the missing capability explained; unsupported facts stay unknown until sourced.. Output: compatibility rule. Cases: TC47; decisions: D03; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][operations]Define safe model connection outcome evidence — TK41

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: contract_design; planned owner: System Architect — Feng Guo; parent: TK05; WP: WP04; CUS: CUS06; features: FEAT35; SR: SR57, SR59; dependencies: TK36, TK37, TK38; decisions: D03; planned cases: TC50.

  Acceptance: The evidence examples distinguish the planned success, authentication, temporary, timeout and malformed-response outcomes while excluding credential values; each unresolved lifecycle, retention and D03 owner decision is listed separately, with no event or logging schema selected.

  Outputs: Safe operational outcome-evidence examples and unresolved lifecycle questions

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md

  - **[Task][operations]Identify safe connection outcome evidence — STK122** (decision_research; Planned; Blocked on decision; owner System Architect — Feng Guo). Produce examples of outcome evidence sufficient for diagnosis without choosing an event or logging schema. Use only the assigned DATARA scope; label unverified evidence and unresolved decisions explicitly. Acceptance: Given success and failure outcomes, each proposed evidence example distinguishes the outcome sufficiently for diagnosis and excludes credential values; event fields, retention, and lifecycle controls remain undecided.. Output: Safe outcome-evidence examples. Cases: TC50; decisions: D03; source: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md, docs/management/decision-register.md.

  #### [Task][backend]Implement customer-selected model connections — TK46

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK05; WP: WP04; CUS: CUS06; features: FEAT06, FEAT32, FEAT33, FEAT34, FEAT35; SR: SR12, SR13, SR30, SR54, SR55, SR56, SR57, SR59; dependencies: TK36, TK38, TK39, TK40, TK41; decisions: D03; planned cases: TC46, TC47, TC48, TC49, TC50.

  Acceptance: For an authorized candidate SHA and named environment, the future implementation uses only the selected customer connection, blocks unsupported capability with an explanation, excludes credential values from outputs/evidence, and distinguishes declared outcomes; attach fixture results and defects. Actual supported-customer-model integration remains a separate release gate (TC08).

  Outputs: Future selected-connection behavior and candidate-specific verification record

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md

  - **[Task][backend]Support customer-selected connections with protected credentials — STK132** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Future planned implementation: support the explicitly selected customer connection and apply the credential-protection design approved under D03. Acceptance: On a future authorized candidate revision, only the explicitly selected customer connection is used, unsupported capability blocks with an explanation, credentials are excluded from outputs/evidence, and declared outcomes remain distinguishable; record candidate SHA and environment.. Output: Planned credential protection and explicit selected-connection behavior. Cases: TC46, TC47, TC48, TC49, TC50; decisions: D03; source: docs/management/product-requirements.md, docs/management/system-requirements.md.

  #### [Task][backend]Verify customer-selected model connections — TK47

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK05; WP: WP04; CUS: CUS06; features: FEAT06, FEAT32, FEAT33, FEAT34, FEAT35; SR: SR12, SR13, SR30, SR54, SR55, SR56, SR57, SR59; dependencies: TK46; decisions: D03; planned cases: TC46, TC47, TC48, TC49, TC50.

  Acceptance: On the named candidate SHA and environment, the tester uses deterministic mock/contract cases to verify selected connection, no fallback, capability blocking, credential exclusion, and distinct outcomes; records each pass/fail/blocked result, defects, and evidence. This does not satisfy real supported-model integration TC08.

  Outputs: Candidate-specific mock/contract results, defects, and verification report

  Sources: docs/management/product-requirements.md, docs/management/system-requirements.md, docs/management/wp01-requirements-package.md

  - **[Task][backend]Verify selected-connection choice and unsupported-execution outcomes — STK134** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Future planned verification: confirm analysis uses the selected connection, never substitutes another, and explains unsupported execution. Acceptance: On a future authorized candidate SHA, run deterministic mock/contract cases for selected-connection choice, no fallback, capability blocking, credential exclusion, and declared outcomes; record fixture pass/fail, blocked cases, defects, and evidence links. Actual supported-customer-model integration remains a separate release gate.. Output: Verify selected-connection routing, no fallback and unsupported-capability blocking. Cases: TC46, TC47, TC48, TC49, TC50; decisions: D03; source: docs/management/product-requirements.md, docs/management/system-requirements.md.

  #### [Task][backend]Implement explicit run selection binding — TK52

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK05; WP: WP04; CUS: CUS07; features: FEAT07; SR: SR14; dependencies: TK50, TK51; decisions: D03; planned cases: TC62.

  Acceptance: Given an eligible dataset, chosen skill and selected customer model, when a run is submitted, then the saved run identifies those exact selections and unavailable access does not invoke a different connection; oracle TC62.

  Outputs: Manual run behavior preserving explicit user selections

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Capture immutable selections — STK204** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Capture immutable selections. Given a submitted user selection and the resulting run request, when the fixed-candidate test compares scope/snapshot/skill/model, then every value equals the selection; oracle TC62. Acceptance: Given a submitted user selection and the resulting run request, when the fixed-candidate test compares scope/snapshot/skill/model, then every value equals the selection; oracle TC62.. Output: Selection binding behavior. Cases: TC62; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Bind selections to adapter dispatch — STK205** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Bind selections to adapter dispatch. Given an unavailable selected connection, when run submission is attempted, then the request fails explicitly without dispatch to another connection; oracle TC62. Acceptance: Given an unavailable selected connection, when run submission is attempted, then the request fails explicitly without dispatch to another connection; oracle TC62.. Output: No-fallback selection behavior. Cases: TC62; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][backend]Implement persisted run state transitions — TK53

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK05; WP: WP04; CUS: CUS07; features: FEAT07; SR: SR14, SR15; dependencies: TK50, TK51; decisions: D03; planned cases: TC60, TC63.

  Acceptance: Given success, malformed response, timeout, authentication failure and provider error, when the run is saved, then status matches the actual outcome and only validated output is marked successful; oracle TC60/TC63.

  Outputs: Persisted run outcomes matching actual execution

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Implement allowed transitions — STK206** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Implement allowed transitions. Given valid and failed executions, when their lifecycle is persisted, then the actual terminal outcome is retained on the run; oracle TC60. Acceptance: Given valid and failed executions, when their lifecycle is persisted, then the actual terminal outcome is retained on the run; oracle TC60.. Output: Persisted run transitions. Cases: TC60, TC63; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Persist failure distinct from success — STK207** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Persist failure distinct from success. Given malformed output, auth failure, and timeout, when each run is reloaded, then none is marked successful; oracle TC60/TC63. Acceptance: Given malformed output, auth failure, and timeout, when each run is reloaded, then none is marked successful; oracle TC60/TC63.. Output: Persistent non-success outcomes. Cases: TC60, TC63; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][backend]Implement fail-closed output validation — TK55

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK05; WP: WP04; CUS: CUS07; features: FEAT40; SR: SR15, SR70; dependencies: TK50, TK51; decisions: D02, D03; planned cases: TC61.

  Acceptance: Given one valid response and malformed or mismatched fixtures, when each run completes, then only the valid matching response becomes a finding and every other outcome remains failed with no finding; oracle TC61/TC66.

  Outputs: Fail-closed output validation behavior

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Validate output against approved run contract — STK210** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Validate output against the approved run contract. Given a response and its associated run, when the response is evaluated against the approved validity criteria and selected run context, then only a valid matching response is exposed as a finding and invalid or mismatched output remains non-success; oracle TC61. Acceptance: Given a response and associated run, when the approved validity criteria are applied, then only a valid response matching the run context is exposed as a finding and malformed, unsupported or mismatched output remains a non-success; oracle TC61.. Output: Accepted matching response behavior. Cases: TC61; decisions: D02, D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Record invalid output as non-success — STK211** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Record invalid output as non-success. Given malformed or mismatched responses, when output validation completes, then no finding is exposed and the run remains an explicit non-success; oracle TC61/TC66. Acceptance: Given malformed or mismatched responses, when output validation completes, then no finding is exposed and the run remains an explicit non-success; oracle TC61/TC66.. Output: Rejected response behavior. Cases: TC61; decisions: D02, D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][security]Implement safe credential and error outputs — TK70

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK05; WP: WP04; CUS: CUS07, CUS10; features: FEAT07, FEAT44; SR: SR70, SR74; dependencies: TK51; decisions: D03; planned cases: TC63, TC76.

  Acceptance: Given successful and failed run outputs with controlled secret/provider-payload sentinels, when saved status/result/dashboard/API representations are retrieved, then no credential or raw provider payload appears and failure remains explicit; logs remain under existing SR13; oracle TC63/TC76.

  Outputs: Sanitized saved run outputs without changing failure status

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][security]Implement safe failure mapping — STK240** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Implement safe failure mapping. Given a saved success/failure containing controlled sensitive sentinels, when supported user-facing output is produced, then safe status remains while secret/provider raw payloads are absent; oracle TC63/TC76. Acceptance: Given a saved success/failure containing controlled sensitive sentinels, when supported user-facing output is produced, then safe status remains while secret/provider raw payloads are absent; oracle TC63/TC76.. Output: Sanitized run outcome behavior. Cases: TC63, TC76; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][security]Redact sensitive output fields — STK241** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Redact sensitive output fields. Given a response includes secret or raw provider-error fields, when saved result/dashboard/API representations are read, then those fields are not exposed; logs remain outside this requirement under SR13; oracle TC63/TC76. Acceptance: Given a response includes secret or raw provider-error fields, when saved result/dashboard/API representations are read, then those fields are not exposed; logs remain outside this requirement under SR13; oracle TC63/TC76.. Output: Safe user-facing output filtering. Cases: TC63, TC76; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.
### [Task][backend]Deliver result history dashboard and API — TK06

#### [Task][backend]Deliver result history dashboard and API — TK06

Priority: ; requirement status: Planned; readiness: ; work kind: ; planned owner: Primary Coordinator — Yi Tang (planned aggregate coordination); parent: ; WP: WP05; CUS: ; features: ; SR: ; dependencies: TK03, TK05; decisions: ; planned cases: TC11, TC12, TC13, TC14, TC20.

  #### [Task][backend]Implement persistent immutable history — TK57

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK06; WP: WP05; CUS: CUS08; features: FEAT08; SR: SR16, SR17; dependencies: TK56; decisions: D04; planned cases: TC64, TC65, TC67.

  Acceptance: Given a saved result and a later run over the same scope, when the owner reloads history after restart, then both remain retrievable with each run own input, preprocessing, skill/model, time and evidence references; oracle TC64/65/67.

  Outputs: Persistent history with independent lineage per run

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Persist result/snapshot lineage — STK214** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Persist result/snapshot lineage. Given a saved result, when its owner reloads history, then snapshot, preprocessing, skill/model, time and evidence references resolve to the actual run/input; oracle TC64. Acceptance: Given a saved result, when its owner reloads history, then snapshot, preprocessing, skill/model, time and evidence references resolve to the actual run/input; oracle TC64.. Output: Resolved saved lineage. Cases: TC64, TC65, TC67; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Create rerun without overwrite — STK215** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Create rerun without overwrite. Given two runs of the same scope, when both are retrieved, then both have separate identifiers and the first record contents remain unchanged; oracle TC65. Acceptance: Given two runs of the same scope, when both are retrieved, then both have separate identifiers and the first record contents remain unchanged; oracle TC65.. Output: Append-only assessment history. Cases: TC64, TC65, TC67; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][backend]Implement snapshot-bound evidence lookup — TK58

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK06; WP: WP05; CUS: CUS08; features: FEAT41; SR: SR16, SR72; dependencies: TK56; decisions: D04; planned cases: TC66.

  Acceptance: Given valid, broken, cross-snapshot and unauthorized evidence references, when the result owner opens a saved finding, then only authorized references to that result snapshot resolve and the others are shown unavailable; oracle TC66.

  Outputs: Snapshot-bound evidence retrieval behavior

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Resolve evidence to snapshot — STK216** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Resolve evidence to snapshot. Given a valid evidence reference from the saved snapshot, when the owner opens the finding, then the referenced source evidence is available for that same result; oracle TC66. Acceptance: Given a valid evidence reference from the saved snapshot, when the owner opens the finding, then the referenced source evidence is available for that same result; oracle TC66.. Output: Same-snapshot evidence behavior. Cases: TC66; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Return unavailable for invalid references — STK217** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Return unavailable for invalid references. Given broken, cross-snapshot, or unauthorized references, when the owner opens the result, then each is explicitly unavailable and no alternate evidence is substituted; oracle TC66. Acceptance: Given broken, cross-snapshot, or unauthorized references, when the owner opens the result, then each is explicitly unavailable and no alternate evidence is substituted; oracle TC66.. Output: Unavailable invalid evidence behavior. Cases: TC66; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][frontend]Implement saved dashboard and accessible states — TK61

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK06; WP: WP05; CUS: CUS07, CUS08, CUS09, CUS10; features: FEAT09, FEAT46; SR: SR18, SR31, SR75, SR76; dependencies: TK60, TK73; decisions: D04, D05; planned cases: TC68, TC69, TC78.

  Acceptance: Given approved saved records and model access disabled, when the owner views the dashboard, then values match saved records without inference, failures remain explicit, and approved keyboard/status/error behavior is present; oracle TC68/69/78.

  Outputs: Dashboard behavior for saved values, failures and accessible states

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][frontend]Render saved contract fields/states — STK222** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Render saved contract fields/states. Given approved saved result records, when the owner views history/readiness, then displayed values and failures match stored outcomes without an inference request; oracle TC68-TC70. Acceptance: Given approved saved result records, when the owner views history/readiness, then displayed values and failures match stored outcomes without an inference request; oracle TC68-TC70.. Output: Contract-backed saved dashboard values. Cases: TC68, TC69, TC78; decisions: D04, D05; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][frontend]Implement keyboard/focus/status behavior — STK223** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Implement keyboard/focus/status behavior. Given dashboard controls, errors, and async status changes, when the approved accessibility behaviors are implemented, then controls are keyboard-operable, focus is perceivable, errors identify controls, and status is semantic; oracle TC78. Acceptance: Given dashboard controls, errors, and async status changes, when the approved accessibility behaviors are implemented, then controls are keyboard-operable, focus is perceivable, errors identify controls, and status is semantic; oracle TC78.. Output: Accessible dashboard interaction behavior. Cases: TC68, TC69, TC78; decisions: D04, D05; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][backend]Implement authorized read-only API — TK64

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK06; WP: WP05; CUS: CUS09, CUS10; features: FEAT42; SR: SR19, SR31, SR73; dependencies: TK63, TK66; decisions: D04; planned cases: TC70, TC71, TC72, TC73.

  Acceptance: Given the approved read-only API contract and a saved result, when the owner retrieves it, then values match the dashboard, foreign resources are denied, and non-read methods leave state unchanged; oracle TC70-TC74.

  Outputs: Authorized read-only retrieval behavior

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Implement approved authorized result retrieval — STK228** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Given an authorized owner and a saved result, when the approved read-only output is retrieved, then only permitted saved values are returned and they match the stored result; D04 controls the operation and representation; oracle TC70/TC71. Acceptance: Given an authorized owner and saved result, when the approved read-only output is retrieved, then returned values match the saved result and expose no unauthorized data; the approved operation and representation remain governed by D04; oracle TC70/TC71.. Output: Implemented saved-resource reads. Cases: TC70, TC71, TC72, TC73; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Implement scoped queries/mutation rejection — STK229** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Implement scoped queries/mutation rejection. Given an attempted mutation or foreign read, when the approved API is used, then stored data is unchanged and no foreign output is returned; oracle TC71/TC73. Acceptance: Given an attempted mutation or foreign read, when the approved API is used, then stored data is unchanged and no foreign output is returned; oracle TC71/TC73.. Output: Read-only and owner-scoped API behavior. Cases: TC70, TC71, TC72, TC73; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][frontend]Implement identity-bound asynchronous UI state — TK68

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: implementation; planned owner: Worker — Torsten Maier; parent: TK06; WP: WP05; CUS: CUS10; features: FEAT43; SR: SR21, SR71; dependencies: TK66; decisions: D04; planned cases: TC75.

  Acceptance: Given user A has a delayed history/result response and user B becomes active before it arrives, when the response completes, then no user A value renders for user B; it is discarded or authorized for B; oracle TC75.

  Outputs: Identity-change handling for delayed results

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][frontend]Keep prior-identity data out of the current view — STK236** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Given identity A changes to identity B while an A request is pending, when the A response arrives, then A data is not visible in B current view; oracle TC75. Acceptance: Given identity A changes to identity B while an A request is pending, when the response arrives, then no A data is visible in B current view; oracle TC75.. Output: Identity-state invalidation behavior. Cases: TC75; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][frontend]Discard or reauthorize stale responses — STK237** (implementation; Planned; Blocked on decision; owner Worker — Torsten Maier). Discard or reauthorize stale responses. Given a delayed response from the prior identity, when it arrives after the change, then it is discarded or authorized for the current identity before rendering; oracle TC75. Acceptance: Given a delayed response from the prior identity, when it arrives after the change, then it is discarded or authorized for the current identity before rendering; oracle TC75.. Output: Stale-response handling. Cases: TC75; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.
### [Task][management]Verify P0 and validate athlete journey — TK07

#### [Task][management]Verify P0 and validate athlete journey — TK07

Priority: ; requirement status: Planned; readiness: ; work kind: ; planned owner: Primary Coordinator — Yi Tang (planned aggregate coordination); parent: ; WP: WP06; CUS: ; features: ; SR: ; dependencies: TK01, TK02, TK03, TK04, TK05, TK06; decisions: ; planned cases: TC01, TC02, TC03, TC04, TC05, TC06, TC07, TC08, TC09, TC10, TC11, TC12, TC13, TC14, TC15, TC19, TC20.

  #### [Task][management]Verify FIT classification and file disposition — TK12

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS01; features: FEAT01; SR: SR01, SR02, SR27, SR32; dependencies: TK11; decisions: D01; planned cases: TC01, TC19, TC21.

  Acceptance: On the fixed candidate, execute supported, malformed, unsupported and missing-field fixtures; oracle: dispositions/reasons match the approved matrix and rendered text identifies file/outcome; record actual environment, result and limits.

  Outputs: Candidate-specific TC01/TC19/TC21 verification record

  Sources: docs/management/validation-plan.md, docs/management/p0-ui-requirements-review.md

  - **[Task][management]Run source conformance fixtures — STK007** (; Planned; Blocked on decision; owner User Tester — Abt Hermann). Execute approved supported, malformed, unsupported and missing-field fixtures against fixed candidate. Acceptance: Record actual result and target commit per fixture; oracle: outcomes/reasons match approved matrix or a reproducible defect is logged.. Output: TC01/TC19 candidate evidence record. Cases: TC01, TC19; decisions: D01; source: docs/management/validation-plan.md.

  - **[Task][management]Inspect rendered file disposition — STK008** (; Planned; Blocked on decision; owner User Tester — Abt Hermann). Inspect file-linked text and rejection reasons for approved fixtures in the fixed rendered UI. Acceptance: Record actual rendered result/viewport and any failure; oracle: file/outcome/reason are identifiable without color/icon alone per TC21.. Output: TC21 candidate rendered evidence. Cases: TC21; decisions: D01; source: docs/management/p0-ui-requirements-review.md.

  #### [Task][management]Verify original preservation and history behavior — TK16

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS02; features: FEAT02; SR: SR03, SR04, SR33; dependencies: TK15; decisions: D01; planned cases: TC02, TC03, TC22.

  Acceptance: On the fixed candidate, reload originals, re-import identical bytes and submit approved conflict fixtures; oracle: integrity/source links resolve, duplicate count is unchanged, conflict remains visible, and actual results/limits are recorded. Record a keyboard-only and semantic/text inspection of duplicate and conflict states, including whether names, status and reason are available without color; mark each check pass/fail/blocked and leave any required standard or conformance decision open under D05.

  Outputs: Candidate-specific TC02/TC03/TC22 verification record

  Sources: docs/management/validation-plan.md, docs/management/p0-ui-requirements-review.md

  - **[Task][management]Verify original integrity and lineage — STK015** (; Planned; Blocked on decision; owner User Tester — Abt Hermann). Reload original files and resolve normalized records to their stored source on fixed candidate. Acceptance: Actual digest and source-link outcomes are recorded for fixtures; oracle: bytes and lineage match TC02 or a defect is logged.. Output: Candidate-specific TC02 evidence. Cases: TC02; decisions: D01; source: docs/management/validation-plan.md.

  - **[Task][management]Verify duplicate and conflict history states — STK016** (; Planned; Blocked on decision; owner User Tester — Abt Hermann). Repeat identical imports and exercise approved logical-conflict fixtures against rendered history. Acceptance: Record actual state/count and candidate/viewport; oracle: duplicate is not counted twice and conflict remains textually unresolved per TC03/TC22.. Output: Candidate-specific TC03/TC22 evidence. Cases: TC03, TC22; decisions: D01; source: docs/management/validation-plan.md, docs/management/p0-ui-requirements-review.md.

  #### [Task][management]Verify deterministic normalization — TK19

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS03; features: FEAT03; SR: SR05, SR06; dependencies: TK18; decisions: D01; planned cases: TC04.

  Acceptance: On the fixed candidate, repeat preparation with inference disabled; oracle: semantic output matches excluding permitted IDs/timestamps and observed inference calls equal zero; record actual environment/results.

  Outputs: Candidate-specific TC04 verification record

  Sources: docs/management/validation-plan.md, docs/management/p0-ui-requirements-review.md

  - **[Task][management]Verify repeat preparation and model isolation — STK021** (; Planned; Blocked on decision; owner User Tester — Abt Hermann). Run the same approved source/configuration twice while inference access is disabled and record actual candidate results. Acceptance: Target commit/environment and repeat outputs are recorded; oracle: semantic values match under TC04.. Output: Candidate-specific TC04 evidence. Cases: TC04; decisions: D01; source: docs/management/validation-plan.md.

  - **[Task][management]Record repeat-preparation outcomes — STK026** (; Planned; Blocked on decision; owner User Tester — Abt Hermann). Execute two runs with fixed source/configuration/version and compare semantic output fields. Acceptance: Target commit/environment and both outputs are recorded; oracle: equality excludes only approved generated IDs and processing timestamps per TC04.. Output: Repeat-preparation candidate evidence. Cases: TC04; decisions: D01; source: docs/management/validation-plan.md.

  #### [Task][management]Verify scoped input provenance and readiness — TK22

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS03; features: FEAT21; SR: SR07, SR28, SR34; dependencies: TK21; decisions: D01, D02; planned cases: TC05, TC20, TC23.

  Acceptance: On the fixed candidate, inspect narrow scope, envelope and rendered labels; oracle: included values are declared/in-scope with resolvable lineage, absent optional data is not zero, and negative secret/out-of-scope examples reject; record actual evidence. Record keyboard-only and semantic/text inspection of scope, provenance, readiness and unavailable-value states; mark each check pass/fail/blocked and leave any required standard or conformance decision open under D05.

  Outputs: Candidate-specific TC05/TC20/TC23 verification record

  Sources: docs/management/validation-plan.md, docs/management/p0-ui-requirements-review.md

  - **[Task][management]Verify scope provenance and readiness labels — STK022** (; Planned; Blocked on decision; owner User Tester — Abt Hermann). Inspect a narrow prepared-data envelope and rendered readiness state with missing optional values and warnings. Acceptance: Target commit/viewport and actual displayed and packaged fields are recorded; oracle: all fields are in selected declared scope with resolvable lineage and missing optional data is not shown as zero per TC05/20/23.. Output: Candidate-specific TC05/TC20/TC23 evidence. Cases: TC05, TC20, TC23; decisions: D01, D02; source: docs/management/validation-plan.md, docs/management/p0-ui-requirements-review.md.

  - **[Task][management]Verify envelope scope and rendered provenance — STK028** (; Planned; Blocked on decision; owner User Tester — Abt Hermann). Inspect prepared envelope and readiness display using a narrow known fixture with absent optional data. Acceptance: Candidate commit, viewport and field links are recorded; oracle: TC05/20/23 show only declared in-scope fields, resolvable evidence and unavailable rather than zero.. Output: Scoped input/provenance verification evidence. Cases: TC05, TC20, TC23; decisions: D01, D02; source: docs/management/validation-plan.md, docs/management/p0-ui-requirements-review.md.

  #### [Task][backend]Verify run states and invalid output — TK54

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS07, CUS08; features: FEAT07, FEAT40; SR: SR14, SR15, SR70; dependencies: TK52, TK53, TK55; decisions: D02, D03; planned cases: TC60, TC61.

  Acceptance: On a fixed candidate, execute valid, malformed, mismatched, authentication and timeout fixtures; compare saved and visible states with the approved contract and record candidate SHA, environment, fixture IDs and actual outcomes; oracle TC60/TC61.

  Outputs: Candidate-specific run state and invalid-output verification

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Prepare disposable response fixtures — STK208** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Prepare disposable response fixtures. Given the approved run contract, when synthetic success/malformed/mismatch/auth/timeout responses are prepared, then each fixture has an identifier and expected state before execution; oracle TC60/TC61. Acceptance: Given the approved run contract, when synthetic success/malformed/mismatch/auth/timeout responses are prepared, then each fixture has an identifier and expected state before execution; oracle TC60/TC61.. Output: Identified controlled response fixtures. Cases: TC60, TC61; decisions: D02, D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Execute and record outcomes — STK209** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Execute and record outcomes. Given those fixtures on the fixed candidate, when each run is executed and reloaded, then actual visible and saved states are compared with expected states and recorded with SHA/environment; oracle TC60/TC61. Acceptance: Given those fixtures on the fixed candidate, when each run is executed and reloaded, then actual visible and saved states are compared with expected states and recorded with SHA/environment; oracle TC60/TC61.. Output: Candidate-specific run observations. Cases: TC60, TC61; decisions: D02, D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][backend]Verify lineage, rerun, evidence and restart — TK59

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS08; features: FEAT08, FEAT41; SR: SR16, SR17, SR72; dependencies: TK57, TK58; decisions: D04; planned cases: TC64, TC65, TC66, TC67.

  Acceptance: On a fixed candidate, save a result, restart, rerun the same scope and retrieve valid/broken/foreign references; record whether the first result remains unchanged and each reference matches the approved contract; oracle TC64-TC67.

  Outputs: Candidate-specific history and evidence verification

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Prepare disposable history fixtures — STK218** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Prepare disposable history fixtures. Given fixtures for lineage, repeat runs, and valid/broken/foreign evidence, when they are prepared, then expected references and values are independently recorded before execution; oracle TC64-TC67. Acceptance: Given fixtures for lineage, repeat runs, and valid/broken/foreign evidence, when they are prepared, then expected references and values are independently recorded before execution; oracle TC64-TC67.. Output: Identified history and evidence fixtures. Cases: TC64, TC65, TC66, TC67; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Execute restart/rerun/reference cases — STK219** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Execute restart/rerun/reference cases. Given the fixed candidate, when restart, rerun, and reference cases execute, then prior results and reference outcomes are compared with expected observations and recorded; oracle TC64-TC67. Acceptance: Given the fixed candidate, when restart, rerun, and reference cases execute, then prior results and reference outcomes are compared with expected observations and recorded; oracle TC64-TC67.. Output: Actual persistence and evidence findings. Cases: TC64, TC65, TC66, TC67; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][frontend]Verify dashboard values, offline viewing and accessibility — TK62

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS07, CUS08, CUS09, CUS10; features: FEAT09, FEAT46; SR: SR18, SR31, SR75, SR76; dependencies: TK61; decisions: D04, D05; planned cases: TC68, TC69, TC70, TC78.

  Acceptance: On a fixed candidate with inference disabled, render approved empty/populated/warning/failure/denied states; compare saved values with API and perform the approved keyboard/assistive-technology checks; record viewport, browser, setup, fixture IDs and observations; oracle TC68-TC70/78.

  Outputs: Rendered dashboard and accessibility verification record

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][frontend]Prepare saved value/state fixtures — STK224** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Prepare saved value/state fixtures. Given approved UI states and persisted success/failure/readiness values, when test fixtures are assembled, then each expected display value/state is traceable to a saved record; oracle TC68-TC70. Acceptance: Given approved UI states and persisted success/failure/readiness values, when test fixtures are assembled, then each expected display value/state is traceable to a saved record; oracle TC68-TC70.. Output: Traceable dashboard fixtures. Cases: TC68, TC69, TC70, TC78; decisions: D04, D05; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][frontend]Render, compare, and execute keyboard/AT checks — STK225** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Render, compare, and execute keyboard/AT checks. Given the fixed candidate and approved accessibility setup, when saved states are rendered and traversed, then observed values match saved/API data and keyboard/status outcomes are recorded; oracle TC68-TC70/TC78. Acceptance: Given the fixed candidate and approved accessibility setup, when saved states are rendered and traversed, then observed values match saved/API data and keyboard/status outcomes are recorded; oracle TC68-TC70/TC78.. Output: Rendered saved-value and accessibility observations. Cases: TC68, TC69, TC70, TC78; decisions: D04, D05; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][backend]Verify API parity, paging and read-only behavior — TK65

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS09, CUS10; features: FEAT42; SR: SR19, SR31, SR73; dependencies: TK64; decisions: D04; planned cases: TC70, TC71, TC72, TC73.

  Acceptance: On a fixed candidate with owner and second disposable account, compare dashboard/API values, repeat approved cursors, submit invalid queries and attempt mutations; record each observation against the approved contract; oracle TC70-TC74.

  Outputs: Candidate-specific API parity, pagination and mutation verification

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][backend]Run parity and cursor cases — STK230** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Run parity and cursor cases. Given the owner dashboard and API views for one saved fixture, when matching fields are compared, then values and stable IDs agree under the approved contract; oracle TC70. Acceptance: Given the owner dashboard and API views for one saved fixture, when matching fields are compared, then values and stable IDs agree under the approved contract; oracle TC70.. Output: Parity comparison result. Cases: TC70, TC71, TC72, TC73; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][backend]Run query-negative/mutation probes — STK231** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Run query-negative/mutation probes. Given approved cursor/query rules, when valid repeated pages and invalid queries are exercised, then page results follow the approved order and invalid queries return the specified error; oracle TC72. Acceptance: Given approved cursor/query rules, when valid repeated pages and invalid queries are exercised, then page results follow the approved order and invalid queries return the specified error; oracle TC72.. Output: Pagination and query observations. Cases: TC70, TC71, TC72, TC73; decisions: D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][security]Verify two-user isolation and identity changes — TK69

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS07, CUS08, CUS09, CUS10; features: FEAT07, FEAT40, FEAT08, FEAT41, FEAT09, FEAT42, FEAT10, FEAT43, FEAT44, FEAT46; SR: SR14, SR15, SR16, SR17, SR18, SR19, SR20, SR21, SR31, SR70, SR71, SR72, SR73, SR74, SR75, SR76; dependencies: TK67, TK68; decisions: D03, D04; planned cases: TC14, TC15, TC73, TC74, TC75.

  Acceptance: On a fixed candidate with two disposable users, probe own/foreign file, run, history, dashboard and API access, then follow a selected manual run through saved history to retrieval; record TC14/TC73-TC75 and provide the CUS07-CUS10 journey inputs for separate TC15 athlete validation; TC79 remains a separate audit.

  Outputs: Candidate-specific isolation verification and TC15 handoff

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][security]Prepare two-user requests — STK238** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Prepare two-user requests. Given two disposable accounts, when owner and foreign IDs/cursors are prepared, then each protected boundary has one reproducible positive and negative request; oracle TC73/TC74. Acceptance: Given two disposable accounts, when owner and foreign IDs/cursors are prepared, then each protected boundary has one reproducible positive and negative request; oracle TC73/TC74.. Output: Two-user request fixture set. Cases: TC73, TC74, TC75; decisions: D03, D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][security]Execute denials/stale-response/retrieval cases — STK239** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Execute denials/stale-response/retrieval cases. Given the fixed candidate and two accounts, when each protected path and delayed identity response is exercised, then no cross-user data appears and actual denials are recorded; oracle TC14/TC73-TC75. Acceptance: Given the fixed candidate and two accounts, when each protected path and delayed identity response is exercised, then no cross-user data appears and actual denials are recorded; oracle TC14/TC73-TC75.. Output: Observed two-user isolation results. Cases: TC73, TC74, TC75; decisions: D03, D04; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][security]Verify credential/provider-payload nondisclosure — TK71

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: verification; planned owner: User Tester — Abt Hermann; parent: TK07; WP: WP06; CUS: CUS07, CUS10; features: FEAT07, FEAT44; SR: SR70, SR74; dependencies: TK70; decisions: D03; planned cases: TC63, TC76.

  Acceptance: On a fixed candidate, inject unique sentinels into controlled success/failure outputs and inspect saved run status/result, dashboard and API only; confirm no sentinel appears and actual failure remains visible; this case does not inspect logs; oracle TC63/TC76.

  Outputs: Candidate-specific saved-output disclosure result

  Sources: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md

  - **[Task][security]Prepare unique sentinels — STK242** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Prepare unique sentinels. Given the approved test contract, when sentinel values are prepared for result and failure outputs, then each value is unique and the expected absence is recorded; oracle TC63/TC76. Acceptance: Given the approved test contract, when sentinel values are prepared for result and failure outputs, then each value is unique and the expected absence is recorded; oracle TC63/TC76.. Output: Sensitive-output fixture list. Cases: TC63, TC76; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  - **[Task][security]Inspect supported surfaces — STK243** (verification; Planned; Blocked on decision; owner User Tester — Abt Hermann). Inspect supported surfaces. Given those sentinels, when saved results/status/dashboard/API output is inspected, then actual presence/absence is recorded and no log-handling claim is made; oracle TC63/TC76. Acceptance: Given those sentinels, when saved results/status/dashboard/API output is inspected, then actual presence/absence is recorded and no log-handling claim is made; oracle TC63/TC76.. Output: Disclosure inspection observations. Cases: TC63, TC76; decisions: D03; source: docs/management/p0-breakdown-plan.md, docs/management/wp01-requirements-package.md, docs/management/p0-ui-requirements-review.md, docs/project-brief-and-roadmap.md.

  #### [Task][quality]Audit group C traceability and evidence states — TK74

  Priority: P0; requirement status: Planned; readiness: Blocked on decision; work kind: quality_audit; planned owner: Quality Manager — Wang Xiaofeng; parent: TK07; WP: WP06; CUS: CUS07, CUS08, CUS09, CUS10; features: FEAT07, FEAT40, FEAT08, FEAT41, FEAT09, FEAT42, FEAT10, FEAT43, FEAT44, FEAT46; SR: SR14, SR15, SR16, SR17, SR18, SR19, SR20, SR21, SR31, SR70, SR71, SR72, SR73, SR74, SR75, SR76; dependencies: TK54, TK59, TK62, TK65, TK69, TK71, TK72, TK73; decisions: D02, D03, D04, D05; planned cases: TC79.

  Acceptance: Given the complete fragment and frozen coverage rubric, when the independent audit runs, then every missing reciprocal link, implementation/verification mapping, dependency, or false evidence status is reported by exact row ID; no product case is marked passed. Oracle TC79.

  Outputs: Independent traceability audit findings and unresolved-gate list

  Sources: docs/management/p0-breakdown-plan.md, docs/team/workflow.md

  - **[Task][quality]Check reciprocal group C requirement links — STK248** (quality_audit; Planned; Blocked on decision; owner Quality Manager — Wang Xiaofeng). Check reciprocal group C requirement links. Given the saved fragment, when requirement references and reciprocal coverage are checked against the reserved ranges, then each discrepancy is identified by record ID and planned evidence is not called passed; oracle TC79. Acceptance: Given each owned row and reserved ID range, when IDs, reciprocal links and coverage are checked, then every discrepancy is listed by exact record ID and no planned case is reported as passed; oracle TC79.. Output: Exact-ID traceability audit findings. Cases: TC79; decisions: D02, D03, D04, D05; source: docs/management/p0-breakdown-plan.md, docs/team/workflow.md.


## CUS perspective assessments and open questions

### CUS01

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | FIT documentation and fixture terms have not been assessed; no rights or legal duty is inferred. |  | TK09 |
| engineering | applicable | Acceptance/rejection and source field rules are explicit obligations. | SR01, SR02, SR27 | TK10, TK11, TK12 |
| runtime | unknown | Decoder resource bounds require evidence and decision; no threshold selected. | SR02, SR27 | TK10, TK11 |
| architecture | applicable | A versioned source matrix defines the import boundary. | SR01, SR02, SR27 | TK10 |
| privacy_security | unknown | Upload data flow/access questions need review; CUS10 requirements do not prove this path is implemented. |  | TK13 |
| accessibility | applicable | Users need textual file outcome and approved rejection reason. | SR32 | TK11, TK12 |
| operations_backup_retention_recovery | unknown | Source failure diagnostics/recovery are not fully specified. |  | TK13 |
| domain_provenance | applicable | FIT variants and field mappings require authoritative source evidence. | SR27 | TK09, TK10 |
### CUS02

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | Rights/retention implications for uploaded and derived data are not assessed; no duration or duty is inferred. |  | TK17 |
| engineering | applicable | Original preservation, normalized source links, duplicate and conflict behavior are explicit obligations. | SR03, SR04, SR33 | TK14, TK15, TK16 |
| runtime | unknown | History growth/resource bounds and operating constraints are not selected. |  | TK17 |
| architecture | applicable | Persistent source lineage and conflict lifecycle need a defined model. | SR03, SR04 | TK14, TK15 |
| privacy_security | unknown | Access and lifecycle impacts of retained source data require assessment. |  | TK17 |
| accessibility | unknown | SR33 covers distinct duplicate and unresolved-conflict outcomes, but semantic, text-only and keyboard coverage has not been assessed. TK16 will record those applicability checks and any remaining D05 decision; no conformance claim is made. | SR33 | TK15, TK16 |
| operations_backup_retention_recovery | unknown | Retention, backup, recovery and capacity policies remain open. |  | TK17 |
| domain_provenance | applicable | Activity history retains links to original source bytes. | SR03, SR04 | TK15 |
### CUS03

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | Source/derived-data rights questions are not assessed; no legal duty is asserted. |  | TK17 |
| engineering | applicable | Deterministic normalization, no inference, and scoped skill inputs are explicit obligations. | SR05, SR06, SR07, SR28, SR34 | TK18, TK19 |
| runtime | unknown | Preprocessing resource bounds and execution environment remain unmeasured/unselected. |  | TK20 |
| architecture | applicable | Versioned canonical input packaging is proposed by SR28. | SR28 | TK18 |
| privacy_security | applicable | SR28 requires credential and out-of-scope data exclusion; a negative-case review is still planned. | SR28 | TK18, TK19 |
| accessibility | unknown | SR34 covers scope, provenance and unavailable values, but semantic, text-only and keyboard coverage has not been assessed. TK22 will record those applicability checks and any remaining D05 decision; no conformance claim is made. | SR34 | TK18, TK19, TK22 |
| operations_backup_retention_recovery | unknown | Repeatability diagnostics and recovery from preprocessing/packaging failures need assessment. |  | TK20 |
| domain_provenance | applicable | Prepared metrics and observations need traceable source/calculation lineage. | SR07, SR28, SR34 | TK18, TK19 |
### CUS04

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | Third-party methods and source use need rights review; no permission conclusion is available. |  | TK33 |
| engineering | applicable | Provider-independent versioned skill contracts and evaluation need verifiable definitions. | SR08, SR09, SR29, SR50, SR51 |  |
| runtime | unknown | Evaluation runtime and resource bounds are not defined; investigate without selecting thresholds. |  | TK32 |
| architecture | applicable | Skill declarations and output contracts distinguish data preparation from model-specific operation. | SR09, SR29, SR50 |  |
| privacy_security | unknown | Candidate skill inputs, evidence and source material access require a bounded data-flow review. |  | TK31, TK33 |
| accessibility | unknown | Catalog and selection states need an operability/text review; supported standards and technologies are not chosen. |  | TK35 |
| operations_backup_retention_recovery | unknown | Skill version retention, rollback and evidence lifecycle are not specified. |  | TK32 |
| domain_provenance | applicable | Athlete-domain claims require source provenance and must remain within reviewed skill methods. | SR52 |  |
### CUS05

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | Legal applicability of candidate-method provenance to eligibility is unassessed. TK33 records source/use questions for later review; no legal conclusion or eligibility restriction is inferred. |  | TK33 |
| engineering | applicable | Eligibility is deterministic and must block execution while identifying unmet inputs. | SR10, SR11, SR53 |  |
| runtime | unknown | Cost/latency bounds for eligibility evaluation are not established; investigate using representative fixtures. |  | TK34 |
| architecture | applicable | Eligibility is a pre-execution gate between prepared snapshots and skill/model execution. | SR10, SR53 |  |
| privacy_security | applicable | Reason outputs must not disclose another user's dataset or history. | SR11, SR53 |  |
| accessibility | applicable | Blocking gaps and selection state must be available as text and operable controls. | SR58 |  |
| operations_backup_retention_recovery | unknown | Operational monitoring and recovery for stale or failed readiness evaluation need assessment. |  | TK34 |
| domain_provenance | applicable | Eligibility must use only the skill's declared input and coverage requirements, not infer unsupported suitability. | SR10, SR53 |  |
### CUS06

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | Legal/regulatory duties for customer API credentials and provider use have not been assessed. |  | TK36 |
| engineering | applicable | Requests use an explicitly chosen connection, with success and declared failure outcomes made distinguishable. | SR12, SR30, SR55, SR56, SR57 |  |
| runtime | unknown | Timeout, retry, rate handling and deploy-time limits require official interface evidence and D03. |  | TK37, TK38, TK41 |
| architecture | applicable | Skill definitions remain independent of provider interfaces; the selected model connection is explicit. | SR30, SR55, SR56 |  |
| privacy_security | applicable | Customer secrets require scoped isolation and exclusion from payloads, outputs and logs. | SR13, SR54, SR59 |  |
| accessibility | unknown | Connection setup and error recovery need accessible-state review; no supported viewport/assistive technology is set. |  | TK39 |
| operations_backup_retention_recovery | unknown | Secret rotation/deletion/retention and safe operational evidence remain open under D03. | SR59 | TK36, TK41 |
| domain_provenance | applicable | Model differences are recorded; portability does not imply equal skill performance. | SR30, SR57 |  |
### CUS07

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | Legal/contract duties for model execution and failures remain unassessed. |  | TK72 |
| engineering | applicable | Run outcomes and invalid outputs need explicit handling. | SR14, SR15, SR70 | TK50, TK51, TK52, TK53, TK54, TK55 |
| runtime | applicable | Timeouts and provider errors affect run state. | SR15 | TK53, TK54 |
| architecture | applicable | Selection, adapter, validation, persistence are boundaries. | SR14, SR70 | TK50, TK51, TK52, TK55 |
| privacy_security | applicable | Run outcomes expose saved data and customer-model failure information; the output boundary depends on D03. | SR74 | TK70, TK71 |
| accessibility | applicable | Run controls/status need accessible behavior. | SR75, SR76 | TK61, TK62, TK73 |
| operations_backup_retention_recovery | unknown | Retry and recovery behavior needs owner decisions. |  | TK72 |
| domain_provenance | applicable | Findings bind to selected data and evidence. | SR70 | TK51, TK52, TK55 |
### CUS08

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | Retention/access duties for saved assessments unassessed. |  | TK72 |
| engineering | applicable | History preserves lineage, reruns and evidence. | SR16, SR17, SR72 | TK56, TK57, TK58, TK59 |
| runtime | unknown | Durability, backup and retention goals undefined. |  | TK72 |
| architecture | applicable | Result contracts join source, execution and retrieval. | SR16, SR17, SR72 | TK56, TK57, TK58 |
| privacy_security | unknown | The applicable authorization duties for saved-history and evidence reads have not been established; bounded evidence/decision investigation is TK66 and TK72. |  | TK66, TK72 |
| accessibility | applicable | History states need accessible presentation. | SR75, SR76 | TK61, TK62, TK73 |
| operations_backup_retention_recovery | unknown | Backup/restore/retention ownership open. |  | TK72 |
| domain_provenance | applicable | Revisited results need snapshot, versions, date, evidence. | SR16, SR72 | TK56, TK58, TK59 |
### CUS09

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | Applicable API/data/accessibility duties unassessed. |  | TK63, TK72 |
| engineering | applicable | Dashboard/API values agree and mutations fail. | SR18, SR19, SR31 | TK60, TK61, TK62, TK63, TK64, TK65 |
| runtime | unknown | Availability/query/pagination bounds unresolved. |  | TK63, TK72 |
| architecture | applicable | Versioned resources and stable query semantics needed. | SR19, SR31 | TK63, TK64, TK65 |
| privacy_security | applicable | Retrieval scopes resources to current user. | SR19, SR31 | TK63, TK64, TK65 |
| accessibility | applicable | Results and errors need accessible display. | SR75, SR76 | TK61, TK62, TK73 |
| operations_backup_retention_recovery | unknown | Support, backup, restore duties open. |  | TK72 |
| domain_provenance | applicable | Displayed values trace to saved outputs and run lineage. | SR18, SR31 | TK60, TK61, TK56, TK58 |
### CUS10

| Perspective | Applicability | Rationale / open question | SR links | Investigation tasks |
| --- | --- | --- | --- | --- |
| legal | unknown | Jurisdictional privacy/credential/retention duties unassessed. |  | TK66, TK72 |
| engineering | applicable | Files, credentials, runs/results need per-user checks. | SR20, SR21, SR73 | TK66, TK67, TK69 |
| runtime | applicable | Checks span request, dispatch and changed sessions. | SR20, SR21, SR73 | TK66, TK67, TK68 |
| architecture | applicable | Identity spans storage, model, run and result paths. | SR20, SR21, SR73 | TK66, TK67, TK68 |
| privacy_security | applicable | Foreign data/secrets must not be disclosed or used. | SR20, SR21, SR73, SR74 | TK66, TK67, TK70, TK71 |
| accessibility | applicable | Identity-change, denial, and result states apply to the customer view; criteria and target remain proposals pending D04/D05. | SR71, SR75, SR76 | TK61, TK62, TK68, TK73 |
| operations_backup_retention_recovery | unknown | Identity lifecycle/logging/incident/recovery need review. |  | TK72 |
| domain_provenance | applicable | Results retain correct owner's source/run lineage. | SR21, SR73 | TK66, TK67, TK58, TK59 |

## Newly planned P0 verification cases

All cases below are Not run with empty evidence. The global candidate protocol in the validation plan applies; this table does not report product checks.

| ID | Title | Method | Procedure / expected outcome | Assigned task(s) | Status |
| --- | --- | --- | --- | --- | --- |
| TC21 | Accessible file disposition and rejection reason | Inspection and rendered UI test | For every approved accepted/rejected fixture, result identifies file, textual disposition and approved reason; outcome is not conveyed by color or icon alone. | TK11, TK12 | Not run |
| TC22 | History duplicate and conflict presentation | Inspection and rendered UI test | Repeated identical bytes do not appear as a second activity; approved conflicts identify affected records and remain unresolved without implying merge or overwrite. | TK15, TK16 | Not run |
| TC23 | Readiness scope and provenance presentation | Inspection and rendered UI test | Selected scope and source/calculated/quality value classes match prepared fixture provenance; absent optional value is unavailable/unknown, never zero or inferred. | TK21, TK22 | Not run |
| TC24 | FIT source and fixture provenance inspection | Inspection | Official protocol/profile references and proposed fixture sources have provenance and terms recorded; unresolved rights questions are explicit and no unsupported legal conclusion is made. | TK09, TK17 | Not run |
| TC25 | FIT decoder resource-bound evidence inspection | Inspection | Candidate decoder resource dimensions and bounds cite authoritative evidence or remain unresolved; no numeric threshold is invented. | TK10, TK13, TK20 | Not run |
| TC26 | Persistent data lifecycle policy inspection | Inspection | Retention, privacy, backup and recovery choices are cited or remain explicit gaps; no duration, legal duty, RPO or RTO is fabricated. | TK17 | Not run |
| TC27 | Preprocessing runtime and reproducibility inspection | Inspection | Resource variables and run configuration/version needed to interpret repeated preparation are documented; unapproved limits remain open. | TK20 | Not run |
| TC40 | Skill definition contract | Inspection and contract test | For each proposed skill fixture, inspect version, declared inputs, applicability, method, output schema and evaluation references; the contract checker accepts complete provider-independent definitions and rejects a missing mandatory declaration. | TK31, TK42, TK43 | Not run |
| TC41 | Skill evaluation evidence and release gate | Inspection and evaluation | Run the approved evaluation procedure on its declared fixtures and selected supported connection; record deterministic assertions, schema checks, substantive review results and unresolved threshold separately; no skill is labeled evaluated or releasable without the D02-approved gate. | TK32, TK42, TK43 | Not run |
| TC42 | Skill source provenance review | Inspection | Inspect each proposed baseline skill's source/evidence inventory; every included method claim has a reviewable provenance entry and unresolved source-rights questions are assigned for decision, with no rights conclusion inferred. | TK33, TK42, TK43 | Not run |
| TC43 | Eligibility repeatability | Test | Evaluate identical skill version, dataset snapshot and rule version twice; eligibility and unmet requirement codes match, and an unavailable mandatory input produces ineligible without an inference request. | TK34, TK44, TK45 | Not run |
| TC44 | Eligibility explanations | Test and inspection | For eligible and ineligible fixtures, compare displayed reasons with the machine unmet-requirements result; every blocking rule names its required input and observed gap, and reasons contain no other user's data. | TK44, TK45 | Not run |
| TC45 | Skill and eligibility accessibility states | Inspection and test | Inspect catalog, eligible/ineligible states and empty/error states with keyboard navigation and text output; each action has an accessible name and meaning is available without color alone; record unsupported assistive-technology assumptions. | TK35, TK44, TK45 | Not run |
| TC46 | Credential boundary and exposure | Inspection and test | Trace a test credential through connection setup and request construction; credential bytes are absent from skill definitions, execution envelopes, responses, logs and public evidence, while the documented protection boundary remains marked proposed pending D03. | TK36, TK46, TK47 | Not run |
| TC47 | Connection capability declaration | Contract test | Compare declared skill needs with supported connection capabilities; unsupported execution is blocked and the missing capability is explained before analysis begins. | TK37, TK40, TK46, TK47 | Not run |
| TC48 | Explicit model selection and no fallback | Deterministic mock/contract test; actual supported-customer-model integration remains separate release gate TC08 | Select connection/model A in the mock and capture the candidate request; it identifies A, and when A is unavailable the run is blocked/failed with a safe reason and no request reaches B or a Datara-owned analysis credential. This case does not establish real provider integration. | TK39, TK46, TK47 | Not run |
| TC49 | Model connection outcome handling | Deterministic mock/contract test; actual supported-customer-model integration remains separate release gate TC08 | Exercise mocked success, authentication, temporary, timeout and malformed-response cases; each is distinguishable as a declared model connection outcome, and credential values are excluded from user-visible errors. This case does not establish real provider integration. | TK38, TK46, TK47 | Not run |
| TC50 | Credential lifecycle and operational evidence | Inspection | Review credential protection, access paths, deletion and rotation questions against D03; unresolved lifecycle choices remain explicit, and outcome evidence examples contain no credential values. | TK41, TK46, TK47 | Not run |
| TC51 | Skill version retention and run binding | Contract test and inspection | Publish two distinct skill definition versions and create a run reference to the first; history resolves the run to the original immutable definition while retaining both versions and does not silently replace either. | TK31, TK42, TK43 | Not run |
| TC60 | Manual run lifecycle states | Test | On the approved fixed candidate, submit one controlled run for each configured valid, malformed, authentication-failure, timeout, and provider-error fixture. Record run ID, persisted status, visible status, and whether a finding exists. Compare each with the D03-approved outcome; a fake adapter validates only lifecycle handling, not live-model quality. Expected: Pending/success/auth-error/timeout/provider-error match approved states; only validated success is terminal success. | TK50, TK53, TK54 | Not run |
| TC61 | Invalid output rejection | Test | Submit one contract-conforming response, then responses with malformed structure, unsupported classification, wrong snapshot/skill version, and missing evidence. For each record validation result, run status, and whether any finding is exposed; use the approved D02/D03 contract as oracle. Expected: Valid output alone becomes assessment; malformed schema/classification/snapshot/version/evidence becomes non-success with no finding. | TK51, TK54, TK55 | Not run |
| TC62 | Run selection binding | Test | As one disposable user, choose a known scope/snapshot/skill/connection/model and submit a run. Compare the saved request and dispatched connection with the selection; repeat with unavailable selected access and confirm no alternate connection is called. Expected: Persisted request and dispatch equal explicit scope/snapshot/skill/connection/model; no alternative connection called. | TK52 | Not run |
| TC63 | Sanitized failure record | Test | Use unique sentinel credentials and provider-error payloads in controlled success/failure responses. Retrieve saved run status and result through supported views; record presence/absence and confirm the failure remains explicit. Expected: Unique secret/provider sentinels in failures do not appear in retrieved failure output. | TK53, TK70, TK71 | Not run |
| TC64 | Result lineage resolution | Test | Create one saved assessment from a known fixture. Retrieve its lineage fields and resolve each to the selected input, preprocessing version, skill/model, run time, and evidence supplied for that run; report any missing/mismatched reference. Expected: Snapshot/preprocessing/skill/model/time/evidence fields resolve to actual source and run. | TK56, TK57, TK59 | Not run |
| TC65 | Append-only rerun history | Test | Run the same selected snapshot twice with distinct controlled outcomes. Retrieve both records and compare IDs and the earlier record before/after rerun; the first record must remain unchanged and separately addressable. Expected: Two same-scope runs have distinct IDs and first record/lineage remain unchanged. | TK56, TK57, TK59 | Not run |
| TC66 | Evidence reference binding | Test | Create valid same-snapshot, broken, cross-snapshot, and foreign-user evidence references. As the result owner, open each finding and record which reference resolves; only valid same-snapshot authorized evidence may resolve. Expected: Only valid same-snapshot authorized evidence resolves; broken/cross-snapshot/foreign refs are unavailable. | TK58, TK59 | Not run |
| TC67 | History across restart | Test | Persist at least one successful and one failed result with lineage using disposable data. Restart the service using the recorded candidate/setup, retrieve both records, then rerun one scope and confirm prior records remain distinct. Expected: After restart prior result/lineage remains retrievable and rerun creates distinct record. | TK57, TK59 | Not run |
| TC68 | Dashboard without inference | Test | Disable inference/model access before loading each D04-approved saved dashboard view. Capture displayed record IDs and inference-request count; verify values load from saved records and request count remains zero. Expected: With inference disabled, approved saved views render and inference requests equal zero. | TK60, TK61, TK62 | Not run |
| TC69 | Dashboard states and provenance | Test | Using controlled saved records, render the D04-approved empty, populated, warning, failed, evidence-unavailable, and denied states. Capture visible text/semantic state and verify each distinction does not depend on color alone. Expected: Approved status states match saved contract and never rely on color alone. | TK60, TK61, TK62 | Not run |
| TC70 | Dashboard/API parity | Test | For a fixed authorized saved fixture, capture dashboard values and corresponding API values/identifiers, canonicalize only as the approved contract allows, and compare each field. Attempt approved read-only mutation probes and confirm persisted state is unchanged. Expected: Canonicalized dashboard saved values/IDs equal API; read-only attempts do not mutate. | TK62, TK63, TK64, TK65 | Not run |
| TC71 | Read-only output retrieval and mutation behavior | Test | Using the founder-approved read-only operations and output contract, retrieve owned saved output and attempt operations not allowed by that contract. Compare returned values with the saved result and compare persisted state before and after; operation, representation and error details are defined by D04. Expected: Authorized read-only retrieval returns only the intended saved values; disallowed mutation attempts leave persisted state unchanged and produce the D04-approved outcome. This case does not select the operation or representation. | TK63, TK64, TK65 | Not run |
| TC72 | API pagination/query errors | Test | With a fixed saved collection and approved pagination/query rules, fetch successive pages and repeat a cursor, then submit each approved invalid-query fixture. Check for omissions/duplicates and compare error responses with the approved contract; unresolved bounds remain blocked. Expected: Repeated cursors preserve ordering; invalid queries use stable errors. | TK63, TK64, TK65 | Not run |
| TC73 | Cross-user retrieval isolation | Test | Use two disposable accounts. Request direct and collection output owned by the other account using valid foreign IDs and cursors; record status/body and confirm neither foreign values nor a resource-existence signal is disclosed under approved D04 behavior. Expected: Foreign direct/collection IDs/cursors reveal no other-user data or existence. | TK64, TK65, TK66, TK67, TK69 | Not run |
| TC74 | Authorization boundaries | Test | Using two test identities, probe file access, credential operation, run submission/status, history, dashboard and result retrieval as owner and non-owner. Verify denial occurs before foreign data use/execution and record every boundary result. Expected: Owner access succeeds; foreign file/credential/run/result actions denied before protected use. | TK66, TK67, TK69 | Not run |
| TC75 | Identity switch delayed response | Test | Start a history/result request as user A and hold its response. Change the active identity to user B, release the response, and inspect rendered state/network result; user A values must not render for B. Expected: Prior-user values never render after identity changes during an outstanding request. | TK68, TK69 | Not run |
| TC76 | Credential/provider payload inspection | Inspection and test | Place unique sentinels in controlled success/failure payload fields. Inspect only saved run status/result, dashboard representation, and output API response. Record hits; do not inspect logs or claim SR13 verification. Expected: Unique sentinels are absent from saved run status/results, dashboard representations, and output API responses. This case does not inspect logs; existing SR13 governs log credential handling. | TK70, TK71 | Not run |
| TC77 | Operations/legal investigation | Inspection | Inspect the current brief, WP01 proposal, decision register, and authoritative evidence available to the reviewer for retention, backup, restoration, access and legal applicability. Report source limits and named unresolved decisions; do not infer law, time periods, or recovery targets. Expected: Evidence/decision owners recorded for retention/backup/restore and applicable law; no values/conclusions invented. | TK72 | Not run |
| TC78 | Rendered accessibility acceptance | Test and demonstration | After D04/D05 define the supported browser, viewport, assistive-technology setup and applicable target, complete the approved run/result/retrieval states with keyboard and semantic output. Record versions, fixture IDs, steps, focus/errors/status announcements and limitations; if setup/decision is absent, leave blocked. Expected: Approved browser/viewport/AT keyboard/semantic flows show focus, associated errors, non-color states and async announcements. | TK61, TK62, TK73 | Not run |
| TC79 | Integrated owned-scope procedure | Inspection | Independently inspect this fragment against the frozen schema and coverage rubric: IDs/ranges, reciprocal CUS-feature-SR links, WP/parent/task/leaf/TC links, dependencies, ownership, implementation plus verification coverage, decision readiness, and evidence status. Report exact rows/gaps. This is a traceability audit; TC15 athlete validation remains separate. Expected: CUS07–10 mapped to reproducible checks; missing evidence remains Not run/blocked. | TK74 | Not run |
| TC80 | Baseline skill shortlist completeness review | Inspection | Inspect included and excluded candidates for outcome, scope, origin, input needs, evidence, exclusion reason, and open D02 questions; mark present, missing or open. No skill approval or substantive evaluation is implied. | TK30 | Not run |

## Decision gates

| Decision | Current topic | State in this plan |
| --- | --- | --- |
| D01 | FIT source evidence, supported mappings/limits, conflict and fixture terms | Open; no protocol/source choices inferred |
| D02 | Baseline skills, eligibility/evaluation thresholds and release quality | Open; no shortlist or threshold approved |
| D03 | Customer model capability, credentials, lifecycle and outcome handling | Open; capability/source facts remain pending |
| D04 | Saved dashboard, output API, evidence, access and pagination outcomes | Open; founder scope and representation decisions pending |
| D05 | Accessibility applicability/targets, platform and deployment choices | Open; no standard or topology selected |

## Authoritative status and P1 boundary

The GitHub Project is the shared central backlog and status record. P0 CUS, Feature, SR, Task, and STK items are published with their content, priority, dependencies, owner role, and readiness before execution; each issue/project-item link and read-back field snapshot is mirrored in the registry and mapping. This local breakdown is a content/traceability mirror, not a competing status board.

CUS11–CUS13, SR22–SR26, and TK08 remain unchanged P1 records. P0 requirement planning completion, product implementation, verification, athlete acceptance, and release are separate milestones.
