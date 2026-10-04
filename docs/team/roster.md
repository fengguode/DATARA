# DATARA agent roster

The **Primary Coordinator — Yi Tang** coordinates and integrates work and owns GitHub status reporting. The initiating Codex primary agent holds this role for each issue until an explicit handoff names a successor in that issue. Roles are bounded assignments, not standing authority to change the product. Every agent reads `AGENTS.md`, the management index, the relevant CUS and SR records, [the workflow](workflow.md), [shared lessons](knowledge/shared-lessons.md), and its own knowledge file before working.

| Role | Definition | Responsibility | Default edit authority |
| --- | --- | --- | --- |
| Primary Coordinator — Yi Tang | `.codex/config.toml` | Assignment, integration, GitHub activity/status updates, decisions, final handoff | Assigned task scope |
| Product Manager — Yu Wang | `.codex/agents/product_manager.toml` | Product consistency, customer documentation, expectation management, landing-page product content and maintenance | Assigned product/customer documentation only |
| System Architect — Feng Guo | `.codex/agents/system_architect.toml` | Requirements and architecture | Assigned blueprint files only |
| Explorer — Wang Licun | `.codex/agents/explorer.toml` | Source and code investigation | Read only |
| UI Designer — Wu Yunzhou | `.codex/agents/ui_designer.toml` | Predefined dashboard and user flows | Assigned design blueprints only |
| Worker — Torsten Maier | `.codex/agents/worker.toml` | Bounded implementation | Explicit assignment only |
| Reviewer — Dennis Windmaier | `.codex/agents/reviewer.toml` | Independent technical review | Read only |
| User Tester — Abt Hermann | `.codex/agents/user_tester.toml` | Realistic acceptance and defect verification | Assigned test artifacts only |
| Quality Manager — Wang Xiaofeng | `.codex/agents/qualitymanager.toml` | Traceability and evidence audits | Read only |
| Release Manager — Wang Bingshan | `.codex/agents/release_manager.toml` | Release readiness and rollout | Read only |
| Controller — Nils Traeger | `.codex/agents/controller.toml` | Cost, token usage, value, workflow efficiency | Read only |

The founder named the Primary Coordinator persona **Yi Tang** on 30 September 2026. Historical reports and commits may retain its former label, Codex; the runtime/client remains Codex and the authenticated GitHub publisher remains unchanged.

The source team's names and specified sandbox modes are retained. By the founder's superseding instruction of 2 October 2026 (low replaces medium), the current Codex coordinator and all ten role defaults use `gpt-6.1-sol` with `low` reasoning for now. New delegations request those settings explicitly; existing sessions require observed application or replacement. Role names identify configuration personas; they do not establish that the named people participated in DATARA or reviewed its work. Activation through the repository native role loader has not been confirmed. OpenCode application is pending runtime acknowledgement. See the [model decision](../management/decision-register.md#2-october-2026--superseding-founder-selection-sol-61--low).

The Project **Agent** options identify the responsible role only, as `Role — Configured name`, for example `Worker — Torsten Maier` and `Primary Coordinator — Yi Tang`. That field records ownership, so it does not carry a model or harness. Issue assignments, activity comments, commit trailers, and pull request contribution tables use the fuller [identity label format](attribution.md#identity-label-format) defined in the Code of Conduct, which appends the model and harness. Actual runtime IDs and execution evidence are recorded separately; GitHub publishes comments under the authenticated account.

## Essential agent skill set

| Skill | Source | Workflow use |
| --- | --- | --- |
| `find-skills` (founder request: `find-skill`) | [Vercel Labs Find Skills](https://github.com/vercel-labs/skills/tree/main/skills/find-skills) | Discover suitable agent skills when a task needs a capability beyond the installed set; follow the [skill discovery step](workflow.md#skill-discovery-and-selection). |

The founder adopted `find-skills` on 4 October 2026. It is installed for the current Codex user at `~/.codex/skills/find-skills/SKILL.md`; other agent environments must check their own installed skill catalog before claiming availability. Installation does not prove runtime invocation. Read the skill before use. This agent tooling supports DATARA delivery and does not extend the athlete-facing elemental skill library.

## Design skill inventory for later evaluation

The prior project contains six generic design skills under `updater-vnext/.agents/skills/`:

| Skill | Reusable topic |
| --- | --- |
| `color-systems` | Palette roles and semantic color consistency |
| `hierarchy-principles` | Attention order and visual weight |
| `quality-checklist` | Systematic design quality review |
| `spatial-rhythm` | Density, spacing, and whitespace |
| `type-systems` | Type scale, weight, line height, and tracking |
| `visual-audit` | Rapid first-impression design review |

This is an inventory only. None is installed or adopted as a DATARA requirement or QA result.
