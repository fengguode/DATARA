# Decisions and change management

## Team confirmation decision (30 September 2026)

After nine-role consultation in [issue #26](https://github.com/fengguode/DATARA/issues/26), the founder approved the proposed confirmation flow: founder final confirmation for CUS-level changes, dedicated role confirmation for other scopes, independent nonauthor review, applicable cross-domain evidence gates, and SHA-specific confirmation refreshed after relevant changes. The founder named the Primary Coordinator persona **Yi Tang** and required role/name attribution on GitHub for commits and Project-management changes. The [confirmation policy](../team/pull-request-confirmation.md) records stage ownership and scope mapping. This approval adopts the process; it does not accept a product candidate, approve open product decisions, or authorize merge/deployment.

## Requirement title decision (30 September 2026)

The founder requires all requirement and backlog titles to follow `[Type][area]content_of_title`, with one type (for example CUS, SR, Feature, Task, or bug) and one affected area (for example frontend, backend, database, or security). Priority belongs in its dedicated Project field or requirement metadata and must not appear in titles. See the [project title convention](README.md#requirement-and-backlog-title-convention). This changes presentation guidance; requirement identifiers, product obligations, priorities, and evidence states are not changed by the rule. Delivery is tracked in [issue #25](https://github.com/fengguode/DATARA/issues/25) and [pull request #24](https://github.com/fengguode/DATARA/pull/24).

## Requirement hierarchy decision (30 September 2026)

The founder defined Customer-User-Story (CUS) as the top level of all requirements. System requirements (SR) derive from CUS and cover applicable legal, engineering, running-environment, architecture, data-security, and other perspectives. This terminology and traceability change maps each former `PR01`–`PR13` identifier to `CUS01`–`CUS13` with the same number, priority, and existing scope. A system requirement may trace to multiple CUS records. The current SR draft has not been audited for completeness across those perspectives; adding or changing substantive obligations remains subject to the normal decision and evidence process. PR means pull request in current prose.

| ID | Decision needed | Package | Status |
| --- | --- | --- | --- |
| D01 | Official FIT version, mappings/variants, limits, conflicts and fixture provenance | WP01 | SDK and intake policy selected under founder direction/delegation; source matrix, rights and conformance evidence pending |
| D02 | Elemental skills, coverage/trend rules and evaluation thresholds | WP01 / WP03 | Three skills and descriptive/evaluation policy selected under delegation; schemas, fixture/rubric review and live evaluation pending |
| D03 | Providers, credential boundary, capabilities, retention and failures | WP01 / WP04 | OpenAI and DeepSeek founder-selected; key/run policy selected under delegation; exact models, capability/retention/access evidence pending |
| D04 | Recorded-volume/data-readiness dashboard and authorized read API | WP01 / WP05 | Outcome, resources and pagination/access/retention direction selected under delegation; exact schemas, UI/accessibility and operational evidence pending |
| D05 | Stack, reference topology, operations and estimates | WP01 | Django/Python, PostgreSQL and local browser pilot in China selected; dependency pins, runtime/operator setup/recovery evidence and measured estimates pending |
| D06 | Meaning of owned or saved skills in the free trial | WP07 | Open |
| D07 | Source rights and source-to-skill workflow | Later | Deferred |

For each resolution record: decision, rationale, alternatives, affected requirement IDs, date, and linked PR. Changes to agreed product scope or priorities are proposals until the founder accepts them. Routine derived engineering details may progress within scope. A change request must identify affected skills, data contracts, APIs, verification, and existing results before the baseline is updated.

Concrete options, impacts, and approval gates for D01–D05 are in the [WP01 requirements package](wp01-requirements-package.md). Nothing in that proposal records founder approval.

## D01–D05 delegated selections (1 October 2026)

The founder selected FIT SDK 21.217.0, delegated remaining D01–D05 choice work to Yi Tang with Yu Wang, then explicitly selected OpenAI and DeepSeek as the first providers. The [dated decision record](p0-decision-baseline-2026-10-01.md) contains selected options, rationale, affected CUS/SR/tasks, official sources, remaining evidence and founder support inputs. Its authority and GitHub links are recorded there.

Selected direction is distinct from completed contracts or satisfied G0. Earlier WP01/design packages remain historical proposals; their open-option wording is superseded only by explicit selections in the dated record. Preserve historical results. No SR/case, product implementation, founder athlete acceptance, merge or deployment is asserted by these selections.

Pilot clarification: the founder selected personal use in China, first running locally with a web UI. See [the live clarification](https://github.com/fengguode/DATARA/issues/1#issuecomment-5924895687) and the dated baseline. Runtime/setup and both provider capability gates remain pending.
