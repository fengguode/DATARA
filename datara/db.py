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
from datara.canonical import (
    CANONICAL_DURATION_UNIT,
    elapsed_duration_ms_from_seconds,
    require_elapsed_duration_ms,
)
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
                # Write-site unit guard. `normalized` carries the TK18
                # normalization contract, which is integer seconds by contract;
                # the column is the canonical millisecond unit. The conversion is
                # exact and asserted here rather than left to a reader.
                elapsed_duration_ms=require_elapsed_duration_ms(
                    elapsed_duration_ms_from_seconds(
                        normalized.elapsed_duration_seconds,
                        origin=(
                            "OwnerScopedStore.record_normalized_activity"
                            ".elapsed_duration_seconds"
                        ),
                    ),
                    origin=(
                        "OwnerScopedStore.record_normalized_activity"
                        ".elapsed_duration_ms"
                    ),
                    unit=CANONICAL_DURATION_UNIT,
                ),
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
#:
#: The patterns are anchored on the whole *family*, not on three literals. The
#: previous `run_pointer` pattern was `^(latest|current)_run$`, which let
#: `last_run`, `last_run_id`, `current_run_id`, `last_run_at` and `most_recent_run`
#: through while catching `latest_run` and `current_run` -- the guard was
#: satisfied by the two names its own test exercised and blind to the rest of the
#: family it exists to forbid. Every "newest value" adjective is therefore
#: accepted, and a trailing qualifier (`_id`, `_at`, `_digest`, ...) is allowed,
#: because a pointer to the newest run *by id* or *at an instant* is the same
#: mutable pointer with a different suffix.
#:
#: #318 reported the missing `last_run` case and it did not land. It is covered by
#: `datara/tests/test_isolation.py::test_mutable_pointer_names_are_refused_even_
#: without_a_forbidden_entity`, which now exercises every member of the family.
_NEWEST_ADJECTIVES = "latest|last|current|most_recent|newest"
_POINTER_QUALIFIER = r"(?:_[a-z0-9]+)*"

FORBIDDEN_COLUMN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # The two specific families first, so a violation is reported under the name
    # that says what it is rather than under the generic `latest_` catch-all.
    (
        "run_pointer",
        re.compile(
            rf"^(?:{_NEWEST_ADJECTIVES})_?run{_POINTER_QUALIFIER}$", re.IGNORECASE
        ),
    ),
    (
        "result_pointer",
        re.compile(
            rf"^(?:{_NEWEST_ADJECTIVES})_?result{_POINTER_QUALIFIER}$",
            re.IGNORECASE,
        ),
    ),
    ("latest_pointer", re.compile(r"^latest_", re.IGNORECASE)),
    ("current_value_pointer", re.compile(r"^current_value", re.IGNORECASE)),
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


def _folded(name: str) -> str:
    """Fold a name for entity comparison: lower case, underscores removed.

    The comparison used to be ``name.lower() == entity.lower()``, which caught
    ``datara_skilldefinition`` but missed ``datara_skill_definition``. Every model
    in this package sets a snake_case ``db_table`` (the house style), so a
    multi-word forbidden entity written in house style escaped the table-level
    check entirely -- as did ``selected_skill_execution`` and
    ``assessment_result``. Removing ``_`` from *both* sides closes that without
    inventing any new name: it makes ``skill_definition``, ``SkillDefinition``
    and ``SKILL_DEFINITION`` one comparison rather than three.
    """

    return name.replace("_", "").lower()


#: The forbidden entities, pre-folded, so each comparison is one set lookup and
#: every path (table, column, field, model, module symbol) folds identically.
_FORBIDDEN_FOLDED: dict[str, str] = {
    _folded(entity): entity for entity in FORBIDDEN_ENTITY_NAMES
}


def _name_is_forbidden(name: str) -> tuple[str, str] | None:
    """Whether ``name`` is a forbidden entity name or a mutable pointer name.

    Returns ``(entity_or_label, reason_kind)`` or ``None``. The mutable-pointer
    patterns are applied to the name *as written*, because they are anchored on
    underscores (``^latest_``, ``_pointer$``); folding first would silently
    change what they match.
    """

    for label, pattern in FORBIDDEN_COLUMN_PATTERNS:
        if pattern.search(name):
            return label, "mutable_pointer_name"
    entity = _FORBIDDEN_FOLDED.get(_folded(name))
    if entity is not None:
        if name == entity:
            return entity, "forbidden_entity_name"
        return entity, "forbidden_entity_name_normalised"
    return None


def find_forbidden_schema_entities(facts: SchemaFacts) -> tuple[SchemaViolation, ...]:
    """Return every breach of the binding condition. Empty tuple means satisfied.

    Pure function of ``facts``. Deliberately returns the *violations* rather than
    a boolean so a failure names the offending entity, table and column.
    """
    violations: list[SchemaViolation] = []

    for name in facts.model_names:
        # Case-insensitive and underscore-insensitive, exactly like the table
        # path. The registry check used to be exact set membership, so a model
        # registered as `run` produced no violation here while the table it
        # created was still caught by the table path: the guard's verdict
        # depended on how the table happened to be named rather than on what the
        # entity *is*.
        if _FORBIDDEN_FOLDED.get(_folded(name)) is not None:
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
        if _FORBIDDEN_FOLDED.get(_folded(symbol)) is not None:
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
