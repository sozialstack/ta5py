"""Aggregate maintainer-visible governance status."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ta5py.governance.store import (
    latest_detection_run,
    list_candidates,
    list_detection_runs,
    load_check_metadata,
    load_live_binding,
)
from ta5py.governance.validate_state import validate_status_payload
from ta5py.spec_loader import SPEC_ROOT


def gather_status(spec_root: Path | None = None) -> dict[str, Any]:
    root = spec_root if spec_root is not None else SPEC_ROOT
    live = load_live_binding(root)
    if live is None:
        live_dict: dict[str, Any] = {
            "package_label": "v21",
            "activated_at": "1970-01-01T00:00:00+00:00",
            "activated_by": "missing",
            "approval_ref": "missing",
        }
    else:
        live_dict = live.to_dict()
        live_dict.pop("note", None)

    detections = [r.to_dict() for r in list_detection_runs(root)]
    candidates = []
    for c in list_candidates(root):
        d = c.to_dict()
        # Intentional: source_publications is internal integrate payload, not status schema
        d.pop("source_publications", None)
        candidates.append(d)

    # Schema currently omits out_of_scope_ids; keep on detections for operators,
    # strip only when validating against strict schema copy.
    last = latest_detection_run(root)
    oos_ids: list[str] = list(last.out_of_scope_ids) if last else []
    check_meta = load_check_metadata(root)

    payload: dict[str, Any] = {
        "live": live_dict,
        "detections": detections,
        "candidates": candidates,
        "out_of_scope": {
            "ids": oos_ids,
            "gate_state": "ignored" if oos_ids else "none",
        },
        "check_metadata": check_meta or None,
    }
    # Validate schema-compatible core (live/detections/candidates)
    schema_view = {
        "live": live_dict,
        "detections": detections,
        "candidates": candidates,
    }
    errors = validate_status_payload(schema_view)
    payload["_validation_errors"] = errors
    return payload

def format_status_human(payload: dict[str, Any]) -> str:
    live = payload.get("live") or {}
    lines = [
        f"Live package: {live.get('package_label')} (by {live.get('activated_by')})",
        "",
        "Recent detections:",
    ]
    detections = payload.get("detections") or []
    if not detections:
        lines.append("  (none)")
    else:
        last = detections[-1]
        lines.append(
            f"  last: {last.get('id')} status={last.get('status')} "
            f"new={last.get('new_or_changed_ids')}"
        )
        oos = last.get("out_of_scope_ids") or (payload.get("out_of_scope") or {}).get("ids") or []
        if oos:
            gate = (payload.get("out_of_scope") or {}).get("gate_state", "ignored")
            lines.append(f"  out_of_scope ({gate}): {oos}")
        if last.get("error_message"):
            lines.append(f"  error: {last['error_message']}")

    check = payload.get("check_metadata") or {}
    if check:
        lines.append("")
        lines.append(
            f"Check metadata: last={check.get('last_check_at')} "
            f"status={check.get('last_check_status')} etag={check.get('etag')}"
        )

    lines.append("")
    lines.append("Candidates:")
    cands = payload.get("candidates") or []
    if not cands:
        lines.append("  (none)")
    else:
        for c in cands:
            lines.append(
                f"  {c.get('id')}: state={c.get('state')} branch={c.get('branch_name')} "
                f"package={c.get('package_label')}"
            )
            approval = c.get("approval")
            if approval:
                lines.append(
                    f"    approval={approval.get('decision')} by {approval.get('actor')}"
                )

    oos_block = payload.get("out_of_scope") or {}
    if oos_block.get("ids"):
        lines.append("")
        lines.append(
            f"Out-of-scope publications (gate={oos_block.get('gate_state')}): "
            f"{oos_block.get('ids')}"
        )
    return "\n".join(lines) + "\n"
