# FIT fixture provenance inventory — TK09 / STK002

Assignment FIT-EVID-20261001; [STK002 #174](https://github.com/fengguode/DATARA/issues/174), parent [TK09 #115](https://github.com/fengguode/DATARA/issues/115); WP01 / CUS01 / FEAT01 / SR27 / D01 / TC24. Status: candidate-source inventory with explicit unknowns; no fixture binaries acquired, created, executed or published.

Explorer Wang Licun searched repository paths for fit/fixture/sample/garmin and found no matching artifact set. Existing manifests and test scenarios are proposals. Primary official tag-tree inspection identified upstream sample paths, without downloading binary content. [Source inventory](fit-source-inventory.md) distinguishes current SDK license text from missing license paths at the pinned release.

| ID | Candidate origin / location | Available provenance | Terms / owner question | Hash, oracle and disposition |
| --- | --- | --- | --- | --- |
| FIX01 | Future DATARA-authored synthetic running/cycling activities, indoor/outdoor | Authorship/generator is proposed; no generator or binary exists | Record actual author and independent generation method; determine any SDK-derived code/output conditions before generation/publication | Artifact hash unavailable; exact expected values and byte-structure oracle require independent TK10 review; not ready for fixture use |
| FIX02 | Upstream pinned SDK tests/fits/ActivityDevFields.fit at commit6db34d7958dce3cef89194e82d6bdc9437c810de | Path exists in official recursive Git tree; binary not downloaded | Applicable license/sample redistribution rights unresolved; owner review required | SHA256 unavailable; no verified independent expected values; candidate for developer-field behavior only, not accepted semantic support |
| FIX03 | Same pinned tree tests/fits/HrmPluginTestActivity.fit | Official upstream path, no binary acquired | Same explicit source/sample rights gap | No byte hash/oracle established; candidate sample only |
| FIX04 | Same pinned tree tests/fits/WithGearChangeData.fit | Official upstream path, no binary acquired | Same explicit source/sample rights gap | No byte hash/oracle established; no new sport/gear semantics approved |
| FIX05 | Separately permissioned controlled athlete example, supplied privately in future | No file/owner/permission supplied | Need actual owner authorization for processing and any intended restricted sharing; never infer public repository permission from upload. Do not request personal telemetry for public Git | No hash/oracle; private evidence location to be agreed before acquisition; not a publication candidate |

[Upstream candidate directory](https://github.com/garmin/fit-python-sdk/tree/6db34d7958dce3cef89194e82d6bdc9437c810de/tests/fits). These rows inventory every candidate source presently identified; they do not claim exhaustive FIT variant coverage or fixture rights.

## Future fixture manifest and independent oracle

Before a fixture is used, record artifact ID/path/hash; origin/actual author; acquisition/creation date; generator/tool version; applicable source/profile identity; rights/permission decision and evidence; intended supported/unsupported variant; expected file disposition and reason; explicit normalized values and metric references; independent expected-value reviewer/method. A generator and decoder sharing the same erroneous mapping cannot be the sole oracle. Byte mutations must record original hash, mutation method and independent expected failure. Personal examples remain outside Git and public logs; sanitized evidence must retain enough provenance to reproduce authorized checks.

Initial synthetic design coverage follows the selected scope: supported single-session runs/cycles with and without optional GPS/HR/distance; missing required values; invalid sentinels/structure/integrity; byte-identical repeat and different-byte logical conflicts; resource boundary cases; UTC boundaries; unknown/developer fields and unsupported layouts. This is proposed coverage, not generated artifacts, passing tests or approved detailed wire mappings.

## Questions and gates

The license applicability gap does not block publishing an inventory of public references and unknowns. It does block assuming lawful SDK use/sample redistribution. Resolve actual terms and owner decisions before dependent install/use/copy. Fixture generators/oracles require approved TK10 mappings; no useful controlled fixture set exists yet. TC24's inspection can assess whether these unknowns are explicit. Complete TC19/source conformance and product tests remain pending. No SDK/sample terms accepted and no external permission request sent.
