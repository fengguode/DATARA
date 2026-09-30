# Product requirements

The founding P0 and P1 directions are preserved here with stable identifiers. System statements are derived drafts until their open contracts are resolved; recording a requirement does not imply implementation or validation.

| ID | Priority | Requirement | User outcome |
| --- | --- | --- | --- |
| PR01 | P0 | Supported source specification | Accept manually uploaded Garmin .fit files only through a published source specification. |
| PR02 | P0 | Persistent data home | Preserve original uploads and normalized history, with explicit duplicate and conflict handling. |
| PR03 | P0 | Deterministic preparation | Validate, normalize, calculate, and package skill inputs without AI. |
| PR04 | P0 | Baseline elemental skills | Offer a small evaluated Datara-created library with explicit inputs, methods, outputs, and versions. |
| PR05 | P0 | Input eligibility | Exclude skills whose required inputs are unavailable and explain the missing requirements. |
| PR06 | P0 | Customer model access | Use the customer's own API access for analysis; keep skills independent of model interfaces. |
| PR07 | P0 | Manual analysis execution | Execute selected eligible skills against a defined dataset and report failures explicitly. |
| PR08 | P0 | Traceable result history | Persist results with evidence, input references, skill version, model, and run date. |
| PR09 | P0 | Dashboard and output API | Present saved results through a predefined dashboard and authorized read-only API. |
| PR10 | P0 | User isolation | Isolate user files, credentials, and results across all access paths. |
| PR11 | P1 | Demand-based recommendations | Recommend only eligible marketplace combinations, prefer suitable owned skills, and explain demand coverage. |
| PR12 | P1 | Automatic routines | Support user-configured scheduled and upload-triggered analysis without silently changing selected skills or model. |
| PR13 | P1 | Comparison and feedback | Support user corrections and comparisons that disclose model and skill version changes. |

Canonical machine-readable records: [requirements registry](requirements-registry.json). Changes require an impact assessment of dependent system requirements, tasks, and verification cases. Preserve identifiers; retire rather than reuse them.
