# TK17 persistent-data history, rights and lifecycle gap report

**Evidence review date:** 2026-10-10  
**Status:** Evidence-linked requirements report prepared for review. This is not legal advice, an approved implementation contract, product verification, or evidence that controls are deployed.

**Traceability:** WP02; TK17 (#123); CUS02/CUS03; FEAT02/FEAT03; SR03/SR28; STK017 (#189)/STK018 (#190); TC24/TC26. Parent TK03 (#270). TK17's acceptance criterion is to cite a source or explicitly record an unknown/owner question for rights, retention, backup/recovery and privacy affecting retained and prepared user data, without inventing legal duties or durations. This report changes neither requirements registry nor task status.

**Attribution:** Compiled by Primary Coordinator Yi Tang as a supporting evidence report for the existing TK17 assignment. The Project still identifies System Architect — Feng Guo as the planned assigned role, Quality Manager — Wang Xiaofeng as quality owner, and the founder as final CUS confirmer. This report does not claim those roles reviewed or authored it.

## Executive result

The P0 direction selects manual owner-supplied FIT imports, persistent original and normalized history, owner deletion, seven-day backup expiry, a deletion ledger reapplied on restore, 30-day operational metadata logs without secrets or raw telemetry, and daily encrypted backups with RPO 24 hours / RTO 4 hours as objectives. These are selected product/engineering directions; this report found no candidate-specific evidence that the corresponding product controls, operator arrangements, recovery process, or objectives have been implemented or measured.

Rights evidence is version-specific. The selected Python SDK is Garmin FIT SDK 21.217.0. The pinned public Git tree for that release has no root LICENSE or LICENSE.txt file even though package metadata refers to a license and source headers name the FIT Protocol License. Garmin's 21.218.00 announcement says LICENSE.txt was re-added to the Python SDK repository on 2026-10-06. That later publication does not itself establish the terms applicable to the selected 21.217.0 artifact. The issue history records the founder's affirmative “Both yes” response concerning license acceptance/permitted-use details and merging documentation PRs #288/#289. Record that decision as made; it does not provide entity/date details, separately prove permission to benchmark or redistribute, or waive restrictions.

No public source reviewed here establishes DATARA's legal basis, notice, jurisdictional duties, or service obligations for processing a user's FIT files. Garmin's website terms and Garmin Connect privacy policy describe Garmin's own services and handling; they do not, by themselves, settle DATARA's rights or responsibilities for a FIT file manually exported and uploaded to DATARA.

**Result:** the evidence supports documenting the chosen policy and identifying implementation/factual gaps. TC24 and TC26 remain “Not run”; no legal conclusion, product verification, or acceptance is claimed. Do not install/use the SDK, reproduce benchmarks, or redistribute SDK/sample content on the strength of this report.

## 1. Evidence and authority

| Ref | Source | What it supports | Boundary |
|---|---|---|---|
| E01 | [TK17 task #123](https://github.com/fengguode/DATARA/issues/123) and its [issue comments](https://github.com/fengguode/DATARA/issues/123#issuecomment-5926958364) | Task scope and acceptance criterion; comment 5926958364 records the official C# 21.217 license text/hash and its described use, SDK-distribution, benchmarking and interoperability clauses. | A source/comment is not a legal applicability determination. The comment explicitly says the interpretation/applicability question remains open. |
| E02 | [Founder response on #123](https://github.com/fengguode/DATARA/issues/123#issuecomment-5927128627) | Founder reply “Both yes”, recorded as affirmative owner confirmation on license acceptance/permitted-use details and authorization limited to merging documentation PRs #288/#289. | No acceptance date or contracting entity is supplied. It is not evidence of separate Garmin permission to benchmark or redistribute, or a waiver. |
| E03 | [Selected P0 decision baseline](https://github.com/fengguode/DATARA/blob/da236f824e384a55713184984cf2162f5454e1d9/docs/management/p0-decision-baseline-2026-10-01.md) | Product/engineering direction for manual FIT import, immutable originals/history, retention/deletion, backup objectives and selected runtime. | Decision selection is not implementation or verification evidence. |
| E04 | [Decision register](https://github.com/fengguode/DATARA/blob/da236f824e384a55713184984cf2162f5454e1d9/docs/management/decision-register.md), [WP01 package](https://github.com/fengguode/DATARA/blob/da236f824e384a55713184984cf2162f5454e1d9/docs/management/wp01-requirements-package.md), and [validation plan](https://github.com/fengguode/DATARA/blob/da236f824e384a55713184984cf2162f5454e1d9/docs/management/validation-plan.md) | Requirements traceability and planned validation. The plan labels TC24 and TC26 “Not run; evidence empty.” | Neither planned case is a pass. |
| E05 | [Pinned Python SDK 21.217.0 source tree](https://github.com/garmin/fit-python-sdk/tree/6db34d7958dce3cef89194e82d6bdc9437c810de); [version-specific PyPI record](https://pypi.org/project/garmin-fit-sdk/21.217.0/) | PyPI identifies release 21.217.0, publisher repository/commit and published wheel/sdist checksums. The exact pinned Git tree was inspected; a root LICENSE/LICENSE.txt was absent, while pinned project metadata refers to a license and source headers name the FIT Protocol License. | Published checksums are not locally verified artifact bytes; no package was downloaded or installed for this report. This is a documentation/source gap, not a conclusion that no license applies. |
| E06 | [Garmin FIT SDK 21.218.00 announcement](https://forums.garmin.com/developer/fit-sdk/b/news-announcements/posts/fit-sdk-21-218-00-release) | Garmin's 2026-10-06 release announcement says the Python SDK LICENSE.txt was re-added to its GitHub repository. | 21.218.00 is a later release; it does not silently change the selected 21.217.0 baseline or answer version-specific applicability. |
| E07 | [Garmin Terms of Use](https://www.garmin.com/en-US/legal/terms-of-use/), [Garmin Connect Privacy Policy](https://www.garmin.com/en-GB/privacy/connect/policy/), and [Garmin global privacy policy](https://www.garmin.com/en-US/privacy/global/policy/) | Context for Garmin's own sites/services and Garmin Connect handling. Garmin publishes a separate Connect policy. | These pages do not establish DATARA's processing basis, notices, retention rights, or duties for user-exported FIT files. No legal conclusion is drawn from them. |
| E08 | Existing [FIT source inventory](fit-source-inventory.md) and [fixture provenance inventory](fixture-provenance.md) | Prior source retrieval details; candidate official samples and synthetic/controlled fixture provenance gaps. | The inventories record that no binaries were acquired, created, executed, or published and that candidate fixture rights/oracles remain open. |

## 2. Selected lifecycle direction versus verified control

The following selections are taken from E03. “Not evidenced here” means this task did not inspect a deployed control or produce an operational record; it does not claim the control is absent.

| Data stage / category | Selected direction | Evidence or gap to close | Trace |
|---|---|---|---|
| Intake and identity | Manual upload of owner-supplied FIT files; app identity/session is server-derived. | Owner authority to provide each file, upload authorization and identity binding need implementation and candidate-specific access evidence. No personal FIT file was accessed for this report. | CUS02/CUS03; SR03/SR28 |
| Original file | Preserve immutable original bytes and their integrity identifier as persistent history. | Storage location, access boundaries, integrity verification, orphan handling and restore consistency are not verified by this document. | CUS02; SR03 |
| Normalized/prepared data | Retain normalized activity/history and links to source; prepared analysis is snapshot-bound. | Category inventory, lineage, snapshot retention/deletion semantics and proof that reads remain owner-scoped are not established here. | CUS03; SR03/SR28 |
| Saved results and evidence | P0 direction retains saved result/history until owner deletion. | Exact evidence rows, derived metrics, logs and result records covered by deletion need to be enumerated in the implementation contract; persistence behavior is not verified. | CUS03; SR03/SR28 |
| Temporary/rejected upload data | Existing policy direction calls for prompt disposal of rejected raw bytes and removal of abandoned temporary uploads within 24 hours. | “Promptly,” transient copies, crash/retry cleanup and failed-cleanup reporting require precise behavior and evidence. | CUS02/CUS03; SR03 |
| Owner deletion | Remove live target data within 24 hours; preserve the deletion ledger needed to reapply deletion during restore. | No deletion-path, ledger protection, backup restore, or post-restore non-resurrection evidence is attached to TK17. | CUS02; SR03 |
| Backups | Daily encrypted backups; seven-day expiry. RPO 24h and RTO 4h are objectives. | No named operator, destination, key custody/recovery, actual backup inventory, expiry record, restore rehearsal or measured RPO/RTO is evidenced here. Do not present objectives as achieved service levels. | CUS02; SR03 |
| Operational logs | 30-day metadata logs; exclude credentials/secrets and raw telemetry. | Actual event fields, storage/rotation, access, redaction and deletion are not inspected or tested here. | CUS02/CUS03; SR03/SR28 |
| Personal data and privacy | Owner-controlled local browser pilot in China is the selected context; avoid collecting data unnecessary to the declared skills. | Local deployment does not alone settle notice, purpose, access, export/deletion, incident, jurisdiction, or third-party processing questions. The applicable requirements and user-facing disclosures need an evidence-backed owner/qualified review. | CUS02/CUS03; SR03/SR28 |

The selected periods above are product-policy inputs, not statements of statutory retention periods. No additional retention duration, legal duty, RPO, or RTO is invented by this report.

## 3. Rights, source, and fixture gaps

### 3.1 SDK and source terms

The source inventory pins Garmin FIT Python SDK 21.217.0 to commit 6db34d7958dce3cef89194e82d6bdc9437c810de. PyPI reports the version-specific source archive SHA-256 as df88c37cb0b28cdebbb1b0aeb9c514b078c832a0ab4e4f4ca14d19ccecd27ed2 and wheel SHA-256 as 382bc4cba7cc3e26bd6d65fbf5ad6864cf15feeafcf21dd226e2697df1063e96; these are publisher-declared values, not locally recalculated hashes. No package was downloaded or installed.

At the selected source commit, no root LICENSE/LICENSE.txt was present in the public Git tree. The package metadata refers to a license and source headers name the FIT Protocol License. Garmin later announced that release 21.218.00 re-added LICENSE.txt. Thus the evidence question is how the license applies to use of the selected 21.217.0 artifact and which versioned terms/evidence should accompany it—not whether a later file can be treated as if it had been present in the selected commit.

The founder's recorded “Both yes” response is preserved as an affirmative decision on the question actually asked. Before SDK execution, measurement/benchmarking, copying or distribution, the project still needs evidence that the proposed act is within the accepted terms and technical/runtime gates. The existing C# license comment records restrictions that make benchmark/competitive analysis and distribution especially important to clarify. No SDK was executed and no permission request was sent to Garmin in this work.

### 3.2 FIT files and fixtures

The product direction includes user-supplied files, including files a user obtains through Garmin Connect Export File. It does not establish that DATARA may publish a user's bytes or upstream samples. Existing fixture inventory identifies:

- DATARA-authored synthetic fixtures as a future option; generator, binaries, expected values and independent oracle do not yet exist.
- Upstream official sample paths at the pinned SDK commit; binaries were not acquired, and redistribution/use terms plus expected-value oracles remain open.
- Controlled athlete examples as a future private option only; no file or permission was supplied, and personal telemetry must not enter this public repository.

Before a fixture is used, its author/origin, acquisition or generation date, source/profile, rights decision, intended supported/unsupported case, hash, expected disposition, independent oracle and reviewer must be recorded. A user's upload is not permission to publish the file. Decoder output alone is not its own independent oracle. TC24 can inspect whether these records are complete; it does not grant rights or prove semantic conformance.

## 4. Explicit unknowns and owner/factual inputs

These are evidence gaps for the existing TK17 lane, not a repeat of the already answered “Both yes” question.

1. **Selected-artifact terms record:** What exact authoritative versioned license text and artifact identity should the project retain alongside the accepted 21.217.0 baseline, given the missing root license at its source commit and the later 21.218.00 addition? No conclusion that the license is absent or inapplicable is made.
2. **Permitted actions:** The recorded founder response does not contain entity/date detail or a separate permission to benchmark or redistribute. Before any such action, obtain the applicable scoped confirmation/qualified interpretation from the responsible owner; until then, do not benchmark or redistribute SDK/sample content.
3. **User-upload authority and fixture rights:** What evidence is required to document that an uploader may supply a file for personal analysis, and which fixtures may be used in tests or published? Existing direction distinguishes user upload from public sample distribution; implementation-ready acceptance criteria remain to be reviewed.
4. **Data inventory and deletion boundary:** Which concrete tables/files/caches/derived snapshots/results/evidence/logs and temporary copies are included in the selected owner-deletion promise? Define how the 24-hour live deletion and restored deletion ledger are observed without exposing private athlete data.
5. **Operational ownership and recovery facts:** Who will operate the local deployment, where encrypted backup material resides, who controls/recover keys, how expiry is observed, and what non-sensitive evidence can establish restore integrity and measured RPO/RTO? No operator or arrangement is inferred.
6. **Privacy and user-facing disclosure:** Which categories/purposes, user controls, local access boundaries, and any relevant third-party transfer/processing disclosures are needed for the actual pilot? The selected China/local-browser context does not itself resolve these factual or legal questions. Qualified owner review is needed before a public compliance claim.
7. **Implementation evidence:** No source inspection of deployed retention, deletion, log rotation, backup or restore controls is recorded here. Record candidate commit and environment only when those checks actually run; never put raw FIT data, personal telemetry, credentials or private connection details in public evidence.

## 5. Validation and follow-through

| Evidence case | Planned purpose | Current result |
|---|---|---|
| TC24 | Inspect official source/fixture provenance and terms; keep unresolved rights explicit and avoid unsupported legal conclusions. | **Not run.** This report is a candidate artifact for that inspection; it is not an independent TC24 pass. |
| TC26 | Inspect lifecycle choices and identify source-backed decisions versus explicit gaps without invented periods, duties, RPO or RTO. | **Not run.** This report does not verify product controls. |

Next steps stay within the existing project backlog and its gates:

1. Feng Guo, in the already assigned System Architect role, reviews this evidence matrix against TK17 and its linked CUS/SR records; Wang Xiaofeng provides independent QA/evidence confirmation as assigned. This report is not attributed to either reviewer.
2. Resolve only material evidence/contract questions through the existing GitHub task and decision records, preserving the founder's existing “Both yes” decision and its scope.
3. Keep fixture rights, exact SDK/artifact conditions, lifecycle contract, operator facts, implementation, and tests as separate evidence gates. A report or documentation merge does not authorize SDK use, product-data access, deployment, release or athlete acceptance.
4. Update the requirements registry only if review establishes an actual traceability or requirement change; then run the required requirements checker. This report alone changes no registry.

### Evidence quality notes

- Official Garmin/PyPI material was consulted as cited above; the issue and repository records are the project-authoritative source for selected decisions and traceability.
- External source and package contents were inspected as public text/metadata only. No SDK/package install, execution, source/sample redistribution, personal FIT access, database action, provider call or product test was performed for this report.
- Package checksums above are copied from PyPI's release record, not reproduced locally.
- This report is newly prepared source documentation. No independent technical review or Quality Manager confirmation has yet been performed on this file.

## Agent attribution

**Primary Coordinator — Yi Tang**  
Model configuration requested/available in project settings: gpt-6-luna, reasoning high. Harness: Codex. Effective model/backend loading was not independently observed for this run.
