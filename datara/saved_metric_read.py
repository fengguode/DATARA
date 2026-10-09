"""Owner-bound, read-only projection for the approved saved-metric contract.

WP05/TK64; CUS08-CUS10; SR18-SR21/SR31/SR73. This module never prepares,
persists, or regenerates a metric and contains no provider or network client.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.db import DatabaseError
from django.http import HttpRequest

from datara import models as m
from datara.metric_projection import (
    OPERAND_PROJECTION_VERSION,
    PERSISTENCE_CONTRACT_VERSION,
    PURE_CONTRACT_VERSION,
    PURE_ADAPTER_VERSION,
    REGISTRY_ADAPTER_VERSION,
    READER_VERSION,
    SCOPED_INPUT_VERSION,
    SOURCE_CONTRACT_VERSION,
    CODEC_VERSION,
    MANIFEST_VERSION,
)
from datara.metric_store import MetricStoreRefusal, SavedMetricEvidence, SavedMetricStore
from datara.recorded_metrics import _SPECIFICATION_DIGEST

API_VERSION = "datara/recorded-metric-read/1"
RESOURCE_METRIC = "recorded_metric"
RESOURCE_EVIDENCE = "computed_metric_evidence"
INTEGER_RE = re.compile(r"(?:0|[1-9][0-9]*|-[1-9][0-9]*)\Z")
DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
UTC_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z")
CORE_OPERANDS = ("elapsed_duration_ms", "sport", "start_epoch_seconds")
_MISSING = object()

ERROR_MESSAGES = {
    "authentication_required": "Sign in to view saved recorded metrics.",
    "operation_denied": "This read operation is not permitted.",
    "method_not_allowed": "Use GET or HEAD for this read resource.",
    "rate_limited": "Too many read requests. Try again later.",
    "invalid_request": "This read resource accepts no query parameters or request body.",
    "resource_not_available": "The requested resource is not available.",
    "retrieval_unavailable": "Saved detail cannot be retrieved now. Try again later.",
}


class InvalidCanonical(ValueError):
    pass


def _pairs_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidCanonical("duplicate key")
        result[key] = value
    return result


def _ascii_document(value: bytes) -> dict:
    if type(value) is not bytes:
        raise InvalidCanonical("missing canonical bytes")
    try:
        decoded = value.decode("ascii")
        result = json.loads(decoded, object_pairs_hook=_pairs_without_duplicates,
                            parse_constant=lambda _: (_ for _ in ()).throw(InvalidCanonical("constant")))
    except (UnicodeError, ValueError, TypeError):
        raise InvalidCanonical("invalid canonical bytes") from None
    if type(result) is not dict:
        raise InvalidCanonical("object required")
    return result


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _uuid(value: str) -> bool:
    if type(value) is not str:
        return False
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return str(parsed) == value


def _require_digest(value: object) -> None:
    if type(value) is not str or not DIGEST_RE.fullmatch(value):
        raise InvalidCanonical("digest")


def _require_utc(value: object) -> None:
    if type(value) is not str or not UTC_RE.fullmatch(value):
        raise InvalidCanonical("utc instant")
    try:
        if datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%dT%H:%M:%SZ") != value:
            raise InvalidCanonical("utc instant")
    except ValueError:
        raise InvalidCanonical("utc instant") from None


def _utc_epoch(value: str) -> int:
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = parsed - epoch
    return delta.days * 86400 + delta.seconds


def _validate_scope(scope: object) -> None:
    keys = {"kind", "start_utc", "end_utc", "window", "sports", "max_activities",
            "preparation_version", "policy_version", "mapping_reference"}
    if type(scope) is not dict or set(scope) != keys:
        raise InvalidCanonical("scope keys")
    for name in ("kind", "window", "preparation_version", "policy_version", "mapping_reference"):
        if type(scope[name]) is not str or not scope[name]:
            raise InvalidCanonical("scope text")
    _require_utc(scope["start_utc"])
    _require_utc(scope["end_utc"])
    if (scope["start_utc"] >= scope["end_utc"]
            or type(scope["max_activities"]) is not str
            or not re.fullmatch(r"[1-9][0-9]*", scope["max_activities"])):
        raise InvalidCanonical("scope bounds")
    sports = scope["sports"]
    if sports is not None and (type(sports) is not list or any(type(item) is not str for item in sports)
                               or sports != sorted(set(sports))):
        raise InvalidCanonical("scope sports")


def _validate_source_graph(content: dict, manifest: dict) -> list[str]:
    """Validate the pinned page decoder's nested source/member contract."""
    _require_digest(content.get("input_content_digest"))
    _validate_scope(content.get("selected_scope"))
    members = manifest.get("members")
    exclusions = manifest.get("exclusions")
    if type(members) is not list or type(exclusions) is not list:
        raise InvalidCanonical("membership lists")
    identities = []
    operand_index = {}
    scope = content["selected_scope"]
    selected_sports = scope["sports"]
    maximum = int(scope["max_activities"])
    for member in members:
        if type(member) is not dict or set(member) != {
                "normalization_digest", "source_digest", "start_utc", "sport", "operands"}:
            raise InvalidCanonical("member shape")
        identity = member["normalization_digest"]
        _require_digest(identity)
        _require_digest(member["source_digest"])
        _require_utc(member["start_utc"])
        if member["sport"] not in ("running", "cycling") or type(member["operands"]) is not list:
            raise InvalidCanonical("member values")
        if (member["start_utc"] < scope["start_utc"] or member["start_utc"] >= scope["end_utc"]
                or (selected_sports is not None and member["sport"] not in selected_sports)):
            raise InvalidCanonical("member outside selected scope")
        if identity in identities:
            raise InvalidCanonical("duplicate member")
        identities.append(identity)
        member_operands = {}
        for source in member["operands"]:
            if type(source) is not dict or set(source) != {
                    "source_digest", "normalization_digest", "source_field_path",
                    "preparation_version", "mapping_reference", "value"}:
                raise InvalidCanonical("source operand shape")
            _require_digest(source["source_digest"])
            if (source["normalization_digest"] != identity
                    or source["source_digest"] != member["source_digest"]
                    or type(source["source_field_path"]) is not str
                    or not source["source_field_path"].startswith(identity + ".")
                    or source["source_field_path"].split(".")[-1] not in CORE_OPERANDS
                    or type(source["preparation_version"]) is not str
                    or type(source["mapping_reference"]) is not str
                    or type(source["value"]) is not str):
                raise InvalidCanonical("source operand binding")
            field = source["source_field_path"].split(".")[-1]
            if source["source_field_path"] != f"{identity}.{field}":
                raise InvalidCanonical("source field reference")
            if field in member_operands:
                raise InvalidCanonical("duplicate source operand")
            member_operands[field] = source
            operand_index[f"{identity}.{field}"] = source
        if set(member_operands) != set(CORE_OPERANDS):
            raise InvalidCanonical("core operands")
        if (member_operands["sport"]["value"] != member["sport"]
                or not INTEGER_RE.fullmatch(member_operands["start_epoch_seconds"]["value"])
                or int(member_operands["start_epoch_seconds"]["value"]) != _utc_epoch(member["start_utc"])
                or not re.fullmatch(r"[1-9][0-9]*", member_operands["elapsed_duration_ms"]["value"])):
            raise InvalidCanonical("member sport operand")
    if len(identities) > maximum:
        raise InvalidCanonical("scope capacity")
    if identities != sorted(identities, key=lambda identity: next(
            (member["start_utc"], identity) for member in members
            if member["normalization_digest"] == identity)):
        # The metric input sorts by (start epoch, digest); canonical UTC text sorts identically.
        raise InvalidCanonical("member order")
    if type(content.get("operands")) is not list:
        raise InvalidCanonical("operands")
    actual_operands = {}
    for operand in content["operands"]:
        if type(operand) is not dict or set(operand) != {"role", "source"}:
            raise InvalidCanonical("operand role shape")
        role = operand["role"]
        if type(role) is not str or role in actual_operands or role not in operand_index:
            raise InvalidCanonical("unresolved operand role")
        if operand["source"] != operand_index[role]:
            raise InvalidCanonical("operand source binding")
        actual_operands[role] = operand["source"]
    if set(actual_operands) != set(operand_index) or list(actual_operands) != sorted(actual_operands):
        raise InvalidCanonical("operand set/order")
    prior = []
    for exclusion in exclusions:
        if type(exclusion) is not dict or set(exclusion) != {
                "normalization_digest", "reason_code", "multiplicity"}:
            raise InvalidCanonical("exclusion shape")
        _require_digest(exclusion["normalization_digest"])
        if (type(exclusion["reason_code"]) is not str or not exclusion["reason_code"]
                or type(exclusion["multiplicity"]) is not str
                or not re.fullmatch(r"[1-9][0-9]*", exclusion["multiplicity"])):
            raise InvalidCanonical("exclusion value")
        key = (exclusion["normalization_digest"], exclusion["reason_code"])
        if prior and key <= prior[-1]:
            raise InvalidCanonical("exclusion order")
        prior.append(key)
    return identities


