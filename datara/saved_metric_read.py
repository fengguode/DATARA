"""Read-only WP05 projection for owner-bound saved recorded metrics.

CUS09/CUS10; SR19-SR21/SR31/SR73. This module adapts existing persisted
records. It never prepares, saves, or recalculates a metric for a request.
"""
from __future__ import annotations

import json
import math
import re
from uuid import UUID

from django.urls import reverse

from datara import models as m
from datara.metric_projection import (
    CODEC_VERSION,
    MANIFEST_VERSION,
    PURE_ADAPTER_VERSION,
    PURE_CONTRACT_VERSION,
    READER_VERSION,
    REGISTRY_ADAPTER_VERSION,
    SOURCE_CONTRACT_VERSION,
)
from datara.metric_store import MetricStoreRefusal, SavedMetricStore
from datara.recorded_metrics import METRIC_CONTRACT_VERSION, _SPECIFICATION_DIGEST

API_VERSION = "datara/recorded-metric-read/1"
ERRORS = {
    "authentication_required": "Sign in to view saved recorded metrics.",
    "operation_denied": "This read operation is not permitted.",
    "method_not_allowed": "Use GET or HEAD for this read resource.",
    "rate_limited": "Too many read requests. Try again later.",
    "invalid_request": "This read resource accepts no query parameters or request body.",
    "resource_not_available": "The requested resource is not available.",
    "retrieval_unavailable": "Saved detail cannot be retrieved now. Try again later.",
}
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")
_NONCOMPLETE = {
    "unsupported_decoder", "source_unavailable", "corrupt_content",
    "incomplete_graph", "unavailable",
}
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
_INTEGER = re.compile(r"0|[1-9][0-9]*\Z")
_SPORTS = {"running", "cycling"}
_LIMITATIONS = {"recorded_data_only", "utc_start_attribution", "optional_metrics_excluded"}
_MEMBER_LIMITATIONS = {"recorded_data_only", "missing_records"}
_EXCLUSION_REASONS = {
    "quarantined_candidate", "disposition_not_published", "outside_scope_window",
    "sport_not_selected", "policy_version_not_selected", "mapping_reference_not_selected",
    "preparation_version_not_selected", "required_field_absent",
    "duplicate_canonical_identity", "scope_capacity_exceeded",
}
_ELIGIBILITY_REASONS = {
    "no_included_activity", "scope_less_than_28_days",
    "fewer_than_four_complete_weeks", "fewer_than_three_recorded_weeks",
}


class SavedReadUnavailable(ValueError):
    """Safe boundary error; caller-visible text is selected from ERRORS."""

    def __init__(self, code: str) -> None:
        self.code = code if code in ERRORS else "retrieval_unavailable"
        super().__init__(self.code)


def operation_allowed(_request) -> bool:
    """Object-independent policy hook; no operation policy is configured yet."""
    return True


def rate_limited(_request) -> bool:
    """Object-independent rate hook; no rate limiter is configured yet."""
    return False


def canonical_uuid(value: str) -> bool:
    if not isinstance(value, str) or _UUID.fullmatch(value) is None:
        return False
    try:
        return str(UUID(value)) == value
    except ValueError:
        return False


def _canonical_json(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _decode_canonical(carrier: bytes) -> dict:
    if type(carrier) is not bytes:
        raise ValueError("canonical carrier must be bytes")
    decoded = json.loads(carrier.decode("ascii"))
    if type(decoded) is not dict or _canonical_json(decoded) != carrier:
        raise ValueError("saved carrier is not canonical ASCII JSON")
    return decoded


def _digest(value) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _utc_text(value) -> bool:
    if type(value) is not str or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value) is None:
        return False
    try:
        from datetime import datetime
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%dT%H:%M:%SZ") == value
    except ValueError:
        return False


def _validate_scope(scope: dict) -> None:
    keys = {"kind", "start_utc", "end_utc", "window", "sports", "max_activities",
            "preparation_version", "policy_version", "mapping_reference"}
    if type(scope) is not dict or set(scope) != keys:
        raise ValueError("invalid selected scope keys")
    if (any(type(scope[name]) is not str or not scope[name]
            for name in ("kind", "preparation_version", "policy_version", "mapping_reference"))
            or not _utc_text(scope["start_utc"]) or not _utc_text(scope["end_utc"])
            or scope["start_utc"] >= scope["end_utc"]
            or scope["window"] != "[start_utc,end_utc)"
            or type(scope["max_activities"]) is not str
            or _INTEGER.fullmatch(scope["max_activities"]) is None
            or int(scope["max_activities"]) < 1):
        raise ValueError("invalid selected scope values")
    sports = scope["sports"]
    if sports is not None and (type(sports) is not list or not sports
                               or any(type(item) is not str or item not in _SPORTS for item in sports)
                               or sports != sorted(set(sports))):
        raise ValueError("invalid selected sports")


