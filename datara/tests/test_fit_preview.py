"""Private local FIT preview route tests using DATARA-authored synthetic data."""

import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from datara.models import Import, SourceObject
from datara.tests.test_classification import _build_fit


class FitPreviewTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="synthetic-preview-owner")
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)

    @staticmethod
    def csrf_token(response):
        match = re.search(rb'name="csrfmiddlewaretoken" value="([^"]+)"', response.content)
        if match is None:
            raise AssertionError("CSRF token was not rendered")
        return match.group(1).decode("ascii")

    def submit(self, files):
        home = self.client.get(reverse("home"))
        token = self.csrf_token(home)
        return self.client.post(reverse("fit_preview"), {
            "csrfmiddlewaretoken": token,
            "fit_file": files,
        })

    def test_real_classifier_preview_shows_facts_without_importing_or_saving(self):
        private_name = "private-route-name.fit"
        response = self.submit(SimpleUploadedFile(private_name, _build_fit()))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Source disposition: accepted")
        self.assertContains(response, "2026-03-15T08:30:00Z")
        self.assertContains(response, "This is a preview only")
        self.assertNotContains(response, private_name)
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertEqual(Import.objects.for_owner(self.owner.pk).count(), 0)
        self.assertEqual(SourceObject.objects.for_owner(self.owner.pk).count(), 0)

    def test_rejected_source_shows_classifier_reason_without_filename(self):
        private_name = "private-location.fit"
        response = self.submit(SimpleUploadedFile(private_name, b"not a FIT file"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Source disposition: rejected")
        self.assertContains(response, "not_a_fit_file")
        self.assertNotContains(response, private_name)
        self.assertEqual(Import.objects.for_owner(self.owner.pk).count(), 0)

    def test_preview_requires_one_file_and_post(self):
        no_file = self.submit([])
        self.assertEqual(no_file.status_code, 400)
        self.assertContains(no_file, "Choose exactly one FIT file", status_code=400)

        response = self.client.get(reverse("fit_preview"))
        self.assertEqual(response.status_code, 405)

    def test_preview_post_requires_csrf(self):
        response = self.client.post(reverse("fit_preview"), {
            "fit_file": SimpleUploadedFile("synthetic.fit", _build_fit()),
        })
        self.assertEqual(response.status_code, 403)

    def test_anonymous_upload_is_redirected_before_classifier_runs(self):
        self.client.logout()
        with patch("datara.views.classify_bytes") as classifier:
            response = self.client.post(reverse("fit_preview"), {
                "fit_file": SimpleUploadedFile("synthetic.fit", _build_fit()),
            })
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])
        classifier.assert_not_called()

    def test_multiple_files_are_refused(self):
        response = self.submit([
            SimpleUploadedFile("one.fit", _build_fit()),
            SimpleUploadedFile("two.fit", _build_fit(sport=2)),
        ])
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Choose exactly one FIT file", status_code=400)
        self.assertEqual(Import.objects.for_owner(self.owner.pk).count(), 0)
