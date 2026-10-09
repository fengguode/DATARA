"""WP05 TK64 session boundary and same-origin login/logout checks.

Scope: CUS10; SR20-SR21/SR73. These checks prove the local Django boundary
without asserting that a session table has been migrated or that authentication
has succeeded against a running PostgreSQL service.
"""
from __future__ import annotations

from django.conf import settings
from django.db.migrations.loader import MigrationLoader
from django.test import Client, SimpleTestCase


class SessionIdentityBoundaryTests(SimpleTestCase):
    def test_sessions_middleware_precedes_authentication_middleware(self) -> None:
        middleware = list(settings.MIDDLEWARE)
        self.assertIn("django.contrib.sessions.middleware.SessionMiddleware", middleware)
        self.assertIn("django.contrib.auth.middleware.AuthenticationMiddleware", middleware)
        self.assertLess(
            middleware.index("django.contrib.sessions.middleware.SessionMiddleware"),
            middleware.index("django.contrib.auth.middleware.AuthenticationMiddleware"),
        )

    def test_django_sessions_migration_is_installed(self) -> None:
        # This inspects Django's source migration graph only; it does not connect
        # to or mutate any database.
        loader = MigrationLoader(None)
        self.assertIn(("sessions", "0001_initial"), loader.disk_migrations)

    def test_login_page_is_same_origin_and_renders_csrf_token(self) -> None:
        response = Client(enforce_csrf_checks=True).get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="csrfmiddlewaretoken"', response.content)
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)

    def test_login_requires_csrf_for_unsafe_post(self) -> None:
        response = Client(enforce_csrf_checks=True).post(
            "/login/", {"username": "synthetic", "password": "not-a-secret"}
        )
        self.assertEqual(response.status_code, 403)

    def test_logout_is_post_only_and_requires_csrf(self) -> None:
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.get("/logout/").status_code, 405)
        self.assertEqual(client.post("/logout/").status_code, 403)

    def test_home_redirects_anonymous_user_to_local_login(self) -> None:
        response = Client().get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/login/?next="))
