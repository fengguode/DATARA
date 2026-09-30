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

Use one project backlog. Name the work package and affected PR/SR IDs. Respect dependencies. Use isolated task branches and reviewable PRs. Record decisions and traceability changes. Do not commit credentials, personal FIT telemetry, or runtime data to this public repository.

Run `python scripts/check_requirements.py` for registry changes. Execute relevant product checks once they exist; report actual results, not plans. Distinguish mocked tests, real model integration, system verification, and final user validation. Preserve historical results and record candidate commits in release evidence. Requirements must not be marked verified without evidence. Cloud environment setup is distinct from product deployment.

## Agent team

Read [the team workflow](docs/team/workflow.md) and the relevant saved knowledge in `docs/team/knowledge/` before team work. The primary agent coordinates assignments and integrates all changes. Delegate only bounded, independent work with an issue, scope, acceptance criteria, evidence request, and exclusive file ownership. Avoid concurrent edits to the same files. Role file restrictions are assignment rules; a `workspace-write` sandbox may technically allow broader edits, so the primary must inspect every tracked and untracked changed path before integration.

Use [the DATARA GitHub Project](https://github.com/users/fengguode/projects/3) as the shared task-status record. Report agent runtime status explicitly; it is not synchronized to GitHub automatically. Require independent technical review and evidence-backed QA appropriate to the change. Record actual checks and limitations, preserve candidate-specific release evidence, and keep Done, Verified, Accepted, and released distinct. The founder owns product decisions and final acceptance; release readiness requires the gates in `docs/management/validation-plan.md` and `docs/management/lifecycle-and-releases.md`.
