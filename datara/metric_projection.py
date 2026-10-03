"""Internal saved-recorded registry projection, without storage or authorization.

WP02/WP03; CUS03-05/CUS08/CUS10; SR05-11/SR20-21/SR28-29.
Only validated frozen recorded results enter this adapter. Portable metric bytes
are preserved; persistence addresses have their own version and digest. This
module establishes neither saved graph completeness nor owner access.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from datara.recorded_metrics import (
    PreparedSummary, PreparedTrend, RecordedInputRefusal, canonical_metric_content,
)

PERSISTENCE_CONTRACT_VERSION = "datara/saved-recorded-aggregate/1"
REGISTRY_ADAPTER_VERSION = "recorded-persistence-registry/1"
OPERAND_PROJECTION_VERSION = "recorded-source-operands/1"
READER_VERSION = "saved-recorded-reader/1"
PURE_CONTRACT_VERSION = "datara/internal-recorded-metrics/1"
PURE_ADAPTER_VERSION = "scoped-recorded-core/1"
MANIFEST_VERSION = "recorded-membership/1"
CODEC_VERSION = "ascii-json-integer-strings/1"
SOURCE_CONTRACT_VERSION = "datara-milestone-a/scoped-input/1"
SCOPED_INPUT_VERSION = "tk21-scoped-input/1"

__all__ = ["project_recorded_result"]


def _canonical(document: dict) -> bytes:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _digest(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _binding(document: dict) -> dict:
    return {
        "input_content_digest": document["input_content_digest"],
        "manifest_path": "/manifest",
        "method_identity": document["method_identity"],
        "method_parameters": document["method_parameters"],
    }


def _selection(document: dict, members: list[str], **context) -> dict:
    """Bind both elapsed arithmetic and count membership to all core sources."""
    return {
        **_binding(document), **context, "members": members,
        "operand_roles": sorted(
            f"{member}.{field}" for member in members
            for field in ("elapsed_duration_ms", "sport", "start_epoch_seconds")
        ),
    }


def _dependency(document: dict, paths: tuple[str, ...], **context) -> dict:
    return {**_binding(document), **context, "value_paths": list(paths)}


def _numeric(path: str, value: dict, derivation: dict, kind: str) -> dict:
    # Exact numeric grammar, unit, precision and availability have already been
    # independently recomputed by canonical_metric_content, including fractions.
    return {"path": path, "type": "numeric", "payload": value,
            "values_kind": kind, "derivation": derivation}


def _registry(document: dict) -> dict:
    manifest = document["manifest"]
    entries = [
        {"path": "/manifest", "type": "structured_context",
         "payload": manifest, "derivation": {
             "input_content_digest": document["input_content_digest"],
             "method_identity": document["method_identity"],
             "method_parameters": document["method_parameters"],
         }},
        {"path": "/eligibility", "type": "structured_context",
         "payload": document["eligibility"], "derivation": _binding(document)},
    ]
    if document["metric_code"] == "activity-summary":
        for group in document["values"]:
            sport = group["sport"]
            # Match actual unique sport tokens, never infer sport from position.
            bucket = next(item for item in manifest["buckets"]
                          if item["grouping"] == sport)
            derivation = _selection(document, bucket["members"], sport=sport)
            for name in ("activity_count", "elapsed_ms"):
                entries.append(_numeric(f"/sports/{sport}/{name}", group[name],
                                        derivation, "eligible"))
    else:
        kind = document["values_kind"]
        buckets = manifest["buckets"]
        for index, bucket in enumerate(buckets):
            derivation = _selection(document, bucket["members"],
                                    start_utc=bucket["start_utc"],
                                    end_utc=bucket["end_utc"],
                                    limitations=bucket["limitations"])
            count = {"status": "available", "unit": "activity_count",
                     "precision": "exact_integer", "value": bucket["count"]}
            entries.append(_numeric(f"/weeks/{index}/activity_count", count,
                                    derivation, kind))
            entries.append(_numeric(f"/weeks/{index}/elapsed_ms", bucket["elapsed_ms"],
                                    derivation, kind))
        for name, indices in (("earlier_total", (0, 1)), ("later_total", (2, 3))):
            # An insufficient scope has no week addresses. Preserve declared
            # unavailability and the required comparison policy, without zeros
            # or references to registry paths that do not exist.
            derivation = _dependency(document,
                tuple(f"/weeks/{i}/elapsed_ms" for i in indices) if buckets else (),
                required_week_indices=[str(i) for i in indices],
                effective_scope=document["effective_scope"])
            entries.append(_numeric(f"/{name}", document["values"][name], derivation, kind))
        for name, paths in (
            ("signed_difference", ("/earlier_total", "/later_total")),
            ("magnitude", ("/earlier_total", "/later_total")),
            ("percentage", ("/signed_difference", "/earlier_total")),
        ):
            entries.append(_numeric(f"/{name}", document["values"][name],
                                    _dependency(document, paths), kind))
        if "classification" in document:
            entries.append({"path": "/classification", "type": "sign_enum",
                            "payload": document["classification"],
                            "values_kind": kind,
                            "derivation": _dependency(document, ("/signed_difference",))})
    return {
        "persistence_contract_version": PERSISTENCE_CONTRACT_VERSION,
        "registry_adapter_version": REGISTRY_ADAPTER_VERSION,
        "entries": sorted(entries, key=lambda entry: entry["path"]),
    }


@dataclass(frozen=True, init=False)
class _RecordedProjection:
    """Immutable internal carrier; even direct construction validates a result."""
    canonical_content: bytes
    content_digest: str
    canonical_registry_content: bytes
    registry_projection_digest: str
    canonical_operand_content: bytes

    def __init__(self, prepared: PreparedSummary | PreparedTrend) -> None:
        content = canonical_metric_content(prepared)
        document = json.loads(content)
        if (document["metric_contract_version"] != PURE_CONTRACT_VERSION
                or document["codec_version"] != CODEC_VERSION
                or document["supported_input_contract_version"] != SOURCE_CONTRACT_VERSION
                or document["manifest"]["manifest_version"] != MANIFEST_VERSION
                or document["method_identity"]["adapter_version"] != PURE_ADAPTER_VERSION
                or json.loads(prepared.source.source_canonical_content)["scoped_input_version"]
                != SCOPED_INPUT_VERSION):
            raise RecordedInputRefusal("unsupported_persistence_projection_version")
        registry = _canonical(_registry(document))
        operands = _canonical({
            "operand_projection_version": OPERAND_PROJECTION_VERSION,
            "operands": [{"role": operand["role"], "ordinal": ordinal,
                          "source": operand["source"]}
                         for ordinal, operand in enumerate(document["operands"])],
        })
        for name, value in (
            ("canonical_content", content), ("content_digest", _digest(content)),
            ("canonical_registry_content", registry),
            ("registry_projection_digest", _digest(registry)),
            ("canonical_operand_content", operands),
        ):
            object.__setattr__(self, name, value)

    def registry_document(self) -> dict:
        """Return a fresh mutable view; edits cannot change the projection."""
        return json.loads(self.canonical_registry_content)

    def operand_document(self) -> dict:
        """Exact source-only roles/ordinals/identities for service resolution."""
        return json.loads(self.canonical_operand_content)

    def evidence_paths(self) -> tuple[str, ...]:
        return tuple(entry["path"] for entry in self.registry_document()["entries"])


def project_recorded_result(prepared: PreparedSummary | PreparedTrend) -> _RecordedProjection:
    """Revalidate the supported result and build its exhaustive version1 registry.

    Arbitrary canonical bytes, subclasses and fabricated result/source carriers
    are refused by the pure validation boundary. No database identities, foreign
    metric operands or additional arithmetic policies are accepted here.
    """
    return _RecordedProjection(prepared)
