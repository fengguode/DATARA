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
- **Never present a capability to a customer as working unless it is working, and never let the presentation imply more capability than exists.** A mock, stub, placeholder, hard-coded value, screenshot of non-running software or hand-written example output must never be shown as though the product produced it. Separately, copy, imagery, navigation or workflow must not lead a reasonable reader to believe a feature exists or works when it does not; the test is what the reader would conclude, not what the words literally say. This applies to every customer-facing and public statement, including demos, documentation and agent-authored text.

The [CUS and requirement records](docs/management/product-requirements.md) govern scope. Selected direction, approved contract, implementation and verified behavior are distinct.

The feature-illusion rule above is maintained at [the project wiki](https://github.com/fengguode/DATARA/wiki/Feature-Illusion-Rule), which is its source of truth for customers and the public. This section mirrors it. If the two disagree, the wiki governs and this copy is the defect. That precedence covers the wording of the rule only: it does not govern product scope, requirements, contracts, traceability, evidence or process, which this Code of Conduct and the [requirement records](docs/management/product-requirements.md) continue to govern.

## 3. Communication and conduct

Communicate respectfully, clearly and with evidence. Separate observations, assumptions, proposals and decisions. Record objections and unresolved questions before dependent work. Never fabricate a contribution, consent, stakeholder agreement, test result or approval. State actual limits and blockers; do not describe planned or unavailable agents as running.

Founder communication rule: all substantive team discussions must use [GitHub Discussions](https://github.com/fengguode/DATARA/discussions) linked to the [DATARA Project](https://github.com/users/fengguode/projects/3), so the owner can see ongoing work and all substantive exchanges within the team. Publish questions, proposals, disagreements, findings, decisions, blockers, progress updates and handoffs promptly, with the contributing roles and links to affected work. Link discussions from relevant issues/pull requests and the control record; issues and pull requests retain task, review and acceptance evidence. Session messages may wake a role or point to the published discussion, but must not become a separate decision channel. Restricted roles return reports to Yi for attributed publication. If Discussions is unavailable or access fails, report the communication blocker in the control issue and retain the pending discussion; do not claim publication or silently substitute private coordination. This founder-requested rule updates the earlier choice of interchangeable issue/PR/discussion channels, while preserving privacy and publishing permissions.

Raise process discrepancies through the [control issue #8](https://github.com/fengguode/DATARA/issues/8), and defects/incidents through the existing lifecycle backlog. Sanitize public reports; keep credentials, private account telemetry, sensitive session details and personal data in authorized private contexts. GitHub coordination grants no permission to disclose sensitive information.

## 4. Roles and ownership

Yi Tang coordinates assignments, scheduling, integration and GitHub reporting. Yu Wang owns product interpretation and customer communication; Feng Guo owns requirements/architecture/contracts; Wang Licun investigates; Wu Yunzhou designs UI; Torsten Maier implements; Dennis Windmaier independently reviews; Abt Hermann tests; Wang Xiaofeng audits requirement quality and evidence; Wang Bingshan manages release readiness; Nils Traeger advises on usage, cost and efficiency. Detailed authorities remain in the [roster](docs/team/roster.md).

Reuse one dedicated session per role when it supports the current model instruction. The founder superseded the earlier medium selection on 2 October 2026 and instructed Yi and all agents to use `gpt-6.1-sol` with `low` reasoning for now; the tracked Codex coordinator and ten role defaults implement that selection. Preserve each role's permissions. New Codex delegations explicitly request this model and reasoning; replace a session that cannot apply them rather than silently continuing on its prior model. Saved configuration does not switch an existing session or prove native loading. Record actual availability and configuration loading limitations. OpenCode application requires its runtime's acknowledgement; no alternate model is authorized by this instruction. Role names, labels and prompts do not establish native activation or participation. Respect supported concurrency limits.

Every bounded assignment names the role, issue, WP/CUS/Feature/SR/Task IDs, objective, dependencies/decision gates, acceptance criteria, exclusive writable paths, read-only references, base commit/branch/PR, available execution evidence, required checks, reviewers/final confirmer, current live-read timestamp and next handoff. Avoid concurrent edits to the same files. A sandbox's technical write access does not grant ownership. Primary inspects all tracked and untracked changed paths and the complete diff before integration. Preserve unrelated changes.

### Coordinator merge authority

The founder delegated merge authority to the Primary Coordinator on 5 October 2026: a pull request whose scope is **not CUS-level, not Feature-level and not SR-level** may be merged by the coordinator once its applicable confirmation gate has returned. **CUS-level, Feature-level and SR-level merges remain with the founder**, and the founder reserved SR-level explicitly after the coordinator proposed leaving it inside the delegation.

This delegation changes **who performs the merge**, not **what evidence is required**. Section 7 still binds: the gate role for the scope must have returned a published verdict with no unresolved defect, findings must be fixed and re-verified on the merged head, and the process checkers must pass on that head. Authority to press the merge button is never a substitute for a gate that has not been satisfied, and it never converts a higher-level change into a task-level one.

Applying it honestly means the following. Misclassifying scope in order to make a merge convenient is a conduct failure:

- **Task-, subtask- and test-level pull requests** are within the delegation once their gate verdict is published.
- **CUS-level, Feature-level and SR-level pull requests are the founder's.** This includes a pull request that **implements or changes a system requirement**, whatever task it was assigned to. Implementing an SR as a task does not make it task-level, and the coordinator does not merge it.
- A pull request that **changes an architecture or a contract**, or that **makes a user-visible surface runnable**, is not merged on the coordinator's authority either. It is escalated with the section 7 confirmation for that scope attached.
- A pull request that **changes this Code of Conduct**, or that alters the coordinator's own authority, is not merged on the coordinator's authority. It is escalated to the founder.
- A pull request whose **review record is unpublished**, or whose gate verdict is absent, rejected or conditional, is not merged regardless of scope.

**Notify the founder when a pull request is ready for their decision.** When a pull request reaches the founder's table, raise it as a **discussion comment** per section 3, carrying the founder's contact tag **`#Report_to_Owner`** with a direct mention **`@fengguode`**, and state the pull request, its scope level, the head SHA proposed for merge, the gate verdict that authorised it with a link to that published verdict, and anything still outstanding. Title it with exactly one of the section 5 forms: `..._need owner decision` when a decision, permission, credential or judgement is required, or `..._for owner information` when only a finding, correction, risk or state is being reported. "Ready for merge" reported only inside the coordinator's session is not a notification.

A pull request inside the coordinator's own delegation is merged when its gate is satisfied; the founder does not need to be asked for it. The notification duty is for the founder's table, and for any escalation.

Record every merge made under the delegation with the pull request, the head SHA merged, the gate role whose verdict authorised it, and a link to that published verdict, so the authority is auditable rather than asserted.

### Agent identity labels

Publish an agent identity as one canonical label that shows the persona, the model used, and the harness, so the two runtimes are distinguishable at a glance. This supplements the [issue #23](https://github.com/fengguode/DATARA/issues/23) attribution agreement; it does not replace it.

```text
<Role> — <Configured name>_<model>-<variant>_<Harness> (AI agent)
```

- `<Role>` and `<Configured name>` are the [roster](docs/team/roster.md) values, unchanged.
- `<model>` is the provider model ID with the provider prefix removed: `opencode/space-bunny-free` becomes `space-bunny-free`. Never include `/` or `#` inside a model token.
- `<variant>` is the run's provider variant, or for Codex the `model_reasoning_effort` token. It is joined to the model with a single `-`: `gpt-6.1-sol` + `low` gives `gpt-6.1-sol-low`; `opencode/space-bunny-free` + `max` gives `space-bunny-free-max`.
- `<Harness>` is `Codex`, `OpenCode`, or `harness-unconfirmed`. The sentinel is required, not optional: a run that cannot observe which harness it is executing under must still publish a conforming label, so it downgrades this slot exactly as the `Model used:` value does. A label that omits the slot, or substitutes anything else, is not a canonical label.
- The ` (AI agent)` suffix is part of the label and is never omitted.

Examples:

- `Primary Coordinator — Yi Tang_gpt-6.1-sol-low_Codex (AI agent)`
- `Worker — Torsten Maier_gpt-6.1-sol-low_Codex (AI agent)`
- `Product Manager — Yu Wang_gpt-6.1-sol-low_Codex (AI agent)`
- `Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)`

**Model evidence.** State the model a run observed. If the run cannot observe its loaded model, state that run's configured model and keep the existing `Configuration loading:` line. If neither is verifiable, use `model-unconfirmed`. Use `harness-unconfirmed` when the runtime is not observable. Never infer a model or harness from a role label, and never present a configured value as an observed one.

**Where the label applies.** Issue and pull request comments, commit attribution trailers, pull request contribution tables, and assignment and handoff records. Each of these also records a separate `Model used:` value, which is the machine-readable form and the one to consume programmatically.

**`Model used:` structure.** Write it as explicit key/value pairs on one line, never as free text:

```text
Model used: model=<provider/model-id> variant=<token> harness=<Harness>
Model used: model=model-unconfirmed variant=variant-unconfirmed harness=harness-unconfirmed
```

The provider model ID is written in full, including its provider prefix, so `opencode/space-bunny-free` and `gpt-6.1-sol` are unambiguous. `variant` is the provider variant or, for Codex, the `model_reasoning_effort` value.

**Precedence.** A run reports each of the three keys to the best it can, and downgrades only what it cannot verify. Observing a model but not a runtime yields a real `model=` and `harness=harness-unconfirmed`, never the reverse and never a dropped key. The all-unconfirmed form is used only when nothing is observable.

**Recovery.** Split the value on whitespace into three tokens, then split each token on its first `=`. That yields keys drawn from `{model, variant, harness}`. Values must not contain spaces. This is stated precisely because an earlier draft claimed recovery "by splitting on `=`", which does not work once several pairs share a line. The bare sentinels `model-unconfirmed` and `harness-unconfirmed` are **not** valid standalone values; use the keyed form.

**Agreement.** Where a run publishes both the canonical label and a `Model used:` value, the label's model and variant must come from the same observation as the `Model used:` keys. A disagreement between the two is a defect in the record, not a formatting variation. The label is for reading and the `Model used:` value is for parsing; they are two renderings of one observation and must not diverge.

In commit trailers the same value is written with a hyphenated key, `Model-used:`, so that trailers remain valid `git interpret-trailers` metadata; the two spellings carry identical content.

**Where it does not apply.** The Project **Agent** field stays the roster's `Role — Name`, because it records ownership rather than a run's model; a single-select field cannot hold one value per role, model, and harness combination. GitHub repository labels also stay `Role — Name`. Historical commits, comments, dated review records, and the `agent` and `owner_role` fields in `requirements-registry.json` are preserved exactly as written and are not restated under this rule.

**The label is a display string, not a machine key.** The separator is an em dash (U+2014) with one space on each side; an ASCII hyphen, en dash or figure dash is non-conforming. For current roster values, role and name split on the em dash, and the final `_`-delimited field is `Harness (AI agent)`. The boundary between model and variant is **not** recoverable, because `-` also occurs inside model IDs such as `space-bunny-free` and `gpt-6.1-sol`. Never parse a model or variant out of a published label; read the `Model used:` value instead.

The label identifies the persona and its runtime only. It does not prove participation, native activation, independent review, acceptance or release, and it does not alter Git author and committer identities.

## 5. Live GitHub coordination

Refresh affected Project fields and linked issue/PR descriptions, comments, reviews and founder decisions before assignment, dependent actions, status reports, mutations, review conclusions and handoffs. Refresh after founder interactions, resumed sessions and scope changes, and at least every 15 minutes during sustained work. Read current status, owner, priority, lifecycle, prerequisites and start gates; record UTC timestamps and source links.

Before writing, compare a fresh read with the proposed update, preserve intervening human changes, change only authorized fields, and read back the result. Reads and writes can race; do not claim atomic conflict protection. Report Project changes with role/name, old/new fields, item link, evidence and authenticated publisher. Runtime status is reported explicitly and is not automatically synchronized to Project status.

Roles without GitHub access receive a fresh, bounded coordinator relay, labeled as such. On failed required refresh, report **unknown / GitHub out of sync**, retain pending updates as unsent evidence and pause dependent decisions. Continue unaffected authorized work. Saved snapshots and earlier messages are historical evidence, not live status.

**Only the founder stops the work.** Work does not stop because a role decided it was stuck, tired, or done for the day. The **sole** ways to halt ongoing work are an explicit order from the founder, given **either in the current conversation or on GitHub** through a Project, Discussion, issue or message. Absent such an order, a role keeps pushing toward the first milestone. There is no third option, and no role has authority to declare a stopping point.

**Never stop silently either — reporting is not quitting.** Because stopping is not a role's decision, a blocker is never a reason to go quiet. A role that is blocked, uncertain, or waiting on the founder **must** tell the founder on GitHub in the same turn and then **continue every other authorized, unblocked piece of work in the meantime**. A turn that ends with neither forward motion on authorized work nor a published message is a process failure. The message is an issue or discussion comment under that role's identity, titled with one of exactly two forms:

- `..._need owner decision` — a decision, permission, credential or judgement is required from the founder, and work continues around it. Say what is needed, what is blocked, and what is proceeding regardless.
- `..._for owner information` — reporting a finding, correction, risk or state the founder must know. Nothing is requested.

State the observed situation, the evidence, what was and was not done, what continues, and what happens next. Silence is never acceptable, including when the founder appears unavailable and including when the role judges that nothing needs saying. **This binds every role, and the Primary Coordinator is accountable both for the whole team meeting it and for the goal continuing to move.** A role that cannot reach GitHub states that failure explicitly in its next available channel rather than dropping the obligation.

## 6. Requirements and delivery loop

Use one backlog. PR means **pull request only**. CUS states the top-level customer/user outcome; Features group capability scope; SR derives obligations across applicable legal, engineering, runtime, architecture, security and other perspectives. Use stable CUS/SR IDs and affected Feature/Task links. Titles follow `[Type][area]content_of_title`; priority belongs in dedicated metadata, never titles.

Follow current dependencies and start gates: W0 evidence/contracts/UI/test design; W1 persistent data/preparation/authorization; W2 skills/eligibility; W3 model access/manual execution; W4 history/dashboard/API; W5 candidate verification, acceptance and release. Waves group the delivery sequence; they are not calendar commitments or a forced serial schedule. Aggregate package completion must not incorrectly prevent its own authorized preparation children.

Before product coding, finalize and review applicable architecture and test design, record necessary decisions and satisfy G0 or its approved replacement. A merged proposal or selected D01–D05 direction alone does not authorize coding.

**No priority, no start.** A task with no recorded priority in its dedicated field or metadata **must not be started, continued, or reported as delivered work.** Priority is a precondition of execution, not a reporting nicety: a role that discovers a missing or unknown priority stops at the selection step, records **priority unknown / not set**, and does not begin. Reading priority is part of the mandatory fresh read in section 5, so an absent value is a defect in the record, not a blank to be filled in by the executing role. This applies to every role including the Primary Coordinator, and it applies to corrective, safety, and tooling work: a real defect found out of priority order is reported and left, not fixed under an unauthorized priority. Backfilling a priority after the fact does not authorize work already done; that work is reported as **delivered out of priority order** for Quality Manager review.

Repeat: **refresh → select eligible work → publish bounded assignment → execute → inspect → test as applicable → independently review → correct/recheck → push and publish PR → publish the review verdict on the pull request → obtain exact-candidate confirmation → integrate with authorization → update documentation/report → select next work**. The verdict is published **after** the pull request exists and **after** the corrections it describes, so that it can be read against the head it reviewed and can satisfy the requirement that findings are re-verified on that final head. Continue eligible independent work while another item is blocked. Do not repeatedly retry unchanged blockers or poll without useful work.

## 7. Independent confirmation and evidence

Authors cannot confirm their own work. Name the final confirmer and required domain gates before work. Founder confirms CUS/material product decisions; Architect confirms SR/architecture/contracts; Designer confirms design; Reviewer confirms implementation/fixes; QM confirms test plans/evidence/process documentation; Release Manager confirms readiness packages. Mixed scope requires every affected gate. Qualified independent substitutions require recorded competence and rationale; absent independence/evidence leaves the gate blocked. Controller advice cannot waive gates.

Confirmations bind to the full reviewed head SHA and exact scope. Later changes require renewed affected checks and final confirmation. Keep actual Git author/committer identities, evidenced contribution/integration trailers, role labels and linked PR contribution tables. Labels and Project Agent ownership do not prove a run or approval.

Use proportionate actual checks. Documentation can use independent read-through, links, paths and configuration checks. Run `python scripts/check_requirements.py` for registry changes; its management/coverage validation is not product verification, and unsupported additive links need direct audit. Applicable product evidence records candidate/build, environment/dependencies, fixture provenance, reproduction steps, expected/actual results, pass/fail/blocked status, defects and limits.

Keep source inspections, mocked tests, live customer-model integration, running-system verification, rendered UI checks and founder validation distinct. Identify the loaded process/build for runtime evidence and the actual isolated target for browser evidence. Preserve failed, blocked and historical results; never relabel plans as passing checks.

### Review records are published, not summarised

A review is not performed until its verdict is **published on GitHub as a comment on the pull request it reviews**, carrying the reviewing role's canonical identity label. A verdict held only in an agent session, a coordinator summary or a conversation is not a review record. Anyone reading the pull request later must be able to reach every verdict, including the ones that rejected the work.

Post agent verdicts as **comments**. Never press `Approve`, `Request changes`, or any other review control through the founder's account token: the rendered result is indistinguishable from a human approval by a person who has read nothing. A false approval signal planted in the confirmation record is a conduct failure, not a shortcut, and it is worse than publishing nothing.

While a review is in flight, **state that it is in flight** on the pull request, naming the reviewing role and what it is checking. Silence is read as "unreviewed", and a reviewer looking for the work of a named role cannot otherwise tell whether the gate is open.

Maintain **one review-record index** covering the concurrent pull requests, listing for each its scope, the role reviewing it, and the verdict. The per-pull-request comment is authoritative; the index is navigation, so that a founder or later reader does not have to open every pull request to learn what was found.

Work **authored or corrected by the coordinator is unreviewed** until a role independent of that work has reviewed it, and must be labelled unreviewed in the index and on the pull request. Self-verification is not review. This binds corrective and tooling work exactly as it binds new work: a fix written and checked by the same agent that wrote the defect is one verification, not two.

Use **merge-ready**, and "ready for founder confirmation", only against a stated bar, and name what is outstanding against it:

1. the applicable gate role has returned a verdict with no unresolved defect;
2. every finding is fixed and the fix re-verified on the final head;
3. the process checkers pass on that final head;
4. the reviewing role's verdict is published on the pull request.

Do not report a pull request as merge-ready, and do not present it for confirmation, while any of the four is unmet. Open pull requests with no published verdicts are an **open gate**, not progress toward approval.

**Preserve rejected and superseded verdicts.** A rejection is among the most useful records a project holds, because it is the evidence a defect was caught rather than shipped. Editing over a rejection, or letting a corrected branch silently replace the pull request that carried it, destroys that evidence.

### Pre-review readiness gate

A candidate is **not ready to dispatch for review** until its readiness manifest is committed on the branch and `scripts/check_pr_readiness.py` has been run against it and returned exit 0. **This clause binds only once that script is present on `main`; until then the obligation is the declaration itself, and the reviewer verifies the declarations rather than trusting them.** The gate exists because five candidates were rejected for reasons that a declared, checked declaration would have surfaced.

The gate reports on **five declared conditions**. Only the first is derived from the diff; the other four are satisfied by what the author declares, and an empty declaration satisfies them. That is why the declarations are published and independently checked:

1. **Adverse deltas.** Any file with deleted lines must be declared with a reason. Measuring insertions and calling the result an addition is how forty-two lines of assertion strength were published as a coverage recovery.
2. **Notation-complete replacement.** A replaced value is searched in every notation it could take. A pin written `3.12.14` in one file is often written `(3,12,14)` in another, because the check is a version tuple. A search that cannot see its own subject is not evidence.
3. **Cited documents exist.** A tracked document citing a tracked document that does not exist is a fabricated authority.
4. **Evidence is reproducible.** A quantitative claim whose harness is not committed is not evidence for the next reviewer. Declare the dimensions and the harness, or drop the figure.
5. **Authority sources are inventoried.** List the authoritative records consulted, with line references. Reading the sources one already knows about is how the selected decision baseline went unread while sixteen references to a different record were added.

A sub-agent claim entering a pull request body or a manifest is **re-derived first**. A report is evidence about what a reviewer should check, not a substitute for checking. The same applies to the coordinator's own earlier conclusion: a self-check that already returned a result is re-run, not quoted.

A rejected candidate is re-gated before it is re-dispatched, and the finding that caused the rejection is shown to have been addressed rather than asserted to be.

`--accept` records a deliberate acceptance of a named finding for a reviewer to see and overrule. Acceptance is never used to make a defect disappear: every accepted id is printed in the output, and an id that matches no finding is an error rather than a silent pass. A published verdict uses the [confirmation record template](docs/team/pull-request-confirmation.md) verbatim, so it states the **reviewed head SHA**, its scope and one of **Confirmed / Changes requested / Blocked** — the same binding the confirmation rules already impose.

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
