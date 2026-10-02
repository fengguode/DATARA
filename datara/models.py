"""DATARA Milestone A persistence set.

Binding architectural condition (`docs/management/decision-register.md`,
"Binding architectural condition, stated by meaning rather than by name"):
Milestone A persists only ``Import``, ``SourceObject``, ``Activity``/``Session``,
``Snapshot`` plus the three supporting records ``Eligibility``, ``Evidence`` and
the quarantined conflict record -- and **none of them stores a skill-against-model
outcome under any name**. The exclusion is semantic. Explicitly a defect if
present: ``Run``, ``SelectedSkillExecution``, ``Attempt``, ``AssessmentResult``,
``Assessment``, ``Finding``, ``Connection``, ``SkillDefinition``, or any mutable
"latest result"/current-value pointer on any entity.

`datara.db.find_forbidden_schema_entities()` machine-checks this file's output
against the live database schema, so the condition is verified rather than
asserted.

What is deliberately NOT here, and why:

* No ``Metric`` table. The contracts reference computed metrics but define no
  schema of their own; that field contract is a D02/WP02 output. ``Evidence``
  refuses the ``computed_metric`` kind until that contract exists.
* No skill identifier on ``Eligibility``. Milestone A has no skill definitions
  (``SkillDefinition`` is an excluded entity), so the record carries a caller
  supplied rule-set version and a boolean, exactly as the G0 record describes.
* No quarantine population logic. The record exists because the founder's
  authorised scope requires logical-tuple quarantine; intake behaviour is another
  task's and is not implemented here.
* No mutable "latest result"/current-value pointer on any entity.

Required-field enforcement is structural: the four required normalized inputs
cannot be null in a persisted row. A file missing a required field is not
partially persisted -- it produces an ``Import`` with ``status='rejected'`` and a
stable ``reason_code``, and no ``Activity``/``Session`` at all.

Attribution: Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

from __future__ import annotations

import uuid
from typing import Any, Iterable

from django.conf import settings
from django.db import models

from datara import CONTRACT_VERSION, NORMALIZER_VERSION, SCHEMA_VERSION
from datara.canonical import MAX_ELAPSED_DURATION_MS, MIN_ELAPSED_DURATION_MS


class OwnerScopeNotBound(Exception):
    """An owner-unscoped query was attempted.

    Raised by ``OwnerScopedManager.all()`` and by unbound reads. The data-access
    layer in `datara.db` is the authorization boundary; this exception makes an
    accidental unscoped ORM read loud instead of returning another identity's
    rows.
    """


class ResourceNotVisible(Exception):
    """A resource is absent, or belongs to another identity.

    Deliberately does not distinguish the two. D04: an inaccessible or missing
    owner resource is a generic not-found; a denial must not confirm that another
    owner's object exists. ``model_label`` and ``resource_id`` are recorded for
    the access log; nothing about the other owner's data is disclosed.
    """

    def __init__(self, model_label: str, resource_id: Any) -> None:
        self.model_label = model_label
        self.resource_id = str(resource_id)
        super().__init__(
            f"resource not available: {model_label} {self.resource_id}"
        )


class ImmutabilityViolation(Exception):
    """An attempt was made to rewrite an immutable original or frozen record."""


# --------------------------------------------------------------------------
# Owner scoping
# --------------------------------------------------------------------------


class OwnerScopedQuerySet(models.QuerySet):
    """A queryset that can be narrowed to exactly one authenticated owner."""

    owner_id: int | None = None

    def for_owner(self, owner_id: int) -> "OwnerScopedQuerySet":
        if owner_id is None:
            raise OwnerScopeNotBound("an owner id is required to scope a query")
        scoped = self.filter(owner_id=owner_id)
        scoped.owner_id = owner_id
        return scoped


class OwnerScopedManager(models.Manager.from_queryset(OwnerScopedQuerySet)):
    """Default-deny owner-scoped manager.

    Two independent mechanisms:

    1. ``get_queryset()`` returns an **empty** queryset when unbound. An
       accidental unscoped read therefore returns nothing rather than another
       identity's rows, even if a caller forgets to scope.
    2. ``all()`` raises ``OwnerScopeNotBound``. The normal read path must state
       the owner explicitly, so the mistake is reported rather than absorbed.

    Known limitation, recorded rather than hidden: Django's *forward* relation
    descriptors (``activity.session_record``) resolve through
    ``Model._base_manager``, which is a plain ``Manager`` and is not scoped.
    Forward-descriptor traversal is therefore **not** an authorization boundary.
    Every read in this unit goes through `datara.db.OwnerScopedStore`, which is
    the boundary; `datara/tests/test_isolation.py` asserts that the store denies
    a swapped owner.
    """

    use_in_migrations = False

    def get_queryset(self) -> OwnerScopedQuerySet:
        return super().get_queryset().none()

    def all(self) -> OwnerScopedQuerySet:  # noqa: D102 - documented above
        raise OwnerScopeNotBound(
            "unscoped read refused: use Model.objects.for_owner(owner_id) or "
            "datara.db.OwnerScopedStore"
        )

    def for_owner(self, owner_id: int) -> OwnerScopedQuerySet:
        if owner_id is None:
            raise OwnerScopeNotBound("an owner id is required to scope a query")
        scoped = super().get_queryset().for_owner(owner_id)
        scoped.owner_id = owner_id
        return scoped

    def unbound(self) -> OwnerScopedQuerySet:
        """Unscoped access for trusted maintenance only.

        Never call this from a request, a view or a store read. It exists so that
        structural guards inside this module -- the ``SourceObject`` immutability
        check -- can compare a stored row against a supplied one without
        pretending to be an owner-scoped read.
        """
        return super().get_queryset()


class OwnerScopedModel(models.Model):
    """Base for every Milestone A record. Owner scope is never optional."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
        db_index=True,
    )

    objects = OwnerScopedManager()

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        if getattr(self, "owner_id", None) is None:
            raise OwnerScopeNotBound(
                f"{type(self).__name__} cannot be saved without an owner"
            )
        super().save(*args, **kwargs)


