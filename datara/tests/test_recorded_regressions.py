"""Synthetic regression authoring for WP02/WP03.

CUS03-05/CUS08/CUS10; SR05-11/SR20-21/SR28-29. These focused
source and persistence tests are not model, rendered UI or athlete validation.
All inputs reuse DATARA-authored synthetic fixtures; no FIT bytes are read.
"""
from dataclasses import replace
from fractions import Fraction
import json
from unittest import mock

from django.test import SimpleTestCase, TestCase

from datara import models as m
from datara.metric_projection import project_recorded_result
from datara.normalization import canonical_json, sha256_digest
from datara.provenance import ProvenanceIncomplete, VALUE_CLASS_SOURCE_OBSERVATION, build_ledger
from datara.recorded_metrics import (
    RecordedInputRefusal, canonical_metric_content, prepare_overall_trend,
    prepare_recorded_input, summarize_recorded,
)
from datara.scoped_input import InputFieldSpec, prepare_scoped_input
from datara.tests.test_scoped_input import (
    SYNTHETIC_POLICY, _Owner, _epoch, identity, make_record, make_scope,
)

CORE = tuple(InputFieldSpec(name, VALUE_CLASS_SOURCE_OBSERVATION, True)
             for name in ("sport", "start_epoch_seconds", "elapsed_duration_ms"))


def prepared(rows, *, start="2026-08-31T00:00:00Z", end="2026-10-02T00:00:00Z"):
    """Rows state UTC starts and exact milliseconds independently of arithmetic."""
    records = [make_record(canonical_identity=identity(n), start=_epoch(utc),
                           elapsed_ms=elapsed, sport=sport,
                           sport_code=1 if sport == "running" else 2, declared=CORE)
               for n, utc, elapsed, sport in rows]
    version = prepare_scoped_input(scope=make_scope(start_utc=start, end_utc=end),
                                  records=records, field_specs=CORE, policy=SYNTHETIC_POLICY)
    return version, prepare_recorded_input(version)


def bypass(value, **changes):
    """Simulate a caller bypassing frozen dataclass constructor validation."""
    clone = object.__new__(type(value))
    for name in value.__dataclass_fields__:
        object.__setattr__(clone, name, changes.get(name, getattr(value, name)))
    return clone


