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
| training-consistency | Understand the distribution of recorded active days and recorded gaps in a selected period. | Count UTC active days and longest consecutive runs of recorded-active days and days with no recorded activity within scope, including leading/trailing gaps. An active day has at least one included activity starting on that UTC date; count each date once. Option A uses only complete UTC days wholly inside the selected period for day counts and streaks. Edge partial-day activities remain in the period summary and may satisfy activity-presence eligibility, but do not count toward consistency days or the 28-complete-day minimum; disclose selected and effective boundaries. | A date without an uploaded activity is not proof that training did not happen. UTC days may differ from the athlete's local calendar. No adherence, fitness, recovery, or health conclusion. | Selected Datara-created, provider-independent baseline candidate. Proposed fields include a selected scope and accepted activities with start times; exact contract/schema is open. | D02 requires at least 28 complete UTC days and an accepted activity; a scope with none is ineligible. The edge partial-day rule is founder-approved option A ([decision #366](https://github.com/fengguode/DATARA/discussions/366#discussioncomment-18737403)); boundary, streak, and no-record fixtures and independent oracles remain open. |

## Provenance and exclusions

The founding record describes books and videos as possible sources for Datara-authored baseline expertise and separately requires source traceability. The inspected records do not identify a method source passage for any of these three candidates, a permissioned source, or an approved fixture. Therefore per-method source citations, source-rights evidence, and fixture provenance are **missing/open**; this proposal makes no rights or legal conclusion.

Medical or diagnostic expertise; recovery, nutrition, and advice; load-change interpretation; recovery trends; missing-information analysis as a standalone skill; and conversion of findings into suggested actions are not added to this shortlist. The founding record presents several as examples, not as the selected P0 set. Automated source-to-skill creation and commercial expert-IP mechanisms remain deferred.

## Excluded illustrative candidates — required fields recorded as open

These examples remain unselected ideas from the founding record, not proposed P0 skills. The table records TC80's required fields without inventing outcomes, inputs, evidence, or D02 selections.

| Excluded idea | Intended outcome | Scope / excluded behavior | Origin / method source | Input needs | Available evidence | Exclusion reason and unresolved D02 item |
|---|---|---|---|---|---|---|
| Medical diagnosis or advice | Open — no approved user outcome or method defined. | Excluded from the selected descriptive P0 skills; no diagnosis or treatment recommendation. | Founding brainstorming example only; no method source. | Missing/open — none specified. | Brainstorming mention only; no method, fixture, or evaluation evidence. | Not selected by D02; medical scope is unsupported here. No D02 decision to publish it. |
| Recovery advice or trend | Open — no approved user outcome or method defined. | Excluded as a standalone P0 skill; no recovery assessment or prescription. | Founding brainstorming example only; no method source. | Missing/open — none specified. | Brainstorming mention only; no method, fixture, or evaluation evidence. | Not among the three selected D02 skills. A future candidate needs separate scope and evidence review. |
| Nutrition advice | Open — no approved user outcome or method defined. | Excluded from the selected P0 shortlist; no nutrition assessment or prescription. | Founding brainstorming example only; no method source. | Missing/open — none specified. | Brainstorming mention only; no method, fixture, or evaluation evidence. | Not among the three selected D02 skills. A future candidate needs separate scope and evidence review. |
| Load-change interpretation | Open — the example does not define an athlete outcome or method. | Not included in the selected P0 skill set. | Founding brainstorming example only; no method source. | Missing/open — none specified. | Brainstorming mention only; no operational or evaluation evidence. | D02 selected three other targets. No selection or threshold decision for this example. |
| Missing-information check as a standalone skill | Open — no standalone outcome or method defined. | Missing-data limitations may be disclosed by a selected skill; this example is not a separate selected skill. | Founding brainstorming example only; no method source. | Missing/open — none specified. | Brainstorming mention only; no standalone method or evaluation evidence. | Not among the three selected D02 skills. A future standalone candidate needs separate scope and evidence. |
| Converting assessments into suggested actions | Open — no approved action outcome or method defined. | Not in the selected descriptive P0 library; recommendations are outside this D02 shortlist. | Founding brainstorming example only; no method source. | Missing/open — none specified. | Brainstorming mention only; no method, fixture, or evaluation evidence. | Not among the three selected D02 skills. Any future recommendation capability needs separate scope and approval. |

Automated source-to-skill creation and commercial expert-IP mechanisms are deferred project capabilities, not candidate skills in this shortlist.

## D02 evaluation gates and unresolved contract work

The D02 baseline records a proposed/selected evaluation structure: at least ten distinct cases per skill, with relevant positive, insufficient-input, optional-missing, conflict-exclusion, UTC-boundary, and arithmetic/zero-baseline cases; at least three independent attempts per case for each released provider/model pair; and distinct evidence for deterministic metrics, schema/contract validation, mocked adapter behavior, and substantive live-connection quality. The substantive rubric describes five dimensions scored 0/1/2; the D02 baseline selects an initial minimum of 8/10 with no zero dimension. Independent review/freeze of the rubric anchors remains a gate, and no quality run is evidenced here.

