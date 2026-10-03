"""Synthetic Snapshot/Evidence contention; WP02/03 CUS03-05/CUS08/CUS10.

SR05-11/SR20-21/SR28-29. Primary authored; actual PostgreSQL connection
and lock observation, no application-role, provider or athlete-validation claim.
"""
from contextlib import contextmanager
from threading import Event, Thread, current_thread
from time import monotonic
from unittest import mock

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase

from datara import models as m
from datara.db import OwnerScopedStore
from datara.scoped_input import MilestoneAInputStore, prepare_scoped_input
from datara.tests.test_recorded_regressions import CORE
from datara.tests.test_scoped_input import SYNTHETIC_POLICY, _Owner, make_scope


class ScopedVersionConcurrencyRegressions(TransactionTestCase):
    def setUp(self):
        if connections["default"].vendor != "postgresql":
            self.skipTest("requires PostgreSQL owner serialization")
        self.owner = _Owner("version-concurrency-owner")
        self.other = _Owner("version-concurrency-other")
        self.owner.add_accepted(start_utc="2026-09-01T06:00:00Z")

    def prepared(self, start="2026-08-31T00:00:00Z"):
        scope = make_scope(start_utc=start, end_utc="2026-10-02T00:00:00Z")
        return prepare_scoped_input(
            scope=scope, records=self.owner.inputs.scope_candidates(scope, CORE),
            field_specs=CORE, policy=SYNTHETIC_POLICY)

    def overlapping_appends(self, versions):
        locked, attempting, release = Event(), Event(), Event()
        pids, results, errors = {}, {}, {}
        original = OwnerScopedStore._owner_serialized_write

        @contextmanager
        def observed(store):
            if current_thread().name == "version-second":
                attempting.set()
            with original(store):
                if current_thread().name == "version-first":
                    locked.set()
                    if not release.wait(20):
                        raise AssertionError("holder release deadline exceeded")
                yield

        def append(name, version):
            connection = connections["default"]
            try:
                connection.close()
                with connection.cursor() as cursor:
                    cursor.execute("SET statement_timeout = '12s'")
                    cursor.execute("SET lock_timeout = '10s'")
                    cursor.execute("SELECT pg_backend_pid()")
                    pids[name] = cursor.fetchone()[0]
                user = get_user_model().objects.get(pk=self.owner.user.pk)
                inputs = MilestoneAInputStore(OwnerScopedStore.for_user(user))
                results[name] = inputs.append_version(version)
            except BaseException as error:
                errors[name] = type(error).__name__
            finally:
                connection.close()

        first = Thread(target=append, args=("first", versions[0]), name="version-first", daemon=True)
        second = Thread(target=append, args=("second", versions[1]), name="version-second", daemon=True)
        with mock.patch.object(OwnerScopedStore, "_owner_serialized_write", observed):
            try:
                first.start()
                self.assertTrue(locked.wait(5), "first append did not acquire owner lock")
                second.start()
                self.assertTrue(attempting.wait(5), "second append did not attempt owner lock")
                self.assertNotEqual(pids["first"], pids["second"])
                deadline, saw_lock = monotonic() + 5, False
                while monotonic() < deadline:
                    with connections["default"].cursor() as cursor:
                        cursor.execute("SELECT pg_blocking_pids(%s)", [pids["second"]])
                        if pids["first"] in cursor.fetchone()[0]:
                            saw_lock = True
                            break
                    release.wait(0.01)
                self.assertTrue(saw_lock, "PostgreSQL did not report actual append contention")
            finally:
                release.set()
                first.join(15)
                if second.ident is not None:
                    second.join(15)
            self.assertFalse(first.is_alive())
            self.assertFalse(second.is_alive())
        self.assertEqual(errors, {})
        self.assertEqual(set(results), {"first", "second"})
        return results["first"], results["second"]

    def assert_complete_version(self, handle, version):
        read = self.owner.inputs.get_version(handle.version_ref)
        self.assertEqual(read.canonical_payload, version.canonical_payload)
        self.assertEqual(read.input_digest, version.input_digest)
        self.assertEqual(len(self.owner.inputs.provenance_rows(handle.version_ref)), 5)
        self.assertEqual(m.Evidence.objects.for_owner(self.owner.user.pk)
                         .filter(snapshot_id=handle.version_ref).count(), 5)

    def test_contending_identical_appends_reuse_complete_snapshot_and_evidence(self):
        version = self.prepared()
        first, second = self.overlapping_appends((version, version))
        self.assertEqual(first.version_ref, second.version_ref)
        self.assertTrue(first.created)
        self.assertFalse(second.created)
        self.assertEqual(m.Snapshot.objects.for_owner(self.owner.user.pk).count(), 1)
        self.assert_complete_version(first, version)

    def test_contending_distinct_versions_preserve_both_complete_histories(self):
        original, changed = self.prepared(), self.prepared("2026-09-01T00:00:00Z")
        first, second = self.overlapping_appends((original, changed))
        self.assertNotEqual(first.version_ref, second.version_ref)
        self.assertTrue(first.created)
        self.assertTrue(second.created)
        self.assertEqual(m.Snapshot.objects.for_owner(self.owner.user.pk).count(), 2)
        self.assert_complete_version(first, original)
        self.assert_complete_version(second, changed)
        with self.assertRaises(m.ResourceNotVisible):
            self.other.inputs.get_version(first.version_ref)
        self.assertEqual(m.Snapshot.objects.for_owner(self.other.user.pk).count(), 0)
