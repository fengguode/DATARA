# DATARA team workflow

## Authority and source of truth

Start with `AGENTS.md`, `docs/management/README.md`, `docs/project-brief-and-roadmap.md`, the relevant requirement and decision records, [the roster](roster.md), [shared lessons](knowledge/shared-lessons.md), and the assigned role knowledge file. The dated brainstorming record explains historical choices. DATARA's registry is the canonical requirement and planned-coverage record; the [GitHub Project](https://github.com/users/fengguode/projects/3) is the shared task-status record. Do not create a second backlog. Prior-project lessons are methods to evaluate, not DATARA product requirements or verification evidence.

## Assignment and GitHub reporting

The primary defines a bounded assignment before delegation and keeps one accountable owner. Each assignment and GitHub issue/PR update identifies: agent, issue and work package, PR/SR IDs, outcome and file scope, dependencies and open decisions, acceptance criteria, branch and PR, execution link when available, and actual validation evidence or a named blocker. Use isolated task branches and reviewable PRs for delivery. Record agent runtime state explicitly in the issue or handoff; neither Codex activity nor an agent's completion automatically updates GitHub. Update status at assignment, blocker, review handoff, and completion. The primary reconciles the GitHub record with the actual branch and evidence.

Assign nonoverlapping files. Prefer parallel read-only investigation; dependent design, implementation, test, and integration steps remain ordered. A broad `workspace-write` sandbox does not enforce file ownership. After delegated writes, the primary checks tracked and untracked paths and the complete diff against the assignment, resolves overlaps, and integrates only in-scope work. Preserve unrelated changes. Never infer stakeholder agreement from an agent exchange.

## Design, defect, and quality flow

The System Architect traces requirements and contracts to PR/SR IDs and decision records. Material changes to product scope, priority, data contracts, or public interfaces require the founder's decision. The UI Designer defines dashboard flows, states, accessibility, and concrete acceptance checks within approved scope. The Worker implements approved bounded behavior. The User Tester records reproducible results against disposable data. For defects, capture expected/actual behavior and evidence, then have the Architect and Worker trace root cause and proposed effects; consult the Designer and Controller where their concerns apply. Record objections and unresolved decisions before dependent implementation.

The Reviewer independently inspects the final diff and affected behavior. The Quality Manager audits traceability, QA evidence, and open gates. The primary fixes findings, reruns affected checks, and integrates. For documentation-only work, a focused read-through, link/path check, and configuration validation are proportionate. For product work, run relevant checks once they exist and record commands, target commit, environment, fixtures, outcomes, defects, and limits. Source tests, mocked adapters, live customer-model integration, system verification, rendered UI acceptance, and final athlete validation are separate evidence types. Browser checks must actually render the intended isolated target; service checks must identify the loaded process/build and same-origin routes. Block a required gate when tooling or evidence is absent.

## Status and release gates

GitHub lifecycle is Backlog → Ready → In progress → In review → Done, with named blockers recorded in the issue. Done means task delivery only. Verified requires candidate-specific passing evidence against the applicable SR and test case. Accepted requires the founder's explicit decision. Released requires a separate release gate and authorized rollout. Do not mark a requirement verified from planned coverage, a closed issue, a merged PR, or a passing management registry check.

For a fixed P0 candidate commit, follow `docs/management/validation-plan.md` and `docs/management/lifecycle-and-releases.md`: all P0 SR checks with reproducible evidence, actual live-model integration where required, TC15 athlete journey and founder acceptance, triaged defects, release notes, version/compatibility, deployment and rollback plan, and an explicit release decision. Keep cloud environment readiness separate from product deployment. Release Manager prepares readiness evidence and coordinates rollout only when separately authorized. Preserve historical results, including failed and blocked checks, without relabeling them as passed.

## Migration provenance

This operating method adapts the prior project's `AGENTS.md`, `docs/CODEX_WORKFLOW.md`, `updater-vnext/docs/RETRO_2026-09-27.md`, and `updater-vnext/docs/qa/2026-09-28-retro-lessons-learned.md`. Their incident, service, browser, and QA results apply only to that project. The DATARA product and release gates come from DATARA management records.
