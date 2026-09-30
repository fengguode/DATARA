# Datara cloud project setup

Target name: **DATARA**. Repository: **fengguode/DATARA**. Purpose: project management, product requirements, system requirements engineering, implementation task coordination, verification, and final validation within one Codex cloud project/environment.

## Creation status

Cloud environment creation is pending authenticated access. Repository configuration documents do not themselves create a Codex cloud environment, and a GitHub issue hub is not a GitHub Projects board.

## Setup specification

- Select only the DATARA repository and use main as the base branch.
- Prepare a runtime that can run Python standard-library management checks; choose application dependencies after WP01 resolves architecture.
- Keep network access limited to required package and service destinations. No model credentials are needed for initial requirement management.
- Run `python scripts/check_requirements.py` as the initial project check.
- Use controlled fixtures for cloud execution. Customer model credentials belong in approved secret handling, never repository files or task prompts.
- Reuse this single project environment; each task uses its own branch/workspace.

## First cloud task

Read AGENTS.md and docs/management/README.md. Work on WP01, linked from the management index. Draft the supported FIT source contract, input/output contracts, baseline skill shortlist, model connection shortlist, and dashboard outcome. Identify unresolved decisions with concrete options. Update system requirements and traceability; do not claim any unexecuted tests passed. Open a reviewable PR and summarize decisions needed before implementation. Do not begin WP02 until WP01 contracts are sufficiently defined.

## Ongoing task contract

Every task names its work package, requirements, dependencies, outputs, and acceptance evidence. Update the linked issue when blocked or ready for review. Link PRs and commit IDs in the management record. GitHub is the durable record; cloud chat history supplements it. Do not create a second project for system engineering or validation.

These are coding and management environments, not production hosting for the Datara product.
