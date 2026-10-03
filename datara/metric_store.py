"""Authenticated immutable recorded metric graphs (WP02/WP03).

CUS03-05/CUS08/CUS10; SR05-11/SR20-21/SR28-29. Internal persistence
only. Successful nested saves remain provisional until the outer commit.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, transaction

from datara import models as m
from datara.db import OwnerScopedStore
from datara.metric_projection import (
    CODEC_VERSION, MANIFEST_VERSION, OPERAND_PROJECTION_VERSION,
    PURE_ADAPTER_VERSION, PURE_CONTRACT_VERSION, READER_VERSION,
    REGISTRY_ADAPTER_VERSION, SCOPED_INPUT_VERSION, SOURCE_CONTRACT_VERSION,
    project_recorded_result,
)
from datara.provenance import ProvenanceError
from datara.recorded_metrics import (
    RecordedInputRefusal, canonical_metric_content, prepare_overall_trend,
    prepare_recorded_input, summarize_recorded,
)
from datara.scoped_input import MilestoneAInputStore, ScopedInputError


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


class MetricStoreRefusal(ValueError):
    """Safe internal reason, without source data or database diagnostics."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True)
class SavedMetric:
    metric_id: str
    snapshot_id: str
    state: str
    canonical_content: bytes | None = None
    canonical_registry_content: bytes | None = None
    canonical_method_identity: bytes | None = None
    created: bool = False
    reader_version: str = READER_VERSION


@dataclass(frozen=True)
class SavedMetricEvidence:
    evidence_id: str
    metric: SavedMetric
    value_path: str | None = None
    canonical_registry_entry: bytes | None = None


