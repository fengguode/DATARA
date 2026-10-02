"""Two-identity isolation and the machine-checked binding condition.

Two things are proven here, and both are proven by making the check fail on
purpose as well as by having it pass:

1. **Owner isolation at the data-access layer.** A store bound to identity B
   cannot read identity A's activity, snapshot or evidence, cannot list it, and
   cannot be persuaded by passing A's identifier. The denial is a generic
   not-found, so it does not confirm that the object exists.
2. **The binding architectural condition.** The live database schema, the model
   metadata and the package source contain no entity whose meaning is the outcome
   of executing a skill against a model, and no mutable "latest result" pointer.
   `test_schema_guard_detects_a_real_violation_when_one_exists` creates a real
   violating table in the test database and shows the guard reporting it, so the
   passing assertion is known to be capable of failing.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase

from datara.db import (
    FORBIDDEN_ENTITY_NAMES,
    OwnerScope,
    OwnerScopedStore,
    SchemaFacts,
    find_forbidden_schema_entities,
    introspect_persisted_schema,
)
from datara.models import (
    Activity,
    Evidence,
    Import,
    ImmutabilityViolation,
    OwnerScopeNotBound,
    ResourceNotVisible,
    SourceObject,
)
from datara.normalization import (
    RawActivityInput,
    evaluate_eligibility,
    normalize,
    prepare_snapshot,
)

from datara.tests.test_normalization import (
    ONE_ACTIVITY_REQUIREMENT,
    SYNTHETIC_COMPLETE_RAW,
    SYNTHETIC_POLICY,
)


def _seed(owner, digest_tail: str, sport: str):
    """Write one accepted normalized activity for ``owner`` through the store."""
    store = OwnerScopedStore.for_user(owner)
    raw = RawActivityInput(
        source_digest="sha256:" + digest_tail * 32,
        sport=sport,
        session_start_utc="2026-10-01T06:30:00Z",
        elapsed_duration_seconds=3600,
        record_sample_count=1800,
    )
    normalized = normalize(raw, SYNTHETIC_POLICY)
    source = store.record_source_object(
        digest=raw.source_digest,
        byte_length=2048,
        storage_reference=f"synthetic/owner-scoped/{digest_tail}",
        media_type="application/vnd.datara.synthetic",
    )
    import_record = store.record_import(source_digest=raw.source_digest, status="accepted")
    activity = store.record_normalized_activity(
        source_object=source, import_record=import_record, normalized=normalized
    )
    preparation = prepare_snapshot(
        normalized=[normalized], excluded=[], policy=SYNTHETIC_POLICY, scope_kind="synthetic_isolation"
    )
    snapshot = store.record_snapshot(preparation, [activity.activity_id])
    evidence = store.record_evidence(
        snapshot,
        kind=Evidence.KIND_SOURCE_RECORD,
        source_object_ref=str(source.source_object_id),
        activity_ref=str(activity.activity_id),
        field_path="session.elapsed_duration_seconds",
        value_canonical="3600",
    )
    return store, activity, snapshot, evidence


class TwoIdentityIsolationTests(TestCase):
    """CUS10, SR20-SR21. Two disposable identities; the founder's own data is not used."""

    def setUp(self) -> None:
        user_model = get_user_model()
        self.owner_a = user_model.objects.create_user(username="tk18-owner-a", password="x")
        self.owner_b = user_model.objects.create_user(username="tk18-owner-b", password="x")
        self.store_a, self.activity_a, self.snapshot_a, self.evidence_a = _seed(
            self.owner_a, "ab", "running"
        )
        self.store_b = OwnerScopedStore.for_user(self.owner_b)

    def test_each_identity_reads_its_own_record(self) -> None:
        """Positive control: the denial below is not an empty-store artifact."""
        found = self.store_a.get_activity(self.activity_a.activity_id)
        self.assertEqual(found.owner_id, self.owner_a.pk)
        self.assertEqual(found.owner_id, self.store_a.scope.owner_id)
        self.assertEqual(self.store_a.count_activities(), 1)

    def test_swapping_the_owner_denies_the_other_identitys_resource(self) -> None:
        for getter, resource in (
            ("get_activity", self.activity_a.activity_id),
            ("get_snapshot", self.snapshot_a.snapshot_id),
            ("get_evidence", self.evidence_a.evidence_id),
            ("get_source_object", self.activity_a.source_object_id),
            ("get_session", self.activity_a.activity_id),
        ):
            with self.subTest(resource=getter):
                with self.assertRaises(ResourceNotVisible):
                    getattr(self.store_b, getter)(resource)

    def test_a_denied_read_reveals_nothing_about_the_other_identity(self) -> None:
        with self.assertRaises(ResourceNotVisible) as caught:
            self.store_b.get_activity(self.activity_a.activity_id)
        with self.assertRaises(ResourceNotVisible) as absent:
            self.store_b.get_activity("00000000-0000-0000-0000-000000000000")
        # Identical class and identical shape of message whether the row exists
        # or not: the denial does not confirm that the object exists.
        self.assertEqual(type(caught.exception), type(absent.exception))
        prefix = "resource not available: datara.Activity "
        self.assertTrue(str(caught.exception).startswith(prefix))
        self.assertTrue(str(absent.exception).startswith(prefix))
        self.assertIn(str(self.activity_a.activity_id), str(caught.exception))
        self.assertNotIn(str(self.activity_a.activity_id), str(absent.exception))
        for leak in ("running", self.owner_a.username, "synthetic", "3600"):
            self.assertNotIn(leak, str(caught.exception))

    def test_identity_b_sees_no_rows_and_no_counts(self) -> None:
        self.assertEqual(self.store_b.count_activities(), 0)
        self.assertEqual(self.store_b.list_activities(), [])
        with self.assertRaises(ResourceNotVisible):
            self.store_b.get_snapshot(self.snapshot_a.snapshot_id)
        with self.assertRaises(ResourceNotVisible):
            self.store_b.list_eligibility_for_snapshot(self.snapshot_a.snapshot_id)

    def test_a_rewrite_through_identity_b_is_refused(self) -> None:
        """A store must not be able to write into another identity's chain."""
        # `unbound()` is the documented maintenance accessor; a test forging a
        # cross-owner reference is the one legitimate use.
        with self.assertRaises(ResourceNotVisible):
            self.store_b.record_normalized_activity(
                source_object=SourceObject.objects.unbound().get(pk=self.activity_a.source_object_id),
                import_record=Import.objects.unbound().get(pk=self.activity_a.import_record_id),
                normalized=normalize(
                    RawActivityInput(
                        source_digest="sha256:" + "ff" * 32,
                        sport="running",
                        session_start_utc="2026-10-01T06:30:00Z",
                        elapsed_duration_seconds=3600,
                    ),
                    SYNTHETIC_POLICY,
                ),
            )

    def test_owner_scope_requires_an_authenticated_principal(self) -> None:
        from django.contrib.auth.models import AnonymousUser

        with self.assertRaises(ValueError):
            OwnerScope.for_authenticated_user(AnonymousUser())
        with self.assertRaises(ValueError):
            OwnerScope.for_authenticated_user(None)

    def test_unscoped_orm_reads_are_refused_rather_than_returning_everything(self) -> None:
        # The stored row exists and the maintenance accessor can prove it.
        self.assertEqual(
            Activity.objects.unbound().filter(pk=self.activity_a.activity_id).count(), 1
        )
        with self.assertRaises(OwnerScopeNotBound):
            Activity.objects.all()
        with self.assertRaises(OwnerScopeNotBound):
            Activity.objects.for_owner(None)
        # The manager defaults to deny: an unbound read returns nothing, not the
        # other identity's row.
        self.assertEqual(Activity.objects.get_queryset().count(), 0)
        self.assertEqual(len(Activity.objects.get_queryset()), 0)

    def test_a_scoped_queryset_filters_on_the_owner_column(self) -> None:
        """The filter is real, not a post-hoc in-memory check."""
        queryset = Activity.objects.for_owner(self.owner_b.pk)
        sql, params = queryset.query.sql_with_params()
        self.assertIn("owner_id", sql)
        self.assertIn(self.owner_b.pk, list(params))
        self.assertNotIn(self.owner_a.pk, list(params))
        self.assertEqual(queryset.count(), 0)