def _validate_effective_scope(scope: dict) -> None:
    if type(scope) is not dict:
        raise ValueError("invalid effective scope")
    if set(scope) == {"start_utc", "end_utc"}:
        if (not _utc_text(scope["start_utc"]) or not _utc_text(scope["end_utc"])
                or scope["start_utc"] >= scope["end_utc"]):
            raise ValueError("invalid effective interval")
    elif set(scope) == {"status", "reason_code"}:
        if scope != {"status": "unavailable", "reason_code": "insufficient_scope"}:
            raise ValueError("unknown unavailable scope")
    else:
        raise ValueError("invalid effective scope keys")


def _validate_operand(operand: dict) -> None:
    keys = {"source_digest", "normalization_digest", "source_field_path",
            "preparation_version", "mapping_reference", "value"}
    if (type(operand) is not dict or set(operand) != keys
            or not _digest(operand["source_digest"])
            or not _digest(operand["normalization_digest"])
            or type(operand["source_field_path"]) is not str
            or not operand["source_field_path"].startswith(operand["normalization_digest"] + ".")
            or operand["source_field_path"].rsplit(".", 1)[-1] not in
                {"sport", "elapsed_duration_ms", "start_epoch_seconds"}
            or any(type(operand[name]) is not str or not operand[name]
                   for name in ("preparation_version", "mapping_reference", "value"))):
        raise ValueError("invalid saved source operand")


