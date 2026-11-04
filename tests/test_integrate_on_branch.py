from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from ta5py.governance.detect import run_detection
from ta5py.governance.integrate import DuplicateCandidateError, integrate_candidate
from ta5py.governance.models import LiveVersionBinding
from ta5py.governance.store import list_candidates, load_live_binding, save_live_binding
from ta5py.spec_loader import SPEC_ROOT

FIXTURES = Path(__file__).parent / "fixtures" / "governance"
KNOWN = FIXTURES / "sources_known.yaml"
NEW = FIXTURES / "sources_with_new_version.yaml"


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=path, check=True)
    (path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True)


def _spec_with_v21(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    spec = repo / "modules" / "format" / "spec"
    spec.mkdir(parents=True)
    shutil.copytree(SPEC_ROOT / "v21", spec / "v21")
    official = spec / "official"
    official.mkdir(parents=True)
    shutil.copy(KNOWN, official / "sources.manifest.yaml")
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
    return repo, spec


def test_integrate_creates_branch_and_scaffold(tmp_path: Path):
    repo, spec = _spec_with_v21(tmp_path)
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=spec)
    live_before = load_live_binding(spec).package_label

    cand = integrate_candidate(
        from_latest_new=True,
        create_git_branch=True,
        repo_root=repo,
        spec_root=spec,
        base_package="v21",
        known_manifest=spec / "official" / "sources.manifest.yaml",
    )
    assert cand.state == "awaiting_approval"
    assert (spec / "v23" / "provenance.yaml").is_file()
    summary = (spec / "v23" / "CHANGE_SUMMARY.md").read_text(encoding="utf-8")
    assert "Detected publication deltas" in summary
    assert "stand" in summary.lower() or "New" in summary or "Changed" in summary
    manifest = yaml.safe_load(
        (spec / "official" / "sources.manifest.yaml").read_text(encoding="utf-8")
    )
    ids = {d["id"] for d in manifest["documents"]}
    assert "anlage-1-v23" in ids
    assert "anlage-3-v23" in ids
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert branch == "ta5py/spec-v23-integration"
    assert load_live_binding(spec).package_label == live_before
    prov = yaml.safe_load((spec / "v23" / "provenance.yaml").read_text(encoding="utf-8"))
    by_id = {p["anlage_id"]: p for p in prov["publications"]}
    v21_prov = yaml.safe_load((spec / "v21" / "provenance.yaml").read_text(encoding="utf-8"))
    v21_by_id = {p["anlage_id"]: p for p in v21_prov["publications"]}
    assert by_id["anlage-1"]["replaced_stand"] == v21_by_id["anlage-1"]["stand_date"]
    assert by_id["anlage-3"]["replaced_stand"] == v21_by_id["anlage-3"]["stand_date"]


def test_integrate_dry_run_no_package(tmp_path: Path):
    repo, spec = _spec_with_v21(tmp_path)
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=spec)
    cand = integrate_candidate(
        from_latest_new=True,
        dry_run=True,
        create_git_branch=False,
        repo_root=repo,
        spec_root=spec,
    )
    assert cand.state == "detected"
    assert not (spec / "v23").exists()


def test_duplicate_integrate_refuses_second_open(tmp_path: Path):
    repo, spec = _spec_with_v21(tmp_path)
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=spec)
    integrate_candidate(
        from_latest_new=True,
        create_git_branch=True,
        repo_root=repo,
        spec_root=spec,
        base_package="v21",
        known_manifest=spec / "official" / "sources.manifest.yaml",
    )
    from datetime import datetime, timezone

    from ta5py.governance.models import IntegrationCandidate
    from ta5py.governance.store import save_candidate

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    dup = IntegrationCandidate(
        id="v23-dup",
        package_label="v23",
        branch_name="ta5py/spec-v23-dup-integration",
        source_publication_ids=["anlage-1-v23"],
        state="detected",
        created_at=now,
        updated_at=now,
    )
    save_candidate(dup, spec)
    with pytest.raises(DuplicateCandidateError, match="duplicate"):
        integrate_candidate(
            "v23-dup",
            create_git_branch=False,
            repo_root=repo,
            spec_root=spec,
            base_package="v21",
        )
    assert len([c for c in list_candidates(spec) if c.state == "awaiting_approval"]) == 1


def test_corrupt_package_marks_failed(tmp_path: Path):
    repo, spec = _spec_with_v21(tmp_path)
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=spec)
    # Break base package so scaffolded copy fails validation
    (spec / "v21" / "una.yaml").unlink()
    with pytest.raises(Exception):
        integrate_candidate(
            from_latest_new=True,
            create_git_branch=False,
            repo_root=repo,
            spec_root=spec,
            base_package="v21",
            known_manifest=spec / "official" / "sources.manifest.yaml",
        )
    failed = [c for c in list_candidates(spec) if c.package_label == "v23"]
    assert failed and failed[0].state == "failed"
    assert failed[0].error_message


