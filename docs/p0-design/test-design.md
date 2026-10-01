# P0 comprehensive test design

Status: proposal only; no product validation has run. Existing test definitions and IDs remain in the [validation plan](../management/validation-plan.md), and the complete prospective oracles/fixtures/gates are in [test-design-findings.md](test-design-findings.md). Do not change canonical case statuses from `Not run` based on these documents.

## Scope and test levels

Designed coverage spans unit/deterministic transforms, component/schema contracts, disposable-database integration, mocked adapter integration, fixed-candidate system checks, actual rendered browser acceptance, live-model integration, and separate athlete/founder validation. Evidence at one level cannot substitute for another. Each case records its environment, fixture provenance/hash, commit, versions, command, observable result and sanitized evidence reference.

## Canonical cases

| IDs | Coverage | Applies to |
|---|---|---|
| TC01–TC05 | FIT acceptance, original preservation, duplicates/conflicts, reproducible preparation, scoped/provenance-bound skill inputs | WP01–WP03; CUS01–03, SR01–07/SR27–28 |
| TC06–TC07 | versioned skill quality/contract, deterministic ineligibility | WP03; CUS04–05, SR08–11/SR29 |
| TC08–TC10 | explicit selected connection, secret protection, run state and failures | WP04; CUS06–07/SR12–15/SR30 |
| TC11–TC14 | append-only lineage, dashboard saved reads, API contract, cross-user isolation | WP05; CUS08–10/SR16–21/SR31 |
| TC15 | full P0 user journey and separate final athlete validation | WP06; CUS01–10 |
| TC19–TC20 | official source evidence and cross-contract conformance | WP01–WP05; CUS01, CUS03–06, CUS09/SR27–31 |

TC16–TC18 cover P1 recommendations, routines and comparisons; they are out of this design baseline. Retain their planning records, but do not use them as P0 acceptance cases.

## Additional candidate coverage

The traceability audit identifies recovery, deletion, backup/restore, operations, migration/rollback, and expanded accessibility tests needed before final system acceptance. These should receive canonical SR and TC identifiers after the registry merge markers are reconciled. Until then they are gap candidates, not silently added verification cases. No candidate is run or passed.