class SavedMetricStore(OwnerScopedStore):
    """Owner is derived by inherited ``for_user(user)``, never a client id."""

    def _metrics(self):
        return m.Metric.objects.for_owner(self.scope.owner_id)

    def _metric(self, metric_id):
        try:
            return self._metrics().get(pk=metric_id)
        except (m.Metric.DoesNotExist, ValueError, TypeError, ValidationError):
            raise MetricStoreRefusal("resource_not_available") from None

    def _snapshot(self, snapshot_id):
        try:
            return self.get_snapshot(snapshot_id)
        except (m.ResourceNotVisible, ValidationError):
            raise MetricStoreRefusal("resource_not_available") from None

    def _source(self, snapshot):
        """Validate the complete envelope and source ledger before operands."""
        inputs = MilestoneAInputStore(self)
        try:
            version = inputs.get_version(snapshot.pk)
            data = prepare_recorded_input(version)
        except (ScopedInputError, RecordedInputRefusal, ProvenanceError,
                ValueError, TypeError, KeyError):
            raise MetricStoreRefusal("corrupt_content") from None
        inputs.provenance_rows(snapshot.pk)
        activity_ids = inputs.resolve_activity_ids(version.included_digests)
        expected = {
            "contract_version": m.CONTRACT_VERSION,
            "scope_kind": version.scope_kind,
            "included_digests": list(version.included_digests),
            "included_activity_ids": sorted(str(pk) for pk in activity_ids),
            "included_count": version.included_count,
            "excluded_count": version.excluded_count,
            "preparation_version": version.preparation_version,
            "policy_version": version.policy_version,
            "mapping_reference": version.mapping_reference,
            "exclusions": [{"activity_ref": e.activity_ref,
                            "reason_code": e.reason_code} for e in version.exclusions],
        }
        if any(getattr(snapshot, name) != value for name, value in expected.items()):
            raise MetricStoreRefusal("corrupt_content")
        for name, value in (("scope_start_utc", version.scope_start_utc),
                            ("scope_end_utc", version.scope_end_utc)):
            if getattr(snapshot, name) != datetime.fromisoformat(value.replace("Z", "+00:00")):
                raise MetricStoreRefusal("corrupt_content")
        # Resolve source/import/session through explicit owner scope, never FK
        # descriptors. The snapshot ledger remains the method-policy authority.
        for record, activity_id in zip(
                sorted(version.records, key=lambda r: r.canonical_identity), activity_ids):
            activity = self.get_activity(activity_id)
            source = self.get_source_object(activity.source_object_id)
            imports = m.Import.objects.for_owner(self.scope.owner_id).filter(
                pk=activity.import_record_id)
            import_record = imports.first()
            if (source.deleted_at is not None or source.retention_state != "account_lifetime"
                    or source.digest != record.source_digest or import_record is None
                    or import_record.source_digest != record.source_digest
                    or import_record.status != m.Import.ACCEPTED
                    or import_record.contract_version != activity.contract_version
                    or activity.contract_version != snapshot.contract_version
                    or import_record.preparation_version != record.preparation_version
                    or activity.normalization_digest != record.canonical_identity
                    or activity.normalizer_version != record.preparation_version
                    or activity.mapping_reference != record.mapping_reference
                    or activity.policy_version != record.policy_version):
                raise MetricStoreRefusal("source_unavailable")
            # Current quarantine/disposition does not redefine the frozen
            # selected membership. Validate original accepted lineage and exact
            # values, rather than recomputing a present-day selection.
            session = self.get_session(activity_id)
            if (session.sport != record.field("sport").value_canonical
                    or session.elapsed_duration_ms != int(record.field("elapsed_duration_ms").value_canonical)
                    or session.session_start_utc != datetime.fromtimestamp(
                        int(record.field("start_epoch_seconds").value_canonical), timezone.utc)):
                raise MetricStoreRefusal("source_unavailable")
        return version, data

    def _resolve_operands(self, snapshot, version, projection):
        resolved = []
        for operand in projection.operand_document()["operands"]:
            source = operand["source"]
            entry = version.ledger.resolve(source["source_field_path"])
            if (operand["role"] != source["source_field_path"]
                    or entry.canonical_identity != source["normalization_digest"]
                    or entry.source_digest != source["source_digest"]
                    or entry.preparation_version != source["preparation_version"]
                    or entry.mapping_reference != source["mapping_reference"]
                    or entry.value_canonical != source["value"] or not entry.available):
                raise MetricStoreRefusal("incomplete_graph")
            matches = list(m.Evidence.objects.for_owner(self.scope.owner_id).filter(
                snapshot_id=snapshot.pk, kind=m.Evidence.KIND_SOURCE_RECORD,
                field_path=source["source_field_path"]))
            if len(matches) != 1 or matches[0].value_canonical != source["value"]:
                raise MetricStoreRefusal("source_unavailable")
            resolved.append((operand, matches[0].pk))
        return resolved

    def _validate(self, metric, snapshot, projection, resolved):
        """Exact bytes, metadata and sealed relational sets; never repair."""
        document = json.loads(projection.canonical_content)
        expected = {
            "owner_id": self.scope.owner_id, "snapshot_id": snapshot.pk,
            "content_digest": projection.content_digest,
            "canonical_content": projection.canonical_content.decode("ascii"),
            "metric_contract_version": document["metric_contract_version"],
            "metric_code": document["metric_code"],
            "method_identity": document["method_identity"],
            "supported_input_contract_version": document["supported_input_contract_version"],
            "input_content_digest": document["input_content_digest"],
            "registry_adapter_version": REGISTRY_ADAPTER_VERSION,
            "canonical_registry_content": projection.canonical_registry_content.decode("ascii"),
            "registry_projection_digest": projection.registry_projection_digest,
            "operand_projection_version": OPERAND_PROJECTION_VERSION,
            "canonical_operand_content": projection.canonical_operand_content.decode("ascii"),
        }
        if any((_canonical(getattr(metric, name)) != _canonical(value)
                if isinstance(value, (dict, list)) else getattr(metric, name) != value)
               for name, value in expected.items()):
            raise MetricStoreRefusal("corrupt_content")
        seals = list(m.MetricSeal.objects.for_owner(self.scope.owner_id).filter(metric_id=metric.pk))
        if (len(seals) != 1 or seals[0].snapshot_id != snapshot.pk
                or metric.creation_txid <= 0 or seals[0].creation_txid != metric.creation_txid):
            raise MetricStoreRefusal("incomplete_graph")
        rows = list(m.MetricOperand.objects.for_owner(self.scope.owner_id).filter(parent_metric_id=metric.pk))
        wanted = {(o["role"], o["ordinal"], pk, _canonical(o).decode("ascii")) for o, pk in resolved}
        actual = {(row.role, row.ordinal, row.source_evidence_id, row.canonical_operand) for row in rows}
        if (len(rows) != len(wanted) or actual != wanted
                or any(row.snapshot_id != snapshot.pk or row.dependency_metric_id is not None
                       or row.dependency_value_path is not None for row in rows)):
            raise MetricStoreRefusal("incomplete_graph")
        entries = projection.registry_document()["entries"]
        evidence = list(m.Evidence.objects.for_owner(self.scope.owner_id).filter(metric_id=metric.pk))
        wanted_evidence = {(entry["path"], _canonical(entry).decode("ascii")) for entry in entries}
        actual_evidence = {(row.value_path, row.value_canonical) for row in evidence}
        if (len(evidence) != len(wanted_evidence) or actual_evidence != wanted_evidence
                or any(row.snapshot_id != snapshot.pk or row.kind != m.Evidence.KIND_COMPUTED_METRIC
                       or row.method_version is not None or row.method_inputs != {}
                       or row.source_object_ref is not None or row.activity_ref is not None
                       or row.field_path is not None for row in evidence)):
            raise MetricStoreRefusal("incomplete_graph")

    def _result(self, metric, *, state="complete", created=False):
        complete = state == "complete"
        return SavedMetric(str(metric.pk), str(metric.snapshot_id), state,
                           metric.canonical_content.encode("ascii") if complete else None,
                           metric.canonical_registry_content.encode("ascii") if complete else None,
                           _canonical(json.loads(metric.canonical_content)["method_identity"]) if complete else None,
                           created)

    def save_prepared_metrics(self, saved_snapshot_id, prepared):
        """Atomically save one supported compound result, or reuse exact history."""
        try:
            self._snapshot(saved_snapshot_id)  # authorization precedes preparation
            with self._owner_serialized_write():
                snapshot = self._snapshot(saved_snapshot_id)
                version, _ = self._source(snapshot)
                content = canonical_metric_content(prepared)
                if (prepared.source.source_canonical_content != snapshot.canonical_payload.encode("utf-8")
                        or prepared.source.input_content_digest != version.input_digest):
                    raise MetricStoreRefusal("input_binding_mismatch")
                projection = project_recorded_result(prepared)
                document = json.loads(content)
                resolved = self._resolve_operands(snapshot, version, projection)
                matches = list(self._metrics().filter(snapshot_id=snapshot.pk,
                                                     content_digest=projection.content_digest))
                if len(matches) > 1:
                    raise MetricStoreRefusal("incomplete_graph")
                created = not matches
                if matches:
                    metric = matches[0]
                else:
                    try:
                        with transaction.atomic(using="default"):
                            metric = m.Metric.objects.create(
                                owner_id=self.scope.owner_id, snapshot_id=snapshot.pk,
                                content_digest=projection.content_digest,
                                metric_contract_version=document["metric_contract_version"],
                                metric_code=document["metric_code"],
                                canonical_content=content.decode("ascii"),
                                method_identity=document["method_identity"],
                                supported_input_contract_version=document["supported_input_contract_version"],
                                input_content_digest=document["input_content_digest"],
                                registry_adapter_version=REGISTRY_ADAPTER_VERSION,
                                canonical_registry_content=projection.canonical_registry_content.decode("ascii"),
                                registry_projection_digest=projection.registry_projection_digest,
                                operand_projection_version=OPERAND_PROJECTION_VERSION,
                                canonical_operand_content=projection.canonical_operand_content.decode("ascii"))
                    except IntegrityError as error:
                        # Only this constraint can represent an insertion winner.
                        diagnostic = getattr(getattr(error, "__cause__", None), "diag", None)
                        if getattr(diagnostic, "constraint_name", None) != METRIC_IDENTITY_CONSTRAINT:
                            raise
                        matches = list(self._metrics().filter(snapshot_id=snapshot.pk,
                                                             content_digest=projection.content_digest))
                        if len(matches) != 1:
                            raise MetricStoreRefusal("incomplete_graph") from None
                        metric, created = matches[0], False
                    if created:
                        for operand, evidence_id in resolved:
                            m.MetricOperand.objects.create(
                                owner_id=self.scope.owner_id, snapshot_id=snapshot.pk,
                                parent_metric_id=metric.pk, source_evidence_id=evidence_id,
                                role=operand["role"], ordinal=operand["ordinal"],
                                canonical_operand=_canonical(operand).decode("ascii"))
                        for entry in projection.registry_document()["entries"]:
                            m.Evidence.objects.create(
                                owner_id=self.scope.owner_id, snapshot_id=snapshot.pk,
                                kind=m.Evidence.KIND_COMPUTED_METRIC, metric_id=metric.pk,
                                value_path=entry["path"], value_canonical=_canonical(entry).decode("ascii"),
                                method_version=None, method_inputs={})
                        m.MetricSeal.objects.create(owner_id=self.scope.owner_id,
                                                    snapshot_id=snapshot.pk, metric_id=metric.pk)
                        # The database assigns transaction identity before INSERT.
                        metric.refresh_from_db(fields=["creation_txid"])
                if metric.canonical_content != projection.canonical_content.decode("ascii"):
                    raise MetricStoreRefusal("digest_collision")
                self._validate(metric, snapshot, projection, resolved)
                return self._result(metric, created=created)
        except MetricStoreRefusal:
            raise
        except (DatabaseError, ScopedInputError, ProvenanceError, RecordedInputRefusal,
                m.ResourceNotVisible, ValidationError, ValueError, TypeError,
                KeyError, AttributeError):
            raise MetricStoreRefusal("metric_persistence_unavailable") from None

    def _read(self, metric, snapshot):
        try:
            content = metric.canonical_content.encode("ascii")
            document = json.loads(content)
            if _digest(content) != metric.content_digest:
                raise MetricStoreRefusal("corrupt_content")
            if (metric.metric_contract_version != PURE_CONTRACT_VERSION
                    or metric.registry_adapter_version != REGISTRY_ADAPTER_VERSION
                    or metric.operand_projection_version != OPERAND_PROJECTION_VERSION
                    or document.get("metric_contract_version") != PURE_CONTRACT_VERSION
                    or document.get("codec_version") != CODEC_VERSION
                    or document.get("supported_input_contract_version") != SOURCE_CONTRACT_VERSION
                    or document.get("manifest", {}).get("manifest_version") != MANIFEST_VERSION
                    or document.get("method_identity", {}).get("adapter_version") != PURE_ADAPTER_VERSION):
                return self._result(metric, state="unsupported_decoder")
            source_document = json.loads(snapshot.canonical_payload)
            if (source_document.get("contract_version") != SOURCE_CONTRACT_VERSION
                    or source_document.get("scoped_input_version") != SCOPED_INPUT_VERSION):
                return self._result(metric, state="unsupported_decoder")
            version, data = self._source(snapshot)
            if version.scoped_input_version != SCOPED_INPUT_VERSION:
                return self._result(metric, state="unsupported_decoder")
            if document.get("metric_code") == "activity-summary":
                oracle = summarize_recorded(data)
            elif document.get("metric_code") == "training-volume-trend":
                oracle = prepare_overall_trend(data)
            else:
                return self._result(metric, state="unsupported_decoder")
            projection = project_recorded_result(oracle)
            # Reconstruction is solely an equality oracle. Return stored bytes.
            resolved = self._resolve_operands(snapshot, version, projection)
            self._validate(metric, snapshot, projection, resolved)
            return self._result(metric)
        except MetricStoreRefusal as error:
            return self._result(metric, state=error.reason_code)
        except (m.ResourceNotVisible, ScopedInputError, ProvenanceError):
            return self._result(metric, state="source_unavailable")
        except (RecordedInputRefusal, ValueError, TypeError, KeyError, AttributeError, UnicodeError):
            return self._result(metric, state="corrupt_content")

    def get_metric(self, metric_id):
        try:
            metric = self._metric(metric_id)
            snapshot = self._snapshot(metric.snapshot_id)
            return self._read(metric, snapshot)
        except DatabaseError:
            raise MetricStoreRefusal("metric_retrieval_unavailable") from None

    def get_metric_evidence(self, evidence_id):
        try:
            try:
                evidence = m.Evidence.objects.for_owner(self.scope.owner_id).get(
                    pk=evidence_id, kind=m.Evidence.KIND_COMPUTED_METRIC)
            except (m.Evidence.DoesNotExist, ValueError, TypeError, ValidationError):
                raise MetricStoreRefusal("resource_not_available") from None
            metric = self._metric(evidence.metric_id)
            snapshot = self._snapshot(metric.snapshot_id)
            result = self._read(metric, snapshot)
            return SavedMetricEvidence(str(evidence.pk), result,
                evidence.value_path if result.state == "complete" else None,
                evidence.value_canonical.encode("ascii") if result.state == "complete" else None)
        except DatabaseError:
            raise MetricStoreRefusal("metric_retrieval_unavailable") from None

    def list_metrics_for_snapshot(self, snapshot_id):
        try:
            snapshot = self._snapshot(snapshot_id)
            return tuple(self._read(metric, snapshot) for metric in self._metrics().filter(
                snapshot_id=snapshot.pk).order_by("created_at", "metric_id"))
        except DatabaseError:
            raise MetricStoreRefusal("metric_retrieval_unavailable") from None


# Must match the named migration constraint; only this conflict is a retry.
METRIC_IDENTITY_CONSTRAINT = "datara_metric_owner_snapshot_digest_uniq"

__all__ = ["SavedMetricStore", "SavedMetric", "SavedMetricEvidence", "MetricStoreRefusal"]
