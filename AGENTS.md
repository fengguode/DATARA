# Datara project instructions

Read docs/management/README.md, docs/project-brief-and-roadmap.md, and the relevant requirement records before work. The dated brainstorming record preserves rationale and superseded choices.

## Product constraints

- Source-first supported data with deterministic ingestion and preprocessing.
- Persistent history; dashboard/database outputs and read-only API at P0.
- Provider-independent elemental skills; customer-owned API access for analysis.
- Datara's own model is for P1 recommendations only.
- Deterministic eligibility before recommendation and execution; explain unsupported demands.
- Users select combinations and models. No silent provider fallback or routine changes.
- Commercial mechanisms and source-to-skill automation are deferred.

## Delivery discipline

Use the GitHub Project as the central shared backlog and authoritative status record. The local requirements registry is a synchronized machine-readable content and traceability mirror, not a second backlog. Name the work package and affected Customer-User-Story (CUS), Feature, and system requirement (SR) IDs. Respect dependencies. Use isolated task branches and reviewable pull requests. Record decisions and traceability changes. Do not commit credentials, personal FIT telemetry, or runtime data to this public repository.

Requirement and backlog titles must follow `[Type][area]content_of_title`, using a type such as `CUS`, `SR`, `Feature`, `Task`, or `bug` and an area such as `frontend`, `backend`, `database`, or `security`. Follow the [project title convention](docs/management/README.md#requirement-and-backlog-title-convention); keep priority in its dedicated field or metadata, never in the title.

Terminology: **PR means pull request only.** A Customer-User-Story (CUS) states the top-level customer or user need and outcome. Features group capability scope between CUS and SR without changing CUS outcomes. System requirements (SR) derive from CUS and cover every applicable perspective, including legal, engineering, running environments, architecture, and data security. Use CUS and SR IDs in traceability. See `docs/management/product-requirements.md` for the one-to-one mapping from historical identifiers.

Run `python scripts/check_requirements.py` for registry changes. The current checker validates the legacy CUS/SR/TK/WP/TC core; additive Feature, STK, and perspective-assessment links still require direct audit and independent QM/Reviewer review. Execute relevant product checks once they exist; report actual results, not plans. Distinguish mocked tests, real model integration, system verification, and final user validation. Preserve historical results and record candidate commits in release evidence. Requirements must not be marked verified without evidence. Cloud environment setup is distinct from product deployment.

## Agent team

Follow [pull request confirmation responsibilities](docs/team/pull-request-confirmation.md). The founder gives final confirmation for CUS-level changes; other pull requests use the dedicated role for their scope, with independent review and applicable evidence gates. Primary Coordinator — Yi Tang records the final confirmer, role/name labels, commit attribution, and Project-management changes.

Use [the named attribution protocol](docs/team/attribution.md) for assignments, comments, commits, and pull request contribution tables. Identify each agent by role and configured name, link actual runtime evidence when available, and distinguish contributor, integrator, and authenticated publisher. The primary maintains the Project Agent field. Preserve existing permission limits and historical identities; do not infer a contribution from a role label alone.

Read [the team workflow](docs/team/workflow.md) and the relevant saved knowledge in `docs/team/knowledge/` before team work. The primary agent coordinates assignments and integrates all changes. Delegate only bounded, independent work with an issue, scope, acceptance criteria, evidence request, and exclusive file ownership. Avoid concurrent edits to the same files. Role file restrictions are assignment rules; a `workspace-write` sandbox may technically allow broader edits, so the primary must inspect every tracked and untracked changed path before integration.

Use [the DATARA GitHub Project](https://github.com/users/fengguode/projects/3) as the shared task-status record. Report agent runtime status explicitly; it is not synchronized to GitHub automatically. Require independent technical review and evidence-backed QA appropriate to the change. Record actual checks and limitations, preserve candidate-specific release evidence, and keep Done, Verified, Accepted, and released distinct. The founder owns product decisions and final acceptance; release readiness requires the gates in `docs/management/validation-plan.md` and `docs/management/lifecycle-and-releases.md`.
