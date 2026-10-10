"""Synthetic same-origin authentication/session persistence tests (WP05)."""
import re

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.test import Client, TransactionTestCase


class SameOriginSessionLifecycleTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.username = "wp05-synthetic-owner"
        self.raw_password = "synthetic-only-password-31"
        self.user = get_user_model().objects.create_user(
            username=self.username, password=self.raw_password)
        self.client = Client(enforce_csrf_checks=True)

    @staticmethod
    def csrf_from(response):
        match = re.search(rb'name="csrfmiddlewaretoken" value="([^"]+)"', response.content)
        if not match:
            raise AssertionError("CSRF token field was not rendered")
        return match.group(1).decode("ascii")

    def test_login_persists_server_side_session_and_logout_flushes_it(self):
        login_page = self.client.get("/login/")
        self.assertEqual(login_page.status_code, 200)
        login_token = self.csrf_from(login_page)
        logged_in = self.client.post("/login/", {
            "username": self.username,
            "password": self.raw_password,
            "csrfmiddlewaretoken": login_token,
        })
        self.assertEqual(logged_in.status_code, 302)
        self.assertTrue(self.user.check_password(self.raw_password))
        self.assertNotEqual(self.user.password, self.raw_password)
        self.assertTrue(self.client.session.get("_auth_user_id"))
        session_key = self.client.session.session_key
        persisted = Session.objects.get(session_key=session_key)
        decoded = persisted.get_decoded()
        self.assertEqual(decoded["_auth_user_id"], str(self.user.pk))
        self.assertNotIn(self.raw_password, persisted.session_data)

        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        logout_token = self.csrf_from(home)
        denied_logout = self.client.post("/logout/")
        self.assertEqual(denied_logout.status_code, 403)
        self.assertTrue(Session.objects.filter(session_key=session_key).exists())

        logged_out = self.client.post("/logout/", {"csrfmiddlewaretoken": logout_token})
        self.assertEqual(logged_out.status_code, 302)
        self.assertFalse(Session.objects.filter(session_key=session_key).exists())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_without_csrf_is_rejected(self):
        response = self.client.post("/login/", {
            "username": self.username,
            "password": self.raw_password,
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get("_auth_user_id"))
