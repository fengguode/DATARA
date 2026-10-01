# Roadmap and progress update

**Status:** customer-facing draft for review; not externally published.
**As of:** 1 October 2026. Planning baseline: main commit ca689afccb9a6887e789b2975bd953e396b03eae, merged pull request #278. Live task status: the [DATARA GitHub Project](https://github.com/users/fengguode/projects/3). The board may require access; no stale task counts are repeated here.

## Roadmap at a glance

Dates are omitted because the project has no approved calendar commitments.

| Stage | Intended outcome | Dependency or gate | Current state |
| --- | --- | --- | --- |
| Foundation | Vision, user outcomes, requirements and delivery sequence | Approved requirements and traceability | Planning baseline recorded; product choices remain open |
| Validated data home | Supported imports, persistent history, deterministic preparation and user isolation | Approved file/data and security rules; lawful controlled fixtures | Not implemented; first coding waits for approved contracts and setup evidence |
| Manual analysis | Eligible baseline analyses, customer-selected model, manual runs and explicit failures | Data home; approved analysis and model-access rules | Not implemented; dependent |
| Saved outputs | Result lineage/history, dashboard and read-only API | Data and analysis stages; approved result/dashboard/API definitions | Not implemented; dependent |
| P0 validation | Candidate checks and complete athlete workflow | P0 evidence, live model checks where required, founder acceptance, separate release decision | Not run |
| P1 recommendations and routines | User-approved recommendations, recurring runs and comparisons | Accepted P0 and separate P1 contracts | Deferred |
| Later expansion | Source-to-skill, expert creator workflow, more sources/domains | Separate requirements and gates | Deferred |

The detailed [P0 implementation plan](../management/p0-implementation-plan.md) describes the sequence and pre-coding gate. Product coding starts only after the source and output contracts are approved, product decisions are resolved or explicitly scoped, controlled fixture provenance is recorded, and runtime/setup/check evidence is pinned. The [decision register](../management/decision-register.md) identifies open choices.

## Current progress update — 1 October 2026

### Achieved

- DATARA's intended product and first-release scope are documented.
- The P0 implementation plan is merged on main at commit ca689afccb9a6887e789b2975bd953e396b03eae. Planning review covered sequencing and task publication. It did not implement product behavior or verify a product.
- Yu Wang's role configuration and customer overview, roadmap, and landing-page content handoff are in draft PR [#281](https://github.com/fengguode/DATARA/pull/281). The independent technical review passed the source-document candidate [fdd856d](https://github.com/fengguode/DATARA/commit/fdd856d45254805e04457fcd673f2a221eedffa1) and reconfirmed the final status update at [6e4184b](https://github.com/fengguode/DATARA/commit/6e4184bf0201cc3f6c34cadf189a8994d5bd8d2f); the Quality Manager process/traceability review also passed at that head. The customer-comprehension review passed the progress/feedback wording at e3e02ff. No product feature is evidenced as implemented by this documentation work.
- Issue [#279](https://github.com/fengguode/DATARA/issues/279) is In review in the shared Project. This status describes the documentation task only.
- Product verification, the end-to-end athlete journey, founder acceptance and release have not occurred.

### Working on

- Reviewing the onboarding and customer-documentation draft PR. Yu Wang's configured role requests gpt-6.1-sol at medium reasoning effort; native role-loader activation is unconfirmed.
- Keeping product design and documentation distinct from product implementation. No product behavior is evidenced as implemented by this documentation work.

### Next

- Complete the review of PR #281 and retain the remaining accessibility-target, feedback-route, and public-access decisions as pre-publication items.
- Resolve the product decisions and evidence gates in the existing backlog before assigning product implementation.
- Plan and build the website only after design/architecture acceptance and approved stack/hosting scope.
- Keep product verification, athlete validation, founder acceptance, and release as distinct later gates.

### Open questions

- Which activity-file variants, fields and limits will be supported, and what controlled fixtures can be used?
- Which analyses, input requirements and quality checks belong in the first release?
- Which customer-selected model connections will be supported, and how will credentials be handled?
- What exactly should the dashboard and read-only API expose?
- Which stack, hosting, operational ownership and accessibility target will be approved?

These choices remain open in the decision register. This draft makes no provider, date, legal/compliance, retention, customer-feedback, or release commitment.

## Repeatable progress announcement

Use this format for each meaningful change:

> **Achieved:** outcome, evidence link and candidate; state whether it is implemented, verified, accepted or released.
>
> **Working on:** linked assignment, owner, intended outcome and current dependency.
>
> **Next:** upcoming work and prerequisites.
>
> **Open questions:** decision owner, affected users and expected impact.
>
> **Evidence and limits:** checks actually performed, results and what remains unverified.

Update after a material decision is recorded; work starts, completes or becomes blocked; review changes a material finding; verification changes; founder acceptance changes; or a release status changes. Keep detailed identifiers and engineering gates in the linked plan and issues. Refresh task status from the shared Project before every update. Keep announcement drafts in the repository. External publication requires the project's review and approval process.
