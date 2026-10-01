# DATARA product overview

**Product direction and delivery status — 1 October 2026**

## What DATARA is

DATARA is being designed as a persistent personal data home that turns supported data into useful outcomes through reusable expertise. The first intended audience is athletes who want to understand training history and use analysis on their own terms.

The planned first release centers on supported Garmin FIT activity files. DATARA's conventional software will validate and prepare those files. Users will choose from eligible analysis skills, select a supported model connection using their own API access, and run an analysis manually. DATARA will retain result history with evidence and provide a predefined dashboard and read-only API for saved information.

## What exists today

The product is in requirements and delivery planning. The P0 implementation plan is merged and reviewed as a task sequence and proposed readiness plan, but it is not product software; product decisions remain open. No product feature is currently evidenced as implemented or released in the reviewed baseline. Product verification cases and the complete athlete journey remain not run, and there is no founder acceptance or product release.

The current P0 task sequence and proposed readiness gates are recorded in the merged [implementation plan](../management/p0-implementation-plan.md). The [GitHub Project](https://github.com/users/fengguode/projects/3) is the live task-status source; some visitors may need access or a GitHub sign-in. If the board is unavailable, the repository [issue list](https://github.com/fengguode/DATARA/issues) remains the public work-discussion path. Roadmap dates are not committed.

## Intended first-release workflow

1. Upload supported activity files.
2. Review what was accepted, rejected, duplicated, or needs attention.
3. Inspect retained training history and data readiness.
4. Choose an analysis (called a skill in the project records) that fits your selected data; the system should explain missing inputs.
5. Select a supported model connection using your own provider account and API access. The provider may require a separate account or charge under its terms.
6. Run the analysis and review findings with their evidence.
7. Return to saved results later or retrieve them through an authorized read-only API.

This workflow is a product goal. It is not yet available for customer use. Supported file variants, the exact skill set, model connections, dashboard details, and output API contract remain subject to open decisions and implementation.

## Data and model expectations

The product direction requires original uploads and normalized history to be retained with traceable relationships. Data preparation is intended to be deterministic and must not call a model. Access to files, credentials, and results must be isolated by user. Product documentation does not promise a specific retention period, encryption design, hosting region, certification, or legal compliance until those details are approved and evidenced.

For analysis, the user selects a supported model connection and supplies their own provider account/API access. The model provider may require account setup and may charge separately under its terms; review those terms before use. DATARA's own model is reserved for P1 recommendations. The intended system will not silently switch providers or use DATARA-owned analysis credentials. Model providers may have their own data-handling terms. Exact credential storage, supported providers, and retention boundaries remain open.

## Scope boundaries

The first milestone is P0: source specification, persistent data, deterministic preparation, evaluated baseline skills, deterministic eligibility, customer-selected model access, manual analysis, result history, a predefined dashboard, authorized read-only output API, and user isolation.

Later P1 work includes skill recommendations, scheduled or upload-triggered routines, feedback, and comparisons. Commercial mechanisms, source-to-skill automation, expert creator tooling, and additional data sources or domains are deferred. P1 or deferred plans are not current availability.

## Feedback and participation

The currently documented feedback path is the repository [issue tracker](https://github.com/fengguode/DATARA/issues). Submitting an issue requires a GitHub account and permission to create repository issues; no separate customer contact channel has been approved yet. Contributors can start with a focused issue and follow the [team workflow](../team/workflow.md). The shared [project board](https://github.com/users/fengguode/projects/3) shows delivery status and may require access. Feedback informs review; a material change to customer outcomes or commitments requires founder approval.

This overview is a draft for review. External publication requires the project's review and approval process.
