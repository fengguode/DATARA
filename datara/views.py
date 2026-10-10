"""Minimal same-origin login and saved recorded-metric read views (WP05)."""
from __future__ import annotations

from django.contrib.auth import views as auth_views
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from datara.saved_metric_read import (
    API_VERSION,
    ERRORS,
    SavedReadUnavailable,
    decode_page_metric,
    evidence_document,
    metric_document,
    operation_allowed,
    rate_limited,
)


def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "datara/home.html", {"logout_url": reverse("logout")})


class DataraLoginView(auth_views.LoginView):
    template_name = "datara/login.html"
    redirect_authenticated_user = True


class DataraLogoutView(auth_views.LogoutView):
    next_page = "/login/"


def _decorate(response, *, is_api: bool):
    response["Cache-Control"] = "private, no-store"
    response["Vary"] = "Cookie"
    if is_api:
        response["Content-Type"] = "application/json; charset=utf-8"
    else:
        response["Content-Type"] = "text/html; charset=utf-8"
    return response


def _json_response(document: dict, status: int = 200):
    return _decorate(JsonResponse(document, status=status), is_api=True)


def _api_error(code: str, status: int):
    return _json_response({
        "api_version": API_VERSION,
        "error": {"code": code, "message": ERRORS[code]},
    }, status)


def _render_page_error(request, code: str, status: int):
    response = render(request, "datara/read_error.html",
                      {"code": code, "message": ERRORS[code]}, status=status)
    return _decorate(response, is_api=False)


def _input_is_empty(request) -> bool:
    # The detail contract accepts no query string and no request body. Inspect
    # only this transport input; no object or owner query happens before it.
    if request.GET:
        return False
    if request.META.get("HTTP_TRANSFER_ENCODING"):
        return False
    content_length = request.META.get("CONTENT_LENGTH", "")
    if content_length:
        try:
            if int(content_length) > 0:
                return False
        except (TypeError, ValueError):
            return False
    try:
        return request.body == b""
    except Exception:
        return False


def _head(request, response):
    if request.method == "HEAD":
        response.content = b""
    return response


def _gate(request, *, is_api: bool):
    """Contract order: authentication, policy, method, rate, input, then IDs."""
    if not getattr(request.user, "is_authenticated", False):
        response = _api_error("authentication_required", 401) if is_api else _render_page_error(
            request, "authentication_required", 401)
        return _head(request, response)
    try:
        if not operation_allowed(request):
            response = _api_error("operation_denied", 403) if is_api else _render_page_error(
                request, "operation_denied", 403)
            return _head(request, response)
        if request.method not in ("GET", "HEAD"):
            response = _api_error("method_not_allowed", 405) if is_api else _render_page_error(
                request, "method_not_allowed", 405)
            response["Allow"] = "GET, HEAD"
            return _head(request, response)
        if rate_limited(request):
            response = _api_error("rate_limited", 429) if is_api else _render_page_error(
                request, "rate_limited", 429)
            return _head(request, response)
        if not _input_is_empty(request):
            response = _api_error("invalid_request", 422) if is_api else _render_page_error(
                request, "invalid_request", 422)
            return _head(request, response)
    except Exception:
        response = _api_error("retrieval_unavailable", 503) if is_api else _render_page_error(
            request, "retrieval_unavailable", 503)
        return _head(request, response)
    return None


def _read_failure(request, error: SavedReadUnavailable, *, is_api: bool):
    code = error.code
    status = {
        "resource_not_available": 404,
        "retrieval_unavailable": 503,
    }.get(code, 503)
    response = _api_error(code, status) if is_api else _render_page_error(request, code, status)
    return _head(request, response)


@csrf_exempt
def recorded_metric_api(request, metric_id: str):
    failure = _gate(request, is_api=True)
    if failure is not None:
        return failure
    try:
        document = metric_document(request.user, metric_id)
    except SavedReadUnavailable as error:
        return _read_failure(request, error, is_api=True)
    return _head(request, _json_response(document))


@csrf_exempt
def recorded_metric_evidence_api(request, metric_id: str, evidence_id: str):
    failure = _gate(request, is_api=True)
    if failure is not None:
        return failure
    try:
        document = evidence_document(request.user, metric_id, evidence_id)
    except SavedReadUnavailable as error:
        return _read_failure(request, error, is_api=True)
    return _head(request, _json_response(document))


@csrf_exempt
def recorded_metric_page(request, metric_id: str):
    failure = _gate(request, is_api=False)
    if failure is not None:
        return failure
    try:
        document = metric_document(request.user, metric_id)
    except SavedReadUnavailable as error:
        return _read_failure(request, error, is_api=False)
    if document["state"] != "complete":
        message = ("Saved history exists, but this reader cannot display it."
                   if document["state"] == "unsupported_decoder"
                   else "Saved detail cannot currently be validated.")
        page = {"supported": False, "display_message": message}
    else:
        page = decode_page_metric(document)
    response = render(request, "datara/saved_metric_detail.html", {
        "document": document,
        "page": page,
        "logout_url": reverse("logout"),
    })
    return _head(request, _decorate(response, is_api=False))


__all__ = [
    "home", "DataraLoginView", "DataraLogoutView", "recorded_metric_api",
    "recorded_metric_evidence_api", "recorded_metric_page",
]
