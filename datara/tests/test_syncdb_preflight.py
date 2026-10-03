"""Synthetic/offline preflight regressions; WP02/WP03, CUS03-05/08/10.
SR05-11/20-21/28-29. Primary authored under synthetic testing approval.
No preserved database or adoption action is performed by these checks.
"""
import unittest

from datara.preflight.canonical import canonical_bytes, digest


class PreflightCanonicalRegressions(unittest.TestCase):
    def test_mapping_order_does_not_change_fingerprint(self):
        left = {"columns": [{"name": "owner_id", "nullable": False}], "format": "v1"}
        right = {"format": "v1", "columns": [{"nullable": False, "name": "owner_id"}]}
        self.assertEqual(canonical_bytes(left), canonical_bytes(right))
        self.assertEqual(digest(left), digest(right))

    def test_null_false_and_zero_remain_distinct(self):
        values = [None, False, 0, "0", "", []]
        encoded = [canonical_bytes({"value": value}) for value in values]
        self.assertEqual(len(set(encoded)), len(values))

    def test_ordered_keys_and_duplicate_entries_are_preserved(self):
        self.assertNotEqual(digest({"keys": ["owner_id", "snapshot_id"]}),
                            digest({"keys": ["snapshot_id", "owner_id"]}))
        row = {"column": "owner_id", "kind": "fk"}
        self.assertNotEqual(digest({"objects": [row]}), digest({"objects": [row, row]}))

    def test_unicode_object_names_are_not_silently_normalized(self):
        self.assertNotEqual(digest({"name": "\u00e9"}), digest({"name": "e\u0301"}))

    def test_float_catalog_values_refuse_instead_of_rounding(self):
        for value in (1.0, float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises((TypeError, ValueError)):
                    canonical_bytes({"value": value})

    def test_fingerprint_changes_for_nullability_or_icu_rule_drift(self):
        baseline = {"column": {"nullable": False, "collicurules": None}}
        for changed in ({"column": {"nullable": True, "collicurules": None}},
                        {"column": {"nullable": False, "collicurules": "&a<b"}}):
            self.assertNotEqual(digest(baseline), digest(changed))

from datara.preflight.canonical import FORMAT
from datara.preflight.compare import compare


class PreflightComparisonRegressions(unittest.TestCase):
    def inputs(self, rows=None):
        rows = [{"attname": "owner_id", "attnotnull": True, "collicurules": None}] if rows is None else rows
        manifest = {"format": FORMAT, "baseline_input_hashes": {},
                    "observations": {"catalog_05": rows},
                    "schemas": ["public"], "relations": [["public", "synthetic"]]}
        inventory = {"format": FORMAT, "observations": {"catalog_05": [dict(row) for row in rows]},
                     "covered_query_ids": [], "errors": []}
        return manifest, inventory, {}

    def test_equal_observed_catalog_does_not_claim_adoption_eligibility(self):
        report = compare(*self.inputs())
        self.assertEqual(report["exit_code"], 3)
        self.assertFalse(report["eligible"])
        self.assertFalse(report["data_validity_complete"])
        self.assertIn("UNKNOWN_DATA_VALIDITY", report["reason_codes"])

    def test_caller_coverage_claims_cannot_enable_eligibility(self):
        manifest, inventory, policy = self.inputs()
        inventory.update(eligible=True, data_validity_complete=True, missing_coverage=[],
                         covered_query_ids=["all_required_checks"])
        policy.update(approved=True, complete=True, data_validity_complete=True)
        report = compare(manifest, inventory, policy)
        self.assertNotEqual(report["exit_code"], 0)
        self.assertFalse(report["eligible"])
        self.assertTrue(report["missing_coverage"])

    def test_nullability_and_icu_rule_drift_are_observed(self):
        for key, value in (("attnotnull", False), ("collicurules", "&a<b")):
            with self.subTest(field=key):
                manifest, inventory, policy = self.inputs()
                inventory["observations"]["catalog_05"][0][key] = value
                report = compare(manifest, inventory, policy)
                self.assertEqual(report["exit_code"], 2)
                self.assertIn("OBSERVED_CATALOG_DRIFT", report["reason_codes"])
                self.assertFalse(report["eligible"])

    def test_duplicate_objects_are_not_collapsed(self):
        manifest, inventory, policy = self.inputs()
        inventory["observations"]["catalog_05"].append(dict(inventory["observations"]["catalog_05"][0]))
        report = compare(manifest, inventory, policy)
        self.assertEqual(report["exit_code"], 2)
        difference = next(d for d in report["differences"] if d["category"] == "catalog_05" and d["status"] == "different")
        self.assertEqual(difference["reference_count"], 1)
        self.assertEqual(difference["inventory_count"], 2)

    def test_unordered_catalog_rows_compare_as_multisets(self):
        manifest, inventory, policy = self.inputs([{ "attname": "id"}, {"attname": "owner_id"}])
        inventory["observations"]["catalog_05"].reverse()
        report = compare(manifest, inventory, policy)
        self.assertNotIn("OBSERVED_CATALOG_DRIFT", report["reason_codes"])
        self.assertFalse(report["eligible"])

    def test_missing_inventory_and_collection_error_refuse(self):
        for replacement in (None, {}):
            manifest, inventory, policy = self.inputs()
            inventory["observations"] = replacement
            inventory["errors"] = [{"code": "UNKNOWN_COLLECTION_ERROR", "sqlstate": "42501"}]
            report = compare(manifest, inventory, policy)
            self.assertNotEqual(report["exit_code"], 0)
            self.assertIn("UNKNOWN_COLLECTION_ERROR", report["reason_codes"])
            self.assertFalse(report["eligible"])

    def test_database_name_is_observational_but_icu_rules_are_structural(self):
        manifest, inventory, policy = self.inputs()
        row = {"datname": "synthetic_reference", "encoding": "UTF8", "daticurules": None}
        manifest["observations"]["catalog_02"] = [row]
        inventory["observations"]["catalog_02"] = [dict(row, datname="synthetic_candidate")]
        report = compare(manifest, inventory, policy)
        self.assertNotIn("OBSERVED_CATALOG_DRIFT", report["reason_codes"])
        inventory["observations"]["catalog_02"][0]["daticurules"] = "&a<b"
        self.assertIn("OBSERVED_CATALOG_DRIFT", compare(manifest, inventory, policy)["reason_codes"])

    def test_index_collation_drift_is_not_omitted(self):
        manifest, inventory, policy = self.inputs()
        row = {"index_name": "public.synthetic_idx", "key_ordinal": 1, "collicurules": None}
        manifest["observations"]["catalog_20"] = [row]
        inventory["observations"]["catalog_20"] = [dict(row, collicurules="&a<b")]
        report = compare(manifest, inventory, policy)
        self.assertEqual(report["exit_code"], 2)
        self.assertTrue(any(d["category"] == "catalog_20" for d in report["differences"]))

    def test_role_metadata_difference_never_claims_access_policy_pass(self):
        manifest, inventory, policy = self.inputs()
        manifest["observations"]["catalog_13"] = [{"rolname": "reference_role", "rolsuper": False}]
        inventory["observations"]["catalog_13"] = [{"rolname": "candidate_role", "rolsuper": False}]
        report = compare(manifest, inventory, policy)
        self.assertFalse(report["eligible"])
        self.assertIn("transitive_role_access_policy", report["missing_coverage"])


class PreflightInputRegressions(unittest.TestCase):
    def test_malformed_catalog_rows_refuse(self):
        manifest, inventory, policy = PreflightComparisonRegressions().inputs()
        inventory['observations']['catalog_05'] = [None]
        with self.assertRaisesRegex(ValueError, 'INVALID_CATALOG_ROWS'):
            compare(manifest, inventory, policy)

    def test_fixed_queries_have_stable_ids_and_select_only(self):
        from datara.preflight.catalog import QUERIES, QUERY_NAMES
        self.assertEqual(set(QUERIES), {f'catalog_{number:02}' for number in range(1, 22)})
        self.assertEqual(set(QUERIES), set(QUERY_NAMES))
        for query in QUERIES.values():
            self.assertTrue(query.lstrip().startswith('SELECT '))

    def test_json_duplicate_keys_and_float_values_refuse(self):
        import tempfile
        from pathlib import Path
        from scripts.syncdb_preflight import load_json
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic.json'
            for value in ('{"a":1,"a":2}', '{"a":1.0}', '{"a":NaN}'):
                path.write_text(value, encoding='utf-8')
                with self.assertRaises(ValueError):
                    load_json(path)

    def test_invalid_cli_arguments_do_not_echo_values(self):
        import io
        from contextlib import redirect_stdout, redirect_stderr
        from scripts.syncdb_preflight import main
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = main(['compare', '--synthetic-invalid=private-marker'])
        self.assertEqual(code, 3)
        self.assertEqual(output.getvalue() + errors.getvalue(), '')

    def test_existing_output_is_preserved(self):
        import tempfile
        from pathlib import Path
        from scripts.syncdb_preflight import private_output
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic.json'
            path.write_bytes(b'existing-evidence')
            with self.assertRaises(FileExistsError):
                private_output(path, {'eligible': False})
            self.assertEqual(path.read_bytes(), b'existing-evidence')


from django.test import TransactionTestCase


class PreflightPostgreSQLRegressions(TransactionTestCase):
    def test_fixed_collector_on_disposable_synthetic_database(self):
        import os
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from django.db import connection
        from datara.preflight.catalog import collect, QUERIES
        settings = connection.settings_dict
        self.assertTrue(settings['NAME'].startswith('test_datara_'))
        self.assertEqual(connection.vendor, 'postgresql')
        def libpq_quote(value):
            return "'" + str(value).replace('\\', '\\\\').replace("'", "\\'") + "'"
        with tempfile.TemporaryDirectory(prefix='datara-synthetic-preflight-') as folder:
            service = Path(folder) / 'pg_service.conf'
            service.write_text('[synthetic_preflight]\n' + '\n'.join(
                key + '=' + libpq_quote(settings[field])
                for key, field in [('host', 'HOST'), ('port', 'PORT'), ('dbname', 'NAME'), ('user', 'USER')]
            ) + '\n', encoding='utf-8')
            with connection.cursor() as cursor:
                tables = connection.introspection.table_names(cursor)
            manifest = {'format': FORMAT, 'baseline_input_hashes': {}, 'schemas': ['public'],
                        'relations': [['public', table] for table in tables],
                        'recorder': ['public', 'django_migrations']}
            with patch.dict(os.environ, {'PGSERVICEFILE': str(service), 'PGPASSWORD': settings['PASSWORD']}):
                inventory = collect('synthetic_preflight', manifest, {'roles': [settings['USER']]})
        self.assertEqual(inventory['errors'], [])
        self.assertTrue(set(QUERIES).issubset(inventory['covered_query_ids']))
        self.assertTrue({'acl_relations', 'acl_namespaces', 'acl_database', 'acl_columns',
                         'database_privileges', 'recorder_observations'}.issubset(inventory['covered_query_ids']))
        identity = inventory['observations']['catalog_01'][0]
        self.assertEqual(identity['read_only'], 'on')
        self.assertEqual(identity['isolation'], 'repeatable read')
        self.assertFalse(inventory['eligible'])
        self.assertEqual(len(inventory['structural_hash']), 64)


class PreflightEvidenceBindingRegressions(unittest.TestCase):
    def test_parser_and_hash_use_the_same_single_byte_read(self):
        import hashlib
        from pathlib import Path
        from unittest.mock import patch
        from scripts.syncdb_preflight import load_json_with_hash
        raw = b'\xef\xbb\xbf{"a":1}'
        with patch.object(Path, 'read_bytes', return_value=raw) as read:
            value, fingerprint = load_json_with_hash('synthetic.json')
        read.assert_called_once()
        self.assertEqual(value, {'a': 1})
        self.assertEqual(fingerprint, hashlib.sha256(raw).hexdigest())

    def test_offline_cli_preserves_exact_inputs_and_source_hashes(self):
        import hashlib
        import json
        import tempfile
        from pathlib import Path
        from scripts.syncdb_preflight import main
        manifest, inventory, policy = PreflightComparisonRegressions().inputs()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = {}
            expected = {}
            for name, content in [('manifest', manifest), ('inventory', inventory), ('policy', policy)]:
                paths[name] = root / (name + '.json')
                raw = b'\xef\xbb\xbf' + json.dumps(content).encode('utf-8')
                paths[name].write_bytes(raw)
                expected[name] = hashlib.sha256(raw).hexdigest()
            output = root / 'output.json'
            args = ['compare', '--output', str(output)]
            for name, path in paths.items():
                args.extend(['--' + name, str(path)])
            self.assertEqual(main(args), 3)
            report = json.loads(output.read_bytes())
        self.assertEqual(report['input_file_hashes'], expected)
        self.assertEqual(len(report['source_file_hashes']), 6)
        self.assertEqual(report['implementation_source_hash'], digest(report['source_file_hashes']))
        self.assertFalse(report['eligible'])
