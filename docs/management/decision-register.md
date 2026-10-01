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
| D06 | Meaning of owned or saved skills in the free trial | WP07 | **Closed for P0 (1 October 2026):** P0 has no ownership, purchase, saving, or authoring concept; all three baseline skills are Datara-created, free, and available when eligible. The substantive marketplace question remains open and is deferred to WP07 |
| D07 | Source rights and source-to-skill workflow | Later | Deferred |

For each resolution record: decision, rationale, alternatives, affected requirement IDs, date, and linked PR. Changes to agreed product scope or priorities are proposals until the founder accepts them. Routine derived engineering details may progress within scope. A change request must identify affected skills, data contracts, APIs, verification, and existing results before the baseline is updated.

Concrete options, impacts, and approval gates for D01–D05 are in the [WP01 requirements package](wp01-requirements-package.md). Nothing in that proposal records founder approval.

## G0 replacement for Milestone A (1 October 2026)

The founder authorised a G0 replacement under the Code of Conduct rule that coding requires G0 "or its approved replacement", which had never been pulled. The round table's Architect, Product Manager, and Controller reached the same conclusion independently: the binding constraint is **decision closure rather than decision absence**. The operative contracts largely exist in the dated decision baseline, while approximately 95 individually gated subtasks stand between the project and its first line of code, and the TK02 gate cannot close as scheduled because all eight of its children are written to forbid selecting a behaviour while G0 requires approved contracts.

**Authorised scope — Milestone A.** Source acceptance per D01; immutable original storage with SHA-256; exact-duplicate idempotence and logical-tuple quarantine; deterministic normalisation of the four P0 required inputs with no imputation; a deterministic, pure eligibility function that explains unmet requirements and makes no model call; saved history with a read surface; two-identity isolation; and a read-only API returning the same saved values as the page. Milestone A is authorised to proceed to implementation **without G0**.

**Not waived, and no criterion waived by silence.** G0 is defined with six criteria at `docs/management/p0-implementation-plan.md:34-39`. Each is dispositioned individually:

| # | G0 criterion | Status for Milestone A |
| --- | --- | --- |
| 1 | D01 protocol/profile/decoder evidence, supported matrix, resource limits, conflict policy | Partially substituted. **Still unmet: fixture origin, terms, hashes, intended oracles, rights and unknowns.** Accepted risk |
| 2 | D02 shortlist, eligibility/coverage/trend rules, rubric and thresholds | Partially substituted. **Still unmet: evaluation rubric anchors and live evaluation.** Accepted risk |
| 3 | D03 capability, credential, retention, safe errors | **Not waived.** Not needed for Milestone A, which makes no provider call |
| 4 | D04 dashboard outcome, read-only resource/evidence/pagination/access behaviour | Partially substituted. **Still unmet: exact schemas, pagination, accessibility scope.** Accepted risk |
| 5 | D05 stack and topology, platform/browser/accessibility scope, operational ownership, pinned install/run/test commands | Stack and topology substituted. **Still unmet: operational ownership.** Pinned install/run/test commands are **added to Milestone A scope** and must exist before any Milestone A result is offered as evidence |
| 6 | TK02 completion and a first-coding-assignment specification | Substituted **for Milestone A only**. A bounded assignment must still name concrete paths, the fixture, command and environment identity, acceptance cases, owner, and an independent reviewer. **TK02 itself does not close** |

G0 continues to gate, unchanged: provider and model integration, skill execution, the TC15 athlete journey, and the release gate. Also unchanged and not tradeable: user isolation, immutable originals, determinism, provenance on every number, the no-silent-fallback rule, rights and privacy handling, and the release gate.

The founder accepts that Milestone A proceeds as **accepted risk** while D01 fixture provenance and rights, D02 evaluation anchors, D04 exact schemas and accessibility scope, and D05 operational ownership remain unmet. That acceptance is bounded to Milestone A, is not a precedent for widening the replacement, and no G0 criterion is treated as satisfied by silence.

**Binding architectural condition.** Milestone A must create only `Import → SourceObject → Activity/Session → Metric/QualityFinding → Snapshot`, and must **not** create `Run`, `Assessment`, or any "latest result" column. SR14 currently specifies a single run, and encoding that shape into persisted history would make multi-skill support a migration of history, colliding with the append-only rule and with the selected deletion-ledger and reapply-on-restore semantics. The absence of those entities is the contract.

**Language discipline.** Milestone A is **not** the P0 first milestone, **not** a first usable release, and **not** an MVP. It is a trust outcome. Nothing produced under it may be described as Done, Verified, Accepted, or released. The first customer-recognisable utility outcome remains the first live baseline-skill run on the athlete's own model, retrievable unchanged from both dashboard and API.

**Evidence basis, and its limits.** A spike ran the pinned `garmin-fit-sdk` **21.217.0** (tag `production/release/21.217.0-0-g248b1c46`) against one real founder-supplied Garmin Connect export. The decode completed with CRC verification enabled, yielding 40 message definitions, 3,880 record messages, and **zero** compressed-timestamp definitions. The file is private and local, is excluded from the repository, and **no hash of it is recorded here or published**, pending the separate founder privacy decision. The spike is an observation, not TC01 or TC19 evidence, and not conformance evidence: a single successful decode proves neither mapping correctness nor coverage of the supported population.

**The compressed-timestamp blocker remains open and is not resolved by that spike.** `docs/p0-design/fit-support-matrix.md:58` records that the pinned decoder explicitly rejects compressed timestamp records, and the SDK source confirms the path is unreachable in 21.217.0. The spike shows the founder's current single-activity export does not exercise that path; it does not show that no file in the supported population does. The D01 engine and coverage decision therefore remains open, and D01 fixture provenance, terms, hashes, intended oracles, and rights remain unmet, as recorded above.

Per the dated baseline, local import, preparation, and saved-history viewing require no provider call, so Milestone A is immune to the open provider-reachability question.

This decision authorises one bounded implementation increment to begin. It approves no product candidate, accepts no requirement, authorises no release, and changes no CUS, SR, priority, contract, or evidence state. The founder's authorisation is recorded in [discussion #296](https://github.com/fengguode/DATARA/discussions/296) on 1 October 2026, together with the System Architect's binding condition and the Product Manager's language discipline. Decode spike: [discussion #297](https://github.com/fengguode/DATARA/discussions/297), with the compressed-timestamp deferral and its reopen triggers recorded there. Published by Primary Coordinator — Yi Tang_space-bunny-free-max_OpenCode (AI agent), authenticated account `fengguode`.

## D01–D05 delegated selections (1 October 2026)

The founder selected FIT SDK 21.217.0, delegated remaining D01–D05 choice work to Yi Tang with Yu Wang, then explicitly selected OpenAI and DeepSeek as the first providers. The [dated decision record](p0-decision-baseline-2026-10-01.md) contains selected options, rationale, affected CUS/SR/tasks, official sources, remaining evidence and founder support inputs. Its authority and GitHub links are recorded there.

Selected direction is distinct from completed contracts or satisfied G0. Earlier WP01/design packages remain historical proposals; their open-option wording is superseded only by explicit selections in the dated record. Preserve historical results. No SR/case, product implementation, founder athlete acceptance, merge or deployment is asserted by these selections.

Pilot clarification: the founder selected personal use in China, first running locally with a web UI. See [the live clarification](https://github.com/fengguode/DATARA/issues/1#issuecomment-5924895687) and the dated baseline. Runtime/setup and both provider capability gates remain pending.
