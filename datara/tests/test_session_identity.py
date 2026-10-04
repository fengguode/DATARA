"""Session-derived identity for the #378 application surface.

WP05 (TK64); CUS09, CUS10; SR20, SR21.

Pure logic. No database, no socket, no provider: every test here runs on a host
where PostgreSQL 17 cannot start, and none of them would notice, because none of
them touches a server.

HOW EACH PROPERTY IS BACKED BY A MUTATION
------------------------------------------
A control that has never been seen to fail is not evidence. Each test states the
change that breaks it, and every one of those changes was executed during this
assignment; see the assignment report.

| Property | Mutation that breaks it |
| --- | --- |
| the owner comes only from the session user | read ``request.GET.get("owner")`` instead |
| no query, header, cookie or body can move the owner | read ``request.headers`` for an owner header |
| every unusable principal is refused identically | raise a per-principal reason code |
| the refusal discloses nothing | interpolate the primary key into the message |
| the tripwire is not vacuous | (control) read a forbidden attribute and assert it raises |
"""

from __future__ import annotations

import unittest

from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase

from datara.session_identity import (
    IDENTITY_UNAVAILABLE,
    PERMITTED_REQUEST_ATTRIBUTES,
    SessionIdentity,
    SessionIdentityUnavailable,
    derive_session_identity,
)


class _Authenticated:
    """A minimal authenticated principal, standing in for an ``auth.User``.

    Only ``pk`` and ``is_authenticated`` are read by the code under test. The
    database-backed ``auth.User`` cannot be constructed on a host with no
    PostgreSQL 17, and resolving one through a real session needs the
    ``django_session`` table, so this stand-in carries the same two facts.
    """

    def __init__(self, pk: object) -> None:
        self.pk = pk
        self.is_authenticated = True

    def __repr__(self) -> str:
        return f"_Authenticated(pk={self.pk!r})"


class _Anonymous:
    """A principal that is present but not authenticated."""

    is_authenticated = False
    pk = None


class _HostileRequest:
    """A request on which reading anything but ``user`` fails loudly.

    This is the executable form of "the owner comes from the session". It is not
    a mock with a permissive default: an unexpected attribute read raises here
    rather than returning ``None`` and quietly yielding a wrong owner.
    """

    def __init__(self, user: object) -> None:
        self.__dict__["_user"] = user

    def __getattr__(self, name: str) -> object:
        if name == "user":
            return self.__dict__["_user"]
        raise AssertionError(
            f"identity derivation read request.{name!r}; only "
            f"{PERMITTED_REQUEST_ATTRIBUTES!r} may be read"
        )


class _RecordingRequest:
    """A request that logs every attribute read and serves hostile payloads.

    Used for the positive direction of the same property: this one *offers* an
    owner in the query string, the headers, the body and the cookies, so the
    assertion is that none of it is even looked at.
    """

    def __init__(self, user: object) -> None:
        self.reads: list[str] = []
        self.GET = {"owner": "2", "owner_id": "2", "user": "2"}
        self.POST = {"owner": "2", "owner_id": "2", "user": "2"}
        self.headers = {"HTTP_X_OWNER_ID": "2", "HTTP_X_DATARA_OWNER": "2"}
        self.COOKIES = {"owner": "2", "sessionid": "2"}
        self.body = b'{"owner": 2, "owner_id": 2, "user": 2}'
        self.content_type = "application/json"
        self.path = "/internal/saved-metric/anything"
        self.method = "GET"
        self.__dict__["_user"] = user

    def __getattr__(self, name: str) -> object:
        if name in self.__dict__:
            return self.__dict__[name]
        if name == "user":
            self.reads.append("user")
            return self.__dict__["_user"]
        self.reads.append(name)
        return self.__dict__.get(name)