def _status_message(state: str) -> str:
    if state == "unsupported_decoder":
        return "Saved history exists, but this reader cannot display it."
    return "Saved detail cannot currently be validated."


def _error(status: int, code: str) -> tuple[int, dict]:
    return status, {"api_version": API_VERSION,
                    "error": {"code": code, "message": ERROR_MESSAGES[code]}}


def _object_policy_allows(request: HttpRequest) -> bool:
    # Object-independent local read permission. No per-role policy engine is
    # installed; the explicit setting is the selected authenticated-owner rule.
    return bool(getattr(settings, "DATARA_RECORDED_METRIC_READ_ENABLED", True))


def _has_body(request: HttpRequest) -> bool:
    declared = request.META.get("CONTENT_LENGTH")
    if declared not in (None, ""):
        try:
            if int(declared) > 0:
                return True
        except (TypeError, ValueError):
            return True
    # WSGI servers normally provide CONTENT_LENGTH. Inspect the buffered body
    # only when it is absent so an unexpected body is still rejected safely.
    return bool(request.body)


def _response_preflight(request: HttpRequest) -> tuple[int, str] | None:
    user = getattr(request, "user", None)
    if user is None or not bool(getattr(user, "is_authenticated", False)):
        return 401, "authentication_required"
    if not _object_policy_allows(request):
        return 403, "operation_denied"
    if request.method not in ("GET", "HEAD"):
        return 405, "method_not_allowed"
    # The approved contract requires an owner/operation rate policy before any
    # query/body validation or object lookup. Missing or failing policy
    # configuration must fail closed instead of silently disabling the gate.
    rate_policy = getattr(settings, "DATARA_READ_RATE_LIMITED", None)
    if not callable(rate_policy):
        return 503, "retrieval_unavailable"
    try:
        if rate_policy(request.user.pk, "recorded_metric_read"):
            return 429, "rate_limited"
    except Exception:
        return 503, "retrieval_unavailable"
    if request.META.get("QUERY_STRING", "") or request.GET or _has_body(request):
        return 422, "invalid_request"
    return None


