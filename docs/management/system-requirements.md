# System requirements engineering

Status: proposed derived baseline, 30 September 2026. These statements translate agreed product directions into verifiable system behavior. They do not select a technology stack. The [WP01 requirements package](wp01-requirements-package.md) proposes the open contracts; official FIT evidence, limits, interfaces, and quality thresholds require approval before a release baseline is frozen.

| ID | Parent | Priority | System requirement | Verification | Work package |
| --- | --- | --- | --- | --- | --- |
| SR01 | PR01 | P0 | The system shall classify every submitted file as accepted or rejected using the versioned source specification and return a reason for every rejection. | TC01 | WP01 |
| SR02 | PR01 | P0 | The source specification shall define supported records, timestamp interpretation, units, null values, required fields, and validation limits before import implementation is accepted. | TC01 | WP01 |
| SR03 | PR02 | P0 | The system shall preserve original file bytes with an integrity identifier and retain normalized records linked to their original source. | TC02 | WP02 |
| SR04 | PR02 | P0 | Re-importing the same accepted file for the same user shall not create a duplicate activity; conflict cases shall be surfaced and not silently overwrite history. | TC03 | WP02 |
| SR05 | PR03 | P0 | For the same source bytes, configuration, and preprocessing version, preparation shall produce semantically identical normalized records and metrics, excluding generated identifiers and processing timestamps. | TC04 | WP02 |
| SR06 | PR03 | P0 | Ingestion and preprocessing shall complete with model access disabled and shall make no inference requests. | TC04 | WP02 |
| SR07 | PR03 | P0 | Prepared skill inputs shall contain only the selected dataset and context required by the selected skill, with provenance for computed metrics. | TC05 | WP03 |
| SR08 | PR04 | P0 | Each published skill shall declare an immutable version, mandatory inputs, applicability rules, method, output schema, and evaluation cases. | TC06 | WP03 |
| SR09 | PR04 | P0 | Skill definitions shall not embed provider credentials or provider-specific endpoint and transport logic; such logic shall reside in model adapters. | TC06 | WP03 |
| SR10 | PR05 | P0 | The system shall evaluate eligibility deterministically for the selected dataset before execution, including mandatory fields, history coverage, and permitted quality limits specified by the skill. | TC07 | WP03 |
| SR11 | PR05 | P0 | An ineligible skill shall be unavailable for execution and shall identify unmet requirements without invoking a model. | TC07 | WP03 |
| SR12 | PR06 | P0 | Analysis requests shall use the user's explicitly selected supported model connection and shall never silently fall back to Datara-owned analysis credentials. | TC08 | WP04 |
| SR13 | PR06 | P0 | Credentials shall not appear in repository files, dashboard or API responses, or application logs; credential handling shall follow a documented access and protection design. | TC09 | WP04 |
| SR14 | PR07 | P0 | A manual analysis run shall record its dataset scope, selected skill versions, and model before execution and expose pending, running, succeeded, and failed states. | TC10 | WP04 |
| SR15 | PR07 | P0 | Timeouts, authentication failures, and malformed model responses shall result in explicit failure or invalid-result states; they shall not be persisted as successful assessments. | TC10 | WP04 |
| SR16 | PR08 | P0 | Each stored assessment shall reference the input snapshot or immutable source records, preprocessing version, skill version, model identifier, execution time, and supporting evidence. | TC11 | WP05 |
| SR17 | PR08 | P0 | A re-run shall create a new assessment without overwriting the previous one; observations, computed metrics, assessments, and recommendations shall remain distinguishable. | TC11 | WP05 |
| SR18 | PR09 | P0 | The predefined dashboard shall display data readiness, selected analysis scope, saved findings, evidence, and failures without requiring a new model call for viewing. | TC12 | WP05 |
| SR19 | PR09 | P0 | The read-only API shall return versioned structured records and results consistent with the dashboard and shall reject attempts to mutate data through its read-only routes. | TC13 | WP05 |
| SR20 | PR10 | P0 | Every upload, data query, analysis run, credential operation, and result query shall enforce user authorization. | TC14 | WP02 |
| SR21 | PR10 | P0 | One user shall not read or execute against another user's files, credentials, or results by changing identifiers in supported UI or API requests. | TC14 | WP05 |
| SR22 | PR11 | P1 | The recommendation model shall receive only deterministically eligible skill candidates and data-availability summaries rather than raw activity records. | TC16 | WP07 |
| SR23 | PR11 | P1 | Suggested combinations shall identify contributions, unmet portions of the demand, and ownership; suitability shall take precedence over ownership and a narrower demand shall require user choice. | TC16 | WP07 |
| SR24 | PR12 | P1 | A routine shall persist user-selected skills and model, dataset scope, trigger, and notification preference, and shall recheck eligibility before each run. | TC17 | WP07 |
| SR25 | PR12 | P1 | An upload-triggered routine shall process the completed batch once according to its configured scope rather than initiating one review per file; changing its skills or model shall require user selection. | TC17 | WP07 |
| SR26 | PR13 | P1 | Comparisons shall disclose relevant model and skill version differences; feedback shall not silently convert model assessments into observed facts. | TC18 | WP07 |
| SR27 | PR01 | P0 | The approved source contract shall identify the authoritative official FIT protocol/profile version and evidence used for every accepted variant, field mapping, unit conversion, timestamp rule, integrity rule, and fixture oracle; unverified variants shall be rejected as unsupported. | TC19 | WP01 |
| SR28 | PR03 | P0 | The skill input envelope shall be schema-versioned, deterministically canonicalized, bound to one immutable snapshot, and carry source or calculation provenance and data-quality metadata without credentials or out-of-scope records. | TC05, TC20 | WP03 |
| SR29 | PR04 | P0 | The skill output envelope shall distinguish observations, computed metrics, and assessments; require resolvable evidence for every finding; reject unapproved classifications or unresolved references; and prohibit P0 recommendation outputs. | TC06, TC20 | WP03 |
| SR30 | PR06 | P0 | Each supported model adapter shall accept the common provider-independent execution request and return normalized outcomes for responses and declared failure classes while keeping credentials and provider transport outside skill definitions. | TC08, TC10, TC20 | WP04 |
| SR31 | PR09 | P0 | The versioned output API shall expose only authorized read-only activity, readiness, run-history, and validated-result resources using stable error and pagination contracts, and the predefined dashboard shall derive its displayed saved values from the same contracts. | TC12, TC13, TC20 | WP05 |

Each system requirement traces to one product parent here. A work package may implement several requirements. Pull request reviews must list affected requirement IDs and verification evidence; modifications to public contracts need an explicit decision record.
