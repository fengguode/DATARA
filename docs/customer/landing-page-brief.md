# Customer and contributor landing-page brief

**Status:** product content and delivery handoff for the current architecture/design phase; not a built or published website.
**Status checked:** 1 October 2026 against main commit ca689afccb9a6887e789b2975bd953e396b03eae, merged planning PR #278, project issue #277 and current product validation/lifecycle records. Refresh these sources before design acceptance or publication.

## Audience and objectives

**Primary audience:** athletes with Garmin activity history who want consistent training context, transparent analysis and control over which model is used.

**Secondary audience:** prospective contributors who want to understand product boundaries, maturity and useful ways to participate.

Visitors should be able to answer: What is DATARA trying to do? What is available today? How is the intended workflow supposed to work? What is delayed or unknown? Where can I follow progress, ask a question or contribute?

## Information structure

1. Hero: one-sentence purpose, current maturity label, links to overview and status.
2. Intended workflow: upload → validate and prepare → check availability → user selects analysis and model → manual run → saved result with evidence.
3. Scope: P0 first milestone, explicitly deferred P1 and later work.
4. Current status: planning, implementation, verification, founder acceptance and release shown separately.
5. Roadmap: stages and dependencies, linked to the implementation plan and shared Project.
6. Data and model expectations: deterministic preparation, customer-owned model access, isolation goals and unresolved details.
7. Participate: customer feedback path and contributor path, with access requirements disclosed.
8. Footer: source documents, status as-of date, last-reviewed date and verified links.

## Complete draft copy

### Hero

**A personal data home for useful expertise.**

DATARA is being designed to turn supported activity data into useful, traceable outcomes. You will choose which analysis fits your data and which supported model connection to run it with.

**Current stage: product planning.** The first athlete workflow is not yet available for customer use.