def _complete_metric_envelope(metric, user) -> tuple[str, dict]:
    content = _ascii_document(metric.canonical_content)
    registry = _ascii_document(metric.canonical_registry_content)
    method = _ascii_document(metric.canonical_method_identity)
    if (metric.reader_version != READER_VERSION
            or content.get("metric_contract_version") != PURE_CONTRACT_VERSION
            or content.get("codec_version") != CODEC_VERSION
            or content.get("supported_input_contract_version") != SOURCE_CONTRACT_VERSION
            or content.get("manifest", {}).get("manifest_version") != MANIFEST_VERSION
            or content.get("method_identity") != method
            or method.get("adapter_version") != PURE_ADAPTER_VERSION
            or method.get("method_version") != "1"
            or method.get("specification_digest") != _SPECIFICATION_DIGEST
            or method.get("adapter_id") != "scoped-recorded-core"
            or method.get("method_id") != content.get("metric_code")
            or content.get("metric_code") not in ("activity-summary", "training-volume-trend")
            or registry.get("persistence_contract_version") != PERSISTENCE_CONTRACT_VERSION
            or registry.get("registry_adapter_version") != REGISTRY_ADAPTER_VERSION):
        return "unsupported_decoder", {}

    entries = registry.get("entries")
    if type(entries) is not list or any(type(entry) is not dict for entry in entries):
        return "incomplete_graph", {}
    paths = [entry.get("path") for entry in entries]
    if any(type(path) is not str for path in paths) or len(paths) != len(set(paths)):
        return "incomplete_graph", {}

    rows = list(m.Evidence.objects.for_owner(user.pk).filter(
        snapshot_id=metric.snapshot_id, metric_id=metric.metric_id,
        kind=m.Evidence.KIND_COMPUTED_METRIC).order_by("value_path", "evidence_id"))
    if (len(rows) != len(entries)
            or any(row.value_path is None or row.value_canonical is None
                   for row in rows)):
        return "incomplete_graph", {}
    row_by_path = {row.value_path: row for row in rows}
    if len(row_by_path) != len(rows) or set(row_by_path) != set(paths):
        return "incomplete_graph", {}

    evidence = []
    for entry in entries:
        row = row_by_path[entry["path"]]
        if row.value_canonical.encode("ascii") != _canonical(entry):
            return "incomplete_graph", {}
        evidence.append({
            "evidence_id": str(row.pk),
            "value_path": row.value_path,
            "href": f"/api/v1/recorded-metrics/{metric.metric_id}/evidence/{row.pk}",
            "_entry": entry,
        })

    envelope = {
        "api_version": API_VERSION,
        "resource_type": RESOURCE_METRIC,
        "metric_id": metric.metric_id,
        "snapshot_id": metric.snapshot_id,
        "state": "complete",
        "reader_version": metric.reader_version,
        "canonical_content": metric.canonical_content.decode("ascii"),
        "canonical_registry_content": metric.canonical_registry_content.decode("ascii"),
        "canonical_method_identity": metric.canonical_method_identity.decode("ascii"),
        "evidence": [{key: item[key] for key in ("evidence_id", "value_path", "href")}
                     for item in evidence],
    }
    return "complete", {"envelope": envelope, "content": content,
                         "registry": registry, "method": method,
                         "evidence": evidence}


def metric_read(request: HttpRequest, metric_id: str) -> tuple[int, dict]:
    """Return the exact v1 API decision and body for the metric detail route."""
    return _metric_read(request, metric_id)


def _metric_read(request: HttpRequest, metric_id: str) -> tuple[int, dict]:
    preflight = _response_preflight(request)
    if preflight:
        return _error(*preflight)
    if not _uuid(metric_id):
        return _error(404, "resource_not_available")

    try:
        dto = SavedMetricStore.for_user(request.user).get_metric(metric_id)
    except MetricStoreRefusal as error:
        if error.reason_code == "resource_not_available":
            return _error(404, "resource_not_available")
        return _error(503, "retrieval_unavailable")
    except Exception:
        return _error(503, "retrieval_unavailable")

    state = dto.state
    if state == "complete":
        try:
            page_state, decoded = _complete_metric_envelope(dto, request.user)
        except DatabaseError:
            return _error(503, "retrieval_unavailable")
        except Exception:
            page_state, decoded = "incomplete_graph", {}
        if page_state == "complete":
            status, body = 200, decoded["envelope"]
        else:
            status, body = 200, _noncomplete_metric(dto, page_state)
    elif state in ("unsupported_decoder", "source_unavailable", "corrupt_content",
                   "incomplete_graph", "unavailable"):
        status, body = 200, _noncomplete_metric(dto, state)
    elif state == "resource_not_available":
        return _error(404, "resource_not_available")
    elif state == "metric_retrieval_unavailable":
        return _error(503, "retrieval_unavailable")
    else:
        status, body = 200, _noncomplete_metric(dto, "unavailable")
    return status, body


