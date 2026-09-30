# Verification and final validation plan

Status: planning only; no product verification or final validation has been executed.

## Distinct checks

Verification demonstrates that system requirements are satisfied. Final validation demonstrates that the athlete can complete the intended workflow and understand the results. A schema-valid model answer alone is not proof of substantive quality or useful advice.

## Planned cases

| ID | Case | Method | Expected evidence |
| --- | --- | --- | --- |
| TC01 | Source conformance | Test | Supported, malformed, unsupported, missing-field, unit, and timestamp fixtures receive specified outcomes. |
| TC02 | Original preservation | Test | Original bytes retain their integrity identifier after import and reload; normalized records point to the correct source. |
| TC03 | Duplicate and conflict handling | Test | Upload the same batch twice and submit declared conflict fixtures; duplicate count stays unchanged and conflicts are visible. |
| TC04 | Preparation reproducibility | Test | Run preprocessing twice with inference blocked; normalized values match and no inference requests occur. |
| TC05 | Input scope and provenance | Test | Prepare a narrow period and inspect the payload; no records outside its required scope are included and metrics have source links. |
| TC06 | Skill contract and quality | Inspection and evaluation | Check provider-independent definitions and all required metadata; run approved evaluation cases for each released skill and supported model connection. |
| TC07 | Eligibility rejection | Test | Remove mandatory inputs or fail declared coverage rules; affected skills are blocked with reasons and zero inference calls. |
| TC08 | Model routing | Test | Configure different customer connections; captured requests use the chosen connection, and unavailable access fails without platform fallback. |
| TC09 | Credential protection | Inspection and test | Review the protection design and inspect responses, logs, repository changes, and cross-user access for credential exposure. |
| TC10 | Execution failure handling | Test | Exercise successful output, invalid output, authentication error, and timeout; run states and stored success flags match actual outcomes. |
| TC11 | Result lineage and persistence | Test | Restart services, retrieve historical runs, and re-run the same dataset; lineage survives and earlier assessments remain intact. |
| TC12 | Dashboard use | Test and demonstration | View history, readiness, evidence, and failures while inference access is disabled; no regeneration is required. |
| TC13 | API consistency | Test | An external client retrieves the same saved values and result identifiers as the dashboard; mutation attempts fail. |
| TC14 | User isolation | Test | Use two test users to attempt cross-user access at every declared boundary, including substituted identifiers; all attempts are denied. |
| TC15 | Final P0 user validation | End-to-end demonstration | An athlete uploads a valid batch, checks history and readiness, selects an eligible skill and personal model, runs analysis, interprets evidence, revisits history, and retrieves results externally; repeat with invalid and insufficient data. |
| TC16 | Recommendation coverage | Test | Eligible, insufficient, partial-demand, owned, and marketplace fixtures yield explainable choices without raw-data recommendation payloads. |
| TC17 | Routine execution | Test | Schedule and batch triggers execute the configured scope; insufficient inputs block runs and selected skills and model remain unchanged. |
| TC18 | Comparisons and feedback | Test | Comparisons display relevant version changes and corrections remain distinct from observations and inferences. |

## Release gate

For a fixed candidate commit, all P0 system requirements must have passing checks with reproducible evidence. TC15 must demonstrate the complete user journey and capture founder acceptance. No unresolved defect may violate a P0 requirement; defects that do not affect P0 acceptance must be explicitly documented. Live model integration is separate from mocked routing tests. Report skipped or unavailable live checks as blocked, not passed. Quality thresholds and fixture expected values are established in WP01 and WP03 before execution.

Record runtime versions, setup commands, fixture identifiers and checksums, skill and preprocessing versions, model identifiers, results, defects, and sanitized evidence references. Keep raw personal data and credentials out of the public repository. If controlled local evidence is needed, record its location and review status without claiming a cloud reproduction.

## Release report structure

- Candidate commit and test environment.
- Requirements coverage and actual outcomes.
- Evidence index with reproduction commands.
- End-to-end validation observations and user acceptance.
- Open defects, limitations, and blocked checks.
- Release conclusion and acceptance date.

The project control issue tracks readiness. A task is not verified merely because it is closed.
