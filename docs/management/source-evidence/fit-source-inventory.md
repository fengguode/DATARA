# FIT source inventory — TK09 / STK001

Status: retrieved source metadata and explicit gaps; no approved acceptance matrix, SDK execution, permitted-use conclusion or G0 clearance. Assignment FIT-EVID-20261001, [TK09 #115](https://github.com/fengguode/DATARA/issues/115), [STK001 #173](https://github.com/fengguode/DATARA/issues/173), WP01 / CUS01 / FEAT01 / SR27 / D01. Base dc2126cbf5a5eb57157e74110e209cb42ea6136e; branch codex/wp01-fit-evidence.

## Authority and retrieval

[Assignment and fresh readiness](https://github.com/fengguode/DATARA/issues/115#issuecomment-5925001241), [Explorer handoff](https://github.com/fengguode/DATARA/issues/115#issuecomment-5925030715), [retrieval findings](https://github.com/fengguode/DATARA/issues/115#issuecomment-5925049900). Yi retrieved official public metadata on 1 October 2026, approximately04:53–05:00 UTC. Initial restricted-shell network reads failed with WinError10013; authorized metadata-only retry succeeded. GitHub/PyPI responses were parsed in memory; no SDK archive, binary fixture or third-party source was saved into DATARA or executed. Read source-document bytes were hashed in memory.

D01 pins21.217.0 through [the merged decision baseline](../p0-decision-baseline-2026-10-01.md). Later upstream releases do not change it automatically. Distinguish SDK release label, generated profile identity, protocol major version and FIT file header profile number. The observed generated profile version does not establish a tested header interpretation.

## Official reference rows

| ID | Source / location | Observed version / identity | Retrieval and what it establishes | Terms / gaps |
| --- | --- | --- | --- | --- |
| SRC01 | [Official Python release](https://github.com/garmin/fit-python-sdk/releases/tag/21.217.0); [tag API](https://api.github.com/repos/garmin/fit-python-sdk/git/ref/tags/21.217.0) | Tag21.217.0; commit6db34d7958dce3cef89194e82d6bdc9437c810de; public release page22 September2026 | Web and API success; immutable commit resolved, not merely mutable main | Release status does not establish usage or sample rights |
| SRC02 | [Generated profile](https://github.com/garmin/fit-python-sdk/blob/6db34d7958dce3cef89194e82d6bdc9437c810de/garmin_fit_sdk/profile.py) | Declares21.217.0Release; generation tag production/release/21.217.0-0-g248b1c46;967399 bytes; Git blob bcab34b4c44474ae01cea98a1d7d4722faec2536 | Pinned API content read/hash success; SHA256 cfc2737638285d1ec09d2972e4bc88b30b4b5a5bc07bfcd843669e7c92cb865c | Header names FIT Protocol License; exact supported field/unit/sport/time mappings and file-header interpretation await TK10 |
| SRC03 | [Pinned project metadata](https://github.com/garmin/fit-python-sdk/blob/6db34d7958dce3cef89194e82d6bdc9437c810de/pyproject.toml) | Project garmin-fit-sdk21.217.0; requires Python>=3.6; SHA256 b3bb3f18638d209e7e00d5e29c4c5d79e895bca057be053de58e8d9cbc0e18aa | API content success; declares conditional typing_extensions dependency for Python<3.8 and development extras | Minimum package metadata is not proof of the chosen supported Django/runtime compatibility. Refers to LICENSE, which was absent at this commit |
| SRC04 | [Official pinned README](https://github.com/garmin/fit-python-sdk/blob/6db34d7958dce3cef89194e82d6bdc9437c810de/README.md) | SHA2561ca501525e87357708a0d2b46b118374d3a3367bf4f050c163ef0cc7b2af9ae6 | API read success; documents installation/decoder configuration and links Garmin documentation | Decoder behavior/options require conformance tests, not inferred from a README or successful decoding |
| SRC05 | [Garmin FIT protocol landing page](https://developer.garmin.com/fit/protocol/) | No pinned document revision obtained | Web read returned navigation/footer only in this retrieval; substantive protocol text not captured | Protocol1/2 target remains selected policy; pinned protocol semantics/integrity/timestamp references are still needed for TC19 |
| SRC06 | [Current SDK license](https://github.com/garmin/fit-python-sdk/blob/main/LICENSE.txt); [observed blob](https://api.github.com/repos/garmin/fit-python-sdk/git/blobs/18f524cedfc0eb54ffa276b4bb0b1e12101669fb) | Git blob18f524cedfc0eb54ffa276b4bb0b1e12101669fb;20035 bytes; SHA2566cc7ff94b5afc8c3a2b14aeb3e90da97a9fb6c8d40644304da94df5cf56428cf | Current main document available; selected commit LICENSE.txt and LICENSE both404, recursive tree confirms no root license file | Current-main text cannot silently stand in for artifact-specific rights. Authorized owner must resolve applicable license/conditions before SDK use, copying or redistribution. No acceptance/legal conclusion recorded |
| SRC07 | [Version-specific package metadata](https://pypi.org/pypi/garmin-fit-sdk/21.217.0/json) | garmin-fit-sdk21.217.0; license metadata null; wheel/sdist below | Metadata retrieved successfully; hashes are publisher-index declarations | Packages not downloaded; actual-byte checksum and archive license contents not verified |

## Candidate package identities

These are published metadata checksums, **not locally verified package bytes**. Package origin is corroborated by the pinned official README/project name. Selecting an install artifact remains setup/rights work; no package installed.

| Candidate | Declared byte size | Published SHA256 |
| --- | --- | --- |
| garmin_fit_sdk-21.217.0-py3-none-any.whl |229766|382bc4cba7cc3e26bd6d65fbf5ad6864cf15feeafcf21dd226e2697df1063e96|
| garmin_fit_sdk-21.217.0.tar.gz |208182|df88c37cb0b28cdebbb1b0aeb9c514b078c832a0ab4e4f4ca14d19ccecd27ed2|

Reproduce metadata discovery: GET the version-specific PyPI JSON and official Git tag/tree/contents API at the pinned commit. Inspect version, file names, sizes, digest labels and HTTP results; hash base64-decoded reference content with SHA256. Do not convert these discovery reads into SDK install/use approval. Keep fetched URLs/version responses and byte hashes distinct from future installed artifact/runtime evidence.

## Handoff and evidence boundaries

TK09 inventory acceptance permits explicit unknowns. The remaining source work is concrete: applicable selected-artifact license and use/distribution conditions; pinned substantive protocol references; TK10 exact acceptance/mapping matrix; runtime-specific artifact-byte verification; independent fixture oracle and rights records from [fixture provenance](fixture-provenance.md). No unsupported variant is approved by discovery. No inquiry to Garmin or license agreement acceptance was performed.

TC24 may inspect this inventory for provenance/terms coverage and explicit gaps; it cannot verify permitted use or decoder conformance. Complete TC19 remains pending until every accepted mapping/conversion/time/integrity rule and oracle is traceable. Registry statuses remain unchanged; no SR is marked verified. [Review evidence](../../team/reviews/fit-source-evidence-review-2026-10-01.md) records actual inspection scope, candidate and limits.
