"""Fresh-database baseline of the existing Milestone A source schema.

WP02/WP03; CUS03-CUS05/CUS08/CUS10; SR05-SR11/SR20-SR21/SR28-SR29.
Manually authored from models.py; frozen literals keep history independent of
later application constants. No computed metric schema or data operation.

Discovery of this package makes Django migrate use these operations for datara
instead of syncdb, including when --run-syncdb is supplied. Existing syncdb
schemas require separately authorized adoption engineering and evidence. This
source does not authorize execution, fake application, or establish compatibility
with an existing database. Historical managers are Django's ordinary managers:
the current OwnerScopedManager explicitly has use_in_migrations=False; historical
models do not constitute the application's authorization boundary.
"""

import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Import",
            fields=[
                ("import_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("source_digest", models.CharField(editable=False, max_length=71)),
                ("contract_version", models.CharField(default="datara-milestone-a/normalization/1", max_length=64)),
                ("status", models.CharField(choices=[("accepted", "accepted"), ("rejected", "rejected"), ("conflict", "conflict")], max_length=16)),
                ("reason_code", models.CharField(blank=True, max_length=64, null=True)),
                ("reason_detail", models.CharField(blank=True, max_length=64, null=True)),
                ("warnings", models.JSONField(default=list)),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("parser_version", models.CharField(blank=True, max_length=64, null=True)),
                ("profile_reference", models.CharField(blank=True, max_length=128, null=True)),
                ("preparation_version", models.CharField(default="tk18-normalizer/1", max_length=64)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "datara_import",
                "indexes": [models.Index(fields=["owner", "status"], name="datara_import_owner_status")],
                "constraints": [models.UniqueConstraint(fields=("owner", "source_digest", "contract_version"), name="datara_import_owner_digest_contract_uniq")],
            },
        ),
        migrations.CreateModel(
            name="SourceObject",
            fields=[
                ("source_object_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("digest", models.CharField(editable=False, max_length=71)),
                ("byte_length", models.PositiveBigIntegerField(editable=False)),
                ("storage_reference", models.CharField(max_length=512)),
                ("media_type", models.CharField(max_length=64)),
                ("retention_state", models.CharField(default="account_lifetime", editable=False, max_length=32)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "datara_source_object",
                "constraints": [models.UniqueConstraint(fields=("owner", "digest"), name="datara_source_owner_digest_uniq")],
            },
        ),
        migrations.CreateModel(
            name="Activity",
            fields=[
                ("activity_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("disposition", models.CharField(choices=[("published", "published"), ("quarantined", "quarantined")], default="published", max_length=16)),
                ("timer_duration_seconds", models.PositiveBigIntegerField(blank=True, null=True)),
                ("distance_value", models.PositiveBigIntegerField(blank=True, null=True)),
                ("distance_unit_code", models.CharField(blank=True, max_length=64, null=True)),
                ("record_sample_count", models.PositiveBigIntegerField(blank=True, null=True)),
                ("gps_point_count", models.PositiveBigIntegerField(blank=True, null=True)),
                ("heart_rate_value", models.PositiveBigIntegerField(blank=True, null=True)),
                ("heart_rate_unit_code", models.CharField(blank=True, max_length=64, null=True)),
                ("quality_warnings", models.JSONField(default=list)),
                ("normalization_digest", models.CharField(max_length=71)),
                ("contract_version", models.CharField(default="datara-milestone-a/normalization/1", max_length=64)),
                ("normalizer_version", models.CharField(default="tk18-normalizer/1", max_length=64)),
                ("policy_version", models.CharField(max_length=64)),
                ("mapping_reference", models.CharField(max_length=128)),
                ("import_record", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.import")),
                ("source_object", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.sourceobject")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "datara_activity",
                "indexes": [models.Index(fields=["owner", "disposition"], name="datara_activity_owner_disp")],
            },
        ),
        migrations.CreateModel(
            name="Session",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_index", models.PositiveSmallIntegerField(default=0)),
                ("session_count", models.PositiveSmallIntegerField(default=1)),
                ("sport", models.CharField(max_length=64)),
                ("session_start_utc", models.DateTimeField()),
                ("elapsed_duration_ms", models.PositiveBigIntegerField()),
                ("timer_duration_seconds", models.PositiveBigIntegerField(blank=True, null=True)),
                ("activity", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="session_record", to="datara.activity")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "datara_session",
                "indexes": [models.Index(fields=["owner", "session_start_utc"], name="datara_session_owner_start")],
                "constraints": [models.CheckConstraint(condition=models.Q(elapsed_duration_ms__gte=1000, elapsed_duration_ms__lte=86400000), name="datara_session_elapsed_ms_domain")],
            },
        ),
        migrations.CreateModel(
            name="Snapshot",
            fields=[
                ("snapshot_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("scope_kind", models.CharField(max_length=64)),
                ("scope_start_utc", models.DateTimeField(blank=True, null=True)),
                ("scope_end_utc", models.DateTimeField(blank=True, null=True)),
                ("included_activity_ids", models.JSONField(default=list)),
                ("included_digests", models.JSONField(default=list)),
                ("included_count", models.PositiveIntegerField(default=0)),
                ("excluded_count", models.PositiveIntegerField(default=0)),
                ("exclusions", models.JSONField(default=list)),
                ("snapshot_digest", models.CharField(max_length=71)),
                ("canonical_payload", models.TextField()),
                ("contract_version", models.CharField(default="datara-milestone-a/normalization/1", max_length=64)),
                ("preparation_version", models.CharField(max_length=64)),
                ("policy_version", models.CharField(max_length=64)),
                ("mapping_reference", models.CharField(max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "datara_snapshot"},
        ),
        migrations.CreateModel(
            name="Eligibility",
            fields=[
                ("eligibility_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("rule_version", models.CharField(max_length=64)),
                ("rule_set_version", models.CharField(max_length=64)),
                ("eligible", models.BooleanField()),
                ("unmet_requirements", models.JSONField(default=list)),
                ("warnings", models.JSONField(default=list)),
                ("evaluated_at", models.DateTimeField(auto_now_add=True)),
                ("snapshot", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.snapshot")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "datara_eligibility"},
        ),
        migrations.CreateModel(
            name="Evidence",
            fields=[
                ("evidence_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("kind", models.CharField(choices=[("source_record", "source record"), ("computed_metric", "computed metric")], max_length=32)),
                ("source_object_ref", models.CharField(blank=True, max_length=64, null=True)),
                ("activity_ref", models.CharField(blank=True, max_length=64, null=True)),
                ("field_path", models.CharField(blank=True, max_length=128, null=True)),
                ("value_canonical", models.TextField(blank=True, null=True)),
                ("method_version", models.CharField(blank=True, max_length=64, null=True)),
                ("method_inputs", models.JSONField(default=dict)),
                ("snapshot", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.snapshot")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "datara_evidence"},
        ),
        migrations.CreateModel(
            name="Quarantine",
            fields=[
                ("quarantine_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("logical_tuple", models.JSONField()),
                ("candidate_normalization_digest", models.CharField(max_length=71)),
                ("candidate_normalized_payload", models.JSONField()),
                ("reason_code", models.CharField(default="LOGICAL_TUPLE_CONFLICT", max_length=64)),
                ("state", models.CharField(choices=[("quarantined", "quarantined"), ("resolved", "resolved")], default="quarantined", max_length=16)),
                ("resolution", models.CharField(blank=True, choices=[("keep_existing", "keep existing"), ("replace_via_supersession", "replace via auditable supersession"), ("retain_both", "retain both explicitly")], max_length=32, null=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("import_record", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.import")),
                ("candidate_source_object", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.sourceobject")),
                ("conflicting_source_object", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.sourceobject")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "datara_quarantine"},
        ),
    ]
