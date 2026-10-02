# Roadmap and progress update

**Status:** customer-facing draft for review; not externally published.
**As of:** 2 October 2026. Read live on that date: main at commit `270dd6ca4e203e956b17eb14d4d959e1d57eef7a`, and the state of pull request #281. The previously cited planning baseline, main commit `ca689afccb9a6887e789b2975bd953e396b03eae` and merged pull request #278, remains correct as history and is four merged pull requests behind. Live task status: the [DATARA GitHub Project](https://github.com/users/fengguode/projects/3). The board may require access; no stale task counts are repeated here.

**The feature-illusion rule applies to this page.** It is a customer-facing surface, so it may not present a capability as working unless it is working, and it may not imply more capability than exists, whether through wording, imagery or structure. The [wiki page](https://github.com/fengguode/DATARA/wiki/Feature-Illusion-Rule) is the source of truth for that rule's wording; this page is not a mirror of it, so the precedence clause does not apply here, but the rule itself does. The most common way this page could break the rule is not by lying â€?it is by listing decided work under "Working on" and letting the reader add up the volume.

## Roadmap at a glance

Dates are omitted because the project has no approved calendar commitments.

| Stage | Intended outcome | Dependency or gate | Current state |
| --- | --- | --- | --- |
| Foundation | Vision, user outcomes, requirements and delivery sequence | Approved requirements and traceability | **Delivered as records only.** The five founding product decisions were selected on 1 October 2026 and are written down. That is documentation, not software. |
| First authorised increment | Import a supported file; keep the original unchanged; prepare the recorded values without a model; explain which inputs are missing; show saved history; serve the same saved values to a read-only API | A narrow exception to the usual pre-coding gate, authorised by the founder on 1 October 2026 with named outstanding risks | **Authorised to be built. Not built.** It produces no analysis, no model call, no result and no recommendation, and it is not a usable release. |
| Validated data home | Supported imports, persistent history, deterministic preparation and user isolation beyond the increment above | Approved file/data and security rules; lawful controlled fixtures | Not implemented |
| Manual analysis | Eligible baseline analyses, customer-selected model, manual runs and explicit failures | Data home; approved analysis and model-access rules; still gated | Not implemented; dependent |
| Saved outputs | Result lineage/history, dashboard and read-only API | Data and analysis stages; approved result/dashboard/API definitions | Partly described by the increment above; nothing built |
| Verification and release | Candidate checks and the complete athlete workflow | Evidence, live model checks where required, founder acceptance, then a separate release decision | **Not run.** No check, no athlete journey, no acceptance, no release |
| Later recommendations and routines | User-approved recommendations, recurring runs and comparisons | Acceptance of the first scope, and separate requirements | Deferred |
| Later expansion | Source-to-skill, expert creator workflow, more sources/domains | Separate requirements and gates | Deferred |

The detailed [implementation plan](../management/p0-implementation-plan.md) describes the sequence and the pre-coding gate. That gate was relaxed on 1 October 2026 for the single increment named in the table above, and only for that increment. The [decision register](../management/decision-register.md) records the authorised scope, the risks the founder accepted, and what remains gated. Internal stage identifiers for every row above are held in those management records rather than on this page.

## Current progress update â€?2 October 2026

Read this section with the feature-illusion rule in mind. The list below records
**records produced**, not **software produced**. Those two things are easy to blur and
the blur is the failure this rule exists to prevent.

### Achieved

- DATARA's intended product and first-release scope are documented. Documenting a scope is not delivering it.
- The implementation plan is merged on main (originally at commit `ca689afccb9a6887e789b2975bd953e396b03eae` via PR [#278](https://github.com/fengguode/DATARA/pull/278); main has since advanced to `270dd6ca4e203e956b17eb14d4d959e1d57eef7a`). Planning review covered sequencing and task publication. It did not implement product behavior or verify a product.
- The five founding product decisions were selected on 1 October 2026 and recorded in the [dated decision baseline](../management/p0-decision-baseline-2026-10-01.md): the FIT source and intake approach, the first three analyses and their eligibility rules, the first two model providers, the dashboard and read-only API outcome, and the technical stack and pilot environment. The founder separately selected a narrow exception to the pre-coding gate for one first increment, recorded in the [decision register](../management/decision-register.md). **Deciding and recording are the achievements here. They are not a product.**
- A governance rule about overclaiming was adopted on 1 October 2026 and maintained at [the project wiki](https://github.com/fengguode/DATARA/wiki/Feature-Illusion-Rule). It is written down and mirrored into the Code of Conduct, the [landing-page brief](landing-page-brief.md) and the [project vision](../project-brief-and-roadmap.md).
- The customer documentation work tracked by issue [#279](https://github.com/fengguode/DATARA/issues/279) was delivered and **merged on 1 October 2026** as PR [#281](https://github.com/fengguode/DATARA/pull/281), merge commit `0bf60cb4d1da2f41cf4aa3a11ff71fb17cc8f80b`. Independent technical review, quality/traceability audit and a customer-comprehension review each passed on the reviewed candidates recorded in that pull request. The design and publication items it left open are still open. **An earlier draft of this page described PR #281 as still under review; that was wrong, and is corrected here.**
- **Product verification, the end-to-end athlete journey, founder acceptance and release have not occurred. None of them has started.**

### Working on

- Preparation for the first authorised increment: the source mappings, intake, persistence, normalisation, eligibility and read-surface contracts that have to exist before any of it can be written. All of it is still preparation.
- Customer-facing documentation, including this consistency pass, which found and corrected stale status claims in the customer documents. It changed no product behavior and none exists.
- Role and runtime honesty is maintained rather than assumed: a configured agent role is not a running agent, and native role loading has not been confirmed. This is a statement about how the work is done, not about the product.

### Next

- Finish the contracts the first increment depends on, and record what remains unmet rather than starting to build against them.
- Keep the outstanding accessibility, feedback-route and public-access items as pre-publication decisions for the website.
- Keep model-provider integration, analysis runs, the athlete journey, founder acceptance and release as separate later gates. None of them is authorised yet.
- Plan and build the website only after design and architecture acceptance.

### Decided on 1 October 2026, and still not built

This section exists because a progress page that lists only open questions is as
misleading as one that lists only achievements. These are settled directions. None of
them is running software, and none of them carries a date.

| Question as previously published | What was decided | What is still open |
| --- | --- | --- |
| Which activity-file variants, fields and limits? | Single-session running and cycling, indoor and outdoor; file and batch size limits chosen. | Which test files may lawfully be used, where they come from, and what the field-level mappings are. |
| Which analyses, input requirements and quality checks? | Three analyses: a summary of recorded activity, a recorded-volume trend, and recorded consistency. Their eligibility and coverage rules are written down. | The evaluation anchors, the quality thresholds, and any live testing of a real model. |
| Which model connections, and how are credentials handled? | OpenAI and DeepSeek, chosen by the founder, using the customer's own account and API access with server-side handling. | Which exact models, whether the providers work from the pilot's location, what each provider retains, and what account setup each needs. |
| What does the dashboard and read-only API expose? | Imported history with its quality and conflicts, recorded volume by week and sport, why an analysis is or is not available, and saved runs, results and failures. | The exact field and error formats. |
| Which stack, hosting and accessibility target? | A specific application stack and database; a first pilot run locally for personal use; WCAG 2.2 AA as the design target. | Who operates and supports it, how backups and keys are recovered, and the setup commands that make a run reproducible. |

The previously published open-questions list has been replaced with this table. Four
of its five questions were answered at direction level on 1 October 2026; the table
shows what was actually answered, and what was not, so the two are not confused.

This draft makes no provider, date, legal/compliance, retention, customer-feedback, or
release commitment.

## Repeatable progress announcement

Use this format for each meaningful change:

> **Achieved:** outcome, evidence link and candidate; state whether it is implemented, verified, accepted or released.
>
> **Working on:** linked assignment, owner, intended outcome and current dependency.
>
> **Next:** upcoming work and prerequisites.
>
> **Decided but not built:** directions chosen since the last update, and the named risks the owner accepted to choose them. A decision is not a delivery.
>
> **Open questions:** decision owner, affected users and expected impact.
>
> **Evidence and limits:** checks actually performed, results and what remains unverified.

Before any of it is published, apply the [feature-illusion test](https://github.com/fengguode/DATARA/wiki/Feature-Illusion-Rule): would a reasonable reader, having read this, believe a capability exists that does not? The usual failure in a progress page is not a false sentence. It is a list of decided, prepared or in-progress work that adds up to a product.

Update after a material decision is recorded; work starts, completes or becomes blocked; review changes a material finding; verification changes; founder acceptance changes; or a release status changes. Keep detailed identifiers and engineering gates in the linked plan and issues, not on a customer-facing page. Refresh task status from the shared Project, and re-read the live state of anything this page names as open, before every update. Keep announcement drafts in the repository. External publication requires the project's review and approval process.