# --------------------------------------------------------------------------
# Source chain
# --------------------------------------------------------------------------


class Import(OwnerScopedModel):
    """One occurrence of submitted bytes and its terminal disposition.

    Rejected and conflicting uploads are retained as safe disposition metadata
    with no raw telemetry (D01). A rejected import has no ``Activity``; a
    conflicting import has a ``Quarantine`` and no published ``Activity``.
    """

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CONFLICT = "conflict"
    STATUS_CHOICES = [
        (ACCEPTED, "accepted"),
        (REJECTED, "rejected"),
        (CONFLICT, "conflict"),
    ]

    import_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_digest = models.CharField(max_length=71, editable=False)
    contract_version = models.CharField(max_length=64, default=CONTRACT_VERSION)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    reason_code = models.CharField(max_length=64, null=True, blank=True)
    reason_detail = models.CharField(max_length=64, null=True, blank=True)
    warnings = models.JSONField(default=list)
    accepted_at = models.DateTimeField(null=True, blank=True)

    # Provenance of the method, not of a model. `parser_version` and
    # `profile_reference` are pending TK09/TK10; they are recorded when the
    # source layer supplies them and are never invented here.
    parser_version = models.CharField(max_length=64, null=True, blank=True)
    profile_reference = models.CharField(max_length=128, null=True, blank=True)
    preparation_version = models.CharField(
        max_length=64, default=NORMALIZER_VERSION
    )

    class Meta:
        db_table = "datara_import"
        # Same owner + same bytes + same contract is idempotent: it references
        # existing history instead of creating a second import.
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "source_digest", "contract_version"],
                name="datara_import_owner_digest_contract_uniq",
            )
        ]
        indexes = [models.Index(fields=["owner", "status"], name="datara_import_owner_status")]


