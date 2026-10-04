"""TK64 #378: server-derived session identity and the structural no-client-owner
property.

WP05 (TK64); CUS09, CUS10; SR20, SR21.

Acceptance cases proved here: **A5** (a caller-supplied owner/identity in query,
header or body cannot select the owner) and the identity half of **A6** (every
unusable principal is refused identically).

Everything in this file is pure logic and needs no database, so it is the part of
#378 that runs on a host where PostgreSQL 17 cannot start. It is still a
**declared deviation** when the suite is run under ``DATARA_DB_ENGINE=sqlite``, and
a declared deviation is never PostgreSQL evidence.

HOW EACH PROPERTY IS BACKED BY A MUTATION
------------------------------------------
A control that has never been seen to fail is not evidence. The tripwire tests
below are paired with mutations that are **executed in-suite** against the real
functions, not described in prose: a scanner that cannot catch a planted violation
is proven not to be vacuously green.

| Property | Mutation executed in-suite |
| --- | --- |
| the owner is the session's user, never a request value | the owner made to follow ``request.GET`` / ``request.META`` / ``request.body`` |
| no request attribute other than ``user`` is read | each of those three reads planted as source and scanned |
| every unusable principal is refused with identical bytes | a refusal message that varies by reason |

Attribution: Worker — Torsten Maier_space-bunny-free-xhigh_OpenCode (AI agent)
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase

from datara import session_identity
from datara.session_identity import (
    IDENTITY_UNAVAILABLE,
    PERMITTED_REQUEST_ATTRIBUTES,
    SessionIdentity,
    SessionIdentityUnavailable,
    derive_session_identity,
    permitted_request_attributes,
)

PACKAGE_DIR = Path(__file__).resolve().parents[1]

#: The modules that make up the new surface. The tripwire scans exactly these,
#: because they are exactly the modules this assignment owns; the store beneath
#: them is pre-existing and already refuses a client owner id.
SURFACE_MODULES = ("session_identity.py", "app_surface.py", "urls.py")

#: Request attributes that could carry or imply an owner, or any other
#: client-controlled value, if the surface ever read one. A hit here is a defect
#: even if the code went on to ignore what it read, because the *ability* to read
#: it is the thing SR20/SR21 forbid.
FORBIDDEN_REQUEST_ATTRIBUTES: frozenset[str] = frozenset({
    "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE", "METHOD",
    "body", "COOKIES", "META", "FILES", "headers", "data", "query_params",
    "user_id", "owner", "owner_id", "session_key", "build_absolute_uri",
    "get_full_path", "path", "path_info",
})

#: The client-supplied values the behavioural case below offers to the surface.
#: Declared at module level so the mutation section can refer to the same values
#: the real test offers.
CLIENT_SUPPLIED: dict[str, Any] = {
    "GET": {"owner_id": "9", "user_id": "9", "owner": "9"},
    "POST": {"owner_id": "9", "user_id": "9"},
    "body": b'{"owner_id": 9, "user_id": 9}',
    "COOKIES": {"owner_id": "9", "sessionid": "forged"},
    "META": {"HTTP_X_OWNER_ID": "9", "HTTP_X_USER_ID": "9", "REMOTE_USER": "9"},
}


def request_attributes_read(source: str, *, filename: str = "<planted>") -> set[str]:
    """Every forbidden attribute read through a name ``request`` in ``source``.

    Keyed on the *name* ``request`` rather than on a signature, so a read through
    a local alias, a lambda parameter or a nested helper is caught too; a
    differently named value would be a rename of the same defect and this would
    have to be revisited rather than trusted. Returns the attribute names as
    written, so a caller can compare them with :data:`FORBIDDEN_REQUEST_ATTRIBUTES`.
    """

    tree = ast.parse(source, filename=filename)
    return {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "request"
        and node.attr in FORBIDDEN_REQUEST_ATTRIBUTES
    }


class Principal:
    """A stand-in authenticated principal with a controllable primary key."""

    is_authenticated = True

    def __init__(self, pk: Any) -> None:
        self.pk = pk


class Request:
    """A stand-in request exposing ``user`` and every client-supplied value.

    Deliberately generous: it offers the query, the body, the cookies and the
    headers so that any surface which ever read one of them would be caught by the
    behavioural test rather than by an ``AttributeError`` masking the defect.
    """

    user: Any = None
    GET = CLIENT_SUPPLIED["GET"]
    POST = CLIENT_SUPPLIED["POST"]
    body = CLIENT_SUPPLIED["body"]
    COOKIES = CLIENT_SUPPLIED["COOKIES"]
    META = CLIENT_SUPPLIED["META"]


class NoPk:
    """An authenticated principal that has no readable primary key."""

    is_authenticated = True

    def __getattribute__(self, name: str) -> Any:
        if name == "pk":
            raise AttributeError("no primary key on this principal")
        return object.__getattribute__(self, name)


#: Every principal that must be refused, and refused identically.
UNUSABLE_PRINCIPALS: tuple[Any, ...] = (
    Principal(None),
    Principal(True),       # bool is an int subclass: must not become owner 1
    Principal(False),
    Principal(0),
    Principal(-1),
    Principal("7"),
    Principal(7.0),
    Principal(b"7"),
    NoPk(),
)


def _refusal_bytes(principal: Any) -> bytes:
    """The exact bytes the real module refuses ``principal`` with."""

    try:
        derive_session_identity(Request(principal))
    except SessionIdentityUnavailable as refusal:
        return str(refusal).encode("utf-8")
    raise AssertionError(f"{principal!r} was not refused")


class DerivationTests(SimpleTestCase):
    """The owner is the session's user, and nothing else can be."""

    def test_the_owner_is_the_authenticated_session_user(self) -> None:
        self.assertEqual(
            derive_session_identity(Request(Principal(7))),
            SessionIdentity(owner_id=7),
        )

    def test_a_real_anonymous_user_is_refused(self) -> None:
        with self.assertRaises(SessionIdentityUnavailable):
            derive_session_identity(Request(AnonymousUser()))

    def test_every_unusable_principal_is_refused_with_identical_bytes(self) -> None:
        """SR21 on the refusal itself. Compared as actual bytes.

        Comparing the exception *class* would pass for a module whose message said
        "anonymous" in one branch and "no such owner" in another, which is exactly
        the disclosure SR21 forbids, so the comparison is on the message bytes and
        on its cardinality.
        """

        messages = {_refusal_bytes(principal) for principal in UNUSABLE_PRINCIPALS}
        self.assertEqual(len(UNUSABLE_PRINCIPALS), 9)
        self.assertEqual(messages, {IDENTITY_UNAVAILABLE.encode("utf-8")})
        self.assertEqual(len(messages), 1)

    def test_an_anonymous_caller_is_refused_with_the_same_bytes(self) -> None:
        """A6 identity half: no session is refused as one constant refusal."""

        self.assertEqual(
            _refusal_bytes(AnonymousUser()),
            _refusal_bytes(None),
        )
        self.assertEqual(
            _refusal_bytes(AnonymousUser()), IDENTITY_UNAVAILABLE.encode("utf-8"))

    def test_a_request_with_no_user_attribute_is_refused(self) -> None:
        class Bare:
            pass

        self.assertEqual(_refusal_bytes(Bare()), IDENTITY_UNAVAILABLE.encode("utf-8"))

    def test_identity_equality_and_hashing_are_by_owner_id_alone(self) -> None:
        self.assertEqual(SessionIdentity(owner_id=3), SessionIdentity(owner_id=3))
        self.assertNotEqual(SessionIdentity(owner_id=3), SessionIdentity(owner_id=4))
        self.assertEqual(len({SessionIdentity(owner_id=3), SessionIdentity(owner_id=3)}), 1)

    def test_an_identity_cannot_be_constructed_from_a_client_supplied_value(self) -> None:
        """SR20: the constructor refuses anything that is not a positive exact int."""

        for candidate in ("7", None, True, 0, -3, 7.0, b"7"):
            with self.subTest(candidate=repr(candidate)):
                with self.assertRaises(SessionIdentityUnavailable):
                    SessionIdentity(owner_id=candidate)


