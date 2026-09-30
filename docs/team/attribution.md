# Named agent assignments and contributions

Use this protocol for new work under the [DATARA Project](https://github.com/users/fengguode/projects/3). It implements the founder-approved attribution agreement tracked in [issue #23](https://github.com/fengguode/DATARA/issues/23). The Primary Coordinator maintains the public activity record and preserves the evidence supplied by each contributing agent.

## Identity and responsibility

Use the roster's role and configured name together, for example **Worker — Torsten Maier (AI agent)**. These are AI role personas, not evidence that a person with that name participated. Distinguish the assigned persona, actual runtime agent ID or execution link, contributor, integrator, and authenticated GitHub publisher. If a role definition or effective settings were not observably loaded, say so; a named assignment does not prove native activation.

The Project's single-select **Agent** field identifies the currently responsible role. Use the ten role/name options in the roster, including Primary Coordinator — Codex. It records ownership, not who is currently running or every contributor. Give independent bounded assignments separate linked issues or sub-issues when they need separate ownership or status. An issue-recorded handoff updates this field and names the successor. Leave unassigned work unset rather than inferring an agent from its topic. Multiple contributors appear in the assignment record and contribution table.

GitHub's authenticated account remains the publisher of comments and pushes. The comment heading names the contributing agent and whether the primary relayed its report. Git author and committer identities remain accurate; changing a commit message does not create a GitHub account or independent runtime identity. Separate bot identities would require a separately authorized account/App setup. This agreement does not create them or grant agents publishing rights.

## Assignment record

Before delegation, record the following in the linked issue. The primary owns integration; the assignee owns only the named files for the assignment. Include a visible work-start update and subsequent progress, blocker, review, and completion updates as appropriate.

```text
Assigned agent: Worker — Torsten Maier (AI agent)
Coordinator: Primary Coordinator — Codex
Assignment: #<issue> / <bounded assignment ID>
Work package / CUS / SR: <IDs, or no product scope changes>
Scope and exclusive files: <outcome and exact paths>
Dependencies: <issues and decisions>
Acceptance criteria: <observable conditions>
Evidence requested: <checks, files, and findings>
Branch / pull request: <links, or pending>
Runtime agent ID / execution: <actual ID/link, or unavailable>
Runtime state: <assigned, running, blocked, completed, interrupted>
Configuration loading: <observed evidence, or unconfirmed>
```

An agent returns its actual runtime identifier when available, owned changed paths, results, proposed contribution boundaries, validation evidence, and unresolved questions. Read-only agents return findings and reports without editing, committing, or publishing. The primary captures this handoff before integration and compares every tracked and untracked changed path with the assignment.

## Activity comment

Prefix each issue or pull request comment with the role/name that produced the outcome. A coordinator's own update names the coordinator; a relayed report names both its source and publisher. Only attribute work to an agent when a real run or evidenced handoff supports the claim. Explicitly label examples, planned assignments, and unavailable execution links.

```text
Worker — Torsten Maier (AI agent) · Implementation completed
Published by: Primary Coordinator — Codex, relaying the Worker's report
Assignment: #<issue> / <assignment ID>
Runtime agent ID / execution: <actual ID/link, or unavailable>
Outcome: <concrete result>
Contribution: <changed paths, purpose, and commit/diff links>
Validation: <actual commands/results and evidence links>
Remaining decisions or blockers: <named items, or none>
Branch / pull request: <links>
```

A review comment additionally identifies the reviewed commit, findings with file/line and severity, coverage limits, and whether the review was performed independently. An agent's completion changes its reported runtime state; task Status, verification, acceptance, and release still follow their separate gates.

## Commit attribution

Preserve each bounded agent contribution as a separate commit when practical. The primary reviews the diff and creates or integrates the commit under the actual committing identity. Use per-command Git identity settings if needed, rather than changing the user's global identity. Record the source role in trailers only when supported by the run/handoff evidence. Shared work lists each evidenced contributor and describes the file or change boundaries in the body and pull request table. Integration fixes belong in a separate primary contribution when practical.

```text
Add duplicate detection

Describe the behavior and paths changed by this contribution.

Implemented-by: Worker — Torsten Maier (AI agent)
Integrated-by: Primary Coordinator — Codex
Assignment: #<issue> / <assignment ID>
Agent-run: <actual ID/link, or unavailable>
```

Use `Contributed-by` for documentation or other non-implementation contributions. Use `Implemented-by` for actual implementation. A reviewer who supplies findings is recorded in the review table/comment, not automatically as an implementation author. These are searchable metadata trailers, not signatures or GitHub account attribution. GitHub `Co-authored-by` is reserved for real account-linked attribution with the contributor's authorized email; never invent or borrow a person's address. Preserve historical commit identities and comments. Any retrospective contribution summary must cite existing evidence and label unavailable attribution rather than rewriting history.

## Pull request contribution table

Include this table in the pull request body. Link each contribution to its specific commit/diff, comment or report, and validation. A review-only contribution may have no commit; use the reviewed commit plus the review evidence instead. When squashing or rebasing, preserve the contribution table and trailers and update the links to the resulting commits.

| Agent (AI role) | Assignment / runtime | Contribution and files | Commit or reviewed commit | Comment / evidence | Integrator / publisher |
| --- | --- | --- | --- | --- | --- |
| <role — name> | <issue, run ID/link or unavailable> | <specific changes or review findings> | <linked SHA/diff> | <links and actual checks> | <role and authenticated account> |

## Reporting and audit

The coordinator uses the authorized GitHub CLI or connector to publish updates and set Project fields, then reads them back. Project changes and runtime reports are explicit; there is no automatic synchronization with agent execution. If publishing fails, save the pending comment under `docs/team/pending-updates/<issue>-<assignment>.md`, report the exact failure and out-of-sync state, and publish/reconcile it after access recovers. Keep credentials and raw internal reasoning out of all records.

Independent review and Quality Manager audits check that assignment identity, owned files, actual run evidence, commits, review comments, and Project ownership agree. Report missing evidence rather than attributing a role because its name appears in a template. These process checks do not prove product behavior, native custom-agent activation, acceptance, or release readiness.