def _validate_manifest(content: dict) -> None:
    manifest = content["manifest"]
    if (type(manifest) is not dict
            or set(manifest) != {"manifest_version", "selected_scope", "effective_scope",
                                 "members", "exclusions", "buckets"}
            or manifest["manifest_version"] != MANIFEST_VERSION
            or manifest["selected_scope"] != content["selected_scope"]
            or manifest["effective_scope"] != content["effective_scope"]
            or type(manifest["members"]) is not list
            or type(manifest["exclusions"]) is not list
            or type(manifest["buckets"]) is not list):
        raise ValueError("invalid manifest")
    member_ids = []
    member_sports = {}
    for member in manifest["members"]:
        if (type(member) is not dict or set(member) !=
                {"normalization_digest", "source_digest", "start_utc", "sport", "operands"}
                or not _digest(member["normalization_digest"])
                or not _digest(member["source_digest"])
                or not _utc_text(member["start_utc"])
                or member["sport"] not in _SPORTS or type(member["operands"]) is not list):
            raise ValueError("invalid manifest member")
        if member["normalization_digest"] in member_sports:
            raise ValueError("duplicate member")
        member_ids.append(member["normalization_digest"])
        member_sports[member["normalization_digest"]] = member["sport"]
        paths = []
        for operand in member["operands"]:
            _validate_operand(operand)
            if (operand["normalization_digest"] != member["normalization_digest"]
                    or operand["source_digest"] != member["source_digest"]):
                raise ValueError("member operand binding mismatch")
            paths.append(operand["source_field_path"].rsplit(".", 1)[-1])
        if paths != sorted(set(paths)) or set(paths) != {"sport", "elapsed_duration_ms", "start_epoch_seconds"}:
            raise ValueError("member operand set mismatch")
    for exclusion in manifest["exclusions"]:
        if (type(exclusion) is not dict or set(exclusion) !=
                {"normalization_digest", "reason_code", "multiplicity"}
                or not _digest(exclusion["normalization_digest"])
                or exclusion["reason_code"] not in _EXCLUSION_REASONS
                or type(exclusion["multiplicity"]) is not str
                or _INTEGER.fullmatch(exclusion["multiplicity"]) is None
                or int(exclusion["multiplicity"]) < 1):
            raise ValueError("invalid manifest exclusion")
    buckets = manifest["buckets"]
    for bucket in buckets:
        if type(bucket) is not dict:
            raise ValueError("invalid manifest bucket")
        if content["metric_code"] == "activity-summary":
            if set(bucket) != {"grouping", "members", "count", "limitations"}:
                raise ValueError("invalid summary bucket keys")
            if bucket["grouping"] not in _SPORTS:
                raise ValueError("invalid summary bucket group")
        else:
            if set(bucket) != {"start_utc", "end_utc", "grouping", "members", "count",
                               "elapsed_ms", "limitations"}:
                raise ValueError("invalid trend bucket keys")
            if (not _utc_text(bucket["start_utc"]) or not _utc_text(bucket["end_utc"])
                    or bucket["start_utc"] >= bucket["end_utc"]
                    or bucket["grouping"] != "overall"):
                raise ValueError("invalid trend bucket interval")
            _validate_numeric(bucket["elapsed_ms"], "integer_milliseconds", "exact_integer")
        members = bucket["members"]
        if (type(members) is not list or members != sorted(set(members))
                or any(type(item) is not str or item not in member_sports for item in members)
                or type(bucket["count"]) is not str or bucket["count"] != str(len(members))
                or type(bucket["limitations"]) is not list
                or any(type(item) is not str or item not in _MEMBER_LIMITATIONS for item in bucket["limitations"])):
            raise ValueError("invalid manifest bucket content")
        if content["metric_code"] == "activity-summary" and (
                any(member_sports[item] != bucket["grouping"] for item in members)
                or bucket["limitations"] != ["recorded_data_only"]):
            raise ValueError("summary bucket membership mismatch")
        if content["metric_code"] == "training-volume-trend" and (
                bucket["limitations"] != (["recorded_data_only"] if members else
                                           ["recorded_data_only", "missing_records"])):
            raise ValueError("trend bucket limitation mismatch")
    if content["metric_code"] == "activity-summary":
        expected_sports = sorted({member_sports[item] for item in member_ids})
        if [bucket["grouping"] for bucket in buckets] != expected_sports:
            raise ValueError("summary bucket set mismatch")
    elif buckets:
        if len(buckets) != 4 or any(bucket["start_utc"] >= bucket["end_utc"] for bucket in buckets):
            raise ValueError("invalid complete week set")
        if any(buckets[i]["end_utc"] != buckets[i + 1]["start_utc"] for i in range(3)):
            raise ValueError("noncontiguous complete weeks")
    elif content["effective_scope"] != {"status": "unavailable", "reason_code": "insufficient_scope"}:
        raise ValueError("missing complete weeks without unavailable scope")
    operands = content["operands"]
    if type(operands) is not list:
        raise ValueError("invalid operand list")
    expected_operands = []
    for member in manifest["members"]:
        for source in member["operands"]:
            expected_operands.append({
                "role": f"{member['normalization_digest']}.{source['source_field_path'].rsplit('.', 1)[-1]}",
                "source": source,
            })
    expected_operands.sort(key=lambda item: item["role"])
    if operands != expected_operands:
        raise ValueError("operand list does not resolve to manifest members")


def _binding(content: dict) -> dict:
    return {
        "input_content_digest": content["input_content_digest"],
        "manifest_path": "/manifest",
        "method_identity": content["method_identity"],
        "method_parameters": content["method_parameters"],
    }


def _selection(content: dict, members: list[str], **context) -> dict:
    roles = sorted(operand["role"] for operand in content["operands"]
                   if operand["source"]["normalization_digest"] in members)
    return {**_binding(content), **context, "members": members, "operand_roles": roles}


def _dependency(content: dict, paths: list[str], **context) -> dict:
    return {**_binding(content), **context, "value_paths": paths}