class SourceObject(OwnerScopedModel):
    """Immutable original bytes, referenced by SHA-256.

    Immutable in the database and in the accessor: a saved row cannot change its
    digest, length or storage reference. `save()` enforces this, so an accidental
    rewrite raises rather than silently overwriting history (CUS02, SR03).
    """

    source_object_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    digest = models.CharField(max_length=71, editable=False)
    byte_length = models.PositiveBigIntegerField(editable=False)
    storage_reference = models.CharField(max_length=512)
    media_type = models.CharField(max_length=64)
    retention_state = models.CharField(
        max_length=32, default="account_lifetime", editable=False
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    #: Fields that may never change after the first save.
    IMMUTABLE_FIELDS = ("digest", "byte_length", "storage_reference", "media_type")

    class Meta:
        db_table = "datara_source_object"
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "digest"], name="datara_source_owner_digest_uniq"
            )
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        if self.pk and type(self)._default_manager.unbound().filter(pk=self.pk).exists():
            stored = type(self)._default_manager.unbound().filter(pk=self.pk).first()
            for name in self.IMMUTABLE_FIELDS:
                if getattr(stored, name) != getattr(self, name):
                    raise ImmutabilityViolation(
                        f"SourceObject.{name} is immutable "
                        f"(stored {getattr(stored, name)!r}, supplied {getattr(self, name)!r})"
                    )
        super().save(*args, **kwargs)


# --------------------------------------------------------------------------
# Normalized records
# --------------------------------------------------------------------------


class Activity(OwnerScopedModel):
    """File-level normalized activity record.

    Holds the activity identity, the source lineage, the optional normalized
    metrics and the recorded quality warnings. The four *required* normalized
    inputs are carried by ``Session`` (sport, session UTC start instant, elapsed
    duration) and by the ``SourceObject`` reference (source digest), and the
    complete set is validated before either row is written.
    """

    PUBLISHED = "published"
    QUARANTINED = "quarantined"
    DISPOSITION_CHOICES = [(PUBLISHED, "published"), (QUARANTINED, "quarantined")]

    activity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_object = models.ForeignKey(
        SourceObject, on_delete=models.PROTECT, related_name="+"
    )
    import_record = models.ForeignKey(
        Import, on_delete=models.PROTECT, related_name="+"
    )
    disposition = models.CharField(
        max_length=16, choices=DISPOSITION_CHOICES, default=PUBLISHED
    )

    # Optional normalized metrics. Null means "absent or invalid", never
    # "imputed": D01 forbids imputation and every null here has a matching entry
    # in `quality_warnings` naming the same logical field.
    timer_duration_seconds = models.PositiveBigIntegerField(null=True, blank=True)
    distance_value = models.PositiveBigIntegerField(null=True, blank=True)
    distance_unit_code = models.CharField(max_length=64, null=True, blank=True)
    record_sample_count = models.PositiveBigIntegerField(null=True, blank=True)
    gps_point_count = models.PositiveBigIntegerField(null=True, blank=True)
    heart_rate_value = models.PositiveBigIntegerField(null=True, blank=True)
    heart_rate_unit_code = models.CharField(max_length=64, null=True, blank=True)

    quality_warnings = models.JSONField(default=list)
    normalization_digest = models.CharField(max_length=71)
    contract_version = models.CharField(max_length=64, default=CONTRACT_VERSION)
    normalizer_version = models.CharField(
        max_length=64, default=NORMALIZER_VERSION
    )
    policy_version = models.CharField(max_length=64)
    mapping_reference = models.CharField(max_length=128)

    class Meta:
        db_table = "datara_activity"
        indexes = [
            models.Index(
                fields=["owner", "disposition"], name="datara_activity_owner_disp"
            )
        ]


