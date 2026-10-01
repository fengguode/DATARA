# Duplicate and conflict policy comparison

Status: proposed research output, 1 October 2026. DUPLICATE-OPTIONS-20261001 / WP01 / TK14 #120 / STK011 #183 / STK012 #184 / CUS02 / FEAT02 / SR04 / D01 / TC03. No new policy, schema freeze or implementation evidence.

[Selected D01](../p0-decision-baseline-2026-10-01.md) governs the choice. Older [WP01 alternatives](../wp01-requirements-package.md) preserve historical rationale; their undecided choice wording does not reopen the delegation. [Feng's attributed handoff](https://github.com/fengguode/DATARA/issues/120#issuecomment-5926831364) and [authoring assignment](https://github.com/fengguode/DATARA/issues/120#issuecomment-5926886049) supply scope. Fresh Project 07:35 UTC: TK14/STK011/STK012 In progress, Architect Feng Guo, W0 orders300–302, no direct prerequisites. Native configuration loading unconfirmed; primary publisher fengguode.

## Historical options and selected behavior

Examples below are conceptual policy examples, not actual telemetry, FIT artifacts or independent test oracles. X and Y denote otherwise valid file bytes; A and B denote authenticated owners.

| Option | Observable example/outcome | Limits and status |
| --- | --- | --- |
| Exact bytes only | A submits X twice: second submission refers to existing history. Different Y, even if it represents the same activity, proceeds as a separate import. | Detects identical re-import; can leave duplicates from changed exports. This is the selected idempotency layer, not the full D01 policy. |
| Documented tolerance key | Different X/Y within a hypothetical sport/start/duration tolerance would flag a possible conflict. | Historical option. No thresholds are evidenced or selected; approximate matching could flag different activities. No tolerance is invented here. |
| No logical detection | Identical bytes still follow exact-byte idempotency; different bytes are separate imports even with the same logical activity. | Historical option, not selected. Changed exports can duplicate recorded history. |
| Selected exact tuple with explicit resolution | A submits different Y matching X's exact `(owner, sport, UTC start, elapsed duration)`: quarantine Y as a possible conflict. A mismatch in any tuple component does not match this heuristic; other conformance checks still apply. | Selected application heuristic, not authoritative FIT identity. Can flag legitimate coincident activities and miss the same activity with changed tuple fields. User resolves surfaced conflicts explicitly. |

The founder delegated the D01–D05 selection to Yi/Yu; the recorded selection supersedes the old task text requesting an undecided founder choice. No additional founder endorsement is inferred from this comparison. Changing the outcome remains a separately recorded product decision.

## STK011 — owner-scoped exact-byte trace

| Conceptual scenario | Selected observable result | Contract/test gaps |
| --- | --- | --- |
| A submits accepted X again | Same owner and SHA-256 references existing history, no duplicate accepted activity. | Lost-response replay, repeated rejected/staged bytes, concurrent arrival and exact transaction outcome need frozen rules. |
| B submits the same X | Owner-scoped handling; no access to A's original, digest match or history. | Isolation and lookup responses must prove no cross-owner disclosure with two disposable users. |
| A submits a changed export Y | Exact-byte idempotency does not match; evaluate the selected logical tuple and other validity checks. | Canonical sport/start/duration representations and precision need approved field/schema mappings. |
| Concurrent A/X requests | Final accepted history must remain owner-idempotent. | Lock/constraint/job/staging semantics, conflict disposition and crash recovery are unresolved; no implementation prescribed here. |

Raw originals are immutable. Accepted original/normalized relations appear as one visible operation under D01; file/DB staging reconciliation must prevent a retry from creating a second accepted activity after a partial commit. The exact byte idempotency outcome is selected, but storage and race mechanics still require contracts and actual checks.

## STK012 — logical conflicts and resolution

| Conceptual scenario | Selected direction | Explicit remaining work |
| --- | --- | --- |
| A/X and A/Y differ in bytes, equal exact tuple | Quarantine Y as a possible conflict; exclude unresolved candidates from normal history and skill snapshots. | Quarantine state, visible explanation and permitted fields/IDs; no hidden auto-merge. |
| Tuple differs | No match from this heuristic; import only if every other conformance/eligibility check passes. | Explain that the heuristic misses changed tuple values; no comprehensive deduplication claim. |
| Keep existing | User explicitly resolves in favor of existing history. | Candidate lineage/state, visibility and lifecycle/deletion behavior must be specified. |
| Replace | Auditable supersession; preserve valid originals and lineage. | Atomic transition, interrupted resolution and references from old snapshots/results must remain historical and resolvable. |
| Retain both | User explicitly chooses both. | Record the resolution and prevent unchanged repeated submissions from silently creating more accepted copies. Exact re-import semantics after resolution need contract examples. |
| Concurrent/interrupted resolution | Only authorized owner actions may alter conflict state. | Version/race response, durable recovery and safe retry; no silently lost resolution or supersession. |

Owner identity comes from authenticated server context. Conflict reads, resolution targets and source references require authorization. Existing [intake gap evidence](fit-intake-operations-gaps.md) identifies file/DB reconciliation, logging and access questions; this comparison does not implement those controls. D04's selected retention/deletion policy must be reconciled with conflicts, supersession, backup recovery and immutable historical references; this document assigns no new retention period.

## Trace and remaining evidence

[SR04 and system requirements](../system-requirements.md) require owner-scoped repeat import without duplicate accepted activity and visible conflicts without silent overwrite. TC03's historical undecided-choice oracle needs reconciliation against the selected D01 behavior before implementation/verification, including changed bytes/equal tuple, changed tuple, separate users, explicit resolutions and races. Conceptual examples above are not frozen fixture oracles. TC03 and SR04 remain **Not run / unverified**.

Next contract work must settle mapping precision, staged/concurrent imports, authorized atomic resolution, supersession lineage, snapshot/result references, cleanup/crash/retry and deletion/backup behavior. Follow the existing backlog and [implementation plan](../p0-implementation-plan.md); this research output does not clear G0 or authorize coding. [Review record](../../team/reviews/duplicate-options-review-2026-10-01.md) holds documentation evidence separately from product checks.
