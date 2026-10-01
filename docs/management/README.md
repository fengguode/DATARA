# DATARA project management

*A universe of expertise. Working for you.*

This is the single management entry point for Datara. [Project control issue](https://github.com/fengguode/DATARA/issues/8) tracks delivery. One target Codex cloud environment serves management, system engineering, delivery tasks, verification, and final validation. The [DATARA Codex environment](https://chatgpt.com/codex/cloud/settings/environment/6abc9f6b878c8191bca11872a839a62a) is created and connected to fengguode/DATARA. Runtime checks and product validation are tracked separately.

## Management documents

- [Agreed project brief and roadmap](../project-brief-and-roadmap.md)
- [Founding brainstorming record](../brainstorming-record-2026-09-30.md)
- [Customer-User-Stories (top-level requirements)](product-requirements.md)
- [P0 requirement breakdown](p0-breakdown.md)
- [First-milestone implementation roadmap and ordered plan](p0-implementation-plan.md)
- [System requirements](system-requirements.md)
- [Machine-readable registry](requirements-registry.json)
- [GitHub requirement issue and Project mapping](github-requirements-map.json)
- [Traceability](traceability.md)
- [Verification and final validation plan](validation-plan.md)
- [Decisions and change management](decision-register.md)
- [D01-D05 delegated selections and remaining evidence (1 October 2026)](p0-decision-baseline-2026-10-01.md)
- [WP01 proposed requirements baseline](wp01-requirements-package.md)
- [WP01 issue-update handoff](wp01-issue-handoff.md)
- [Cloud project setup and first task](cloud-project.md)

## Delivery order

| Package | Priority | Task | Dependencies |
| --- | --- | --- | --- |
| WP01 | P0 | [Define source contract and release baseline](https://github.com/fengguode/DATARA/issues/1) | None |
| WP02 | P0 | [Build persistent data home and deterministic preprocessing](https://github.com/fengguode/DATARA/issues/2) | WP01 |
| WP03 | P0 | [Specify baseline skills and eligibility pipeline](https://github.com/fengguode/DATARA/issues/3) | WP01, WP02 |
| WP04 | P0 | [Implement customer model connections and manual execution](https://github.com/fengguode/DATARA/issues/4) | WP03 |
| WP05 | P0 | [Deliver result history dashboard and output API](https://github.com/fengguode/DATARA/issues/5) | WP02, WP04 |
| WP06 | P0 | [Perform final verification and athlete validation](https://github.com/fengguode/DATARA/issues/6) | WP01, WP02, WP03, WP04, WP05 |
| WP07 | P1 | [Add skill recommendations routines and comparison](https://github.com/fengguode/DATARA/issues/7) | WP06 |

## Control rules

Customer-User-Stories (CUS) are the top-level customer and user outcomes derived from the founding decisions. System requirements (SR) are derived obligations across applicable perspectives, including legal, engineering, running environments, architecture, and data security. The current SR set is an initial draft; this classification does not assert complete coverage of those perspectives. The GitHub Project is the central shared backlog and authoritative status record. The local JSON registry is a machine-readable content and traceability mirror, not a second status board. Features link CUS outcomes to SR obligations; planned tasks and STKs inherit package and parent gates. Synchronize human-readable documents and registry links after Project publication. Track planned, implemented, verified, accepted, and released states separately. No added verification case currently has passing evidence.

Use each linked issue as its package record. Split implementation tasks under that package when scope is known, preserving requirement links. Estimate after dependencies and contracts are understood. The founder owns product decisions and final acceptance; cloud tasks prepare reviewable engineering artifacts and evidence.

Run `python scripts/check_requirements.py` after registry changes. It checks legacy CUS/SR/TK/WP/TC links and planned coverage only. Additive Features, STKs, and perspective assessments require direct audit and independent QM/Reviewer review. Final validation requires actual software and a fixed candidate commit.

## Requirement and backlog title convention

Every requirement and backlog-item title must use the same template:

```text
[Type][area]content_of_title
```

Use one actual type and one actual area, not the slash-separated lists. Types include `CUS`, `SR`, `Feature`, `Task`, and `bug`; areas include `frontend`, `backend`, `database`, and `security`. Use an appropriate additional type or area when needed, consistently across the project (for example `management`, `architecture`, `legal`, or `runtime`). The content is a concise, readable description of the need, obligation, feature, task, or defect.

Examples:

- `[CUS][frontend]View saved training results`
- `[SR][security]Enforce user authorization on every result query`
- `[Feature][database]Persist normalized activity history`
- `[Task][backend]Implement deterministic eligibility checks`
- `[bug][frontend]Show failed analysis runs in history`

Apply the convention to requirement-record titles and GitHub backlog issue titles. Keep stable CUS/SR identifiers and their traceability links in the record or issue body; a title prefix does not replace an identifier or change the CUS-to-SR hierarchy. **Priority must not appear in the title**, including `P0`, `P1`, `P2`, or urgency labels. Store priority in the GitHub Project **Priority** field and the requirement record's dedicated priority metadata.

## GitHub lifecycle project

Follow the [pull request confirmation policy](../team/pull-request-confirmation.md) for founder CUS confirmation, dedicated team-role confirmations, independent evidence gates, and named GitHub reporting.

[DATARA — Development and Lifecycle](https://github.com/users/fengguode/projects/3) tracks repository issues and PRs, priorities, lifecycle stages and release milestones. See [lifecycle and release management](lifecycle-and-releases.md).
