"""Synthetic PostgreSQL saved history across independent Python processes.

WP02/WP03; CUS02-03/CUS08/CUS10; SR03/SR05-07/SR20-21/SR28-29.
No server restart, app-role isolation, provider or athlete acceptance claim.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

from django.db import connection, transaction
from django.test import TransactionTestCase

from datara.metric_store import SavedMetricStore
from datara.recorded_metrics import prepare_recorded_input, summarize_recorded, prepare_overall_trend
from datara.scoped_input import prepare_scoped_input
from datara.tests.test_recorded_regressions import CORE
from datara.tests.test_scoped_input import _Owner, make_scope, SYNTHETIC_POLICY

CHILD = r'''
import json, os, sys
import django
django.setup()
from django.contrib.auth import get_user_model
from django.db import connection, connections
from datara.metric_store import SavedMetricStore, MetricStoreRefusal
from datara import models as m

if connection.vendor != "postgresql" or not str(connection.settings_dict["NAME"]).startswith("test_datara_history_"):
    raise SystemExit(2)
try:
    user = get_user_model().objects.get(pk=sys.argv[1])
    store = SavedMetricStore.for_user(user)
    snapshot = None
    try:
        snapshot = store.get_snapshot(sys.argv[2])
        records = []
        for metric_id in sys.argv[3:]:
            result = store.get_metric(metric_id)
            records.append({"id": result.metric_id, "snapshot": result.snapshot_id,
                "state": result.state, "content": result.canonical_content.decode("ascii"),
                "registry": result.canonical_registry_content.decode("ascii"),
                "method": result.canonical_method_identity.decode("ascii")})
        payload = {"state": "complete", "snapshot_content": snapshot.canonical_payload,
                   "metrics": records}
    except (m.ResourceNotVisible, MetricStoreRefusal):
        denied = []
        for metric_id in sys.argv[3:]:
            try:
                store.get_metric(metric_id)
                denied.append({"available": True})
            except MetricStoreRefusal as error:
                denied.append({"available": False, "reason": error.reason_code})
        payload = {"state": "unavailable", "snapshot_available": snapshot is not None, "metrics": denied}
    payload["process_id"] = os.getpid()
    print(json.dumps(payload, sort_keys=True))
finally:
    connections.close_all()
'''


class MetricHistoryProcessBoundary(TransactionTestCase):
    def setUp(self):
        self.assertEqual(connection.vendor, "postgresql")
        self.assertTrue(str(connection.settings_dict["NAME"]).startswith("test_datara_history_"))
        self.owner = _Owner("history-process-owner")
        self.other = _Owner("history-process-other")
        for day in ("2026-09-01", "2026-09-07", "2026-09-14", "2026-09-21"):
            self.owner.add_accepted(start_utc=day + "T06:00:00Z")
        scope = make_scope(start_utc="2026-08-31T00:00:00Z", end_utc="2026-10-02T00:00:00Z")
        self.version = prepare_scoped_input(scope=scope,
            records=self.owner.inputs.scope_candidates(scope, CORE),
            field_specs=CORE, policy=SYNTHETIC_POLICY)
        self.handle = self.owner.inputs.append_version(self.version)
        self.store = SavedMetricStore.for_user(self.owner.user)

    def save(self):
        data = prepare_recorded_input(self.version)
        return tuple(self.store.save_prepared_metrics(self.handle.version_ref, result)
                     for result in (summarize_recorded(data), prepare_overall_trend(data)))

    def child(self, owner, saved):
        environment = os.environ.copy()
        environment["DJANGO_SETTINGS_MODULE"] = "datara.settings"
        environment["DATARA_DB_NAME"] = str(connection.settings_dict["NAME"])
        process = subprocess.run([sys.executable, "-X", "utf8", "-c", CHILD,
            str(owner.user.pk), str(self.handle.version_ref), *(r.metric_id for r in saved)],
            cwd=Path(__file__).resolve().parents[2], env=environment,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            encoding="utf-8", timeout=30, check=False)
        # Child diagnostics may include database connection information: never echo them.
        self.assertEqual(process.returncode, 0, "synthetic child retrieval failed; diagnostics suppressed")
        payload = json.loads(process.stdout)
        self.assertNotEqual(payload.pop("process_id"), os.getpid())
        return payload

    def test_new_interpreter_retrieves_exact_committed_snapshot_and_both_metrics(self):
        saved = self.save()
        self.assertEqual(self.child(self.owner, saved), {
            "state": "complete", "snapshot_content": self.version.canonical_payload,
            "metrics": [{"id": r.metric_id, "snapshot": r.snapshot_id, "state": r.state,
                "content": r.canonical_content.decode("ascii"),
                "registry": r.canonical_registry_content.decode("ascii"),
                "method": r.canonical_method_identity.decode("ascii")} for r in saved]})

    def test_new_interpreter_cannot_resolve_foreign_snapshot_or_saved_metrics(self):
        saved = self.save()
        self.assertEqual(self.child(self.other, saved), {"state": "unavailable", "snapshot_available": False,
            "metrics": [{"available": False, "reason": "resource_not_available"} for _ in saved]})
        for record in saved:
            self.assertEqual(self.store.get_metric(record.metric_id).canonical_content, record.canonical_content)

    def test_outer_rollback_has_no_saved_metric_visible_to_new_interpreter(self):
        class RollbackProbe(Exception):
            pass
        try:
            with transaction.atomic():
                saved = self.save()
                raise RollbackProbe()
        except RollbackProbe:
            pass
        self.assertEqual(self.child(self.owner, saved), {"state": "unavailable", "snapshot_available": True,
            "metrics": [{"available": False, "reason": "resource_not_available"} for _ in saved]})
        self.assertEqual(self.store.list_metrics_for_snapshot(self.handle.version_ref), ())

