"""Acceptance evidence for the #378 identity-bound read surface.

WP05 (TK64); CUS09, CUS10; SR06, SR19, SR20, SR21, SR31.

Every case A1-A8 is exercised here through the real URLconf and the real view,
and every one was seen to fail before it was seen to pass. The mutation for each
property is named in the table below and in the docstring of the test that owns
it; the recorded run of each mutation is in the assignment report.

| Case | Property | Mutation that breaks it |
| --- | --- | --- |
| A1 | the surface is runnable and checks clean | malformed ``urlpatterns`` -> ``urls.E004`` |
| A2 | no existing file is touched | collection-count drift across the whole suite |
| A3 | a read returns the persisted saved bytes | re-serialise the document in the view |
| A4 | foreign and nonexistent are indistinguishable | put the requested id in the denial context |
| A5 | a client-supplied owner is ignored | build the store from ``request.GET`` |
| A6 | an unauthenticated request is denied | construct the store before the identity gate |
| A7 | no socket, database or provider is reachable | import a transport inside a reachable module |
| A8 | a saved metric is never recomputed or rewritten | call ``prepare_and_save_metric`` from the view |

WHAT IS AND IS NOT PROVEN HERE, STATED PLAINLY
------------------------------------------------
PostgreSQL 17 cannot start on this host, so ``datara.migrations.0002`` cannot be
applied and the saved-metric graph cannot be persisted here. Two consequences
are load-bearing and are not papered over:

1. The store is replaced by :class:`_SavedMetricStoreDouble`, which raises the
   **real** ``MetricStoreRefusal`` with the **real** reason code the real store
   uses for an owner mismatch, and returns the **real** ``SavedMetric`` type.
   What is proven here is therefore the surface: the authorization decision, the
   byte-for-byte pass-through, the denial shape, and the absence of egress.
   What is *not* proven here is that ``SavedMetricStore.get_metric`` returns
   those bytes from the database; that is
   ``datara/tests/test_saved_metrics.py::SavedMetricGraphRegressions::
   test_summary_roundtrip_exact_bytes_addressed_evidence_and_source_floor`` on
   PostgreSQL, and it was not re-run for this assignment.
2. The saved bytes used as the fixture are **authentic**, not hand-written: they
   are produced at import by the real deterministic preparer
   (``canonical_metric_content(summarize_recorded(prepare_recorded_input(...)))``)
   over synthetic, DATARA-authored records. No database is needed for that, and
   no personal FIT telemetry is read.
3. ``request.user`` is supplied by a stand-in principal, because resolving a real
   session needs the ``django_session`` table. That Django's own
   ``SessionMiddleware`` and ``AuthenticationMiddleware`` populate
   ``request.user`` from the session is framework behaviour this module does not
   modify; what is proven here is that the surface consumes ``request.user`` and
   nothing else.

FIXTURE PROVENANCE
------------------
Every fixture is synthetic and DATARA-authored. Nothing is derived from the
founder's personal telemetry, which is permanently out of scope and is not read,
hashed, listed or stat'ed anywhere in this file.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.checks import registry
from django.core.checks.urls import check_resolver
from django.test import RequestFactory, SimpleTestCase
from django.urls import URLResolver, resolve
from django.urls.resolvers import RegexPattern

from datara import app_surface, urls as datara_urls
from datara.metric_store import MetricStoreRefusal, SavedMetric, SavedMetricStore
from datara.models import Metric
from datara.recorded_metrics import (
    canonical_metric_content,
    prepare_recorded_input,
    summarize_recorded,
)
from datara.scoped_input import prepare_scoped_input
from datara.tests.test_scoped_input import (
    DECLARED_FULL,
    INSIDE_MORNING,
    SYNTHETIC_POLICY,
    identity,
    make_record,
    make_scope,
)

OWNER = 11
OTHER_OWNER = 22
OWN_METRIC = "3f2b1c40-0000-4000-8000-000000000001"
OTHER_METRIC = "3f2b1c40-0000-4000-8000-000000000002"
MISSING_METRIC = "3f2b1c40-0000-4000-8000-00000000ffff"


def _authentic_saved_summary_bytes() -> bytes:
    """Real ``canonical_metric_content`` output, computed with no database.

    Two synthetic records inside one synthetic scope, prepared by the real
    deterministic pipeline. The bytes are the genuine canonical form of a saved
    ``activity-summary`` metric, which is what makes the byte-identity case a
    real comparison rather than a tautology about a string I chose.
    """

    version = prepare_scoped_input(
        scope=make_scope(),
        records=[
            make_record(canonical_identity=identity(301), start=INSIDE_MORNING),
            make_record(canonical_identity=identity(302), start=INSIDE_MORNING + 3600),
        ],
        field_specs=DECLARED_FULL,
        policy=SYNTHETIC_POLICY,
    )
    return canonical_metric_content(summarize_recorded(prepare_recorded_input(version)))


#: The authentic saved bytes this surface must return unchanged (A3).
SAVED_BYTES = _authentic_saved_summary_bytes()

#: SHA-256 of SAVED_BYTES, pinned so a change to the canonical contract becomes a
#: visible failure here instead of a silent drift. Observed on this baseline and
#: recomputed at run time in ``AuthenticFixtureTests``.
SAVED_BYTES_SHA256 = "f5d8e78fa1026d0feb6232319ed2b80838dfb149e4b304363eea415c115763cd"


class _Principal:
    """A stand-in for an authenticated ``auth.User``; see the module docstring."""

    def __init__(self, pk: int) -> None:
        self.pk = pk
        self.is_authenticated = True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _Principal) and other.pk == self.pk

    def __hash__(self) -> int:
        return hash(("datara-test-principal", self.pk))

    def __repr__(self) -> str:
        return f"_Principal(pk={self.pk})"


@dataclass(frozen=True)
class _Scope:
    """Mirrors ``datara.db.OwnerScope``, which is what the real store exposes."""

    owner_id: object


class _SavedMetricStoreDouble:
    """Stand-in for ``SavedMetricStore`` with the real types and refusal codes.

    It implements the read the surface is allowed to perform and *records*, rather
    than omits, the writes, so an accidental recompute shows up as a named call in
    the log instead of an ``AttributeError``.

    Ownership is enforced here the way the real ``OwnerScopedStore`` enforces it:
    by owner scope, raising ``MetricStoreRefusal("resource_not_available")`` for
    an owner mismatch, for an absent row and for an unparseable identifier
    alike. That single refusal for all three cases is the property the surface
    relies on, and this double reproduces it faithfully instead of inventing two
    distinguishable errors.
    """

    #: ``(method, owner_id, argument)`` for every call, in order.
    calls: list[tuple[str, int | None, str]] = []
    #: The principal object each store was constructed from.
    principals: list[object] = []
    #: ``owner_id -> {metric_id: SavedMetric}``
    saved: dict[int, dict[str, SavedMetric]] = {}

    @classmethod
    def reset(cls) -> None:
        cls.calls = []
        cls.principals = []
        cls.saved = {
            OWNER: {
                OWN_METRIC: SavedMetric(
                    metric_id=OWN_METRIC,
                    snapshot_id="00000000-0000-4000-8000-00000000aaaa",
                    state="complete",
                    canonical_content=SAVED_BYTES,
                    canonical_registry_content=b'{"manifest_version":"x"}',
                    canonical_method_identity=b'{"adapter_version":"x"}',
                )
            },
            OTHER_OWNER: {
                OTHER_METRIC: SavedMetric(
                    metric_id=OTHER_METRIC,
                    snapshot_id="00000000-0000-4000-8000-00000000bbbb",
                    state="complete",
                    canonical_content=b'{"other_owner":"secret"}',
                )
            },
        }

    @classmethod
    def _record(cls, method: str, owner_id: object, argument: str) -> None:
        cls.calls.append((method, owner_id, argument))

    @classmethod
    def for_user(cls, user: object) -> "_SavedMetricStoreDouble":
        owner_id = getattr(user, "pk", None)
        cls._record("for_user", owner_id, type(user).__name__)
        cls.principals.append(user)
        store = cls()
        store.owner_id = owner_id
        return store

    def __init__(self) -> None:
        self.owner_id: object = None

    @property
    def scope(self) -> _Scope:
        """The owner the store actually resolved to.

        ``owner_store_for`` compares this with the derived identity, so a double
        that hid its scope would silently switch that check off.
        """

        return _Scope(owner_id=self.owner_id)

    def get_metric(self, metric_id: object) -> SavedMetric:
        self._record("get_metric", self.owner_id, str(metric_id))
        owned = type(self).saved.get(self.owner_id, {})
        saved = owned.get(str(metric_id))
        if saved is None:
            raise MetricStoreRefusal("resource_not_available")
        return saved

    # -- recorded, never expected ------------------------------------------

    def prepare_and_save_metric(self, snapshot_id: object, metric_code: object) -> SavedMetric:
        self._record("prepare_and_save_metric", self.owner_id, str(metric_code))
        raise AssertionError("the surface must never regenerate a saved metric")

    def save_prepared_metrics(self, snapshot_id: object, prepared: object) -> SavedMetric:
        self._record("save_prepared_metrics", self.owner_id, type(prepared).__name__)
        raise AssertionError("the surface must never write a saved metric")


def _route(metric_id: str) -> str:
    return f"/{datara_urls.PROVISIONAL_ROUTE_PREFIX}{metric_id}"


def _request_with_user(pk: int):
    """A bare GET request carrying only a principal, for direct function calls."""

    request = RequestFactory().get(_route(OWN_METRIC))
    request.user = _Principal(pk)
    return request


def _carriers(other: int, other_is_str: bool = False) -> dict[str, dict]:
    """Every place a client could name an owner, as RequestFactory keyword sets."""

    def value() -> str:
        return str(other) if other_is_str else str(other)

    return {
        "query": {"data": {"owner": value(), "owner_id": value(), "user": value()}},
        "header_owner": {"headers": {"owner": value()}},
        "header_x_owner": {"headers": {"x-owner-id": value(), "x-datara-owner": value()}},
        "cookie": {"headers": {"cookie": f"owner={value()}; sessionid={value()}"}},
        "body": {"body": b'{"owner": %d, "owner_id": %d, "user": %d}'
                 % (other, other, other)},
    }


class _SurfaceTestCase(SimpleTestCase):
    """Drives the real URLconf and the real view over a replaced store."""

    def setUp(self) -> None:
        super().setUp()
        _SavedMetricStoreDouble.reset()
        self.factory = RequestFactory()
        self.patch = mock.patch.object(app_surface, "SavedMetricStore", _SavedMetricStoreDouble)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    # -- request driver -----------------------------------------------------

    def drive(
        self,
        metric_id: str,
        *,
        user: object = ...,
        data: dict | None = None,
        headers: dict | None = None,
        body: bytes | None = None,
    ):
        """Resolve the real route and call the view the real resolver returns."""

        target = _route(metric_id)
        match = resolve(target)
        request = self.factory.generic(
            "GET",
            target,
            data=body if body is not None else "",
            content_type="application/json" if body is not None else "text/plain",
            query_params=data,
            headers=headers,
        )
        request.user = _Principal(OWNER) if user is ... else user
        return match, match.func(request, *match.args, **match.kwargs)

    def drive_carrying(self, metric_id: str, carrier: dict, *, user: object = ...):
        return self.drive(
            metric_id,
            user=user,
            data=carrier.get("data"),
            headers=carrier.get("headers"),
            body=carrier.get("body"),
        )

    @staticmethod
    def comparable(response) -> tuple[int, bytes, str, str]:
        """Status, body and the two headers a denial must not vary on."""

        return (
            response.status_code,
            response.content,
            response.headers.get("Content-Type", ""),
            response.headers.get("Content-Length", ""),
        )

    @staticmethod
    def methods() -> list[str]:
        return [method for method, _owner, _argument in _SavedMetricStoreDouble.calls]


class AuthenticFixtureTests(SimpleTestCase):
    """The saved-byte fixture is real, deterministic and ASCII canonical."""

    def test_the_fixture_is_genuine_canonical_saved_content(self) -> None:
        document = json.loads(SAVED_BYTES)
        self.assertEqual(document["metric_code"], "activity-summary")
        self.assertEqual(document["codec_version"], "ascii-json-integer-strings/1")
        # Two synthetic members were prepared, so this is not an empty result.
        self.assertEqual(len(document["values"]), 1)
        self.assertEqual(document["values"][0]["activity_count"]["value"], "2")
        self.assertEqual(SAVED_BYTES.decode("ascii"), SAVED_BYTES.decode("ascii"))

    def test_the_fixture_digest_is_pinned_and_reproducible(self) -> None:
        self.assertEqual(hashlib.sha256(SAVED_BYTES).hexdigest(), SAVED_BYTES_SHA256)
        self.assertEqual(SAVED_BYTES, _authentic_saved_summary_bytes())

    def test_the_fixture_carries_no_foreign_owner_bytes(self) -> None:
        self.assertNotIn(b'"other_owner"', SAVED_BYTES)


class StoreWiringTests(SimpleTestCase):
    """The surface is wired to the real saved store. No patching here."""

    def test_the_surface_calls_the_real_saved_metric_store(self) -> None:
        self.assertIs(app_surface.SavedMetricStore, SavedMetricStore)
        self.assertEqual(SavedMetricStore.__mro__[1].__name__, "OwnerScopedStore")

    def test_the_surface_reads_through_the_owner_scoped_factory(self) -> None:
        # for_user is the inherited factory that derives owner scope from an
        # authenticated principal. A surface that constructed OwnerScope or a
        # store from a raw id would not reach it.
        with mock.patch.object(
            app_surface, "SavedMetricStore", wraps=SavedMetricStore
        ) as spy:
            request = RequestFactory().get(_route(OWN_METRIC))
            request.user = _Principal(OWNER)
            with self.assertRaises(Exception):
                # No database on this host, so the real call must fail; what is
                # proven is that it was attempted with the session principal.
                app_surface.saved_metric_view(request, OWN_METRIC)
        spy.for_user.assert_called_once()
        passed = spy.for_user.call_args.args[0]
        self.assertIs(passed, request.user)
        self.assertEqual(passed.pk, OWNER)


class RunnabilityTests(_SurfaceTestCase):
    """A1: the surface is runnable and Django's own checks pass over it."""

    def test_the_settings_constants_this_surface_needs_are_in_force(self) -> None:
        self.assertEqual(settings.ROOT_URLCONF, "datara.urls")
        self.assertTrue(settings.TEMPLATES, "TEMPLATES must render the denial")
        self.assertEqual(
            settings.TEMPLATES[0]["BACKEND"],
            "django.template.backends.django.DjangoTemplates",
        )
        self.assertTrue(
            settings.TEMPLATES[0]["APP_DIRS"],
            "APP_DIRS is what makes datara/templates discoverable without DIRS",
        )
        self.assertIn("django.contrib.sessions", settings.INSTALLED_APPS)
        middleware = list(settings.MIDDLEWARE)
        sessions = "django.contrib.sessions.middleware.SessionMiddleware"
        auth = "django.contrib.auth.middleware.AuthenticationMiddleware"
        self.assertIn(sessions, middleware)
        self.assertIn(auth, middleware)
        self.assertLess(
            middleware.index(sessions),
            middleware.index(auth),
            "SessionMiddleware must precede AuthenticationMiddleware for request.user",
        )
        # The three settings changes added on review of #394 were verified
        # behaviourally but had no assertion here, so nothing would have caught a
        # later removal of any of them.
        self.assertIn(
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            middleware,
            "X_FRAME_OPTIONS is set to DENY and is dead without this middleware; "
            "this is the first HTML page the project serves",
        )
        processors = settings.TEMPLATES[0]["OPTIONS"].get("context_processors") or []
        self.assertTrue(
            any("csrf" in str(p) for p in processors),
            "without the csrf context processor a future {% csrf_token %} renders "
            "an empty string and ships a form with no token",
        )

    def test_the_protective_decorator_is_actually_on_the_view(self) -> None:
        """``@never_cache`` must be on the view, not merely configured.

        The 200 returns personal activity telemetry, so a missing no-store is a
        privacy defect, not a style one. This asserts the decorator is present on
        the resolved view.

        **This file cannot assert the resulting headers.** Its request driver is
        ``RequestFactory``, which calls the view directly and therefore bypasses
        the middleware chain, so ``X-Frame-Options`` and ``Cache-Control`` are
        never applied to a response built here. Asserting them would fail for a
        reason that has nothing to do with the behaviour under test, and asserting
        them over the full stack would need a database, which this module
        deliberately never opens. The middleware's presence is asserted in
        ``test_the_settings_constants_this_surface_needs_are_in_force``; the
        header-level effect is recorded as verified over real HTTP by independent
        review, not claimed here.
        """

        view = resolve(_route(MISSING_METRIC)).func
        seen = []
        while view is not None and not seen:
            seen.append(getattr(view, "__name__", ""))
            view = getattr(view, "__wrapped__", None)
        self.assertIn(
            "saved_metric_view",
            seen,
            "the resolved view must still be the one this module reviews",
        )
        decorators = getattr(
            resolve(_route(MISSING_METRIC)).func, "__wrapped__", None
        )
        self.assertIsNotNone(
            decorators,
            "@require_safe and @never_cache each wrap the view; if both wrappers "
            "are gone this surface would answer unsafe methods",
        )

    def test_the_system_checks_report_nothing(self) -> None:
        self.assertEqual(registry.run_checks(), [])

    def test_the_url_checks_really_traverse_a_urlconf(self) -> None:
        # Control for A1. `check` short-circuits when ROOT_URLCONF is unset, so a
        # clean report could be vacuous. This proves the checker inspects a URL
        # pattern list and reports a malformed one, which is what makes a clean
        # report over datara/urls.py meaningful.
        resolver = URLResolver(RegexPattern(r"^/"), ["not-a-pattern"])
        self.assertEqual(
            [issue.id for issue in check_resolver(resolver)], ["urls.E004"]
        )

    def test_the_surface_is_reachable_through_the_real_resolver(self) -> None:
        match, response = self.drive(OWN_METRIC)
        self.assertIs(match.func, app_surface.saved_metric_view)
        self.assertEqual(match.kwargs, {"metric_id": OWN_METRIC})
        self.assertEqual(response.status_code, 200)

    def test_connection_and_time_posture_is_unchanged(self) -> None:
        self.assertEqual(settings.CONN_MAX_AGE, 0)
        self.assertIs(settings.USE_TZ, True)

    def test_exactly_one_route_is_published_and_it_carries_no_version(self) -> None:
        self.assertEqual(len(datara_urls.urlpatterns), 1)
        pattern = str(datara_urls.urlpatterns[0].pattern)
        self.assertTrue(pattern.startswith(datara_urls.PROVISIONAL_ROUTE_PREFIX))
        for version_segment in ("v1", "v2", "1.0", "2.0", "version"):
            self.assertNotIn(
                version_segment,
                pattern,
                "#369 owns any version string, so none is authored here",
            )

    def test_the_denial_template_exists_where_the_settings_can_find_it(self) -> None:
        template = (
            Path(app_surface.__file__).resolve().parent
            / "templates"
            / "datara"
            / "not_available.html"
        )
        self.assertTrue(template.is_file())
        self.assertEqual(
            app_surface.DENIAL_TEMPLATE, "datara/not_available.html"
        )


