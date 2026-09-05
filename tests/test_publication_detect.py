from __future__ import annotations

from pathlib import Path

from gkv_edi.governance.detect import run_detection, should_auto_integrate
from gkv_edi.governance.discover import parse_overview_html
from gkv_edi.governance.models import ApprovalDecision, IntegrationCandidate, LiveVersionBinding
from gkv_edi.governance.store import (
    list_candidates,
    load_candidate,
    load_check_metadata,
    load_live_binding,
    save_candidate,
    save_live_binding,
)

FIXTURES = Path(__file__).parent / "fixtures" / "governance"
KNOWN = FIXTURES / "sources_known.yaml"
NEW = FIXTURES / "sources_with_new_version.yaml"
OVERVIEW_HTML = FIXTURES / "overview_snapshot.html"


def _gov_root(tmp_path: Path) -> Path:
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
    return root


def test_detects_new_in_scope_version(tmp_path: Path):
    root = _gov_root(tmp_path)
    before = load_live_binding(root)
    run = run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=root)
    assert run.status == "ok"
    assert "anlage-1-v23" in run.new_or_changed_ids
    assert "anlage-3-v23" in run.new_or_changed_ids
    assert "heilmittel-other-v99" in run.out_of_scope_ids
    assert "heilmittel-other-v99" not in run.new_or_changed_ids
    cands = list_candidates(root)
    assert any(c.package_label == "v23" and c.state == "detected" for c in cands)
    assert load_live_binding(root).package_label == before.package_label
    meta = load_check_metadata(root)
    assert meta.get("last_check_status") == "ok"


def test_detect_from_overview_html_fixture(tmp_path: Path):
    root = _gov_root(tmp_path)
    run = run_detection(
        known_manifest=KNOWN,
        overview_html=OVERVIEW_HTML,
        spec_root=root,
    )
    assert run.status == "ok"
    assert "anlage-1-v23" in run.new_or_changed_ids
    assert "anlage-3-v23" in run.new_or_changed_ids
    assert any(i.startswith("oos-") for i in run.out_of_scope_ids)
    assert any(c.package_label == "v23" for c in list_candidates(root))


def test_parse_overview_html_extracts_pubs():
    html = OVERVIEW_HTML.read_text(encoding="utf-8")
    pubs = parse_overview_html(html)
    ids = {p.id for p in pubs}
    assert "anlage-1-v23" in ids
    assert "anlage-3-v23" in ids


def test_failed_html_parse(tmp_path: Path):
    root = _gov_root(tmp_path)
    bad = tmp_path / "empty.html"
    bad.write_text("<html><body>no pdfs here</body></html>", encoding="utf-8")
    run = run_detection(known_manifest=KNOWN, overview_html=bad, spec_root=root)
    assert run.status == "failed"
    assert run.error_message


def test_no_change_creates_no_new_candidate(tmp_path: Path):
    root = _gov_root(tmp_path)
    run1 = run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=root)
    assert run1.new_or_changed_ids
    n = len(list_candidates(root))
    run2 = run_detection(known_manifest=KNOWN, fixture=KNOWN, spec_root=root)
    assert run2.status == "ok"
    assert run2.new_or_changed_ids == []
    assert len(list_candidates(root)) == n


def test_failed_unreachable_source(tmp_path: Path):
    root = _gov_root(tmp_path)
    run = run_detection(
        known_manifest=KNOWN,
        fixture=NEW,
        fail=True,
        fail_message="publication source unreachable",
        spec_root=root,
    )
    assert run.status == "failed"
    assert "unreachable" in (run.error_message or "")
    assert list_candidates(root) == []
    assert load_check_metadata(root).get("last_check_status") == "failed"


def test_dedupe_open_candidate(tmp_path: Path):
    root = _gov_root(tmp_path)
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=root)
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=root)
    v23 = [c for c in list_candidates(root) if c.package_label == "v23"]
    assert len(v23) == 1


def test_redetect_preserves_rejected_audit(tmp_path: Path):
    root = _gov_root(tmp_path)
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=root)
    cand = load_candidate("v23", root)
    assert cand is not None
    cand.state = "rejected"
    cand.approval = ApprovalDecision(
        decision="reject",
        actor="maintainer",
        decided_at="2026-08-17T12:00:00+00:00",
        note="not yet",
    )
    save_candidate(cand, root)

    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=root)
    again = load_candidate("v23", root)
    assert again is not None
    assert again.state == "rejected"
    assert again.approval is not None
    assert again.approval.decision == "reject"
    assert again.approval.actor == "maintainer"
    assert again.approval.note == "not yet"


def test_redetect_preserves_live_and_failed(tmp_path: Path):
    root = _gov_root(tmp_path)
    now = "2026-08-17T12:00:00+00:00"
    save_candidate(
        IntegrationCandidate(
            id="v23",
            package_label="v23",
            branch_name="gkv-edi/spec-v23-integration",
            source_publication_ids=["anlage-1-v23"],
            state="live",
            created_at=now,
            updated_at=now,
            approval=ApprovalDecision(
                decision="approve",
                actor="maintainer",
                decided_at=now,
            ),
        ),
        root,
    )
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=root)
    live = load_candidate("v23", root)
    assert live is not None
    assert live.state == "live"
    assert live.approval is not None
    assert live.approval.decision == "approve"


def test_should_auto_integrate_mode_policy():
    assert should_auto_integrate(scheduled=True) is True
    assert should_auto_integrate(scheduled=True, detect_only=True) is False
    assert should_auto_integrate() is False
    assert should_auto_integrate(auto_integrate=True) is True
    assert should_auto_integrate(auto_integrate=True, detect_only=True) is False
    assert should_auto_integrate(scheduled=True, auto_integrate=True, detect_only=True) is False
