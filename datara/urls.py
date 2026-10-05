"""Provisional internal URL map for the identity-bound read surface.

WP05 (TK64); CUS09; SR19, SR20.

ROUTE NAMING IS HELD, NOT DECIDED
---------------------------------
Discussion #369 owns the public route naming, the response envelope and the API
version, and that decision is **not approved**. It is an open owner-decision
Discussion whose candidate artifact is not on ``main``. Nothing here is a
contract, and the path below must not be read as one:

* it carries **no version segment**, deliberately, because a version string is
  part of the contract #369 has not approved;
* it sits under an ``internal/`` prefix and is documented as provisional;
* the resolver name is likewise provisional.

When #369 is approved these values are expected to change. That is recorded
here as a known-open item rather than resolved by guesswork.

There is exactly one route. It exists so that ``manage.py check`` and the Django
test client have a resolvable surface to exercise; it is not an inventory of
what the product should expose. History lists, pagination and read-token issuance
are #369's subsequent increments and are absent here.

There is no ``handler404``. Django 5.2 does not require one (its ``urls.W005``
is the duplicate-namespace warning, not a missing-404 check), so every refusal
is produced inside the view by :func:`datara.app_surface.saved_metric_view`,
which renders the generic denial directly. Stated precisely, because the
absolute form of this claim is false and was corrected on review: an **unmatched**
path still resolves to Django's built-in technical 404 page. That page is
uniform, is served with ``DEBUG=False``, and discloses **nothing about whether
any metric exists** -- so SR21's indistinguishability is unaffected -- but it
does mean route enumeration is possible against this URLconf. What is guaranteed
is the narrower and sufficient claim: **no request for the route above produces
a response shape other than the generic denial or the owner's own metric bytes.**

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

from django.urls import path

from datara import app_surface

#: Documented so a reader can see that the provisional path has no version
#: segment in it, and that adding one is #369's call rather than an oversight.
PROVISIONAL_ROUTE_PREFIX = "internal/saved-metric/"

PROVISIONAL_ROUTE_NAME = "datara-internal-saved-metric"

urlpatterns = [
    path(
        f"{PROVISIONAL_ROUTE_PREFIX}<str:metric_id>",
        app_surface.saved_metric_view,
        name=PROVISIONAL_ROUTE_NAME,
    ),
]

__all__ = [
    "PROVISIONAL_ROUTE_NAME",
    "PROVISIONAL_ROUTE_PREFIX",
    "urlpatterns",
]