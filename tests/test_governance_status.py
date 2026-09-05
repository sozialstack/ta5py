from __future__ import annotations

from pathlib import Path

from ta5py.governance.detect import run_detection
from ta5py.governance.models import IntegrationCandidate, LiveVersionBinding
from ta5py.governance.status import format_status_human, gather_status
from ta5py.governance.store import save_candidate, save_live_binding
from ta5py.governance.validate_state import validate_status_payload

FIXTURES = Path(__file__).parent / "fixtures" / "governance"
KNOWN = FIXTURES / "sources_known.yaml"
NEW = FIXTURES / "sources_with_new_version.yaml"


def test_status_shows_pending_and_rejected(tmp_path: Path):
    root = tmp_path / "spec"
    (root / "governance" / "detections").mkdir(parents=True)
    (root / "governance" / "candidates").mkdir(parents=True)
    save_live_binding(
        LiveVersionBinding(
            package_label="v21",
            activated_at="2026-08-17T00:00:00+00:00",
            activated_by="bootstrap",
            approval_ref="bootstrap",
        ),
        root,
    )
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=root)
    save_candidate(
        IntegrationCandidate(
            id="v99",
            package_label="v99",
            branch_name="ta5py/spec-v99-integration",
            source_publication_ids=["x"],
            state="rejected",
            created_at="2026-08-17T01:00:00+00:00",
            updated_at="2026-08-17T01:00:00+00:00",
        ),
        root,
    )
    payload = gather_status(root)
    assert payload["live"]["package_label"] == "v21"
    states = {c["id"]: c["state"] for c in payload["candidates"]}
    assert "v23" in states
    assert states["v99"] == "rejected"
    human = format_status_human(payload)
    assert "v99" in human and "rejected" in human
    assert "awaiting_approval" in human or "detected" in human
    assert "out_of_scope" in human.lower() or "heilmittel" in human
    assert payload["out_of_scope"]["ids"]
    assert payload["out_of_scope"]["gate_state"] == "ignored"
    schema_view = {
        "live": payload["live"],
        "detections": payload["detections"],
        "candidates": payload["candidates"],
    }
    errors = validate_status_payload(schema_view)
    assert errors == []