class BindingConditionTests(TestCase):
    """No skill-against-model outcome, under any name, and no mutable pointer."""

    def test_the_persisted_schema_contains_no_forbidden_entity(self) -> None:
        facts = introspect_persisted_schema()
        violations = find_forbidden_schema_entities(facts)
        self.assertEqual(
            violations,
            (),
            "binding architectural condition violated: "
            + "; ".join(str(v) for v in violations),
        )

    def test_the_authorized_persistence_set_is_the_whole_set(self) -> None:
        """The Milestone A set is exactly the four record groups plus three."""
        facts = introspect_persisted_schema()
        datara_tables = sorted(
            table for table in facts.table_names if table.startswith("datara_")
        )
        self.assertEqual(
            datara_tables,
            [
                "datara_activity",
                "datara_eligibility",
                "datara_evidence",
                "datara_import",
                "datara_quarantine",
                "datara_session",
                "datara_snapshot",
                "datara_source_object",
            ],
        )

    def test_the_guard_returns_the_other_value_for_a_violating_schema(self) -> None:
        """Control A: a synthetic fact set containing a forbidden name is caught."""
        facts = SchemaFacts(
            table_names=("datara_assessment",),
            columns=(("datara_assessment", "id"), ("datara_activity", "latest_result")),
            model_names=("Activity", "Finding"),
            field_names=(("Activity", "sport"), ("Run", "latest_result")),
            module_symbols=("Activity", "Assessment"),
        )
        violations = find_forbidden_schema_entities(facts)
        reported = {(v.kind, v.name) for v in violations}
        self.assertIn(("model", "Finding"), reported)
        self.assertIn(("table", "assessment"), reported)
        self.assertIn(("column", "latest_result"), reported)
        self.assertIn(("field", "latest_result"), reported)
        self.assertIn(("module_symbol", "Assessment"), reported)

    def test_every_forbidden_name_is_actually_detected(self) -> None:
        """Control B: no name in the founder's list silently passes the check."""
        for name in FORBIDDEN_ENTITY_NAMES:
            with self.subTest(name=name):
                facts = SchemaFacts(
                    table_names=(),
                    columns=(),
                    model_names=(name,),
                    field_names=(),
                    module_symbols=(),
                )
                self.assertEqual(
                    [v.kind for v in find_forbidden_schema_entities(facts)], ["model"]
                )

    def test_the_schema_guard_detects_a_real_violation_when_one_exists(self) -> None:
        """Control C: a real violating table in the live test database is caught."""
        self.assertEqual(find_forbidden_schema_entities(introspect_persisted_schema()), ())
        table = "datara_assessment"
        column = "latest_result"
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE TABLE {table} (id integer NOT NULL PRIMARY KEY, {column} varchar(64) NULL)"
            )
        try:
            facts = introspect_persisted_schema()
            violations = find_forbidden_schema_entities(facts)
            reported = {(v.kind, v.name) for v in violations}
            self.assertIn(("table", "assessment"), reported)
            self.assertIn(("column", column), reported)
            self.assertEqual(len(violations), 2)
        finally:
            with connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE {table}")
        # And the guard is clean again once the violation is gone, so the previous
        # failure was the violation and not a broken introspection call.
        self.assertEqual(find_forbidden_schema_entities(introspect_persisted_schema()), ())

    def test_mutable_pointer_names_are_refused_even_without_a_forbidden_entity(self) -> None:
        for column in ("latest_result", "latest_run", "current_value", "current_run", "snapshot_pointer"):
            facts = SchemaFacts(
                table_names=(),
                columns=(("datara_snapshot", column),),
                model_names=(),
                field_names=(),
                module_symbols=(),
            )
            with self.subTest(column=column):
                self.assertEqual(len(find_forbidden_schema_entities(facts)), 1)


