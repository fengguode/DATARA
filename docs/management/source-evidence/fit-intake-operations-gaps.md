# FIT intake data flow and operational gaps — 1 October 2026

Status: discovery report of intended policy and unresolved contracts; no implemented or verified controls. G0 remains pending. No SR, schema or product approval is added.

INTAKE-GAPS-20261001: WP01, CUS01, FEAT01, SR01/SR27, supporting CUS02/CUS03/CUS08–CUS10 and existing requirements traced below. Backlog: [TK13 #119](https://github.com/fengguode/DATARA/issues/119), [STK009 #181](https://github.com/fengguode/DATARA/issues/181), [STK010 #182](https://github.com/fengguode/DATARA/issues/182). Live Project read/mutation 1 October 2026: Backlog to In progress; Agent System Architect — Feng Guo, W0, orders 200/201/202, no direct prerequisites and discovery/contract preparation gate preserved. This permits gap assessment, not product execution.

Base main `dc2126cbf5a5eb57157e74110e209cb42ea6136e`; branch `codex/wp01-intake-gaps`. Inputs: [merged decisions](../p0-decision-baseline-2026-10-01.md), [proposed implementation contracts](../../p0-design/implementation-contracts.md), [data flow diagram](../../p0-design/diagrams/08-dataflow-security.mmd), [source inventory PR285](https://github.com/fengguode/DATARA/pull/285). Source terms, lawful fixtures and exact field mappings remain open. Source inventory is a separate candidate.

Yi Tang owns the two documents. Feng supplied read-only architecture findings through [the handoff](https://github.com/fengguode/DATARA/issues/119#issuecomment-5925158563) before integration; runtime `/root/feng_decisions` completed, native loading unconfirmed. Publisher fengguode; coordinator Yi `/root`. Independent technical reviewer Dennis Windmaier; final nonauthor documentation/evidence confirmer Wang Xiaofeng. See [review record](../../team/reviews/fit-intake-gaps-review-2026-10-01.md). No SDK, model, application, storage or restore operation was executed.

## Intended flow and unresolved questions

The founder's first pilot is local browser use in China. These are selected directions, not observed controls.

| Stage | Intended policy/boundary | Open contract/evidence | Trace |
| --- | --- | --- | --- |
| Upload identity | Authenticated session determines owner; app endpoint is loopback only. | Every lookup owner binding, CSRF, expiry/change and delayed responses. | CUS01/CUS10; SR01/SR20 |
| Receiving limits | Streamed limits; independent file outcomes. Inclusive 16 MiB/file, 50 files and 128 MiB/batch. | Exactly-at/one-over cleanup, cancel and response-loss retry; policy is not Garmin limits or measured capacity. | SR01/SR02/SR27 |
| Temporary staging | Owner/import-bound bytes pending digest/parse/persistence; durable reconciliation. Abandoned uploads removed within 24 hours. | Physical layout/states, enumeration/access controls, active/stale classification and startup/storage failure cleanup. | SR01/SR03/SR20 |
| Digest/IDs | Completed-byte SHA-256, opaque owner-linked IDs; same-owner same-bytes idempotent. | Digest timing, concurrent uniqueness, safe lookup and equality leakage in UI/API/logs. | SR03/SR04/SR27 |
| Parser/diagnostics | Isolated worker; normalized candidates, provenance, warnings and safe reasons. FIT1/2 and single-session run/cycle are coverage targets. Unknown optional data ignored only with independently verified structure; required unknown semantics reject. Limits 200,000 messages, 100,000 samples, 60 seconds, 512 MiB, one worker. | Exact mappings/integrity, actual isolation/enforcement, termination, malformed output, crash/cancel, reparse versus resume and safe diagnostics. | SR01/SR02/SR27 |
| Accepted persistence | Immutable original and normalized relations, digest and contract/parser/preprocessing versions become visible together through durable staging/reconciliation; independent batch outcomes. | DB/file asymmetry, commit markers, retry idempotency, owner-scoped reconciliation and orphan/partial visibility. | CUS02/CUS03; SR03–SR06/SR20/SR27 |
| Rejected persistence | Whole-file required/integrity rejection; raw bytes discarded promptly; safe disposition metadata. Optional invalid values null only under field contract. | Define promptly, transient retention, protected error metadata, sanitization and cleanup failure behavior. | SR01/SR02 |
| Conflict quarantine | Different bytes with exact (owner, sport, UTC start, elapsed duration) tuple excluded from normal history/snapshots pending resolution. Keep existing, auditable supersession or explicit retain-both preserve valid originals/lineage. | Resolution authorization/atomicity, interruption, quarantine retention and store consistency. Tuple is a heuristic, not authoritative FIT identity. | SR04/SR20 |
| Dashboard/history | Authorized saved disposition/quality/readiness/history; explicit original access; no model calls on viewing. | Foreign-ID existence leakage, digest/diagnostic exposure, UI/stored consistency and stale identity state. | CUS09/CUS10; SR18–SR21/SR31/SR71 |
| Local recovery | Private DB/worker/OpenBao/files with durable local volumes. Daily encrypted backups, seven-day retention; RPO24h/RTO4h objectives. | Named operator, backup destination, key custody, deletion ledger and cross-store restore integrity; objectives unmeasured. | CUS02/CUS08/CUS10; SR03/SR16/SR20 |

## Failure/recovery gap register

Feng owns architecture elaboration in existing tasks; later bounded Worker assignments implement approved contracts and User Tester supplies candidate-specific proof using lawful disposable fixtures. Founder factual input is needed for actual operator/backup/key arrangements. These owner boundaries are follow-through requests, not claims those agents are running.

| Failure | Intended observable outcome | Unresolved contract/evidence | Owner boundary | Existing trace |
| --- | --- | --- | --- | --- |
| Unsupported/malformed/integrity/missing required semantics | Whole-file safe rejection, no accepted partial activity. | Stable taxonomy, exact mapping, independent oracle, safe format. | Architect/Worker/Tester. | CUS01; SR01/SR02/SR27; TC01/TC19/TC25 |
| File/batch limit exceeded | Affected file not accepted; independent completed outcomes visible. | Streaming enforcement, batch accounting, boundary cleanup. | Architect/Worker/Tester. | SR01/SR02/SR27; TC01/TC25 |
| Upload cancel/disconnect | No partial accepted activity; recoverable outcome without duplicate acceptance. | Cancel states, cleanup, resume/restart distinction and response-loss lookup. | Architect/Worker/Tester. | CUS01/CUS02; SR01/SR03/SR04; detailed coverage gap |
| Parser timeout/OOM/crash | No accepted activity; safe terminal disposition. | Actual isolated bounds/termination, recovery and staging cleanup. | Architect/Worker/Tester. | SR01/SR02/SR27; TC01/TC25 |
| File write succeeds/DB fails or reverse | Partial data invisible to ordinary reads/snapshots. | Durable markers, owner-scoped reconcile, idempotent retry and orphan cleanup. | Architect/Worker/Tester. | CUS02/CUS10; SR03/SR20; detailed coverage gap |
| Process crash during batch commit | Per-file atomic visible outcome, independent accepted files survive. | Crash-point cases, uncertain-commit query and restart summary without duplicates. | Architect/Worker/Tester. | CUS01/CUS02; SR01/SR03/SR04; TC01–TC03 |
| Duplicate race/conflict retry | Same-owner exact bytes idempotent; different bytes quarantine visibly. | Pending-first/concurrent uniqueness and uncertain commit/resolution recovery. | Architect/Worker/Tester. | CUS02; SR04; TC03 |
| Temporary/rejected bytes left behind | Prompt rejected cleanup; abandoned cleanup within 24h. | Active/stale classification, locked/corrupt bytes, cleanup failure reporting. | Architect/operator procedure; Worker/Tester. | CUS01/CUS02; SR01/SR03; TC01/TC25 |
| Original missing/corrupt or lineage broken | Detect unavailable evidence; preserve history integrity. | Mark/hide semantics, repair/restore and consistent references. | Architect/operator procedure; Worker/Tester. | CUS02/CUS08; SR03/SR16; TC02/TC11/TC25; detailed gap |
| Identity changes during dashboard request | Current-owner authorization; stale/delayed data cannot appear for another identity. | Cache partitioning, delayed responses, session switch and foreign-ID cases. | Architect/UI Designer; Worker/Tester. | CUS09/CUS10; SR20/SR21/SR71; TC14/TC75 |
| Backup restore/key unavailable | Coherent file/DB/evidence restore; deletion ledger reapplied before serving. | Key recovery, backup destination, restore integrity and measured RPO/RTO. | Architect/operator design; founder factual arrangements; Worker/Tester proof. | CUS02/CUS08/CUS10; SR03/SR16/SR20; TC25/TC26/TC77 |

TC references are planned coverage, not passing evidence. No requirement is verified. TC01/TC14/TC25/TC26 and all detailed product cases remain unrun in this assignment.

## Follow-through

1. TK10 freezes official field/unit/time/integrity mappings after source/artifact rights evidence; decode success does not prove SR27.
2. Existing TK14/TK17/TK20 and security/runtime lanes elaborate duplicate resolution, lifecycle, limits and diagnostics. Map uncovered failures through the normal synchronized registry process; this report changes no registry.
3. Freeze upload/staging/commit/recovery schemas, owner/version bindings and cleanup responsibilities before dependent implementation.
4. Establish actual local runtime/operator, backup destination and key recovery before real data/deployment. Installed containers, service entitlement and legal approval are not inferred from pilot selection.
5. Execute disposable fixture, two-identity, crash/limit and restore checks once software exists. Keep mocks, live models, system verification and founder acceptance separate.

Documentation may pass while product gaps remain open. Merge authorization, G0, rights, mappings, runtime evidence, TC15 and release/deployment remain separate gates.
