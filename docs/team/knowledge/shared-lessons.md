# Shared lessons

These are transferable process lessons from the prior project. They are not DATARA requirements, test results, or approvals. Apply them only when the stated condition exists; DATARA's `AGENTS.md` and management records govern.

| Lesson | Source | When it applies |
| --- | --- | --- |
| Define observable acceptance and record a QA session with actual results; scale documentation checks to risk. | Prior project `AGENTS.md`; `docs/CODEX_WORKFLOW.md` | Every assigned change. |
| Bound delegation, assign exclusive files, and inspect the complete diff because broad write permission is procedural, not path-enforced. | Prior project `docs/CODEX_WORKFLOW.md`; `updater-vnext/docs/qa/2026-09-28-retro-lessons-learned.md` | Any delegated write. |
| A passing source or API test does not prove a running process loaded current code. Confirm process/build identity and same-origin UI and routes in an isolated runtime. | Prior project `updater-vnext/docs/qa/2026-09-28-retro-lessons-learned.md` | Service-backed DATARA implementation or acceptance. |
| Preflight the browser and target before rendered UI acceptance; record browser, viewport, automation path, and failures. API checks do not prove usability. | Prior project `updater-vnext/docs/RETRO_2026-09-27.md`; `updater-vnext/docs/qa/2026-09-28-retro-lessons-learned.md` | DATARA dashboard work once runnable. |
| Test identity changes and delayed responses so one user's state cannot appear for another. | Prior project `updater-vnext/docs/qa/2026-09-28-retro-lessons-learned.md` | Identity-scoped DATARA UI, caches, or async requests. |
| Keep open gates open when the required runtime, browser, or user evidence is missing; do not substitute older or lower-level checks. | Prior project `updater-vnext/docs/RETRO_2026-09-27.md`; `docs/CODEX_WORKFLOW.md` | QA and release reporting. |
| Separate proposed fixes, stakeholder agreement, implementation, regression, and release decisions; preserve objections. | Prior project `docs/CODEX_WORKFLOW.md` | Cross-role defects or design decisions. |
| Cost reviews distinguish measured usage from estimates and never waive quality gates. | Prior project `.codex/agents/controller.toml`; `docs/CODEX_WORKFLOW.md` | Controller reviews. |

DATARA's current management records say product verification cases are planned and not run. This migration supplies no DATARA product test evidence.
