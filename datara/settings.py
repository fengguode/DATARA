"""Pinned Django settings for the DATARA Milestone A unit.

D05 selected Django 5.2 LTS on Python with PostgreSQL 17 and a local browser
pilot published on loopback only. This module encodes that selection and
nothing else: there is no provider configuration, no secret material, no
model-adapter setting and no skill configuration, because Milestone A makes no
provider call (SR06) and G0 criterion 3 is not waived.

Configuration comes from the environment. Nothing in this module is a source of
product behaviour that is not already recorded in the dated decision baseline.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import os
from pathlib import Path

from datara import PINNED_DJANGO_SERIES, PINNED_POSTGRESQL_MAJOR

REPO_ROOT = Path(__file__).resolve().parent.parent

#: Deployment intent. There is no "production" switch in this unit: the pilot
#: runtime and its operator arrangement are still open (G0 criterion 5, "Still
#: unmet: operational ownership"), and this module must not be readable as a
#: production configuration.
DATARA_ENV = os.environ.get("DATARA_ENV", "milestone-a-local")

#: Loopback only. D05: publish the app endpoint only on localhost/127.0.0.1.
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "[::1]"]


def _secret_key() -> str:
    configured = os.environ.get("DATARA_SECRET_KEY")
    if configured:
        return configured
    if DATARA_ENV == "milestone-a-local":
        # A local development value, named so that it cannot be mistaken for a
        # deployment secret. It is not a credential for any external service and
        # grants no access; it only satisfies Django's requirement for a key.
        return "datara-milestone-a-local-development-key-not-a-credential"
    raise RuntimeError(
        "DATARA_SECRET_KEY must be set when DATARA_ENV is not 'milestone-a-local'. "
        "Refusing to start with a development key."
    )


SECRET_KEY = _secret_key()
DEBUG = False

INSTALLED_APPS = [
    # contenttypes/auth back the owner foreign key used for owner scoping
    # (CUS10, SR20-SR21). `sessions` is installed because the identity-bound
    # read surface added in #378 derives its owner from `request.user`, and
    # AuthenticationMiddleware only populates `request.user` from a session
    # when SessionMiddleware and the sessions app are both present. Without
    # them every request resolves to AnonymousUser and the surface denies
    # everything. No messages/admin/static surface is installed.
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "datara",
]

# Present so Django's own security checks pass, and because the #378 read surface
# needs a real session. SessionMiddleware must precede AuthenticationMiddleware:
# the latter reads the session the former has not yet attached, and Django's own
# system check (auth.E001) refuses the reversed order.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

# The #378 surface is the first runnable page in this project. ROOT_URLCONF was
# None because there was no URLconf to point at.
ROOT_URLCONF = "datara.urls"

# APP_DIRS makes datara/templates/ discoverable, so the surface's generic denial
# template is found without coupling this file to that path. Empty
# context_processors: the denial template must not gain a context that could vary
# per request and reintroduce an existence oracle.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

# Still None: WSGI_APPLICATION names datara.wsgi.application, and no such module
# exists. `runserver` falls back to get_internal_wsgi_application(), so leaving
# this unset is honest rather than pointing at a module that is not there.
WSGI_APPLICATION = None

# Deterministic time handling. D02/D05: UTC instants; date scopes are half-open
# [start, end). `USE_TZ` is not optional: a naive datetime reaching a persisted
# session start instant would make the normalized value ambiguous.
USE_TZ = True
TIME_ZONE = "UTC"
USE_I18N = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# The application database role is neither table owner, superuser nor BYPASSRLS
# (D05). `CONN_MAX_AGE=0` closes every connection at request end so a pooled
# connection can never carry one identity's context into the next request.
CONN_MAX_AGE = 0
CONN_HEALTH_CHECKS = True


def _database() -> dict:
    engine = os.environ.get("DATARA_DB_ENGINE", "postgres").strip().lower()
    if engine == "postgres":
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DATARA_DB_NAME", "datara"),
            "USER": os.environ.get("DATARA_DB_USER", "datara_app"),
            "PASSWORD": os.environ.get("DATARA_DB_PASSWORD", ""),
            "HOST": os.environ.get("DATARA_DB_HOST", "127.0.0.1"),
            "PORT": os.environ.get("DATARA_DB_PORT", "5432"),
            "CONN_MAX_AGE": CONN_MAX_AGE,
            "CONN_HEALTH_CHECKS": CONN_HEALTH_CHECKS,
            "TEST": {"NAME": os.environ.get("DATARA_TEST_DB_NAME", "test_datara")},
        }
    if engine == "sqlite":
        # A declared deviation, used only for unit tests of pure deterministic
        # logic on a host where PostgreSQL 17 cannot run. `scripts/milestone_a.sh`
        # reports this state and refuses to present it as the pinned command
        # passing. It is never a product deployment database.
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.environ.get("DATARA_DB_PATH", str(REPO_ROOT / "runtime-data" / "milestone-a.sqlite3")),
            "CONN_MAX_AGE": CONN_MAX_AGE,
            "TEST": {"NAME": os.environ.get("DATARA_TEST_DB_PATH", ":memory:")},
        }
    raise RuntimeError(
        f"DATARA_DB_ENGINE must be 'postgres' or 'sqlite'; got {engine!r}."
    )


DATABASES = {"default": _database()}

# The Windows test phase opts into the fresh-only runner. Default Django and
# the separately declared Bash SQLite deviation retain their existing interface.
_requested_test_runner = os.environ.get("DATARA_TEST_RUNNER")
if _requested_test_runner:
    if _requested_test_runner != "scripts.milestone_a_runner.FreshDatabaseRunner":
        raise RuntimeError("Unsupported DATARA_TEST_RUNNER override")
    TEST_RUNNER = _requested_test_runner

# Safety posture for a local pilot holding personal activity data.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

# Kept deliberately quiet: the pinned command's output must contain the
# environment identity and the test result, not framework chatter. Operational
# metadata logging is an open D05 item and must not carry raw telemetry.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(levelname)s %(name)s %(message)s"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "plain"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
}

# Read by `scripts/milestone_a.sh` to print the resolved environment identity
# alongside the settings actually in force.
DATARA_PINNED = {
    "django_series": PINNED_DJANGO_SERIES,
    "postgres_major": PINNED_POSTGRESQL_MAJOR,
    "db_engine": DATABASES["default"]["ENGINE"],
    "env": DATARA_ENV,
    "repo_root": str(REPO_ROOT),
}