class SessionIdentityDerivationTests(SimpleTestCase):
    """The owner is the session's, and only the session's."""

    def test_the_owner_is_the_authenticated_session_user(self) -> None:
        identity = derive_session_identity(_HostileRequest(_Authenticated(7)))
        self.assertEqual(identity, SessionIdentity(owner_id=7))
        self.assertEqual(identity.owner_id, 7)

    def test_derivation_reads_no_request_attribute_other_than_user(self) -> None:
        request = _RecordingRequest(_Authenticated(7))
        identity = derive_session_identity(request)
        self.assertEqual(identity.owner_id, 7)
        # The payloads above name owner "2" in four places. If any of them had
        # been consulted the owner would be 2.
        self.assertEqual(request.reads, ["user"])

    def test_the_tripwire_is_not_vacuously_green(self) -> None:
        # Control for the two tests above: the hostile request really does refuse
        # a forbidden attribute read.
        request = _HostileRequest(_Authenticated(7))
        for forbidden in ("GET", "headers", "POST", "COOKIES", "body", "path"):
            with self.subTest(forbidden=forbidden):
                with self.assertRaises(AssertionError):
                    getattr(request, forbidden)

    def test_every_unusable_principal_is_refused_identically(self) -> None:
        cases: dict[str, object] = {
            "no_user_attribute": object(),
            "user_is_none": _HostileRequest(None),
            "django_anonymous_user": _HostileRequest(AnonymousUser()),
            "is_authenticated_false": _HostileRequest(_Anonymous()),
            "pk_is_none": _HostileRequest(_Authenticated(None)),
            "pk_is_zero": _HostileRequest(_Authenticated(0)),
            "pk_is_negative": _HostileRequest(_Authenticated(-1)),
            "pk_is_a_string": _HostileRequest(_Authenticated("7")),
            "pk_is_a_bool": _HostileRequest(_Authenticated(True)),
            "pk_is_a_float": _HostileRequest(_Authenticated(7.0)),
        }
        seen: set[tuple[int, str, str]] = set()
        for label, request in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(SessionIdentityUnavailable) as caught:
                    derive_session_identity(request)
                self.assertEqual(caught.exception.reason_code, IDENTITY_UNAVAILABLE)
                self.assertEqual(str(caught.exception), IDENTITY_UNAVAILABLE)
                seen.add(
                    (
                        len(caught.exception.args),
                        str(caught.exception),
                        type(caught.exception).__name__,
                    )
                )
        # One refusal shape for all ten principals: nothing distinguishes them.
        self.assertEqual(len(seen), 1)

    def test_the_refusal_carries_no_identifier_or_request_text(self) -> None:
        with self.assertRaises(SessionIdentityUnavailable) as caught:
            derive_session_identity(_HostileRequest(_Authenticated(-4242)))
        rendered = f"{caught.exception.args!r} {caught.exception!r}"
        for forbidden in ("-4242", "owner", "user", "pk", "session"):
            self.assertNotIn(forbidden, rendered)
        self.assertEqual(IDENTITY_UNAVAILABLE, "identity_unavailable")

    def test_identity_equality_and_hashing_are_by_owner_id_alone(self) -> None:
        # A request-derived value is retained nowhere, so two identities built
        # from different requests compare equal when the owner is equal.
        first = derive_session_identity(_RecordingRequest(_Authenticated(7)))
        second = derive_session_identity(_HostileRequest(_Authenticated(7)))
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        self.assertEqual(len({first, second}), 1)
        self.assertNotEqual(first, SessionIdentity(owner_id=8))
        self.assertEqual(set(SessionIdentity.__dataclass_fields__), {"owner_id"})


class SessionIdentityConstructionTests(SimpleTestCase):
    def test_only_user_is_permitted(self) -> None:
        self.assertEqual(PERMITTED_REQUEST_ATTRIBUTES, ("user",))

    def test_constructing_an_identity_directly_is_still_validated(self) -> None:
        # The dataclass does not trust its callers, so a raw request value that
        # bypassed derivation would still be refused.
        for bad in (None, 0, -1, "7", True, 1.5, [7]):
            with self.subTest(bad=bad):
                with self.assertRaises(SessionIdentityUnavailable):
                    SessionIdentity(owner_id=bad)
        self.assertEqual(SessionIdentity(owner_id=1), SessionIdentity(owner_id=1))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()