# Controller knowledge

Prior-project lesson: cost advice needs actual usage or billing telemetry, assumptions, units, and a user-benefit measure; an estimate is not a measured bill. Source: prior `.codex/agents/controller.toml` and `docs/CODEX_WORKFLOW.md`. Apply when reviewing DATARA task or model API spending. Preserve correctness and the release gate when suggesting savings. DATARA requirement context: customer-owned analysis API access is CUS06; no DATARA cost measurements are established here.

## DATARA usage policy (30 September 2026)

The founder assigned Nils timely Codex usage monitoring and authorized pausing the current task below 3% remaining, then conditionally continuing when the blocking window(s) are freshly measured at 100% available. See the team workflow and controller configuration for exact threshold, checkpoint and resumption rules. This is a DATARA operating agreement, distinct from prior-project lessons and product/test evidence. Percentage telemetry measures shared account capacity, not a task token budget, context window or bill. Keep unchanged checks quiet, preserve read-only role limits and do not redeem reset credits. A scheduled wake-up and a configured instruction are not evidence of a completed live pause/resume transition.

Official scheduling context: https://learn.chatgpt.com/docs/automations?surface=app — local scheduled tasks require the computer on and the desktop app running. Available task tools must be checked for their actual lifecycle capabilities; report missing resume support honestly.
Local heartbeat: **Nils DATARA usage guard**, id `nils-datara-usage-guard`, every 15 minutes in the primary DATARA task. Goal controls are thread-scoped: a Controller child with no goal does not establish that the coordinating task has no active goal. Primary verifies the actual task state. Stop this guard when the requirements task is complete.
