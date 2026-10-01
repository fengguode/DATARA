# Pull request confirmation

The founder approved the nine-role alignment in [issue #26](https://github.com/fengguode/DATARA/issues/26) on 30 September 2026 and named the Primary Coordinator **Yi Tang**. This policy governs confirmation of pull requests. PR means pull request only. Read the [workflow](workflow.md), [attribution protocol](attribution.md), and relevant saved role knowledge before working.

## Stage responsibilities

| Stage | Responsible AI role | Required output |
| --- | --- | --- |
| Scope and requirements | System Architect — Feng Guo | Affected CUS/SR, architecture/contracts, dependencies and open decisions |
| Investigation | Explorer — Wang Licun | Exact source evidence, observations, assumptions and gaps |
| Design | UI Designer — Wu Yunzhou | Flows/states/accessibility and design acceptance criteria |
| Implementation and handoff | Worker — Torsten Maier | Owned paths/diff, actual checks/results/limits and unresolved findings |
| Independent technical review | Reviewer — Dennis Windmaier | Final-diff findings, coverage limits and scoped technical confirmation |
| Realistic testing and defect recheck | User Tester — Abt Hermann | Candidate-specific pass/fail/blocked results and regression evidence |
| Evidence and traceability | Quality Manager — Wang Xiaofeng | Requirement coverage, evidence quality and open-gate audit |
| Release readiness | Release Manager — Wang Bingshan | Candidate readiness, defects, compatibility, release and rollback evidence |
| Cost, value and efficiency | Controller — Nils Traeger | Advisory analysis separating measured usage, calculation and estimates |
| Coordination and integration | Primary Coordinator — Yi Tang | Assignments, final confirmer, GitHub reporting and integrated changes |

## Final confirmation owner

Before work starts, the coordinator records one final confirmer and each required domain gate in the issue and pull request. Use the following scope mapping:

| Pull request scope | Final confirmer | Applicable supporting confirmations |
| --- | --- | --- |
| CUS creation, change or retirement; material customer outcome, scope or acceptance change | Founder (human user) | Architect traceability and relevant technical/evidence gates |
| SR, architecture or contracts within approved product scope | System Architect — Feng Guo | Reviewer for implementation effects; QM evidence audit |
| Design specifications within approved outcomes | UI Designer — Wu Yunzhou | Architect for requirement/contract impact; independent read-through |
| Feature implementation or bug fix within approved requirements | Reviewer — Dennis Windmaier | Affected Architect/Designer scope; Tester results and QM audit appropriate to risk |
| Test plans, evidence records, process or general project documentation | Quality Manager — Wang Xiaofeng | Relevant specialists; Controller for cost/value claims |
| Release-readiness package | Release Manager — Wang Bingshan | Reviewer, QM and Tester evidence; existing founder acceptance where required |

A mixed-scope pull request needs every affected domain gate. Split independently deliverable scopes where practical. The coordinator names the final confirmer for the main scope and records the supporting gates; uncertainty about CUS impact goes to the Architect and founder. Any material product decision, including customer outcome, priority, supported scope, data contract or public interface, requires the founder's explicit decision regardless of title or classification. Implementation of an already approved SR derived from CUS does not by itself make the pull request CUS-level.

Controller remains advisory. Pure cost/efficiency planning documents use QM final confirmation with Controller analysis review. Spending, budget, provider, permission and product decisions require the founder or authorized owner. Explorer, Worker and Tester supply their stage evidence; authorship or test execution alone does not grant final confirmation.

## Independence and evidence

An author cannot confirm their own work. If the usual confirmer authored the change, appoint a qualified independent nonauthor for that role and record their actual role/runtime, competence and substitution rationale. If no qualified independent confirmer or required evidence is available, keep the gate Blocked. Primary integration and founder product confirmation cannot waive independent technical review or evidence-backed QA.

Use only applicable roles and checks for each change. Documentation checks may use independent read-through, links and configuration checks. Product checks require relevant actual evidence: mocked adapters, live model integration, rendered UI, system verification and final user validation remain separate. The full release matrix and final user-validation gate still apply to releases. Nine-role alignment is used for team-wide policy changes, not as a blanket gate for every pull request.

Each confirmation binds to the reviewed full head SHA and exact scope. After later edits, renew affected reviews/checks and confirmation against the new SHA; preserve prior reports as historical evidence. Refresh the final confirmation to the current head SHA, identifying unchanged supporting evidence and the affected checks rerun. Resolve required findings before final confirmation.

```text
<Role> — <Configured name>_<model>-<variant>_<Harness> (AI agent)> · <Confirmed / Changes requested / Blocked>
Assignment / issue: <links>
Reviewed head SHA: <full SHA>
Scope and stage: <exact review responsibility>
Independence: <reviewer is not an author; substitution if any>
Model used: <model>-<variant> (<Harness>), model-unconfirmed, or harness-unconfirmed
Evidence and findings: <checks/results/links/limits>
Runtime / execution: <actual ID/link or unavailable>
Configuration loading: <observed or unconfirmed>
Published by: <contributing role and authenticated publisher; relay if applicable>
```

For CUS-level final confirmation, retain the founder's explicit decision and its link; the coordinator must not fabricate or infer founder confirmation. A role's final confirmation is distinct from product verification, founder final user acceptance, merge permission and release authorization. Done, Verified, Accepted and Released keep their existing separate gates. This policy adds no edit, publishing, merge or deployment permission.

## GitHub labels and change attribution

Use repository labels exactly matching `Role — Name` in the [roster](roster.md), including `Primary Coordinator — Yi Tang`, on issues and pull requests for assigned or evidenced participating roles. Repository labels stay in the short `Role — Name` form; the longer identity label that appends the model and harness is a comment, trailer, and contribution-table form, not a repository label. Identify planned assignments versus actual contributions in the body and named comments. Labels are role tags; the Project **Agent** field identifies the single current owner and also stays in the short `Role — Name` form. Record the final confirmer explicitly in the issue/pull request body. Neither a label nor a Project field proves a run or a confirmation.

Commits use evidenced `Contributed-by` or `Implemented-by` and `Integrated-by` trailers carrying the full identity label, plus a `Model-used:` trailer, the assignment, and available execution evidence. Keep actual Git author/committer identities and the linked pull request contribution table. GitHub issue-style labels are attached to issues/pull requests, so commit attribution is recorded through trailers and linked contribution records. Preserve historical labels in old commits and comments; they are not restated under the identity label format.

Every Project-management change is reported in a named activity comment with the actor role/name, item link, changed fields and old/new values, evidence of readback, and authenticated publisher. Primary Coordinator — Yi Tang publishes its own changes and relayed agent reports. GitHub status reporting is explicit; failures require a locally retained pending update and an out-of-sync report under the attribution protocol. AI persona names are distinct from GitHub account identity and native GitHub review approvals.