def _validate_registry(content: dict, registry: dict) -> None:
    """Check saved registry structure, exact payload values and local references.

    This is a support gate over stored carriers; it does not call a metric
    preparer or calculate numeric values.
    """
    entries = registry["entries"]
    if any(type(entry) is not dict for entry in entries):
        raise ValueError("invalid registry entry")
    paths = [entry.get("path") for entry in entries]
    if paths != sorted(set(paths)) or any(type(path) is not str for path in paths):
        raise ValueError("registry paths are not unique and ordered")

    expected = {
        "/manifest": ("structured_context", content["manifest"], {
            "input_content_digest": content["input_content_digest"],
            "method_identity": content["method_identity"],
            "method_parameters": content["method_parameters"],
        }),
        "/eligibility": ("structured_context", content["eligibility"], _binding(content)),
    }
    member_ids = {member["normalization_digest"]
                  for member in content["manifest"]["members"]}
    if content["metric_code"] == "activity-summary":
        for group in content["values"]:
            bucket = next(item for item in content["manifest"]["buckets"]
                          if item["grouping"] == group["sport"])
            selection = _selection(content, bucket["members"], sport=group["sport"])
            for name in ("activity_count", "elapsed_ms"):
                path = f"/sports/{group['sport']}/{name}"
                expected[path] = ("numeric", group[name], selection, "eligible")
    else:
        kind = content["values_kind"]
        buckets = content["manifest"]["buckets"]
        for index, bucket in enumerate(buckets):
            selection = _selection(content, bucket["members"],
                start_utc=bucket["start_utc"], end_utc=bucket["end_utc"],
                limitations=bucket["limitations"])
            count = {"status": "available", "unit": "activity_count",
                     "precision": "exact_integer", "value": bucket["count"]}
            expected[f"/weeks/{index}/activity_count"] = ("numeric", count, selection, kind)
            expected[f"/weeks/{index}/elapsed_ms"] = (
                "numeric", bucket["elapsed_ms"], selection, kind)
        for name, indices in (("earlier_total", (0, 1)), ("later_total", (2, 3))):
            value_paths = ([f"/weeks/{index}/elapsed_ms" for index in indices]
                           if buckets else [])
            derivation = _dependency(content, value_paths,
                required_week_indices=[str(index) for index in indices],
                effective_scope=content["effective_scope"])
            expected[f"/{name}"] = ("numeric", content["values"][name], derivation, kind)
        for name, refs in (
            ("signed_difference", ["/earlier_total", "/later_total"]),
            ("magnitude", ["/earlier_total", "/later_total"]),
            ("percentage", ["/signed_difference", "/earlier_total"]),
        ):
            expected[f"/{name}"] = (
                "numeric", content["values"][name], _dependency(content, refs), kind)
        if "classification" in content:
            expected["/classification"] = (
                "sign_enum", content["classification"],
                _dependency(content, ["/signed_difference"]), kind)

    if set(paths) != set(expected):
        raise ValueError("registry paths do not match supported saved values")
    for entry in entries:
        path = entry["path"]
        spec = expected[path]
        if spec[0] == "structured_context":
            if (set(entry) != {"path", "type", "payload", "derivation"}
                    or entry["type"] != spec[0] or entry["payload"] != spec[1]
                    or entry["derivation"] != spec[2]):
                raise ValueError("saved structured registry context mismatch")
            continue
        if spec[0] == "sign_enum":
            if (set(entry) != {"path", "type", "payload", "values_kind", "derivation"}
                    or entry["type"] != "sign_enum" or entry["payload"] != spec[1]
                    or entry["values_kind"] != spec[3] or entry["derivation"] != spec[2]):
                raise ValueError("saved classification entry mismatch")
            continue
        if (set(entry) != {"path", "type", "payload", "values_kind", "derivation"}
                or entry["type"] != "numeric" or entry["payload"] != spec[1]
                or entry["values_kind"] != spec[3] or entry["derivation"] != spec[2]):
            raise ValueError("saved numeric registry entry mismatch")
        _validate_numeric(entry["payload"], entry["payload"]["unit"],
                          entry["payload"]["precision"])

    # Validate that dependency paths and operand roles name real entries.
    numeric_paths = {path for path, spec in expected.items() if spec[0] == "numeric"}
    operand_roles = {item["role"] for item in content["operands"]}
    for entry in entries:
        derivation = entry["derivation"]
        if type(derivation) is not dict:
            raise ValueError("invalid registry derivation")
        binding = (_binding(content) if entry["path"] != "/manifest" else {
            "input_content_digest": content["input_content_digest"],
            "method_identity": content["method_identity"],
            "method_parameters": content["method_parameters"],
        })
        if any(derivation.get(name) != value for name, value in binding.items()):
            raise ValueError("registry derivation binding mismatch")
        if entry["path"] == "/manifest" and set(derivation) != set(binding):
            raise ValueError("invalid manifest derivation keys")
        if entry["path"] != "/manifest" and any(
                derivation.get(name) != _binding(content)[name]
                for name in ("manifest_path",)):
                raise ValueError("registry derivation binding mismatch")
        members = derivation.get("members", [])
        roles = derivation.get("operand_roles", [])
        refs = derivation.get("value_paths", [])
        if (type(members) is not list or len(members) != len(set(members))
                or any(member not in member_ids for member in members)
                or type(roles) is not list or roles != sorted(set(roles))
                or any(role not in operand_roles for role in roles)
                or type(refs) is not list or len(refs) != len(set(refs))
                or any(ref not in numeric_paths for ref in refs)):
            raise ValueError("unresolved registry derivation reference")


