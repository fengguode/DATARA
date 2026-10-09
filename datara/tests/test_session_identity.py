"""WP05 TK64 session boundary and same-origin login/logout checks.

Scope: CUS10; SR20-SR21/SR73. These checks prove the local Django boundary
without asserting that a session table has been migrated or that authentication
has succeeded against a running PostgreSQL service.
"""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db.migrations.loader import MigrationLoader
from django.test import Client, SimpleTestCase, TestCase


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


class SessionPersistenceTests(TestCase):
    """Exercise a real synthetic login against Django's server-side session table."""

    def test_login_persists_authenticated_identity_and_logout_flushes_session(self) -> None:
        user = get_user_model().objects.create_user(
            username="synthetic-athlete",
            password="Synthetic-only-Password-42!",
        )
        client = Client(enforce_csrf_checks=True)

        login_page = client.get("/login/")
        csrf_token = client.cookies[settings.CSRF_COOKIE_NAME].value
        login_response = client.post(
            "/login/",
            {
                "username": user.get_username(),
                "password": "Synthetic-only-Password-42!",
                "csrfmiddlewaretoken": csrf_token,
            },
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(login_page.status_code, 200)
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response["Location"], "/")
        session_key = client.session.session_key
        self.assertIsNotNone(session_key)
        saved_session = Session.objects.get(session_key=session_key)
        self.assertEqual(saved_session.get_decoded()['_auth_user_id'], str(user.pk))

        home_response = client.get("/")
        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, "Signed in as")
        self.assertContains(home_response, user.get_username())

        logout_csrf = client.cookies[settings.CSRF_COOKIE_NAME].value
        logout_response = client.post(
            "/logout/",
            HTTP_X_CSRFTOKEN=logout_csrf,
        )
        self.assertEqual(logout_response.status_code, 302)
        self.assertTrue(logout_response["Location"].startswith("/login/"))
        self.assertFalse(Session.objects.filter(session_key=session_key).exists())

        anonymous_response = client.get("/")
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertTrue(anonymous_response["Location"].startswith("/login/?next="))

