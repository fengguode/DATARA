"""WP05 TK64 read-surface acceptance checks (synthetic, no database access).

Scope: CUS09/CUS10; SR19-SR21/SR31. These focused tests exercise the actual
URLconf/views with a store double. They prove request-boundary behavior and exact
pass-through, not PostgreSQL persistence or a real authenticated session.
"""
from __future__ import annotations

import ast
import hashlib
import json
import socket
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.core.management import call_command
from django.core.cache import cache
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.test.runner import DiscoverRunner

from datara.app_surface import recorded_metric_detail
from datara.metric_store import MetricStoreRefusal, SavedMetric, SavedMetricStore
from datara.saved_metric_read import API_VERSION, RESOURCE_METRIC


OWNER_ID = 17001
METRIC_ID = "3f2b1c40-0000-4000-8000-000000000001"
FOREIGN_ID = "3f2b1c40-0000-4000-8000-000000000002"
MISSING_ID = "3f2b1c40-0000-4000-8000-00000000ffff"
SAVED_BYTES = b'{"synthetic_saved_value":"1700000000"}'


class _SurfaceTests(SimpleTestCase):
    def setUp(self) -> None:
        cache.clear()
        self.factory = RequestFactory()
        self.owner = SimpleNamespace(pk=OWNER_ID, is_authenticated=True)

    def request(self, metric_id: str = METRIC_ID, *, owner=None, **headers):
        request = self.factory.get(f"/api/v1/recorded-metrics/{metric_id}", **headers)
        request.user = self.owner if owner is None else owner
        return request

    @staticmethod
    def saved_metric(state: str = "complete") -> SavedMetric:
        return SavedMetric(
            metric_id=METRIC_ID,
            snapshot_id="3f2b1c40-0000-4000-8000-000000000010",
            state=state,
            canonical_content=SAVED_BYTES if state == "complete" else None,
            canonical_registry_content=b"{}" if state == "complete" else None,
            canonical_method_identity=b"{}" if state == "complete" else None,
        )

    def install_store(self, store):
        return mock.patch.object(SavedMetricStore, "for_user", return_value=store)


class AcceptanceA1AndA2(_SurfaceTests):
    def test_a1_django_system_check_loads_the_real_urlconf(self) -> None:
        # SQLite is explicitly an in-memory unit-check deviation. No database
        # file or PostgreSQL connection is used by this system check.
        memory_db = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
        with override_settings(DATABASES=memory_db):
            call_command("check", verbosity=0)

    def test_a2_django_runner_collects_existing_and_both_wp05_modules(self) -> None:
        suite = DiscoverRunner(verbosity=0).build_suite(["datara.tests"])
        identifiers = {
            case.id()
            for case in _walk_tests(suite)
        }
        self.assertGreater(len(identifiers), 200)
        self.assertTrue(any("test_saved_metrics" in item for item in identifiers))
        self.assertTrue(any("test_app_surface" in item for item in identifiers))
        self.assertTrue(any("test_session_identity" in item for item in identifiers))


def _walk_tests(suite):
    for item in suite:
        if hasattr(item, "_tests"):
            yield from _walk_tests(item)
        else:
            yield item