Links: [Explore the product direction](product-overview.md) · [View the GitHub Project](https://github.com/users/fengguode/projects/3) · [Ask a question or share feedback](https://github.com/fengguode/DATARA/issues)

### Intended workflow

**Your data comes first.** DATARA plans to validate supported activity files and prepare consistent training history with conventional software.

**You see what the data supports.** The system will identify which analyses fit the available data and explain missing inputs.

**You stay in control.** You will select an analysis and a supported model connection using your own provider account/API access before a manual run. The provider may require separate account setup or charges under its terms.

**Results remain reviewable.** Saved findings are intended to include evidence and run history, so you can revisit them without making a new model request.

These capabilities are planned; they are not released features.

### Scope

**First milestone:** supported Garmin FIT uploads, persistent history, deterministic preparation, a small evaluated set of analyses, data-based eligibility, manual analysis through a user-selected model connection, saved results, a predefined dashboard, a read-only API and user isolation.

**Later:** user-approved recommendations, recurring routines, feedback and comparisons.

**Deferred:** commercial mechanisms, source-to-skill automation, expert creator tooling and additional data sources or domains.

### Current status

| Delivery state | Current evidence |
| --- | --- |
| Planning | The P0 task sequence and proposed readiness plan are recorded in merged PR #278. Planning review covered sequencing and task publication; product decisions remain open. |
| Implementation | No product implementation is evidenced as of 1 October 2026. Source: the reviewed planning baseline at main commit ca689afccb9a6887e789b2975bd953e396b03eae and issue #277. |
| Verification | Product checks and the end-to-end athlete journey have not been run. The [validation plan](../management/validation-plan.md) lists planned cases, not passing evidence. |
| Acceptance | Founder acceptance of a product candidate has not occurred. See the [P0 release gate issue](https://github.com/fengguode/DATARA/issues/9). |
| Release | No product release is recorded. See [lifecycle and release policy](../management/lifecycle-and-releases.md). |

The [GitHub Project](https://github.com/users/fengguode/projects/3) is the live task-status source and may require access. If a visitor cannot open it, the page must still show its dated maturity summary and link to the public repository [issue list](https://github.com/fengguode/DATARA/issues). Do not describe the board as publicly accessible until access is verified. Planning completion does not mean a product feature is available.

**Feature-illusion constraint on this page.** This page must never present a capability as working unless it is working, and must never imply more capability than exists. No mock, placeholder, sample output, or screenshot of non-running software may appear as a product result, and no wording, image, navigation element or workflow may lead a reasonable reader to believe a feature exists or is available when it does not. The test is what the reader would conclude after reading the page, not what the words literally say.

This constrains illustration as much as claim. A placeholder screenshot, a mock dashboard, or a worked example that was not produced by the real system is prohibited on this page, because a visitor cannot distinguish it from a real one. Where a capability is planned but unbuilt, the page says so in the same place and at the same time as any related mention, rather than in a footnote.

The rule is maintained at [the project wiki](https://github.com/fengguode/DATARA/wiki/Feature-Illusion-Rule), which is its source of truth. If this brief and the wiki disagree, the wiki governs and this brief is the defect. That precedence covers the wording of the rule only. It does not decide what the product may claim: the [requirement records](../management/product-requirements.md) and the [dated decision baseline](../management/p0-decision-baseline-2026-10-01.md) remain authoritative, and this brief may not present a capability those records do not support.

### Data and model expectations

The product direction is to keep original uploads linked to normalized records, prepare data without model calls, and isolate each user's files, credentials and results. An analysis (called a “skill” in the project records) is eligible when the selected data meets its stated input needs. For analysis, the user chooses a supported provider connection and supplies their own account/API access. Provider support, credential handling, retention period and deployment environment remain undecided.

### Join in

**Have a customer question or feedback?** The currently documented route is a focused issue in the [DATARA repository](https://github.com/fengguode/DATARA/issues). Submitting an issue requires a GitHub account and permission to create repository issues. No alternative customer contact channel has been approved. Before publication, the owner must confirm whether this route is usable for the intended audience, including issue-creation permission, or record an approved alternative.

**Want to contribute?** Start with the [shared project board](https://github.com/users/fengguode/projects/3); access may be restricted. If proposing work, open an issue with the user need, affected CUS/SR, dependencies and observable acceptance criteria. Follow the [team workflow](../team/workflow.md). Keep product claims tied to evidence.

## Journeys

**Customer journey:** arrive → understand purpose and maturity → inspect intended workflow and boundaries → review progress and unknowns → open the product overview or dated status summary → submit feedback through the available route.

**Contributor journey:** arrive → understand architecture and scope → review the P0 roadmap and status → open an existing task or propose a scoped issue → coordinate through repository workflow.

Neither journey implies account signup, file upload, API access or a live service.

## Design and accessibility acceptance criteria

**Proposed accessibility target, pending owner approval before design acceptance:** WCAG 2.2 Level AA. This is a design target proposal, not a claim of legal compliance.

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

These measurable criteria follow the [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/) and [Target Size (Minimum) guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum). The target requires owner approval before design acceptance.

## Design and implementation handoff

- **Product content owner:** Product Manager — Yu Wang. Maintains claim accuracy, terminology, roadmap summary, feedback paths, as-of date and link checks before publication and after a material decision, task/status change, implementation/verification/acceptance/release change, or accepted product feedback. Sources: product brief for intent, implementation plan for sequence, GitHub Project for live task status, and candidate-specific verification/acceptance/release records for maturity.
- **Design coordination:** UI Designer — Wu Yunzhou. Owns page hierarchy, responsive behavior, link and access states, interaction details and accessibility design criteria; preserves approved product wording boundaries.
- **Feasibility coordination:** Worker — Torsten Maier. Reviews structure and status-data sources, and estimates implementation handoff only after stack and hosting decisions are approved.
- **Coordination/integration:** Yi Tang. Maintains task and Project status, assigns exclusive design/implementation files, collects reviews and records blockers.
- **Status fallback:** If the Project is private or unavailable to visitors, retain the dated maturity summary on the page and link to the public issue list. Verify access states before publication; never imply that private-board fields are public.
- **Gate:** No product coding assignment starts until G0 in the [P0 implementation plan](../management/p0-implementation-plan.md) is closed: approved source/output contracts; D01–D05 resolved or applicability explicitly approved; lawful controlled fixtures with provenance; and pinned runtime, setup and check evidence. Page implementation is a separate task after architecture/design acceptance and approved stack/hosting scope. Publication requires project reviews and founder approval for material commitments.