def test_integrate_refuses_out_of_scope(tmp_path: Path):
    from datetime import datetime, timezone

    from ta5py.governance.integrate import IntegrateError
    from ta5py.governance.models import IntegrationCandidate
    from ta5py.governance.store import save_candidate

    repo, spec = _spec_with_v21(tmp_path)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    cand = IntegrationCandidate(
        id="oos-hand-seed",
        package_label="v99",
        branch_name="ta5py/spec-v99-integration",
        source_publication_ids=["heilmittel-other-v99"],
        state="detected",
        created_at=now,
        updated_at=now,
        source_publications=[{"id": "heilmittel-other-v99", "bucket": "heilmittel"}],
    )
    save_candidate(cand, spec)
    with pytest.raises(IntegrateError, match="out of ambulance"):
        integrate_candidate(
            "oos-hand-seed",
            create_git_branch=False,
            repo_root=repo,
            spec_root=spec,
            base_package="v21",
        )


def test_remote_integration_branch_is_not_recreated(tmp_path: Path):
    repo, spec = _spec_with_v21(tmp_path)
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", str(origin)], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "branch", "ta5py/spec-v23-integration"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "push", "-u", "origin", "ta5py/spec-v23-integration"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "branch", "-D", "ta5py/spec-v23-integration"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    run_detection(known_manifest=KNOWN, fixture=NEW, spec_root=spec)
    with pytest.raises(DuplicateCandidateError, match="branch ta5py/spec-v23-integration exists"):
        integrate_candidate(
            from_latest_new=True,
            create_git_branch=True,
            repo_root=repo,
            spec_root=spec,
            base_package="v21",
            known_manifest=spec / "official" / "sources.manifest.yaml",
        )
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert branch == "main"
    assert not (spec / "v23").exists()


def test_detected_candidates_land_on_separate_branches(tmp_path: Path):
    from datetime import datetime, timezone

    from ta5py.governance.integrate import integrate_detected_candidates
    from ta5py.governance.models import IntegrationCandidate
    from ta5py.governance.store import save_candidate

    repo, spec = _spec_with_v21(tmp_path)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "spec"], cwd=repo, check=True, capture_output=True)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for label in ("v22", "v23"):
        save_candidate(
            IntegrationCandidate(
                id=label,
                package_label=label,
                branch_name=f"ta5py/spec-{label}-integration",
                source_publication_ids=[],
                state="detected",
                created_at=now,
                updated_at=now,
            ),
            spec,
        )
    integrated, skips = integrate_detected_candidates(
        repo_root=repo,
        spec_root=spec,
        known_manifest=spec / "official" / "sources.manifest.yaml",
        create_git_branch=True,
        push=False,
    )
    assert skips == []
    assert [c.package_label for c in integrated] == ["v22", "v23"]

    def tracked(branch: str) -> str:
        proc = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", branch],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
        return proc.stdout.replace("\\", "/")

    v22_tree = tracked("ta5py/spec-v22-integration")
    v23_tree = tracked("ta5py/spec-v23-integration")
    assert "spec/v22/provenance.yaml" in v22_tree
    assert "spec/v23/" not in v22_tree
    assert "spec/v23/provenance.yaml" in v23_tree
    assert "spec/v22/" not in v23_tree
    current = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert current == "master" or current == "main"


def test_persist_leaves_remote_ahead_branch_unchanged(tmp_path: Path):
    from ta5py.governance.gitops import RemoteAheadError, persist_integration_branch

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", str(origin)], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=repo, check=True, capture_output=True)
    spec = repo / "src" / "ta5py" / "spec"
    spec.mkdir(parents=True)
    (spec / "base.txt").write_text("base", encoding="utf-8")
    subprocess.run(["git", "add", "src"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "base spec"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "ta5py/spec-v9-integration"], cwd=repo, check=True, capture_output=True)
    (spec / "remote.txt").write_text("remote", encoding="utf-8")
    subprocess.run(["git", "add", "src"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "remote scaffold"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "push", "-u", "origin", "ta5py/spec-v9-integration"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    remote_sha = subprocess.run(
        ["git", "rev-parse", "ta5py/spec-v9-integration"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(["git", "checkout", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "branch", "-D", "ta5py/spec-v9-integration"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "ta5py/spec-v9-integration"], cwd=repo, check=True, capture_output=True)
    (spec / "local.txt").write_text("local", encoding="utf-8")
    with pytest.raises(RemoteAheadError, match="left the remote unchanged"):
        persist_integration_branch(repo, push=True, spec_relpath="src/ta5py/spec")
    subprocess.run(["git", "fetch", "origin", "ta5py/spec-v9-integration"], cwd=repo, check=True, capture_output=True)
    remote_after = subprocess.run(
        ["git", "rev-parse", "FETCH_HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert remote_after == remote_sha


def test_default_repo_root_is_package_checkout():
    from ta5py.governance.gitops import sozialstack_root

    root = sozialstack_root(SPEC_ROOT)
    assert (root / "src" / "ta5py").is_dir()
    assert (root / "pyproject.toml").is_file()
    assert root == SPEC_ROOT.resolve().parents[2]