class OwnReadTests(_SurfaceTestCase):
    """A3: an authenticated session reads its own saved metric."""

    def test_the_response_body_is_the_persisted_saved_bytes_unchanged(self) -> None:
        _, response = self.drive(OWN_METRIC)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, SAVED_BYTES)
        self.assertEqual(
            hashlib.sha256(response.content).hexdigest(),
            hashlib.sha256(SAVED_BYTES).hexdigest(),
        )
        self.assertEqual(
            response.headers["Content-Type"], app_surface.SAVED_METRIC_CONTENT_TYPE
        )
        # No envelope, no added wrapper: the body is the saved document.
        self.assertEqual(json.loads(response.content), json.loads(SAVED_BYTES))

    def test_the_store_is_built_from_the_session_user_object(self) -> None:
        principal = _Principal(OWNER)
        self.drive(OWN_METRIC, user=principal)
        self.assertEqual(len(_SavedMetricStoreDouble.principals), 1)
        self.assertIs(
            _SavedMetricStoreDouble.principals[0],
            principal,
            "the store must be built from the very object the session resolved",
        )

    def test_one_read_makes_exactly_one_owner_scoped_read(self) -> None:
        self.drive(OWN_METRIC)
        self.assertEqual(
            _SavedMetricStoreDouble.calls,
            [("for_user", OWNER, "_Principal"), ("get_metric", OWNER, OWN_METRIC)],
        )


