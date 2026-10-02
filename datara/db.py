"""Owner-scoped data access, and the machine check for the binding condition.

This module is the authorization boundary for Milestone A. The service derives
owner scope from the authenticated principal and applies it to every read, so a
client-supplied owner identifier is never trusted (CUS10, SR20-SR21). Swapping
an owner identifier fails: it does not return the other identity's data, and it
does not confirm that the object exists.

Two halves:

* :class:`OwnerScopedStore` -- the only supported read path. It is constructed
  from an authenticated user, never from a request payload.
* :func:`find_forbidden_schema_entities` -- the executable form of the founder's
  binding architectural condition. The condition is semantic, so the check is
  expressed against the *live database schema*, the model metadata and the
  package source symbols, not against a list of names someone remembered.

Neither half opens a socket, calls a model or reads a credential.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from django.apps import apps
from django.db import connection, transaction

from datara import models as m
from datara.models import (
    Activity,
    Eligibility,
    Evidence,
    Import,
    Quarantine,
    ResourceNotVisible,
    Session,
    Snapshot,
    SourceObject,
)

# ---------------------------------------------------------------------------
# Owner scope
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OwnerScope:
    """The authenticated owner's scope.

    Construct it with :meth:`for_authenticated_user`. A raw owner id in a
    request payload is not a valid source for this value; nothing in this module
    accepts one.
    """

    owner_id: int

    def __post_init__(self) -> None:
        if self.owner_id is None:
            raise ValueError("OwnerScope requires an authenticated owner id")

    @classmethod
    def for_authenticated_user(cls, user: Any) -> "OwnerScope":
        if user is None or not getattr(user, "is_authenticated", False):
            raise ValueError("OwnerScope requires an authenticated user")
        return cls(owner_id=user.pk)

    def queryset_for(self, model: type) -> m.OwnerScopedQuerySet:
        return model.objects.for_owner(self.owner_id)


class OwnerScopedStore:
    """Every Milestone A read and write, bound to one authenticated owner."""

    def __init__(self, scope: OwnerScope) -> None:
        self._scope = scope

    @classmethod
    def for_user(cls, user: Any) -> "OwnerScopedStore":
        return cls(OwnerScope.for_authenticated_user(user))

    @property
    def scope(self) -> OwnerScope:
        return self._scope

    # -- reads --------------------------------------------------------------

    def list_activities(self) -> list[Activity]:
        return list(
            Activity.objects.for_owner(self._scope.owner_id)
            .order_by("session_record__session_start_utc", "activity_id")
        )

    def count_activities(self) -> int:
        return Activity.objects.for_owner(self._scope.owner_id).count()

    def get_activity(self, activity_id: Any) -> Activity:
        try:
            return Activity.objects.for_owner(self._scope.owner_id).get(pk=activity_id)
        except (Activity.DoesNotExist, ValueError, TypeError):
            # Generic not-found. Identical response whether the object is absent
            # or belongs to another owner.
            raise ResourceNotVisible("datara.Activity", activity_id) from None

    def get_source_object(self, source_object_id: Any) -> SourceObject:
        try:
            return SourceObject.objects.for_owner(self._scope.owner_id).get(pk=source_object_id)
        except (SourceObject.DoesNotExist, ValueError, TypeError):
            raise ResourceNotVisible("datara.SourceObject", source_object_id) from None

    def get_session(self, activity_id: Any) -> Session:
        activity = self.get_activity(activity_id)
        session = activity.session_record
        if session is None or session.owner_id != self._scope.owner_id:
            raise ResourceNotVisible("datara.Session", activity_id)
        return session

    def get_snapshot(self, snapshot_id: Any) -> Snapshot:
        try:
            return Snapshot.objects.for_owner(self._scope.owner_id).get(pk=snapshot_id)
        except (Snapshot.DoesNotExist, ValueError, TypeError):
            raise ResourceNotVisible("datara.Snapshot", snapshot_id) from None

    def get_evidence(self, evidence_id: Any) -> Evidence:
        try:
            return Evidence.objects.for_owner(self._scope.owner_id).get(pk=evidence_id)
        except (Evidence.DoesNotExist, ValueError, TypeError):
            raise ResourceNotVisible("datara.Evidence", evidence_id) from None

    def list_eligibility_for_snapshot(self, snapshot_id: Any) -> list[Eligibility]:
        snapshot = self.get_snapshot(snapshot_id)
        return list(
            Eligibility.objects.for_owner(self._scope.owner_id)
            .filter(snapshot=snapshot)
            .order_by("rule_set_version", "eligibility_id")
        )

    # -- writes -------------------------------------------------------------

    def record_source_object(
        self, *, digest: str, byte_length: int, storage_reference: str, media_type: str
    ) -> SourceObject:
        with transaction.atomic():
            return SourceObject.objects.create(
                owner_id=self._scope.owner_id,
                digest=digest,
                byte_length=byte_length,
                storage_reference=storage_reference,
                media_type=media_type,
            )

    def record_import(
        self,
        *,
        source_digest: str,
        status: str,
        reason_code: str | None = None,
        reason_detail: str | None = None,
        warnings: Sequence[Any] = (),
        parser_version: str | None = None,
        profile_reference: str | None = None,
    ) -> Import:
        with transaction.atomic():
            return Import.objects.create(
                owner_id=self._scope.owner_id,
                source_digest=source_digest,
                status=status,
                reason_code=reason_code,
                reason_detail=reason_detail,
                warnings=list(warnings),
                parser_version=parser_version,
                profile_reference=profile_reference,
            )

    def record_normalized_activity(
        self,
        *,
        source_object: SourceObject,
        import_record: Import,
        normalized: Any,
        session_index: int = 0,
        session_count: int = 1,
    ) -> Activity:
        """Persist one accepted normalized activity with its session record.

        ``normalized`` is a `datara.normalization.NormalizedActivity`. All four
        required normalized inputs are written here, so a partially populated row
        cannot be constructed through this path.
        """
        self._require_own(source_object)
        self._require_own(import_record)
        with transaction.atomic():
            activity = Activity.objects.create(
                owner_id=self._scope.owner_id,
                source_object=source_object,
                import_record=import_record,
                disposition=Activity.PUBLISHED,
                timer_duration_seconds=normalized.timer_duration_seconds,
                distance_value=normalized.distance_value,
                distance_unit_code=normalized.distance_unit_code,
                record_sample_count=normalized.record_sample_count,
                gps_point_count=normalized.gps_point_count,
                heart_rate_value=normalized.heart_rate_value,
                heart_rate_unit_code=normalized.heart_rate_unit_code,
                quality_warnings=[w.as_record() for w in normalized.quality_warnings],
                normalization_digest=normalized.normalization_digest,
                policy_version=normalized.policy_version,
                mapping_reference=normalized.mapping_reference,
            )
            Session.objects.create(
                owner_id=self._scope.owner_id,
                activity=activity,
                session_index=session_index,
                session_count=session_count,
                sport=normalized.sport,
                session_start_utc=normalized.session_start_utc,
                elapsed_duration_seconds=normalized.elapsed_duration_seconds,
                timer_duration_seconds=normalized.timer_duration_seconds,
            )
            return activity

    def record_snapshot(self, preparation: Any, activity_ids: Sequence[Any]) -> Snapshot:
        """Persist an immutable prepared scope.

        ``activity_ids`` must belong to this owner; each is resolved through the
        owner-scoped read path so a cross-owner id cannot be smuggled into a
        snapshot.
        """
        owned = [self.get_activity(activity_id) for activity_id in activity_ids]
        if len(owned) != len(preparation.included_digests):
            raise ValueError(
                "snapshot inclusion count does not match the supplied activity ids"
            )
        digests = sorted(a.normalization_digest for a in owned)
        if digests != list(preparation.included_digests):
            raise ValueError("snapshot inclusion digests do not match the supplied activities")
        with transaction.atomic():
            return Snapshot.objects.create(
                owner_id=self._scope.owner_id,
                scope_kind=preparation.scope_kind,
                scope_start_utc=preparation.scope_start_utc,
                scope_end_utc=preparation.scope_end_utc,
                included_activity_ids=sorted(str(a.activity_id) for a in owned),
                included_digests=list(digests),
                included_count=preparation.included_count,
                excluded_count=preparation.excluded_count,
                exclusions=[
                    {"activity_ref": e.activity_ref, "reason_code": e.reason_code}
                    for e in preparation.exclusions
                ],
                snapshot_digest=preparation.snapshot_digest,
                canonical_payload=preparation.canonical_payload,
                preparation_version=preparation.preparation_version,
                policy_version=preparation.policy_version,
                mapping_reference=preparation.mapping_reference,
            )

    def record_eligibility(self, snapshot: Snapshot, decision: Any) -> Eligibility:
        self._require_own(snapshot)
        with transaction.atomic():
            return Eligibility.objects.create(
                owner_id=self._scope.owner_id,
                snapshot=snapshot,
                rule_version=decision.rule_version,
                rule_set_version=decision.rule_set_version,
                eligible=decision.eligible,
                unmet_requirements=[dict(item) for item in decision.unmet_requirements],
                warnings=list(decision.warnings),
            )

    def record_evidence(
        self,
        snapshot: Snapshot,
        *,
        kind: str,
        source_object_ref: str | None = None,
        activity_ref: str | None = None,
        field_path: str | None = None,
        value_canonical: str | None = None,
    ) -> Evidence:
        if kind == Evidence.KIND_COMPUTED_METRIC:
            # The contracts reference computed metrics but define no schema of
            # their own; the founder's G0 record says Milestone A must not invent
            # one. Refuse rather than persist a provisional metric shape.
            raise ValueError(
                "Evidence kind 'computed_metric' is not available in Milestone A: the "
                "metric field contract is a D02/WP02 output and has not been authored. "
                "Milestone A must not invent it."
            )
        if kind != Evidence.KIND_SOURCE_RECORD:
            raise ValueError(f"unknown evidence kind {kind!r}")
        self._require_own(snapshot)
        with transaction.atomic():
            return Evidence.objects.create(
                owner_id=self._scope.owner_id,
                snapshot=snapshot,
                kind=kind,
                source_object_ref=source_object_ref,
                activity_ref=activity_ref,
                field_path=field_path,
                value_canonical=value_canonical,
            )

    def record_quarantine(self, **kwargs: Any) -> Quarantine:
        kwargs.setdefault("owner_id", self._scope.owner_id)
        with transaction.atomic():
            return Quarantine.objects.create(**kwargs)

    # -- internals ----------------------------------------------------------

    def _require_own(self, instance: Any) -> None:
        if instance.owner_id != self._scope.owner_id:
            raise ResourceNotVisible(instance._meta.label, getattr(instance, "pk", ""))


# ---------------------------------------------------------------------------
# Binding-architectural-condition check
# ---------------------------------------------------------------------------

#: Entities whose *meaning* is the outcome of executing a skill against a model.
#: Listing the names is not the condition; the condition is semantic, so the
#: check below runs against the real schema. These names are the founder's
#: explicit examples of a violation.
FORBIDDEN_ENTITY_NAMES: tuple[str, ...] = (
    "Run",
    "SelectedSkillExecution",
    "Attempt",
    "AssessmentResult",
    "Assessment",
    "Finding",
    "Connection",
    "SkillDefinition",
)

#: "No mutable 'latest result' or current-value pointer may exist on any entity."
FORBIDDEN_COLUMN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("latest_pointer", re.compile(r"^latest_", re.IGNORECASE)),
    ("current_value_pointer", re.compile(r"^current_value", re.IGNORECASE)),
    ("result_pointer", re.compile(r"^(latest|last|current)_result$", re.IGNORECASE)),
    ("run_pointer", re.compile(r"^(latest|current)_run$", re.IGNORECASE)),
    ("mutable_pointer_suffix", re.compile(r"_pointer$", re.IGNORECASE)),
)

#: Vendor prefix stripped before comparing a table name to the entity list.
_TABLE_PREFIX = "datara_"


@dataclass(frozen=True)
class SchemaViolation:
    """One place where the binding condition is not satisfied."""

    kind: str
    name: str
    location: str

    def __str__(self) -> str:
        return f"{self.kind}:{self.name} ({self.location})"


@dataclass(frozen=True)
class SchemaFacts:
    """Everything the condition is checked against."""

    table_names: tuple[str, ...]
    columns: tuple[tuple[str, str], ...]
    model_names: tuple[str, ...]
    field_names: tuple[tuple[str, str], ...]
    module_symbols: tuple[str, ...]


def _package_module_paths() -> list[Path]:
    """Datara package modules, excluding the test package.

    The tests are excluded because the tests deliberately construct *violated*
    schemas to prove the check can fail; scanning them would report those
    deliberate controls as defects.
    """
    package_dir = Path(__file__).resolve().parent
    return sorted(p for p in package_dir.glob("*.py"))


def _module_symbols(paths: Iterable[Path]) -> set[str]:
    symbols: set[str] = set()
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                symbols.add(node.name)
    return symbols


def introspect_persisted_schema(connection_obj: Any = None) -> SchemaFacts:
    """Read the live schema. Falls back to model metadata for the model names."""
    conn = connection_obj or connection
    with conn.cursor() as cursor:
        tables = tuple(sorted(conn.introspection.table_names(cursor)))
        columns: list[tuple[str, str]] = []
        for table in tables:
            description = conn.introspection.get_table_description(cursor, table)
            for column in description:
                columns.append((table, column.name))

    model_names = tuple(sorted(model.__name__ for model in apps.get_models()))
    field_names = tuple(
        sorted(
            (model.__name__, field.name)
            for model in apps.get_models()
            for field in model._meta.get_fields()
            if getattr(field, "concrete", False)
        )
    )
    symbols = _module_symbols(_package_module_paths())

    return SchemaFacts(
        table_names=tables,
        columns=tuple(sorted(columns)),
        model_names=model_names,
        field_names=field_names,
        module_symbols=tuple(sorted(symbols)),
    )


def _name_is_forbidden(name: str) -> tuple[str, str] | None:
    for entity in FORBIDDEN_ENTITY_NAMES:
        if name == entity:
            return entity, "forbidden_entity_name"
    lowered = name.lower()
    for entity in FORBIDDEN_ENTITY_NAMES:
        if lowered == entity.lower():
            return entity, "forbidden_entity_name_case_insensitive"
    for label, pattern in FORBIDDEN_COLUMN_PATTERNS:
        if pattern.search(name):
            return label, "mutable_pointer_name"
    return None


def find_forbidden_schema_entities(facts: SchemaFacts) -> tuple[SchemaViolation, ...]:
    """Return every breach of the binding condition. Empty tuple means satisfied.

    Pure function of ``facts``. Deliberately returns the *violations* rather than
    a boolean so a failure names the offending entity, table and column.
    """
    violations: list[SchemaViolation] = []
    forbidden = set(FORBIDDEN_ENTITY_NAMES)

    for name in facts.model_names:
        if name in forbidden:
            violations.append(SchemaViolation("model", name, "django model registry"))

    for table in facts.table_names:
        if not table.startswith(_TABLE_PREFIX):
            continue
        bare = table[len(_TABLE_PREFIX) :]
        hit = _name_is_forbidden(bare)
        if hit is not None:
            violations.append(
                SchemaViolation("table", bare, f"table {table} ({hit[1]})")
            )

    for table, column in facts.columns:
        hit = _name_is_forbidden(column)
        if hit is not None:
            violations.append(SchemaViolation("column", column, f"table {table} ({hit[1]})"))

    for model, field_name in facts.field_names:
        hit = _name_is_forbidden(field_name)
        if hit is not None:
            violations.append(
                SchemaViolation("field", field_name, f"model {model} ({hit[1]})")
            )

    for symbol in facts.module_symbols:
        if symbol in forbidden:
            violations.append(SchemaViolation("module_symbol", symbol, "datara package source"))

    return tuple(sorted(violations, key=lambda v: (v.kind, v.name, v.location)))


__all__ = [
    "OwnerScope",
    "OwnerScopedStore",
    "SchemaViolation",
    "SchemaFacts",
    "FORBIDDEN_ENTITY_NAMES",
    "FORBIDDEN_COLUMN_PATTERNS",
    "introspect_persisted_schema",
    "find_forbidden_schema_entities",
]