def _noncomplete_metric(dto, state: str) -> dict:
    if state not in ("unsupported_decoder", "source_unavailable", "corrupt_content",
                     "incomplete_graph", "unavailable"):
        state = "unavailable"
    return {
        "api_version": API_VERSION,
        "resource_type": RESOURCE_METRIC,
        "metric_id": dto.metric_id,
        "snapshot_id": dto.snapshot_id,
        "state": state,
        "reader_version": dto.reader_version,
        "canonical_content": None,
        "canonical_registry_content": None,
        "canonical_method_identity": None,
        "evidence": [],
    }


def evidence_read(request: HttpRequest, metric_id: str,
                  evidence_id: str) -> tuple[int, dict]:
    """Return one owner-scoped computed registry entry bound to its metric."""
    return _evidence_read(request, metric_id, evidence_id)


def _evidence_read(request: HttpRequest, metric_id: str,
                   evidence_id: str) -> tuple[int, dict]:
    preflight = _response_preflight(request)
    if preflight:
        return _error(*preflight)
    if not _uuid(metric_id) or not _uuid(evidence_id):
        return _error(404, "resource_not_available")
    try:
        store = SavedMetricStore.for_user(request.user)
        evidence: SavedMetricEvidence = store.get_metric_evidence(evidence_id)
    except MetricStoreRefusal as error:
        if error.reason_code == "resource_not_available":
            return _error(404, "resource_not_available")
        return _error(503, "retrieval_unavailable")
    except Exception:
        return _error(503, "retrieval_unavailable")

    parent = evidence.metric
    if parent.metric_id != metric_id:
        return _error(404, "resource_not_available")
    if parent.state != "complete":
        body = {
            "api_version": API_VERSION,
            "resource_type": RESOURCE_EVIDENCE,
            "evidence_id": evidence.evidence_id,
            "metric_id": parent.metric_id,
            "snapshot_id": parent.snapshot_id,
            "state": parent.state if parent.state in ("unsupported_decoder", "source_unavailable",
                "corrupt_content", "incomplete_graph", "unavailable") else "unavailable",
            "reader_version": parent.reader_version,
            "value_path": None,
            "canonical_registry_entry": None,
        }
        return 200, body

    try:
        entry = _ascii_document(evidence.canonical_registry_entry)
        _strict_registry_entry(entry, evidence.value_path)
        if entry["type"] == "numeric":
            unit = ("activity_count" if evidence.value_path.endswith("/activity_count") else
                    "percent" if evidence.value_path == "/percentage" else "integer_milliseconds")
            _exact_value(entry["payload"], unit)
    except (InvalidCanonical, UnicodeError, AttributeError, TypeError):
        return 200, {
            "api_version": API_VERSION,
            "resource_type": RESOURCE_EVIDENCE,
            "evidence_id": evidence.evidence_id,
            "metric_id": parent.metric_id,
            "snapshot_id": parent.snapshot_id,
            "state": "incomplete_graph",
            "reader_version": parent.reader_version,
            "value_path": None,
            "canonical_registry_entry": None,
        }
    if evidence.evidence_id != evidence_id:
        return _error(404, "resource_not_available")
    return 200, {
        "api_version": API_VERSION,
        "resource_type": RESOURCE_EVIDENCE,
        "evidence_id": evidence.evidence_id,
        "metric_id": parent.metric_id,
        "snapshot_id": parent.snapshot_id,
        "state": "complete",
        "reader_version": parent.reader_version,
        "value_path": evidence.value_path,
        "canonical_registry_entry": evidence.canonical_registry_entry.decode("ascii"),
    }


def _strict_registry_entry(entry: dict, expected_path: str) -> None:
    if type(expected_path) is not str or entry.get("path") != expected_path:
        raise InvalidCanonical("path mismatch")
    if entry.get("type") == "numeric":
        if set(entry) != {"path", "type", "payload", "values_kind", "derivation"}:
            raise InvalidCanonical("numeric keys")
        payload = entry.get("payload")
        if type(payload) is not dict:
            raise InvalidCanonical("numeric payload")
        status = payload.get("status")
        if status == "available":
            if set(payload) == {"unit", "precision", "status", "value"}:
                value = payload["value"]
                if type(value) is not str or not INTEGER_RE.fullmatch(value):
                    raise InvalidCanonical("integer grammar")
                if payload.get("precision") != "exact_integer":
                    raise InvalidCanonical("integer precision")
            elif set(payload) == {"unit", "precision", "status", "numerator", "denominator"}:
                numerator, denominator = payload["numerator"], payload["denominator"]
                if (type(numerator) is not str or not INTEGER_RE.fullmatch(numerator)
                        or type(denominator) is not str or not INTEGER_RE.fullmatch(denominator)
                        or denominator.startswith("-") or denominator == "0"
                        or payload.get("precision") != "exact_rational"):
                    raise InvalidCanonical("rational grammar")
                from fractions import Fraction
                if str(Fraction(int(numerator), int(denominator)).numerator) != numerator or str(Fraction(int(numerator), int(denominator)).denominator) != denominator:
                    raise InvalidCanonical("fraction not reduced")
            else:
                raise InvalidCanonical("numeric shape")
        elif status == "unavailable":
            if (set(payload) != {"unit", "precision", "status", "reason_code"}
                    or type(payload.get("reason_code")) is not str):
                raise InvalidCanonical("unavailable shape")
        else:
            raise InvalidCanonical("status")
    elif entry.get("type") == "structured_context":
        if set(entry) != {"path", "type", "payload", "derivation"}:
            raise InvalidCanonical("context keys")
    elif entry.get("type") == "sign_enum":
        if (set(entry) != {"path", "type", "payload", "values_kind", "derivation"}
                or entry.get("path") != "/classification"
                or entry.get("payload") not in ("increased", "decreased", "equal")):
            raise InvalidCanonical("classification shape")
    else:
        raise InvalidCanonical("unknown registry entry")