def _noncomplete_state(state: str) -> str:
    return state if state in _NONCOMPLETE else "unavailable"


def _metric_shell(metric) -> dict:
    return {
        "api_version": API_VERSION,
        "resource_type": "recorded_metric",
        "metric_id": metric.metric_id,
        "snapshot_id": metric.snapshot_id,
        "state": _noncomplete_state(metric.state),
        "reader_version": metric.reader_version,
        "canonical_content": None,
        "canonical_registry_content": None,
        "canonical_method_identity": None,
        "evidence": [],
    }


def metric_document(user, metric_id: str) -> dict:
    """Return the exact approved metric envelope over the current user's scope."""
    if not canonical_uuid(metric_id):
        raise SavedReadUnavailable("resource_not_available")
    try:
        store = SavedMetricStore.for_user(user)
        saved = store.get_metric(metric_id)
    except MetricStoreRefusal as error:
        raise SavedReadUnavailable(
            "resource_not_available" if error.reason_code == "resource_not_available"
            else "retrieval_unavailable"
        ) from None
    except Exception:
        raise SavedReadUnavailable("retrieval_unavailable") from None

    result = _metric_shell(saved)
    if saved.state != "complete":
        return result

    try:
        content = _decode_canonical(saved.canonical_content)
        registry = _decode_canonical(saved.canonical_registry_content)
        method = _decode_canonical(saved.canonical_method_identity)
        entries = registry["entries"]
        if (type(entries) is not list or any(type(entry) is not dict for entry in entries)
                or registry.get("persistence_contract_version") != "datara/saved-recorded-aggregate/1"
                or registry.get("registry_adapter_version") != REGISTRY_ADAPTER_VERSION):
            raise ValueError("invalid saved registry")

        # The persistence store has already validated the full graph and exact
        # registry bytes. The page contract exposes evidence links only for
        # numeric value entries; structured context remains in its canonical
        # carrier and must not be exposed as a value-evidence link.
        expected_entries = {entry["path"]: _canonical_json(entry) for entry in entries
                            if entry.get("type") == "numeric"}
        if len(expected_entries) != sum(entry.get("type") == "numeric" for entry in entries):
            raise ValueError("duplicate numeric registry path")
        rows = list(m.Evidence.objects.for_owner(user.pk).filter(
            metric_id=saved.metric_id, snapshot_id=saved.snapshot_id,
            kind=m.Evidence.KIND_COMPUTED_METRIC,
            value_path__in=expected_entries,
        ).order_by("value_path", "evidence_id"))
        by_path = {}
        for row in rows:
            if row.value_path in by_path:
                raise ValueError("duplicate saved evidence path")
            by_path[row.value_path] = row
        if set(by_path) != set(expected_entries):
            raise ValueError("saved registry and evidence paths differ")
        links = []
        for path in sorted(expected_entries):
            row = by_path[path]
            if row.value_canonical.encode("ascii") != expected_entries[path]:
                raise ValueError("saved evidence does not match the validated registry")
            links.append({
                "evidence_id": str(row.pk),
                "value_path": path,
                "href": reverse("recorded_metric_evidence_api", kwargs={
                    "metric_id": saved.metric_id, "evidence_id": str(row.pk),
                }),
            })
        if (content.get("method_identity") != method
                or method.get("method_id") not in ("activity-summary", "training-volume-trend")):
            raise ValueError("saved method identity mismatch")
    except Exception:
        # Do not return partial data after a projection failure. Retain owned
        # graph identifiers and the read version only.
        result["state"] = "incomplete_graph"
        return result

    result.update(
        state="complete",
        canonical_content=saved.canonical_content.decode("ascii"),
        canonical_registry_content=saved.canonical_registry_content.decode("ascii"),
        canonical_method_identity=saved.canonical_method_identity.decode("ascii"),
        evidence=links,
    )
    return result