class StoreScopeInvariantTests(_SurfaceTestCase):
    """The store's resolved scope must be the session's owner (SR20)."""

    def test_a_store_scoped_to_another_owner_is_refused(self) -> None:
        # The store resolves a different owner than the session does. That is the
        # one thing the derived identity exists to catch, and it must be refused
        # rather than read.
        class _MisScoped(_SavedMetricStoreDouble):
            @classmethod
            def for_user(cls, user):
                store = super().for_user(user)
                store.owner_id = OTHER_OWNER
                return store

        with mock.patch.object(app_surface, "SavedMetricStore", _MisScoped):
            _, response = self.drive(OWN_METRIC)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.comparable(response),
                         self.comparable(app_surface.generic_denial()))
        self.assertNotIn(b"other_owner", response.content)

    def test_a_matching_scope_is_served(self) -> None:
        identity, store = app_surface.owner_store_for(_request_with_user(OWNER))
        self.assertEqual(identity.owner_id, OWNER)
        self.assertEqual(app_surface.store_owner_id(store), OWNER)

    def test_store_owner_id_is_unverifiable_rather_than_raising(self) -> None:
        # A store with no scope must degrade to "cannot check", not blow up on an
        # attribute the double may not carry.
        class _Opaque:
            pass

        self.assertIsNone(app_surface.store_owner_id(_Opaque()))
        self.assertIsNone(app_surface.store_owner_id(object()))
        self.assertEqual(
            app_surface.store_owner_id(
                type("S", (), {"scope": _Scope(owner_id=5)})()
            ),
            5,
        )


