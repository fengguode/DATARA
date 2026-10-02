"""Immutable, content-addressed storage of original bytes (CUS02, SR03, SR04).

This module is the **byte** half of TK15 (#121). It owns exactly one idea: an
uploaded original is written once, addressed by the SHA-256 of its own bytes,
and is thereafter immutable. `datara.dedup` is the **policy** half and decides
what a submission means; it calls into this module and never writes a file.

Authority for the rules implemented here:

* `docs/management/p0-decision-baseline-2026-10-01.md:48` (D01) -- "Original
  bytes are immutable"; same owner + same SHA-256 is idempotent; never
  silently merge, use tolerance or overwrite.
* `docs/management/source-evidence/duplicate-conflict-options.md` -- section 7
  ("Never overwrite": originals are immutable, superseded originals are
  retained, never mutated), section 8.1 (idempotence under concurrency is
  enforced by a database unique constraint, **not** application read-then-write)
  and section 8.4 (the file store and the database are not one transaction, so a
  durable staging marker plus owner-scoped reconciliation is required, and an
  unreconciled submission is not visible in normal history).
* `docs/p0-design/implementation-contracts.md:7` -- the owner identity is
  server-derived and is never client-supplied; cross-cutting rule 2 -- original
  bytes are immutable and every derived item carries source references.

Four properties are enforced in code rather than asserted in a comment, and
each is covered by a mutation-proven test in `datara/tests/test_storage.py`:

1. **Write once.** `OriginalStore.put` creates its target with
   ``O_CREAT | O_EXCL``. There is no ``update``, ``overwrite`` or ``delete``
   method on the class at all, so no caller can express a rewrite. A repeat
   ``put`` of identical bytes is a verified no-op that reports
   ``created_new=False``; it never produces a second original.
2. **Addressed by content.** The path is derived from the owner id and the
   SHA-256 of the bytes, never from a filename, a timestamp or a counter, so
   the reference is re-derivable and cannot be guessed from user input.
3. **Owner-scoped paths.** The owner id is part of the path. Two identities
   holding the same bytes get two distinct storage references, and swapping an
   owner identifier raises `ResourceNotVisible` rather than returning the other
   identity's bytes. This is why the store is *not* a global content-addressed
   blob store: a shared one would be a cross-identity disclosure channel for
   the `duplicate_of_existing` rule.
4. **Verified on read.** `OriginalStore.get` re-hashes what it reads and raises
   `OriginalIntegrityError` on any mismatch, so "the stored original is
   byte-identical after re-read" is checked on every read, not assumed.

**No model is called anywhere in this module**, and nothing here stores an
outcome of executing a skill against a model. This file contains no provider
transport, no secret handling and no inference path (SR06).

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

from datara.models import ResourceNotVisible

#: Digest wire format. ``SourceObject.digest`` is a 71-character column, which
#: is exactly ``len("sha256:") + 64``.
DIGEST_PREFIX = "sha256:"

_HEX_64 = re.compile(r"\A[0-9a-f]{64}\Z")

#: Never read a personal telemetry file from the repository. The founder's
#: export is private; this constant exists so that a path pointing at it is
#: refused loudly rather than read. See `docs/management/fit-intake-...` and the
#: founder's 1 October privacy decision: no hash of it is recorded or published.
FORBIDDEN_SOURCE_NAMES = frozenset({"24563001348_ACTIVITY.fit"})


class OriginalIntegrityError(Exception):
    """Stored bytes do not hash to the digest that addresses them.

    Either the file was corrupted outside this module or a digest collision was
    constructed deliberately. Both are refused rather than repaired: repairing
    would be an overwrite.
    """


class UnsupportedSourceName(Exception):
    """A submission named a file that must never be ingested from the repo."""


def sha256_digest(data: bytes) -> str:
    """Return the ``sha256:<64 lowercase hex>`` digest of ``data``."""

    return DIGEST_PREFIX + hashlib.sha256(data).hexdigest()


def parse_digest(digest: str) -> str:
    """Validate a stored digest and return its 64-character hex part.

    Rejects anything that is not exactly the canonical lowercase form. Digest
    strings are compared byte-for-byte everywhere, so a permissive parser would
    create two spellings of one original and defeat the idempotency rule.
    """

    if not isinstance(digest, str):
        raise ValueError(f"digest must be a string, got {type(digest).__name__}")
    if not digest.startswith(DIGEST_PREFIX):
        raise ValueError(f"digest must start with {DIGEST_PREFIX!r}: {digest!r}")
    hex_part = digest[len(DIGEST_PREFIX):]
    if not _HEX_64.match(hex_part):
        raise ValueError(f"digest is not canonical sha256 hex: {digest!r}")
    return hex_part


def reject_forbidden_source_name(name: str | None) -> None:
    """Refuse a source file that is known to be private personal telemetry.

    The repository contains one real Garmin Connect export belonging to the
    founder. It is private, it is excluded from version control, and no hash of
    it may be recorded or published. This guard raises before any byte is read
    or hashed.
    """

    if name is None:
        return
    if Path(name).name in FORBIDDEN_SOURCE_NAMES:
        raise UnsupportedSourceName(
            "refusing to read private personal telemetry from the repository; "
            "use a DATARA-authored synthetic fixture instead"
        )


@dataclass(frozen=True)
class StoredOriginal:
    """The durable result of writing one original.

    ``created_new`` is the evidence that a repeat submission did not create a
    second original: it is ``False`` when the write-once path already held these
    exact bytes for this owner.
    """

    digest: str
    byte_length: int
    storage_reference: str
    media_type: str
    created_new: bool
    verified: bool


@dataclass(frozen=True)
class StagedUpload:
    """A durable staging marker for a submission not yet reconciled.

    Section 8.4: the file store and the database are not one transaction. While
    a submission is unreconciled it is not visible in normal history and cannot
    be counted, because no `Activity` row exists for it. A staging marker is how
    a crash between the two stores is detected and retried rather than lost.
    """

    marker_id: str
    owner_id: int
    digest: str
    byte_length: int
    staged_path: str
    created_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "marker_id": self.marker_id,
            "owner_id": self.owner_id,
            "digest": self.digest,
            "byte_length": self.byte_length,
            "staged_path": self.staged_path,
            "created_at": self.created_at,
        }


def _fsync_directory(path: Path) -> None:
    """Best-effort directory fsync so a rename is durable across a crash.

    Not supported on every platform (notably Windows, where opening a
    directory for fsync fails). A failure here is not fatal: the write-once
    guarantee comes from ``O_EXCL``, not from durability of the directory entry.
    """

    try:
        fd = os.open(str(path), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


class OriginalStore:
    """Write-once, content-addressed, owner-scoped storage of original bytes.

    The class deliberately exposes **no** mutating operation on an existing
    original. ``put`` either creates a new immutable original or verifies and
    returns the existing one. ``remove_staging`` is the only delete, it is
    restricted to unreconciled staging markers, and it cannot address an
    original because the two live in different directories.
    """

    ORIGINALS_DIRNAME = "originals"
    STAGING_DIRNAME = "staging"

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root)

    # -- layout ---------------------------------------------------------------

    def owner_dir(self, owner_id: int, *, kind: str = ORIGINALS_DIRNAME) -> Path:
        """Directory holding one owner's originals or staging markers.

        The owner id is a validated positive integer, never a free-form string,
        so a caller cannot escape the root with ``..``.
        """

        owner = _validate_owner_id(owner_id)
        return self.root / kind / f"owner_{owner:012d}"

    def storage_reference(self, owner_id: int, digest: str) -> str:
        """The stable, re-derivable reference string for one original.

        Derived from owner id plus content digest only -- never from a filename,
        a clock reading or a counter -- so it is reproducible and carries no
        information the owner did not already supply.
        """

        hex_part = parse_digest(digest)
        owner = _validate_owner_id(owner_id)
        return f"{self.ORIGINALS_DIRNAME}/owner_{owner:012d}/{hex_part}.bin"

    def path_for(self, owner_id: int, digest: str) -> Path:
        return self.root / self.storage_reference(owner_id, digest)

    # -- write once -----------------------------------------------------------

    def put(self, owner_id: int, data: bytes, *, media_type: str = "application/octet-stream") -> StoredOriginal:
        """Write ``data`` once, addressed by its own SHA-256.

        Idempotent for identical bytes: the second call verifies the existing
        file and returns ``created_new=False`` without writing. A different
        payload for an occupied path is refused, never merged into the original.
        """

        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError(f"original bytes must be bytes-like, got {type(data).__name__}")
        payload = bytes(data)
        if not payload:
            raise ValueError("refusing to store a zero-length original")

        digest = sha256_digest(payload)
        target = self.path_for(owner_id, digest)
        target.parent.mkdir(parents=True, exist_ok=True)

        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
        try:
            fd = os.open(str(target), flags)
        except FileExistsError:
            # The original already exists. Verify, never rewrite.
            existing = self._read_and_verify(owner_id, digest, target)
            if existing != payload:
                raise OriginalIntegrityError(
                    f"refusing to overwrite original {digest}: stored bytes differ"
                )
            return StoredOriginal(
                digest=digest,
                byte_length=len(existing),
                storage_reference=self.storage_reference(owner_id, digest),
                media_type=media_type,
                created_new=False,
                verified=True,
            )

        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except BaseException:
            # We exclusively created this file and it is incomplete, so removing
            # it discards our own partial write. It was never a complete original
            # and nothing referenced it; this is not a deletion of history.
            try:
                target.unlink()
            except OSError:
                pass
            raise
        _fsync_directory(target.parent)

        return StoredOriginal(
            digest=digest,
            byte_length=len(payload),
            storage_reference=self.storage_reference(owner_id, digest),
            media_type=media_type,
            created_new=True,
            verified=True,
        )

    # -- read and verify ------------------------------------------------------

    def get(self, owner_id: int, digest: str) -> bytes:
        """Read one original back, re-hashing it to prove it is intact.

        A wrong owner id is indistinguishable from a missing original: both
        raise `ResourceNotVisible`, so a denial cannot confirm that another
        identity holds these bytes (section 7, "No cross-owner disclosure").
        """

        target = self.path_for(owner_id, digest)
        return self._read_and_verify(owner_id, digest, target)

    def _read_and_verify(self, owner_id: int, digest: str, target: Path) -> bytes:
        try:
            data = target.read_bytes()
        except FileNotFoundError:
            raise ResourceNotVisible("datara.storage.Original", digest) from None
        except OSError as exc:
            raise OriginalIntegrityError(
                f"original {digest} could not be read: {exc}"
            ) from exc
        actual = sha256_digest(data)
        if actual != digest:
            raise OriginalIntegrityError(
                f"stored bytes hash to {actual}, not the addressing digest {digest}"
            )
        return data

    def exists(self, owner_id: int, digest: str) -> bool:
        return self.path_for(owner_id, digest).is_file()

    def verify(self, owner_id: int, digest: str) -> bool:
        """Re-read and re-hash one original. Used by reconciliation and tests."""

        self.get(owner_id, digest)
        return True

    # -- durable staging and reconciliation (section 8.4) ---------------------

    def stage(self, owner_id: int, data: bytes) -> StagedUpload:
        """Park bytes durably outside the originals tree with a marker.

        A staged upload is deliberately **not** in the originals directory, so
        it is not addressable as history and cannot be counted, before
        reconciliation confirms it.
        """

        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError(f"original bytes must be bytes-like, got {type(data).__name__}")
        payload = bytes(data)
        if not payload:
            raise ValueError("refusing to stage a zero-length original")

        digest = sha256_digest(payload)
        marker_id = str(uuid.uuid4())
        staged_dir = self.owner_dir(owner_id, kind=self.STAGING_DIRNAME)
        staged_dir.mkdir(parents=True, exist_ok=True)
        staged_path = staged_dir / f"{marker_id}.bin"

        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
        fd = os.open(str(staged_path), flags)
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        upload = StagedUpload(
            marker_id=marker_id,
            owner_id=_validate_owner_id(owner_id),
            digest=digest,
            byte_length=len(payload),
            staged_path=str(staged_path.relative_to(self.root)),
            created_at=datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        )
        marker_file = staged_dir / f"{marker_id}.json"
        marker_file.write_text(
            json.dumps(upload.as_dict(), indent=2, sort_keys=True), encoding="utf-8"
        )
        _fsync_directory(staged_dir)
        return upload

    def pending_staging(self, owner_id: int) -> list[StagedUpload]:
        """Owner-scoped reconciliation queue: staged submissions not confirmed."""

        staged_dir = self.owner_dir(owner_id, kind=self.STAGING_DIRNAME)
        if not staged_dir.is_dir():
            return []
        pending: list[StagedUpload] = []
        for marker_file in sorted(staged_dir.glob("*.json")):
            try:
                payload = json.loads(marker_file.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                # A truncated marker is itself an interruption to reconcile.
                continue
            if not (staged_dir / f"{payload['marker_id']}.bin").is_file():
                continue
            if int(payload["owner_id"]) != _validate_owner_id(owner_id):
                # A marker filed under the wrong owner is never adopted.
                continue
            pending.append(StagedUpload(**payload))
        return pending

    def confirm_staging(self, upload: StagedUpload, *, media_type: str = "application/octet-stream") -> StoredOriginal:
        """Reconcile a staged upload into the write-once originals tree.

        This is the only path that turns staged bytes into an original. It is
        safe to retry: a confirmed marker whose original already exists verifies
        and returns ``created_new=False`` instead of writing again.
        """

        staged_dir = self.owner_dir(upload.owner_id, kind=self.STAGING_DIRNAME)
        staged_file = staged_dir / f"{upload.marker_id}.bin"
        try:
            payload = staged_file.read_bytes()
        except FileNotFoundError:
            raise OriginalIntegrityError(
                f"staged payload {upload.marker_id} is missing; cannot reconcile"
            ) from None
        if sha256_digest(payload) != upload.digest:
            raise OriginalIntegrityError(
                f"staged payload {upload.marker_id} does not match its recorded digest"
            )
        stored = self.put(upload.owner_id, payload, media_type=media_type)
        self.remove_staging(upload)
        return stored

    def remove_staging(self, upload: StagedUpload) -> None:
        """Delete a staging marker and its payload.

        Scoped to the staging directory and to the marker's own uuid, so it can
        never address an original. Callers must only use it after the original
        is durable.
        """

        staged_dir = self.owner_dir(upload.owner_id, kind=self.STAGING_DIRNAME)
        for suffix in (".bin", ".json"):
            path = staged_dir / f"{upload.marker_id}{suffix}"
            try:
                path.unlink()
            except OSError:
                pass

    # -- introspection used by the tests -------------------------------------

    def mutating_public_api(self) -> list[str]:
        """Names on this class that could rewrite or remove an original.

        The immutability claim is testable: the set must stay empty, so adding
        an ``overwrite``/``update``/``delete`` method to the store fails a test
        rather than quietly creating a product defect.
        """

        forbidden = ("overwrite", "update", "replace", "delete", "remove_original", "truncate")
        found: list[str] = []
        for name in dir(type(self)):
            if name.startswith("_"):
                continue
            attribute = getattr(type(self), name, None)
            if callable(attribute) and any(token in name.lower() for token in forbidden):
                found.append(name)
        return sorted(found)


def _validate_owner_id(owner_id: Any) -> int:
    """Accept only a positive integer owner id.

    The owner identity is server-derived (contracts rule 1). Rejecting a string
    here keeps a client-supplied value from ever reaching a filesystem path.
    """

    if isinstance(owner_id, bool) or not isinstance(owner_id, int):
        raise TypeError(
            f"owner_id must be a server-derived int, got {type(owner_id).__name__}"
        )
    if owner_id <= 0:
        raise ValueError(f"owner_id must be positive, got {owner_id}")
    return owner_id


def resolve_owner_id(owner: Any) -> int:
    """Return the server-derived owner id from a user instance or a bare id.

    A ``User`` is resolved to its ``pk``. An ``int`` is accepted because the
    store is called from trusted server code that already authenticated the
    request; the type check still refuses a client string.
    """

    if hasattr(owner, "pk") and owner.pk is not None:
        return _validate_owner_id(int(owner.pk))
    return _validate_owner_id(owner)


__all__ = [
    "DIGEST_PREFIX",
    "FORBIDDEN_SOURCE_NAMES",
    "OriginalIntegrityError",
    "OriginalStore",
    "StoredOriginal",
    "StagedUpload",
    "UnsupportedSourceName",
    "parse_digest",
    "reject_forbidden_source_name",
    "resolve_owner_id",
    "sha256_digest",
]
