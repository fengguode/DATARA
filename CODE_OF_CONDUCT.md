# DATARA Code of Conduct and Project Working Rules

This document consolidates DATARA's current project guidelines and team working rules. It applies to project contributors and AI role agents. It is an operating guide, not a software license, product contract, verification result or release approval.

## 1. Authority and sources

Follow explicit founder instructions within existing permissions. Read [AGENTS.md](AGENTS.md), the [management index](docs/management/README.md), [project brief](docs/project-brief-and-roadmap.md), relevant CUS/SR and decision records, [team workflow](docs/team/workflow.md), [roster](docs/team/roster.md), [attribution protocol](docs/team/attribution.md), [confirmation policy](docs/team/pull-request-confirmation.md) and relevant [saved knowledge](docs/team/knowledge/shared-lessons.md) before work.

Use the [DATARA GitHub Project](https://github.com/users/fengguode/projects/3) and linked issues/pull requests as the shared authoritative management and task-status record. Local registries and documents mirror identifiers, traceability and coverage and preserve detailed evidence; they are not a second backlog. Dated brainstorming and superseded decisions retain rationale, not current approval. The [selected decision baseline](docs/management/p0-decision-baseline-2026-10-01.md) records D01–D05 selections and their remaining gates. Consult it for current versions and product choices rather than duplicating them here.

If sources conflict, identify the discrepancy, preserve newer founder changes, and resolve it through the [decision/change process](docs/management/decision-register.md). This consolidation does not silently override its source rules or approve open contracts.

## 2. Product principles

- Start from defined, supported source data; ingest, validate, normalize and preprocess deterministically using conventional software.
- Preserve data and result history. P0 provides a dashboard/database experience and an authorized read-only output API.
- Keep elemental skills provider independent. Customers own the API access used for analysis.
- Check eligibility deterministically before recommendation and execution and explain unsupported inputs and demands.
- Users select skill combinations and supported models. Never silently replace a provider, model, skill or routine.
- DATARA's own recommendation model, automatic routines and recommendations belong to P1. Commercial mechanisms and source-to-skill automation are deferred.
- Preserve user isolation and reproducible provenance throughout the workflow.

The [CUS and requirement records](docs/management/product-requirements.md) govern scope. Selected direction, approved contract, implementation and verified behavior are distinct.

## 3. Communication and conduct

Communicate respectfully, clearly and with evidence. Separate observations, assumptions, proposals and decisions. Record objections and unresolved questions before dependent work. Never fabricate a contribution, consent, stakeholder agreement, test result or approval. State actual limits and blockers; do not describe planned or unavailable agents as running.

Record substantive team assignments, questions, findings, decisions, blockers, handoffs, review outcomes and acceptance evidence in linked GitHub issues, pull requests or discussions. Session messages may wake a role and point to its GitHub assignment; they do not replace that record. Restricted roles return bounded reports to Yi for attributed publication.

Raise process discrepancies through the [control issue #8](https://github.com/fengguode/DATARA/issues/8), and defects/incidents through the existing lifecycle backlog. Sanitize public reports; keep credentials, private account telemetry, sensitive session details and personal data in authorized private contexts. GitHub coordination grants no permission to disclose sensitive information.

## 4. Roles and ownership

Yi Tang coordinates assignments, scheduling, integration and GitHub reporting. Yu Wang owns product interpretation and customer communication; Feng Guo owns requirements/architecture/contracts; Wang Licun investigates; Wu Yunzhou designs UI; Torsten Maier implements; Dennis Windmaier independently reviews; Abt Hermann tests; Wang Xiaofeng audits requirement quality and evidence; Wang Bingshan manages release readiness; Nils Traeger advises on usage, cost and efficiency. Detailed authorities remain in the [roster](docs/team/roster.md).

Reuse one dedicated session per role. Preserve configured models, reasoning and permissions; Yu uses the configured gpt-6.1-sol/medium setting. Record actual availability and configuration loading limitations. Role names, labels and prompts do not establish native activation or participation. Respect supported concurrency limits.

Every bounded assignment names the role, issue, WP/CUS/Feature/SR/Task IDs, objective, dependencies/decision gates, acceptance criteria, exclusive writable paths, read-only references, base commit/branch/PR, available execution evidence, required checks, reviewers/final confirmer, current live-read timestamp and next handoff. Avoid concurrent edits to the same files. A sandbox's technical write access does not grant ownership. Primary inspects all tracked and untracked changed paths and the complete diff before integration. Preserve unrelated changes.

## 5. Live GitHub coordination

Refresh affected Project fields and linked issue/PR descriptions, comments, reviews and founder decisions before assignment, dependent actions, status reports, mutations, review conclusions and handoffs. Refresh after founder interactions, resumed sessions and scope changes, and at least every 15 minutes during sustained work. Read current status, owner, priority, lifecycle, prerequisites and start gates; record UTC timestamps and source links.

Before writing, compare a fresh read with the proposed update, preserve intervening human changes, change only authorized fields, and read back the result. Reads and writes can race; do not claim atomic conflict protection. Report Project changes with role/name, old/new fields, item link, evidence and authenticated publisher. Runtime status is reported explicitly and is not automatically synchronized to Project status.

Roles without GitHub access receive a fresh, bounded coordinator relay, labeled as such. On failed required refresh, report **unknown / GitHub out of sync**, retain pending updates as unsent evidence and pause dependent decisions. Continue unaffected authorized work. Saved snapshots and earlier messages are historical evidence, not live status.

## 6. Requirements and delivery loop

Use one backlog. PR means **pull request only**. CUS states the top-level customer/user outcome; Features group capability scope; SR derives obligations across applicable legal, engineering, runtime, architecture, security and other perspectives. Use stable CUS/SR IDs and affected Feature/Task links. Titles follow `[Type][area]content_of_title`; priority belongs in dedicated metadata, never titles.

Follow current dependencies and start gates: W0 evidence/contracts/UI/test design; W1 persistent data/preparation/authorization; W2 skills/eligibility; W3 model access/manual execution; W4 history/dashboard/API; W5 candidate verification, acceptance and release. Waves group the delivery sequence; they are not calendar commitments or a forced serial schedule. Aggregate package completion must not incorrectly prevent its own authorized preparation children.

Before product coding, finalize and review applicable architecture and test design, record necessary decisions and satisfy G0 or its approved replacement. A merged proposal or selected D01–D05 direction alone does not authorize coding.

Repeat: **refresh → select eligible work → publish bounded assignment → execute → inspect → test as applicable → independently review → correct/recheck → push and publish PR → obtain exact-candidate confirmation → integrate with authorization → update documentation/report → select next work**. Continue eligible independent work while another item is blocked. Do not repeatedly retry unchanged blockers or poll without useful work.

## 7. Independent confirmation and evidence

Authors cannot confirm their own work. Name the final confirmer and required domain gates before work. Founder confirms CUS/material product decisions; Architect confirms SR/architecture/contracts; Designer confirms design; Reviewer confirms implementation/fixes; QM confirms test plans/evidence/process documentation; Release Manager confirms readiness packages. Mixed scope requires every affected gate. Qualified independent substitutions require recorded competence and rationale; absent independence/evidence leaves the gate blocked. Controller advice cannot waive gates.

Confirmations bind to the full reviewed head SHA and exact scope. Later changes require renewed affected checks and final confirmation. Keep actual Git author/committer identities, evidenced contribution/integration trailers, role labels and linked PR contribution tables. Labels and Project Agent ownership do not prove a run or approval.

Use proportionate actual checks. Documentation can use independent read-through, links, paths and configuration checks. Run `python scripts/check_requirements.py` for registry changes; its management/coverage validation is not product verification, and unsupported additive links need direct audit. Applicable product evidence records candidate/build, environment/dependencies, fixture provenance, reproduction steps, expected/actual results, pass/fail/blocked status, defects and limits.

Keep source inspections, mocked tests, live customer-model integration, running-system verification, rendered UI checks and founder validation distinct. Identify the loaded process/build for runtime evidence and the actual isolated target for browser evidence. Preserve failed, blocked and historical results; never relabel plans as passing checks.

## 8. Data, rights and authorization

Do not commit credentials, personal FIT telemetry, runtime data or other sensitive evidence to this public repository. Use sanitized artifacts and authorized restricted evidence locations. Protect customer keys and owner-scoped data. Source access, license presence, owner acceptance, permitted execution, benchmarking and distribution rights are distinct; document required rights before use. Never accept binding terms on the owner's behalf without applicable authorization.

Live model calls require eligible customer-owned access, provider/location suitability and an authorized spend cap. No silent fallback, paid redispatch or scope expansion is authorized by a coordination assignment. Real-data use, permission changes, spending, merge, final acceptance and deployment remain subject to their applicable authorization gates.

## 9. Status and release discipline

**Done** means delivered task scope; **Verified** needs reproducible candidate-specific requirement evidence; **Accepted** needs explicit founder acceptance; **Released** needs an authorized rollout and observed result. A closed issue, merged PR, registry check or agent completion is not proof of the later states. Do not close aggregate work from a partial delivery.

Follow the [validation plan](docs/management/validation-plan.md) and [lifecycle/release rules](docs/management/lifecycle-and-releases.md). A P0 release needs applicable requirement evidence, required real-model integration, the end-to-end athlete journey/TC15 and explicit founder acceptance, triaged defects, compatibility/migration/version records, release notes, operating/rollout/rollback instructions and named release authorization. Cloud tooling setup is separate from product deployment. Report “ready for release decision” while authorization is pending.

Yu's customer-facing achieved/working-on/planned statements must follow current evidence. Do not announce released capabilities from proposals or before authorized publication.

## 10. Usage guard and recovery

Nils monitors fresh supported account limits; Yi owns safe checkpoints and lifecycle actions. Check at work start, before substantial batches/delegations, after handoffs and at most 15 minutes apart. If any applicable window has **strictly less than 3% remaining**, stop new substantive work/delegation, preserve branch/head/owned changes and next steps, and report the blocker through authorized channels. Exactly 3% does not trigger this threshold.

Resume quota-paused work only when each triggering window is freshly observed at **100% available**, other relevant windows have at least 3% available and ordinary usage is allowed. Predicted reset times are not evidence. Manual pauses/cancellations and completed work take precedence. Keep existing authorized monitoring active; disclose client limitations, and do not claim an unobserved pause/reset/resume or background run succeeded. No reset-credit redemption, purchase, credential/model change or broader access is authorized by this guard.

Checkpoints retain branch/head and owned changes, assignments, completed checks/findings, publication/pending updates, blockers and the exact next action. Share only sanitized project information publicly; retain actual private account telemetry in authorized private context.

## Maintenance

This consolidation was requested by the founder on 1 October 2026 under [control issue #8](https://github.com/fengguode/DATARA/issues/8). Maintain it with the linked source rules through reviewed changes. Material product decisions, new team policies and permissions require their existing approval processes. This file does not grant additional authority or declare any product gate complete.
