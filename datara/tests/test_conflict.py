"""TC03 Duplicate and conflict handling, and the TC22/SR33 presentation rules.

Every test states **the mutation that makes it fail**. The negative cases are the
important half: a fuzzy or tolerant implementation must be *shown* to fail them,
so `test_tolerance_mutation_would_have_merged_is_proven_detectable` deliberately
builds the wrong matcher and demonstrates that it produces a different verdict.

Authority: `docs/management/source-evidence/duplicate-conflict-options.md`
sections 5-9, and `p0-decision-baseline-2026-10-01.md:48` (D01).

Substrate note: SQLite, a declared deviation, because PostgreSQL 17 is absent
from this host. The pinned PostgreSQL run did not occur. Two properties below are
**portable risks** rather than equivalent behaviour and are called out as such:
the ``(owner, digest)`` unique constraint is the load-bearing idempotency
mechanism and both engines enforce it, but the *concurrent* interleaving that
section 8.1 describes depends on PostgreSQL's MVCC and on the constraint being
immediate, which this suite does not exercise. The single-writer interleaving is
tested; the multi-connection race is not, and is not claimed.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import tempfile
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase

from datara import dedup
from datara.canonical import SECONDS_UNIT, require_elapsed_duration_ms
from datara.dedup import (
    Disposition,
    LogicalTuple,
    SessionFacts,
    assert_no_outcome_fields,
    assert_no_tolerance_parameters,
    build_snapshot_scope,
    canonical_sport_code,
    describe_reference,
    excluded_candidates,
    find_exact_tuple_match,
    history,
    ingest,
    open_conflicts,
    ordering_comparisons,
    outcome_text,
    resolve_uncertain,
    tolerance_parameters,
    tuple_group_key,
)
from datara.models import (
    MILESTONE_A_MODELS,
    Activity,
    Import,
    Quarantine,
    ResourceNotVisible,
    Session,
    Snapshot,
    SourceObject,
)
from datara.storage import OriginalStore, sha256_digest

from datara.tests.test_storage import synthetic_original

BASE_PAYLOAD = {
    "normalization_digest": sha256_digest(b"synthetic-normalization/1"),
    "policy_version": "synthetic-policy/1",
    "mapping_reference": "synthetic-mapping/1",
}
BASE_START = datetime(2026, 3, 1, 6, 30, 0, tzinfo=timezone.utc)


def base_facts(**overrides: object) -> SessionFacts:
    values = {
        "sport_code": 1,
        "session_start_utc": BASE_START,
        "elapsed_duration_ms": 3_723_000,
    }
    values.update(overrides)
    return SessionFacts(**values)  # type: ignore[arg-type]


class ConflictTestCase(TestCase):
    """Two disposable identities and an isolated store per test."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.store = OriginalStore(Path(self._tmp.name))
        self.addCleanup(self._tmp.cleanup)
        self.owner = User.objects.create_user("conflict-owner")
        self.other = User.objects.create_user("conflict-other")
        self.stranger = User.objects.create_user("conflict-stranger")

    # -- helpers --------------------------------------------------------------

    def submit(
        self,
        owner: User,
        variant: int,
        facts: SessionFacts | None = None,
        *,
        payload: dict | None = None,
        file_name: str | None = None,
    ):
        return ingest(
            owner,
            data=synthetic_original(variant),
            media_type="application/octet-stream",
            sessions=[facts if facts is not None else base_facts()],
            activity_payload=payload or BASE_PAYLOAD,
            store=self.store,
            submitted_file_name=file_name or f"activity-{variant}.fit",
        )

    def assert_only_accepted_history(self, owner: User, expected: int) -> None:
        self.assertEqual(list(history(owner)).__len__(), expected)

    # -- TC03.1 P5 accept is the baseline ------------------------------------

    def test_a_new_file_with_a_new_tuple_is_accepted(self) -> None:
        """P5: bytes differ and the tuple differs, so accept.

        Mutation that fails: quarantining every import, or rejecting one whose
        tuple is merely *similar* to an existing one. Both would replace a
        visible, correct accept with a silent merge-shaped outcome.
        """

        outcome = self.submit(self.owner, 1)

        self.assertIs(outcome.disposition, Disposition.ACCEPTED)
        self.assertEqual(outcome.rule, "P5")
        self.assertTrue(outcome.created_original)
        self.assertTrue(outcome.created_activity)
        self.assertEqual(outcome.activity.disposition, Activity.PUBLISHED)
        self.assertTrue(outcome.counts_toward_volume())
        self.assertFalse(outcome.is_excluded_from_history)
        self.assertEqual(list(history(self.owner)).__len__(), 1)

    # -- TC03.2 P1 exact-duplicate idempotence -------------------------------

    def test_identical_bytes_re_uploaded_create_no_second_original(self) -> None:
        """P1: the core idempotence rule, at the byte layer and at the row layer.

        Mutation that fails: claiming the original by read-then-write instead of
        by the unique constraint, or writing the file unconditionally on a
        repeat. Either produces a second ``SourceObject`` or a second file for
        one set of bytes, which is silent double counting of the athlete's
        volume.
        """

        first = self.submit(self.owner, 1)
        second = self.submit(self.owner, 1)

        self.assertIs(first.disposition, Disposition.ACCEPTED)
        self.assertIs(second.disposition, Disposition.DUPLICATE_OF_EXISTING)
        self.assertEqual(second.rule, "P1")
        self.assertFalse(second.created_original)
        self.assertFalse(second.created_activity)

        self.assertEqual(SourceObject.objects.for_owner(self.owner.pk).count(), 1)
        self.assertEqual(Activity.objects.for_owner(self.owner.pk).count(), 1)
        self.assertEqual(Session.objects.for_owner(self.owner.pk).count(), 1)
        self.assertEqual(len(list((self.store.root / "originals").rglob("*.bin"))), 1)
        self.assertEqual(list(history(self.owner)).__len__(), 1)

    def test_a_replay_cannot_create_a_second_activity_even_after_a_lost_response(self) -> None:
        """P1 and section 8.3: an ambiguous outcome is resolved by lookup.

        Mutation that fails: a blind retry on an uncertain commit, which is
        exactly what creates a second accepted activity after a partial commit.
        The lookup must write nothing, so a caller cannot turn it into a retry.
        """

        self.submit(self.owner, 1)
        rows_before = {
            "source": SourceObject.objects.for_owner(self.owner.pk).count(),
            "activity": Activity.objects.for_owner(self.owner.pk).count(),
            "import": Import.objects.for_owner(self.owner.pk).count(),
        }

        resolved = resolve_uncertain(
            self.owner, sha256_digest(synthetic_original(1)), store=self.store
        )

        self.assertIsNotNone(resolved)
        self.assertIs(resolved.disposition, Disposition.DUPLICATE_OF_EXISTING)
        self.assertFalse(resolved.created_original)
        self.assertEqual(
            {
                "source": SourceObject.objects.for_owner(self.owner.pk).count(),
                "activity": Activity.objects.for_owner(self.owner.pk).count(),
                "import": Import.objects.for_owner(self.owner.pk).count(),
            },
            rows_before,
            "resolve_uncertain wrote to the database",
        )
        self.assertEqual(len(list((self.store.root / "originals").rglob("*.bin"))), 1)

    def test_lookup_of_uncommitted_bytes_reports_that_submission_may_be_sent(self) -> None:
        """The only condition under which a caller may submit again.

        Mutation that fails: returning a duplicate verdict for bytes that were
        never committed, which would strand the athlete's file as a permanent
        no-op, or returning ``accepted``, which would hide the real state.
        """

        resolved = resolve_uncertain(
            self.owner, sha256_digest(synthetic_original(99))
        )

        self.assertIsNotNone(resolved)
        self.assertIs(resolved.disposition, Disposition.REJECTED)
        self.assertEqual(resolved.reason_code, "NOTHING_COMMITTED")
        self.assertFalse(resolved.created_original)

    # -- TC03.3 P3 exact-tuple quarantine ------------------------------------

    def test_byte_different_files_with_an_identical_tuple_are_quarantined(self) -> None:
        """P3: the two byte-different files sharing one exact logical tuple.

        Mutation that fails: comparing on bytes only (the rejected option A),
        which accepts the second file and leaves the athlete with two activities
        from one session and nothing anywhere saying otherwise.
        """

        self.submit(self.owner, 1)
        conflict = self.submit(self.owner, 2)

        self.assertIs(conflict.disposition, Disposition.QUARANTINED_CONFLICT)
        self.assertEqual(conflict.rule, "P3")
        self.assertTrue(conflict.created_original, "the valid original must be kept")
        self.assertEqual(conflict.activity.disposition, Activity.QUARANTINED)
        self.assertIsNotNone(conflict.quarantine)
        self.assertIs(conflict.quarantine.state, Quarantine.STATE_QUARANTINED)
        self.assertEqual(conflict.quarantine.reason_code, "LOGICAL_TUPLE_CONFLICT")
        self.assertEqual(conflict.import_record.status, Import.CONFLICT)

        # Both valid originals survive, unmerged and unmutated.
        self.assertEqual(SourceObject.objects.for_owner(self.owner.pk).count(), 2)
        self.assertEqual(
            self.store.get(self.owner.pk, sha256_digest(synthetic_original(1))),
            synthetic_original(1),
        )
        self.assertEqual(
            self.store.get(self.owner.pk, sha256_digest(synthetic_original(2))),
            synthetic_original(2),
        )

    def test_a_quarantined_candidate_is_excluded_from_history_and_snapshots(self) -> None:
        """The exclusion is structural, so it cannot be forgotten by a caller.

        Mutation that fails: dropping the ``disposition`` filter from ``history``
        or from ``build_snapshot_scope``. The candidate would then be counted in
        the athlete's volume and in a skill snapshot, which section 9 rule 3 and
        D01 both forbid. This test fails loudly on that mutation, and the
        exclusion is also visible in ``excluded_count``/``exclusions`` rather
        than being silent.
        """

        self.submit(self.owner, 1)
        conflict = self.submit(self.owner, 2)

        self.assertEqual(list(history(self.owner)).__len__(), 1)
        self.assertEqual(list(excluded_candidates(self.owner)).__len__(), 1)
        self.assertEqual(list(open_conflicts(self.owner)).__len__(), 1)
        self.assertTrue(conflict.is_excluded_from_history)
        self.assertFalse(conflict.counts_toward_volume())

        snapshot = build_snapshot_scope(
            self.owner,
            scope_kind="training_volume",
            scope_start_utc=BASE_START - timedelta(days=1),
            scope_end_utc=BASE_START + timedelta(days=1),
            policy_version="synthetic-policy/1",
            mapping_reference="synthetic-mapping/1",
            preparation_version="synthetic-preparation/1",
        )

        self.assertEqual(snapshot.included_count, 1)
        self.assertEqual(snapshot.excluded_count, 1)
        self.assertNotIn(str(conflict.activity.pk), snapshot.included_activity_ids)
        self.assertNotIn(
            conflict.activity.source_object.digest, snapshot.included_digests
        )
        self.assertEqual(len(snapshot.exclusions), 1)
        self.assertEqual(snapshot.exclusions[0]["reason"], "LOGICAL_TUPLE_CONFLICT")

    def test_the_same_tuple_does_not_grow_an_unbounded_candidate_set(self) -> None:
        """P4: a repeated re-export links instead of fanning out.

        Mutation that fails: treating every byte-different submission for a
        quarantined tuple as a new candidate. Repeated re-exports of one
        activity would grow the candidate set without bound, and the athlete
        would face an ever-growing list of identical decisions.
        """

        self.submit(self.owner, 1)
        first_candidate = self.submit(self.owner, 2)
        second_candidate = self.submit(self.owner, 3)

        self.assertEqual(first_candidate.rule, "P3")
        self.assertEqual(second_candidate.rule, "P4")
        self.assertTrue(second_candidate.created_original, "the original is retained")
        self.assertFalse(
            second_candidate.created_activity, "P4 must not create a second candidate"
        )
        self.assertEqual(
            Activity.objects.for_owner(self.owner.pk)
            .filter(disposition=Activity.QUARANTINED)
            .count(),
            1,
        )
        self.assertEqual(
            tuple_group_key(first_candidate.logical_tuple),
            tuple_group_key(second_candidate.logical_tuple),
        )
        group = second_candidate.quarantine.candidate_normalized_payload["conflict_group"]
        self.assertEqual(group["primary_quarantine_id"], str(first_candidate.quarantine.pk))
        self.assertEqual(len(list(history(self.owner))), 1)

    def test_resubmitting_the_quarantined_bytes_cannot_flip_it_to_accepted(self) -> None:
        """P2: a retry cannot release a quarantine.

        Mutation that fails: matching on bytes and then recomputing the
        disposition from scratch, which would let an exact retry of a quarantined
        file take the accepted path and silently publish a conflict.
        """

        self.submit(self.owner, 1)
        conflict = self.submit(self.owner, 2)
        replay = self.submit(self.owner, 2)

        self.assertIs(replay.disposition, Disposition.DUPLICATE_OF_QUARANTINED)
        self.assertEqual(replay.rule, "P2")
        self.assertEqual(replay.quarantine.pk, conflict.quarantine.pk)
        self.assertEqual(replay.quarantine.state, Quarantine.STATE_QUARANTINED)
        self.assertEqual(Activity.objects.for_owner(self.owner.pk).count(), 2)
        self.assertEqual(list(history(self.owner)).__len__(), 1)

    # -- TC03.4 the critical negative: no tolerance, ever --------------------

    def test_a_near_match_within_any_plausible_tolerance_is_not_merged(self) -> None:
        """One second, one millisecond and one sport code apart are all distinct.

        This is the negative that matters most. A fuzzy matcher passing here is a
        defect, not a feature: it merges two genuinely different activities or
        discards one, and no user action can undo it -- every other failure mode
        in this policy is recoverable by an explicit resolution.

        Mutation that fails: any window, epsilon or rounding in
        ``find_exact_tuple_match`` -- a ``__gte``/``__lte`` range on the start
        instant, a percentage on the duration, or a same-sport-only comparison.
        """
        self.submit(self.owner, 1)

        one_second_later = self.submit(
            self.owner, 2, base_facts(session_start_utc=BASE_START + timedelta(seconds=1))
        )
        one_ms_longer = self.submit(
            self.owner, 3, base_facts(elapsed_duration_ms=3_723_001)
        )
        one_ms_shorter = self.submit(
            self.owner, 4, base_facts(elapsed_duration_ms=3_722_999)
        )
        different_sport = self.submit(self.owner, 5, base_facts(sport_code=2))

        for outcome in (one_second_later, one_ms_longer, one_ms_shorter, different_sport):
            self.assertIs(
                outcome.disposition,
                Disposition.ACCEPTED,
                f"a near-match was not treated as distinct: {outcome.rule}",
            )
            self.assertEqual(outcome.activity.disposition, Activity.PUBLISHED)
            self.assertEqual(outcome.quarantine, None)
            self.assertEqual(len(open_conflicts(self.owner)), 0)

        self.assertEqual(list(history(self.owner)).__len__(), 5)
        self.assertEqual(
            SourceObject.objects.for_owner(self.owner.pk).count(),
            5,
            "distinct bytes must each be retained as their own immutable original",
        )

    def test_tolerance_mutation_would_have_merged_is_proven_detectable(self) -> None:
        """The negative test above is not vacuous: the wrong matcher fails it.

        A negative test that no plausible defect can fail proves nothing. This
        builds the tolerance matcher the policy rejects -- "within 5 seconds and
        1% of the duration" -- and shows that it classifies the one-second
        near-match as a conflict, which is precisely the defect the real matcher
        avoids. If a future change reintroduced a window, the same near-match
        would come back quarantined and the test above would fail.
        """

        self.submit(self.owner, 1)
        near = LogicalTuple.from_session(self.owner.pk, base_facts())
        real = LogicalTuple.from_session(
            self.owner.pk, base_facts(session_start_utc=BASE_START + timedelta(seconds=1))
        )

        def fuzzy_match(owner_id: int, candidate: LogicalTuple) -> str | None:
            """The rejected option, reproduced only to prove it is detectable."""
            window = 5  # seconds -- invented here on purpose, never in the product
            for session in Session.objects.for_owner(owner_id):
                if canonical_sport_code(session.sport, origin="test.fuzzy_match") != candidate.sport_code:
                    continue
                drift = abs(int(session.session_start_utc.timestamp()) - candidate.start_epoch_seconds)
                if drift <= window:
                    return session.sport
            return None

        # The real matcher: the exact tuple is found, the one-second drift is not.
        self.assertIsNotNone(find_exact_tuple_match(self.owner.pk, near))
        self.assertIsNone(find_exact_tuple_match(self.owner.pk, real))

        # The rejected tolerance matcher: it does match the one-second drift,
        # which is the defect the real matcher above avoids.
        self.assertIsNotNone(
            fuzzy_match(self.owner.pk, real),
            "the rejected tolerance matcher matched a one-second difference, so the "
            "negative test above does discriminate",
        )

    def test_there_is_no_tolerance_parameter_to_configure(self) -> None:
        """Section 7: nothing to set incorrectly, and the check still works.

        Mutation that fails: adding a ``tolerance_seconds`` or ``threshold``
        parameter to any public callable, which would reintroduce an invented
        threshold. The second half proves the detector is not vacuous by planting
        such a parameter and confirming it is found.
        """

        assert_no_tolerance_parameters()
        self.assertEqual(tolerance_parameters(), {})

        # Planting a parameter the detector must notice proves the check is not
        # vacuously satisfied by a broken introspection.
        dedup.probe_with_tolerance = lambda tolerance_seconds=5: None
        try:
            self.assertIn("tolerance_seconds", str(tolerance_parameters()))
        finally:
            del dedup.probe_with_tolerance
        self.assertEqual(tolerance_parameters(), {})

    def test_the_tuple_key_still_has_exactly_the_four_canonical_integers(self) -> None:
        """The other route to a tolerance: widening or softening the key.

        Mutation that fails: adding a component, dropping the owner, or making
        any component a float or a string, which would make ``1`` and ``1.0`` or
        ``"1"`` compare equal by coercion.
        """

        self.assertEqual(
            tuple(LogicalTuple.__dataclass_fields__),
            ("owner_id", "sport_code", "start_epoch_seconds", "elapsed_duration_ms"),
        )
        for field_def in LogicalTuple.__dataclass_fields__.values():
            self.assertEqual(field_def.type, "int", f"{field_def} is not an exact integer")

    def test_a_sub_second_start_instant_is_refused_rather_than_truncated(self) -> None:
        """Section 6 compares whole epoch seconds, so a sub-second instant is a defect.

        Mutation that fails: truncating or rounding a sub-second instant to fit
        the canonical key. Two activities 400 ms apart would then share a tuple
        and be quarantined against each other, or one would overwrite the other.
        """

        with self.assertRaises(ValueError):
            base_facts(session_start_utc=BASE_START.replace(microsecond=400000))
        with self.assertRaises(ValueError):
            base_facts(session_start_utc=BASE_START.replace(tzinfo=None))
        with self.assertRaises(TypeError):
            base_facts(elapsed_duration_ms=3_723_000.0)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            canonical_sport_code(99, origin="test")

    def test_sub_sport_is_not_a_tuple_component(self) -> None:
        """Section 6: a re-export changing only sub-sport still conflicts.

        Mutation that fails: adding sub-sport to the key, which would let a
        re-classified export slip past the conflict check. The conservative
        direction is the correct one.
        """

        facts = base_facts()
        self.assertEqual(
            LogicalTuple.from_session(self.owner.pk, facts).as_dict()["sub_sport_is_a_component"],
            False,
        )
        self.assertNotIn("sub_sport", LogicalTuple.__dataclass_fields__)

    # -- TC03.5 two-identity isolation at the storage/access layer -----------

    def test_identical_bytes_of_another_identity_are_not_a_duplicate(self) -> None:
        """P1 is owner-scoped: no hit, no count, and no distinct error.

        Mutation that fails: looking the digest up without scoping it to the
        owner. Identity B would then be told its file is a duplicate of A's
        activity, which discloses that A holds the same bytes and would make B's
        own activity disappear into someone else's.
        """

        owner_first = self.submit(self.owner, 1)

        other_outcome = self.submit(self.other, 1)
        self.assertIs(other_outcome.disposition, Disposition.ACCEPTED)
        self.assertEqual(other_outcome.rule, "P5")
        self.assertNotEqual(other_outcome.activity.pk, owner_first.activity.pk)

        self.assertEqual(Activity.objects.for_owner(self.owner.pk).count(), 1)
        self.assertEqual(Activity.objects.for_owner(self.other.pk).count(), 1)
        self.assertEqual(list(history(self.owner)).__len__(), 1)
        self.assertEqual(list(history(self.other)).__len__(), 1)

        # The identical-digest case must look exactly like the ordinary accept
        # case, so nothing about the other identity is disclosed.
        stranger_outcome = self.submit(self.stranger, 1)
        self.assertEqual(stranger_outcome.disposition, Disposition.ACCEPTED)
        self.assertEqual(outcome_text(stranger_outcome), outcome_text(other_outcome))

    def test_swapping_the_owner_identifier_fails_at_every_access_layer(self) -> None:
        """No layer answers a substituted identity with the real owner's data.

        Mutation that fails: any access path that filters by a record id without
        also constraining the owner, or that falls back to an unscoped read
        after a denial.
        """

        self.submit(self.owner, 1)
        mine = Activity.objects.for_owner(self.owner.pk).first()
        mine_source = mine.source_object

        self.assertEqual(list(history(self.other)), [])
        self.assertEqual(list(excluded_candidates(self.other)), [])
        self.assertEqual(list(open_conflicts(self.other)), [])

        with self.assertRaises(Activity.DoesNotExist):
            Activity.objects.for_owner(self.stranger.pk).get(source_object=mine_source)
        with self.assertRaises(ResourceNotVisible):
            self.store.get(self.stranger.pk, mine_source.digest)

        resolved = resolve_uncertain(self.stranger, mine_source.digest)
        self.assertIsNotNone(resolved)
        self.assertIs(resolved.disposition, Disposition.REJECTED)
        self.assertEqual(resolved.reason_code, "NOTHING_COMMITTED")
        self.assertEqual(describe_reference(self.stranger, mine_source.digest), "REFERENCE_UNAVAILABLE")

    def test_a_deleted_reference_reports_unavailable_and_resurrects_nothing(self) -> None:
        """P7: a superseded or deleted original is reported, never brought back.

        Mutation that fails: recreating the original on reference, or returning
        the bytes of a deleted original from the store.
        """

        self.submit(self.owner, 1)
        source = SourceObject.objects.for_owner(self.owner.pk).first()
        self.assertEqual(describe_reference(self.owner, source.digest), "available")

        source.retention_state = "deleted_by_owner"
        source.deleted_at = datetime.now(timezone.utc)
        source.save()

        self.assertEqual(describe_reference(self.owner, source.digest), "REFERENCE_UNAVAILABLE")
        self.assertEqual(SourceObject.objects.for_owner(self.owner.pk).count(), 1)

    # -- TC22 / SR33 presentation vocabulary ---------------------------------

    def test_the_three_states_carry_required_content_and_no_prohibited_wording(self) -> None:
        """Section 9: required content present, prohibited wording absent.

        Mutation that fails: any wording change that implies a merge, an
        automatic overwrite, or certainty the system does not have -- for
        example saying the two files "are certainly the same session", or
        calling a conflict a "duplicate activity".
        """

        self.submit(self.owner, 1)
        accepted = self.submit(self.owner, 4, base_facts(session_start_utc=BASE_START + timedelta(days=2)))
        duplicate = self.submit(self.owner, 1)
        conflict = self.submit(self.owner, 2)

        texts = {
            "accepted": outcome_text(accepted, submitted_file_name="a.fit"),
            "duplicate": outcome_text(duplicate, submitted_file_name="b.fit"),
            "conflict": outcome_text(conflict, submitted_file_name="c.fit"),
        }
        self.assertEqual(len(set(texts.values())), 3, "the three states must differ in words")

        for label, text in texts.items():
            lowered = text.lower()
            for phrase in dedup.PROHIBITED_CONFLICT_WORDING:
                self.assertNotIn(phrase, lowered, f"{label} text contains {phrase!r}")

        self.assertIn("may be the same activity", texts["conflict"])
        self.assertIn("three options", texts["conflict"])
        for option in ("Keep the existing activity", "supersession", "keep both"):
            self.assertIn(option, texts["conflict"])
        self.assertIn("excluded", texts["conflict"].lower())
        self.assertIn("every skill snapshot", texts["conflict"])

        self.assertIn("references an activity you already have", texts["duplicate"])
        self.assertIn("not a further activity", texts["duplicate"])
        self.assertIn("not counted again", texts["duplicate"])

    def test_an_unresolved_candidate_is_never_counted_or_totalled(self) -> None:
        """Section 9 rule 3 as a property, not as a wording promise.

        Mutation that fails: including quarantined rows in a total. The text
        would still read correctly while the number was wrong, which is why this
        checks the counts rather than the string.
        """

        self.submit(self.owner, 1)
        self.submit(self.owner, 2)
        self.submit(self.owner, 3)

        included = list(history(self.owner))
        self.assertEqual(len(included), 1)
        total_ms = sum(item.elapsed_duration_ms for item in included)
        self.assertEqual(
            total_ms, 3_723_000, "a quarantined candidate was counted toward volume"
        )
        for item in history(self.owner):
            self.assertEqual(item.activity.disposition, Activity.PUBLISHED)

    # -- binding architectural condition --------------------------------------

    def test_no_persisted_entity_stores_a_skill_against_model_outcome(self) -> None:
        """The exclusion is semantic; these are the machine-checkable parts of it.

        Mutation that fails: adding a ``Run``/``Assessment``/``Finding``/
        ``Result`` model, or a mutable ``latest_*``/``current_*`` pointer column.
        The names below are the explicit list from the decision register; the
        pointer check is the structural half, since a pointer is a defect by
        meaning regardless of what it is called.
        """

        persisted = {model.__name__ for model in MILESTONE_A_MODELS}
        self.assertEqual(
            persisted,
            {
                "Import",
                "SourceObject",
                "Activity",
                "Session",
                "Snapshot",
                "Eligibility",
                "Evidence",
                "Quarantine",
                "Metric",
                "MetricOperand",
                "MetricSeal",
            },
        )
        for forbidden in (
            "Run",
            "SelectedSkillExecution",
            "Attempt",
            "Assessment",
            "AssessmentResult",
            "Finding",
            "Result",
            "Connection",
            "SkillDefinition",
        ):
            self.assertNotIn(forbidden, persisted)

        for model in MILESTONE_A_MODELS:
            for field in model._meta.get_fields():
                name = getattr(field, "name", "")
                self.assertFalse(
                    name.startswith("latest_") or name.startswith("current_"),
                    f"{model.__name__}.{name} is a mutable latest-value pointer",
                )

    def test_the_write_path_refuses_an_outcome_shaped_payload_field(self) -> None:
        """Defence in depth: a caller cannot smuggle an outcome through a payload.

        Mutation that fails: dropping the allowlist so any column name could be
        written. The schema is the real guarantee, but this makes the semantic
        exclusion fail loudly at the write boundary too.
        """

        with self.assertRaises(AssertionError):
            assert_no_outcome_fields({**BASE_PAYLOAD, "latest_result": "x"})
        with self.assertRaises(AssertionError):
            assert_no_outcome_fields({**BASE_PAYLOAD, "model_verdict": "x"})
        with self.assertRaises(ValueError):
            self.submit(self.owner, 1, payload={**BASE_PAYLOAD, "skill_version": "s/1"})

    def test_history_is_queryable_and_offers_no_latest_pointer(self) -> None:
        """History is append-only and queried; there is no "latest" shortcut.

        Mutation that fails: adding a cached latest-result accessor. Reading
        history through a mutable pointer is the defect the binding condition
        names, so the API must not grow one.
        """

        self.assertFalse(hasattr(dedup, "latest_result"))
        self.assertFalse(hasattr(dedup, "latest"))
        for name in dir(dedup):
            self.assertFalse(
                name.startswith("latest_") or name.startswith("current_"),
                f"dedup exposes a latest-value pointer: {name}",
            )


