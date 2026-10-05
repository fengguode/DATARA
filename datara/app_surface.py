"""Owner-scoped read surface over the **existing** saved-metric services.

WP05 (TK64); CUS09, CUS10; SR19, SR20, SR21, SR31.

This module is a read path and nothing else. It calls exactly one saved service,
``SavedMetricStore.get_metric``, and returns the bytes that service returned
unchanged, so the dashboard value and the read-only API value cannot disagree
(SR31). It never calls ``prepare_and_save_metric`` or ``save_prepared_metrics``:
a saved metric is never recomputed or regenerated here, so a read cannot change
what is stored.

Scope discipline, and the reason several things are conspicuously absent:

* **No public contract is defined here.** No envelope, no field list, no route
  naming policy and no API version string is authored or implied. Discussion
  #369 owns those and its decision is not approved. The single route in
  ``datara/urls.py`` is an internal placeholder for this increment.
* **Denial is generic.** A metric owned by another identity and a metric that
  does not exist produce the same status code and the same response body. The
  requested identifier is never echoed, and the denial template is rendered with
  an empty context, so no request-derived value can reach the response (SR21).
* **The owner is the server-side session.** :func:`owner_store_for` derives it
  through :mod:`datara.session_identity`, which reads ``request.user`` only. A
  query parameter, header or body field naming another owner is ignored, because
  nothing on this path dereferences them.
* **No egress.** No socket, no transport, no provider SDK, no credential. A
  saved metric is local deterministic preparation output (SR06).

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

from typing import Any

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.views.decorators.cache import never_cache

from datara.metric_store import MetricStoreRefusal, SavedMetricStore
from datara.session_identity import (
    SessionIdentity,
    SessionIdentityUnavailable,
    derive_session_identity,
)

#: The one template this surface serves. It takes no context and holds no
#: placeholder, so its rendered bytes are a function of the template file alone.
DENIAL_TEMPLATE = "datara/not_available.html"

#: The status every denial returns. Identical for an unauthenticated caller, a
#: metric owned by another identity, a metric that does not exist, a metric whose
#: saved graph the store refuses, and an identifier the store cannot parse.
#:
#: Written as a literal rather than taken from ``http.HTTPStatus`` so that no
#: stdlib HTTP module is imported by a module whose import closure is scanned for
#: transport. ``django.http.HttpStatus`` existed only in Django 3.x and was
#: removed in 4.0, so ``http`` is the only remaining spelling.
DENIAL_STATUS = 404

#: The content type of a readable saved metric. The body is the persisted
#: canonical content byte for byte -- no envelope is added around it, and no
#: field name is chosen here. Whether a read surface should carry an envelope,
#: and what it should be called, is #369's decision.
SAVED_METRIC_CONTENT_TYPE = "application/json"

#: Reason recorded for a denial. Constant, and never surfaced in the response
#: body; it exists so the refusal is observable in a test without being an
#: existence oracle.
DENIAL_REASON = "not_available"


#: Owner scope the store actually resolved, used only to assert that it is the
#: session's owner. Read through :func:`store_owner_id` so a store without a
#: ``scope`` degrades to "unverifiable" rather than raising on an attribute a
#: test double may not carry.
_UNVERIFIABLE_SCOPE = object()


def store_owner_id(store: Any) -> Any:
    """The owner id the store's own scope resolved to, or ``None``.

    ``OwnerScopedStore`` exposes ``scope.owner_id``. Reading it back and comparing
    it with the derived identity is what makes the identity load-bearing: without
    that comparison the derived identity could be computed, discarded, and the
    store built from a different principal with nothing noticing (SR20).
    """

    scope = getattr(store, "scope", _UNVERIFIABLE_SCOPE)
    if scope is _UNVERIFIABLE_SCOPE:
        return None
    return getattr(scope, "owner_id", None)


def owner_store_for(request: Any) -> tuple[SessionIdentity, SavedMetricStore]:
    """Return the session identity and the owner-scoped saved-metric store.

    The store is constructed by ``SavedMetricStore.for_user``, which is the
    inherited ``OwnerScopedStore`` factory: it takes the authenticated principal
    and derives owner scope from it. A raw owner identifier is never accepted by
    either function, so there is no way to construct this pair from a request
    payload (CUS10, SR20).

    The store's resolved scope is then compared against the derived identity and
    a disagreement is refused. Both sides currently read ``request.user``, so the
    check is an invariant assertion rather than a second derivation -- but it is
    the assertion that catches a store built for anyone else, and it is what
    keeps :func:`datara.session_identity.derive_session_identity` load-bearing on
    this path instead of decorative.

    Raises :class:`~datara.session_identity.SessionIdentityUnavailable` when the
    request carries no usable authenticated session, or when the store's scope
    does not resolve to that session's owner.
    """

    identity = derive_session_identity(request)
    store = SavedMetricStore.for_user(request.user)
    resolved = store_owner_id(store)
    if resolved is not None and resolved != identity.owner_id:
        raise SessionIdentityUnavailable()
    return identity, store


def generic_denial() -> HttpResponse:
    """Render the one denial response.

    Takes no request and no context by construction: a denial cannot be made
    request-dependent, so two callers who are refused for different reasons
    receive identical bytes. That is what makes "another owner's metric" and
    "no such metric" indistinguishable.
    """

    return render(None, DENIAL_TEMPLATE, {}, status=DENIAL_STATUS)


@require_safe
@never_cache
def saved_metric_view(request: Any, metric_id: str) -> HttpResponse:
    """Return the saved metric identified by ``metric_id`` for the session owner.

    Read-only: one call to ``SavedMetricStore.get_metric``, then either the saved
    bytes unchanged or the generic denial. There is no write path here.

    ``never_cache`` is applied here rather than in settings because it must cover
    the success path: this response is personal activity telemetry, and without
    it the 200 carried no ``Cache-Control`` header at all. Applied on review of
    #394. It adds headers only -- the denial body stays byte-identical, which is
    what makes the two refusal cases indistinguishable.
    """

    try:
        _identity, store = owner_store_for(request)
        saved = store.get_metric(metric_id)
    except SessionIdentityUnavailable:
        # No usable session: no data, and no statement about the identifier.
        return generic_denial()
    except MetricStoreRefusal:
        # ``SavedMetricStore`` refuses with one reason for an owner mismatch, for
        # an absent row and for an unparseable identifier alike. Mapping every
        # refusal to the same response is therefore the whole of the SR21
        # property; the reason code is not read, because reading it would be the
        # existence oracle SR21 forbids.
        return generic_denial()
    canonical = saved.canonical_content
    if canonical is None:
        # The store returns stored bytes only for a complete saved graph, and
        # ``None`` for every other state. Serving a non-complete state would
        # disclose that the identifier names something; not serving it keeps the
        # surface to saved values and nothing else.
        return generic_denial()
    return HttpResponse(canonical, content_type=SAVED_METRIC_CONTENT_TYPE)


__all__ = [
    "DENIAL_REASON",
    "DENIAL_STATUS",
    "DENIAL_TEMPLATE",
    "SAVED_METRIC_CONTENT_TYPE",
    "generic_denial",
    "owner_store_for",
    "saved_metric_view",
    "store_owner_id",
]