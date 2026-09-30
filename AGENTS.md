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
