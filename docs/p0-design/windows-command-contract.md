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
The candidate contract requires native Windows Python **3.12.14**, PostgreSQL
**17.11**, `DATARA_DB_ENGINE=postgres`, `DATARA_DB_HOST=127.0.0.1` and
`DATARA_DB_PORT=55432`. These are reported candidate settings requiring future
executed evidence, distinct from the Linux/container reference topology.
Optimized Python is refused. No implicit dependency installation occurs outside
`install`; no SQLite fallback occurs in this Windows path.

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

Supply `DATARA_TEST_DB_NAME=test_datara_<safeid>` explicitly. The safe ID consists
of 8–50 lowercase ASCII letters, digits or underscores and begins with a letter or
digit; the total name must fit PostgreSQL's 63-character identifier limit. Choose a
unique run ID before execution. Names for the preserved database, sandbox base,
`postgres`, `template0` and `template1` cannot be test targets. Test reuse,
parallel database clones and mirrors are refused.

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
