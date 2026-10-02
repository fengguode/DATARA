#!/usr/bin/env bash
# DATARA Milestone A -- the single pinned install / migrate / run / test command.
#
# RUN IT WITH:  bash scripts/milestone_a.sh
# This is a POSIX shell script, not a Python program. `python scripts/milestone_a.sh`
# (as written in #305) cannot work and is not supported; the file carries mode
# 100755 so `./scripts/milestone_a.sh` and `bash scripts/milestone_a.sh` both run.
#
# Authorised by the founder's G0 replacement, G0 criterion 5: "Pinned
# install/run/test commands are added to Milestone A scope and must exist before
# any Milestone A result is offered as evidence."
#
# Contract of this script:
#
#   * It is the only supported way to install, migrate and test this unit.
#   * It prints the resolved environment identity -- Python version, Django
#     version, PostgreSQL version, pinned dependency lock hash, commit SHA --
#     BEFORE any test result is printed. Evidence that cannot be reproduced from
#     this output is not evidence.
#   * It reports the real state of the host. If PostgreSQL 17 cannot run here it
#     says so and refuses to pass. It never silently substitutes SQLite.
#
# Exit codes:
#   0  the pinned PostgreSQL path ran and every test passed
#   1  a test failed, or the unit could not be prepared at all
#   2  PostgreSQL was unavailable and DATARA_ALLOW_SQLITE was not set (blocked)
#   3  DEVIATION: tests ran and passed, but on SQLite because PostgreSQL 17 was
#      unavailable. This is NOT the pinned command passing.
#   4  DEVIATION: tests ran on SQLite and at least one failed.
#
# Environment overrides (all optional):
#   DATARA_PYTHON        interpreter used to create the virtualenv
#   DATARA_VENV          virtualenv location (default: $TEMP/datara-milestone-a-venv)
#   DATARA_DB_HOST/PORT/NAME/USER/PASSWORD   PostgreSQL connection
#   DATARA_ALLOW_SQLITE  set to 1 to permit the declared SQLite deviation
#
# Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
# Model used: model=opencode/space-bunny-free variant=max harness=OpenCode
# Agent-run: unavailable (OpenCode runtime); no runtime execution link is exposed
#            by this harness.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# --------------------------------------------------------------------------
# 0. Locate an interpreter and a virtualenv, outside the working tree so that
#    nothing untracked is created inside the repository.
# --------------------------------------------------------------------------
BOOTSTRAP_PYTHON="${DATARA_PYTHON:-}"
if [ -z "$BOOTSTRAP_PYTHON" ]; then
  # Probe candidates rather than trusting `command -v`: on Windows the
  # Microsoft Store alias `python3` under WindowsApps resolves but is not a
  # usable interpreter.
  for candidate in python3.13 python3.12 python3 python; do
    candidate_path="$(command -v "$candidate" 2>/dev/null || true)"
    [ -n "$candidate_path" ] || continue
    case "$candidate_path" in */WindowsApps/*) continue ;; esac
    if "$candidate_path" -c 'import sys' >/dev/null 2>&1; then
      BOOTSTRAP_PYTHON="$candidate_path"
      break
    fi
  done
fi
if [ -z "$BOOTSTRAP_PYTHON" ]; then
  echo "MILESTONE_A_RESULT=ERROR" >&2
  echo "no usable python interpreter was found on PATH." >&2
  echo "Set DATARA_PYTHON to an absolute interpreter path, for example:" >&2
  echo "  DATARA_PYTHON=/c/Users/<you>/AppData/Local/Programs/Python/Python313/python.exe \\" >&2
  echo "    bash scripts/milestone_a.sh" >&2
  exit 1
fi

VENV_DIR="${DATARA_VENV:-${TEMP:-/tmp}/datara-milestone-a-venv}"
case "$(uname -s 2>/dev/null || echo unknown)" in
  MINGW*|MSYS*|CYGWIN*) VENV_PY="$VENV_DIR/Scripts/python.exe" ;;
  *)                    VENV_PY="$VENV_DIR/bin/python" ;;
esac

if [ ! -x "$VENV_PY" ]; then
  echo "== creating virtualenv at $VENV_DIR"
  "$BOOTSTRAP_PYTHON" -m venv "$VENV_DIR"
fi
PY="$VENV_PY"

# --------------------------------------------------------------------------
# 1. Install the pinned dependency set. `--require-hashes` is not used because
#    psycopg-binary ships platform-specific wheels; the reproducibility token is
#    the SHA-256 of the lock file itself, printed below.
# --------------------------------------------------------------------------
LOCK_FILE="requirements-milestone-a.txt"
echo "== installing pinned dependencies from $LOCK_FILE"
"$PY" -m pip install --disable-pip-version-check --quiet --upgrade pip >/dev/null
"$PY" -m pip install --disable-pip-version-check --quiet -r "$LOCK_FILE"

# --------------------------------------------------------------------------
# 1b. Refuse an inherited optimisation level, do not silently inherit one.
#     `PYTHONOPTIMIZE=1` (or `python -O`) strips every `assert` statement from the
#     code being tested. It is silently inherited from the caller's environment,
#     and a stripped run of this unit is not a run of this unit. The pinned
#     command therefore clears it and says so.
# --------------------------------------------------------------------------
if [ -n "${PYTHONOPTIMIZE:-}" ]; then
  echo "milestone_a_opt_level    : clearing inherited PYTHONOPTIMIZE='${PYTHONOPTIMIZE}'"
fi
# Unconditionally, so an exported-but-empty value cannot re-assert itself.
unset PYTHONOPTIMIZE
echo "milestone_a_opt_level    : not optimised (python -O not in effect)"

# --------------------------------------------------------------------------
# 2. Environment identity. Printed before any test result, by design.
# --------------------------------------------------------------------------
LOCK_SHA="$("$PY" -X utf8 - "$LOCK_FILE" <<'PY'
import hashlib, sys
with open(sys.argv[1], "rb") as handle:
    print("sha256:" + hashlib.sha256(handle.read()).hexdigest())
PY
)"
COMMIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
COMMIT_DIRTY="$(git status --porcelain -- requirements-milestone-a.txt datara scripts/milestone_a.sh 2>/dev/null | tr -d '\r' | tr '\n' ' ')"

export DATARA_ALLOW_SQLITE="${DATARA_ALLOW_SQLITE:-0}"

echo
echo "=== DATARA Milestone A environment identity ==="
echo "resolved_interpreter      : $("$PY" -c 'import sys; print(sys.executable)')"
echo "python_version            : $("$PY" -c 'import platform; print(platform.python_version())')"
echo "python_implementation     : $("$PY" -c 'import platform; print(platform.python_implementation())')"
echo "platform                  : $("$PY" -c 'import platform; print(platform.platform())')"
echo "django_version            : $("$PY" -c 'import django; print(django.get_version())')"
echo "pinned_fit_decoder        : $("$PY" -c '
import importlib
try:
    import garmin_fit_sdk
except Exception as exc:
    print(f"ABSENT ({exc.__class__.__name__})")
else:
    from garmin_fit_sdk import Profile
    v = dict(Profile["version"])
    print("garmin-fit-sdk {}.{}.{} {}".format(v["major"], v["minor"], v["patch"], v["type"]))
')"
echo "pinned_dependency_lock    : $LOCK_FILE"
echo "pinned_dependency_lock_sha256: $LOCK_SHA"
echo "resolved_dependencies     :"
# The evidence list must name every distribution in the lock file. `garmin_fit_sdk`
# is included because it is the pinned FIT decoder; leaving it out let an
# environment without it look identical to a resolved one.
"$PY" -m pip freeze --disable-pip-version-check 2>/dev/null \
  | grep -Ei '^(asgiref|django|garmin-fit-sdk|psycopg|psycopg-binary|sqlparse|tzdata)==' \
  | sed 's/^/  - /'
echo "commit_sha                : $COMMIT_SHA"
echo "commit_dirty_owned_paths  : ${COMMIT_DIRTY:-none}"

# --------------------------------------------------------------------------
# 3. PostgreSQL 17 probe. Report the real state; never quietly substitute.
# --------------------------------------------------------------------------
export DATARA_DB_HOST="${DATARA_DB_HOST:-127.0.0.1}"
export DATARA_DB_PORT="${DATARA_DB_PORT:-5432}"
export DATARA_DB_NAME="${DATARA_DB_NAME:-datara}"
export DATARA_DB_USER="${DATARA_DB_USER:-datara_app}"
export DATARA_DB_PASSWORD="${DATARA_DB_PASSWORD:-}"
export DATARA_PINNED_POSTGRESQL_MAJOR=17

PG_STATE="$("$PY" -X utf8 - <<'PY'
import os, sys
try:
    import psycopg
except Exception as exc:  # driver missing or unusable
    print(f"UNAVAILABLE driver-import-failed: {exc.__class__.__name__}")
    sys.exit(0)
try:
    with psycopg.connect(
        host=os.environ["DATARA_DB_HOST"],
        port=int(os.environ["DATARA_DB_PORT"]),
        dbname=os.environ["DATARA_DB_NAME"],
        user=os.environ["DATARA_DB_USER"],
        password=os.environ.get("DATARA_DB_PASSWORD", "") or None,
        connect_timeout=5,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version")
            version = cursor.fetchone()[0]
            cursor.execute("SHOW server_version_num")
            number = int(cursor.fetchone()[0])
    print(f"AVAILABLE {version} major={number // 10000} version_num={number}")
except Exception as exc:
    print(f"UNAVAILABLE connect-failed: {exc.__class__.__name__}: {exc}")
PY
)"

echo "postgres_probe            : $PG_STATE"
case "$PG_STATE" in
  AVAILABLE*)
    PG_MAJOR="$(printf '%s' "$PG_STATE" | sed -n 's/.*major=\([0-9]*\).*/\1/p')"
    echo "postgres_version          : $(printf '%s' "$PG_STATE" | cut -d' ' -f2)"
    echo "postgres_major            : $PG_MAJOR (D05 pins 17)"
    if [ "$PG_MAJOR" != "17" ]; then
      echo
      echo "MILESTONE_A_RESULT=ERROR"
      echo "PostgreSQL major $PG_MAJOR is reachable but D05 pins 17. Refusing to run." >&2
      exit 1
    fi
    export DATARA_DB_ENGINE=postgres
    ENGINE_STATUS="pinned PostgreSQL 17"
    ;;
  *)
    echo
    echo "MILESTONE_A_POSTGRESQL=UNAVAILABLE"
    echo "The D05-pinned PostgreSQL 17 could not be run on this host:"
    echo "  $PG_STATE"
    echo "This unit is NOT reported as passing under the pinned command."
    if [ "$DATARA_ALLOW_SQLITE" != "1" ]; then
      echo
      echo "Set DATARA_ALLOW_SQLITE=1 to run the unit under the DECLARED DEVIATION of a"
      echo "local SQLite database, which is permitted only for unit tests of pure"
      echo "deterministic logic. Its result must never be reported as the pinned"
      echo "command passing."
      echo "MILESTONE_A_RESULT=BLOCKED_POSTGRESQL_UNAVAILABLE"
      exit 2
    fi
    export DATARA_DB_ENGINE=sqlite
    export DATARA_DB_PATH="$VENV_DIR/milestone-a-deviation.sqlite3"
    export DATARA_TEST_DB_PATH="$VENV_DIR/milestone-a-deviation-test.sqlite3"
    ENGINE_STATUS="DECLARED DEVIATION: SQLite (PostgreSQL 17 unavailable)"
    ;;
