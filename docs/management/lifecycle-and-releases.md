# Datara lifecycle and release management

[Native GitHub Project](https://github.com/users/fengguode/projects/3) is the status board for DATARA. It is private and linked to this repository. The repository remains the source of requirements, decisions, code and evidence. [Control issue](https://github.com/fengguode/DATARA/issues/8) connects the board and Codex cloud work.

## Tracking

All repository issues and PRs are included automatically when created or updated; existing 15 issues are present. Views: prioritized backlog, status board, roadmap, bugs, review and assigned work. Classify work with Priority, Lifecycle and Milestone. New issues default to Backlog; set priority and lifecycle during triage. Keep dates and estimates unset until grounded. Bugs view uses the bug label; apply it to actual defect reports.

Statuses: Backlog → Ready → In progress → In review → Done. Blocked records a named dependency in the issue. Done tracks completion, not verification or acceptance: record Verified and Accepted decisions with actual evidence in the issue and requirement/test records. Closing an issue or merging a PR alone is insufficient. Do not close a parent issue merely because a partial PR merged. Retain completed items for release history.

## Milestones and gates

| Milestone | Scope | Acceptance |
| --- | --- | --- |
| P0 — First usable athlete release | WP01–WP06 (#1–#6), release gate #9 | Candidate-specific P0 tests, athlete validation and explicit release decision |
| P1 — Recommendations and routines | WP07 (#7) | Accepted P0, P1 test evidence and separate release decision |

Milestones have no committed dates. Completion percentages measure closed issues, not product quality. No product release is published or accepted yet; product verification remains Not run.

For each release create a gate issue following #9: identify version and candidate commit; map requirements to implementation PRs and executed cases; triage defects; record acceptance; prepare release notes, limitations, deployment and rollback instructions; then tag and publish the accepted candidate. Link post-release defects to affected version and fix evidence. Never mark a planned case Passed without execution evidence.

## Lifecycle backlog

| Issues | Purpose |
| --- | --- |
| #1–#5 | Requirements and P0 implementation |
| #6 | Final verification and athlete validation |
| #7 | P1 expansion |
| #8 | Project and requirements control |
| #9 | P0 release readiness and publication |
| #10 | Defects, incidents, recovery and follow-up |
| #11 | Security, data protection, backups and operational readiness |
| #12 | Dependencies, compatibility, migrations, deprecation and retirement |
| #13 | Later source-to-skill tooling |
| #14 | Later expert creator tools |
| #15 | Later data sources and domains |

Operational processes are planned work, not implemented services. Later initiatives require requirements derivation and review before development. Commercial design stays deferred.

Every development/change issue should include purpose, CUS and SR IDs where applicable, acceptance criteria, dependencies, affected versions and validation plan. Pull requests link the issue and evidence. Defects include reproducible steps, expected/actual behavior, severity, affected version and a regression case. Incidents add recovery and root-cause follow-up. Changes to approved requirements use the existing requirement-change template and update the registry and traceability together.
