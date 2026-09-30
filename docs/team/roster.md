# DATARA agent roster

The **Primary Coordinator (Codex)** coordinates and integrates work and owns GitHub status reporting. The initiating Codex primary agent holds this role for each issue until an explicit handoff names a successor in that issue. Roles are bounded assignments, not standing authority to change the product. Every agent reads `AGENTS.md`, the management index, the relevant PR/SR records, [the workflow](workflow.md), [shared lessons](knowledge/shared-lessons.md), and its own knowledge file before working.

| Role | Definition | Responsibility | Default edit authority |
| --- | --- | --- | --- |
| Primary Coordinator (Codex) | `.codex/config.toml` | Assignment, integration, GitHub activity/status updates, decisions, final handoff | Assigned task scope |
| System Architect (Feng Guo) | `.codex/agents/system_architect.toml` | Requirements and architecture | Assigned blueprint files only |
| Explorer (Wang Licun) | `.codex/agents/explorer.toml` | Source and code investigation | Read only |
| UI Designer (Wu Yunzhou) | `.codex/agents/ui_designer.toml` | Predefined dashboard and user flows | Assigned design blueprints only |
| Worker (Torsten Maier) | `.codex/agents/worker.toml` | Bounded implementation | Explicit assignment only |
| Reviewer (Dennis Windmaier) | `.codex/agents/reviewer.toml` | Independent technical review | Read only |
| User Tester (Abt Hermann) | `.codex/agents/user_tester.toml` | Realistic acceptance and defect verification | Assigned test artifacts only |
| Quality Manager (Wang Xiaofeng) | `.codex/agents/qualitymanager.toml` | Traceability and evidence audits | Read only |
| Release Manager (Wang Bingshan) | `.codex/agents/release_manager.toml` | Release readiness and rollout | Read only |
| Controller (Nils Traeger) | `.codex/agents/controller.toml` | Cost, token usage, value, workflow efficiency | Read only |

The source team's names, model choices, reasoning settings, and specified sandbox modes are retained. Role names identify configuration personas; they do not establish that the named people participated in DATARA or reviewed its work.

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
