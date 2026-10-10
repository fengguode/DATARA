"""Focused synthetic request-boundary tests for the WP05 saved read surface."""
import json
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from datara import views
from datara.saved_metric_read import API_VERSION, ERRORS, SavedReadUnavailable
from datara.metric_projection import project_recorded_result
from datara.recorded_metrics import prepare_overall_trend, summarize_recorded
from datara.tests.test_recorded_regressions import prepared as prepared_input


METRIC_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
OWNER = SimpleNamespace(is_authenticated=True, pk=41)
SAVED_DOCUMENT = {
    "api_version": API_VERSION,
    "resource_type": "recorded_metric",
    "metric_id": METRIC_ID,
    "snapshot_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    "state": "complete",
    "reader_version": "saved-recorded-reader/1",
    "canonical_content": "{\"persisted\":true}",
    "canonical_registry_content": "{\"entries\":[]}",
    "canonical_method_identity": "{\"method_id\":\"activity-summary\"}",
    "evidence": [],
}


class WP05RequestBoundaryTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse("recorded_metric_api", kwargs={"metric_id": METRIC_ID})
        self.page_url = reverse("recorded_metric_page", kwargs={"metric_id": METRIC_ID})

    def request(self, method="get", **kwargs):
        request = getattr(self.factory, method)(self.url, **kwargs)
        request.user = OWNER
        return request

    def test_authenticated_detail_returns_saved_canonical_carriers_and_no_store_headers(self):
        request = self.request()
        with patch.object(views, "metric_document", return_value=SAVED_DOCUMENT) as read:
            response = views.recorded_metric_api(request, METRIC_ID)
        read.assert_called_once_with(OWNER, METRIC_ID)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertEqual(response["Vary"], "Cookie")
        body = json.loads(response.content)
        self.assertEqual(body["canonical_content"], SAVED_DOCUMENT["canonical_content"])
        self.assertEqual(set(body), set(SAVED_DOCUMENT))

    def test_anonymous_get_is_rejected_before_any_saved_store_read(self):
        request = self.factory.get(self.url)
        request.user = AnonymousUser()
        with patch.object(views, "metric_document") as read:
            response = views.recorded_metric_api(request, METRIC_ID)
        read.assert_not_called()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content), {
            "api_version": API_VERSION,
            "error": {"code": "authentication_required",
                      "message": ERRORS["authentication_required"]},
        })

    def test_foreign_missing_and_malformed_ids_share_generic_not_found(self):
        bodies = []
        statuses = []
        for identifier in (METRIC_ID, "cccccccc-cccc-4ccc-8ccc-cccccccccccc", "not-a-uuid"):
            request = self.request()
            with patch.object(views, "metric_document",
                              side_effect=SavedReadUnavailable("resource_not_available")):
                response = views.recorded_metric_api(request, identifier)
            bodies.append(response.content)
            statuses.append(response.status_code)
        self.assertEqual(statuses, [404, 404, 404])
        self.assertEqual(bodies[0], bodies[1])
        self.assertEqual(bodies[1], bodies[2])
        self.assertNotIn(METRIC_ID.encode(), bodies[0])

    def test_client_owner_header_is_not_used_as_identity(self):
        request = self.request(HTTP_X_DATARA_OWNER="999")
        with patch.object(views, "metric_document", return_value=SAVED_DOCUMENT) as read:
            response = views.recorded_metric_api(request, METRIC_ID)
        read.assert_called_once_with(OWNER, METRIC_ID)
        self.assertEqual(response.status_code, 200)

    def test_query_or_body_is_rejected_before_identifier_lookup(self):
        body_request = self.factory.generic(
            "GET", self.url, data="owner_id=999",
            content_type="application/x-www-form-urlencoded")
        body_request.user = OWNER
        requests = (
            (self.request(QUERY_STRING="owner_id=999"), 422, "invalid_request"),
            (self.request("post", data="owner_id=999",
                          content_type="application/x-www-form-urlencoded"),
             405, "method_not_allowed"),
            (body_request, 422, "invalid_request"),
        )
        for request, status, error_code in requests:
            with patch.object(views, "metric_document") as read:
                response = views.recorded_metric_api(request, "bad-id")
            read.assert_not_called()
            self.assertEqual(response.status_code, status)
            self.assertEqual(json.loads(response.content)["error"]["code"], error_code)

    def test_dispatcher_precedence_and_method_allow(self):
        request = self.request("post", data="owner_id=1",
                                content_type="application/x-www-form-urlencoded")
        with patch.object(views, "operation_allowed", return_value=True), \
                patch.object(views, "rate_limited", return_value=False), \
                patch.object(views, "metric_document") as read:
            response = views.recorded_metric_api(request, "bad-id")
        read.assert_not_called()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response["Allow"], "GET, HEAD")

    def test_head_uses_get_decision_and_sends_no_body(self):
        request = self.request("head")
        with patch.object(views, "metric_document", return_value=SAVED_DOCUMENT):
            response = views.recorded_metric_api(request, METRIC_ID)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertEqual(response["Cache-Control"], "private, no-store")

    def test_retrieval_error_page_retries_clean_authorized_get_with_live_status(self):
        request = self.factory.get(self.page_url)
        request.user = OWNER
        with patch.object(views, "operation_allowed", return_value=True), \\
                patch.object(views, "rate_limited", return_value=False), \\
                patch.object(views, "metric_document",
                             side_effect=SavedReadUnavailable("retrieval_unavailable")):
            response = views.recorded_metric_page(request, METRIC_ID)

        self.assertEqual(response.status_code, 503)
        self.assertIn(('<form method="get" action="{}"'.format(self.page_url)).encode(), response.content)
        self.assertIn(b">Retry read</button>", response.content)
        self.assertIn(b'role="status" aria-live="polite"', response.content)
        self.assertIn("Retrying saved detail…".encode(), response.content)
        self.assertNotIn(b"?", response.content)

    def test_non_retrieval_error_page_has_no_retry_action(self):
        request = self.factory.get(self.page_url)
        request.user = OWNER
        response = views._render_page_error(request, "invalid_request", 422)

        self.assertEqual(response.status_code, 422)
        self.assertNotIn(b">Retry read</button>", response.content)
    def page_document(self, result):
        projection = project_recorded_result(result)
        content = projection.canonical_content
        registry = projection.canonical_registry_content
        content_object = json.loads(content)
        registry_object = json.loads(registry)
        evidence = []
        for index, entry in enumerate(registry_object["entries"]):
            if entry["type"] != "numeric":
                continue
            evidence_id = f"dddddddd-dddd-4ddd-8ddd-{index:012d}"
            evidence.append({
                "evidence_id": evidence_id,
                "value_path": entry["path"],
                "href": reverse("recorded_metric_evidence_api", kwargs={
                    "metric_id": METRIC_ID,
                    "evidence_id": evidence_id,
                }),
            })
        canonical = lambda value: json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return {
            "api_version": API_VERSION,
            "resource_type": "recorded_metric",
            "metric_id": METRIC_ID,
            "snapshot_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
            "state": "complete",
            "reader_version": "saved-recorded-reader/1",
            "canonical_content": content.decode("ascii"),
            "canonical_registry_content": registry.decode("ascii"),
            "canonical_method_identity": canonical(content_object["method_identity"]),
            "evidence": evidence,
        }

    def test_page_decoder_supports_pinned_summary_and_week_trend(self):
        _, summary_input = prepared_input([
            (1, "2026-09-01T06:00:00Z", 1001, "running"),
            (2, "2026-09-02T06:00:00Z", 2002, "running"),
        ])
        summary = views.decode_page_metric(self.page_document(
            summarize_recorded(summary_input)))
        self.assertTrue(summary["supported"])
        self.assertIn('"activity_count"', summary["values_json"])
        self.assertIn("integer_milliseconds", summary["values_json"])

        _, trend_input = prepared_input([
            (11, "2026-08-31T00:00:00Z", 1000, "running"),
            (12, "2026-09-07T00:00:00Z", 2000, "cycling"),
            (13, "2026-09-14T00:00:00Z", 4000, "running"),
            (14, "2026-09-21T00:00:00Z", 8000, "cycling"),
            (15, "2026-09-28T00:00:00Z", 999000, "running"),
        ])
        trend = views.decode_page_metric(self.page_document(
            prepare_overall_trend(trend_input)))
        self.assertTrue(trend["supported"])
        self.assertEqual(trend["classification"], "increased")
        self.assertEqual(len(json.loads(trend["buckets_json"])), 4)
        self.assertIn("3000", trend["values_json"])
        self.assertIn("percent", trend["values_json"])

    def test_page_decoder_fails_closed_on_unknown_content_version(self):
        _, summary_input = prepared_input([
            (1, "2026-09-01T06:00:00Z", 1001, "running"),
        ])
        document = self.page_document(summarize_recorded(summary_input))
        content = json.loads(document["canonical_content"])
        content["metric_contract_version"] = "future/unknown"
        document["canonical_content"] = json.dumps(
            content, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        decoded = views.decode_page_metric(document)
        self.assertFalse(decoded["supported"])
        self.assertEqual(decoded["display_message"],
                         "Saved detail cannot be displayed by this page.")

    def test_page_decoder_rejects_unrecognized_nested_member_shape(self):
        _, summary_input = prepared_input([
            (1, "2026-09-01T06:00:00Z", 1001, "running"),
        ])
        document = self.page_document(summarize_recorded(summary_input))
        content = json.loads(document["canonical_content"])
        content["manifest"]["members"][0]["operands"][0]["unapproved"] = "value"
        document["canonical_content"] = json.dumps(
            content, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        decoded = views.decode_page_metric(document)
        self.assertFalse(decoded["supported"])
        self.assertNotIn("values_json", decoded)
        self.assertNotIn("evidence", decoded)

    def test_page_decoder_rejects_registry_payload_or_reference_mismatch(self):
        _, summary_input = prepared_input([
            (1, "2026-09-01T06:00:00Z", 1001, "running"),
        ])
        document = self.page_document(summarize_recorded(summary_input))
        registry = json.loads(document["canonical_registry_content"])
        entry = next(row for row in registry["entries"] if row["type"] == "numeric")
        entry["payload"]["value"] = "999"
        document["canonical_registry_content"] = json.dumps(
            registry, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        decoded = views.decode_page_metric(document)
        self.assertFalse(decoded["supported"])
        self.assertEqual(decoded["display_message"],
                         "Saved detail cannot be displayed by this page.")