def evidence_document(user, metric_id: str, evidence_id: str) -> dict:
    if not canonical_uuid(metric_id) or not canonical_uuid(evidence_id):
        raise SavedReadUnavailable("resource_not_available")
    parent = metric_document(user, metric_id)
    try:
        store = SavedMetricStore.for_user(user)
        saved = store.get_metric_evidence(evidence_id)
    except MetricStoreRefusal as error:
        raise SavedReadUnavailable(
            "resource_not_available" if error.reason_code == "resource_not_available"
            else "retrieval_unavailable"
        ) from None
    except SavedReadUnavailable:
        raise
    except Exception:
        raise SavedReadUnavailable("retrieval_unavailable") from None

    if (saved.metric.metric_id != metric_id or saved.metric.snapshot_id != parent["snapshot_id"]):
        raise SavedReadUnavailable("resource_not_available")
    state = parent["state"]
    path = None
    entry = None
    if state == "complete":
        matching = [row for row in parent["evidence"] if row["evidence_id"] == evidence_id]
        if len(matching) != 1 or saved.value_path != matching[0]["value_path"]:
            raise SavedReadUnavailable("resource_not_available")
        if type(saved.canonical_registry_entry) is not bytes:
            return _evidence_shell(evidence_id, metric_id, parent, "incomplete_graph")
        try:
            _decode_canonical(saved.canonical_registry_entry)
            entry = saved.canonical_registry_entry.decode("ascii")
            path = saved.value_path
        except Exception:
            return _evidence_shell(evidence_id, metric_id, parent, "incomplete_graph")
    return _evidence_shell(evidence_id, metric_id, parent, state,
                           value_path=path, canonical_registry_entry=entry)


def _evidence_shell(evidence_id, metric_id, parent, state, *, value_path=None,
                    canonical_registry_entry=None) -> dict:
    return {
        "api_version": API_VERSION,
        "resource_type": "computed_metric_evidence",
        "evidence_id": evidence_id,
        "metric_id": metric_id,
        "snapshot_id": parent["snapshot_id"],
        "state": state,
        "reader_version": parent["reader_version"],
        "value_path": value_path,
        "canonical_registry_entry": canonical_registry_entry,
    }


