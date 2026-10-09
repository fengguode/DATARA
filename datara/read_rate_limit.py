"""Local owner/operation rate policy for read-only saved-metric routes.

WP05/TK64; CUS09-CUS10; SR19-SR21/SR31/SR73. The local pilot is loopback-only
and uses Django's process-local cache; this is a request-volume guard for that
single-process operating mode, not a distributed or hosted-service guarantee.
"""
from __future__ import annotations

import hashlib

from django.core.cache import cache


WINDOW_SECONDS = 60
REQUESTS_PER_OWNER_OPERATION = 60
SUPPORTED_OPERATIONS = frozenset({"recorded_metric_read"})


def owner_operation_read_limited(owner_id: object, operation: str) -> bool:
    """Return true after 60 reads in a fixed 60-second owner/operation window.

    Cache failures are intentionally raised to the request gate, which fails
    closed with a safe 503. Cache keys contain only a digest, not the owner ID.
    """
    if owner_id is None or operation not in SUPPORTED_OPERATIONS:
        raise ValueError("unsupported owner/operation rate-policy input")

    identity = hashlib.sha256(
        f"{operation}\0{owner_id}".encode("utf-8")
    ).hexdigest()
    key = f"datara:read-rate:v1:{identity}"

    # add() starts the fixed window atomically. LocMemCache serializes its
    # operations within this process; a shared deployment needs an atomic,
    # shared cache implementation to preserve the owner-wide limit.
    if cache.add(key, 1, timeout=WINDOW_SECONDS):
        return False

    try:
        count = cache.incr(key)
    except ValueError:
        # The window may expire between add() and incr(). Starting a new
        # window is safe only if this call wins add() after that expiry.
        if cache.add(key, 1, timeout=WINDOW_SECONDS):
            return False
        count = cache.incr(key)

    return count > REQUESTS_PER_OWNER_OPERATION