def _expected_registry_entries(content: dict, manifest: dict, paths: list[str]) -> list[dict]:
    """Build the exact v1 registry projection shape without recomputing values."""
    method = content["method_identity"]
    parameters = content["method_parameters"]
    binding = {"input_content_digest": content["input_content_digest"],
               "manifest_path": "/manifest", "method_identity": method,
               "method_parameters": parameters}
    entries = [
        {"path": "/manifest", "type": "structured_context", "payload": manifest,
         "derivation": {"input_content_digest": content["input_content_digest"],
                        "method_identity": method, "method_parameters": parameters}},
        {"path": "/eligibility", "type": "structured_context", "payload": content["eligibility"],
         "derivation": binding},
    ]

    def selection(members: list[str], **context) -> dict:
        return {**binding, **context, "members": members,
                "operand_roles": sorted(f"{member}.{field}" for member in members
                                         for field in CORE_OPERANDS)}

    def dependency(value_paths: list[str], **context) -> dict:
        return {**binding, **context, "value_paths": value_paths}

    if content["metric_code"] == "activity-summary":
        for group in content["values"]:
            bucket = next(bucket for bucket in manifest["buckets"]
                          if bucket["grouping"] == group["sport"])
            derivation = selection(bucket["members"], sport=group["sport"])
            for name in ("activity_count", "elapsed_ms"):
                entries.append({"path": f"/sports/{group['sport']}/{name}", "type": "numeric",
                                "payload": group[name], "values_kind": "eligible",
                                "derivation": derivation})
    else:
        kind = content["values_kind"]
        buckets = manifest["buckets"]
        for index, bucket in enumerate(buckets):
            derivation = selection(bucket["members"], start_utc=bucket["start_utc"],
                                   end_utc=bucket["end_utc"], limitations=bucket["limitations"])
            count = {"status": "available", "unit": "activity_count",
                     "precision": "exact_integer", "value": bucket["count"]}
            entries.extend((
                {"path": f"/weeks/{index}/activity_count", "type": "numeric", "payload": count,
                 "values_kind": kind, "derivation": derivation},
                {"path": f"/weeks/{index}/elapsed_ms", "type": "numeric", "payload": bucket["elapsed_ms"],
                 "values_kind": kind, "derivation": derivation},
            ))
        for name, indices in (("earlier_total", (0, 1)), ("later_total", (2, 3))):
            refs = [f"/weeks/{index}/elapsed_ms" for index in indices] if buckets else []
            entries.append({"path": f"/{name}", "type": "numeric", "payload": content["values"][name],
                            "values_kind": kind, "derivation": dependency(refs,
                                required_week_indices=[str(index) for index in indices],
                                effective_scope=content["effective_scope"])})
        for name, refs in (("signed_difference", ["/earlier_total", "/later_total"]),
                           ("magnitude", ["/earlier_total", "/later_total"]),
                           ("percentage", ["/signed_difference", "/earlier_total"])):
            entries.append({"path": f"/{name}", "type": "numeric", "payload": content["values"][name],
                            "values_kind": kind, "derivation": dependency(refs)})
        if "classification" in content:
            entries.append({"path": "/classification", "type": "sign_enum",
                            "payload": content["classification"], "values_kind": kind,
                            "derivation": dependency(["/signed_difference"])})
    entries.sort(key=lambda entry: entry["path"])
    if [entry["path"] for entry in entries] != sorted(paths):
        raise InvalidCanonical("registry projection paths")
    return entries


