"""Approved internal saved-source preparation regressions, WP02/WP03.
CUS03-05/CUS08/CUS10; SR05-11/SR20-21/SR28-29. Synthetic only.
"""

from unittest import mock
from django.db import DatabaseError, transaction
from django.test import TransactionTestCase
from datara import models as m
from datara.metric_store import MetricStoreRefusal
from datara.tests import test_saved_metrics as graph_tests

class SnapshotMetricOperationTests(TransactionTestCase):
    setUp = graph_tests.SavedMetricGraphRegressions.setUp
    prepared = graph_tests.SavedMetricGraphRegressions.prepared

    def test_summary_from_saved_source_matches_canonical_preparer_and_retry(self):
        handle, expected = self.prepared()
        first = self.store.prepare_and_save_metric(handle.version_ref, "activity-summary")
        self.assertEqual(first.canonical_content, expected.canonical_content)
        self.assertEqual(self.store.get_metric(first.metric_id).canonical_content, expected.canonical_content)
        second = self.store.prepare_and_save_metric(handle.version_ref, "activity-summary")
        self.assertEqual(second.metric_id, first.metric_id)
        self.assertFalse(second.created)
        self.assertEqual(m.Metric.objects.for_owner(self.owner.user.pk).count(), 1)

    def test_eligible_trend_preserves_exact_canonical_result_and_summary(self):
        for day in ("2026-09-07", "2026-09-14", "2026-09-21"):
            self.owner.add_accepted(start_utc=day + "T06:00:00Z")
        handle, expected = self.prepared(trend=True)
        self.assertTrue(expected.eligible)
        summary = self.store.prepare_and_save_metric(handle.version_ref, "activity-summary")
        trend = self.store.prepare_and_save_metric(handle.version_ref, "training-volume-trend")
        self.assertEqual(trend.canonical_content, expected.canonical_content)
        self.assertNotEqual(summary.metric_id, trend.metric_id)
        self.assertEqual(len(self.store.list_metrics_for_snapshot(handle.version_ref)), 2)

    def test_ineligible_trend_retains_canonical_unavailable_diagnostics(self):
        handle, expected = self.prepared(trend=True)
        self.assertFalse(expected.eligible)
        saved = self.store.prepare_and_save_metric(handle.version_ref, "training-volume-trend")
        self.assertEqual(saved.canonical_content, expected.canonical_content)
        self.assertEqual(self.store.get_metric(saved.metric_id).canonical_content, expected.canonical_content)

    def test_foreign_snapshot_refused_before_metric_code_or_source_access(self):
        handle, _ = self.prepared()
        with mock.patch.object(self.foreign, "_source") as source:
            for code in ("activity-summary", "training-volume-trend", "unsupported"):
                with self.assertRaises(MetricStoreRefusal) as caught:
                    self.foreign.prepare_and_save_metric(handle.version_ref, code)
                self.assertEqual(caught.exception.reason_code, "resource_not_available")
            source.assert_not_called()
        self.assertEqual(m.Metric.objects.count(), 0)

    def test_unsupported_metric_does_not_prepare_or_persist(self):
        handle, _ = self.prepared()
        with mock.patch.object(self.store, "_source") as source:
            with self.assertRaises(MetricStoreRefusal) as caught:
                self.store.prepare_and_save_metric(handle.version_ref, "unsupported")
            self.assertEqual(caught.exception.reason_code, "unsupported_metric_code")
            source.assert_not_called()
        self.assertEqual(m.Metric.objects.count(), 0)

    def test_source_refusal_preserved_without_graph(self):
        handle, _ = self.prepared()
        with mock.patch.object(self.store, "_source", side_effect=MetricStoreRefusal("corrupt_content")):
            with self.assertRaises(MetricStoreRefusal) as caught:
                self.store.prepare_and_save_metric(handle.version_ref, "activity-summary")
            self.assertEqual(caught.exception.reason_code, "corrupt_content")
        self.assertEqual(m.Metric.objects.count(), 0)

    def test_preparation_failure_is_sanitized_without_graph(self):
        handle, _ = self.prepared()
        with mock.patch("datara.metric_store.summarize_recorded", side_effect=DatabaseError("synthetic-private-diagnostic")):
            with self.assertRaises(MetricStoreRefusal) as caught:
                self.store.prepare_and_save_metric(handle.version_ref, "activity-summary")
            self.assertEqual(caught.exception.reason_code, "metric_persistence_unavailable")
            self.assertNotIn("synthetic-private-diagnostic", str(caught.exception))
        self.assertEqual(m.Metric.objects.count(), 0)

    def test_outer_rollback_removes_provisional_metric_graph(self):
        handle, _ = self.prepared()
        with self.assertRaisesRegex(RuntimeError, "synthetic rollback"):
            with transaction.atomic():
                self.store.prepare_and_save_metric(handle.version_ref, "activity-summary")
                raise RuntimeError("synthetic rollback")
        for model in (m.Metric, m.MetricOperand, m.MetricSeal):
            self.assertEqual(model.objects.for_owner(self.owner.user.pk).count(), 0)
        self.assertEqual(m.Evidence.objects.filter(kind="computed_metric").count(), 0)
