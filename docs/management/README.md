# DATARA project management

*A universe of expertise. Working for you.*

This is the single management entry point for Datara. [Project control issue](https://github.com/fengguode/DATARA/issues/8) tracks delivery. One target Codex cloud environment serves management, system engineering, delivery tasks, verification, and final validation. The [DATARA Codex environment](https://chatgpt.com/codex/cloud/settings/environment/6abc9f6b878c8191bca11872a839a62a) is created and connected to fengguode/DATARA. Runtime checks and product validation are tracked separately.

## Management documents

- [Agreed project brief and roadmap](../project-brief-and-roadmap.md)
- [Founding brainstorming record](../brainstorming-record-2026-09-30.md)
- [Product requirements](product-requirements.md)
- [System requirements](system-requirements.md)
- [Machine-readable registry](requirements-registry.json)
- [Traceability](traceability.md)
- [Verification and final validation plan](validation-plan.md)
- [Decisions and change management](decision-register.md)
- [Cloud project setup and first task](cloud-project.md)

## Delivery order

| Package | Priority | Task | Dependencies |
| --- | --- | --- | --- |
| WP01 | P0 | [Define source contract and release baseline](https://github.com/fengguode/DATARA/issues/1) | None |
| WP02 | P0 | [Build persistent data home and deterministic preprocessing](https://github.com/fengguode/DATARA/issues/2) | WP01 |
| WP03 | P0 | [Specify baseline skills and eligibility pipeline](https://github.com/fengguode/DATARA/issues/3) | WP01, WP02 |
| WP04 | P0 | [Implement customer model connections and manual execution](https://github.com/fengguode/DATARA/issues/4) | WP03 |
| WP05 | P0 | [Deliver result history dashboard and output API](https://github.com/fengguode/DATARA/issues/5) | WP02, WP04 |
| WP06 | P0 | [Perform final verification and athlete validation](https://github.com/fengguode/DATARA/issues/6) | WP01, WP02, WP03, WP04, WP05 |
| WP07 | P1 | [Add skill recommendations routines and comparison](https://github.com/fengguode/DATARA/issues/7) | WP06 |

## Control rules

Product directions derive from the founding decisions. System requirements are initial derived drafts and become a testable baseline as WP01 resolves contracts. The JSON registry is the canonical identifier and coverage record; synchronize human-readable documents in the same change. Track planned, implemented, verified, and accepted states separately. No verification case currently has passing evidence.

Use each linked issue as its package record. Split implementation tasks under that package when scope is known, preserving requirement links. Estimate after dependencies and contracts are understood. The founder owns product decisions and final acceptance; cloud tasks prepare reviewable engineering artifacts and evidence.

Run `python scripts/check_requirements.py` after registry changes. It checks links and planned coverage only. Final validation requires actual software and a fixed candidate commit.