def decode_page_metric(document: dict) -> dict:
    """Fail-closed, read-only support decoder for the pinned page contract."""
    if document.get("state") != "complete":
        reason = ("Saved history exists, but this reader cannot display it."
                  if document.get("state") == "unsupported_decoder"
                  else "Saved detail cannot currently be validated.")
        return {"supported": False, "display_message": reason}
    try:
        if (type(document) is not dict
                or set(document) != {"api_version", "resource_type", "metric_id", "snapshot_id",
                                     "state", "reader_version", "canonical_content",
                                     "canonical_registry_content", "canonical_method_identity", "evidence"}
                or document.get("api_version") != API_VERSION
                or document.get("resource_type") != "recorded_metric"
                or document.get("state") != "complete"
                or document.get("reader_version") != READER_VERSION
                or type(document.get("evidence")) is not list):
            raise ValueError("unsupported metric envelope")
        content_raw = document["canonical_content"].encode("ascii")
        registry_raw = document["canonical_registry_content"].encode("ascii")
        method_raw = document["canonical_method_identity"].encode("ascii")
        content = _decode_canonical(content_raw)
        registry = _decode_canonical(registry_raw)
        method = _decode_canonical(method_raw)
        code = content["metric_code"]
        base_keys = {
            "metric_contract_version", "metric_code", "method_identity",
            "supported_input_contract_version", "input_content_digest",
            "selected_scope", "effective_scope", "codec_version", "manifest",
            "operands", "limitations", "quality_records", "grouping",
            "method_parameters", "eligibility",
        }
        if code == "activity-summary":
            expected_keys = base_keys | {"values"}
        elif code == "training-volume-trend":
            expected_keys = base_keys | {"outside_comparison", "values_kind", "values"}
            if "classification" in content:
                expected_keys.add("classification")
        else:
            raise ValueError("unsupported metric code")
        if set(content) != expected_keys:
            raise ValueError("unknown or missing saved content key")
        if (content["metric_contract_version"] != METRIC_CONTRACT_VERSION
                or content["supported_input_contract_version"] != SOURCE_CONTRACT_VERSION
                or content["codec_version"] != CODEC_VERSION
                or content["manifest"].get("manifest_version") != MANIFEST_VERSION
                or content["method_identity"] != method
                or content["manifest"]["selected_scope"] != content["selected_scope"]
                or content["manifest"]["effective_scope"] != content["effective_scope"]
                or method != {
                    "method_id": code, "method_version": "1",
                    "specification_digest": _SPECIFICATION_DIGEST,
                    "adapter_id": "scoped-recorded-core",
                    "adapter_version": PURE_ADAPTER_VERSION,
                }):
            raise ValueError("unsupported saved version")
        if (not _digest(content["input_content_digest"])
                or type(content["method_identity"]) is not dict
                or type(content["method_parameters"]) is not dict
                or type(content["quality_records"]) is not list
                or content["quality_records"] != []
                or content["limitations"] != ["recorded_data_only", "utc_start_attribution",
                                               "optional_metrics_excluded"]
                or type(content["eligibility"]) is not dict
                or set(content["eligibility"]) != {"eligible", "unmet_reasons"}
                or type(content["eligibility"]["eligible"]) is not bool
                or type(content["eligibility"]["unmet_reasons"]) is not list
                or any(type(reason) is not str or reason not in _ELIGIBILITY_REASONS
                       for reason in content["eligibility"]["unmet_reasons"])
                or len(content["eligibility"]["unmet_reasons"])
                   != len(set(content["eligibility"]["unmet_reasons"]))
                or content["eligibility"]["eligible"]
                   != (not content["eligibility"]["unmet_reasons"])):
            raise ValueError("invalid saved page shape")
        _validate_scope(content["selected_scope"])
        _validate_effective_scope(content["effective_scope"])
        _validate_manifest(content)
        if content["metric_code"] == "activity-summary":
            if content["method_parameters"] != {}:
                raise ValueError("unknown summary parameters")
        elif content["method_parameters"] != {
                "complete_weeks": "4", "minimum_recorded_weeks": "3",
                "minimum_scope_days": "28", "week_start": "monday_00_utc"}:
            raise ValueError("unknown trend parameters")

        values = content["values"]
        if code == "activity-summary":
            if content["grouping"] != "per_sport" or type(values) is not list:
                raise ValueError("invalid summary grouping")
            if [row.get("sport") for row in values if type(row) is dict] != sorted(
                    {bucket["grouping"] for bucket in content["manifest"]["buckets"]}):
                raise ValueError("summary values do not match manifest groups")
            for row in values:
                if type(row) is not dict or set(row) != {"sport", "activity_count", "elapsed_ms"}:
                    raise ValueError("invalid summary row")
                if row["sport"] not in ("running", "cycling"):
                    raise ValueError("unsupported sport")
                _validate_numeric(row["activity_count"], "activity_count", "exact_integer")
                _validate_numeric(row["elapsed_ms"], "integer_milliseconds", "exact_integer")
                bucket = next(item for item in content["manifest"]["buckets"]
                              if item["grouping"] == row["sport"])
                if (row["activity_count"]["value"] != bucket["count"]
                        or row["activity_count"]["status"] != "available"):
                    raise ValueError("summary count differs from saved membership")
        else:
            if (content["grouping"] != "overall"
                    or content["values_kind"] not in ("eligible", "ineligible_diagnostic")
                    or type(values) is not dict
                    or set(values) != {"earlier_total", "later_total", "signed_difference", "magnitude", "percentage"}
                    or ("classification" in content and content["classification"] not in
                        ("increased", "decreased", "equal"))):
                raise ValueError("invalid trend shape")
            for name, numeric in values.items():
                unit, precision = (("percent", "exact_rational") if name == "percentage"
                                   else ("integer_milliseconds", "exact_integer"))
                _validate_numeric(numeric, unit, precision)
            if (type(content["outside_comparison"]) is not list
                    or content["outside_comparison"] != sorted(set(content["outside_comparison"]))
                    or any(type(item) is not str or not _digest(item)
                           or item not in {member["normalization_digest"]
                                           for member in content["manifest"]["members"]}
                           for item in content["outside_comparison"])
                    or content["values_kind"] != ("eligible" if content["eligibility"]["eligible"]
                                                  else "ineligible_diagnostic")
                    or ("classification" in content and
                        (not content["eligibility"]["eligible"]
                         or content["classification"] not in ("increased", "decreased", "equal")))):
                raise ValueError("invalid trend comparison state")
        if (registry.get("persistence_contract_version") != "datara/saved-recorded-aggregate/1"
                or registry.get("registry_adapter_version") != REGISTRY_ADAPTER_VERSION
                or set(registry) != {"persistence_contract_version", "registry_adapter_version", "entries"}
                or type(registry.get("entries")) is not list
                or document["reader_version"] != READER_VERSION):
            raise ValueError("unsupported saved registry version")
        _validate_registry(content, registry)
        # Validate opaque UUIDs before using the saved href collection.
        if (not canonical_uuid(document["metric_id"]) or not canonical_uuid(document["snapshot_id"])
                or any(type(item) is not dict or set(item) != {"evidence_id", "value_path", "href"}
                       or not canonical_uuid(item["evidence_id"])
                       or type(item["value_path"]) is not str or type(item["href"]) is not str
                       for item in document["evidence"])):
            raise ValueError("invalid saved identity")
        evidence = sorted(document["evidence"], key=lambda item: item["value_path"])
        if (document["evidence"] != evidence
                or [item["value_path"] for item in evidence]
                != sorted(entry["path"] for entry in registry["entries"]
                          if entry.get("type") == "numeric")):
            raise ValueError("saved evidence set is incomplete")
        if any(item["href"] != reverse("recorded_metric_evidence_api", kwargs={
                "metric_id": document["metric_id"], "evidence_id": item["evidence_id"]})
               for item in evidence):
            raise ValueError("invalid saved evidence link")
        return {
            "supported": True,
            "code": code,
            "content_json": content_raw.decode("ascii"),
            "registry_json": registry_raw.decode("ascii"),
            "method_json": method_raw.decode("ascii"),
            "eligible": content["eligibility"]["eligible"],
            "unmet_reasons": content["eligibility"]["unmet_reasons"],
            "limitations": content["limitations"],
            "method_id": method["method_id"],
            "method_version": method["method_version"],
            "adapter_id": method["adapter_id"],
            "adapter_version": method["adapter_version"],
            "selected_scope_json": _canonical_json(content["selected_scope"]).decode("ascii"),
            "effective_scope_json": _canonical_json(content["effective_scope"]).decode("ascii"),
            "values_json": _canonical_json(values).decode("ascii"),
            "buckets_json": _canonical_json(content["manifest"]["buckets"]).decode("ascii"),
            "outside_comparison_json": _canonical_json(
                content.get("outside_comparison", [])).decode("ascii"),
            "classification": content.get("classification"),
            "source_operands_json": _canonical_json(content["operands"]).decode("ascii"),
            "evidence": evidence,
        }
    except Exception:
        return {"supported": False,
                "display_message": "Saved detail cannot be displayed by this page."}