def decode_page_projection(envelope: dict) -> dict:
    """Independently fail-closed decoder for the HTML page support gate.

    It consumes the already store-validated outer carriers without calling the
    preparation code. A future payload remains available through the API but
    cannot be partly rendered by this page until this decoder is versioned.
    """
    if type(envelope) is not dict or set(envelope) != {
            "api_version", "resource_type", "metric_id", "snapshot_id", "state",
            "reader_version", "canonical_content", "canonical_registry_content",
            "canonical_method_identity", "evidence"}:
        raise InvalidCanonical("envelope keys")
    if (envelope.get("api_version") != API_VERSION
            or envelope.get("resource_type") != RESOURCE_METRIC
            or envelope.get("state") != "complete"
            or envelope.get("reader_version") != READER_VERSION
            or not _uuid(envelope.get("metric_id"))
            or not _uuid(envelope.get("snapshot_id"))):
        raise InvalidCanonical("envelope version")
    content_bytes = envelope["canonical_content"].encode("ascii")
    registry_bytes = envelope["canonical_registry_content"].encode("ascii")
    method_bytes = envelope["canonical_method_identity"].encode("ascii")
    content = _ascii_document(content_bytes)
    registry = _ascii_document(registry_bytes)
    method = _ascii_document(method_bytes)
    if (_canonical(content) != content_bytes or _canonical(registry) != registry_bytes
            or _canonical(method) != method_bytes):
        raise InvalidCanonical("noncanonical JSON bytes")
    if set(method) != {"method_id", "method_version", "specification_digest", "adapter_id", "adapter_version"}:
        raise InvalidCanonical("method identity keys")
    if (content.get("metric_contract_version") != PURE_CONTRACT_VERSION
            or content.get("codec_version") != CODEC_VERSION
            or content.get("supported_input_contract_version") != SOURCE_CONTRACT_VERSION
            or content.get("manifest", {}).get("manifest_version") != MANIFEST_VERSION
            or content.get("method_identity") != method
            or content.get("metric_code") not in ("activity-summary", "training-volume-trend")
            or method.get("method_id") != content.get("metric_code")
            or method.get("method_version") != "1"
            or method.get("specification_digest") != _SPECIFICATION_DIGEST
            or method.get("adapter_id") != "scoped-recorded-core"
            or method.get("adapter_version") != PURE_ADAPTER_VERSION
            or registry.get("persistence_contract_version") != PERSISTENCE_CONTRACT_VERSION
            or registry.get("registry_adapter_version") != REGISTRY_ADAPTER_VERSION
            or set(registry) != {"persistence_contract_version", "registry_adapter_version", "entries"}):
        raise InvalidCanonical("unsupported page contract")

    base = {"metric_contract_version", "metric_code", "method_identity",
            "supported_input_contract_version", "input_content_digest", "selected_scope",
            "effective_scope", "codec_version", "manifest", "operands", "limitations",
            "quality_records"}
    if content["metric_code"] == "activity-summary":
        required = base | {"grouping", "method_parameters", "eligibility", "values"}
        if set(content) != required or content["grouping"] != "per_sport" or content["method_parameters"] != {}:
            raise InvalidCanonical("summary fields")
        values = content["values"]
        if type(values) is not list:
            raise InvalidCanonical("summary values")
        sports = []
        paths = ["/manifest", "/eligibility"]
        for row in values:
            if type(row) is not dict or set(row) != {"sport", "activity_count", "elapsed_ms"}:
                raise InvalidCanonical("summary group")
            if type(row["sport"]) is not str:
                raise InvalidCanonical("sport")
            sports.append(row["sport"])
            paths.extend((f"/sports/{row['sport']}/activity_count", f"/sports/{row['sport']}/elapsed_ms"))
            _exact_value(row["activity_count"], "activity_count")
            _exact_value(row["elapsed_ms"], "integer_milliseconds")
        if sports != sorted(set(sports)):
            raise InvalidCanonical("sport order")
    else:
        required = base | {"grouping", "method_parameters", "eligibility", "outside_comparison",
                           "values_kind", "values"}
        if "classification" in content:
            required.add("classification")
        if (set(content) != required or content["grouping"] != "overall"
                or content["method_parameters"] != {"complete_weeks": "4",
                    "minimum_recorded_weeks": "3", "minimum_scope_days": "28",
                    "week_start": "monday_00_utc"}):
            raise InvalidCanonical("trend fields")
        if content.get("classification") not in (None, "increased", "decreased", "equal"):
            raise InvalidCanonical("classification")
        buckets = content.get("manifest", {}).get("buckets")
        if type(buckets) is not list or len(buckets) not in (0, 4):
            raise InvalidCanonical("week buckets")
        paths = ["/manifest", "/eligibility"]
        for index, bucket in enumerate(buckets):
            if type(bucket) is not dict or set(bucket) != {
                    "start_utc", "end_utc", "grouping", "members", "count", "elapsed_ms", "limitations"}:
                raise InvalidCanonical("week shape")
            paths.extend((f"/weeks/{index}/activity_count", f"/weeks/{index}/elapsed_ms"))
        names = ("earlier_total", "later_total", "signed_difference", "magnitude", "percentage")
        values = content.get("values")
        if type(values) is not dict or set(values) != set(names):
            raise InvalidCanonical("trend values")
        for name in names:
            _exact_value(values[name], "percent" if name == "percentage" else "integer_milliseconds")
            paths.append(f"/{name}")
        if "classification" in content:
            paths.append("/classification")

    eligibility = content.get("eligibility")
    if (type(eligibility) is not dict or set(eligibility) != {"eligible", "unmet_reasons"}
            or type(eligibility["eligible"]) is not bool
            or type(eligibility["unmet_reasons"]) is not list
            or any(type(item) is not str for item in eligibility["unmet_reasons"])):
        raise InvalidCanonical("eligibility")
    manifest = content.get("manifest")
    if (type(manifest) is not dict or set(manifest) != {
            "manifest_version", "selected_scope", "effective_scope", "members", "exclusions", "buckets"}
            or manifest["selected_scope"] != content.get("selected_scope")
            or manifest["effective_scope"] != content.get("effective_scope")
            or type(manifest["members"]) is not list or type(manifest["exclusions"]) is not list
            or type(content.get("operands")) is not list
            or type(content.get("limitations")) is not list
            or type(content.get("quality_records")) is not list):
        raise InvalidCanonical("manifest")

    _validate_scope(content["selected_scope"])
    member_ids = _validate_source_graph(content, manifest)
    if (content["limitations"] != ["recorded_data_only", "utc_start_attribution",
                                   "optional_metrics_excluded"]
            or content["quality_records"] != []):
        raise InvalidCanonical("top-level limitations/quality")
    eligible = eligibility["eligible"]
    if eligible != (not eligibility["unmet_reasons"]):
        raise InvalidCanonical("eligibility consistency")

    # The saved manifest is a second disclosure of membership. Validate the
    # pinned summary/trend shapes and their references before allowing the page
    # decoder to render any of its nested values.
    member_by_id = {item["normalization_digest"]: item for item in manifest["members"]}
    buckets = manifest["buckets"]
    if type(buckets) is not list:
        raise InvalidCanonical("manifest buckets")
    if content["metric_code"] == "activity-summary":
        expected_reasons = [] if member_ids else ["no_included_activity"]
        if eligibility["unmet_reasons"] != expected_reasons:
            raise InvalidCanonical("summary eligibility reasons")
        expected_sports = sorted({member_by_id[item]["sport"] for item in member_ids})
        if sports != expected_sports:
            raise InvalidCanonical("summary sport coverage")
        if len(buckets) != len(expected_sports):
            raise InvalidCanonical("summary bucket count")
        for bucket, sport in zip(buckets, expected_sports):
            expected_members = [item for item in member_ids if member_by_id[item]["sport"] == sport]
            if (type(bucket) is not dict or set(bucket) != {"grouping", "members", "count", "limitations"}
                    or bucket["grouping"] != sport or bucket["members"] != expected_members
                    or bucket["count"] != str(len(expected_members))
                    or bucket["limitations"] != ["recorded_data_only"]):
                raise InvalidCanonical("summary bucket")
        for row in values:
            bucket = next(bucket for bucket in buckets if bucket["grouping"] == row["sport"])
            if row["activity_count"] != {
                    "unit": "activity_count", "precision": "exact_integer",
                    "status": "available", "value": bucket["count"]}:
                raise InvalidCanonical("summary count does not match manifest")
        effective = content["effective_scope"]
        if (type(effective) is not dict or set(effective) != {"start_utc", "end_utc"}
                or effective["start_utc"] != content["selected_scope"]["start_utc"]
                or effective["end_utc"] != content["selected_scope"]["end_utc"]):
            raise InvalidCanonical("summary effective scope")
    else:
        if content.get("values_kind") != ("eligible" if eligible else "ineligible_diagnostic"):
            raise InvalidCanonical("trend values kind")
        if len(buckets) not in (0, 4):
            raise InvalidCanonical("trend bucket count")
        scoped_start = content["selected_scope"]["start_utc"]
        scoped_end = content["selected_scope"]["end_utc"]
        end_dt = datetime.strptime(scoped_end, "%Y-%m-%dT%H:%M:%SZ")
        comparison_end = end_dt - timedelta(days=end_dt.weekday(), hours=end_dt.hour,
                                            minutes=end_dt.minute, seconds=end_dt.second)
        comparison_start = comparison_end - timedelta(days=28)
        comparison_start_utc = comparison_start.strftime("%Y-%m-%dT%H:%M:%SZ")
        expected_reasons = []
        if _utc_epoch(scoped_end) - _utc_epoch(scoped_start) < 28 * 86400:
            expected_reasons.append("scope_less_than_28_days")
        if scoped_start > comparison_start_utc:
            expected_reasons.append("fewer_than_four_complete_weeks")
        expected_bucket_count = 0 if "fewer_than_four_complete_weeks" in expected_reasons else 4
        if len(buckets) != expected_bucket_count:
            raise InvalidCanonical("trend complete-week coverage")
        comparison = set()
        previous_end = None
        for index, bucket in enumerate(buckets):
            if type(bucket) is not dict or set(bucket) != {
                    "start_utc", "end_utc", "grouping", "members", "count", "elapsed_ms", "limitations"}:
                raise InvalidCanonical("trend bucket shape")
            start, end = bucket["start_utc"], bucket["end_utc"]
            _require_utc(start)
            _require_utc(end)
            start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
            end_dt = datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
            expected_start = comparison_start + timedelta(days=7 * index)
            expected_end = expected_start + timedelta(days=7)
            if (bucket["grouping"] != "overall" or end_dt - start_dt != timedelta(days=7)
                    or start_dt.weekday() != 0 or start_dt.hour or start_dt.minute or start_dt.second
                    or start_dt != expected_start or end_dt != expected_end
                    or start < scoped_start or end > scoped_end or (previous_end and start != previous_end)):
                raise InvalidCanonical("trend bucket interval")
            previous_end = end
            expected_members = [item for item in member_ids
                                if start <= member_by_id[item]["start_utc"] < end]
            if (bucket["members"] != expected_members
                    or bucket["count"] != str(len(expected_members))
                    or bucket["limitations"] != ["recorded_data_only"] +
                       ([] if expected_members else ["missing_records"])):
                raise InvalidCanonical("trend bucket membership")
            if comparison.intersection(expected_members):
                raise InvalidCanonical("overlapping trend members")
            comparison.update(expected_members)
            _exact_value(bucket["elapsed_ms"], "integer_milliseconds")
        expected_outside = [item for item in member_ids if item not in comparison]
        if content["outside_comparison"] != expected_outside:
            raise InvalidCanonical("outside-comparison membership")
        if buckets:
            expected_effective = {"start_utc": buckets[0]["start_utc"],
                                  "end_utc": buckets[-1]["end_utc"]}
            if content["effective_scope"] != expected_effective:
                raise InvalidCanonical("trend effective scope")
        elif content["effective_scope"] != {"status": "unavailable", "reason_code": "insufficient_scope"}:
            raise InvalidCanonical("trend unavailable scope")
        if buckets and sum(bool(bucket["members"]) for bucket in buckets) < 3:
            expected_reasons.append("fewer_than_three_recorded_weeks")
        if eligibility["unmet_reasons"] != expected_reasons:
            raise InvalidCanonical("trend eligibility consistency")
        if ("classification" in content) != eligible:
            raise InvalidCanonical("trend classification availability")
        if eligible:
            difference = content["values"]["signed_difference"]
            if difference.get("status") != "available":
                raise InvalidCanonical("eligible trend difference")
            signed = int(difference["value"])
            expected_classification = "increased" if signed > 0 else "decreased" if signed < 0 else "equal"
            if content["classification"] != expected_classification:
                raise InvalidCanonical("trend sign classification")
        allowed_reasons = ["scope_less_than_28_days", "fewer_than_four_complete_weeks",
                           "fewer_than_three_recorded_weeks"]
        reasons = eligibility["unmet_reasons"]
        if (type(reasons) is not list or any(item not in allowed_reasons for item in reasons)
                or reasons != [item for item in allowed_reasons if item in reasons]):
            raise InvalidCanonical("trend eligibility reasons")

    entries = registry.get("entries")
    if type(entries) is not list or [item.get("path") for item in entries if type(item) is dict] != sorted(paths):
        raise InvalidCanonical("registry paths")
    for expected, entry in zip(sorted(paths), entries):
        _strict_registry_entry(entry, expected)
        if entry["type"] == "numeric":
            payload = entry["payload"]
            unit = ("activity_count" if expected.endswith("/activity_count") else
                    "percent" if expected == "/percentage" else "integer_milliseconds")
            _exact_value(payload, unit)
            if entry.get("values_kind") not in ("eligible", "ineligible_diagnostic"):
                raise InvalidCanonical("numeric values kind")
        derivation = entry.get("derivation")
        if type(derivation) is not dict:
            raise InvalidCanonical("derivation")
        refs = derivation.get("value_paths", [])
        if type(refs) is not list or any(type(path) is not str or path not in paths for path in refs):
            raise InvalidCanonical("unresolved derivation path")

    expected_entries = _expected_registry_entries(content, manifest, paths)
    if len(entries) != len(expected_entries):
        raise InvalidCanonical("registry entry count")
    for entry, expected_entry in zip(entries, expected_entries):
        if _canonical(entry) != _canonical(expected_entry):
            raise InvalidCanonical("registry payload or derivation mismatch")
    evidence = envelope.get("evidence")
    if type(evidence) is not list or len(evidence) != len(entries):
        raise InvalidCanonical("evidence set")
    by_path = {item["value_path"]: item for item in evidence
               if type(item) is dict and set(item) == {"evidence_id", "value_path", "href"}}
    if len(by_path) != len(evidence) or set(by_path) != set(paths):
        raise InvalidCanonical("evidence references")
    for path, item in by_path.items():
        if (not _uuid(item["evidence_id"])
                or item["href"] != f"/api/v1/recorded-metrics/{envelope['metric_id']}/evidence/{item['evidence_id']}"):
            raise InvalidCanonical("evidence href")

    return {"content": content, "entries": [dict(path=entry["path"], payload=entry.get("payload"),
                type=entry["type"], derivation=entry["derivation"],
                href=by_path[entry["path"]]["href"]) for entry in entries]}