esac
echo "database_engine_status    : $ENGINE_STATUS"
echo "==========================================================="
echo

# --------------------------------------------------------------------------
# 4. Migrate, then test. Both inside the pinned command.
# --------------------------------------------------------------------------
export DJANGO_SETTINGS_MODULE=datara.settings
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1

echo "== django check"
"$PY" -X utf8 -m django check

echo "== migrate (--run-syncdb: this unit has no migrations directory)"
"$PY" -X utf8 -m django migrate --run-syncdb --noinput

echo "== test datara.tests"
set +e
# Belt and braces for 1b: if the interpreter is nonetheless optimised, every
# `assert` in the unit is gone. Refuse rather than report a stripped run.
if [ "$("$PY" -c 'import sys; print(int(not __debug__))')" != "0" ]; then
  echo "MILESTONE_A_RESULT=ERROR" >&2
  echo "the interpreter is running with asserts disabled (-O). This unit's" >&2
  echo "contract checks are executable code, not asserts, but a stripped run is" >&2
  echo "not the pinned command and is not reported as one." >&2
  exit 1
fi
"$PY" -X utf8 -m django test datara.tests --verbosity 2
TEST_EXIT=$?
set -e

echo
echo "=== DATARA Milestone A result ==="
echo "commit_sha                : $COMMIT_SHA"
echo "database_engine_status    : $ENGINE_STATUS"
echo "test_exit_code            : $TEST_EXIT"
if [ "$DATARA_DB_ENGINE" = "sqlite" ]; then
  if [ "$TEST_EXIT" -eq 0 ]; then
    echo "MILESTONE_A_RESULT=DEVIATION_SQLITE_TESTS_PASSED"
    echo "NOTE: not the pinned PostgreSQL command passing."
    exit 3
  fi
  echo "MILESTONE_A_RESULT=DEVIATION_SQLITE_TESTS_FAILED"
  exit 4
fi
if [ "$TEST_EXIT" -eq 0 ]; then
  echo "MILESTONE_A_RESULT=PASSED"
  exit 0
fi
echo "MILESTONE_A_RESULT=FAILED"
exit 1
