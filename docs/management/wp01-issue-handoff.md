# WP01 GitHub issue handoff

GitHub issue mutation was not available from this environment. The text below is prepared for a maintainer to post; it has **not** been posted.

## Issue #1 — WP01 status update

> **Status: ready for requirements review; not accepted or complete.**
>
> Proposed baseline: `docs/management/wp01-requirements-package.md`.
>
> Scope delivered: proposed Garmin FIT source/normalization/validation/dedup contract and synthetic fixture plan; three provider-independent elemental-skill candidates; common skill I/O and model-adapter contracts; predefined training-volume/readiness dashboard outcome and read-only `/api/v1` contract; dependency plan TK01–TK08 spanning WP01–WP07.
>
> Affected IDs: CUS01–CUS10, SR01–SR21, new SR27–SR31, TC01–TC15, new TC19–TC20. P1 CUS11–CUS13/SR22–SR26 remain bounded to WP07.
>
> Blockers/decisions: D01 official Garmin evidence and fixture/license/limits/conflict policy; D02 shortlist and evaluation thresholds; D03 provider connection and credential design; D04 dashboard/API details; D05 stack only after contracts. Official web attempts were denied (HTTP 401/403), so FIT/provider specifics remain pending rather than asserted.
>
> Actual management check: `python3 scripts/check_requirements.py` (record the PR run result). No product tests, model integration, system verification, athlete validation, or founder acceptance were run or claimed.

## Issue #8 — control hub status update

> WP01 has a reviewable proposed requirements baseline. CUS → SR → task → planned-validation traceability now includes TK01–TK08 and contract cases TC19–TC20. All verification cases and VAL-P0 remain `Not run`; the registry check only establishes internal link integrity. Do not start WP02 until the necessary WP01 contracts are approved. Do not select the application stack under D05 yet. Link the review pull request and candidate commit here after publication; do not merge or mark accepted without founder review.
