# Customer and contributor landing-page brief

**Status:** product content and delivery handoff for the current architecture/design phase; not a built or published website.
**Status checked:** 2 October 2026, against a live read of main at commit `270dd6ca4e203e956b17eb14d4d959e1d57eef7a`, the five merged pull requests that followed the previously cited commit `ca689afccb9a6887e789b2975bd953e396b03eae`, and the current validation and lifecycle records. The earlier status line was checked against a commit that predates every product decision in this project, and has been replaced. Refresh these sources again before design acceptance or publication; a status line is only worth printing if it is still true when it is read.

## Audience and objectives

**Primary audience:** athletes with Garmin activity history who want consistent training context, transparent analysis and control over which model is used.

**Secondary audience:** prospective contributors who want to understand product boundaries, maturity and useful ways to participate.

Visitors should be able to answer: What is DATARA trying to do? What is available today? How is the intended workflow supposed to work? What is delayed or unknown? Where can I follow progress, ask a question or contribute?

## Information structure

1. Hero: one-sentence purpose, current maturity label, links to overview and status.
2. Intended workflow: upload → validate and prepare → check availability → user selects analysis and model → manual run → saved result with evidence. Every one of these steps is labelled *not built* in the copy itself, not once at the end of the section.
3. Scope: the first release scope, with later and deferred work named separately. Internal stage identifiers are held in the [decision register](../management/decision-register.md) rather than on this page, because a visitor has no way to interpret them and a bare label reads as a promise.
4. Current status: decisions, implementation, verification, founder acceptance and release shown separately, because they are separate facts and conflating them is how a decision starts reading as a delivery.
5. Roadmap: stages and dependencies, linked to the implementation plan and shared Project.
6. Data and model expectations: deterministic preparation, customer-owned model access, isolation goals and unresolved details.
7. Participate: customer feedback path and contributor path, with access requirements disclosed.
8. Footer: source documents, status as-of date, last-reviewed date and verified links.

## Complete draft copy

### Hero

**A personal data home for useful expertise.**

DATARA is being designed to turn supported activity data into useful, traceable outcomes. **None of it is built.** The intended design is that you choose which analysis fits your data, and which supported model connection to run it with.

**Current stage: the first scope has been decided, and none of it is built.** There is no DATARA application. No part of the athlete workflow is available for customer use, and nothing has been verified, accepted or released.

