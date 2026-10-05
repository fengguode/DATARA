# Windows phase command contract

Control #8 / WINDOWS-PHASE-COMMAND, Priority P0; WP03 / CUS03 / FEAT21 / SR07,
SR28, SR34; D05 environment readiness. Implements the reviewed proposal in
[Discussion 341](https://github.com/fengguode/DATARA/discussions/341#discussioncomment-18714861).
This is source implementation. No runtime, installation, database permission,
product verification, acceptance or release evidence accompanies it.

## Native invocation

Run one explicit phase per process from an authorized private environment:

```powershell
powershell -NoProfile -File scripts/milestone_a.ps1 -Phase inspect -Python <absolute-python-path> -Venv <absolute-venv-path>
```

`Phase` accepts only `inspect`, `install`, `migrate`, `test`, or `app-check`.
The candidate contract requires native Windows Python **3.12.10**, PostgreSQL
**17.11**, `DATARA_DB_ENGINE=postgres`, `DATARA_DB_HOST=127.0.0.1` and
`DATARA_DB_PORT=55432`. These are reported candidate settings requiring future
executed evidence, distinct from the Linux/container reference topology.
Optimized Python is refused. No implicit dependency installation occurs outside
`install`; no SQLite fallback occurs in this Windows path.

The interpreter pin was **3.12.14** and was moved to **3.12.10** by recorded
founder decision; see
[the pinned-environment decision record](../management/pinned-environment-decisions-2026-10-05.md).
3.12.14 has no official Windows build, so the original pin was unsatisfiable on
this platform. The pin itself is retained: an unpinned interpreter is still
refused.

### Parity break: the `test` phase pins a test database name prefix

**The `test` phase on this platform requires the disposable database name to
begin `test_datara_history_`.** This is not a convention of this document; it is a
hard requirement enforced elsewhere, and it is a **platform parity break**.

The cause is `datara/tests/test_metric_history_process.py:66`, which asserts that
the configured test database name starts with `test_datara_history_`. Three tests
fail when the name does not, **even though the name is otherwise perfectly
conformant with the runner's own validation rule**
(`scripts/milestone_a_runner.py`, the `test_datara_[a-z0-9][a-z0-9_]{7,49}`
pattern). Reproduced: a name satisfying that regex but not the hard-coded prefix
produces exactly three unrelated failures.

**Why this belongs in the command contract.** Without it, a reviewer reproducing
a `test` phase result on a different but equally valid database name sees three
failures, reasonably concludes the branch regressed, and reports a defect that
does not exist. Worse, any recorded pass figure becomes non-reproducible for
reasons that have nothing to do with the code under test. A reader must be able
to tell a real regression from a naming mismatch without reading a test file.

**Independently reproduced.** With `DATARA_TEST_DB_NAME` set to a name that
satisfies the runner's regex but not this prefix, the suite previously reported
`FAILED (failures=3)` and exited 1, with exactly the three named failures — a
regression that does not exist.

**Now fixed in the runner, and this section describes the enforced rule rather
than a workaround.** `scripts/milestone_a_runner.py` validates the prefix
alongside its own `TARGET` regex, so a non-conforming name is **refused up front**
with a message naming the requirement, instead of surfacing later as three test
failures whose cause the operator did not choose.

The suite's requirement is the binding one and was deliberately **not** weakened.
`datara/tests/test_metric_history_process.py` spawns a child Python process that
connects to the disposable database for real, and that child refuses any other
name — a safety guard proving it cannot reach a real database. Loosening it
to accept arbitrary names would have removed that guard.

Verified after the change: a `TARGET`-conformant non-prefixed name now exits 1
with `REFUSED: test database name must begin 'test_datara_history_'`; a
prefixed name still runs `Ran 316 tests`, `OK`, exit 0.

| Phase | Explicit DATARA_DB_USER / DATARA_DB_NAME | Action |
| --- | --- | --- |
| inspect | One of the three pairs below | Interpreter/dependency/candidate identity and nonmutating connection/role metadata |
| install | No database connection | Create a missing venv and install the committed exact dependency set |
| migrate | datara_migrator / datara_local | Django system check and migration with syncdb in the existing owned database |
| test | datara_test_runner / datara_testsandbox | Existing Django suite in a newly created explicitly named disposable database |
| app-check | datara_app / datara_local | Django system check and connection/role metadata only |

Set connection credentials privately through process environment or approved
connection authentication. No password command-line argument exists. The command
never grants privileges, creates roles, bootstraps the base databases or starts
services. Each role change requires a separate invocation with the corresponding
explicit connection tuple. `inspect` reports attributes without inferring missing
privileges. Migration and application roles must have no CREATEDB; all connected
roles must have no superuser/BYPASSRLS. Migration requires database ownership;
application checks refuse owned user-schema relations. These metadata guards do
not establish application isolation or all effective permissions.

## Installation and identity

Installation uses the venv's existing pip and does **not** upgrade it automatically.
Output records actual pip, Python and dependency versions, the committed lock SHA256,
Git candidate SHA and changed paths, and shell version. Installation output is captured
and withheld on failure because installer diagnostics can contain private URLs.
Exact lock pins are checked after installation and before database phases. A lock hash
identifies the pin file; it is not a wheel integrity hash. Package/runtime downloads
and their rights remain later authorized setup operations.

PowerShell captures each native process exit code and propagates it. Python propagates
installer/test exit status; refused inputs and sanitized unexpected errors exit 1.
Unexpected exception messages are suppressed, including database connection errors.
No phase chain silently continues after a failure.

## Fresh test lifecycle

Supply `DATARA_TEST_DB_NAME=test_datara_history_<safeid>` explicitly. The name
**must** begin `test_datara_history_` — the runner refuses anything else before
creating a database, with a message saying so; see [the prefix requirement](#the-test-phase-pins-a-test-database-name-prefix)
above for why. After the prefix, the safe ID consists of 7–42 lowercase ASCII
letters, digits or underscores and begins with a letter or digit.

Two limits bound that length, and the smaller one wins:

- **PostgreSQL identifiers are capped at 63 bytes.** The 21-byte prefix leaves
  **42** bytes for the safe ID.
- **The runner's own regex caps the whole name at 61 bytes**
  (`test_datara_` + 1 character + up to 49), which leaves **40**.

So the usable safe-ID length is **7–40**, and a name longer than that is refused.
Choose a unique run ID before execution. Names for the preserved database,
sandbox base, `postgres`, `template0` and `template1` cannot be test targets. Test
reuse, parallel database clones and mirrors are refused.

The runner factory replaces PostgreSQL's database-creation object for this invocation.
It checks for a collision through the explicit `postgres` maintenance connection,
then issues CREATE directly. A collision after that check fails at CREATE, with no
interactive reset, automatic DROP or retry. Django's normal migrations execute only
after connection switching to that newly created target. The sandbox is a connection
base, never the test target. `DATARA_TEST_RUNNER` accepts only the reviewed factory
path; the settings default remains unchanged outside this explicit override.

Normal Django teardown can drop only the exact target created by this runner after
checking its recorded PostgreSQL OID and owner. No prefix cleanup, forced disconnect,
existing-database reset or automatic recovery is implemented. Creation/setup failures
and catchable interruptions can leave a residual target. Both setup and teardown
failure handlers report the residual state before rethrowing, including when Django
later suppresses a teardown exception to preserve an earlier suite failure. The
runner records the attempted target immediately before CREATE and reports a possible residual target
if creation/setup fails before its OID and owner are recorded. This report explicitly
labels the identity unverified; an attempted name never authorizes an automatic DROP.
A failed CREATE may therefore report a possible residual even when it created none.
Hard process termination cannot guarantee a report, so the declared run target must
also be retained privately before execution. Later cleanup requires a separately
authorized disposition. A teardown error is a failure rather than a claim of
successful cleanup.

Maintenance connection permission is currently unknown and remains a later authorized
evidence gate. The command uses `postgres` explicitly with the test role and does not
fall back to a preserved/base database or broaden permissions. A successful suite under
test_runner will not prove application-role authorization or two-identity service access.
`app-check` currently performs no synthetic record creation and reports
`isolation_not_verified`; service checks need their own reviewed data/cleanup contract.

## Bash compatibility and remaining evidence

`bash scripts/milestone_a.sh <phase>` uses the shared phase runner and explicit
`DATARA_PYTHON` / `DATARA_VENV`; paths and shell compatibility require separate
executed evidence. It does not imply native PowerShell or Linux/WSL compatibility.
The old no-argument combined path is restricted to the already declared SQLite
deviation with `DATARA_ALLOW_SQLITE=1` and PostgreSQL unavailable. Its exit 3/4 remains
a deviation, never PostgreSQL verification. Combined PostgreSQL migration/tests are
refused. No unpinned pip upgrade occurs in either path.

Future authorized execution must preserve exact candidate SHA, dirty state,
OS/shell/interpreter/installer/dependency identity, endpoint, role attributes, test
name, phase exits and cleanup outcome. Independent technical review and QM audit
apply to the exact candidate; TC05/TC20/TC23 and application isolation evidence remain
separate. Operator, real-data, backup/recovery, deployment and full P0 gates remain open.