Before implementation or release contracts are frozen, the project still needs:
- common and per-skill input/output schemas, classifications, abstention behavior, and evidence-reference rules;
- reconciliation of the older WP01 “stable” threshold proposal with D02's sign-based trend direction;
- permissioned fixture manifests and independently calculated expected values;
- independent review and freeze of rubric anchors; the D02 baseline's initial minimum of 8/10 with no zero dimension is selected;
- substantive evidence for every supported provider/model connection.

This shortlist does not itself authorize or perform those activities. Deterministic correctness, schema checks, mocked behavior, and live-connection quality remain separate evidence categories.

## TC80 completeness inspection

TC80 passed as a requirements-artifact inspection on the candidate content recorded in [the TC80 evidence note](../team/reviews/tc80-shortlist-inspection-2026-10-10.md). The inspection distinguishes current D02 selections from unresolved details: the three P0 skills, their deterministic metric and eligibility direction, the initial 8/10/no-zero substantive criterion, and consistency option A for complete UTC-day counts and streaks are selected; schemas, method sources and rights, fixtures, rubric-anchor review, and per-connection substantive evidence remain open. The proposal labels those states accurately and does not describe a candidate as evaluated or released. This is proposal-completeness evidence only, not product verification, contract approval, or founder acceptance.

| Required review field | Status in this proposal |
|---|---|
| Candidate and intended outcome | Present for all three selected candidates. |
| Scope and exclusions | Present; claims are limited to recorded data and descriptive outputs. |
| Origin and method source | Selected Datara-created direction is identified; per-method source passage and rights evidence are missing/open. |
| Input needs | Proposed fields and D02 eligibility direction are present; frozen schemas and source mappings remain open. |
| Evidence | Current D02, WP01, CUS/SR, and TC records are linked below; no product test result is claimed. |
| Exclusion rationale | Present for the selected candidates; excluded-example rows record intended outcome, scope, origin, inputs, evidence, rationale, and D02 status, marking undefined fields open/missing. |
| D02 selections and unresolved details | Present and distinguished: the three-skill direction, per-skill deterministic metric/eligibility direction, initial 8/10/no-zero score rule, and consistency option A are selected; schemas, older WP01 “stable” reconciliation, method sources/rights, fixture oracles, rubric-anchor review, and per-connection live evaluation remain open. |
| Evaluated or released claim | None. TC80 is an artifact inspection, not product verification. |

## Evidence references

All repository citations below point to the reviewed source snapshot at [646404f](https://github.com/fengguode/DATARA/tree/646404fa1d8bd61dbd883c367e55983b84b48faa).

- [D02 decision register](https://github.com/fengguode/DATARA/blob/646404fa1d8bd61dbd883c367e55983b84b48faa/docs/management/decision-register.md) and [P0 decision baseline](https://github.com/fengguode/DATARA/blob/646404fa1d8bd61dbd883c367e55983b84b48faa/docs/management/p0-decision-baseline-2026-10-01.md): record the selected three-skill target, UTC metric direction, and remaining evidence gates.
- [WP01 proposed baseline](https://github.com/fengguode/DATARA/blob/646404fa1d8bd61dbd883c367e55983b84b48faa/docs/management/wp01-requirements-package.md): supplies an earlier candidate and threshold proposal; its “stable” trend wording needs reconciliation with D02.
- [CUS04 / FEAT04](https://github.com/fengguode/DATARA/blob/646404fa1d8bd61dbd883c367e55983b84b48faa/docs/management/product-requirements.md): establishes the user outcome and library requirement; it does not establish an evaluated skill.
- [SR08 / SR50 and evaluation/provenance obligations](https://github.com/fengguode/DATARA/blob/646404fa1d8bd61dbd883c367e55983b84b48faa/docs/management/system-requirements.md): require declared skill versions, inputs, applicability, method, output contract and evaluation cases, with retained versions.
- [TC80](https://github.com/fengguode/DATARA/blob/646404fa1d8bd61dbd883c367e55983b84b48faa/docs/management/requirements-registry.json): defines a shortlist-completeness artifact inspection whose evidence is recorded in the TC80 review note. Passing the inspection does not verify product behavior.
- [Founding brainstorming record](https://github.com/fengguode/DATARA/blob/646404fa1d8bd61dbd883c367e55983b84b48faa/docs/brainstorming-record-2026-09-30.md): preserves the distinction between illustrative ideas, selected baseline direction, and deferred source-to-skill/commercial work.
- [TK30 #129](https://github.com/fengguode/DATARA/issues/129) and [STK100 #201](https://github.com/fengguode/DATARA/issues/201): track this source-only proposal and candidate inventory.

## Execution record and limitations

This proposal is based on repository documents at the source snapshot above and issue descriptions for TK30/STK100. It is a document-only W0 deliverable. No product code, imports, tests, database actions, provider calls, athlete data, or runtime verification were used. The project execution agent requested gpt-6-luna with high reasoning; effective model/backend loading is not independently observable.