# ---------------------------------------------------------------------------
# B3: one column, one unit, and a comparison that cannot silently miss.
#
# The harm the review identified is a *silent duplicate accept*, not a false
# conflict: ``Session.elapsed_duration_seconds`` was written in seconds by TK18
# and in milliseconds by TK15, and ``find_exact_tuple_matches`` compared the
# seconds column against a millisecond candidate. A 30-minute run was stored as
# 1800 by one path and 1800000 by the other, so the exact comparison reported two
# different activities and the same activity was accepted again.
# ``PositiveBigIntegerField`` accepts both values, so nothing objected.
# ---------------------------------------------------------------------------


class CanonicalUnitTests(ConflictTestCase):
    """The column, its name and its two write sites now agree."""

    def test_the_persisted_duration_is_milliseconds(self) -> None:
        """The write site stores the canonical unit under a name that states it.

        Mutation that fails: write the seconds value into ``elapsed_duration_ms``
        -- this assertion fails.
        """

        self.submit(self.owner, 1)
        session = Session.objects.for_owner(self.owner.pk).get()
        self.assertEqual(session.elapsed_duration_ms, 3_723_000)

    def test_the_same_activity_is_never_accepted_twice(self) -> None:
        """The regression itself, exercised through the precedence table.

        With one column in one unit, a second submission carrying different bytes
        but the same logical activity reaches P3 and is quarantined. Before the
        fix the comparison compared 3723 against 3_723_000, found no match, and
        P5 accepted a second *published* copy of the same run.

        P3 keeps the candidate as a valid original in quarantined scope, so a
        ``Session`` row exists for it by design -- that is the ratified P3/P4
        deviation and this test does not touch it. What must not exist is a
        second *published* activity, and the candidate must not count toward
        history.

        Mutation that fails: store seconds in ``elapsed_duration_ms`` -- the
        second submission is then ACCEPTED under P5, two activities are PUBLISHED
        and history counts two.
        """

        first = self.submit(self.owner, 1)
        self.assertIs(first.disposition, Disposition.ACCEPTED)
        self.assertEqual(first.rule, "P5")

        again = self.submit(self.owner, 2)
        self.assertIs(again.disposition, Disposition.QUARANTINED_CONFLICT)
        self.assertEqual(again.rule, "P3")
        self.assertEqual(
            Activity.objects.for_owner(self.owner.pk)
            .filter(disposition=Activity.PUBLISHED)
            .count(),
            1,
            "the same activity was published a second time",
        )
        self.assertEqual(len(list(history(self.owner))), 1)
        self.assertFalse(again.counts_toward_volume())

    def test_the_write_site_refuses_a_unit_it_was_not_declared_with(self) -> None:
        """The unit guard is code at this write site too, not only on TK18's.

        Mutation that fails: pass ``unit=SECONDS_UNIT``, or drop the
        ``require_elapsed_duration_ms`` call -- nothing is raised.
        """

        with self.assertRaises(TypeError) as caught:
            require_elapsed_duration_ms(3_723_000, origin="test", unit=SECONDS_UNIT)
        self.assertIn("elapsed_duration_ms_from_seconds", str(caught.exception))

    def test_the_facts_refuse_the_representations_that_caused_the_defect(self) -> None:
        """`SessionFacts` declares the unit, so a float or an out-of-domain count
        never reaches the column.

        Note what is *not* asserted here: ``base_facts(elapsed_duration_ms=3723)``
        is accepted, because 3723 ms is a legitimate 3.7 second duration. A bare
        integer carries no unit, so no check can tell 3723 intended as
        milliseconds from 3723 intended as seconds -- claiming otherwise would be
        a fake control. What is enforced is the declared unit at the write site
        (the previous test), the type, and the domain.

        Mutation that fails: drop the ``require_elapsed_duration_ms`` call from
        ``SessionFacts.__post_init__`` -- neither assertion below raises.
        """

        with self.assertRaises(TypeError):
            base_facts(elapsed_duration_ms=3_723_000.0)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            base_facts(elapsed_duration_ms="3723000")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            base_facts(elapsed_duration_ms=0)
        with self.assertRaises(ValueError):
            base_facts(elapsed_duration_ms=86_400_001)
        # A legal value in the canonical unit is accepted, so the guard is not
        # simply refusing everything.
        self.assertEqual(base_facts().elapsed_duration_ms, 3_723_000)

    def test_the_database_refuses_a_seconds_count_in_the_column(self) -> None:
        """The schema guard, so a future writer bypassing the helpers is caught.

        Mutation that fails: drop the ``CheckConstraint`` on ``Session`` -- the
        insert below succeeds and no ``IntegrityError`` is raised.
        """

        activity = self.submit(self.owner, 1).activity
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Session.objects.create(
                    owner_id=self.owner.pk,
                    activity=activity,
                    session_index=1,
                    session_count=1,
                    sport="running",
                    session_start_utc=BASE_START,
                    elapsed_duration_ms=3723,  # seconds, not milliseconds
                )


