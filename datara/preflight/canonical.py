"""Strict JSON representation and conservative diagnostic structural identity."""
import hashlib
import json

FORMAT = "datara/syncdb-preflight/1"

def canonical_bytes(value):
    def validate(item):
        if item is None or type(item) in (str, int, bool):
            return
        if isinstance(item, list):
            for child in item:
                validate(child)
            return
        if isinstance(item, dict) and all(type(k) is str for k in item):
            for child in item.values():
                validate(child)
            return
        raise ValueError("UNSUPPORTED_JSON_VALUE")
    validate(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

def multiset(rows):
    """Sorting preserves duplicate objects; never collapse them into a mapping."""
    return sorted(rows, key=canonical_bytes)

# Diagnostic only. Generated object name mapping remains deliberately unimplemented.
OBSERVATION_FIELDS = frozenset({"owner", "nspacl", "relacl", "attacl", "full_definition"})

def structural_objects(observations):
    result = {}
    for key, rows in observations.items():
        if key in STRUCTURAL_QUERY_IDS:
            result[key] = multiset([{k: v for k, v in row.items() if k not in OBSERVATION_FIELDS and not (key == "catalog_02" and k == "datname")} for row in rows])
    return result

STRUCTURAL_QUERY_IDS = frozenset({"catalog_02", "catalog_03", "catalog_04", "catalog_05", "catalog_06", "catalog_07", "catalog_08", "catalog_09", "catalog_10", "catalog_11", "catalog_12", "catalog_20", "catalog_21"})