def _validate_numeric(value, unit: str, precision: str) -> None:
    if type(value) is not dict or value.get("unit") != unit or value.get("precision") != precision:
        raise ValueError("invalid saved numeric value")
    status = value.get("status")
    if status == "available":
        if set(value) == {"unit", "precision", "status", "value"}:
            text = value["value"]
            if type(text) is not str or re.fullmatch(r"0|[1-9][0-9]*|-[1-9][0-9]*", text) is None:
                raise ValueError("invalid exact integer string")
        elif set(value) == {"unit", "precision", "status", "numerator", "denominator"}:
            if precision != "exact_rational":
                raise ValueError("unexpected fraction")
            numerator, denominator = value["numerator"], value["denominator"]
            pattern = r"0|[1-9][0-9]*|-[1-9][0-9]*"
            if (type(numerator) is not str or re.fullmatch(pattern, numerator) is None
                    or type(denominator) is not str
                    or re.fullmatch(r"[1-9][0-9]*", denominator) is None):
                raise ValueError("invalid exact rational strings")
            if math.gcd(abs(int(numerator)), int(denominator)) != 1:
                raise ValueError("saved fraction is not reduced")
        else:
            raise ValueError("invalid available numeric shape")
    elif status == "unavailable":
        if (set(value) != {"unit", "precision", "status", "reason_code"}
                or value["reason_code"] not in {"zero_baseline", "insufficient_scope"}):
            raise ValueError("invalid unavailable numeric shape")
    else:
        raise ValueError("unknown numeric status")


__all__ = [
    "API_VERSION", "ERRORS", "SavedReadUnavailable", "canonical_uuid",
    "operation_allowed", "rate_limited", "metric_document",
    "evidence_document", "decode_page_metric",
]
