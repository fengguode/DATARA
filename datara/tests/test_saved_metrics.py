"""Synthetic PostgreSQL saved-graph regressions; WP02/WP03.
CUS03-05/CUS08/CUS10; SR05-11/SR20-21/SR28-29.
Primary authored; no personal FIT data, providers, UI or app-role claim.
"""
import json
from unittest import mock
from django.db import DatabaseError, transaction
from django.test import TransactionTestCase
from datara import models as m
from datara.db import OwnerScopedStore
from datara.metric_store import SavedMetricStore, MetricStoreRefusal
from datara.metric_projection import project_recorded_result
from datara.recorded_metrics import prepare_recorded_input, summarize_recorded, prepare_overall_trend
from datara.scoped_input import prepare_scoped_input
from datara.tests.test_recorded_regressions import CORE
from datara.tests.test_scoped_input import _Owner, make_scope, SYNTHETIC_POLICY

class SavedMetricGraphRegressions(TransactionTestCase):
    def setUp(self):
        self.owner = _Owner("saved-graph-owner")
        self.other = _Owner("saved-graph-other")
        self.store = SavedMetricStore.for_user(self.owner.user)
        self.foreign = SavedMetricStore.for_user(self.other.user)
        self.activity = self.owner.add_accepted(start_utc="2026-09-01T06:00:00Z")

    def prepared(self, trend=False):
        scope = make_scope(start_utc="2026-08-31T00:00:00Z", end_utc="2026-10-02T00:00:00Z")
        version = prepare_scoped_input(
            scope=scope, records=self.owner.inputs.scope_candidates(scope, CORE),
            field_specs=CORE, policy=SYNTHETIC_POLICY)
        handle = self.owner.inputs.append_version(version)
        data = prepare_recorded_input(version)
        result = prepare_overall_trend(data) if trend else summarize_recorded(data)
        return handle, result

    def save(self, trend=False):
        handle, result = self.prepared(trend)
        saved = self.store.save_prepared_metrics(handle.version_ref, result)
        return handle, result, saved

    def test_summary_roundtrip_exact_bytes_addressed_evidence_and_source_floor(self):
        handle, result, saved = self.save()
        self.assertTrue(saved.created)
        self.assertEqual(saved.state, "complete")
        read = self.store.get_metric(saved.metric_id)
        self.assertEqual(read.canonical_content, result.canonical_content)
        self.assertEqual(read.canonical_registry_content,
                         project_recorded_result(result).canonical_registry_content)
        document = json.loads(read.canonical_content)
        self.assertEqual(document["values"][0]["activity_count"]["value"], "1")
        self.assertEqual(document["values"][0]["elapsed_ms"]["value"], "3600000")
        rows = list(m.Evidence.objects.for_owner(self.owner.user.pk).filter(metric_id=saved.metric_id))
        self.assertEqual(len(rows), 4)
        self.assertEqual(m.MetricOperand.objects.for_owner(self.owner.user.pk).count(), 3)
        self.assertEqual(m.MetricSeal.objects.for_owner(self.owner.user.pk).count(), 1)
        for row in rows:
            addressed = self.store.get_metric_evidence(row.pk)
            self.assertEqual(addressed.metric.state, "complete")
            self.assertEqual(addressed.value_path, row.value_path)
            self.assertEqual(addressed.canonical_registry_entry.decode("ascii"), row.value_canonical)
            self.assertIsNone(row.method_version)
            self.assertEqual(row.method_inputs, {})
            with self.assertRaises(m.ResourceNotVisible):
                OwnerScopedStore.for_user(self.owner.user).get_evidence(row.pk)
        self.assertEqual(len(self.owner.inputs.provenance_rows(handle.version_ref)), 5)

    def test_complete_week_trend_saves_and_reads_without_replacing_summary(self):
        for day in ("2026-09-07", "2026-09-14", "2026-09-21"):
            self.owner.add_accepted(start_utc=day + "T06:00:00Z")
        handle, summary, first = self.save()
        _, trend = self.prepared(True)
        self.assertTrue(trend.eligible)
        second = self.store.save_prepared_metrics(handle.version_ref, trend)
        self.assertNotEqual(first.metric_id, second.metric_id)
        self.assertEqual(self.store.get_metric(first.metric_id).canonical_content, summary.canonical_content)
        self.assertEqual(self.store.get_metric(second.metric_id).canonical_content, trend.canonical_content)
        self.assertEqual(len(self.store.list_metrics_for_snapshot(handle.version_ref)), 2)

    def test_exact_retry_reuses_one_complete_graph(self):
        handle, result, first = self.save()
        counts = [model.objects.for_owner(self.owner.user.pk).count()
                  for model in (m.Metric, m.MetricOperand, m.MetricSeal, m.Evidence)]
        second = self.store.save_prepared_metrics(handle.version_ref, result)
        self.assertFalse(second.created)
        self.assertEqual(second.metric_id, first.metric_id)
        self.assertEqual(counts, [model.objects.for_owner(self.owner.user.pk).count()
                                 for model in (m.Metric, m.MetricOperand, m.MetricSeal, m.Evidence)])

    def test_foreign_metric_evidence_and_snapshot_are_unavailable(self):
        handle, result, saved = self.save()
        evidence = m.Evidence.objects.for_owner(self.owner.user.pk).filter(metric_id=saved.metric_id).first()
        for action in (lambda: self.foreign.get_metric(saved.metric_id),
                       lambda: self.foreign.get_metric_evidence(evidence.pk),
                       lambda: self.foreign.list_metrics_for_snapshot(handle.version_ref),
                       lambda: self.foreign.save_prepared_metrics(handle.version_ref, result)):
            with self.assertRaisesRegex(MetricStoreRefusal, "resource_not_available"):
                action()

    def test_second_computed_evidence_failure_rolls_back_entire_graph_then_retry(self):
        handle, result = self.prepared()
        create = m.Evidence.objects.create
        calls = []
        def fail_second(**kwargs):
            if kwargs.get("kind") == m.Evidence.KIND_COMPUTED_METRIC:
                calls.append(kwargs["value_path"])
                if len(calls) == 2:
                    raise DatabaseError("synthetic database failure")
            return create(**kwargs)
        with mock.patch.object(m.Evidence.objects, "create", side_effect=fail_second):
            with self.assertRaises(MetricStoreRefusal) as caught:
                self.store.save_prepared_metrics(handle.version_ref, result)
        self.assertNotIn("synthetic database failure", str(caught.exception))
        self.assertEqual(len(calls), 2)
        for model in (m.Metric, m.MetricOperand, m.MetricSeal):
            self.assertEqual(model.objects.for_owner(self.owner.user.pk).count(), 0)
        self.assertEqual(m.Evidence.objects.for_owner(self.owner.user.pk).filter(kind="computed_metric").count(), 0)
        self.assertEqual(self.store.save_prepared_metrics(handle.version_ref, result).state, "complete")

    def test_outer_transaction_rollback_keeps_no_provisional_graph(self):
        handle, result = self.prepared()
        with self.assertRaisesRegex(RuntimeError, "synthetic outer rollback"):
            with transaction.atomic():
                self.assertEqual(self.store.save_prepared_metrics(handle.version_ref, result).state, "complete")
                raise RuntimeError("synthetic outer rollback")
        self.assertEqual(m.Metric.objects.for_owner(self.owner.user.pk).count(), 0)
        self.assertEqual(m.MetricSeal.objects.for_owner(self.owner.user.pk).count(), 0)

    def test_sealed_graph_rejects_update_delete_and_additional_evidence(self):
        handle, result, saved = self.save()
        metric = m.Metric.objects.for_owner(self.owner.user.pk).get(pk=saved.metric_id)
        evidence = m.Evidence.objects.for_owner(self.owner.user.pk).filter(metric=metric).first()
        actions = [
            lambda: m.Metric.objects.for_owner(self.owner.user.pk).filter(pk=metric.pk).update(metric_code="changed"),
            lambda: m.Metric.objects.for_owner(self.owner.user.pk).filter(pk=metric.pk)._raw_delete("default"),
            lambda: m.Evidence.objects.create(owner=self.owner.user, snapshot_id=handle.version_ref,
                                             kind="computed_metric", metric=metric, value_path="/extra",
                                             value_canonical=evidence.value_canonical),
        ]
        for action in actions:
            with self.assertRaises(DatabaseError):
                with transaction.atomic():
                    action()
        self.assertEqual(self.store.get_metric(saved.metric_id).canonical_content, result.canonical_content)

    def test_commit_rejects_new_metric_without_graph_and_seal(self):
        _, _, saved = self.save()
        original = m.Metric.objects.for_owner(self.owner.user.pk).get(pk=saved.metric_id)
        values = {field.attname: getattr(original, field.attname)
                  for field in m.Metric._meta.concrete_fields
                  if field.name not in {"metric_id", "created_at", "creation_txid"}}
        values["content_digest"] = "sha256:" + "a" * 64
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                m.Metric.objects.create(**values)
        self.assertEqual(m.Metric.objects.for_owner(self.owner.user.pk).count(), 1)

    def test_changed_source_is_unavailable_and_saved_history_is_preserved(self):
        _, result, saved = self.save()
        m.Session.objects.for_owner(self.owner.user.pk).filter(activity=self.activity).update(elapsed_duration_ms=1000)
        read = self.store.get_metric(saved.metric_id)
        self.assertEqual(read.state, "source_unavailable")
        self.assertIsNone(read.canonical_content)
        stored = m.Metric.objects.for_owner(self.owner.user.pk).get(pk=saved.metric_id)
        self.assertEqual(stored.canonical_content.encode("ascii"), result.canonical_content)
