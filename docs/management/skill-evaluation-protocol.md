# P0 skill evaluation protocol — TK32 / STK104 proposal

**Status:** Requirements proposal for independent review. This document defines evidence boundaries and a proposed procedure; it does not approve a schema, fixture set, rubric anchors, provider capability, release threshold beyond the selections already recorded in D02, or any skill as evaluated or released.

**Traceability:** WP03 W0 contract preparation; TK32 / STK104; CUS04; FEAT04; SR08, SR09, SR29, SR50, SR51; D02; TC41. The GitHub Project is authoritative for live task status. At the 2026-10-10 readback, Project 3 showed TK32 #131 as P0 / In progress / Requirements; the issue body still contains older Backlog wording. WP03 product implementation remains gated by WP01 and WP02.

## Purpose and rule

Keep four kinds of evidence distinct. Passing a weaker layer never substitutes for a stronger one. In particular, deterministic checks, schema validation, and mocked adapter checks do not establish that a supported model connection produces useful, faithful skill assessments.

This protocol applies separately to each immutable skill version and, for substantive evidence, to each selected supported provider/model combination. A result applies only to the exact candidate, skill, fixtures, schemas, procedure, and connection configuration recorded with that result. It does not transfer to another version or model alias.

## Evidence layers

| Layer | Question | Required evidence | What the layer does not establish |
| --- | --- | --- | --- |
| 1. Deterministic inputs and metrics | Did conventional software select the declared snapshot, apply eligibility, calculate metrics, and attach resolvable source evidence as specified? | Candidate commit; skill and rule versions; snapshot/fixture identity; expected values and oracle provenance; eligibility outcome and reason codes; exact metric comparison; evidence-reference resolution; boundary, missing-input, conflict-exclusion, and repeatability results. | Natural-language quality, provider behavior, or model assessment quality. No model call belongs in this layer. |
| 2. Contract and schema conformance | Does the frozen provider-independent skill input/output contract accept valid examples and reject invalid, incomplete, mismatched, or prohibited examples? | Approved schema and version identifiers; positive and negative fixture results; required-field, type, classification, evidence-reference, scope, and prohibited-claim checks; skill/model/snapshot binding where declared. | Runtime compatibility with a real provider or substantive quality. A schema-valid response may still be unfaithful or unhelpful. |
| 3. Mocked adapter interaction | Does application routing form and handle the expected adapter exchange using a controlled mock? | Mock definition/version; selected-connection routing assertion; request/response mapping; timeout, refusal, truncation, invalid-response, and safe-error cases as applicable; explicit evidence that no external provider was called. | Provider API compatibility, model capability, or substantive model quality. Mock results must never be counted as substantive attempts. |
| 4. Substantive assessment | On the exact approved fixtures and supported live connection, does the selected model return an acceptable evidence-bound descriptive assessment? | Frozen fixture set, expected deterministic facts, approved schema and rubric anchors; exact candidate/skill/provider/model/adapter versions; independent attempts; per-attempt deterministic, evidence, limitation, schema/version, prohibited-claim, and substantive-rubric results; reviewer disposition and unresolved issues. | Quality for another skill version, provider, model, fixture set, or untested capability. Results do not imply broad statistical guarantees. |

An absent layer is `Not run` or `Blocked` with its cause recorded; it is never inferred from another layer. Preserve failures and rejected outputs as evidence. Do not change fixtures, expected values, or rubric anchors to make a failed output pass; make a reviewed versioned change and rerun against the recorded candidate.

## D02 criteria carried forward

The following are selected in the dated D02 baseline and are carried forward without alteration:

- The P0 skill candidates are `activity-summary`, `training-volume-trend`, and `training-consistency`.
- Numerical metrics and eligibility are computed by conventional software. The model produces constrained descriptive findings and limitations tied to prepared evidence; P0 recommendations and medical, injury-risk, physiological-significance, or prescription claims are prohibited.
- The initial suite contains at least ten distinct cases per skill, including positive, insufficient-input, missing-optional-input, conflict-exclusion, UTC-boundary, and arithmetic/zero-baseline cases where applicable.
- For every provider/model pair selected for release, evaluate each applicable skill on its frozen suite with at least three independent attempts per case.
- Each accepted output must pass numerical-accuracy, resolvable-evidence, limitation-disclosure, schema/version-binding, and prohibited-claim checks. Five substantive dimensions are selected: faithful interpretation, clarity, relevance, limitation explanation, and useful organization. Each is scored 0–2; every accepted case must score at least 8/10 with no zero dimension.