class Session(OwnerScopedModel):
    """Normalized session record: the three timing inputs of the required set.

    A session carries the sport, the UTC start instant and the *elapsed*
    activity duration, plus the official *timer* duration as a separate optional
    metric. All three required timing fields are NOT NULL, which is the
    structural statement that a record with a missing required field cannot be
    persisted: such a file is rejected whole, and no row is created.

    Elapsed and timer are separate columns and are never written from one
    another. Duration-based P0 volume means recorded elapsed activity duration
    (SR/D01); switching silently between elapsed and timer time is forbidden.

    **Unit.** ``elapsed_duration_ms`` is integer *milliseconds*, which is the
    canonical comparison unit of ``datara.canonical`` (section 6 of the
    duplicate/conflict contract; the P1-P7 precedence table is built on it). The
    column was previously named ``elapsed_duration_seconds`` while two modules
    wrote to it -- one in seconds, one in milliseconds -- and the exact tuple
    comparison compared the seconds value against a millisecond candidate, so the
    same 30-minute activity was stored as both ``1800`` and ``1800000`` and the
    second copy was accepted again. ``PositiveBigIntegerField`` cannot detect
    that: both are valid positive integers. The name now states the unit and
    :attr:`Meta.constraints` bounds the value to the millisecond domain, so a
    future writer that stores an unconverted seconds count is refused by the
    database as well as by ``datara.canonical.require_elapsed_duration_ms``.

    ``timer_duration_seconds`` deliberately keeps its own name and unit: it is a
    different metric (official timer time, not recorded elapsed time) and is not
    a tuple component.
    """

    activity = models.OneToOneField(
        Activity, on_delete=models.CASCADE, related_name="session_record"
    )
    session_index = models.PositiveSmallIntegerField(default=0)
    session_count = models.PositiveSmallIntegerField(default=1)

    sport = models.CharField(max_length=64)
    session_start_utc = models.DateTimeField()
    elapsed_duration_ms = models.PositiveBigIntegerField()
    timer_duration_seconds = models.PositiveBigIntegerField(null=True, blank=True)

    class Meta:
        db_table = "datara_session"
        indexes = [
            models.Index(
                fields=["owner", "session_start_utc"], name="datara_session_owner_start"
            )
        ]
        constraints = [
            # Schema-level half of the unit guard. See the class docstring: without
            # this, a seconds count stored in the millisecond column is an
            # indistinguishable valid integer, which is how one activity was
            # accepted twice. Bounds are the canonical millisecond domain from
            # `datara.canonical`.
            models.CheckConstraint(
                condition=models.Q(
                    elapsed_duration_ms__gte=MIN_ELAPSED_DURATION_MS,
                    elapsed_duration_ms__lte=MAX_ELAPSED_DURATION_MS,
                ),
                name="datara_session_elapsed_ms_domain",
            ),
        ]


# --------------------------------------------------------------------------
# Prepared scope
# --------------------------------------------------------------------------


class Snapshot(OwnerScopedModel):
    """Immutable prepared scope.

    The digest binds the canonical scope. It deliberately excludes the owner id,
    the generated ``snapshot_id`` and ``created_at``, because SR05 excludes
    generated identifiers and processing timestamps from the identity of a
    prepared result. Two preparations of the same accepted input under the same
    configuration and versions produce an identical ``snapshot_digest``.
    """

    snapshot_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scope_kind = models.CharField(max_length=64)
    scope_start_utc = models.DateTimeField(null=True, blank=True)
    scope_end_utc = models.DateTimeField(null=True, blank=True)
    included_activity_ids = models.JSONField(default=list)
    included_digests = models.JSONField(default=list)
    included_count = models.PositiveIntegerField(default=0)
    excluded_count = models.PositiveIntegerField(default=0)
    exclusions = models.JSONField(default=list)
    snapshot_digest = models.CharField(max_length=71)
    canonical_payload = models.TextField()
    contract_version = models.CharField(max_length=64, default=CONTRACT_VERSION)
    preparation_version = models.CharField(max_length=64)
    policy_version = models.CharField(max_length=64)
    mapping_reference = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "datara_snapshot"


# --------------------------------------------------------------------------
# Supporting records (in scope, and not findings)
# --------------------------------------------------------------------------


class Eligibility(OwnerScopedModel):
    """Deterministic eligibility outcome for a scope and a rule set.

    Records a rule version and a boolean plus an explanation of every unmet
    requirement. It names no skill version and no model: Milestone A has no skill
    definitions, and the founder's G0 record requires the record to be a rule
    version and a boolean, not a model outcome (CUS05, SR10-SR11).
    """

    eligibility_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    snapshot = models.ForeignKey(Snapshot, on_delete=models.PROTECT, related_name="+")
    rule_version = models.CharField(max_length=64)
    rule_set_version = models.CharField(max_length=64)
    eligible = models.BooleanField()
    unmet_requirements = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "datara_eligibility"


