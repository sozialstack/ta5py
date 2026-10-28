"""Validate governance status payloads against the feature contract schema (intentional subset)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "specs"
    / "002-auto-spec-integration"
    / "contracts"
    / "governance-state.schema.json"
)

# Intentional extras beyond governance-state.schema.json (T046):
# - Operator status may include top-level `out_of_scope` and `check_metadata`.
# - Candidate `source_publications` is stripped before status schema validation.
# - Core live/detections/candidates (including out_of_scope_ids / error_message)
#   are validated structurally; full Draft 2020-12 runs when jsonschema is installed.


def load_governance_schema() -> dict[str, Any]:
    try:
        data = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FileNotFoundError(f"governance schema unreadable: {SCHEMA_PATH}") from exc
    if not isinstance(data, dict):
        raise TypeError(f"governance schema must be a JSON object: {SCHEMA_PATH}")
    return data


def _check_detection(item: Any, index: int, errors: list[str]) -> None:
    if not isinstance(item, dict):
        errors.append(f"detections[{index}] must be object")
        return
    for req in ("id", "started_at", "finished_at", "status"):
        if req not in item:
            errors.append(f"detections[{index}] missing: {req}")
    status = item.get("status")
    if status is not None and status not in {"ok", "failed", "partial"}:
        errors.append(f"detections[{index}] invalid status: {status}")


def _check_candidate(item: Any, index: int, errors: list[str]) -> None:
    if not isinstance(item, dict):
        errors.append(f"candidates[{index}] must be object")
        return
    for req in (
        "id",
        "package_label",
        "branch_name",
        "source_publication_ids",
        "state",
        "created_at",
        "updated_at",
    ):
        if req not in item:
            errors.append(f"candidates[{index}] missing: {req}")
    label = item.get("package_label")
    if isinstance(label, str) and not label.startswith("v"):
        errors.append(f"candidates[{index}].package_label must look like vN")
    state = item.get("state")
    allowed = {
        "detected",
        "integrating",
        "awaiting_approval",
        "live",
        "failed",
        "rejected",
    }
    if state is not None and state not in allowed:
        errors.append(f"candidates[{index}] invalid state: {state}")
    pubs = item.get("source_publication_ids")
    if pubs is not None and (not isinstance(pubs, list) or len(pubs) < 1):
        errors.append(f"candidates[{index}].source_publication_ids must be non-empty array")
    approval = item.get("approval")
    if approval is not None:
        if not isinstance(approval, dict):
            errors.append(f"candidates[{index}].approval must be object or null")
        else:
            for req in ("decision", "actor", "decided_at"):
                if req not in approval:
                    errors.append(f"candidates[{index}].approval missing: {req}")
            if approval.get("decision") not in {None, "approve", "reject"}:
                errors.append(f"candidates[{index}].approval.decision invalid")


def validate_status_payload(payload: dict[str, Any]) -> list[str]:
    """Structural checks aligned with governance-state.schema.json (core subset)."""
    errors: list[str] = []
    for key in ("live", "detections", "candidates"):
        if key not in payload:
            errors.append(f"missing key: {key}")
    live = payload.get("live")
    if isinstance(live, dict):
        for req in ("package_label", "activated_at", "activated_by", "approval_ref"):
            if req not in live:
                errors.append(f"live missing: {req}")
        label = live.get("package_label")
        if isinstance(label, str) and not label.startswith("v"):
            errors.append("live.package_label must look like vN")
    elif live is not None:
        errors.append("live must be object")

    detections = payload.get("detections")
    if detections is not None:
        if not isinstance(detections, list):
            errors.append("detections must be array")
        else:
            for i, item in enumerate(detections):
                _check_detection(item, i, errors)

    candidates = payload.get("candidates")
    if candidates is not None:
        if not isinstance(candidates, list):
            errors.append("candidates must be array")
        else:
            for i, item in enumerate(candidates):
                _check_candidate(item, i, errors)

    # Optional: full Draft 2020-12 validation when jsonschema is installed
    try:
        import jsonschema

        schema = load_governance_schema()

        def _omit_none(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _omit_none(v) for k, v in obj.items() if v is not None}
            if isinstance(obj, list):
                return [_omit_none(v) for v in obj]
            return obj

        core = _omit_none(
            {
                "live": payload.get("live"),
                "detections": payload.get("detections"),
                "candidates": [
                    {k: v for k, v in c.items() if k != "source_publications"}
                    if isinstance(c, dict)
                    else c
                    for c in (payload.get("candidates") or [])
                ],
            }
        )
        validator_cls = jsonschema.Draft202012Validator
        for err in sorted(validator_cls(schema).iter_errors(core), key=lambda e: e.path):
            errors.append(f"schema: {err.message}")
    except ImportError:
        pass
    except (OSError, json.JSONDecodeError, FileNotFoundError) as exc:
        errors.append(f"schema: failed to load {SCHEMA_PATH.name}: {exc}")

    return errors
