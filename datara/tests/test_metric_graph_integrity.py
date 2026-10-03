"""Direct synthetic PostgreSQL integrity regressions for WP02/WP03.

CUS03-05/CUS08/CUS10; SR05-11/SR20-21/SR28-29. No runtime result claimed.
"""
import uuid

from django.db import DatabaseError, transaction
from django.test import TransactionTestCase

from datara import models as m
from datara.metric_store import SavedMetricStore
from datara.recorded_metrics import prepare_recorded_input, summarize_recorded
from datara.scoped_input import prepare_scoped_input
from datara.tests.test_recorded_regressions import CORE
from datara.tests.test_scoped_input import _Owner, make_scope, SYNTHETIC_POLICY


class MetricGraphIntegrityRegressions(TransactionTestCase):
    def _save(self, owner, start="2026-08-31T00:00:00Z"):
        scope = make_scope(start_utc=start, end_utc="2026-10-02T00:00:00Z")
        version = prepare_scoped_input(
            scope=scope, records=owner.inputs.scope_candidates(scope, CORE),
            field_specs=CORE, policy=SYNTHETIC_POLICY)
        handle = owner.inputs.append_version(version)
        result = summarize_recorded(prepare_recorded_input(version))
        store = SavedMetricStore.for_user(owner.user)
        saved = store.save_prepared_metrics(handle.version_ref, result)
        self.assertEqual(saved.state, "complete")
        self.assertEqual(store.get_metric(saved.metric_id).canonical_content, result.canonical_content)
        return m.Metric.objects.for_owner(owner.user.pk).get(pk=saved.metric_id)

    def setUp(self):
        self.owner = _Owner("integrity-owner")
        self.other = _Owner("integrity-other")
        for owner in (self.owner, self.other):
            owner.add_accepted(start_utc="2026-09-01T06:00:00Z")
        self.original = self._save(self.owner)
        self.same_owner_other_snapshot = self._save(self.owner, "2026-09-01T00:00:00Z")
        self.foreign = self._save(self.other)
        self.store = SavedMetricStore.for_user(self.owner.user)
        self.original_bytes = self.store.get_metric(self.original.pk).canonical_content

    def _counts(self):
        # Include source history and every graph table for both synthetic users.
        return {(model.__name__, owner.user.pk): model.objects.for_owner(owner.user.pk).count()
                for model in (m.SourceObject, m.Import, m.Activity, m.Session, m.Snapshot,
                              m.Evidence, m.Metric, m.MetricOperand, m.MetricSeal)
                for owner in (self.owner, self.other)}

    def _rejected(self, action, *, message=None, constraint=None):
        counts = self._counts()
        with self.assertRaises(DatabaseError) as caught:
            with transaction.atomic():
                action()
        diagnostic = caught.exception.__cause__.diag
        if constraint:
            self.assertEqual(diagnostic.constraint_name, constraint)
        if message:
            self.assertEqual(diagnostic.message_primary, message)
        self.assertEqual(self._counts(), counts)
        self.assertEqual(self.store.get_metric(self.original.pk).canonical_content, self.original_bytes)

    @staticmethod
    def _values(row, exclude):
        return {field.attname: getattr(row, field.attname)
                for field in row._meta.concrete_fields if field.name not in exclude}

    def _parent(self, **changes):
        values = self._values(self.original, {"metric_id", "created_at", "creation_txid"})
        # DB structural tests deliberately bypass the service digest oracle.
        values["content_digest"] = "sha256:" + uuid.uuid4().hex * 2
        values.update(changes)
        return m.Metric.objects.create(**values)

    def _operand_values(self, parent):
        row = m.MetricOperand.objects.for_owner(self.owner.user.pk).filter(parent_metric=self.original).first()
        values = self._values(row, {"id"})
        values["parent_metric_id"] = parent.pk
        return values

    def test_composite_graph_references_reject_cross_owner_and_cross_snapshot(self):
        for target in (self.foreign, self.same_owner_other_snapshot):
            for kind, constraint in (
                ("parent", "datara_operand_parent_scope_fk"),
                ("source", "datara_operand_source_scope_fk"),
                ("dependency", "datara_operand_dependency_scope_fk"),
                ("evidence", "datara_evidence_metric_scope_fk"),
                ("seal", "datara_seal_parent_scope_fk"),
            ):
                with self.subTest(target=str(target.pk), kind=kind):
                    def attempt():
                        parent = self._parent()
                        if kind in {"parent", "seal", "evidence"}:
                            # Point to a fresh unsealed target in this transaction;
                            # the insert guard succeeds before the composite FK.
                            target_parent = self._parent(owner_id=target.owner_id,
                                                         snapshot_id=target.snapshot_id)
                        if kind == "seal":
                            m.MetricSeal.objects.create(owner=self.owner.user,
                                snapshot_id=self.original.snapshot_id, metric=target_parent)
                        elif kind == "evidence":
                            m.Evidence.objects.create(owner=self.owner.user,
                                snapshot_id=self.original.snapshot_id, metric=target_parent,
                                kind="computed_metric", value_path="/manifest", value_canonical="{}")
                        else:
                            values = self._operand_values(parent)
                            if kind == "parent":
                                values["parent_metric_id"] = target_parent.pk
                            elif kind == "source":
                                values["source_evidence_id"] = m.Evidence.objects.for_owner(target.owner_id).filter(
                                    snapshot_id=target.snapshot_id, kind="source_record").first().pk
                            else:
                                values.update(source_evidence_id=None, dependency_metric_id=target.pk,
                                              dependency_value_path="/manifest")
                            m.MetricOperand.objects.create(**values)
                    self._rejected(attempt, constraint=constraint)

    def test_cross_owner_snapshot_references_rejected_by_database(self):
        self._rejected(lambda: self._parent(snapshot_id=self.foreign.snapshot_id),
                       constraint="datara_metric_snapshot_scope_fk")
        source = m.Evidence.objects.for_owner(self.owner.user.pk).filter(
            snapshot_id=self.original.snapshot_id, kind="source_record").first()
        values = self._values(source, {"evidence_id"})
        values["snapshot_id"] = self.foreign.snapshot_id
        self._rejected(lambda: m.Evidence.objects.create(**values),
                       constraint="datara_evidence_snapshot_scope_fk")

    def _bundle(self, defect):
        parent = self._parent()
        operands = list(m.MetricOperand.objects.for_owner(self.owner.user.pk).filter(
            parent_metric=self.original).order_by("ordinal"))
        evidence = list(m.Evidence.objects.for_owner(self.owner.user.pk).filter(
            metric=self.original).order_by("value_path"))
        for index, row in enumerate(operands):
            if defect == "missing_operand" and index == 0:
                continue
            values = self._values(row, {"id"})
            values["parent_metric_id"] = parent.pk
            if defect == "malformed_operand" and index == 0:
                values["canonical_operand"] = "{}"
            m.MetricOperand.objects.create(**values)
        for index, row in enumerate(evidence):
            if defect == "missing_evidence" and index == 0:
                continue
            values = self._values(row, {"evidence_id"})
            values["metric_id"] = parent.pk
            if defect == "malformed_evidence" and index == 0:
                values["value_canonical"] = "{}"
            m.Evidence.objects.create(**values)
        m.MetricSeal.objects.create(owner=self.owner.user,
                                   snapshot_id=parent.snapshot_id, metric=parent)
        # All inserts succeeded; rejection must occur as the outer atomic commits.
        self.assertTrue(m.MetricSeal.objects.for_owner(self.owner.user.pk).filter(metric=parent).exists())

    def test_commit_rejects_incomplete_or_malformed_operands(self):
        for defect in ("missing_operand", "malformed_operand"):
            with self.subTest(defect=defect):
                self._rejected(lambda: self._bundle(defect),
                               message="missing extra or inconsistent operands")

    def test_commit_rejects_incomplete_or_malformed_addressed_evidence(self):
        for defect in ("missing_evidence", "malformed_evidence"):
            with self.subTest(defect=defect):
                self._rejected(lambda: self._bundle(defect),
                               message="missing extra or inconsistent addressed evidence")

    def test_operand_and_seal_update_delete_rejected_by_database(self):
        operand = m.MetricOperand.objects.for_owner(self.owner.user.pk).filter(parent_metric=self.original).first()
        for model, pk, change in ((m.MetricOperand, operand.pk, {"role": "changed"}),
                                  (m.MetricSeal, self.original.pk, {"creation_txid": 0})):
            for operation in ("update", "delete"):
                with self.subTest(model=model.__name__, operation=operation):
                    def attempt():
                        query = model.objects.for_owner(self.owner.user.pk).filter(pk=pk)
                        if operation == "update":
                            query.update(**change)
                        else:
                            query._raw_delete("default")
                    self._rejected(attempt, message="saved metric graph is immutable")