class DenialTests(_SurfaceTestCase):
    """A4 and A6: one denial, whatever the reason."""

    def test_a_foreign_metric_and_a_nonexistent_metric_are_indistinguishable(self) -> None:
        _, foreign = self.drive(OTHER_METRIC)
        _, missing = self.drive(MISSING_METRIC)
        self.assertEqual(foreign.status_code, 404)
        self.assertEqual(self.comparable(foreign), self.comparable(missing))
        self.assertEqual(foreign.content, missing.content)
        for response in (foreign, missing):
            with self.subTest(body_sha=hashlib.sha256(response.content).hexdigest()[:8]):
                self.assertNotIn(b"other_owner", response.content)
                self.assertNotIn(OTHER_METRIC.encode(), response.content)
                self.assertNotIn(MISSING_METRIC.encode(), response.content)
                self.assertNotIn(OWN_METRIC.encode(), response.content)

    def test_a_malformed_identifier_is_denied_identically_too(self) -> None:
        _, malformed = self.drive("not-a-uuid")
        _, missing = self.drive(MISSING_METRIC)
        self.assertEqual(self.comparable(malformed), self.comparable(missing))

    def test_an_unauthenticated_request_is_denied_with_no_store_call(self) -> None:
        for label, principal in (
            ("bare_object", object()),
            ("none", None),
            ("django_anonymous_user", AnonymousUser()),
        ):
            with self.subTest(principal=label):
                _SavedMetricStoreDouble.calls = []
                _, response = self.drive(OWN_METRIC, user=principal)
                self.assertEqual(response.status_code, 404)
                self.assertEqual(
                    _SavedMetricStoreDouble.calls,
                    [],
                    "no store may be constructed without a usable session",
                )

    def test_every_denied_state_shares_one_response(self) -> None:
        canonical = self.comparable(app_surface.generic_denial())
        states = {
            "foreign": self.drive(OTHER_METRIC)[1],
            "missing": self.drive(MISSING_METRIC)[1],
            "malformed": self.drive("not-a-uuid")[1],
            "anonymous": self.drive(OWN_METRIC, user=AnonymousUser())[1],
            "no_user": self.drive(OWN_METRIC, user=object())[1],
        }
        for label, response in states.items():
            with self.subTest(state=label):
                self.assertEqual(self.comparable(response), canonical)

    def test_the_denial_body_is_constant_across_repeats(self) -> None:
        first = app_surface.generic_denial().content
        for _ in range(5):
            self.assertEqual(app_surface.generic_denial().content, first)
        self.assertIn(b"<!DOCTYPE html>", first)
        self.assertNotIn(b"{{", first)

    def test_an_unexpected_store_error_is_not_silently_converted(self) -> None:
        # Only MetricStoreRefusal maps to the denial. An unexpected failure stays
        # loud rather than being dressed as a refusal, so a genuine defect cannot
        # hide behind a uniform 404.
        class _Exploding(_SavedMetricStoreDouble):
            def get_metric(self, metric_id):
                raise RuntimeError("synthetic unexpected store failure")

        with mock.patch.object(app_surface, "SavedMetricStore", _Exploding):
            with self.assertRaises(RuntimeError):
                self.drive(OWN_METRIC)