class RecordedArithmeticRegressions(SimpleTestCase):
    def test_summary_and_registry_bind_count_and_elapsed_to_exact_sources(self):
        version, data = prepared([
            (1, "2026-09-01T06:00:00Z", 1001, "running"),
            (2, "2026-09-02T06:00:00Z", 2002, "running"),
            (3, "2026-09-03T06:00:00Z", 9009, "cycling"),
        ])
        result = summarize_recorded(data)
        self.assertTrue(result.eligible)
        self.assertEqual([(g.sport, g.activity_count.integer, g.elapsed_ms.integer)
                          for g in result.groups], [("cycling", 1, 9009), ("running", 2, 3003)])
        projection = project_recorded_result(result)
        document = json.loads(projection.canonical_content)
        self.assertEqual(document["input_content_digest"], version.input_digest)
        self.assertEqual(projection.canonical_content, result.canonical_content)
        entries = {e["path"]: e for e in projection.registry_document()["entries"]}
        expected = {"cycling": [identity(3)], "running": [identity(1), identity(2)]}
        for sport, members in expected.items():
            for name in ("activity_count", "elapsed_ms"):
                derivation = entries[f"/sports/{sport}/{name}"]["derivation"]
                self.assertEqual(derivation["members"], members)
                self.assertEqual(derivation["manifest_path"], "/manifest")
                self.assertEqual(derivation["operand_roles"], sorted(
                    f"{member}.{field}" for member in members
                    for field in ("elapsed_duration_ms", "sport", "start_epoch_seconds")))
        operands = projection.operand_document()["operands"]
        self.assertEqual([o["ordinal"] for o in operands], list(range(9)))
        records = {r.canonical_identity: r for r in version.records}
        for operand in operands:
            member, field = operand["role"].rsplit(".", 1)
            record = records[member]
            self.assertEqual(operand["source"], {
                "source_digest": record.source_digest, "normalization_digest": member,
                "source_field_path": f"{member}.{field}",
                "preparation_version": record.preparation_version,
                "mapping_reference": record.mapping_reference,
                "value": record.field(field).value_canonical,
            })
        view = projection.registry_document()
        view["entries"].clear()
        self.assertEqual(len(projection.registry_document()["entries"]), 6)

    def test_four_complete_monday_weeks_ignore_in_scope_partial_week(self):
        _, data = prepared([
            (11, "2026-08-31T00:00:00Z", 1000, "running"),
            (12, "2026-09-07T00:00:00Z", 2000, "cycling"),
            (13, "2026-09-14T00:00:00Z", 4000, "running"),
            (14, "2026-09-21T00:00:00Z", 8000, "cycling"),
            (15, "2026-09-28T00:00:00Z", 999000, "running"),
        ])
        result = prepare_overall_trend(data)
        self.assertTrue(result.eligible)
        self.assertEqual([w.elapsed_ms.integer for w in result.weeks], [1000, 2000, 4000, 8000])
        self.assertEqual([w.activity_count.integer for w in result.weeks], [1, 1, 1, 1])
        self.assertEqual(result.outside_comparison, (identity(15),))
        self.assertEqual((result.earlier_total.integer, result.later_total.integer,
                          result.signed_difference.integer, result.magnitude.integer),
                         (3000, 12000, 9000, 9000))
        self.assertEqual(result.percentage.fraction, Fraction(300, 1))
        self.assertEqual(result.classification, "increased")
        entries = {e["path"]: e for e in project_recorded_result(result).registry_document()["entries"]}
        self.assertEqual(entries["/earlier_total"]["derivation"]["value_paths"],
                         ["/weeks/0/elapsed_ms", "/weeks/1/elapsed_ms"])
        self.assertEqual(entries["/percentage"]["derivation"]["value_paths"],
                         ["/signed_difference", "/earlier_total"])
        self.assertEqual(entries["/classification"]["payload"], "increased")

    def test_insufficient_scope_exports_unavailable_without_fabricated_week_paths(self):
        _, data = prepared([(21, "2026-10-01T06:00:00Z", 1000, "running")],
                           start="2026-10-01T00:00:00Z", end="2026-10-02T00:00:00Z")
        result = prepare_overall_trend(data)
        self.assertFalse(result.eligible)
        self.assertEqual(result.unmet_reasons,
                         ("scope_less_than_28_days", "fewer_than_four_complete_weeks"))
        self.assertEqual(result.weeks, ())
        self.assertIsNone(result.earlier_total.integer)
        self.assertEqual(result.earlier_total.unavailable_reason, "insufficient_scope")
        entries = {e["path"]: e for e in project_recorded_result(result).registry_document()["entries"]}
        self.assertNotIn("/classification", entries)
        self.assertFalse(any(path.startswith("/weeks/") for path in entries))
        self.assertEqual(entries["/earlier_total"]["derivation"]["value_paths"], [])
        self.assertNotIn("value", entries["/earlier_total"]["payload"])

    def test_forged_typed_values_bytes_and_source_bindings_are_revalidated(self):
        _, data = prepared([(31, "2026-09-01T00:00:00Z", 1000, "running")])
        summary = summarize_recorded(data)
        mutations = [
            bypass(summary, eligible=False),
            bypass(summary, groups=()),
            bypass(summary, canonical_content=summary.canonical_content + b"\n"),
            bypass(summary, canonical_content=b"{}"),
            bypass(summary, source=bypass(data, input_content_digest="sha256:" + "0" * 64)),
            bypass(summary, source=bypass(data, source_canonical_content=b"{}")),
            bypass(summary, source=bypass(data, members=())),
        ]
        for forged in mutations:
            with self.subTest(forged=forged.canonical_content[:20]):
                for export in (canonical_metric_content, project_recorded_result):
                    with self.assertRaises(RecordedInputRefusal):
                        export(forged)
        with self.assertRaises(RecordedInputRefusal):
            replace(summary, canonical_content=b"{}")

    def test_self_consistent_payload_with_malformed_mandatory_integer_is_refused(self):
        version, _ = prepared([(41, "2026-09-01T00:00:00Z", 1000, "running")])
        # Repair the bytes and digest as an attacker could: the semantic integer
        # check must still refuse, rather than merely relying on a stale hash.
        for bad in ("01000", "1000.0", "-1000", "0", "true"):
            record = version.records[0]
            fields = tuple(replace(f, value_canonical=bad) if f.field_name == "elapsed_duration_ms"
                           else f for f in record.fields)
            forged_record = bypass(record, fields=fields)
            payload = json.loads(version.canonical_payload)
            payload["records"] = [forged_record.as_record()]
            text = canonical_json(payload)
            forged = bypass(version, records=(forged_record,), canonical_payload=text,
                            input_digest=sha256_digest(text), ledger=build_ledger(((forged_record.canonical_identity, forged_record.source_digest, forged_record.fields),)))
            with self.subTest(value=bad), self.assertRaises(RecordedInputRefusal):
                prepare_recorded_input(forged)


