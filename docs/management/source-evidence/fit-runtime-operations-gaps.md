# FIT preprocessing runtime and operations gaps

Status: proposed evidence/gap inventory, 1 October 2026; no runtime approved, measured capacity, executed decoder or G0 confirmation. WP02 pre-code preparation: TK20 #126 / STK023 #195 / STK024 #196; CUS03, FEAT03, SR05/SR06/SR28; D01/D05; TC25/TC27. This preparation feeds WP01 G0 without waiving WP02 dependencies.

Authority: [selected D01/D05 baseline](../p0-decision-baseline-2026-10-01.md), [source inventory](fit-source-inventory.md), [implementation plan](../p0-implementation-plan.md). [Assignment](https://github.com/fengguode/DATARA/issues/126#issuecomment-5925628103), [Licun handoff](https://github.com/fengguode/DATARA/issues/126#issuecomment-5925688935), [official source finding](https://github.com/fengguode/DATARA/issues/126#issuecomment-5925705097). Primary GitHub/Project read 06:01–06:05 UTC: all three runtime tasks In progress, Explorer Wang Licun, W0, orders500/501/502, no direct prerequisites; discovery/contract preparation only. No new founder steering in issue activity.

## Resource dimensions and evidence gaps

Every numeric bound below is **selected application policy, unmeasured**. None is a Garmin constraint, demonstrated capacity or service availability promise. Future boundary fixtures must satisfy all other conformance rules.

| Dimension | Selected policy or current gap | Proposed measurement and evidence needed |
| --- | --- | --- |
| Input bytes | 16 MiB/file, inclusive | Count actual received bytes while streaming; exactly-at/one-over cases and middleware/multipart enforcement. |
| Submitted batch | 50 files, 128 MiB aggregate bytes, inclusive | Count files and bytes with independent per-file dispositions; count and aggregate boundary cases. |
| Decoded messages | 200,000/file | Count decoder events and failure peak; synthetic exactly-at/one-over fixtures with lawful independent oracles. |
| Samples | 100,000/file | Count produced samples separately from messages; verify output expansion and rejected-file cleanup. |
| Wall time | 60 seconds/file | Monotonic upload/parse/normalize/persist/cleanup timings; timeout outcome and target machine/fixture identity. This ceiling is not batch latency. |
| Worker memory | 512 MiB/file | Isolated worker OS/container peak RSS/high-water, configured ceiling, OOM/kill outcome and process attribution. No measurements yet. |
| Concurrency | One parser worker/host | Count simultaneous workers and queue depth/wait. Queue strategy, limits and throughput remain unresolved. |
| Staging/cleanup | Prompt rejection-byte discard; abandoned uploads within 24h | Peak staging/temp bytes, crash/abandonment cleanup and cleanup failure outcome. Selected objective, not demonstrated. |
| Persistence/output | No evidenced expansion ratio or storage budget | Original and normalized row/byte counts by activity/session/lap/sample/event; transaction and reconciliation failures. Schema cardinality remains pending. |
| Fixture mix | Proposed cases only | Fixture ID/hash, provenance, bytes/messages/samples, optional/developer fields, disposition and independent oracle. No benchmark artifacts currently available. |

A later bounded spike must record the selected machine/container, process, installed dependencies and actual fixture set. Enforcement, largest realistic density, failure cleanup and repeated execution need actual checks. Limits may need recorded adjustment after evidence; do not silently revise them. No SLA or numeric performance result is asserted.

## Repeat-run diagnostic proposal

STK024/TC27 need comparable records, with explicit `unknown` or `not measured` values where absent. Proposed operations records contain:

- Source SHA-256, provenance/fixture ID and immutable input snapshot reference; source contract/schema version.
- Decoder/package name/version, artifact SHA-256 and verification class (publisher-declared versus locally byte-verified), release commit and profile identity.
- Parser/config version, preprocessing code commit/release, canonical policy/config hash and selected resource caps.
- Exact runtime patch, OS/architecture, container image digest and dependency lock/hash; entrypoint and worker/concurrency setting.
- UTC start/end plus monotonic elapsed duration, per-stage timing, peak RSS, input/output bytes, messages, samples and normalized row counts.
- Safe quality warnings, ignored-field descriptions, failure stage/class/rejection code and cleanup outcome; no keys or raw personal telemetry in diagnostics.
- Canonical normalized output digest excluding generated IDs/timestamps under SR05. A digest alone does not prove determinism: repeated runs must compare canonical normalized content for the same bytes/config/preprocessing version.

These are proposed diagnostic fields, not a frozen public API or UI. SR06 requires deterministic preprocessing with no model inference, including an access-disabled check. SR28 requires schema-versioned canonical inputs bound to immutable snapshots/provenance. Current SR05/SR06/SR28 and TC25/TC27 evidence remains **Not run**.

## Decoder compatibility investigation

The pinned official Python SDK21.217.0 decoder explicitly rejects compressed timestamp records at lines347–348, previously inspected at commit `6db34d7958dce3cef89194e82d6bdc9437c810de` (decoder SHA-256 `afed5ac1876cfe19949c4e0bce24c7fcdb31f72752db79d757be2da59fc23675`). This is static source evidence; it does not imply all FIT files use this encoding or prove any accepted DATARA import. D01 requires the supported target's compressed timestamp conformance, so a direct Python integration cannot be declared ready from release metadata alone.

Garmin's [official SDK distribution table](https://developer.garmin.com/fit/get-the-sdk/) identifies its C# implementation. A bounded alternate-source investigation retrieved tag21.217.0 at commit `025a1957aee81bec33bc26153c4dbcde0051356b` on 1 October 2026. Raw bytes were read and hashed in memory; no vendor code was saved into DATARA, imported, installed, compiled or executed.

| Pinned official source | Actual bytes / SHA-256 | Observed fact and limit |
| --- | --- | --- |
| [Decode.cs](https://github.com/garmin/fit-csharp-sdk/blob/025a1957aee81bec33bc26153c4dbcde0051356b/Dynastream/Fit/Decode.cs) | 20,682 / `3acccc5a6dd4393a14c47497834ef97fee1435b8e0866c0f27adc642953cb385` | Compressed-header branch302–336, reference/offset updates307–309 and415–424. Candidate implementation path; no fixture/conformance/runtime proof. |
| [FitSDK.csproj](https://github.com/garmin/fit-csharp-sdk/blob/025a1957aee81bec33bc26153c4dbcde0051356b/FitSDK.csproj) | 1,345 / `04534a4deaad831968c607bab0fd9b8cc608d4bab945223618d5de3a2a0f2aed` | Declares Garmin.FIT.Sdk21.217.0 and netcoreapp2.0/net46/netstandard2.0 targets. These declarations do not establish an installed or supported runtime. |
| [LICENSE.txt](https://github.com/garmin/fit-csharp-sdk/blob/025a1957aee81bec33bc26153c4dbcde0051356b/LICENSE.txt) | 20,035 / `6cc7ff94b5afc8c3a2b14aeb3e90da97a9fb6c8d40644304da94df5cf56428cf` | Located at the exact tag. No acceptance, applicability or redistribution conclusion. |

The [official FIT protocol](https://developer.garmin.com/fit/protocol/) describes compressed timestamp records and reference/offset reconstruction. It supplies a protocol reference, not an executed oracle or permission to create an unreviewed custom decoder. Product interpretation is recorded in [Yu's issue116 advice](https://github.com/fengguode/DATARA/issues/116#issuecomment-5925553036): investigate another official implementation at the same selected version/coverage; do not omit records, accept partial files, reduce coverage or change the baseline silently.

No alternate engine is selected here. Before adoption: architecture confirmation of the Python application/isolated decoder boundary and revised D05 direct-Python rationale; lawful artifact/fixture use; exact runtime/lock/image pins; worker isolation and resource/cleanup evidence; independent header/CRC/normal/compressed/sentinel/developer-field conformance oracles and repeat-output comparisons. Official source presence does not clear any of these gates. Reducing the selected support outcome or changing SDK21.217.0 would require founder product decision.

## D05 setup and next gates

The selected pilot is the founder in China using a local browser web UI, with a container reference topology. Compatible Windows host/container/runtime installation is not assumed. Python metadata's minimum version is insufficient evidence for current Django/runtime/decoder compatibility. PostgreSQL and private volumes, secret-store integration, operator/key/backup recovery, local transport/cookie settings and exact patch/dependency pins need setup and security evidence. No personal data, provider calls, terms acceptance, purchases or deployment occurred.

Next authorized handoff is independent documentation review of this inventory. A subsequent narrowly assigned compatibility/setup spike can establish measurements and candidate engine facts after its applicable gates; this document does not authorize that execution. Preserve missing results as missing. [Review record](../../team/reviews/fit-runtime-gaps-review-2026-10-01.md) distinguishes document checks from product verification.
