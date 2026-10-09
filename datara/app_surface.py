"""HTTP transport for the approved recorded-metric read contract only."""
from __future__ import annotations

import json

from django.http import HttpRequest, HttpResponse
from django.utils.cache import patch_vary_headers
from django.views.decorators.csrf import csrf_exempt

from datara.saved_metric_read import API_VERSION, evidence_read, metric_read


def _json_response(request: HttpRequest, status: int, body: dict) -> HttpResponse:
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode("ascii")
    response = HttpResponse(payload, status=status,
                            content_type="application/json; charset=utf-8")
    response["Cache-Control"] = "private, no-store"
    patch_vary_headers(response, ("Cookie",))
    if status == 405:
        response["Allow"] = "GET, HEAD"
    if request.method == "HEAD":
        response["Content-Length"] = str(len(response.content))
        response.content = b""
    return response


@csrf_exempt
def recorded_metric_detail(request: HttpRequest, metric_id: str) -> HttpResponse:
    status, body = metric_read(request, metric_id)
    return _json_response(request, status, body)


@csrf_exempt
def recorded_metric_evidence(request: HttpRequest, metric_id: str,
                             evidence_id: str) -> HttpResponse:
    status, body = evidence_read(request, metric_id, evidence_id)
    return _json_response(request, status, body)


__all__ = ["recorded_metric_detail", "recorded_metric_evidence"]
