# Open decisions and change management

## Requirement title decision (30 September 2026)

The founder requires all requirement and backlog titles to follow `[Type][area]content_of_title`, with one type (for example CUS, SR, Feature, Task, or bug) and one affected area (for example frontend, backend, database, or security). Priority belongs in its dedicated Project field or requirement metadata and must not appear in titles. See the [project title convention](README.md#requirement-and-backlog-title-convention). This changes presentation guidance; requirement identifiers, product obligations, priorities, and evidence states are not changed by the rule. Delivery is tracked in [issue #25](https://github.com/fengguode/DATARA/issues/25) and [pull request #24](https://github.com/fengguode/DATARA/pull/24).

## Requirement hierarchy decision (30 September 2026)

The founder defined Customer-User-Story (CUS) as the top level of all requirements. System requirements (SR) derive from CUS and cover applicable legal, engineering, running-environment, architecture, data-security, and other perspectives. This terminology and traceability change maps each former `PR01`–`PR13` identifier to `CUS01`–`CUS13` with the same number, priority, and existing scope. A system requirement may trace to multiple CUS records. The current SR draft has not been audited for completeness across those perspectives; adding or changing substantive obligations remains subject to the normal decision and evidence process. PR means pull request in current prose.

| ID | Decision needed | Package | Status |
| --- | --- | --- | --- |
| D01 | Approve official FIT evidence/version, accepted mappings and variants, limits, exact/tolerant conflict policy, and fixture provenance/redistribution | WP01 | Proposed options; open |
| D02 | Approve the elemental-skill shortlist, coverage/trend rules, evaluation rubric and per-connection release threshold | WP01 / WP03 | Proposed options; open |
| D03 | Choose capability-spike/one-provider or multi-provider connection sequencing and approve credential boundary, capabilities, retention and error mapping from official provider evidence | WP01 / WP04 | Proposed options; open |
| D04 | Approve the training-volume/readiness dashboard outcome, read-only resources, evidence representation, pagination and authorization details, or choose a reduced/different outcome | WP01 / WP05 | Proposed options; open |
| D05 | Application stack, deployment topology, and delivery estimates | WP01 | Open |
| D06 | Meaning of owned or saved skills in the free trial | WP07 | Open |
| D07 | Source rights and source-to-skill workflow | Later | Deferred |

For each resolution record: decision, rationale, alternatives, affected requirement IDs, date, and linked PR. Changes to agreed product scope or priorities are proposals until the founder accepts them. Routine derived engineering details may progress within scope. A change request must identify affected skills, data contracts, APIs, verification, and existing results before the baseline is updated.

Concrete options, impacts, and approval gates for D01–D05 are in the [WP01 requirements package](wp01-requirements-package.md). Nothing in that proposal records founder approval.
