# WP05 / TK64 focused boundary evidence

Status: focused synthetic checks passed; PostgreSQL, full-suite, and athlete validation remain not run.

## Candidate and scope

- Source candidate: `6a62ddfc858e6fe6e618d9e14fcf96ee87769c83` (`feat(WP05): add authenticated saved-metric read surface`).
- Task: [#378](https://github.com/fengguode/DATARA/issues/378), WP05 / TK64.
- Traceability: CUS09, CUS10; SR19, SR20, SR21, SR31, SR73.
- Decision basis: [saved-history contract #369](https://github.com/fengguode/DATARA/discussions/369) approved by the founder; [same-origin session decision #422](https://github.com/fengguode/DATARA/discussions/422) option A selected by the founder.
- Environment: Windows; Python 3.12.10; Django 5.2.17; candidate worktree `codex/wp05-saved-history-current`.
- Database override: explicit SQLite `:memory:` for the focused unit checks only. No PostgreSQL server, database migration, or persisted session was used.

## Actual checks

Command, with `DATARA_ENV=milestone-a-local`, `DATARA_DB_ENGINE=sqlite`, `DATARA_DB_PATH=:memory:`, and `DATARA_TEST_RUNNER` empty:

```text
python manage.py test datara.tests.test_app_surface datara.tests.test_session_identity --verbosity 2
Ran 14 tests in 0.354s
OK
Found 14 test(s).
Skipping setup of unused database(s): default.
System check identified no issues (0 silenced).
```

The 14 checks comprise eight focused A1–A8 boundary tests and six session-boundary tests. They are synthetic tests. The store-facing tests use mocks; they do not prove a successful authenticated database session or real cross-owner rows.

## Mutation outcomes

Each mutation was applied alone, its corresponding focused test was run, and the mutated file was restored byte-for-byte before the next mutation. Every mutant exited nonzero:

| Case | Temporary mutation target | Observed detection |
| --- | --- | --- |
| A1 | `datara/settings.py`: change `ROOT_URLCONF` from `datara.urls` to `datara.missing_urls`. | Focused A1 command exited 1; Django raised `ModuleNotFoundError: No module named 'datara.missing_urls'`. |
| A2 | `datara/tests/test_app_surface.py`: limit `DiscoverRunner.build_suite` to `datara.tests.test_app_surface`, omitting the existing saved-metric module. | Focused A2 command exited 1; collection assertion reported 8 IDs, not greater than 200. |
| A3 | `datara/app_surface.py`, in `_json_response` after `json.dumps` and before `HttpResponse`: temporarily replace response bytes `1700000000` with `1700000001`. The fixture and expected DTO were unchanged. | Focused A3 command exited 1; byte-parity assertion compared `...1700000001...` with the unchanged saved bytes `...1700000000...`. |
| A4 | `datara/saved_metric_read.py`, in the owner-scoped `MetricStoreRefusal` branch: include the requested metric ID in the refusal body. | Focused A4 command exited 1; the foreign-ID and missing-ID response bodies differed. |
| A5 | `datara/saved_metric_read.py`, in the metric read: pass `request.headers.get("X-Datara-Owner-Id")` to `SavedMetricStore.for_user` instead of `request.user`. | Focused A5 command exited 1; the store-owner assertion received the client header value instead of the server user. |
| A6 | `datara/saved_metric_read.py`, in `_response_preflight`: replace the anonymous-authentication condition with `if False`. | Focused A6 command exited 1; the anonymous request reached a non-denial path and errored while serializing the mock result. |
| A7 | `datara/app_surface.py`: add `import socket` to the read-surface module. | Focused A7 command exited 1; the forbidden-import scan reported `socket`. |
| A8 | `datara/saved_metric_read.py`, in the owner-scoped metric read: call `prepare_and_save_metric(metric_id)` before `get_metric`. | Focused A8 command exited 1; the test received 503 instead of the expected 200 after the forbidden recomputation call. |

Each focused mutant command used the exact method name from the corresponding test and this form:

```text
python manage.py test <fully-qualified-test-name> --verbosity 0
```

All eight mutant runs exited `1`; the details above are their observed failure signatures. The probe kept byte snapshots of the four production/test files it could mutate and restored them in `finally`. After the probe, `git diff --exit-code HEAD -- datara/settings.py datara/tests/test_app_surface.py datara/app_surface.py datara/saved_metric_read.py` exited `0`, confirming those four paths match the source candidate. Their post-probe SHA-256 values were:

| Path | SHA-256 after restoration |
| --- | --- |
| `datara/settings.py` | `bd9068467539303ce3bb87dd3b2fb4745944244f93a381882c7697b93296557e` |
| `datara/tests/test_app_surface.py` | `48abece7926faa018d3dbfe7e1bb9d289b18f33b88c425fc2e3d0a92bc1cb055` |
| `datara/app_surface.py` | `95d2fc17f11d1956c69baa353d1d06f4e1bcae68e425992581042e248e93d59b` |
| `datara/saved_metric_read.py` | `187c7850c6fe6ee43edb21de1f4228a76f6a67da94533d30ac10bebeb7733e88` |

After mutation probing, the candidate files were restored and `git diff --exit-code` against the source candidate was clean for every path the probe could modify. The focused 14-test pass above was run against the unmutated source before the mutation probe.

## Evidence limits and remaining gates

- **A2 is partial:** collection covers more than 200 existing test IDs and includes the two WP05 test modules, but the existing suite was not executed. It therefore does not establish that no previously passing test regressed.
- **A3/A4/A5/A6/A8 are boundary-level proofs with a store double/request factory.** Real persisted-value parity, two-user database isolation, and authentication lifecycle across a migrated session store remain unverified.
- **A7 is a scoped source/import and socket-mock check,** not a complete transitive dependency audit or live egress observation.
- No PostgreSQL 17 service/instance was available. No schema/session migration, database-constraint suite, or complete product suite was run.
- No successful end-to-end login, authenticated saved-metric retrieval, rendered browser acceptance, TC15 athlete journey, founder acceptance, deployment, or release is claimed.
- No provider/model call, credential access, or network egress was performed by these focused checks.

Required next evidence: run the candidate's approved persistence/session and cross-user checks on the authorized fresh disposable PostgreSQL test database; then execute the applicable full suite and capture actual login/session and route behavior. Until then this increment remains source-reviewed with focused synthetic boundary evidence, not verified or accepted.