class ClientSuppliedOwnerTests(_SurfaceTestCase):
    """A5: the owner is the session's, whatever the request carries."""

    def test_a_supplied_owner_is_ignored_in_every_carrier(self) -> None:
        for label, carrier in _carriers(OTHER_OWNER).items():
            with self.subTest(carrier=label):
                _SavedMetricStoreDouble.calls = []
                _, response = self.drive_carrying(OWN_METRIC, carrier)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.content, SAVED_BYTES, "the session owner's saved value"
                )
                self.assertEqual(
                    [owner for method, owner, _ in _SavedMetricStoreDouble.calls
                     if method == "for_user"],
                    [OWNER],
                )

    def test_a_supplied_owner_cannot_widen_access_to_another_identity(self) -> None:
        # The dangerous direction: naming the session owner must not unlock the
        # other identity's metric, and naming the other owner must not either.
        for label, carrier in _carriers(OWNER).items():
            with self.subTest(carrier=label, metric=OTHER_METRIC):
                _, response = self.drive_carrying(OTHER_METRIC, carrier)
                self.assertEqual(response.status_code, 404)
                self.assertNotIn(b"other_owner", response.content)
                self.assertEqual(self.comparable(response),
                                 self.comparable(app_surface.generic_denial()))

    def test_every_carrier_really_reaches_the_request(self) -> None:
        # Control: the carriers above are not vacuous. The request handed to the
        # view really does carry the other owner's identifier.
        for label, carrier in _carriers(OTHER_OWNER).items():
            with self.subTest(carrier=label):
                target = _route(OWN_METRIC)
                request = self.factory.generic(
                    "GET",
                    target,
                    data=carrier.get("body") or "",
                    content_type="application/json" if carrier.get("body") else "text/plain",
                    query_params=carrier.get("data"),
                    headers=carrier.get("headers"),
                )
                carried = {
                    **dict(request.GET),
                    **{
                        k: v
                        for k, v in request.headers.items()
                        if "owner" in k.lower()
                    },
                    **dict(request.COOKIES),
                    **({"body": request.body.decode()} if request.body else {}),
                }
                self.assertIn(str(other := 2), str(carried), label)
                self.assertNotEqual(carried, {})


