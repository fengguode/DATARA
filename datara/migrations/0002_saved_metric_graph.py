"""Additive immutable recorded graph; PostgreSQL 17, no extensions/grants.

WP02/WP03 CUS03-05/CUS08/CUS10 SR05-11/SR20-21/SR28-29.
Reverse is deliberately refused: historical graph rollback is behavioral only.
This source has not been executed against any database.
"""
import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.db.migrations.exceptions import IrreversibleError


def refuse_reverse(apps, schema_editor):
    raise IrreversibleError("Saved history must be retained; disable writers and retain the compatible reader/schema.")


SQL = r"""
DO $$ BEGIN
 IF current_setting('server_version_num')::integer < 170000
    OR current_setting('server_version_num')::integer >= 180000 THEN
  RAISE EXCEPTION 'saved metric graph requires PostgreSQL 17';
 END IF;
END $$;
ALTER TABLE datara_metric ADD CONSTRAINT datara_metric_snapshot_scope_fk
 FOREIGN KEY (owner_id,snapshot_id) REFERENCES datara_snapshot(owner_id,snapshot_id);
ALTER TABLE datara_metric_operand ADD CONSTRAINT datara_operand_parent_scope_fk
 FOREIGN KEY (owner_id,snapshot_id,parent_metric_id) REFERENCES datara_metric(owner_id,snapshot_id,metric_id);
ALTER TABLE datara_metric_operand ADD CONSTRAINT datara_operand_source_scope_fk
 FOREIGN KEY (owner_id,snapshot_id,source_evidence_id) REFERENCES datara_evidence(owner_id,snapshot_id,evidence_id);
ALTER TABLE datara_metric_operand ADD CONSTRAINT datara_operand_dependency_scope_fk
 FOREIGN KEY (owner_id,snapshot_id,dependency_metric_id) REFERENCES datara_metric(owner_id,snapshot_id,metric_id);
ALTER TABLE datara_metric_seal ADD CONSTRAINT datara_seal_parent_scope_fk
 FOREIGN KEY (owner_id,snapshot_id,metric_id) REFERENCES datara_metric(owner_id,snapshot_id,metric_id);
ALTER TABLE datara_evidence ADD CONSTRAINT datara_evidence_metric_scope_fk
 FOREIGN KEY (owner_id,snapshot_id,metric_id) REFERENCES datara_metric(owner_id,snapshot_id,metric_id);
ALTER TABLE datara_evidence ADD CONSTRAINT datara_evidence_snapshot_scope_fk
 FOREIGN KEY (owner_id,snapshot_id) REFERENCES datara_snapshot(owner_id,snapshot_id);
ALTER TABLE datara_metric_operand ADD CONSTRAINT datara_operand_reference_shape CHECK (
 (source_evidence_id IS NOT NULL AND dependency_metric_id IS NULL AND dependency_value_path IS NULL)
 OR (source_evidence_id IS NULL AND dependency_metric_id IS NOT NULL AND dependency_value_path IS NOT NULL));
ALTER TABLE datara_evidence ADD CONSTRAINT datara_evidence_kind_shape CHECK (
 (kind='source_record' AND metric_id IS NULL AND value_path IS NULL)
 OR (kind='computed_metric' AND metric_id IS NOT NULL AND value_path IS NOT NULL
 AND source_object_ref IS NULL AND activity_ref IS NULL AND field_path IS NULL
 AND value_canonical IS NOT NULL AND method_version IS NULL AND method_inputs='{}'::jsonb));

CREATE FUNCTION datara_metric_insert_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE parent datara_metric;
BEGIN
 IF TG_TABLE_NAME='datara_metric' THEN NEW.creation_txid:=txid_current(); RETURN NEW; END IF;
 IF TG_TABLE_NAME='datara_evidence' THEN
  IF NEW.kind='source_record' THEN RETURN NEW; END IF;
 END IF;
 IF TG_TABLE_NAME='datara_metric_operand' THEN
  SELECT * INTO parent FROM datara_metric WHERE metric_id=NEW.parent_metric_id FOR KEY SHARE;
 ELSE
  SELECT * INTO parent FROM datara_metric WHERE metric_id=NEW.metric_id FOR KEY SHARE;
 END IF;
 IF parent.metric_id IS NULL OR parent.creation_txid<>txid_current() THEN
  RAISE EXCEPTION 'metric graph must be created in one transaction';
 END IF;
 IF EXISTS(SELECT 1 FROM datara_metric_seal WHERE metric_id=parent.metric_id) THEN
  RAISE EXCEPTION 'sealed metric admits no additional rows';
 END IF;
 IF TG_TABLE_NAME='datara_metric_seal' THEN NEW.creation_txid:=txid_current(); END IF;
 RETURN NEW;
END $$;
CREATE FUNCTION datara_metric_immutable_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_TABLE_NAME='datara_evidence' THEN
  IF OLD.kind='source_record' THEN
   IF TG_OP='DELETE' THEN RETURN OLD; END IF;
   IF NEW.kind='source_record' THEN RETURN NEW; END IF;
  END IF;
 END IF;
 RAISE EXCEPTION 'saved metric graph is immutable';
END $$;

-- Reconstruct the registry from the parent document, including derivation
-- context. jsonb equality here is structural; canonical bytes/digests and
-- mathematical truth remain independently validated by the service/reader.
CREATE FUNCTION datara_recorded_registry(d jsonb) RETURNS jsonb LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE entries jsonb; binding jsonb; deriv jsonb; b jsonb; g jsonb; names text[];
 n text; i integer; paths jsonb; members jsonb; roles jsonb; kind text;
BEGIN
 binding:=jsonb_build_object('input_content_digest',d->'input_content_digest','manifest_path','/manifest',
 'method_identity',d->'method_identity','method_parameters',d->'method_parameters');
 entries:=jsonb_build_array(
 jsonb_build_object('path','/manifest','type','structured_context','payload',d->'manifest',
 'derivation',binding-'manifest_path'),
 jsonb_build_object('path','/eligibility','type','structured_context','payload',d->'eligibility','derivation',binding));
 IF d->>'metric_code'='activity-summary' THEN
  FOR g IN SELECT value FROM jsonb_array_elements(d->'values') LOOP
   IF g->>'sport' NOT IN ('running','cycling') THEN RAISE EXCEPTION 'unsupported sport'; END IF;
   SELECT value INTO STRICT b FROM jsonb_array_elements(d->'manifest'->'buckets') WHERE value->>'grouping'=g->>'sport';
   members:=b->'members';
   SELECT coalesce(jsonb_agg(role ORDER BY role COLLATE "C"),'[]'::jsonb) INTO roles
   FROM (SELECT m||'.'||f AS role FROM jsonb_array_elements_text(members) m
   CROSS JOIN unnest(ARRAY['elapsed_duration_ms','sport','start_epoch_seconds']) f) q;
   deriv:=binding||jsonb_build_object('members',members,'operand_roles',roles,'sport',g->'sport');
   FOREACH n IN ARRAY ARRAY['activity_count','elapsed_ms'] LOOP
    entries:=entries||jsonb_build_array(jsonb_build_object('path','/sports/'||(g->>'sport')||'/'||n,
    'type','numeric','payload',g->n,'values_kind','eligible','derivation',deriv));
   END LOOP;
  END LOOP;
 ELSIF d->>'metric_code'='training-volume-trend' THEN
  kind:=d->>'values_kind'; i:=0;
  FOR b IN SELECT value FROM jsonb_array_elements(d->'manifest'->'buckets') LOOP
   members:=b->'members';
   SELECT coalesce(jsonb_agg(role ORDER BY role COLLATE "C"),'[]'::jsonb) INTO roles
   FROM (SELECT m||'.'||f AS role FROM jsonb_array_elements_text(members) m
   CROSS JOIN unnest(ARRAY['elapsed_duration_ms','sport','start_epoch_seconds']) f) q;
   deriv:=binding||jsonb_build_object('members',members,'operand_roles',roles,'start_utc',b->'start_utc',
   'end_utc',b->'end_utc','limitations',b->'limitations');
   entries:=entries||jsonb_build_array(
   jsonb_build_object('path','/weeks/'||i||'/activity_count','type','numeric','payload',
   jsonb_build_object('status','available','unit','activity_count','precision','exact_integer','value',b->'count'),
   'values_kind',kind,'derivation',deriv),
   jsonb_build_object('path','/weeks/'||i||'/elapsed_ms','type','numeric','payload',b->'elapsed_ms',
   'values_kind',kind,'derivation',deriv)); i:=i+1;
  END LOOP;
  IF i NOT IN (0,4) THEN RAISE EXCEPTION 'invalid bucket count'; END IF;
  FOREACH n IN ARRAY ARRAY['earlier_total','later_total','signed_difference','magnitude','percentage'] LOOP
   IF n IN ('earlier_total','later_total') THEN
    paths:=CASE WHEN i=0 THEN '[]'::jsonb WHEN n='earlier_total' THEN '["/weeks/0/elapsed_ms","/weeks/1/elapsed_ms"]'::jsonb ELSE '["/weeks/2/elapsed_ms","/weeks/3/elapsed_ms"]'::jsonb END;
    deriv:=binding||jsonb_build_object('value_paths',paths,'required_week_indices',
    CASE WHEN n='earlier_total' THEN '["0","1"]'::jsonb ELSE '["2","3"]'::jsonb END,'effective_scope',d->'effective_scope');
   ELSE
    paths:=CASE WHEN n='percentage' THEN '["/signed_difference","/earlier_total"]'::jsonb ELSE '["/earlier_total","/later_total"]'::jsonb END;
    deriv:=binding||jsonb_build_object('value_paths',paths);
   END IF;
   entries:=entries||jsonb_build_array(jsonb_build_object('path','/'||n,'type','numeric','payload',d->'values'->n,'values_kind',kind,'derivation',deriv));
  END LOOP;
  IF d ? 'classification' THEN
   entries:=entries||jsonb_build_array(jsonb_build_object('path','/classification','type','sign_enum','payload',d->'classification','values_kind',kind,
   'derivation',binding||jsonb_build_object('value_paths','["/signed_difference"]'::jsonb)));
  END IF;
 ELSE RAISE EXCEPTION 'unsupported metric code'; END IF;
 SELECT jsonb_agg(value ORDER BY value->>'path' COLLATE "C") INTO entries FROM jsonb_array_elements(entries);
 RETURN jsonb_build_object('persistence_contract_version','datara/saved-recorded-aggregate/1',
 'registry_adapter_version','recorded-persistence-registry/1','entries',entries);
END $$;

CREATE FUNCTION datara_metric_complete_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE mid uuid; m datara_metric; d jsonb; r jsonb; op jsonb; expected jsonb; actual jsonb;
BEGIN
 IF TG_TABLE_NAME='datara_metric' THEN mid:=NEW.metric_id;
 ELSIF TG_TABLE_NAME='datara_metric_operand' THEN mid:=NEW.parent_metric_id;
 ELSE mid:=NEW.metric_id; END IF;
 IF mid IS NULL THEN RETURN NEW; END IF;
 SELECT * INTO STRICT m FROM datara_metric WHERE metric_id=mid;
 IF NOT EXISTS(SELECT 1 FROM datara_metric_seal WHERE metric_id=mid AND creation_txid=m.creation_txid)
 THEN RAISE EXCEPTION 'metric bundle requires its creation transaction seal'; END IF;
 d:=m.canonical_content::jsonb; r:=m.canonical_registry_content::jsonb; op:=m.canonical_operand_content::jsonb;
 IF jsonb_typeof(d) IS DISTINCT FROM 'object'
 OR jsonb_typeof(d->'operands') IS DISTINCT FROM 'array'
 OR jsonb_typeof(d->'manifest'->'buckets') IS DISTINCT FROM 'array'
 OR jsonb_typeof(d->'eligibility') IS DISTINCT FROM 'object'
 OR d->>'codec_version' IS DISTINCT FROM 'ascii-json-integer-strings/1'
 OR d->'manifest'->>'manifest_version' IS DISTINCT FROM 'recorded-membership/1'
 OR d->'method_identity'->>'adapter_version' IS DISTINCT FROM 'scoped-recorded-core/1'
 THEN RAISE EXCEPTION 'malformed or unsupported metric document'; END IF;
 IF m.registry_adapter_version<>'recorded-persistence-registry/1'
 OR m.operand_projection_version<>'recorded-source-operands/1'
 OR d->>'metric_contract_version' IS DISTINCT FROM m.metric_contract_version
 OR d->>'metric_code' IS DISTINCT FROM m.metric_code
 OR d->'method_identity' IS DISTINCT FROM m.method_identity
 OR d->>'supported_input_contract_version' IS DISTINCT FROM m.supported_input_contract_version
 OR d->>'input_content_digest' IS DISTINCT FROM m.input_content_digest
 OR m.metric_contract_version<>'datara/internal-recorded-metrics/1'
 OR m.supported_input_contract_version<>'datara-milestone-a/scoped-input/1'
 OR r IS DISTINCT FROM datara_recorded_registry(d) THEN RAISE EXCEPTION 'unsupported or inconsistent parent registry'; END IF;
 -- Rebuild operands directly from frozen parent bytes, not caller projection.
 SELECT coalesce(jsonb_agg(jsonb_build_object('role',value->'role','ordinal',ord-1,'source',value->'source') ORDER BY ord),'[]'::jsonb)
 INTO expected FROM jsonb_array_elements(d->'operands') WITH ORDINALITY q(value,ord);
 IF op IS DISTINCT FROM jsonb_build_object('operand_projection_version','recorded-source-operands/1','operands',expected)
 THEN RAISE EXCEPTION 'operand projection does not match parent'; END IF;
 IF EXISTS(SELECT 1 FROM jsonb_array_elements(expected) x GROUP BY x->>'role' HAVING count(*)<>1)
 OR EXISTS(SELECT 1 FROM datara_metric_operand WHERE parent_metric_id=mid AND dependency_metric_id IS NOT NULL)
 THEN RAISE EXCEPTION 'invalid source-only operand set'; END IF;
 SELECT coalesce(jsonb_agg(o.canonical_operand::jsonb ORDER BY o.ordinal),'[]'::jsonb) INTO actual FROM datara_metric_operand o WHERE parent_metric_id=mid;
 IF actual IS DISTINCT FROM expected OR EXISTS(
 SELECT 1 FROM datara_metric_operand o JOIN datara_evidence e ON e.evidence_id=o.source_evidence_id
 WHERE o.parent_metric_id=mid AND (e.kind<>'source_record' OR o.role IS DISTINCT FROM o.canonical_operand::jsonb->>'role'
 OR to_jsonb(o.ordinal) IS DISTINCT FROM o.canonical_operand::jsonb->'ordinal'
 OR e.field_path IS DISTINCT FROM o.canonical_operand::jsonb->'source'->>'source_field_path'
 OR e.value_canonical IS DISTINCT FROM o.canonical_operand::jsonb->'source'->>'value'))
 THEN RAISE EXCEPTION 'missing extra or inconsistent operands'; END IF;
 SELECT coalesce(jsonb_agg(e.value_canonical::jsonb ORDER BY e.value_path COLLATE "C"),'[]'::jsonb) INTO actual FROM datara_evidence e WHERE e.metric_id=mid;
 IF actual IS DISTINCT FROM r->'entries' OR EXISTS(SELECT 1 FROM datara_evidence e WHERE e.metric_id=mid
 AND e.value_path IS DISTINCT FROM e.value_canonical::jsonb->>'path')
 THEN RAISE EXCEPTION 'missing extra or inconsistent addressed evidence'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER datara_metric_insert BEFORE INSERT ON datara_metric FOR EACH ROW EXECUTE FUNCTION datara_metric_insert_guard();
CREATE TRIGGER datara_operand_insert BEFORE INSERT ON datara_metric_operand FOR EACH ROW EXECUTE FUNCTION datara_metric_insert_guard();
CREATE TRIGGER datara_seal_insert BEFORE INSERT ON datara_metric_seal FOR EACH ROW EXECUTE FUNCTION datara_metric_insert_guard();
CREATE TRIGGER datara_computed_insert BEFORE INSERT ON datara_evidence FOR EACH ROW EXECUTE FUNCTION datara_metric_insert_guard();
CREATE TRIGGER datara_metric_immutable BEFORE UPDATE OR DELETE ON datara_metric FOR EACH ROW EXECUTE FUNCTION datara_metric_immutable_guard();
CREATE TRIGGER datara_operand_immutable BEFORE UPDATE OR DELETE ON datara_metric_operand FOR EACH ROW EXECUTE FUNCTION datara_metric_immutable_guard();
CREATE TRIGGER datara_seal_immutable BEFORE UPDATE OR DELETE ON datara_metric_seal FOR EACH ROW EXECUTE FUNCTION datara_metric_immutable_guard();
CREATE TRIGGER datara_computed_immutable BEFORE UPDATE OR DELETE ON datara_evidence FOR EACH ROW EXECUTE FUNCTION datara_metric_immutable_guard();
CREATE CONSTRAINT TRIGGER datara_metric_complete AFTER INSERT ON datara_metric DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION datara_metric_complete_guard();
CREATE CONSTRAINT TRIGGER datara_operand_complete AFTER INSERT ON datara_metric_operand DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION datara_metric_complete_guard();
CREATE CONSTRAINT TRIGGER datara_seal_complete AFTER INSERT ON datara_metric_seal DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION datara_metric_complete_guard();
CREATE CONSTRAINT TRIGGER datara_computed_complete AFTER INSERT ON datara_evidence DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION datara_metric_complete_guard();
"""


