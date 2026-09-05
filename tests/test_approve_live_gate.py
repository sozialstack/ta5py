from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from gkv_edi.governance.approve import ApprovalError, approve_candidate, go_live
from gkv_edi.governance.detect import run_detection
from gkv_edi.governance.integrate import integrate_candidate
from gkv_edi.governance.models import LiveVersionBinding
from gkv_edi.governance.store import load_candidate, load_live_binding, save_live_binding
from gkv_edi.spec_loader import SPEC_ROOT

FIXTURES = Path(__file__).parent / "fixtures" / "governance"
KNOWN = FIXTURES / "sources_known.yaml"
NEW = FIXTURES / "sources_with_new_version.yaml"


def _spec(tmp_path: Path) -> Path:
    spec = tmp_path / "spec"
    shutil.copytree(SPEC_ROOT / "v21", spec / "v21")
    (spec / "official").mkdir(parents=True)
    shutil.copy(KNOWN, spec / "official" / "sources.manifest.yaml")
    (spec / "governance" / "detections").mkdir(parents=True)
    (spec / "governance" / "candidates").mkdir(parents=True)
    save_live_binding(
        LiveVersionBinding(
            package_label="v21",
            activated_at="2026-08-17T00:00:00+00:00",
            activated_by="bootstrap",
            approval_ref="bootstrap",
        ),
        spec,
    )
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=spec)
    integrate_candidate(
        from_latest_new=True,
        create_git_branch=False,
        spec_root=spec,
        base_package="v21",
        repo_root=tmp_path,
        known_manifest=spec / "official" / "sources.manifest.yaml",
    )
    return spec


def test_go_live_without_approval_fails(tmp_path: Path):
    spec = _spec(tmp_path)
    before = load_live_binding(spec).package_label
    with pytest.raises(ApprovalError, match="missing human approval"):
        go_live("v23", actor="ci-bot", spec_root=spec)
    assert load_live_binding(spec).package_label == before


def test_approve_then_go_live(tmp_path: Path):
    spec = _spec(tmp_path)
    approve_candidate("v23", actor="maintainer@example", decision="approve", spec_root=spec)
    binding = go_live("v23", actor="maintainer@example", spec_root=spec)
    assert binding.package_label == "v23"
    assert load_live_binding(spec).package_label == "v23"
    assert load_candidate("v23", spec).state == "live"
    assert binding.activated_by == "maintainer@example"
    assert binding.approval_ref.startswith("v23:")


def test_reject_leaves_live_unchanged(tmp_path: Path):
    spec = _spec(tmp_path)
    before = load_live_binding(spec).package_label
    approve_candidate("v23", actor="maintainer@example", decision="reject", spec_root=spec)
    assert load_candidate("v23", spec).state == "rejected"
    with pytest.raises(ApprovalError):
        go_live("v23", actor="maintainer@example", spec_root=spec)
    assert load_live_binding(spec).package_label == before


def test_only_approved_candidate_goes_live(tmp_path: Path):
    spec = _spec(tmp_path)
    from datetime import datetime, timezone

    from gkv_edi.governance.models import IntegrationCandidate
    from gkv_edi.governance.store import save_candidate

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    other = IntegrationCandidate(
        id="v24",
        package_label="v24",
        branch_name="gkv-edi/spec-v24-integration",
        source_publication_ids=["synthetic"],
        state="awaiting_approval",
        created_at=now,
        updated_at=now,
    )
    save_candidate(other, spec)
    shutil.copytree(spec / "v21", spec / "v24")

    approve_candidate("v23", actor="maintainer@example", decision="approve", spec_root=spec)
    go_live("v23", actor="maintainer@example", spec_root=spec)
    assert load_live_binding(spec).package_label == "v23"
    assert load_candidate("v24", spec).state == "awaiting_approval"


def test_go_live_refuses_corrupt_package(tmp_path: Path):
    spec = _spec(tmp_path)
    approve_candidate("v23", actor="maintainer@example", decision="approve", spec_root=spec)
    (spec / "v23" / "una.yaml").unlink()
    before = load_live_binding(spec).package_label
    with pytest.raises(ApprovalError, match="incomplete or corrupt"):
        go_live("v23", actor="maintainer@example", spec_root=spec)
    assert load_live_binding(spec).package_label == before
    assert load_candidate("v23", spec).state == "failed"


def test_go_live_older_over_newer_requires_confirm(tmp_path: Path):
    spec = tmp_path / "spec"
    shutil.copytree(SPEC_ROOT / "v21", spec / "v21")
    shutil.copytree(SPEC_ROOT / "v22", spec / "v22")
    (spec / "governance" / "detections").mkdir(parents=True)
    (spec / "governance" / "candidates").mkdir(parents=True)
    save_live_binding(
        LiveVersionBinding(
            package_label="v22",
            activated_at="2026-08-17T00:00:00+00:00",
            activated_by="bootstrap",
            approval_ref="bootstrap",
        ),
        spec,
    )
    from datetime import datetime, timezone

    from gkv_edi.governance.models import IntegrationCandidate
    from gkv_edi.governance.store import save_candidate

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    save_candidate(
        IntegrationCandidate(
            id="v21",
            package_label="v21",
            branch_name="gkv-edi/spec-v21-integration",
            source_publication_ids=["anlage-1-v21"],
            state="awaiting_approval",
            created_at=now,
            updated_at=now,
        ),
        spec,
    )
    approve_candidate("v21", actor="maintainer@example", decision="approve", spec_root=spec)
    with pytest.raises(ApprovalError, match="older package"):
        go_live("v21", actor="maintainer@example", spec_root=spec)
    binding = go_live(
        "v21",
        actor="maintainer@example",
        spec_root=spec,
        confirm_older=True,
    )
    assert binding.package_label == "v21"
    assert "WARNING" in (binding.note or "")
