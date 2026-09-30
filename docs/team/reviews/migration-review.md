# Agent-team migration review

Date: 2026-09-30 (Asia/Shanghai)

Tracking: [DATARA issue #17](https://github.com/fengguode/DATARA/issues/17), [control issue #8](https://github.com/fengguode/DATARA/issues/8)

Base: `main`; migration candidate: `1700ccf50cc80bb41001f04c89f236a8ae4885cd` on `setup/reusable-agent-team`

Scope: agent configuration, instructions, team workflow, roster, and knowledge files. No product PR/SR behavior was changed or tested.

## Independent Reviewer assignment and activation

The primary assigned a separate, read-only reviewer agent to compare `1700ccf` with `main`. The assignment required it to read `.codex/agents/reviewer.toml`, DATARA's instructions, relevant management records, team workflow, and saved knowledge, then report severity-ordered findings without edits or GitHub mutations. That separate agent run completed and returned a review. It manually read and followed the configured Reviewer instructions. This establishes an independent review, **not** automatic activation or sandbox enforcement of the repository's custom agent definition. The available agent orchestration did not load `.codex/agents/reviewer.toml` automatically; no native custom-agent activation result or execution URL was exposed. The Reviewer could not run TOML parsing because `python` was unavailable in its shell; the primary's separate bundled-Python check below covers syntax.

## Reviewer findings and disposition

| Severity | Finding and evidence | Disposition |
| --- | --- | --- |
| P2 | The coordinator for GitHub reporting was generic: `docs/team/roster.md` called it “primary agent” and `docs/team/workflow.md` assigned reconciliation to “the primary”; `.codex/config.toml` only contained model defaults. The workflow did not identify who held the coordination role or how handoff occurred. | Fixed in this branch: the roster names **Primary Coordinator (Codex)**; the workflow makes the initiating Codex primary agent accountable per issue until an explicit issue-recorded handoff, and requires meaningful GitHub updates and pending-update disclosure. |

The Reviewer found no other confirmed defect. Its read-through found DATARA product constraints, P0/P1 separation, and release gates preserved; all nine role files had matching saved-knowledge files; prior-project lessons were marked as process guidance and the six design skills as an inventory. It ran `git diff --check main...1700ccf` successfully. The primary checked the complete tracked and untracked diff after the review and made the bounded documentation repair above.

## Primary validation of the repaired candidate

The primary reran bundled Python 3 `tomllib` checks: all 10 TOML files parsed; all nine agent names, models, reasoning settings, and specified sandbox modes matched the source; all nine role knowledge files and team relative links existed; primary model settings matched; and the active `AGENTS.md`/`.codex` stale-reference scan passed. `git diff --check` passed (Git emitted only line-ending conversion warnings). `scripts/check_requirements.py` reported 13 product requirements, 31 system requirements, 8 tasks, and 20 planned cases with valid links. The registry checker tests management-link consistency only; it does not test DATARA product behavior. This review is not system verification, athlete validation, acceptance, or release readiness.

## Publication and open limits

The GitHub connector supports repository issues and PRs but exposes no Project item or field mutation. A browser attempt to reach the Project failed twice with `Unable to load browser request-header policy`. Project membership and Status/Lifecycle/Agent fields therefore remain unverified until another authorized client succeeds. Native custom-agent loading likewise remains unverified, despite the successful separate Reviewer run, and is tracked separately in [issue #18](https://github.com/fengguode/DATARA/issues/18). Record these limits in issue #17 and the draft PR; do not mark activation confirmed.