def _exact_value(value: object, expected_unit: str) -> None:
    if type(value) is not dict or value.get("unit") != expected_unit:
        raise InvalidCanonical("value shape")
    precision = "exact_rational" if expected_unit == "percent" else "exact_integer"
    if value.get("precision") != precision:
        raise InvalidCanonical("value precision")
    if value.get("status") == "unavailable":
        if set(value) != {"unit", "precision", "status", "reason_code"} or type(value["reason_code"]) is not str:
            raise InvalidCanonical("unavailable value")
    elif value.get("status") == "available":
        if set(value) == {"unit", "precision", "status", "value"}:
            if expected_unit == "percent" or type(value["value"]) is not str or not INTEGER_RE.fullmatch(value["value"]):
                raise InvalidCanonical("integer value")
        elif set(value) == {"unit", "precision", "status", "numerator", "denominator"} and expected_unit == "percent":
            numerator, denominator = value["numerator"], value["denominator"]
            if (type(numerator) is not str or not INTEGER_RE.fullmatch(numerator)
                    or type(denominator) is not str or not INTEGER_RE.fullmatch(denominator)
                    or denominator.startswith("-") or denominator == "0"):
                raise InvalidCanonical("fraction")
            from fractions import Fraction
            fraction = Fraction(int(numerator), int(denominator))
            if str(fraction.numerator) != numerator or str(fraction.denominator) != denominator:
                raise InvalidCanonical("fraction reduction")
        else:
            raise InvalidCanonical("available value")
    else:
        raise InvalidCanonical("value status")


__all__ = ["API_VERSION", "ERROR_MESSAGES", "metric_read", "evidence_read",
           "decode_page_projection", "_status_message"]