class Evidence(OwnerScopedModel):
    """Snapshot-local reference to a source record.

    The `computed_metric` kind is refused at write time. The contracts reference
    computed metrics but define no schema of their own, and the founder's G0
    record states that Milestone A must not invent it; any metric persisted
    before that contract exists is provisional. With no Milestone A run, evidence
    can only ever resolve to a source record.
    """

    KIND_SOURCE_RECORD = "source_record"
    KIND_COMPUTED_METRIC = "computed_metric"
    KIND_CHOICES = [
        (KIND_SOURCE_RECORD, "source record"),
        (KIND_COMPUTED_METRIC, "computed metric"),
    ]

    evidence_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    snapshot = models.ForeignKey(Snapshot, on_delete=models.PROTECT, related_name="+")
    kind = models.CharField(max_length=32, choices=KIND_CHOICES)
    source_object_ref = models.CharField(max_length=64, null=True, blank=True)
    activity_ref = models.CharField(max_length=64, null=True, blank=True)
    field_path = models.CharField(max_length=128, null=True, blank=True)
    value_canonical = models.TextField(null=True, blank=True)
    method_version = models.CharField(max_length=64, null=True, blank=True)
    method_inputs = models.JSONField(default=dict)

    class Meta:
        db_table = "datara_evidence"


class Quarantine(OwnerScopedModel):
    """A logical-tuple conflict held out of normal history.

    D01: different bytes with the exact logical tuple
    ``(owner, sport, UTC start, elapsed duration)`` are quarantined as a possible
    conflict. Never merged, never overwritten, never compared with a tolerance.
    Normal history and snapshots exclude an unresolved candidate. Quarantine is a
    disposition state on the source chain, not a finding.
    """

    REASON_LOGICAL_TUPLE_CONFLICT = "LOGICAL_TUPLE_CONFLICT"
    STATE_QUARANTINED = "quarantined"
    STATE_RESOLVED = "resolved"
    STATE_CHOICES = [(STATE_QUARANTINED, "quarantined"), (STATE_RESOLVED, "resolved")]
    RESOLUTION_CHOICES = [
        ("keep_existing", "keep existing"),
        ("replace_via_supersession", "replace via auditable supersession"),
        ("retain_both", "retain both explicitly"),
    ]

    quarantine_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    import_record = models.ForeignKey(Import, on_delete=models.PROTECT, related_name="+")
    candidate_source_object = models.ForeignKey(
        SourceObject, on_delete=models.PROTECT, related_name="+"
    )
    conflicting_source_object = models.ForeignKey(
        SourceObject, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    logical_tuple = models.JSONField()
    candidate_normalization_digest = models.CharField(max_length=71)
    candidate_normalized_payload = models.JSONField()
    reason_code = models.CharField(
        max_length=64, default=REASON_LOGICAL_TUPLE_CONFLICT
    )
    state = models.CharField(max_length=16, choices=STATE_CHOICES, default=STATE_QUARANTINED)
    resolution = models.CharField(max_length=32, choices=RESOLUTION_CHOICES, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "datara_quarantine"


#: The complete Milestone A persistence set. `datara.db` uses this list as one of
#: the inputs to the schema guard.
MILESTONE_A_MODELS: tuple[type[models.Model], ...] = (
    Import,
    SourceObject,
    Activity,
    Session,
    Snapshot,
    Eligibility,
    Evidence,
    Quarantine,
)


def model_names() -> Iterable[str]:
    return (m.__name__ for m in MILESTONE_A_MODELS)


__all__ = [
    "SCHEMA_VERSION",
    "OwnerScopeNotBound",
    "ResourceNotVisible",
    "ImmutabilityViolation",
    "OwnerScopedQuerySet",
    "OwnerScopedManager",
    "OwnerScopedModel",
    "Import",
    "SourceObject",
    "Activity",
    "Session",
    "Snapshot",
    "Eligibility",
    "Evidence",
    "Quarantine",
    "MILESTONE_A_MODELS",
    "model_names",
]