Links: [Explore the product direction](product-overview.md) · [View the GitHub Project](https://github.com/users/fengguode/projects/3) · [Ask a question or share feedback](https://github.com/fengguode/DATARA/issues)

### Intended workflow

Every item in this section is a design intention. **None of it is built and none of it is available.** Read each line as "this is what DATARA is intended to do", not as a description of software you can use today.

**Your data comes first. (Intended. Not built.)** DATARA is intended to validate supported activity files and prepare consistent training history using ordinary software, without using an AI model to read, check or prepare your files.

**You see what the data supports. (Intended. Not built.)** It is intended to check whether the data you selected supports a given analysis, and to name which inputs are missing. That check is arithmetic over your recorded values. It does not consult a model, and it is not a judgment about your training.

**You stay in control. (Intended. Not built.)** You are intended to select an analysis and a supported model connection, using your own provider account and API access, before any run happens. The provider may require separate account setup or charge under its own terms.

**Results remain reviewable. (Intended. Not built.)** Saved findings are intended to carry their evidence and run history, so you can return to them later without making a new model request.

Nothing in this section exists. No file has been imported, no analysis has been run, and no result has been produced.

### Scope

**The first release scope — intended, and none of it built:** supported Garmin FIT uploads, persistent history, deterministic preparation, a small evaluated set of analyses, eligibility based on your own data, manual analysis through a model connection you select, saved results, a predefined dashboard, a read-only API, and separation between users.

**This bundle is not what arrives next.** A smaller first increment has been authorised to be built, covering file import, immutable originals, deterministic preparation, eligibility explanation, saved history and a read surface. **It produces no analysis, no model call, no result and no recommendation, and it is not a usable release.** The authorised scope and what it deliberately excludes are recorded in the [decision register](../management/decision-register.md).

**Later:** user-approved recommendations, recurring routines, feedback and comparisons.

**Deferred:** commercial mechanisms, source-to-skill automation, expert creator tooling and additional data sources or domains.

### Current status

| Delivery state | Current evidence |
| --- | --- |
| Decisions | The task sequence and readiness plan are recorded in merged PR #278. The five founding product decisions (D01–D05) were selected on 1 October 2026 and are recorded in the [dated decision baseline](../management/p0-decision-baseline-2026-10-01.md). Selecting a direction is not building it: source conformance evidence, evaluation anchors, exact interface schemas and operational ownership are still unmet. |
| Implementation | **No product implementation is evidenced as of 2 October 2026.** The repository holds requirements, decision records, design material and one tooling script. It holds no application code. Source: live read of main at commit `270dd6ca4e203e956b17eb14d4d959e1d57eef7a`, 2 October 2026. |
| Verification | Product checks and the end-to-end athlete journey have not been run. The [validation plan](../management/validation-plan.md) lists planned cases, not passing evidence. |
| Acceptance | Founder acceptance of a product candidate has not occurred. See the [release gate issue](https://github.com/fengguode/DATARA/issues/9). |
| Release | No product release is recorded. See [lifecycle and release policy](../management/lifecycle-and-releases.md). |

The [GitHub Project](https://github.com/users/fengguode/projects/3) is the live task-status source and may require access. If a visitor cannot open it, the page must still show its dated maturity summary and link to the public repository [issue list](https://github.com/fengguode/DATARA/issues). Do not describe the board as publicly accessible until access is verified. Planning completion does not mean a product feature is available.

**Feature-illusion constraint on this page.** This page must never present a capability as working unless it is working, and must never imply more capability than exists. No mock, placeholder, sample output, or screenshot of non-running software may appear as a product result, and no wording, image, navigation element or workflow may lead a reasonable reader to believe a feature exists or is available when it does not. The test is what the reader would conclude after reading the page, not what the words literally say.

This constrains illustration as much as claim. A placeholder screenshot, a mock dashboard, or a worked example that was not produced by the real system is prohibited on this page, because a visitor cannot distinguish it from a real one. Where a capability is planned but unbuilt, the page says so in the same place and at the same time as any related mention, rather than in a footnote.

The rule is maintained at [the project wiki](https://github.com/fengguode/DATARA/wiki/Feature-Illusion-Rule), which is its source of truth. If this brief and the wiki disagree, the wiki governs and this brief is the defect. That precedence covers the wording of the rule only. It does not decide what the product may claim: the [requirement records](../management/product-requirements.md) and the [dated decision baseline](../management/p0-decision-baseline-2026-10-01.md) remain authoritative, and this brief may not present a capability those records do not support. This mirror was compared against the live wiki page on 2 October 2026 and agrees with it. The wiki itself was not changed.

### Data and model expectations

Everything in this section is design intent, not current behavior. **None of it is built. DATARA currently holds no user file, no credential and no result, and provides no separation between users.** Anyone who hands DATARA a file today is handing it to nothing.

- **Data handling.** The intent is to keep each original upload linked to the prepared records derived from it, to do that preparation without calling a model, and to keep one user's files, credentials and results inaccessible to another user. **Not implemented, and not tested.**
- **Whether an analysis is available.** The intent is that an analysis — called a “skill” in the project records — is available when the data you selected meets the inputs that analysis declares, and that when it is not available, the missing inputs are named. That check is arithmetic over your recorded values. It does not consult a model. **Not implemented.**
- **Whose model runs it.** The intent is that you choose a supported provider connection and supply your own account and API access. **Not implemented.**

**What has actually been decided, and what has not.** On 1 October 2026 the project selected its first two model providers, its technical stack, and a first pilot that runs locally for personal use. Approaches for credentials, data retention and deployment were chosen in the same decision. Still undecided: which exact models to support, whether those providers can be reached and used from the pilot's location, retention obligations under law, and any hosting or operating arrangement.

Choosing an approach is not building it. **None of the above exists as working software**, and a decided direction is not a promise of a date.

### Join in

**Have a customer question or feedback?** The currently documented route is a focused issue in the [DATARA repository](https://github.com/fengguode/DATARA/issues). Submitting an issue requires a GitHub account and permission to create repository issues. No alternative customer contact channel has been approved. Before publication, the owner must confirm whether this route is usable for the intended audience, including issue-creation permission, or record an approved alternative.

**Want to contribute?** Start with the [shared project board](https://github.com/users/fengguode/projects/3); access may be restricted. If proposing work, open an issue with the user need, affected CUS/SR, dependencies and observable acceptance criteria. Follow the [team workflow](../team/workflow.md). Keep product claims tied to evidence.

## Journeys

**Customer journey:** arrive → understand purpose and maturity → inspect intended workflow and boundaries → review progress and unknowns → open the product overview or dated status summary → submit feedback through the available route.

**Contributor journey:** arrive → understand architecture and scope → review the [roadmap and current status](roadmap-and-progress.md) → open an existing task or propose a scoped issue → coordinate through the repository workflow.

Neither journey implies account signup, file upload, API access or a live service.

## Design and accessibility acceptance criteria

**Selected accessibility design target:** WCAG 2.2 Level AA, selected by the project on 1 October 2026. This is a design target. **It is not a claim of legal compliance, and it is not a claim that any page conforms, because there is no page.** It applies once a page is built.

- At narrow mobile, tablet and wide desktop widths, content reflows without horizontal page scrolling; navigation, tables and calls to action remain usable.
- Text remains usable at 200% zoom without loss of content or function.
- Normal text contrast is at least 4.5:1; large text at least 3:1. Visual information needed to identify controls and states has at least 3:1 contrast.
- Pointer targets are at least 24 by 24 CSS pixels where WCAG 2.2 SC 2.5.8 applies, or meet its spacing/exceptions.
- Every interaction works by keyboard, follows a logical focus order, has a visible focus state and a descriptive accessible name.
- Heading levels describe the information structure; links describe their destination or action.
- Status is conveyed in text, not color alone. Tables have clear headers and remain understandable on small screens.
- Reduced-motion preferences are respected. Current-stage and roadmap copy remains understandable without graphics or animation.
- Screen readers can identify the page title, section headings, status labels, link purpose and any form validation/error message.
- Customer comprehension review confirms that planning, a mock or a proposed contract cannot be mistaken for a released capability.
- This brief assumes an external repository issue link, matching the currently documented feedback route. Design its sign-in, permission-denied and unavailable states; do not add an in-page form or alternate contact route unless separately approved.

These measurable criteria follow the [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/) and [Target Size (Minimum) guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum). The target was selected on 1 October 2026 and still has to be applied and checked before this page is built or published.

## Design and implementation handoff

- **Product content owner:** Product Manager — Yu Wang. Maintains claim accuracy, terminology, roadmap summary, feedback paths, as-of date and link checks before publication and after a material decision, task/status change, implementation/verification/acceptance/release change, or accepted product feedback. Sources: product brief for intent, implementation plan for sequence, GitHub Project for live task status, and candidate-specific verification/acceptance/release records for maturity.
- **Design coordination:** UI Designer — Wu Yunzhou. Owns page hierarchy, responsive behavior, link and access states, interaction details and accessibility design criteria; preserves approved product wording boundaries.
- **Feasibility coordination:** Worker — Torsten Maier. Reviews structure and status-data sources, and estimates implementation handoff only after stack and hosting decisions are approved.
- **Coordination/integration:** Yi Tang. Maintains task and Project status, assigns exclusive design/implementation files, collects reviews and records blockers.
- **Status fallback:** If the Project is private or unavailable to visitors, retain the dated maturity summary on the page and link to the public issue list. Verify access states before publication; never imply that private-board fields are public.
- **Gate:** Product coding was originally held behind a readiness checklist in the [implementation plan](../management/p0-implementation-plan.md). On 1 October 2026 the founder authorised a narrow exception for one first increment — file import, immutable originals, deterministic preparation, eligibility explanation, saved history and a read surface — accepting named outstanding risks. The [decision register](../management/decision-register.md) records the authorised scope and what it does not waive. Model-provider integration, analysis runs, the end-to-end athlete journey and release stay gated, and nothing in the authorised increment produces an analysis result. Page implementation remains a separate task after design and architecture acceptance. Publication requires project reviews and founder approval for material commitments.
