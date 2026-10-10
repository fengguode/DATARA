"""Synthetic PostgreSQL tests for persisted WP05 reads and owner isolation."""
import html
import json

from django.test import TestCase
from django.urls import reverse

from datara import models as m
from datara.metric_store import SavedMetricStore
from datara.recorded_metrics import summarize_recorded, prepare_recorded_input
from datara.scoped_input import prepare_scoped_input
from datara.tests.test_recorded_regressions import CORE
from datara.tests.test_scoped_input import _Owner, SYNTHETIC_POLICY, make_scope


class PersistedRecordedMetricReadTests(TestCase):
    def setUp(self):
        self.owner = _Owner("wp05-reader-owner")
        self.other = _Owner("wp05-reader-other")
        self.owner.add_accepted(start_utc="2026-09-01T06:00:00Z")
        self.saved = self._save_summary(self.owner)
        self.other_saved = self._save_summary(self.other)

    @staticmethod
    def _save_summary(owner):
        scope = make_scope(start_utc="2026-08-31T00:00:00Z",
                           end_utc="2026-10-02T00:00:00Z")
        version = prepare_scoped_input(
            scope=scope,
            records=owner.inputs.scope_candidates(scope, CORE),
            field_specs=CORE,
            policy=SYNTHETIC_POLICY,
        )
        handle = owner.inputs.append_version(version)
        prepared = summarize_recorded(prepare_recorded_input(version))
        return SavedMetricStore.for_user(owner.user).save_prepared_metrics(
            handle.version_ref, prepared)

    @staticmethod
    def _stored_graph(metric_id):
        return (
            tuple(m.Metric.objects.filter(pk=metric_id).order_by("pk").values()),
            tuple(m.MetricOperand.objects.filter(parent_metric_id=metric_id)
                  .order_by("pk").values()),
            tuple(m.MetricSeal.objects.filter(metric_id=metric_id)
                  .order_by("pk").values()),
            tuple(m.Evidence.objects.filter(metric_id=metric_id)
                  .order_by("pk").values()),
        )

    def test_owner_reads_exact_saved_bytes_and_evidence_without_writes(self):
        self.client.force_login(self.owner.user)
        graph_before = self._stored_graph(self.saved.metric_id)
        response = self.client.get(reverse("recorded_metric_api", kwargs={
            "metric_id": self.saved.metric_id,
        }))
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertEqual(body["state"], "complete")
        self.assertEqual(body["canonical_content"].encode("ascii"),
                         self.saved.canonical_content)
        self.assertEqual(body["canonical_registry_content"].encode("ascii"),
                         self.saved.canonical_registry_content)
        self.assertEqual(body["canonical_method_identity"].encode("ascii"),
                         self.saved.canonical_method_identity)
        registry = json.loads(self.saved.canonical_registry_content)
        numeric_paths = sorted(
            entry["path"] for entry in registry["entries"]
            if entry.get("type") == "numeric"
        )
        self.assertEqual([item["value_path"] for item in body["evidence"]], numeric_paths)
        evidence = body["evidence"][0]
        detail = self.client.get(evidence["href"])
        self.assertEqual(detail.status_code, 200)
        evidence_body = json.loads(detail.content)
        self.assertEqual(evidence_body["metric_id"], self.saved.metric_id)
        self.assertEqual(evidence_body["value_path"], evidence["value_path"])
        self.assertEqual(evidence_body["canonical_registry_entry"].encode("ascii"),
                         m.Evidence.objects.for_owner(self.owner.user.pk).get(
                             pk=evidence["evidence_id"]).value_canonical.encode("ascii"))
        self.assertEqual(graph_before, self._stored_graph(self.saved.metric_id))

    def test_other_owner_and_absent_metric_have_identical_404(self):
        self.client.force_login(self.other.user)
        foreign = self.client.get(reverse("recorded_metric_api", kwargs={
            "metric_id": self.saved.metric_id,
        }))
        absent = self.client.get(reverse("recorded_metric_api", kwargs={
            "metric_id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        }))
        self.assertEqual(foreign.status_code, 404)
        self.assertEqual(absent.status_code, 404)
        self.assertEqual(foreign.content, absent.content)
        self.assertNotIn(self.saved.metric_id.encode(), foreign.content)

    def test_client_owner_parameters_are_rejected_and_never_select_scope(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("recorded_metric_api", kwargs={
            "metric_id": self.saved.metric_id,
        }) + "?owner_id=" + str(self.other.user.pk))
        self.assertEqual(response.status_code, 422)
        self.assertEqual(json.loads(response.content)["error"]["code"], "invalid_request")

    def test_authenticated_page_uses_same_saved_value_projection(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("recorded_metric_page", kwargs={
            "metric_id": self.saved.metric_id,
        }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Deterministic recorded observation")
        self.assertContains(response, "Saved values")
        self.assertIn('"activity_count"',
                      html.unescape(response.content.decode("utf-8")))
        self.assertContains(response, "Computed evidence")
