"""Explicit missing evaluators; caller attestations cannot implement these."""
MISSING_COVERAGE = (
    "generated_name_unique_mapping", "default_sequence_dependency_resolution",
    "type_function_operator_extension_dependencies", "index_opclass_opfamily_support",
    "inheritance_partition_dependencies", "transitive_role_access_policy",
    "signed_reference_scope_policy", "recorder_state_policy", "not_null_checks",
    "check_constraint_checks", "unique_constraint_checks", "foreign_key_checks",
    "sequence_headroom_cache_quiescence", "legacy_choices_json_lineage_digests",
    "ddl_writer_quiescence", "approved_dependency_migration_closure",
)

def evaluate_data_validity():
    return {"complete": False, "reason_codes": ["UNKNOWN_DATA_VALIDITY"], "checks": []}