class ReadContractAcceptance(_SurfaceTests):
    def test_a3_owned_read_preserves_the_store_bytes_exactly(self) -> None:
        saved = self.saved_metric()
        canonical_content = SAVED_BYTES.decode("ascii")
        envelope = {
            "api_version": API_VERSION,
            "resource_type": RESOURCE_METRIC,
            "metric_id": METRIC_ID,
            "canonical_content": canonical_content,
        }
        store = mock.Mock()
        store.get_metric.return_value = saved
        with self.install_store(store), mock.patch(
            "datara.saved_metric_read._complete_metric_envelope",
            return_value=("complete", {"envelope": envelope}),
        ):
            response = recorded_metric_detail(self.request(), METRIC_ID)

        body = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["canonical_content"].encode("ascii"), saved.canonical_content)
        store.get_metric.assert_called_once_with(METRIC_ID)

    def test_a4_foreign_and_missing_ids_have_identical_denials(self) -> None:
        bodies = []
        statuses = []
        for metric_id in (FOREIGN_ID, MISSING_ID):
            store = mock.Mock()
            store.get_metric.side_effect = MetricStoreRefusal("resource_not_available")
            with self.install_store(store):
                response = recorded_metric_detail(self.request(metric_id), metric_id)
            statuses.append(response.status_code)
            bodies.append(response.content)
        self.assertEqual(statuses, [404, 404])
        self.assertEqual(bodies[0], bodies[1])

    def test_a5_identity_is_taken_from_request_user_not_client_carriers(self) -> None:
        # The approved contract rejects query/body input; it does not use those
        # values to construct the owner scope. A foreign-owner header is inert.
        query_store = mock.Mock()
        query_request = self.factory.get(
            f"/api/v1/recorded-metrics/{METRIC_ID}?owner_id={FOREIGN_ID}"
        )
        query_request.user = self.owner
        with self.install_store(query_store) as query_factory:
            query_response = recorded_metric_detail(query_request, METRIC_ID)
        self.assertEqual(query_response.status_code, 422)
        query_factory.assert_not_called()

        header_store = mock.Mock()
        header_store.get_metric.side_effect = MetricStoreRefusal("resource_not_available")
        with self.install_store(header_store) as header_factory:
            header_response = recorded_metric_detail(
                self.request(HTTP_X_DATARA_OWNER_ID=str(FOREIGN_ID)), METRIC_ID
            )
        self.assertEqual(header_response.status_code, 404)
        header_factory.assert_called_once_with(self.owner)

        body_store = mock.Mock()
        request = self.factory.post(
            f"/api/v1/recorded-metrics/{METRIC_ID}",
            data=json.dumps({"owner_id": FOREIGN_ID}),
            content_type="application/json",
        )
        request.user = self.owner
        with self.install_store(body_store):
            body_response = recorded_metric_detail(request, METRIC_ID)
        self.assertEqual(body_response.status_code, 405)
        body_store.get_metric.assert_not_called()

    def test_a6_unauthenticated_request_is_denied_before_store_construction(self) -> None:
        anonymous = SimpleNamespace(pk=OWNER_ID, is_authenticated=False)
        with mock.patch.object(SavedMetricStore, "for_user") as factory:
            response = recorded_metric_detail(self.request(owner=anonymous), METRIC_ID)
        self.assertEqual(response.status_code, 401)
        factory.assert_not_called()

    def test_a7_read_route_does_not_open_a_socket_or_import_a_provider(self) -> None:
        store = mock.Mock()
        store.get_metric.return_value = self.saved_metric("unsupported_decoder")
        with self.install_store(store), \
             mock.patch.object(socket, "socket", side_effect=AssertionError("socket attempted")), \
             mock.patch.object(socket, "create_connection", side_effect=AssertionError("socket attempted")):
            response = recorded_metric_detail(self.request(), METRIC_ID)
        self.assertEqual(response.status_code, 200)

        package = Path(__file__).resolve().parents[1]
        reachable = (
            "app_surface.py", "saved_metric_read.py", "views.py",
            "session_identity.py", "urls.py", "read_rate_limit.py",
        )
        forbidden = {"socket", "requests", "httpx", "urllib", "openai", "anthropic"}
        for filename in reachable:
            tree = ast.parse((package / filename).read_text(encoding="utf-8"))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".", 1)[0])
            self.assertFalse(forbidden & imports, f"forbidden imports in {filename}")

    def test_a8_read_never_recomputes_or_writes_and_keeps_digest_stable(self) -> None:
        saved = self.saved_metric()
        digest_before = hashlib.sha256(saved.canonical_content).hexdigest()
        envelope = {"api_version": API_VERSION, "canonical_content": saved.canonical_content.decode("ascii")}
        store = mock.Mock()
        store.get_metric.return_value = saved
        store.prepare_and_save_metric.side_effect = AssertionError("recompute reached")
        store.save_prepared_metrics.side_effect = AssertionError("write reached")
        with self.install_store(store), mock.patch(
            "datara.saved_metric_read._complete_metric_envelope",
            return_value=("complete", {"envelope": envelope}),
        ):
            response = recorded_metric_detail(self.request(), METRIC_ID)
        self.assertEqual(response.status_code, 200)
        store.get_metric.assert_called_once_with(METRIC_ID)
        store.prepare_and_save_metric.assert_not_called()
        store.save_prepared_metrics.assert_not_called()
        self.assertEqual(hashlib.sha256(saved.canonical_content).hexdigest(), digest_before)
