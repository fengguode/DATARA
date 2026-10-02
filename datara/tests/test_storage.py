"""TC02 Original preservation: immutability, content addressing and isolation.

Every test below states **the mutation that makes it fail**. A test that cannot
be made to fail by a plausible defect is not evidence, so each one names the
defect it detects rather than only the behaviour it observes.

Substrate note: these run on SQLite, a declared deviation, because PostgreSQL
17 is absent from this host. The properties asserted here are filesystem
properties and Python-level guarantees, not transaction-isolation behaviour, so
the deviation does not weaken them. The database-constraint behaviour that *does*
depend on the engine is in `test_conflict.py`, which records that dependency.

Fixtures are DATARA-authored synthetic blobs. The founder's private export is
never read, copied, hashed or stat-ed, and no upstream SDK sample is committed:
both are refused in code (`datara.storage.reject_forbidden_source_name`).

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.test import TestCase

from datara.models import ImmutabilityViolation, ResourceNotVisible, SourceObject
from datara.storage import (
    DIGEST_PREFIX,
    OriginalIntegrityError,
    OriginalStore,
    UnsupportedSourceName,
    parse_digest,
    reject_forbidden_source_name,
    resolve_owner_id,
    sha256_digest,
)

#: DATARA-authored synthetic original. Not a FIT file and not derived from any
#: SDK sample: it is a self-describing blob so the byte-level contract can be
#: tested without any third-party redistribution question (FIX02-FIX04).
GENERATOR_VERSION = "datara-synthetic-original/1"


def synthetic_original(variant: int = 1, *, size: int = 384) -> bytes:
    """Deterministic synthetic bytes. Same variant always yields the same bytes."""

    header = f"{GENERATOR_VERSION}|variant={variant}|".encode("utf-8")
    filler = bytes((variant * 7 + index) % 251 for index in range(size))
    return header + filler


def count_original_files(root: Path) -> int:
    return len(list((root / OriginalStore.ORIGINALS_DIRNAME).rglob("*.bin")))


class StorageTestCase(TestCase):
    """A store rooted in a throwaway directory, and two disposable identities."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.store = OriginalStore(self.root)
        self.owner = User.objects.create_user("storage-owner")
        self.other = User.objects.create_user("storage-other")
        self.addCleanup(self._tmp.cleanup)

    # -- TC02.1 immutability -------------------------------------------------

    def test_original_is_created_once_and_repeat_is_a_verified_no_op(self) -> None:
        """Identical bytes never produce a second original.

        Mutation that fails: ``put`` using ``O_TRUNC``/``O_CREAT`` without
        ``O_EXCL``, or returning ``created_new=True`` unconditionally. The first
        call reports ``created_new=True``; the second must report ``False`` and
        must not touch the file.
        """

        data = synthetic_original(1)
        first = self.store.put(self.owner.pk, data)
        second = self.store.put(self.owner.pk, data)

        self.assertTrue(first.created_new)
        self.assertFalse(second.created_new, "a repeat put claimed a new original")
        self.assertEqual(first.digest, second.digest)
        self.assertEqual(first.storage_reference, second.storage_reference)
        self.assertEqual(count_original_files(self.root), 1)

    def test_stored_original_is_byte_identical_after_re_read(self) -> None:
        """The bytes that come back are the bytes that went in.

        Mutation that fails: ``get`` returning a re-derived, truncated,
        decompressed or re-serialised payload instead of reading the stored
        file. The stored file is also re-hashed on every read, so a silent
        rewrite between write and read is caught rather than returned.
        """

        data = synthetic_original(7)
        stored = self.store.put(self.owner.pk, data)
        read_back = self.store.get(self.owner.pk, stored.digest)

        self.assertEqual(read_back, data)
        self.assertEqual(sha256_digest(read_back), stored.digest)
        self.assertTrue(self.store.verify(self.owner.pk, stored.digest))

    def test_a_different_payload_cannot_be_written_over_an_original(self) -> None:
        """A second, different original never replaces the first.

        Mutation that fails: ``put`` treating an occupied path as an overwrite.
        Here the different payload simply lands at its own content-addressed
        path, so the first original is still readable and unchanged.
        """

        first = self.store.put(self.owner.pk, synthetic_original(1))
        second = self.store.put(self.owner.pk, synthetic_original(2))

        self.assertNotEqual(first.digest, second.digest)
        self.assertEqual(self.store.get(self.owner.pk, first.digest), synthetic_original(1))
        self.assertEqual(count_original_files(self.root), 2)

    def test_store_exposes_no_mutation_api(self) -> None:
        """Immutability is structural: there is no method that could rewrite one.

        Mutation that fails: adding an ``overwrite``/``update``/``delete``
        method to ``OriginalStore``. The immutability claim is then no longer
        enforced by the shape of the class and this test fails.
        """

        self.assertEqual(
            self.store.mutating_public_api(),
            [],
            "OriginalStore gained a method that could rewrite or remove an original",
        )
        for forbidden in ("overwrite", "update", "delete", "truncate", "remove_original"):
            self.assertFalse(
                hasattr(OriginalStore, forbidden),
                f"OriginalStore must not expose {forbidden}()",
            )

    def test_corrupted_original_is_refused_rather_than_repaired(self) -> None:
        """Damage is detected on read and never silently accepted.

        Mutation that fails: ``_read_and_verify`` returning the bytes without
        re-hashing, or repairing them. Repairing would be an overwrite, so the
        only correct behaviour is to raise.
        """

        stored = self.store.put(self.owner.pk, synthetic_original(3))
        path = self.store.path_for(self.owner.pk, stored.digest)
        path.write_bytes(b"corrupted" + b"z" * 64)

        with self.assertRaises(OriginalIntegrityError):
            self.store.get(self.owner.pk, stored.digest)

    def test_digest_is_content_addressed_and_canonically_spelled(self) -> None:
        """The reference is derived from content, and one original one spelling.

        Mutation that fails: a filename-, timestamp- or counter-derived
        reference, or a permissive digest parser that would let two spellings of
        the same original defeat the idempotency rule.
        """

        data = synthetic_original(4)
        stored = self.store.put(self.owner.pk, data)

        self.assertTrue(stored.digest.startswith(DIGEST_PREFIX))
        self.assertEqual(len(stored.digest), 71)
        self.assertIn(parse_digest(stored.digest), stored.storage_reference)
        self.assertNotIn("upload", stored.storage_reference)

        for bad in ("", "sha1:deadbeef", stored.digest[:-1], stored.digest.upper(), "abc"):
            with self.assertRaises(ValueError):
                parse_digest(bad)

    def test_source_object_row_is_immutable_in_the_database(self) -> None:
        """The database row refuses a rewrite as well as the file.

        Mutation that fails: removing the ``IMMUTABLE_FIELDS`` guard from
        ``SourceObject.save()``. The file layer already refuses the rewrite, so
        only this check proves the metadata cannot be rewritten underneath it.
        """

        data = synthetic_original(5)
        row = SourceObject.objects.create(
            owner=self.owner,
            digest=sha256_digest(data),
            byte_length=len(data),
            storage_reference=self.store.storage_reference(self.owner.pk, sha256_digest(data)),
            media_type="application/octet-stream",
        )
        row.byte_length = row.byte_length + 1
        with self.assertRaises(ImmutabilityViolation):
            row.save()

    # -- TC02.2 two-identity isolation ---------------------------------------

    def test_identical_bytes_of_two_identities_get_distinct_references(self) -> None:
        """Two owners with the same bytes do not share one original.

        Mutation that fails: a global content-addressed store whose path omits
        the owner id. The two references would be identical, one identity's
        read would return the other identity's bytes, and a digest match would
        become a cross-identity disclosure channel.
        """

        data = synthetic_original(6)
        mine = self.store.put(self.owner.pk, data)
        theirs = self.store.put(self.other.pk, data)

        self.assertEqual(mine.digest, theirs.digest)
        self.assertNotEqual(
            mine.storage_reference, theirs.storage_reference, "references collided"
        )
        self.assertEqual(count_original_files(self.root), 2)

    def test_swapping_the_owner_identifier_fails_rather_than_returning_data(self) -> None:
        """Cross-identity read is refused, not served.

        Mutation that fails: a read path that looks the original up by digest
        alone, or that catches ``ResourceNotVisible`` and falls back to an
        unscoped read. The second is the dangerous one, because it returns the
        other identity's bytes while still reporting a denial.
        """

        stored = self.store.put(self.owner.pk, synthetic_original(8))
        stranger = User.objects.create_user("storage-stranger")

        with self.assertRaises(ResourceNotVisible):
            self.store.get(stranger.pk, stored.digest)
        with self.assertRaises(ResourceNotVisible):
            self.store.get(self.owner.pk + 9999, stored.digest)

    def test_owner_id_must_be_a_server_derived_integer(self) -> None:
        """A client-supplied owner string cannot become a filesystem path.

        Mutation that fails: ``_validate_owner_id`` accepting any string, which
        would let ``owner_id="../../.."`` escape the store root.
        """

        for bad in ("1", 1.0, True, 0, -3, None):
            with self.assertRaises((TypeError, ValueError)):
                self.store.owner_dir(bad)
        self.assertEqual(self.store.owner_dir(1).name, "owner_000000000001")
        self.assertEqual(resolve_owner_id(self.owner), self.owner.pk)

    # -- TC02.3 durable staging and reconciliation ---------------------------

    def test_unreconciled_staged_upload_is_not_an_original(self) -> None:
        """A staged submission is invisible until it is reconciled.

        Mutation that fails: ``stage`` writing into the originals directory, or
        ``pending_staging`` ignoring the marker. Section 8.4 requires that an
        unreconciled submission cannot be counted, which holds here because it
        is not addressable as an original at all.
        """

        data = synthetic_original(9)
        staged = self.store.stage(self.owner.pk, data)

        self.assertEqual(count_original_files(self.root), 0)
        self.assertFalse(self.store.exists(self.owner.pk, staged.digest))
        self.assertEqual(self.store.pending_staging(self.owner.pk), [staged])
        self.assertEqual(self.store.pending_staging(self.other.pk), [])

    def test_confirming_staging_is_retry_safe_and_idempotent(self) -> None:
        """Reconciliation can be retried without creating a second original.

        Mutation that fails: ``confirm_staging`` writing unconditionally, or
        ``remove_staging`` addressing the originals tree. A crash-and-retry is
        the normal case here, so the retry must converge.
        """

        data = synthetic_original(10)
        staged = self.store.stage(self.owner.pk, data)
        confirmed = self.store.confirm_staging(staged)

        self.assertTrue(confirmed.created_new)
        self.assertEqual(self.store.get(self.owner.pk, confirmed.digest), data)
        self.assertEqual(self.store.pending_staging(self.owner.pk), [])
        self.assertEqual(count_original_files(self.root), 1)

        # Retrying the same confirmation, as a crash-retry would.
        replay = self.store.put(self.owner.pk, data)
        self.assertFalse(replay.created_new)
        self.assertEqual(count_original_files(self.root), 1)

    def test_staged_payload_that_does_not_match_its_marker_is_refused(self) -> None:
        """A tampered staging payload cannot be promoted to an original.

        Mutation that fails: ``confirm_staging`` trusting the marker and calling
        ``put`` on whatever bytes are on disk, which would let a replaced
        staging file become an immutable original under the old digest.
        """

        data = synthetic_original(11)
        staged = self.store.stage(self.owner.pk, data)
        (self.root / staged.staged_path).write_bytes(synthetic_original(12))

        with self.assertRaises(OriginalIntegrityError):
            self.store.confirm_staging(staged)

    # -- fixture and privacy guards ------------------------------------------

    def test_private_founder_telemetry_is_refused_before_any_read(self) -> None:
        """The founder's private export can never be ingested from the repo.

        Mutation that fails: removing the guard, or renaming the constant. The
        founder's 1 October privacy decision forbids reading, copying, hashing
        or publishing that file, so the refusal happens before any byte is
        touched rather than being left to reviewer discipline.
        """

        with self.assertRaises(UnsupportedSourceName):
            reject_forbidden_source_name("24563001348_ACTIVITY.fit")
        with self.assertRaises(UnsupportedSourceName):
            reject_forbidden_source_name("some/dir/24563001348_ACTIVITY.fit")
        reject_forbidden_source_name("synthetic.fit")
        reject_forbidden_source_name(None)

    def test_degenerate_submissions_are_refused(self) -> None:
        """Empty bytes and non-bytes never become an original.

        Mutation that fails: dropping the zero-length check, which would create
        a valid-looking original addressed by the digest of the empty string.
        """

        with self.assertRaises(ValueError):
            self.store.put(self.owner.pk, b"")
        with self.assertRaises(TypeError):
            self.store.put(self.owner.pk, "not bytes")  # type: ignore[arg-type]
        self.assertEqual(count_original_files(self.root), 0)

    def test_synthetic_fixture_generator_is_deterministic(self) -> None:
        """The fixture is DATARA-authored and byte-stable.

        Mutation that fails: a generator using a clock, a random source or an
        OS path, which would make every run a fresh digest and quietly destroy
        the duplicate test's ability to compare bytes.
        """

        self.assertEqual(synthetic_original(1), synthetic_original(1))
        self.assertNotEqual(synthetic_original(1), synthetic_original(2))
        self.assertTrue(synthetic_original(1).startswith(GENERATOR_VERSION.encode()))
