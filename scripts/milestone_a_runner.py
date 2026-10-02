"""Reviewed Windows phase commands; control #8, D05, WP03/CUS03/FEAT21/SR07/SR28/SR34.

No role bootstrap or privilege grants. Failures deliberately omit exception messages.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
from importlib import metadata
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
ROLES = {"migrate": ("datara_migrator", "datara_local"),
         "test": ("datara_test_runner", "datara_testsandbox"),
         "app-check": ("datara_app", "datara_local")}
PHASES = ("inspect", "install", "migrate", "test", "app-check")
TARGET = re.compile(r"test_datara_[a-z0-9][a-z0-9_]{7,49}\Z")

class CommandRefused(RuntimeError):
    pass

def require(condition, message):
    if not condition:
        raise CommandRefused(message)

def validate_connection(phase):
    require(os.environ.get("DATARA_DB_ENGINE") == "postgres", "explicit PostgreSQL engine required")
    require(os.environ.get("DATARA_DB_HOST") == "127.0.0.1" and
            os.environ.get("DATARA_DB_PORT") == "55432", "candidate loopback endpoint required")
    actual = (os.environ.get("DATARA_DB_USER"), os.environ.get("DATARA_DB_NAME"))
    require(actual in ROLES.values() if phase == "inspect" else actual == ROLES[phase],
            "phase role/database selection refused")
    if phase == "test":
        validate_target(os.environ.get("DATARA_TEST_DB_NAME", ""), actual[1])

def validate_target(name, base):
    require(bool(TARGET.fullmatch(name)) and len(name) <= 63 and
            name not in {base, "datara_local", "datara_testsandbox", "postgres", "template0", "template1"},
            "fresh allowlisted disposable test database name required")

def inventory():
    lock = ROOT / "requirements-milestone-a.txt"
    print("lock_sha256=" + hashlib.sha256(lock.read_bytes()).hexdigest())
    for line in lock.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            name, expected = line.split("==")
            actual = metadata.version(name)
            print(f"dependency={name} version={actual}")
            require(actual == expected, "dependency pin mismatch")
    print("installer_pip=" + metadata.version("pip"))

def identity():
    print("python=" + platform.python_version())
    print("platform=" + platform.system())
    print("interpreter=" + sys.executable)
    for args, label in [(["rev-parse", "HEAD"], "candidate_sha"),
                        (["status", "--porcelain"], "candidate_changes")]:
        try:
            result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True)
            # Status reports paths, never file contents or environment values.
            print(label + "=" + result.stdout.strip())
        except (OSError, subprocess.CalledProcessError):
            print(label + "=unavailable")

def probe(phase):
    import psycopg
    with psycopg.connect(host="127.0.0.1", port=55432,
                         dbname=os.environ["DATARA_DB_NAME"], user=os.environ["DATARA_DB_USER"],
                         password=os.environ.get("DATARA_DB_PASSWORD", ""), connect_timeout=5,
                         autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_user, current_database(), current_setting('server_version_num')::int")
            role, database, version = cursor.fetchone()
            require((role, database) == (os.environ["DATARA_DB_USER"], os.environ["DATARA_DB_NAME"]),
                    "connected role/database mismatch")
            require(version == 170011, "candidate PostgreSQL 17.11 required")
            cursor.execute("SELECT rolsuper, rolcreatedb, rolbypassrls FROM pg_roles WHERE rolname=current_user")
            superuser, createdb, bypass = cursor.fetchone()
            print(f"postgres_version_num={version} role={role} database={database}")
            print(f"role_superuser={superuser} role_createdb={createdb} role_bypassrls={bypass}")
            require(not superuser and not bypass, "privileged role refused")
            if phase in {"migrate", "app-check"}:
                require(not createdb, "phase role must not have CREATEDB")
            if phase == "test":
                require(createdb, "test runner requires existing CREATEDB privilege")
            if phase == "app-check":
                cursor.execute("SELECT count(*) FROM pg_class WHERE relowner=(SELECT oid FROM pg_roles WHERE rolname=current_user) AND relnamespace IN (SELECT oid FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname <> 'information_schema')")
                require(cursor.fetchone()[0] == 0, "application role owns relations")
            if phase == "migrate":
                cursor.execute("SELECT pg_get_userbyid(datdba)=current_user FROM pg_database WHERE datname=current_database()")
                require(cursor.fetchone()[0], "migration database ownership required")
    print("maintenance_permission=not_checked")

def FreshDatabaseRunner(*args, **kwargs):
    """Django runner factory; deferred imports permit explicit first installation."""
    from django.db.backends.postgresql.creation import DatabaseCreation
    from django.test.runner import DiscoverRunner

    class FreshDatabaseCreation(DatabaseCreation):
        @contextmanager
        def _nodb_cursor(self):
            # Explicit maintenance connection; no fallback to a preserved database.
            import psycopg
            config = self.connection.settings_dict
            with psycopg.connect(host=config["HOST"], port=config["PORT"],
                                 dbname="postgres", user=config["USER"],
                                 password=config["PASSWORD"], connect_timeout=5,
                                 autocommit=True) as connection:
                with connection.cursor() as cursor:
                    yield cursor

        def _create_test_db(self, verbosity, autoclobber, keepdb=False):
            name = self._get_test_db_name()
            validate_target(name, self.connection.settings_dict["NAME"])
            require(not keepdb, "database reuse refused")
            self._created_identity = None
            with self._nodb_cursor() as cursor:
                cursor.execute("SELECT oid FROM pg_database WHERE datname=%s", [name])
                require(cursor.fetchone() is None, "test database collision refused")
                # No exception handler that offers DROP/retry. CREATE itself handles
                # a race after the preflight lookup by failing without deleting it.
                from psycopg import sql
                cursor.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0").format(sql.Identifier(name)))
                cursor.execute("SELECT oid, datdba FROM pg_database WHERE datname=%s", [name])
                self._created_identity = (name, *cursor.fetchone())
            print("test_database_created=" + name)
            return name

        def _destroy_test_db(self, test_database_name, verbosity):
            require(self._created_identity is not None and self._created_identity[0] == test_database_name,
                    "cleanup target was not created by this runner")
            with self._nodb_cursor() as cursor:
                cursor.execute("SELECT oid, datdba FROM pg_database WHERE datname=%s", [test_database_name])
                require(cursor.fetchone() == self._created_identity[1:], "cleanup identity changed; manual disposition required")
                from psycopg import sql
                cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(test_database_name)))
            print("test_database_cleanup=completed")
            self._created_identity = None

    class FreshDatabaseRunnerImpl(DiscoverRunner):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            require(not self.keepdb and self.parallel in (0, 1), "reuse and parallel database cloning refused")
            validate_connection("test")
            require(sys.flags.optimize == 0 and platform.python_version() == "3.12.14",
                    "test interpreter contract refused")
            inventory()
            probe("test")

        def setup_databases(self, **kwargs):
            from django.db import connections
            require(list(connections) == ["default"], "only the declared default database is supported")
            connection = connections["default"]
            require(connection.vendor == "postgresql", "fresh test runner requires PostgreSQL")
            config = connection.settings_dict
            require((config["USER"], config["NAME"], config["HOST"], str(config["PORT"])) ==
                    ("datara_test_runner", "datara_testsandbox", "127.0.0.1", "55432"),
                    "test settings differ from declared connection")
            require(not config["TEST"].get("MIRROR"), "test mirrors refused")
            validate_target(config["TEST"]["NAME"], config["NAME"])
            connection.creation = FreshDatabaseCreation(connection)
            connection.creation._created_identity = None
            try:
                return super().setup_databases(**kwargs)
            except BaseException:
                if connection.creation._created_identity is not None:
                    print("test_database_cleanup=not_completed; residual_target=" +
                          connection.creation._created_identity[0])
                raise
    return FreshDatabaseRunnerImpl(*args, **kwargs)

def _runner_arguments(parser):
    from django.test.runner import DiscoverRunner
    DiscoverRunner.add_arguments(parser)


# Django's command parser obtains runner-specific options before instantiation.
FreshDatabaseRunner.add_arguments = _runner_arguments


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=PHASES)
    parser.add_argument("--native-windows", action="store_true")
    args = parser.parse_args()
    require(sys.flags.optimize == 0 and not os.environ.get("PYTHONOPTIMIZE"), "optimized Python refused")
    require(platform.python_version() == "3.12.14", "candidate Python 3.12.14 required")
    if args.native_windows:
        require(sys.platform == "win32", "native Windows interpreter required")
    identity()
    if args.phase == "install":
        # Capture installer diagnostics: URLs/configuration may contain credentials.
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                                 "-r", str(ROOT / "requirements-milestone-a.txt")],
                                cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            print("installation_failed: diagnostics suppressed")
            return result.returncode
        inventory()
        return 0
    validate_connection(args.phase)
    inventory()
    probe(args.phase)
    if args.phase == "inspect":
        return 0
    os.environ["DJANGO_SETTINGS_MODULE"] = "datara.settings"
    if args.phase == "test":
        os.environ["DATARA_TEST_RUNNER"] = "scripts.milestone_a_runner.FreshDatabaseRunner"
    import django
    django.setup()
    from django.core.management import call_command
    call_command("check", verbosity=0)
    if args.phase == "migrate":
        call_command("migrate", run_syncdb=True, interactive=False, verbosity=0)
    elif args.phase == "test":
        call_command("test", "datara.tests", verbosity=1, interactive=False, parallel=1, keepdb=False)
    else:
        print("app_check=system_and_role_metadata_only; isolation_not_verified")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CommandRefused as exc:
        print("MILESTONE_A_RESULT=REFUSED: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        print("MILESTONE_A_RESULT=ERROR: " + type(exc).__name__ + "; diagnostics suppressed", file=sys.stderr)
        raise SystemExit(1)