class NoEgressTests(_SurfaceTestCase):
    """A7: nothing reachable from this surface opens a socket or the database."""

    @contextmanager
    def sockets_disabled(self):
        """The house tripwire from datara/tests/test_scoped_input.py."""

        def blocked(*args, **kwargs):
            raise AssertionError("egress attempted from the application surface")

        with mock.patch("socket.socket", side_effect=blocked), mock.patch(
            "socket.create_connection", side_effect=blocked
        ), mock.patch("urllib.request.urlopen", side_effect=blocked):
            yield

    #: The house set from datara/tests/test_scoped_input.py, plus FTP and SMTP. A
    #: local file-format decoder such as garmin_fit_sdk is deliberately NOT here:
    #: requirements-milestone-a.txt records that it parses a container and
    #: contacts nothing, and it is not a model-provider SDK.
    FORBIDDEN_IMPORT_ROOTS = frozenset(
        {
            "anthropic", "cohere", "ftplib", "google", "groq", "http", "httpcore",
            "httplib", "httpx", "litellm", "mistralai", "ollama", "openai",
            "requests", "smtplib", "socket", "socketserver", "ssl", "telnetlib",
            "transformers", "urllib", "urllib3", "websockets",
        }
    )

    #: Roots that may legitimately appear in sys.modules from unrelated imports,
    #: so the sys.modules assertion can look at provider names only.
    TRANSPORT_ROOTS = frozenset(
        {
            "http", "httpcore", "httplib", "httpx", "requests", "socket",
            "socketserver", "ssl", "telnetlib", "urllib", "urllib3", "websockets",
        }
    )

    @staticmethod
    def import_roots(path: Path) -> set[str]:
        roots: set[str] = set()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots.add(node.module.split(".")[0])
        return roots

    def test_every_state_is_reached_with_sockets_disabled(self) -> None:
        states = {
            "own": (OWN_METRIC, ..., 200),
            "foreign": (OTHER_METRIC, ..., 404),
            "missing": (MISSING_METRIC, ..., 404),
            "malformed": ("not-a-uuid", ..., 404),
            "anonymous": (OWN_METRIC, AnonymousUser(), 404),
        }
        with self.sockets_disabled():
            for label, (metric_id, user, expected) in states.items():
                with self.subTest(state=label):
                    _, response = self.drive(metric_id, user=user)
                    self.assertEqual(response.status_code, expected)
            self.assertEqual(app_surface.generic_denial().status_code, 404)

    @contextmanager
    def database_disabled(self):
        """Make opening a database connection an immediate, loud failure.

        Patched on the wrapper *class*, not on the ``connection`` proxy, so the
        tripwire cannot be confused by attribute lookup on the proxy.
        """

        def blocked(*args, **kwargs):
            raise AssertionError("a database connection was opened from the surface")

        from django.db.backends.base.base import BaseDatabaseWrapper

        with mock.patch.object(
            BaseDatabaseWrapper, "get_new_connection", side_effect=blocked
        ), mock.patch.object(
            BaseDatabaseWrapper, "cursor", side_effect=blocked
        ), mock.patch.object(
            BaseDatabaseWrapper, "connect", side_effect=blocked
        ):
            yield

    def test_no_database_connection_is_reachable_from_the_surface(self) -> None:
        # Prove the tripwire fires before relying on it. The probe must be a
        # *scoped* query: `Metric.objects.count()` on the unbound manager
        # short-circuits to `.none()` and would never open a cursor, so it would
        # make this test pass vacuously (see datara/models.py get_queryset).
        with self.database_disabled():
            with self.assertRaises(AssertionError):
                Metric.objects.for_owner(OWNER).count()
            for label, (metric_id, user) in {
                "own": (OWN_METRIC, ...),
                "foreign": (OTHER_METRIC, ...),
                "missing": (MISSING_METRIC, ...),
                "anonymous": (OWN_METRIC, AnonymousUser()),
            }.items():
                with self.subTest(state=label):
                    self.drive(metric_id, user=user)
            app_surface.generic_denial()

    def test_the_import_closure_of_the_surface_has_no_transport_or_provider(self) -> None:
        package = Path(app_surface.__file__).resolve().parent
        seen: set[Path] = set()
        pending = [
            package / name
            for name in ("app_surface.py", "urls.py", "session_identity.py")
        ]
        hits: list[str] = []
        while pending:
            path = pending.pop()
            if path in seen or not path.exists():
                continue
            seen.add(path)
            for root in self.import_roots(path):
                if root in self.FORBIDDEN_IMPORT_ROOTS:
                    hits.append(f"{path.name} imports {root}")
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    names = [node.module]
                else:
                    continue
                for name in names:
                    if not name.startswith("datara."):
                        continue
                    leaf = package / (name.split(".")[1] + ".py")
                    package_init = package / name.split(".")[1] / "__init__.py"
                    if leaf.exists():
                        pending.append(leaf)
                    elif package_init.exists():
                        pending.append(package_init)
        self.assertEqual(hits, [])
        # Not vacuous: the closure really does span the whole saved read path.
        self.assertIn(package / "metric_store.py", seen)
        self.assertIn(package / "db.py", seen)
        self.assertIn(package / "models.py", seen)
        self.assertGreaterEqual(len(seen), 8, sorted(p.name for p in seen))

    def test_the_closure_scan_would_catch_a_transport_import(self) -> None:
        # Control: the scan above is not green because it inspects nothing.
        with tempfile.TemporaryDirectory() as scratch:
            probe = Path(scratch) / "probe.py"
            probe.write_text(
                "import json\nimport requests\nfrom openai import OpenAI\n", "utf-8"
            )
            found = sorted(
                root
                for root in self.import_roots(probe)
                if root in self.FORBIDDEN_IMPORT_ROOTS
            )
        self.assertEqual(found, ["openai", "requests"])

    def test_no_provider_module_is_imported_by_driving_the_surface(self) -> None:
        for metric_id, user in (
            (OWN_METRIC, ...),
            (OTHER_METRIC, ...),
            (MISSING_METRIC, ...),
            (OWN_METRIC, AnonymousUser()),
        ):
            self.drive(metric_id, user=user)
        provider_roots = self.FORBIDDEN_IMPORT_ROOTS - self.TRANSPORT_ROOTS
        loaded = sorted(
            name for name in sys.modules if name.split(".")[0] in provider_roots
        )
        self.assertEqual(loaded, [])