class ToleranceOperatorTests(SimpleTestCase):
    """The comparison operator is checked, not only the parameter name."""

    def test_the_name_check_says_it_is_only_a_name_check(self) -> None:
        """It is a token check and the code now says so.

        Mutation that fails: restore the old claim in the docstring -- the
        ``assertIn`` below is what fails, which is how the overstatement about
        ``delta_ms`` / ``precision_s`` / ``bucket_s`` stops being invisible.
        """

        self.assertNotIn("delta_ms", dedup.TOLERANCE_PARAMETER_TOKENS)
        self.assertIn("name", (dedup.tolerance_parameters.__doc__ or "").lower())
        self.assertEqual(
            dedup.ordering_comparisons(),
            {},
            "the real module source must contain no ordering comparison of a "
            "tuple component",
        )

    def test_an_unnamed_tolerance_operator_is_detected(self) -> None:
        """The check the name check cannot do.

        ``delta_ms`` carries no tolerance token, and ``abs(a - b) <= 5`` names no
        parameter at all. Both are refused, because both compare a value that
        must match exactly with an operator other than ``==`` / ``!=``.

        Mutation that fails: change ``ordering_comparisons`` to look only at
        parameter names -- all three planted sources report zero findings.
        """

        planted = {
            "unnamed_window": (
                "def match(a, b, delta_ms):\n"
                "    return abs(a - b) <= delta_ms\n"
            ),
            "ordering_on_a_component": (
                "def near(session, candidate):\n"
                "    return session.elapsed_duration_ms <= candidate.elapsed_duration_ms\n"
            ),
            "bucketing": (
                "def bucket(duration):\n"
                "    return round(duration / 1000)\n"
            ),
        }
        for label, source in planted.items():
            with self.subTest(planted=label):
                self.assertTrue(
                    dedup.ordering_comparisons(source),
                    f"{label} is a tolerance and was not detected",
                )

    def test_exact_equality_is_not_flagged(self) -> None:
        """The check is not vacuous in the other direction.

        Mutation that fails: flag every comparison -- this fails.
        """

        exact = (
            "def same(session, candidate):\n"
            "    return session.elapsed_duration_ms == candidate.elapsed_duration_ms\n"
        )
        self.assertEqual(dedup.ordering_comparisons(exact), {})

    def test_assert_no_tolerance_parameters_runs_the_operator_check(self) -> None:
        """Wiring: the two checks are not independent decorations.

        Mutation that fails: drop the ``ordering_comparisons()`` call from
        ``assert_no_tolerance_parameters`` -- the poisoned source below then
        raises nothing.
        """

        original = dedup.ordering_comparisons
        dedup.ordering_comparisons = lambda *a, **k: {"line 1: x": ["planted"]}
        try:
            with self.assertRaises(AssertionError) as caught:
                dedup.assert_no_tolerance_parameters()
            self.assertIn("non-exact comparison", str(caught.exception))
        finally:
            dedup.ordering_comparisons = original
        dedup.assert_no_tolerance_parameters()