class ScopedSnapshotAtomicRegressions(TestCase):
    def setUp(self):
        self.owner = _Owner("recorded-atomic")
        self.owner.add_accepted(start_utc="2026-10-01T06:00:00Z")
        scope = make_scope()
        self.version = prepare_scoped_input(
            scope=scope, records=self.owner.inputs.scope_candidates(scope, CORE),
            field_specs=CORE, policy=SYNTHETIC_POLICY)

    def test_second_evidence_failure_rolls_back_snapshot_and_first_row_then_retry(self):
        original = self.owner.store.record_evidence
        calls = []

        def fail_second(*args, **kwargs):
            calls.append(kwargs["field_path"])
            if len(calls) == 2:
                raise RuntimeError("synthetic second evidence failure")
            return original(*args, **kwargs)

        with mock.patch.object(self.owner.store, "record_evidence", side_effect=fail_second):
            with self.assertRaisesRegex(RuntimeError, "synthetic second evidence failure"):
                self.owner.inputs.append_version(self.version)
        self.assertEqual(len(calls), 2)
        self.assertEqual(m.Snapshot.objects.for_owner(self.owner.user.pk).count(), 0)
        self.assertEqual(m.Evidence.objects.for_owner(self.owner.user.pk).count(), 0)
        saved = self.owner.inputs.append_version(self.version)
        self.assertTrue(saved.created)
        self.assertEqual(len(self.owner.inputs.provenance_rows(saved.version_ref)), 5)
        self.assertFalse(self.owner.inputs.append_version(self.version).created)
        self.assertEqual(m.Snapshot.objects.for_owner(self.owner.user.pk).count(), 1)
        self.assertEqual(m.Evidence.objects.for_owner(self.owner.user.pk).count(), 5)

    def test_existing_incomplete_history_is_refused_without_repair(self):
        # Deliberately incomplete historical writer: save the Snapshot but omit
        # its source Evidence rows, avoiding mutation of immutable history.
        snapshot = self.owner.store.record_snapshot(
            self.version, self.owner.inputs.resolve_activity_ids(self.version.included_digests))
        with self.assertRaises(ProvenanceIncomplete):
            self.owner.inputs.append_version(self.version)
        self.assertEqual(m.Snapshot.objects.for_owner(self.owner.user.pk).count(), 1)
        self.assertEqual(m.Evidence.objects.for_owner(self.owner.user.pk).count(), 0)
        self.assertEqual(self.owner.inputs.get_version(snapshot.pk).input_digest, self.version.input_digest)

    def test_source_provenance_reader_returns_only_source_rows(self):
        saved = self.owner.inputs.append_version(self.version)
        rows = self.owner.inputs.provenance_rows(saved.version_ref)
        self.assertEqual({row["field_path"] for row in rows}, set(self.version.all_field_paths()))
        self.assertTrue(all(row.get("method_version") is None for row in rows))
        other = _Owner("recorded-foreign")
        with self.assertRaises(m.ResourceNotVisible):
            other.inputs.get_version(saved.version_ref)
        with self.assertRaises(m.ResourceNotVisible):
            other.inputs.provenance_rows(saved.version_ref)

