# Named agent assignments and contributions

Use this protocol for new work under the [DATARA Project](https://github.com/users/fengguode/projects/3). It implements the founder-approved attribution agreement tracked in [issue #23](https://github.com/fengguode/DATARA/issues/23). The Primary Coordinator maintains the public activity record and preserves the evidence supplied by each contributing agent.

## Identity and responsibility

Use the roster's role and configured name together, published in the [identity label format](#identity-label-format), for example **Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)**. These are AI role personas, not evidence that a person with that name participated. Distinguish the assigned persona, actual runtime agent ID or execution link, contributor, integrator, and authenticated GitHub publisher. If a role definition or effective settings were not observably loaded, say so; a named assignment does not prove native activation.

The Project's single-select **Agent** field identifies the currently responsible role. Use the roster's `Role — Name` options, including `Primary Coordinator — Yi Tang`. It records ownership, not who is currently running or every contributor, so it does not carry the model or harness; those are recorded in the assignment and handoff `Model used:` value instead. Give independent bounded assignments separate linked issues or sub-issues when they need separate ownership or status. An issue-recorded handoff updates this field and names the successor. Leave unassigned work unset rather than inferring an agent from its topic. Multiple contributors appear in the assignment record and contribution table.

GitHub's authenticated account remains the publisher of comments and pushes. The comment heading names the contributing agent and whether the primary relayed its report. Git author and committer identities remain accurate; changing a commit message does not create a GitHub account or independent runtime identity. Separate bot identities would require a separately authorized account/App setup. This agreement does not create them or grant agents publishing rights.

## Identity label format

Publish an agent identity in the canonical form defined in the [Code of Conduct](../../CODE_OF_CONDUCT.md#agent-identity-labels), as `<Role> — <Configured name>_<model>-<variant>_<Harness> (AI agent)`. The persona, the model used, and the harness are visible in one label. That section defines the field rules, the model-evidence ladder, the applicable and non-applicable surfaces, and the limit that the label is a display string rather than a machine key. It supplements this agreement and does not replace it.

Worked labels for every roster role:

| Role | Configured name | Codex label | OpenCode label |
| --- | --- | --- | --- |
| Primary Coordinator | Yi Tang | `Primary Coordinator — Yi Tang_gpt-6-luna-high_Codex (AI agent)` | `Primary Coordinator — Yi Tang_space-bunny-free-max_OpenCode (AI agent)` |
| Product Manager | Yu Wang | `Product Manager — Yu Wang_gpt-6-luna-high_Codex (AI agent)` | `Product Manager — Yu Wang_space-bunny-free-max_OpenCode (AI agent)` |
| System Architect | Feng Guo | `System Architect — Feng Guo_gpt-6-luna-high_Codex (AI agent)` | `System Architect — Feng Guo_space-bunny-free-max_OpenCode (AI agent)` |
| Explorer | Wang Licun | `Explorer — Wang Licun_gpt-6-luna-high_Codex (AI agent)` | `Explorer — Wang Licun_space-bunny-free-max_OpenCode (AI agent)` |
| UI Designer | Wu Yunzhou | `UI Designer — Wu Yunzhou_gpt-6-luna-high_Codex (AI agent)` | `UI Designer — Wu Yunzhou_space-bunny-free-max_OpenCode (AI agent)` |
| Worker | Torsten Maier | `Worker — Torsten Maier_gpt-6-luna-high_Codex (AI agent)` | `Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)` |
| Reviewer | Dennis Windmaier | `Reviewer — Dennis Windmaier_gpt-6-luna-high_Codex (AI agent)` | `Reviewer — Dennis Windmaier_space-bunny-free-max_OpenCode (AI agent)` |
| User Tester | Abt Hermann | `User Tester — Abt Hermann_gpt-6-luna-high_Codex (AI agent)` | `User Tester — Abt Hermann_space-bunny-free-max_OpenCode (AI agent)` |
| Quality Manager | Wang Xiaofeng | `Quality Manager — Wang Xiaofeng_gpt-6-luna-high_Codex (AI agent)` | `Quality Manager — Wang Xiaofeng_space-bunny-free-max_OpenCode (AI agent)` |
| Release Manager | Wang Bingshan | `Release Manager — Wang Bingshan_gpt-6-luna-high_Codex (AI agent)` | `Release Manager — Wang Bingshan_space-bunny-free-max_OpenCode (AI agent)` |
| Controller | Nils Traeger | `Controller — Nils Traeger_gpt-6-luna-high_Codex (AI agent)` | `Controller — Nils Traeger_space-bunny-free-max_OpenCode (AI agent)` |

The Codex model tokens are the configured values in `.codex/agents/*.toml`, which are tracked. `.codex/config.toml` also carries `model` and `model_reasoning_effort` but has no `developer_instructions`, so **the eleventh roster role, Primary Coordinator — Yi Tang, has no tracked Codex role definition instructing a label**; its Codex label in the table above derives from the coordinator configuration and is not emitted by a role file. There is no tracked OpenCode role definition in this baseline either, so an OpenCode run's `Model used:` value is self-reported by that run and has no baseline provenance; it is not verifiable from a fresh clone until such a definition is tracked. Neither case proves that a role was natively loaded. A run that cannot observe its own model publishes `model-unconfirmed`, and one that cannot observe its runtime publishes `harness-unconfirmed`.

## Assignment record

Before delegation, record the following in the linked issue. The primary owns integration; the assignee owns only the named files for the assignment. Include a visible work-start update and subsequent progress, blocker, review, and completion updates as appropriate.

```text
Assigned agent: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
Coordinator: Primary Coordinator — Yi Tang_gpt-6-luna-high_Codex (AI agent)
Assignment: #<issue> / <bounded assignment ID>
Work package / CUS / SR: <IDs, or no product scope changes>
Scope and exclusive files: <outcome and exact paths>
Dependencies: <issues and decisions>
Acceptance criteria: <observable conditions>
Evidence requested: <checks, files, and findings>
Branch / pull request: <links, or pending>
Runtime agent ID / execution: <actual ID/link, or unavailable>
Runtime state: <assigned, running, blocked, completed, interrupted>
Model used: model=<provider/model-id> variant=<token> harness=<Harness>
Configuration loading: <observed evidence, or unconfirmed>
```

An agent returns its actual runtime identifier when available, owned changed paths, results, proposed contribution boundaries, validation evidence, and unresolved questions. Read-only agents return findings and reports without editing, committing, or publishing. The primary captures this handoff before integration and compares every tracked and untracked changed path with the assignment.

## Activity comment

Prefix each issue or pull request comment with the role/name that produced the outcome. A coordinator's own update names the coordinator; a relayed report names both its source and publisher. Only attribute work to an agent when a real run or evidenced handoff supports the claim. Explicitly label examples, planned assignments, and unavailable execution links.

```text
Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent) · Implementation completed
Published by: Primary Coordinator — Yi Tang_gpt-6-luna-high_Codex (AI agent), relaying the Worker's report
Assignment: #<issue> / <assignment ID>
Runtime agent ID / execution: <actual ID/link, or unavailable>
Model used: model=<provider/model-id> variant=<token> harness=<Harness>
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

Implemented-by: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
Integrated-by: Primary Coordinator — Yi Tang_gpt-6-luna-high_Codex (AI agent)
Assignment: #<issue> / <assignment ID>
Work-package-CUS-SR: <IDs, or no product scope changes>
Agent-run: <actual ID/link, or unavailable>
Model-used: model=<provider/model-id> variant=<token> harness=<Harness>
```

Two Git constraints apply, both verified with `git interpret-trailers --parse`:

- A trailer key must match `[A-Za-z0-9-]+`. A key containing spaces or slashes, such as `Work package / CUS / SR:`, makes Git discard the **entire** trailer block rather than that one line. Use a hyphenated key.
- The trailer block must be the last paragraph and must be preceded by a non-trailer paragraph. A commit message consisting only of trailers is not parsed at all, so keep the summary and body above the block.

Use `Contributed-by` for documentation or other non-implementation contributions. Use `Implemented-by` for actual implementation. A reviewer who supplies findings is recorded in the review table/comment, not automatically as an implementation author. These are searchable metadata trailers, not signatures or GitHub account attribution. GitHub `Co-authored-by` is reserved for real account-linked attribution with the contributor's authorized email; never invent or borrow a person's address. Preserve historical commit identities and comments. Any retrospective contribution summary must cite existing evidence and label unavailable attribution rather than rewriting history.

## Pull request contribution table

Include this table in the pull request body. Link each contribution to its specific commit/diff, comment or report, and validation. A review-only contribution may have no commit; use the reviewed commit plus the review evidence instead. When squashing or rebasing, preserve the contribution table and trailers and update the links to the resulting commits.

| Agent (AI role) | Assignment / runtime | Contribution and files | Commit or reviewed commit | Comment / evidence | Integrator / publisher |
| --- | --- | --- | --- | --- | --- |
| <Role> — <Configured name>_<model>-<variant>_<Harness> (AI agent)> | <issue, run ID/link or unavailable> | <specific changes or review findings> | <linked SHA/diff> | <links and actual checks> | <Role> — <Configured name>_<model>-<variant>_<Harness> (AI agent)> and <authenticated account> |

## Reporting and audit

The coordinator uses the authorized GitHub CLI or connector to publish updates and set Project fields, then reads them back. Project changes and runtime reports are explicit; there is no automatic synchronization with agent execution. If publishing fails, save the pending comment under `docs/team/pending-updates/<issue>-<assignment>.md`, report the exact failure and out-of-sync state, and publish/reconcile it after access recovers. Keep credentials and raw internal reasoning out of all records.

## Identity label check

Run `python -X utf8 scripts/check_identity_labels.py` after changing any record that publishes an agent identity, and before opening a pull request that adds or edits one. Exit status 0 means no defect was found; 1 means at least one short-form or wrong-dash label is live, or a branch trailer is not in the canonical form.

The check reports which occurrences are preserved dated records and why, and refuses to report results at all if its own patterns do not behave or its finding lists are inconsistent. It scans tracked Markdown **and tracked role definitions** (`.md` and `.toml`), plus the attribution trailers on this branch relative to a base ref. It does not scan the requirements registry, does not inspect other branches or `main`, and validates label text only: it does not prove that a role was natively loaded, that a run occurred, or that any product behavior is verified. When it cannot resolve a base ref, or the range is empty, it says so rather than reporting a pass.

Declared limits of what the check does **not** enforce, so a green run is not over-read: it does not verify the mandatory ` (AI agent)` suffix is present, that there is exactly one space on each side of the separator, that a variant is present rather than omitted, that a harness name is one of the two known values, or that a configured name has at most two words. Those are documented rules the check does not yet test. Untracked Markdown is not scanned at all, so a new unpublished record can carry a non-conforming identity.

On a non-UTF-8 locale `-X utf8` is required, for the same reason it is required by `scripts/check_requirements.py`.

Independent review and Quality Manager audits check that assignment identity, owned files, actual run evidence, commits, review comments, and Project ownership agree. Report missing evidence rather than attributing a role because its name appears in a template. These process checks do not prove product behavior, native custom-agent activation, acceptance, or release readiness.