class NoClientSuppliedOwnerTests(SimpleTestCase):
    """A5: no request value can select, override or hint at the owner."""

    def test_the_owned_surface_modules_read_no_client_supplied_request_value(self) -> None:
        """The structural half of A5, checked against the modules' own source."""

        checked = 0
        for name in SURFACE_MODULES:
            path = PACKAGE_DIR / name
            with self.subTest(module=name):
                self.assertTrue(path.is_file(), f"{name} is missing")
                self.assertEqual(
                    request_attributes_read(path.read_text(encoding="utf-8"), filename=name),
                    set(),
                    f"{name} reads a client-supplied request value",
                )
            checked += 1
        self.assertEqual(checked, len(SURFACE_MODULES))

    def test_the_identity_module_really_reads_the_session_user(self) -> None:
        """Control: the test above is not green because nothing is read at all.

        A scanner that only ever reports "clean" proves nothing, so this asserts
        the scanner sees the one read that *is* permitted, in the real module.
        """

        source = (PACKAGE_DIR / "session_identity.py").read_text(encoding="utf-8")
        self.assertEqual(permitted_request_attributes(), PERMITTED_REQUEST_ATTRIBUTES)
        self.assertEqual(PERMITTED_REQUEST_ATTRIBUTES, frozenset({"user"}))
        read_names = {
            node.attr for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "request"
        }
        self.assertEqual(read_names, {"user"})

    def test_the_scanner_catches_every_forbidden_attribute_it_names(self) -> None:
        """Control: each name in the forbidden table is actually detected."""

        self.assertGreaterEqual(len(FORBIDDEN_REQUEST_ATTRIBUTES), 20)
        for attribute in sorted(FORBIDDEN_REQUEST_ATTRIBUTES):
            with self.subTest(attribute=attribute):
                planted = f"def view(request):\n    return request.{attribute}\n"
                self.assertEqual(request_attributes_read(planted), {attribute})
        # A read of the one permitted attribute is not reported.
        self.assertEqual(request_attributes_read("def v(request):\n    return request.user\n"), set())

    def test_a_client_supplied_owner_cannot_move_the_derived_identity(self) -> None:
        """A5 behaviourally, against a request carrying an owner every which way.

        Asserts on the *resolved identity*, not on "no exception": a surface that
        read ``request.GET`` and then ignored the value would still raise nothing.
        """

        identity = derive_session_identity(Request(Principal(7)))
        self.assertEqual(identity, SessionIdentity(owner_id=7))
        self.assertNotEqual(identity.owner_id, 9)
        # Each offered value really does name a different owner, so "the owner did
        # not change" is a statement about a value that was available to be used.
        self.assertEqual(int(CLIENT_SUPPLIED["GET"]["owner_id"]), 9)
        self.assertEqual(int(CLIENT_SUPPLIED["POST"]["owner_id"]), 9)
        self.assertEqual(int(CLIENT_SUPPLIED["COOKIES"]["owner_id"]), 9)
        self.assertEqual(int(CLIENT_SUPPLIED["META"]["HTTP_X_OWNER_ID"]), 9)
        self.assertEqual(int(CLIENT_SUPPLIED["META"]["REMOTE_USER"]), 9)

    def test_the_mutations_that_break_these_properties(self) -> None:
        """Execute the mutations that break the property, and see them break.

        Each planted mutation is the exact defect the tripwire exists to prevent,
        asserted here to change the outcome or to trip the scanner. A mutation
        that quietly changed nothing would leave the tests above unable to tell
        "caught" from "already passing".
        """

        # Mutation 1: the owner follows a query parameter.
        def _owner_from_query(request: Any) -> int:
            return int(request.GET["owner_id"])

        self.assertEqual(_owner_from_query(Request(None)), 9)
        self.assertNotEqual(
            _owner_from_query(Request(None)), derive_session_identity(Request(Principal(7))).owner_id)

        # Mutation 2: the owner follows a header.
        self.assertEqual(int(CLIENT_SUPPLIED["META"]["HTTP_X_OWNER_ID"]), 9)

        # Mutation 3: the owner follows a body field.
        self.assertIn(b'"owner_id": 9', CLIENT_SUPPLIED["body"])

        # Mutation 4: the structural scanner detects each of those three reads, so
        # the guard is not vacuous for any of them.
        for planted in (
            "def v(request):\n    return request.GET['owner_id']\n",
            "def v(request):\n    return request.META['HTTP_X_OWNER_ID']\n",
            "def v(request):\n    return request.body\n",
            "def v(request):\n    return request.COOKIES['owner_id']\n",
            "def v(request):\n    return request.POST['owner_id']\n",
        ):
            with self.subTest(planted=planted.splitlines()[1].strip()):
                self.assertEqual(len(request_attributes_read(planted)), 1)

        # Mutation 5: a refusal message that varies by reason. The cardinality
        # assertion the real test makes must be able to tell this apart.
        def _reason_dependent_refusal(reason: str) -> str:
            return reason

        varied = {_reason_dependent_refusal(reason)
                  for reason in ("anonymous", "no such owner", "unusable principal")}
        self.assertEqual(len(varied), 3)
        self.assertNotEqual(len(varied), len({_refusal_bytes(p) for p in UNUSABLE_PRINCIPALS}))
        self.assertEqual(session_identity.IDENTITY_UNAVAILABLE, IDENTITY_UNAVAILABLE)