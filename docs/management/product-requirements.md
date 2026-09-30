# Customer-User-Stories (CUS)

CUS is the top level of DATARA requirements: each record states a customer or user need and the intended outcome. System requirements (SR) derive from one or more CUS records and express verifiable obligations across applicable perspectives, including legal, engineering, running environments, architecture, and data security. The existing P0 and P1 scope and priorities are preserved. The `CUS01`–`CUS13` identifiers replace the former `PR01`–`PR13` identifiers one-to-one; for every `NN`, `PRNN` maps to `CUSNN`. Historical citations and GitHub records may retain the former IDs. **PR means pull request only** in current prose. SR statements are derived drafts until open contracts are resolved; recording a requirement does not imply implementation or validation.

| ID | Priority | Customer or user story | Existing outcome and scope |
| --- | --- | --- | --- |
| CUS01 | P0 | As an athlete, I want to upload supported activity files so that I can rely on the imported data. | Accept manually uploaded Garmin .fit files only through a published source specification. |
| CUS02 | P0 | As an athlete, I want my uploads and training history retained so that I can return to earlier activities. | Preserve original uploads and normalized history, with explicit duplicate and conflict handling. |
| CUS03 | P0 | As an athlete, I want activity data prepared consistently so that analyses are repeatable. | Validate, normalize, calculate, and package skill inputs without AI. |
| CUS04 | P0 | As an athlete, I want evaluated expertise options so that I can choose a useful analysis. | Offer a small evaluated Datara-created library with explicit inputs, methods, outputs, and versions. |
| CUS05 | P0 | As an athlete, I want unavailable analyses explained so that I know which inputs are missing. | Exclude skills whose required inputs are unavailable and explain the missing requirements. |
| CUS06 | P0 | As an athlete, I want to use my chosen model account so that I control access for my analyses. | Use the customer's own API access for analysis; keep skills independent of model interfaces. |
| CUS07 | P0 | As an athlete, I want to run selected analyses and see failures clearly so that I can trust the outcomes. | Execute selected eligible skills against a defined dataset and report failures explicitly. |
| CUS08 | P0 | As an athlete, I want to revisit analyses with their evidence so that I can understand my history. | Persist results with evidence, input references, skill version, model, and run date. |
| CUS09 | P0 | As an athlete, I want saved results in a dashboard and output API so that I can use them elsewhere. | Present saved results through a predefined dashboard and authorized read-only API. |
| CUS10 | P0 | As a customer, I want my data and credentials isolated so that other users cannot access them. | Isolate user files, credentials, and results across all access paths. |
| CUS11 | P1 | As an athlete, I want suitable skill recommendations so that I can address my demand with available data. | Recommend only eligible marketplace combinations, prefer suitable owned skills, and explain demand coverage. |
| CUS12 | P1 | As an athlete, I want recurring analysis under my chosen settings so that I receive updates without manual runs. | Support user-configured scheduled and upload-triggered analysis without silently changing selected skills or model. |
| CUS13 | P1 | As an athlete, I want comparisons and corrections so that I can understand changes and refine context. | Support user corrections and comparisons that disclose model and skill version changes. |

Canonical machine-readable records: [requirements registry](requirements-registry.json). Changes require an impact assessment of dependent system requirements, tasks, and verification cases. Preserve identifiers; retire rather than reuse them.
