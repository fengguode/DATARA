"""The canonical duration unit and logical tuple for DATARA Milestone A.

WHY THIS MODULE EXISTS
----------------------
The independent review of TK11/TK15/TK18 found one persisted column,
``Session.elapsed_duration_seconds``, written by two modules in two different
units: ``datara.db`` wrote integer *seconds* and ``datara.dedup`` wrote integer
*milliseconds*, and ``datara.dedup`` then compared that seconds column against a
millisecond candidate. A 30-minute run was stored as ``1800`` by one path and
``1800000`` by the other, the exact comparison reported them as different
activities, and the same activity was accepted a second time. The column type
``PositiveBigIntegerField`` cannot detect this: both values are valid positive
integers. ``datara.classification`` emitted a third representation of the same
quantity -- an exact decimal *string* -- and a logical tuple of three strings,
which cannot be compared with the integer tuple at all.

THE DECISION
------------
**Integer milliseconds is the canonical comparison unit.** Section 6 of
``docs/management/source-evidence/duplicate-conflict-options.md`` specifies it and
the Architect's P1-P7 precedence table is built on it (Primary Coordinator
decision, Milestone A review of TK11/TK15/TK18). This module is the single
definition that the classifier, the normalizer, the persistence layer and the
conflict state machine all use, so there is exactly one tuple and one unit.

HOW THE UNIT IS ENFORCED, AND WHY IT IS NOT INFERRED
----------------------------------------------------
A bare integer carries no unit, so no function can *detect* that ``1800`` means
seconds rather than milliseconds -- ``1800`` milliseconds is a legitimate 1.8
second duration. Guessing would be a fake control. The unit is therefore
**declared by the caller and checked**, never inferred:

* :func:`require_elapsed_duration_ms` takes the unit as a mandatory keyword and
  refuses any unit other than :data:`CANONICAL_DURATION_UNIT`. It also refuses a
  non-``int`` (``float``, ``str``, ``bool`` -- the representations that caused the
  defect) and refuses a value outside the plausible millisecond domain.
* :func:`elapsed_duration_ms_from_seconds` is the only sanctioned seconds -> ms
  conversion. TK18's normalization contract stays in integer seconds, because
  its canonical payload and digest are already published and SR05 forbids
  silently re-basing stored digests; the conversion is exact, is performed once,
  and is asserted at the persistence boundary.
* ``Session.elapsed_duration_ms`` carries a database ``CheckConstraint`` on the
  same domain, so a future writer that bypasses both helpers is still refused.

SCOPE
-----
Pure: no database, no Django, no filesystem, no network, no model call. The
classifier (``datara.classification``) is required to stay free of Django, and it
imports this module, so nothing here may import a framework.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

# ---------------------------------------------------------------------------
# The canonical unit
# ---------------------------------------------------------------------------

#: The one canonical comparison unit, named so it can be compared as a string in
#: a manifest, a report or an error message without parsing prose.
CANONICAL_DURATION_UNIT = "integer_milliseconds"

#: Exact, integer, total. Used only to make the seconds -> ms conversion
#: self-evident; no division is performed anywhere in this module.
MILLISECONDS_PER_SECOND = 1000

#: D01 requires a session's elapsed duration to be a positive whole number of
#: seconds, so the millisecond domain starts at one second. A value below this is
#: a unit error (a seconds count that was never converted), not a short session.
MIN_ELAPSED_DURATION_MS = 1000

#: The maximum accepted elapsed duration, matching the normalization policy
#: default of 24 hours expressed in milliseconds.
MAX_ELAPSED_DURATION_MS = 86_400_000

#: The unit name a caller must pass when it holds seconds. Named here so the two
#: sanctioned units are discoverable together and a typo is visible.
SECONDS_UNIT = "integer_seconds"


def require_elapsed_duration_ms(
    value: Any, *, origin: str, unit: str
) -> int:
    """Return ``value`` if it is an exact integer number of milliseconds.

    This is the guard every millisecond write site and every millisecond
    comparison calls. It refuses, loudly and with ``origin`` in the message:

    * a declared unit other than :data:`CANONICAL_DURATION_UNIT` -- this is what
      catches a seconds-shaped value labelled as seconds reaching a
      millisecond column, which is the exact defect this module exists to close;
    * a ``bool``, ``float`` or ``str`` -- ``bool`` is an ``int`` subclass and
      ``float``/``str`` are the two other representations that previously
      reached this quantity;
    * a value outside :data:`MIN_ELAPSED_DURATION_MS` ..
      :data:`MAX_ELAPSED_DURATION_MS`, which is where an unconverted seconds
      count or a stray identifier would land.

    ``origin`` is required so a failure names the write site rather than an
    anonymous helper.
    """

    if unit != CANONICAL_DURATION_UNIT:
        raise TypeError(
            f"{origin}: elapsed duration unit must be "
            f"{CANONICAL_DURATION_UNIT!r}, but this site declared {unit!r}. "
            "Integer milliseconds is the canonical comparison unit (duplicate-"
            "conflict-options section 6); convert with "
            "datara.canonical.elapsed_duration_ms_from_seconds rather than "
            "writing a seconds count into a millisecond field."
        )
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"{origin}: elapsed duration must be an exact integer number of "
            f"milliseconds, got {type(value).__name__} ({value!r}). A float or a "
            "decimal string is refused because it would make two different "
            "durations compare equal after rounding."
        )
    if value < MIN_ELAPSED_DURATION_MS:
        raise ValueError(
            f"{origin}: elapsed duration {value} ms is below the canonical "
            f"minimum of {MIN_ELAPSED_DURATION_MS} ms (one second). A positive "
            f"seconds count below {MIN_ELAPSED_DURATION_MS // MILLISECONDS_PER_SECOND} "
            "arriving here means it was not converted to milliseconds."
        )
    if value > MAX_ELAPSED_DURATION_MS:
        raise ValueError(
            f"{origin}: elapsed duration {value} ms exceeds the canonical "
            f"maximum of {MAX_ELAPSED_DURATION_MS} ms (24 hours), which is the "
            "normalization policy limit expressed in the canonical unit."
        )
    return value


def elapsed_duration_ms_from_seconds(value: Any, *, origin: str) -> int:
    """Convert an exact integer number of seconds to the canonical unit.

    TK18's normalization contract is defined in integer seconds and its canonical
    payload and digest are already published, so that contract is not renamed
    here (SR05 forbids silently re-basing a stored digest). This function is the
    single, exact, asserted crossing point between that contract and the
    millisecond persistence and comparison unit.
    """

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"{origin}: expected an exact integer number of seconds, got "
            f"{type(value).__name__} ({value!r})"
        )
    if value < 1:
        raise ValueError(
            f"{origin}: elapsed duration must be a positive whole number of "
            f"seconds, got {value}"
        )
    return require_elapsed_duration_ms(
        value * MILLISECONDS_PER_SECOND,
        origin=f"{origin} (seconds -> ms)",
        unit=CANONICAL_DURATION_UNIT,
    )


# ---------------------------------------------------------------------------
# The approved normalised sport enum (section 6)
# ---------------------------------------------------------------------------

#: Section 6 fixes the canonical comparison value as the *integer*; the string
#: form is the display name of the same approved pair and is what
#: ``Session.sport`` stores. A closed two-value vocabulary taken verbatim from
#: section 6, not an invented mapping.
SPORT_CODES: Mapping[int, str] = {1: "running", 2: "cycling"}


def canonical_sport_code(value: Any, *, origin: str) -> int:
    """Return the canonical integer sport code for a normalised value.

    An unrecognised value is refused rather than coerced, because coercing it
    would invent a sport and therefore invent a tuple.
    """

    if isinstance(value, bool):
        raise ValueError(f"{origin}: sport must be a sport code, not a bool")
    if isinstance(value, int):
        if value not in SPORT_CODES:
            raise ValueError(
                f"{origin}: sport code {value!r} is outside the approved set "
                f"{sorted(SPORT_CODES)}"
            )
        return value
    if isinstance(value, str):
        folded = value.strip().lower()
        for code, name in SPORT_CODES.items():
            if folded == name:
                return code
        raise ValueError(
            f"{origin}: sport {value!r} is not in the approved normalised set "
            f"{sorted(SPORT_CODES)}"
        )
    raise ValueError(f"{origin}: cannot canonicalise sport of type {type(value).__name__}")


def sport_name(code: Any, *, origin: str = "sport") -> str:
    """The display name of a canonical integer sport code."""

    return SPORT_CODES[canonical_sport_code(code, origin=origin)]


# ---------------------------------------------------------------------------
# The logical tuple -- defined once, here
# ---------------------------------------------------------------------------

#: The exact components of the logical tuple, in canonical order. The owner is
#: the scoping component; ``sub_sport`` is deliberately NOT a component, so a
#: re-export that changed only the sub-sport classification still conflicts.
IDENTITY_COMPONENTS: tuple[str, ...] = (
    "sport_code",
    "start_epoch_seconds",
    "elapsed_duration_ms",
)

#: The full conflict key, in canonical order. ``datara.dedup`` asserts this
#: against the live dataclass so the key cannot be widened.
TUPLE_COMPONENTS: tuple[str, ...] = ("owner_id",) + IDENTITY_COMPONENTS


def _require_epoch_seconds(value: Any, *, origin: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"{origin}: start must be an exact integer number of seconds since "
            f"the Unix epoch, got {type(value).__name__} ({value!r})"
        )
    if value < 0:
        raise ValueError(f"{origin}: start epoch seconds must not be negative")
    return value


def start_epoch_seconds_from_datetime(value: datetime, *, origin: str) -> int:
    """Exact integer epoch seconds from an aware datetime.

    A sub-second instant cannot be represented by the canonical value, so it is
    refused rather than truncated: two activities 400 ms apart would otherwise
    share a tuple.
    """

    if value.tzinfo is None:
        raise ValueError(f"{origin}: session start must be an aware UTC datetime")
    if value.microsecond != 0:
        raise ValueError(
            f"{origin}: session start must be an exact whole second: the "
            "canonical comparison value is integer epoch seconds"
        )
    return _require_epoch_seconds(int(value.timestamp()), origin=origin)


def start_epoch_seconds_from_utc_text(value: str, *, origin: str) -> int:
    """Exact integer epoch seconds from the canonical ``...Z`` UTC text form."""

    import datetime as _datetime  # local import: keeps module import cost trivial

    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        moment = _datetime.datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(
            f"{origin}: session start {value!r} is not an ISO-8601 UTC instant"
        ) from exc
    return start_epoch_seconds_from_datetime(moment, origin=origin)


@dataclass(frozen=True)
class LogicalIdentity:
    """The identity-independent half of the logical tuple: three integers.

    Returned by the classifier, which does not know the owner and must not be
    given one; the caller that owns identity adds it through
    :meth:`LogicalTuple.from_identity`.
    """

    sport_code: int
    start_epoch_seconds: int
    elapsed_duration_ms: int

    @classmethod
    def from_values(
        cls,
        *,
        sport_code: Any,
        session_start_utc: Any,
        elapsed_duration_ms: Any,
        origin: str,
    ) -> "LogicalIdentity":
        """Build the identity half from decoded values, checking every unit."""

        if isinstance(session_start_utc, datetime):
            start_seconds = start_epoch_seconds_from_datetime(
                session_start_utc, origin=origin
            )
        elif isinstance(session_start_utc, str):
            start_seconds = start_epoch_seconds_from_utc_text(
                session_start_utc, origin=origin
            )
        elif isinstance(session_start_utc, int) and not isinstance(
            session_start_utc, bool
        ):
            start_seconds = _require_epoch_seconds(session_start_utc, origin=origin)
        else:
            raise TypeError(
                f"{origin}: session start must be an aware datetime or the "
                f"canonical UTC text form, got {type(session_start_utc).__name__}"
            )
        return cls(
            sport_code=canonical_sport_code(sport_code, origin=origin),
            start_epoch_seconds=start_seconds,
            elapsed_duration_ms=require_elapsed_duration_ms(
                elapsed_duration_ms,
                origin=origin,
                unit=CANONICAL_DURATION_UNIT,
            ),
        )

    def with_owner(self, owner_id: int) -> "LogicalTuple":
        return LogicalTuple.from_identity(owner_id, self)

    def as_dict(self) -> dict[str, Any]:
        """The persisted form, carrying the unit of every component.

        The units are written into the record rather than assumed by a reader,
        so ``elapsed_duration_ms`` cannot later be compared as if it were seconds.
        """

        return {
            "sport_code": self.sport_code,
            "sport_name": sport_name(self.sport_code),
            "start_epoch_seconds": self.start_epoch_seconds,
            "elapsed_duration_ms": self.elapsed_duration_ms,
            "start_unit": "integer_seconds_since_unix_epoch",
            "elapsed_unit": CANONICAL_DURATION_UNIT,
            "comparison": "exact_integer_equality",
            "tolerance": None,
            "sub_sport_is_a_component": False,
            "contract": "duplicate-conflict-options section 6",
        }


@dataclass(frozen=True)
class LogicalTuple:
    """The exact logical tuple of section 6, and the only conflict key.

    Equality is integer equality on the four canonical values. There is no
    tolerance, epsilon, rounding or normalisation step, because there is nothing
    to configure: ``TOLERANCE_PARAMETER_TOKENS`` is empty and
    ``datara.dedup.assert_no_tolerance_parameters`` keeps it that way, and its
    companion ``ordering_comparisons`` refuses any ordering comparison on a tuple
    component.

    This is the one definition. ``datara.classification`` produces the
    :class:`LogicalIdentity` half from file bytes, ``datara.normalization``
    produces the millisecond value, and ``datara.dedup`` consumes the whole key.
    """

    owner_id: int
    sport_code: int
    start_epoch_seconds: int
    elapsed_duration_ms: int

    @classmethod
    def from_identity(cls, owner_id: int, identity: LogicalIdentity) -> "LogicalTuple":
        if isinstance(owner_id, bool) or not isinstance(owner_id, int):
            raise TypeError(
                "the logical tuple owner component must be an integer identity "
                f"id, got {type(owner_id).__name__} ({owner_id!r})"
            )
        return cls(
            owner_id=owner_id,
            sport_code=identity.sport_code,
            start_epoch_seconds=identity.start_epoch_seconds,
            elapsed_duration_ms=identity.elapsed_duration_ms,
        )

    @classmethod
    def from_session(cls, owner_id: int, facts: Any, *, origin: str | None = None) -> "LogicalTuple":
        """Build the key from anything exposing the three canonical facts.

        ``facts`` is duck-typed on purpose: ``datara.dedup.SessionFacts`` carries
        them, and so does any future caller, without this pure module importing
        the persistence layer.
        """

        where = origin or f"LogicalTuple.from_session({type(facts).__name__})"
        identity = LogicalIdentity.from_values(
            sport_code=facts.sport_code,
            session_start_utc=facts.session_start_utc,
            elapsed_duration_ms=facts.elapsed_duration_ms,
            origin=where,
        )
        return cls.from_identity(owner_id, identity)

    def as_dict(self) -> dict[str, Any]:
        payload = {"owner_id": self.owner_id}
        payload.update(
            LogicalIdentity(
                sport_code=self.sport_code,
                start_epoch_seconds=self.start_epoch_seconds,
                elapsed_duration_ms=self.elapsed_duration_ms,
            ).as_dict()
        )
        return payload


__all__ = [
    "CANONICAL_DURATION_UNIT",
    "SECONDS_UNIT",
    "MILLISECONDS_PER_SECOND",
    "MIN_ELAPSED_DURATION_MS",
    "MAX_ELAPSED_DURATION_MS",
    "SPORT_CODES",
    "IDENTITY_COMPONENTS",
    "TUPLE_COMPONENTS",
    "require_elapsed_duration_ms",
    "elapsed_duration_ms_from_seconds",
    "canonical_sport_code",
    "sport_name",
    "start_epoch_seconds_from_datetime",
    "start_epoch_seconds_from_utc_text",
    "LogicalIdentity",
    "LogicalTuple",
]