class PersistedRecordTests(TestCase):
    """Structural properties of the persistence set."""

    def setUp(self) -> None:
        owner = get_user_model().objects.create_user(username="tk18-struct", password="x")
        self.store = OwnerScopedStore.for_user(owner)

    def test_evidence_refuses_a_computed_metric_until_the_field_contract_exists(self) -> None:
        owner = get_user_model().objects.get(username="tk18-struct")
        _, _, snapshot, _ = _seed(owner, "cd", "cycling")
        with self.assertRaises(ValueError) as caught:
            self.store.record_evidence(snapshot, kind=Evidence.KIND_COMPUTED_METRIC)
        self.assertIn("D02/WP02", str(caught.exception))
        self.assertEqual(
            Evidence.objects.for_owner(self.store.scope.owner_id)
            .filter(kind=Evidence.KIND_COMPUTED_METRIC)
            .count(),
            0,
        )

    def test_source_object_digest_cannot_be_rewritten(self) -> None:
        source = self.store.record_source_object(
            digest="sha256:" + "11" * 32,
            byte_length=10,
            storage_reference="synthetic/owner-scoped/immutable",
            media_type="application/vnd.datara.synthetic",
        )
        source.digest = "sha256:" + "22" * 32
        with self.assertRaises(ImmutabilityViolation) as caught:
            source.save()
        self.assertIn("immutable", str(caught.exception).lower())
        self.assertEqual(
            SourceObject.objects.for_owner(self.store.scope.owner_id)
            .get(pk=source.pk)
            .digest,
            "sha256:" + "11" * 32,
        )

    def test_a_record_cannot_be_saved_without_an_owner(self) -> None:
        with self.assertRaises(OwnerScopeNotBound):
            SourceObject(
                digest="sha256:" + "11" * 32,
                byte_length=1,
                storage_reference="synthetic/no-owner",
                media_type="application/vnd.datara.synthetic",
            ).save()

    def test_a_rejected_import_leaves_no_activity(self) -> None:
        rejected = self.store.record_import(
            source_digest="sha256:" + "33" * 32,
            status="rejected",
            reason_code="REQ_ELAPSED_DURATION_MISSING",
            reason_detail="absent",
        )
        self.assertEqual(rejected.status, "rejected")
        self.assertEqual(rejected.reason_code, "REQ_ELAPSED_DURATION_MISSING")
        self.assertEqual(
            Activity.objects.for_owner(self.store.scope.owner_id)
            .filter(import_record=rejected)
            .count(),
            0,
        )

    def test_eligibility_record_names_no_skill_version_or_model(self) -> None:
        owner = get_user_model().objects.get(username="tk18-struct")
        _, _, snapshot, _ = _seed(owner, "ef", "running")
        decision = evaluate_eligibility(
            observations={"activity_count": 0},
            requirements=ONE_ACTIVITY_REQUIREMENT,
            rule_set_version="synthetic-rule-set-1",
        )
        record = self.store.record_eligibility(snapshot, decision)
        self.assertFalse(record.eligible)
        self.assertTrue(record.rule_version)
        self.assertTrue(record.rule_set_version)
        self.assertEqual(record.snapshot_id, snapshot.snapshot_id)
        for field in record._meta.get_fields():
            if not getattr(field, "concrete", False):
                continue
            self.assertNotIn(
                field.name,
                {"skill_version", "model_id", "provider", "connection", "prompt"},
            )
