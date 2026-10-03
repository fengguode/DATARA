from .canonical import FORMAT, STRUCTURAL_QUERY_IDS, canonical_bytes, digest, structural_objects
from .data_checks import MISSING_COVERAGE

def compare(manifest, inventory, policy):
    """Compare observed catalogs offline; diagnostic differences are conservative.

    Manifest: {format, baseline_input_hashes, observations, schemas, relations}.
    Inventory: {format, observations, covered_query_ids, errors}.
    Policy is retained as hashed evidence, never interpreted as executable SQL.
    No user coverage claims can enable eligibility in this bounded implementation.
    """
    for value in (manifest, inventory, policy):
        canonical_bytes(value)
        if not isinstance(value, dict):
            raise ValueError("INVALID_INPUT_SHAPE")
    reasons = set()
    differences = []
    if manifest.get("format") != FORMAT or inventory.get("format") != FORMAT:
        reasons.add("UNKNOWN_FORMAT")
    expected = manifest.get("observations")
    actual = inventory.get("observations")
    if not isinstance(expected, dict) or not isinstance(actual, dict):
        reasons.add("UNKNOWN_REFERENCE_OR_INVENTORY")
    else:
        if not all(type(rows) is list and all(type(row) is dict for row in rows) for rows in list(expected.values()) + list(actual.values())):
            raise ValueError("INVALID_CATALOG_ROWS")
        absent = sorted(STRUCTURAL_QUERY_IDS - (set(expected) & set(actual)))
        if absent:
            reasons.add("UNKNOWN_CATALOG_COVERAGE")
            differences.extend({"category": category, "status": "mandatory_category_unobserved"} for category in absent)
        left, right = structural_objects(expected), structural_objects(actual)
        for category in sorted(set(left) | set(right)):
            if category not in left or category not in right:
                reasons.add("UNKNOWN_CATALOG_COVERAGE")
                differences.append({"category": category, "status": "missing_category"})
            elif canonical_bytes(left[category]) != canonical_bytes(right[category]):
                reasons.add("OBSERVED_CATALOG_DRIFT")
                differences.append({"category": category, "status": "different", "reference_hash": digest(left[category]), "inventory_hash": digest(right[category]), "reference_count": len(left[category]), "inventory_count": len(right[category])})
    reasons.update({"UNKNOWN_IMPLEMENTATION_COVERAGE", "UNKNOWN_DATA_VALIDITY"})
    if inventory.get("errors"):
        reasons.add("UNKNOWN_COLLECTION_ERROR")
    return {"format": FORMAT, "exit_code": 2 if "OBSERVED_CATALOG_DRIFT" in reasons else 3,
            "eligible": False, "data_validity_complete": False,
            "comparison_scope": "conservative_catalog_diagnostics",
            "input_hashes": {"manifest": digest(manifest), "inventory": digest(inventory), "policy": digest(policy)},
            "reason_codes": sorted(reasons), "missing_coverage": list(MISSING_COVERAGE), "differences": differences}

