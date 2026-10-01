# DATARA P0 architecture and test-design package

Status: **engineering proposal; not approved, implemented, verified, accepted, or released**
Work package scope: WP01–WP06; existing package issues #1–#6, control issue #8
Affected stories: CUS01–CUS10. P1 CUS11–CUS13 remain outside this baseline.
Branch: `codex/p0-architecture-test-design`
Primary coordinator: initiating Codex task (runtime identity is recorded in the task report; it is not inferred from role names).

## Purpose and authority

This package makes the P0 implementation sequence reviewable against current repository requirements. Confirmed product direction is taken from `docs/project-brief-and-roadmap.md`; current CUS, SR, task, decision, and test identifiers are taken from `docs/management/requirements-registry.json` and the management records. Contracts are proposals unless a founder decision record says otherwise. D01–D05 remain open in `docs/management/decision-register.md`.

This package does not authorize product implementation. It supplies a proposed contract for Torsten's implementability review. Requirements, task plans, tests, and design records remain proposal/planned state. No product checks have been run because this repository contains no application source or product test suite.

## Contents

- [Interactive architecture explorer](architecture-explorer.html) — a guided HTML viewer for all eight diagrams with explanations, search, keyboard navigation, zoom, and source inspection. It loads Mermaid from jsDelivr, so rendered diagrams require an internet connection; the source text remains embedded in the file.
- [Architecture baseline](architecture-baseline.md) — system boundaries, components, flows, security and operational questions.
- [Implementation contracts and handoff](implementation-contracts.md) — ordered WP/TK contracts, status and start blockers.
- [Test design](test-design.md) — test cases mapped to requirements, fixtures, oracles, retained evidence and gates.
- [Traceability and readiness](traceability-readiness.md) — CUS → SR → unit → decision/design → test → evidence mapping and coverage gaps.
- [Decision proposals](decision-proposals.md) — options and evidence for D01–D05; founder decisions remain outstanding.
- [Review and delivery log](review-and-delivery.md) — role assignments, actual reviews, checks, candidate and reporting state.
- [Review findings](review-findings.md) — independent implementability, technical, quality, release and controller findings and disposition.
- [Dashboard contract](dashboard-contract.md) — UI proposal and acceptance states (assigned to the Designer).
- [Test design findings](test-design-findings.md) — independent acceptance/test review (assigned to the User Tester).
- [Evidence audit](evidence-audit.md) — read-only official/source evidence review (assigned to the Explorer).
- [Editable diagrams](diagrams/) — eight Mermaid diagram sources. Written contracts are authoritative where an open decision is explicitly called out.

## Known repository condition

At task start, the user's worktree already contained modifications to seven management/registry files and `scripts/check_requirements.py`. Several of those modified files contain literal merge-conflict markers, including the canonical JSON registry. Those files are preserved and not edited by this design task. The branch was created from the existing terminology branch with its uncommitted working tree preserved; only task-owned files are intended for this package's commit. This condition prevents treating the canonical registry check or a pull request candidate as validated until the owner resolves the existing edits and reruns the check.

## Decision and evidence labels

| Label | Meaning |
|---|---|
| Confirmed direction | Explicit in the founder's brief / current CUS scope. |
| Proposed contract | Concrete design awaiting review and any required founder decision. |
| Open decision | D01–D05 or a newly identified owner question not yet answered. |
| Designed / Not run | A test plan only. It is not evidence of product behavior. |
| Verified | Reserved for reproducible, candidate-specific passing evidence under the project workflow. None is claimed here. |
