"""Bounded synthetic PostgreSQL concurrency coverage for WP02/WP03.

CUS03-05/CUS08/CUS10; SR05-11/SR20-21/SR28-29. Independent thread
connections exercise cooperative owner locking and complete graph reuse.
No FIT files, providers or production/application-role claims are involved.
"""
from contextlib import contextmanager
from threading import Event, Thread, current_thread
from time import monotonic
from unittest import mock

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase

from datara import models as m
from datara.metric_store import MetricStoreRefusal, SavedMetricStore
from datara.recorded_metrics import prepare_overall_trend, prepare_recorded_input, summarize_recorded
from datara.scoped_input import prepare_scoped_input
from datara.tests.test_recorded_regressions import CORE
from datara.tests.test_scoped_input import SYNTHETIC_POLICY, _Owner, make_scope


class SavedMetricConcurrencyRegressions(TransactionTestCase):
    def setUp(self):
        if connections["default"].vendor != "postgresql":
            self.skipTest("requires PostgreSQL owner-row locking and graph constraints")
        self.owner = _Owner("metric-concurrency-owner")
        self.other = _Owner("metric-concurrency-foreign")
        for day in ("2026-09-01", "2026-09-07", "2026-09-14", "2026-09-21"):
            self.owner.add_accepted(start_utc=day + "T06:00:00Z")
        scope = make_scope(start_utc="2026-08-31T00:00:00Z", end_utc="2026-10-02T00:00:00Z")
        version = prepare_scoped_input(
            scope=scope, records=self.owner.inputs.scope_candidates(scope, CORE),
            field_specs=CORE, policy=SYNTHETIC_POLICY)
        self.snapshot = self.owner.inputs.append_version(version).version_ref
        data = prepare_recorded_input(version)
        self.summary = summarize_recorded(data)
        self.trend = prepare_overall_trend(data)
        self.store = SavedMetricStore.for_user(self.owner.user)

    def overlapping_saves(self, first_result, second_result):
        """Hold the first real owner lock until PostgreSQL sees the second wait.

        Events order connection startup and lock acquisition. The assertion is
        actual pg_blocking_pids membership, not a timing guess or sleeping race.
        Every event, SQL lock and thread join has a finite bound.
        """
        first_locked, second_attempting, release_first = Event(), Event(), Event()
        backend_ids, results, errors = {}, {}, {}
        original = SavedMetricStore._owner_serialized_write

        @contextmanager
        def gated_lock(store):
            name = current_thread().name
            if name == "metric-save-second":
                second_attempting.set()
            with original(store):
                if name == "metric-save-first":
                    first_locked.set()
                    if not release_first.wait(20):
                        raise AssertionError("first writer release deadline exceeded")
                yield

        def save(name, result):
            connection = connections["default"]
            try:
                # Django connections are thread-local; each worker opens and
                # closes its own backend and never receives the main connection.
                connection.close()
                with connection.cursor() as cursor:
                    cursor.execute("SET statement_timeout = '12s'")
                    cursor.execute("SET lock_timeout = '10s'")
                    cursor.execute("SELECT pg_backend_pid()")
                    backend_ids[name] = cursor.fetchone()[0]
                user = get_user_model().objects.get(pk=self.owner.user.pk)
                results[name] = SavedMetricStore.for_user(user).save_prepared_metrics(self.snapshot, result)
            except BaseException as error:
                errors[name] = error
            finally:
                connection.close()

        first = Thread(target=save, args=("first", first_result), name="metric-save-first", daemon=True)
        second = Thread(target=save, args=("second", second_result), name="metric-save-second", daemon=True)
        with mock.patch.object(SavedMetricStore, "_owner_serialized_write", gated_lock):
            try:
                first.start()
                self.assertTrue(first_locked.wait(5), "first writer failed to acquire its owner lock")
                second.start()
                self.assertTrue(second_attempting.wait(5), "second writer did not enter the owner-lock boundary")
                self.assertNotEqual(backend_ids["first"], backend_ids["second"])
                deadline, observed = monotonic() + 5, False
                while monotonic() < deadline:
                    with connections["default"].cursor() as cursor:
                        cursor.execute("SELECT pg_blocking_pids(%s)", [backend_ids["second"]])
                        blockers = cursor.fetchone()[0]
                    if backend_ids["first"] in blockers:
                        observed = True
                        break
                    # Bounded event waiting throttles observation; success still
                    # requires PostgreSQL to report the actual first blocker.
                    release_first.wait(0.01)
                self.assertTrue(observed, "second backend was never observed waiting on first writer")
            finally:
                release_first.set()
                first.join(15)
                if second.ident is not None:
                    second.join(15)
            self.assertFalse(first.is_alive(), "first writer did not terminate")
            self.assertFalse(second.is_alive(), "second writer did not terminate")
        self.assertEqual(errors, {}, {name: repr(error) for name, error in errors.items()})
        self.assertEqual(set(results), {"first", "second"})
        return results["first"], results["second"]

    def assert_complete_graph(self, saved, result):
        read = self.store.get_metric(saved.metric_id)
        self.assertEqual(read.state, "complete")
        self.assertEqual(read.canonical_content, result.canonical_content)
        self.assertEqual(m.MetricSeal.objects.for_owner(self.owner.user.pk).filter(metric_id=saved.metric_id).count(), 1)
        # Four synthetic activities each supply exactly three core operands.
        self.assertEqual(m.MetricOperand.objects.for_owner(self.owner.user.pk).filter(parent_metric_id=saved.metric_id).count(), 12)
        evidence = m.Evidence.objects.for_owner(self.owner.user.pk).filter(metric_id=saved.metric_id)
        for row in evidence:
            self.assertEqual(self.store.get_metric_evidence(row.pk).metric.state, "complete")
        return evidence.count()

    def test_overlapping_identical_calls_return_one_complete_sealed_graph(self):
        first, second = self.overlapping_saves(self.summary, self.summary)
        self.assertEqual(first.metric_id, second.metric_id)
        self.assertEqual(first.snapshot_id, second.snapshot_id)
        self.assertTrue(first.created)
        self.assertFalse(second.created)
        self.assertEqual(self.assert_complete_graph(first, self.summary), 4)
        self.assertEqual(m.Metric.objects.for_owner(self.owner.user.pk).count(), 1)
        self.assertEqual(m.MetricSeal.objects.for_owner(self.owner.user.pk).count(), 1)
        self.assertEqual(m.MetricOperand.objects.for_owner(self.owner.user.pk).count(), 12)
        self.assertEqual(len(self.store.list_metrics_for_snapshot(self.snapshot)), 1)

    def test_overlapping_distinct_results_keep_two_graphs_and_foreign_owner_refuses(self):
        first, second = self.overlapping_saves(self.summary, self.trend)
        self.assertNotEqual(first.metric_id, second.metric_id)
        self.assertTrue(first.created)
        self.assertTrue(second.created)
        self.assertEqual(self.assert_complete_graph(first, self.summary), 4)
        # manifest, eligibility, 8 week values, 5 totals and sign classification.
        self.assertEqual(self.assert_complete_graph(second, self.trend), 16)
        self.assertEqual(m.Metric.objects.for_owner(self.owner.user.pk).count(), 2)
        self.assertEqual(m.MetricSeal.objects.for_owner(self.owner.user.pk).count(), 2)
        self.assertEqual(m.MetricOperand.objects.for_owner(self.owner.user.pk).count(), 24)
        self.assertEqual(len(self.store.list_metrics_for_snapshot(self.snapshot)), 2)
        foreign = SavedMetricStore.for_user(self.other.user)
        for action in (
            lambda: foreign.save_prepared_metrics(self.snapshot, self.summary),
            lambda: foreign.list_metrics_for_snapshot(self.snapshot),
            lambda: foreign.get_metric(first.metric_id),
        ):
            with self.assertRaisesRegex(MetricStoreRefusal, "resource_not_available"):
                action()
        self.assertEqual(m.Metric.objects.for_owner(self.other.user.pk).count(), 0)

