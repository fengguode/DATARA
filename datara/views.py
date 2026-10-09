"""Rendered local saved-metric detail page over the same read projection."""
from __future__ import annotations

import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.cache import patch_vary_headers
from django.views.decorators.csrf import csrf_exempt

from datara.saved_metric_read import (
    ERROR_MESSAGES, _metric_read, _status_message, decode_page_projection,
)


def _page_response(request: HttpRequest, template: str, context: dict,
                   status: int = 200) -> HttpResponse:
    response = render(request, template, context=context, status=status,
                      content_type="text/html; charset=utf-8")
    response["Cache-Control"] = "private, no-store"
    patch_vary_headers(response, ("Cookie",))
    if status == 405:
        response["Allow"] = "GET, HEAD"
    if request.method == "HEAD":
        response["Content-Length"] = str(len(response.content))
        response.content = b""
    return response


@csrf_exempt
def recorded_metric_page(request: HttpRequest, metric_id: str) -> HttpResponse:
    status, body = _metric_read(request, metric_id)
    if status != 200:
        error = body.get("error", {})
        code = error.get("code", "retrieval_unavailable")
        message = ERROR_MESSAGES.get(code, ERROR_MESSAGES["retrieval_unavailable"])
        return _page_response(request, "datara/saved_metric_detail.html", {
            "error": {"code": code, "message": message},
        }, status)

    if body.get("state") != "complete":
        state = body.get("state", "unavailable")
        return _page_response(request, "datara/saved_metric_detail.html", {
            "state_message": _status_message(state),
            "state": state,
        })

    try:
        decoded = decode_page_projection(body)
    except (ValueError, TypeError, KeyError, AttributeError, UnicodeError, OverflowError):
        # Page support failure does not change the API's store-validated bytes.
        return _page_response(request, "datara/saved_metric_detail.html", {
            "page_unsupported": True,
            "state_message": "Saved detail cannot be displayed by this page.",
        })

    content = decoded["content"]
    evidence = [{**entry, "entry_text": json.dumps({"payload": entry["payload"],
                  "derivation": entry["derivation"]}, sort_keys=True,
                  ensure_ascii=True, indent=2)} for entry in decoded["entries"]]
    page = {
        "metric_id": body["metric_id"],
        "snapshot_id": body["snapshot_id"],
        "selected_scope": content["selected_scope"],
        "effective_scope": content["effective_scope"],
        "method_identity": content["method_identity"],
        "eligibility": content["eligibility"],
        "limitations": content["limitations"],
        "metric_code": content["metric_code"],
        "values": content["values"],
        "manifest": content["manifest"],
        "operands": content["operands"],
        "classification": content.get("classification"),
        "evidence": evidence,
        "values_text": json.dumps(content["values"], sort_keys=True, ensure_ascii=True, indent=2),
        "scope_text": json.dumps({"selected": content["selected_scope"],
                                   "effective": content["effective_scope"]},
                                  sort_keys=True, ensure_ascii=True, indent=2),
        "method_text": json.dumps(content["method_identity"], sort_keys=True,
                                   ensure_ascii=True, indent=2),
        "operands_text": json.dumps(content["operands"], sort_keys=True,
                                     ensure_ascii=True, indent=2),
    }
    return _page_response(request, "datara/saved_metric_detail.html", {"page": page})


__all__ = ["recorded_metric_page"]