class Migration(migrations.Migration):
    atomic = True
    dependencies = [("datara", "0001_initial")]
    operations = [
        migrations.AddConstraint(model_name="snapshot", constraint=models.UniqueConstraint(fields=["owner", "snapshot_id"], name="datara_snapshot_owner_id_uniq")),
        migrations.AddConstraint(model_name="evidence", constraint=models.UniqueConstraint(fields=["owner", "snapshot", "evidence_id"], name="datara_evidence_scope_id_uniq")),
        migrations.CreateModel(name="Metric", fields=[
            ("metric_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("content_digest", models.CharField(max_length=71)),
            ("metric_contract_version", models.CharField(max_length=64)),
            ("metric_code", models.CharField(max_length=64)),
            ("canonical_content", models.TextField()),
            ("method_identity", models.JSONField()),
            ("supported_input_contract_version", models.CharField(max_length=64)),
            ("input_content_digest", models.CharField(max_length=71)),
            ("registry_adapter_version", models.CharField(max_length=64)),
            ("canonical_registry_content", models.TextField()),
            ("registry_projection_digest", models.CharField(max_length=71)),
            ("operand_projection_version", models.CharField(max_length=64)),
            ("canonical_operand_content", models.TextField()),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("creation_txid", models.BigIntegerField(default=0, editable=False)),
            ("owner", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to=settings.AUTH_USER_MODEL)),
            ("snapshot", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.snapshot")),
        ], options={"db_table": "datara_metric", "constraints": [
            models.UniqueConstraint(fields=["owner", "snapshot", "content_digest"], name="datara_metric_owner_snapshot_digest_uniq"),
            models.UniqueConstraint(fields=["owner", "snapshot", "metric_id"], name="datara_metric_scope_id_uniq")]}),
        migrations.AddField(model_name="evidence", name="metric", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.metric")),
        migrations.AddField(model_name="evidence", name="value_path", field=models.CharField(blank=True, null=True, max_length=128)),
        migrations.AddConstraint(model_name="evidence", constraint=models.UniqueConstraint(fields=["owner", "snapshot", "metric", "value_path"], name="datara_computed_evidence_path_uniq")),
        migrations.CreateModel(name="MetricOperand", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("role", models.CharField(max_length=128)), ("ordinal", models.PositiveIntegerField()),
            ("canonical_operand", models.TextField()),
            ("dependency_value_path", models.CharField(blank=True, null=True, max_length=128)),
            ("owner", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to=settings.AUTH_USER_MODEL)),
            ("snapshot", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.snapshot")),
            ("parent_metric", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.metric")),
            ("source_evidence", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.evidence")),
            ("dependency_metric", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.metric")),
        ], options={"db_table": "datara_metric_operand", "constraints": [models.UniqueConstraint(fields=["parent_metric", "role", "ordinal"], name="datara_metric_operand_role_ordinal_uniq")]}),
        migrations.CreateModel(name="MetricSeal", fields=[
            ("metric", models.OneToOneField(primary_key=True, serialize=False, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.metric")),
            ("owner", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to=settings.AUTH_USER_MODEL)),
            ("snapshot", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="datara.snapshot")),
            ("creation_txid", models.BigIntegerField(default=0, editable=False)),
        ], options={"db_table": "datara_metric_seal"}),
        migrations.RunSQL(SQL),
        # First operation encountered in reverse, before any destructive action.
        migrations.RunPython(migrations.RunPython.noop, reverse_code=refuse_reverse),
    ]