These are initial criteria, not observed results or a statistical performance guarantee. Independent reviewers must freeze and approve the observable rubric anchors and expected examples before substantive evaluation. **The anchors remain an unmet D02 decision/evidence gate.** This proposal does not define those anchors by implication. Fixture provenance/oracles, frozen schemas and method/source references, rights disposition, exact supported model capability, and live per-connection evidence also remain separate prerequisites or evidence gaps.

## Proposed run and disposition procedure

1. Identify one exact candidate commit, immutable skill ID/version, applicable method/source reference, deterministic rule version, approved input/output schema versions, and the exact fixture-manifest revision. Record the source and expected-value authority for every fixture; rights and publication status must be explicit.
2. Run and record Layer 1 without a provider call. Confirm eligibility before inference, deterministic expected values, UTC/scope rules, snapshot binding, and evidence-reference resolution. An ineligible fixture stays ineligible with its reason and makes no inference request.
3. Run Layer 2 against the approved schema using valid and invalid fixtures. Record the exact validator/schema version and each assertion. Keep a schema failure distinct from a deterministic metric defect and a model-quality result.
4. Run Layer 3 with controlled mocks only. Record mock identity and prove no network/provider call occurred. A mock pass may support adapter logic only; it contributes zero Layer 4 attempts.
5. Start Layer 4 only after fixture/oracle, schema, model capability, supported connection, and independently reviewed rubric anchors are frozen and the live evaluation is separately authorized. Execute the selected minimum cases and independent attempts for each skill/model pair; record every attempt, including failures, refusals, and blocked attempts. Do not silently retry or replace a model.
6. For each attempt, first assess the objective checks in the D02 criteria. Score the five substantive dimensions against the frozen anchors and record accepted/rejected disposition with reviewer rationale. A case is accepted only when every mandatory objective check passes, its total is at least 8/10, and no dimension is zero. A failed case remains visible and does not count as accepted.
7. Report results per candidate, skill version, and provider/model pair. Keep counts of planned, attempted, accepted, rejected, and blocked cases separate. A combination is not represented as evaluated/releasable unless its complete applicable evidence meets the approved D02 gate; a result for one combination does not authorize another.

This is a proposed procedure for review. It is not authority to call a provider, spend funds, use credentials, publish real athlete data, or claim TC41 passed. Existing TC41 remains `Not run; evidence empty` until the approved procedure is actually executed on its declared fixtures and selected supported connection.

## Candidate-specific evidence record

For any future run, record at least:

| Field | Record |
| --- | --- |
| Candidate | Repository and exact commit SHA |
| Skill | Stable skill ID and immutable version |
| Inputs | Snapshot/fixture-manifest ID, fixture IDs, deterministic rule version |
| Contract | Input/output schema IDs and versions; validator version |
| Connection | Provider, exact requested/returned model identifiers, adapter version, and capability-matrix revision; never keys or secret references |
| Procedure | Approved protocol/rubric revision and reviewer identities/roles |
| Per-layer evidence | Layer, case/attempt ID, command or method, expected/actual result, status, evidence link, and defect or blocked reason |
| Disposition | Accepted/rejected and rationale for each attempt; aggregate counts by layer and skill/model combination |
| Limitations | Unsupported cases, unresolved thresholds/anchors, fixture/right gaps, and scope not established by this run |

Do not place credentials, private connection details, personal FIT telemetry, raw customer payloads, or sensitive provider responses in this public repository. Publish only approved synthetic or sanitized evidence; retain any sensitive run material only in its authorized protected location and link it using the project's approved evidence-reference process.

## References and limits

- [D02 selected baseline](p0-decision-baseline-2026-10-01.md#d02--elemental-skills-and-evaluation)
- [Decision register and accepted Milestone A risks](decision-register.md)
- [WP01 requirements baseline](wp01-requirements-package.md)
- [CUS/SR registry](requirements-registry.json), especially CUS04, SR08, SR09, SR29, SR50 and SR51
- [TC41 and release gate](validation-plan.md#release-gate); TC41 is currently `Not run`
- GitHub task records: [TK32 #131](https://github.com/fengguode/DATARA/issues/131) and [STK104 #203](https://github.com/fengguode/DATARA/issues/203)

This requirements artifact does not complete WP03, close TK32/STK104, approve remaining D02 details, satisfy TC41, verify product behavior, or constitute founder acceptance or release approval.