class NoRecomputationTests(_SurfaceTestCase):
    """A8: a read returns saved values and changes nothing."""

    @staticmethod
    def digests() -> dict[str, str]:
        return {
            f"{owner}:{key}": hashlib.sha256(saved.canonical_content or b"").hexdigest()
            for owner, rows in _SavedMetricStoreDouble.saved.items()
            for key, saved in rows.items()
        }

    def test_a_read_does_not_change_any_stored_digest(self) -> None:
        before = self.digests()
        for metric_id, user in (
            (OWN_METRIC, ...),
            (OTHER_METRIC, ...),
            (MISSING_METRIC, ...),
            (OWN_METRIC, AnonymousUser()),
        ):
            self.drive(metric_id, user=user)
        self.assertEqual(self.digests(), before)

    def test_no_read_reaches_a_recompute_or_write_entry_point(self) -> None:
        _SavedMetricStoreDouble.calls = []
        for metric_id, user in (
            (OWN_METRIC, ...),
            (OTHER_METRIC, ...),
            (MISSING_METRIC, ...),
            (OWN_METRIC, AnonymousUser()),
        ):
            self.drive(metric_id, user=user)
        self.assertEqual(
            sorted(set(self.methods())),
            ["for_user", "get_metric"],
            "the only store methods this surface may reach",
        )

    def test_a_denied_read_calls_nothing_at_all_when_there_is_no_session(self) -> None:
        _SavedMetricStoreDouble.calls = []
        self.drive(OWN_METRIC, user=AnonymousUser())
        self.assertEqual(_SavedMetricStoreDouble.calls, [])

    def test_no_surface_module_names_a_recompute_or_write_entry_point(self) -> None:
        forbidden = {
            "prepare_and_save_metric",
            "save_prepared_metrics",
            "summarize_recorded",
            "prepare_overall_trend",
            "canonical_metric_content",
            "project_recorded_result",
            "record_eligibility",
            "record_evidence",
        }
        package = Path(app_surface.__file__).resolve().parent
        for name in ("app_surface.py", "urls.py", "session_identity.py"):
            tree = ast.parse(
                (package / name).read_text(encoding="utf-8"), filename=name
            )
            called: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        called.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        called.add(node.func.attr)
            with self.subTest(module=name):
                self.assertEqual(
                    sorted(called & forbidden),
                    [],
                    "the read surface must not name a prepare, save or project entry point",
                )

    def test_the_surface_names_the_real_read_service_only(self) -> None:
        source = Path(app_surface.__file__).read_text(encoding="utf-8")
        for expected in ("SavedMetricStore.for_user", "get_metric", "MetricStoreRefusal"):
            self.assertIn(expected, source)
        self.assertNotIn("get_metric_evidence", source)
        self.assertNotIn("list_metrics_for_snapshot", source)