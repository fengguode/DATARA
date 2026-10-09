# WP03 baseline elemental skill shortlist (proposal)

**Work package:** WP03 — Specify baseline skills and eligibility pipeline  
**Traceability:** CUS04, FEAT04, SR08, SR50; D02; TC80  
**Assignments:** TK30 #129 and STK100 #201  
**State:** Source-only discovery proposal for review. This document records a shortlist and explicit evidence gaps. It does not freeze skill schemas, approve product implementation, establish evaluation results, or mark a skill evaluated or released.

## Decision boundary

The current D02 baseline selects three P0 library targets: activity-summary, training-volume-trend, and training-consistency. This is the selected target direction; it does not mean that the candidates have passed quality evaluation or are ready for release.

Eligibility and numeric calculation belong to deterministic conventional software before any model request. A customer chooses the model connection. Skills remain provider-independent. Findings must describe the selected records and disclose their limits. No P0 recommendation, medical, injury-risk, physiological, causal, or prescription claim is in scope.

## Candidate shortlist

| Candidate | Intended athlete outcome | In scope | Exclusions and limitations | Origin and proposed inputs | D02 direction and evidence gaps |
|---|---|---|---|---|---|
| activity-summary | Understand which training is recorded in a selected period. | Count accepted, nonconflicting activities and total elapsed duration by sport. Report distance only for records with valid distance and disclose distance coverage. Every value must resolve to activity evidence. | No imputed distance and no claim that uploaded records are a complete training history. No recommendations or health claims. | Selected Datara-created, provider-independent baseline candidate. Proposed fields include the selected UTC scope and accepted activities with sport, start time, elapsed duration, and optional valid distance. Exact envelope/schema and source mapping are open. | D02 requires at least one accepted activity. Exact input/output schema, method-source citations, rights review, fixture manifest/oracles, and substantive per-connection evidence are not supplied by this shortlist. |
| training-volume-trend | Understand how recorded training duration changes across a selected period. | Compare elapsed-duration totals for the earlier two and later two of the last four complete UTC calendar weeks wholly inside scope. Report the absolute difference, percent when the earlier total is positive, and increased/decreased/equal from the difference sign. | Empty weeks contribute zero recorded duration and require a missing-records limitation; this does not prove no training occurred. No causal, medical, injury, or performance conclusion. | Selected Datara-created, provider-independent baseline candidate. Proposed fields include a selected scope and accepted activities with the summary fields; exact contract/schema is open. | D02 requires a scope of at least 28 days, four complete weeks wholly inside it, and accepted activity in at least three of those weeks. Zero earlier duration makes the percentage unavailable. Older WP01 wording includes a “stable” threshold; reconcile that proposal with the later D02 sign-based increased/decreased/equal direction before freezing a contract. No threshold is invented here. |
| training-consistency | Understand the distribution of recorded active days and recorded gaps in a selected period. | Count UTC active days and longest consecutive runs of recorded-active days and days with no recorded activity within scope, including leading/trailing gaps. An active day has at least one included activity starting on that UTC date; count each date once. | A date without an uploaded activity is not proof that training did not happen. UTC days may differ from the athlete's local calendar. No adherence, fitness, recovery, or health conclusion. | Selected Datara-created, provider-independent baseline candidate. Proposed fields include a selected scope and accepted activities with start times; exact contract/schema is open. | D02 requires at least 28 complete UTC days and an accepted activity; a scope with none is ineligible. Boundary, streak, and no-record fixtures and independent oracles remain to be frozen. |

## Provenance and exclusions

The founding record describes books and videos as possible sources for Datara-authored baseline expertise and separately requires source traceability. The inspected records do not identify a method source passage for any of these three candidates, a permissioned source, or an approved fixture. Therefore per-method source citations, source-rights evidence, and fixture provenance are **missing/open**; this proposal makes no rights or legal conclusion.

Medical or diagnostic expertise; recovery, nutrition, and advice; load-change interpretation; recovery trends; missing-information analysis as a standalone skill; and conversion of findings into suggested actions are not added to this shortlist. The founding record presents several as examples, not as the selected P0 set. Automated source-to-skill creation and commercial expert-IP mechanisms remain deferred.

## D02 evaluation gates and unresolved contract work

