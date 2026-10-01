# Read-only evidence audit

Status: completed evidence review; this is not an approval or verification report.
Assigned role: Explorer (Wang Licun). Runtime identity: `/root/evidence_audit`.
Scope: WP01/WP04/WP05/WP06; CUS01, CUS06, CUS09, CUS10; SR01–SR02, SR12–SR13, SR19–SR21, SR27, SR30–SR31; D01/D03/D04/D05.

## Repository evidence

- The [project brief](../project-brief-and-roadmap.md) confirms manual Garmin `.fit` upload, deterministic preprocessing, customer-owned model access, persistent results, dashboard, authorized read-only API and user isolation in P0. Recommendations and routines are P1.
- The CUS layer has ten P0 stories and three P1 stories in [product requirements](../management/product-requirements.md). The [SR draft](../management/system-requirements.md) says it has not established completeness across applicable legal, engineering, runtime, architecture and security perspectives.
- The [WP01 package](../management/wp01-requirements-package.md) proposes data records, FIT behavior, skill envelopes, a provider adapter and API routes; its status is explicitly proposed, not approved or verified.
- The [validation plan](../management/validation-plan.md) says product checks and final user validation are not run. The repository has no application source, app configuration, or product test suite, so there is no current behavior to validate.
- The existing worktree has unresolved literal conflict markers in management documents including [README](../management/README.md), [system requirements](../management/system-requirements.md), [WP01 package](../management/wp01-requirements-package.md), and [traceability](../management/traceability.md). The canonical registry is also unparseable in the current worktree. Its check was not run. These files are deliberately preserved by this design assignment.

## Official evidence consulted

- [Garmin FIT Protocol](https://developer.garmin.com/fit/protocol/) describes the FIT structure, extensible message/profile model and SDK. [FIT File Types](https://developer.garmin.com/fit/file-types/) describes FIT file categories. These pages support pinning an official protocol/profile artifact; they do not establish DATARA's accepted field mappings, ranges, limits, fixture rights or conflict key.
- [OpenAI API data controls](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint) describes endpoint-specific storage and retention behavior. It demonstrates that storage behavior can vary by endpoint and setting; no OpenAI provider has been selected for DATARA.
- [Google Gemini API key security](https://ai.google.dev/gemini-api/docs/api-key) describes server-side secret handling and key protection. [Structured output](https://ai.google.dev/gemini-api/docs/structured-output) describes provider-specific schema support. These are provider examples only and do not decide D03.

## D01–D05 assessment

| Decision | Status | Evidence needed before closing |
|---|---|---|
| D01 FIT source contract | Open. Existing normalized semantics and exact logical key are proposals. | Pin official protocol/profile/SDK version; matrix every accepted variant, message/field mapping, conversion, timestamp and integrity rule; independent fixture oracle; numerical/resource limits; conflict semantics; documented usage/redistribution rights. |
| D02 skills and evaluation | Open. Activity summary, volume trend and consistency candidates are proposals. | Founder selects scope and meaning; define coverage/trend thresholds and blind evaluation fixtures/rubric; establish per-model release threshold; explicitly approve any unsupported-claim/safety rule. |
| D03 customer model integration | Open. Provider count, API feature subset, secret boundary, retention and failure normalization are undecided. | Select a provider strategy after documented capability spike and official docs review; approve what customer data is sent, credential lifecycle/storage, endpoint retention implications, timeout/rate-limit/error mapping, same-provider retry rules; retain separate mock and live evidence. |
| D04 dashboard/API | Open. Proposed `/api/v1` surface and dashboard outcome await decision. | Founder confirms outcome and reduced-scope alternative; approve endpoints, response schemas, auth, evidence references, pagination, error semantics, rate limits and retention. |
| D05 stack and deployment | Open. No current source/config provides evidence for a stack. | Decide deployment owner/environment, identity mechanism, storage and secret services, network boundary, backup/recovery target, observability, upgrade/rollback and operational ownership after D01–D04 contracts. Ground estimates in implementation spikes. |

## Cross-cutting gaps and careful limits

The founding record says that assuming skills are free/license-free for planning does not establish rights to third-party source material. A permitted-use and provenance record is needed for official source materials and any sample fixture before redistribution. No legal jurisdiction or compliance regime can be named from current records; product owner must identify intended operating jurisdictions and obtain qualified review of applicable privacy, consumer, data-protection and contract obligations before release. This is a question to resolve, not a legal conclusion.

Additional missing derived requirements likely include retention/deletion, backup restoration, encryption/key access boundaries, audit-event scope, operational monitoring/incident response, resource exhaustion limits, accessibility acceptance and deployment/rollback. These are coverage candidates, not approved new SRs. The System Architect should derive them, mark applicability with rationale, and synchronize the canonical registry only after its existing merge markers are reconciled. No current decision or evidence supports a specific cloud, database, jurisdiction, provider, or retention duration.

## Fact / inference / proposal

- **Fact:** The repository records P0 direction, proposed contracts, open decisions, and `Not run` product cases.
- **Inference:** In the absence of source code/configuration/tests, implementation behavior and runtime security properties cannot be assessed.
- **Proposal:** Keep D01–D05 open until the listed evidence and approvals are recorded. This matches the current decision register and WP01 gate.

No product, live-model, system, browser, deployment, or athlete validation was performed during this read-only audit.
