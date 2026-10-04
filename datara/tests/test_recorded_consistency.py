"""Synthetic complete-UTC-day consistency oracles; WP03 CUS03-05 SR05-11/SR28-29."""
from dataclasses import replace
import json

from django.test import SimpleTestCase

from datara.recorded_consistency import (
    prepare_recorded_consistency, canonical_consistency_content,
)
from datara.recorded_metrics import RecordedInputRefusal
from datara.tests.test_recorded_regressions import prepared, bypass
from datara.tests.test_scoped_input import identity, _epoch


class RecordedConsistencyTests(SimpleTestCase):
    def result(self, rows=(), start="2026-09-01T00:00:00Z", end="2026-09-29T00:00:00Z"):
        return prepare_recorded_consistency(prepared(rows, start=start, end=end)[1])

    def counts(self, result):
        values = (result.evaluated_day_count, result.active_day_count,
                  result.longest_active_streak, result.longest_no_record_streak)
        self.assertTrue(all(value.unit == "day_count" for value in values))
        return tuple(value.integer for value in values)

    def test_complete_28_days_and_all_gaps(self):
        result = self.result([(1, "2026-09-04T10:00:00Z", 1000, "running"),
                              (2, "2026-09-05T10:00:00Z", 1000, "running")])
        self.assertTrue(result.eligible)
        self.assertEqual(self.counts(result), (28, 2, 2, 23))
        self.assertEqual(len(result.days), 28)
        self.assertEqual(result.days[0].start_epoch_seconds, _epoch("2026-09-01T00:00:00Z"))
        self.assertEqual(result.days[-1].end_epoch_seconds, _epoch("2026-09-29T00:00:00Z"))

    def test_leading_gap_counts(self):
        result = self.result([(1, "2026-09-27T10:00:00Z", 1000, "running")])
        self.assertEqual(self.counts(result), (28, 1, 1, 26))

    def test_multiple_sports_and_duration_do_not_duplicate_days(self):
        result = self.result([(1, "2026-09-01T23:59:59Z", 86400000, "running"),
                              (2, "2026-09-01T06:00:00Z", 1000, "cycling"),
                              (3, "2026-09-02T00:00:00Z", 1000, "running")])
        self.assertEqual(self.counts(result), (28, 2, 2, 26))
        self.assertEqual(result.days[0].activity_count.integer, 2)
        self.assertEqual(result.days[0].members, tuple(sorted((identity(1), identity(2)))))
        self.assertEqual(result.days[1].activity_count.integer, 1)
        self.assertFalse(result.days[2].recorded_active)

    def test_partial_edge_only_activity_retained_and_disclosed(self):
        result = self.result([(1, "2026-09-01T13:00:00Z", 1000, "running"),
                              (2, "2026-09-30T01:00:00Z", 1000, "cycling")],
                             start="2026-09-01T12:00:00Z", end="2026-09-30T12:00:00Z")
        self.assertTrue(result.eligible)
        self.assertEqual(self.counts(result), (28, 0, 0, 28))
        self.assertEqual(result.outside_effective, tuple(sorted((identity(1), identity(2)))))
        self.assertEqual(result.days[0].start_epoch_seconds, _epoch("2026-09-02T00:00:00Z"))
        self.assertEqual(result.days[-1].end_epoch_seconds, _epoch("2026-09-30T00:00:00Z"))
        self.assertIn(b"partial", canonical_consistency_content(result))

    def test_28_elapsed_days_with_partial_edges_has_only_27_complete_days(self):
        result = self.result([(1, "2026-09-02T06:00:00Z", 1000, "running")],
                             start="2026-09-01T12:00:00Z", end="2026-09-29T12:00:00Z")
        self.assertFalse(result.eligible)
        self.assertIn("scope_less_than_28_complete_days", result.unmet_reasons)
        self.assertEqual(self.counts(result), (27, 1, 1, 26))

    def test_no_included_activity_is_explicit(self):
        result = self.result()
        self.assertFalse(result.eligible)
        self.assertIn("no_included_activity", result.unmet_reasons)
        self.assertEqual(self.counts(result), (28, 0, 0, 28))

    def test_zero_complete_days_has_no_buckets_and_zero_runs(self):
        result = self.result([(1, "2026-09-01T13:00:00Z", 1000, "running")],
                             start="2026-09-01T12:00:00Z", end="2026-09-01T18:00:00Z")
        self.assertFalse(result.eligible)
        self.assertEqual(result.days, ())
        self.assertEqual(self.counts(result), (0, 0, 0, 0))
        self.assertEqual(result.outside_effective, (identity(1),))

    def test_single_day_counts_even_when_ineligible(self):
        result = self.result([(1, "2026-09-01T00:00:00Z", 1000, "running")],
                             end="2026-09-02T00:00:00Z")
        self.assertFalse(result.eligible)
        self.assertEqual(self.counts(result), (1, 1, 1, 0))

    def test_end_boundary_excluded_and_exclusion_bound(self):
        rows = [(1, "2026-09-01T00:00:00Z", 1000, "running"),
                (2, "2026-09-29T00:00:00Z", 1000, "running")]
        result = self.result(rows)
        self.assertEqual(self.counts(result), (28, 1, 1, 27))
        self.assertNotIn(identity(2), tuple(member for day in result.days for member in day.members))
        self.assertNotEqual(canonical_consistency_content(result),
                            canonical_consistency_content(self.result(rows[:1])))

    def test_order_independent_exact_portable_canonical_bytes(self):
        rows = [(2, "2026-09-02T00:00:00Z", 1000, "running"),
                (1, "2026-09-01T00:00:00Z", 1000, "cycling")]
        first, second = self.result(rows), self.result(rows[::-1])
        content = canonical_consistency_content(first)
        self.assertEqual(content, canonical_consistency_content(second))
        payload = json.loads(content)
        self.assertEqual(content, json.dumps(payload, ensure_ascii=True, sort_keys=True,
                         separators=(",", ":")).encode("ascii"))
        self.assertIn(b"datara/internal-recorded-consistency/1", content)
        self.assertNotIn(b"owner_id", content)

    def test_bypassed_results_and_forged_bytes_refused(self):
        result = self.result([(1, "2026-09-01T00:00:00Z", 1000, "running")])
        mutations = {"eligible": False, "days": (), "outside_effective": (identity(1),),
                     "canonical_content": b"{}", "source": None,
                     "evaluated_day_count": replace(result.evaluated_day_count, integer=27)}
        for field, value in mutations.items():
            with self.subTest(field=field), self.assertRaises(RecordedInputRefusal):
                canonical_consistency_content(bypass(result, **{field: value}))
        with self.assertRaises(RecordedInputRefusal):
            canonical_consistency_content(bypass(result, eligible=1))

    def test_bypassed_input_refused(self):
        data = prepared([(1, "2026-09-01T00:00:00Z", 1000, "running")])[1]
        with self.assertRaises(RecordedInputRefusal):
            prepare_recorded_consistency(bypass(data, source_canonical_content=b"{}"))