The D02 baseline records a proposed/selected evaluation structure: at least ten distinct cases per skill, with relevant positive, insufficient-input, optional-missing, conflict-exclusion, UTC-boundary, and arithmetic/zero-baseline cases; at least three independent attempts per case for each released provider/model pair; and distinct evidence for deterministic metrics, schema/contract validation, mocked adapter behavior, and substantive live-connection quality. The substantive rubric describes five dimensions scored 0/1/2, with an initial 8/10 minimum and no zero dimension. Its anchors and approval/freeze status remain an independent-review gate; no quality run is evidenced here.

Before implementation or release contracts are frozen, the project still needs:
- common and per-skill input/output schemas, classifications, abstention behavior, and evidence-reference rules;
- reconciliation of the older WP01 “stable” threshold proposal with D02's sign-based trend direction;
- permissioned fixture manifests and independently calculated expected values;
- independently reviewed rubric anchors and confirmation of the applicable minimum threshold;
- substantive evidence for every supported provider/model connection.

This shortlist does not itself authorize or perform those activities. Deterministic correctness, schema checks, mocked behavior, and live-connection quality remain separate evidence categories.

## TC80 completeness inspection

| Required review field | Status in this proposal |
|---|---|
| Candidate and intended outcome | Present for all three selected candidates. |
| Scope and exclusions | Present; claims are limited to recorded data and descriptive outputs. |
| Origin and method source | Selected Datara-created direction is identified; per-method source passage and rights evidence are missing/open. |
| Input needs | Proposed fields and D02 eligibility direction are present; frozen schemas and source mappings remain open. |
| Evidence | Current D02, WP01, CUS/SR, and TC records are linked below; no product test result is claimed. |
| Exclusion rationale | Present for selected candidates and examples outside the shortlist. |
| Unresolved decisions/gates | Present: schema, trend wording, fixture/provenance, rubric, and live evaluation. |
| Evaluated or released claim | None. TC80 is an artifact inspection, not product verification. |

## Evidence references

All repository citations below point to the reviewed source snapshot at [e59294d](https://github.com/fengguode/DATARA/tree/e59294d80218b7701051a9cba2d26413754a728a).

- [D02 decision register](https://github.com/fengguode/DATARA/blob/e59294d80218b7701051a9cba2d26413754a728a/docs/management/decision-register.md) and [P0 decision baseline](https://github.com/fengguode/DATARA/blob/e59294d80218b7701051a9cba2d26413754a728a/docs/management/p0-decision-baseline-2026-10-01.md): record the selected three-skill target, UTC metric direction, and remaining evidence gates.
- [WP01 proposed baseline](https://github.com/fengguode/DATARA/blob/e59294d80218b7701051a9cba2d26413754a728a/docs/management/wp01-requirements-package.md): supplies an earlier candidate and threshold proposal; its “stable” trend wording needs reconciliation with D02.
- [CUS04 / FEAT04](https://github.com/fengguode/DATARA/blob/e59294d80218b7701051a9cba2d26413754a728a/docs/management/product-requirements.md): establishes the user outcome and library requirement; it does not establish an evaluated skill.
- [SR08 / SR50 and evaluation/provenance obligations](https://github.com/fengguode/DATARA/blob/e59294d80218b7701051a9cba2d26413754a728a/docs/management/system-requirements.md): require declared skill versions, inputs, applicability, method, output contract and evaluation cases, with retained versions.
- [TC80](https://github.com/fengguode/DATARA/blob/e59294d80218b7701051a9cba2d26413754a728a/docs/management/requirements-registry.json): defines the planned shortlist-completeness inspection; it is not passing product evidence.
- [Founding brainstorming record](https://github.com/fengguode/DATARA/blob/e59294d80218b7701051a9cba2d26413754a728a/docs/brainstorming-record-2026-09-30.md): preserves the distinction between illustrative ideas, selected baseline direction, and deferred source-to-skill/commercial work.
- [TK30 #129](https://github.com/fengguode/DATARA/issues/129) and [STK100 #201](https://github.com/fengguode/DATARA/issues/201): track this source-only proposal and candidate inventory.

## Execution record and limitations

This proposal is based on repository documents at the source snapshot above and issue descriptions for TK30/STK100. It is a document-only W0 deliverable. No product code, imports, tests, database actions, provider calls, athlete data, or runtime verification were used. The project execution agent requested gpt-6-luna with high reasoning; effective model/backend loading is not independently observable.
