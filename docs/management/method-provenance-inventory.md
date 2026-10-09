# TK33 candidate-method provenance and eligibility inventory

**State:** Source-only evidence inventory and owner decision request. It does not freeze a skill schema, authorize implementation, evaluate a skill, establish source permission, or make a legal conclusion.

**Traceability:** WP03; TK33 issue #132; STK106 issue #204; CUS04 #62; CUS05 #63; FEAT30 #41; FEAT05 #42; SR52 #100; TC42. Project 3 showed TK33 In progress, P0, order 900, no plan prerequisite, Agent System Architect — Feng Guo at the time inspected. The Project Agent value records ownership and does not establish an active runtime. The issue records Yi Tang as coordinator and Feng Guo as planned requirements owner.

**Source snapshot inspected:** DATARA main commit `b7b65182f84e6a60006468c278dfb1b74a7b79af`, verified from the GitHub main commit history on 2026-10-10. This inventory describes that snapshot; recheck source links before a later contract or implementation is frozen.

## Decision boundary

CUS04 asks for a small evaluated Datara-created library with explicit inputs, methods, outputs, and versions. CUS05 excludes skills whose required inputs are unavailable and asks that missing requirements be explained. SR52 separately requires source provenance for each proposed skill-method claim and requires unresolved source-rights questions to remain open without implying a legal conclusion.

The D02 baseline selects activity-summary, training-volume-trend, and training-consistency, and defines their deterministic calculations. The current shortlist calls each a selected Datara-created, provider-independent baseline candidate. The founding record says source passages or video timestamps should support traceability and says third-party use requires separate source-rights decisions. The records inspected do not identify a per-method external source passage, permissioned source, or approved fixture for any of the three candidates. That is an evidence gap in this snapshot, not proof that no such source exists elsewhere.

## Candidate source-to-method map

| Candidate and proposed method claim | Resolvable internal origin reference | External method source located in inspected records | Attribution, rights, and fixture evidence |
|---|---|---|---|
| activity-summary — count accepted, nonconflicting activities and total elapsed duration by sport; report distance only for valid-distance records and disclose coverage | [D02 selected baseline](https://github.com/fengguode/DATARA/blob/b7b65182f84e6a60006468c278dfb1b74a7b79af/docs/management/p0-decision-baseline-2026-10-01.md); [candidate shortlist](https://github.com/fengguode/DATARA/blob/b7b65182f84e6a60006468c278dfb1b74a7b79af/docs/management/skill-shortlist-proposal.md) | None identified for this claim in the inspected records. The shortlist describes the candidate as a Datara-created baseline; that is an internal origin statement, not an external citation. | No external method passage, source attribution, permission evidence, or approved fixture reference is recorded per method. Status open; no permission or clearance is inferred. |
| training-volume-trend — compare elapsed-duration totals for the earlier two and later two of the last four complete UTC weeks within scope; expose difference, percentage only with a positive earlier total, and the selected direction | [D02 selected baseline](https://github.com/fengguode/DATARA/blob/b7b65182f84e6a60006468c278dfb1b74a7b79af/docs/management/p0-decision-baseline-2026-10-01.md); [candidate shortlist](https://github.com/fengguode/DATARA/blob/b7b65182f84e6a60006468c278dfb1b74a7b79af/docs/management/skill-shortlist-proposal.md) | None identified for this claim in the inspected records. The shortlist describes the candidate as a Datara-created baseline; that is an internal origin statement, not an external citation. | No external method passage, source attribution, permission evidence, or approved fixture reference is recorded per method. Status open; no permission or clearance is inferred. |
| training-consistency — count recorded active UTC days and longest consecutive recorded-active and no-record streaks; only complete UTC days wholly inside the selected period count for consistency under the approved option A | [D02 selected baseline](https://github.com/fengguode/DATARA/blob/b7b65182f84e6a60006468c278dfb1b74a7b79af/docs/management/p0-decision-baseline-2026-10-01.md); [candidate shortlist](https://github.com/fengguode/DATARA/blob/b7b65182f84e6a60006468c278dfb1b74a7b79af/docs/management/skill-shortlist-proposal.md); [founder selection of option A](https://github.com/fengguode/DATARA/discussions/366#discussioncomment-18737403) | None identified for this claim in the inspected records. The shortlist describes the candidate as a Datara-created baseline; that is an internal origin statement, not an external citation. | No external method passage, source attribution, permission evidence, or approved fixture reference is recorded per method. Status open; no permission or clearance is inferred. |

### Source record references

- [Founding brainstorming record](https://github.com/fengguode/DATARA/blob/b7b65182f84e6a60006468c278dfb1b74a7b79af/docs/brainstorming-record-2026-09-30.md): materials may seed knowledge and skills; method passages or video timestamps should support traceability; third-party use requires separate source-rights decisions.
- [CUS04](https://github.com/fengguode/DATARA/issues/62) and [CUS05](https://github.com/fengguode/DATARA/issues/63): Datara-created evaluated library and deterministic unavailable-input explanations.
- [SR52](https://github.com/fengguode/DATARA/issues/100): per-claim source provenance and unresolved rights questions without legal conclusions.
- [D07](https://github.com/fengguode/DATARA/blob/b7b65182f84e6a60006468c278dfb1b74a7b79af/docs/management/decision-register.md): source rights and source-to-skill workflow are deferred; this does not answer whether provenance changes the eligibility rule for these candidates.

## Founder decision needed

Does source provenance affect proposed eligibility use for the three selected D02 candidates?

- **A.** Keep eligibility tied to the existing deterministic D02 inputs and rules for these Datara-created baseline calculations; require provenance metadata, and do not use any materially third-party-derived method claim unless its source and rights are resolved.
- **B.** Treat unresolved method provenance or rights as an eligibility blocker for every candidate, including these Datara-created baseline calculations, until the evidence is resolved.
- **C.** Specify a different boundary.

**Recommendation:** A, because CUS04 and the current shortlist identify the three candidates as Datara-created deterministic baselines, while SR52 still requires provenance records and the founding record separately requires source-rights decisions for third-party material. This is a recommendation only; it does not select an option or change eligibility.

Until the founder decides, this inventory does not encode either rule. Applicability remains unknown; no eligibility implementation or public claim should be derived from this open question. No legal conclusion, source permission, skill evaluation, product verification, acceptance, or release is claimed.

## Evidence and limitations

The internal D02/shortlist references resolve to the inspected main snapshot and link each proposed method claim to its recorded origin. No per-method external method source or permission record was found in the inspected sources. Absence from those records is not evidence that a source does not exist. TC42 remains the planned verification oracle; this document is source evidence for review, not a passing TC42 execution.

**Contribution:** Primary Coordinator — Yi Tang_model-unconfirmed-variant-unconfirmed_Codex (AI agent)  
**Model used:** model=model-unconfirmed variant=variant-unconfirmed harness=Codex  
**Configuration loading:** Project defaults are set to gpt-6-luna/high; this session cannot independently verify that the existing runtime loaded those defaults.
