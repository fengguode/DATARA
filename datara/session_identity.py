"""Server-derived session identity for the identity-bound read surface.

WP05 (TK64); CUS09, CUS10; SR20, SR21.

The owner of a request is the owner of the *server-side session*. Django resolves
that session into ``request.user`` through
``django.contrib.auth.middleware.AuthenticationMiddleware``; this module is the
only place the application surface obtains an owner from, and it reads
``request.user`` and nothing else. A query parameter, a request header, a cookie,
a request body field and a URL capture are all structurally unable to supply or
override the owner, because this module never dereferences any of them.

Refusals are generic and constant. An anonymous caller, a caller with no session
and a caller whose request carries an identifier the session does not own all
fail the same way, with one reason code that names no identifier, so this module
cannot be used to learn whether any identifier exists (SR21).

This module opens no socket, imports no transport and reads no credential. It
makes no model or provider call (SR06): there is no provider authority in
Milestone A to call.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

#: The single, constant reason this module refuses. It is not parameterised by
#: the request, so it cannot become an existence oracle.
IDENTITY_UNAVAILABLE = "identity_unavailable"

#: The only attribute of a request object this module is permitted to read.
#: Named here so that the tripwire in ``datara/tests/test_session_identity.py``
#: can enforce it without duplicating the string.
PERMITTED_REQUEST_ATTRIBUTES: tuple[str, ...] = ("user",)


class SessionIdentityUnavailable(Exception):
    """No usable owner could be derived from the server-side session.

    The message is the constant reason code and carries no request-derived text,
    so it is safe to log and cannot disclose an identifier.
    """

    reason_code = IDENTITY_UNAVAILABLE

    def __init__(self) -> None:
        super().__init__(IDENTITY_UNAVAILABLE)


@dataclass(frozen=True)
class SessionIdentity:
    """One authenticated session's owner, and nothing else.

    Equality and hashing are by ``owner_id`` only. No request-derived value is
    retained, so two identities can never be compared in a way that leaks
    anything about the request that produced them.
    """

    owner_id: int

    def __post_init__(self) -> None:
        if type(self.owner_id) is not int:  # bool is an int subclass; refuse it
            raise SessionIdentityUnavailable()
        if self.owner_id <= 0:
            raise SessionIdentityUnavailable()


def derive_session_identity(request: Any) -> SessionIdentity:
    """Return the owner of ``request``'s authenticated session.

    Reads ``request.user`` and nothing else. Every refusal -- no request, no
    user attribute, an anonymous user, a user with no usable primary key -- is
    the same :class:`SessionIdentityUnavailable` with the same reason code, so a
    caller cannot distinguish "not signed in" from "this principal is unusable",
    and neither discloses whether an identifier exists.
    """

    try:
        user = request.user
    except AttributeError:
        raise SessionIdentityUnavailable() from None
    if user is None or not getattr(user, "is_authenticated", False):
        raise SessionIdentityUnavailable()
    try:
        owner_id = user.pk
    except AttributeError:
        raise SessionIdentityUnavailable() from None
    return SessionIdentity(owner_id=owner_id)


__all__ = [
    "IDENTITY_UNAVAILABLE",
    "PERMITTED_REQUEST_ATTRIBUTES",
    "SessionIdentity",
    "SessionIdentityUnavailable",
    "derive_session_identity",
]