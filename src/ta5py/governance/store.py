from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from gkv_edi.governance.models import DetectionRun, IntegrationCandidate, LiveVersionBinding
from gkv_edi.spec_loader import SPEC_ROOT

OPEN_CANDIDATE_STATES = frozenset(
    {"detected", "integrating", "awaiting_approval"}
)


def governance_root(spec_root: Path | None = None) -> Path:
    root = spec_root if spec_root is not None else SPEC_ROOT
    return root / "governance"


def live_version_path(spec_root: Path | None = None) -> Path:
    return governance_root(spec_root) / "live-version.yaml"


def detections_dir(spec_root: Path | None = None) -> Path:
    return governance_root(spec_root) / "detections"


def candidates_dir(spec_root: Path | None = None) -> Path:
    return governance_root(spec_root) / "candidates"


def ensure_governance_dirs(spec_root: Path | None = None) -> None:
    detections_dir(spec_root).mkdir(parents=True, exist_ok=True)
    candidates_dir(spec_root).mkdir(parents=True, exist_ok=True)


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_live_binding(spec_root: Path | None = None) -> LiveVersionBinding | None:
    path = live_version_path(spec_root)
    if not path.is_file():
        return None
    return LiveVersionBinding.from_dict(_read_yaml(path))


def save_live_binding(binding: LiveVersionBinding, spec_root: Path | None = None) -> None:
    _write_yaml(live_version_path(spec_root), binding.to_dict())


def save_detection_run(run: DetectionRun, spec_root: Path | None = None) -> Path:
    ensure_governance_dirs(spec_root)
    path = detections_dir(spec_root) / f"{run.id}.yaml"
    _write_yaml(path, run.to_dict())
    return path


def list_detection_runs(spec_root: Path | None = None) -> list[DetectionRun]:
    d = detections_dir(spec_root)
    if not d.is_dir():
        return []
    runs: list[DetectionRun] = []
    for path in sorted(d.glob("*.yaml")):
        runs.append(DetectionRun.from_dict(_read_yaml(path)))
    return runs


def latest_detection_run(spec_root: Path | None = None) -> DetectionRun | None:
    runs = list_detection_runs(spec_root)
    return runs[-1] if runs else None


def candidate_path(candidate_id: str, spec_root: Path | None = None) -> Path:
    safe = candidate_id.replace(":", "_").replace("/", "_")
    return candidates_dir(spec_root) / f"{safe}.yaml"


def load_candidate(candidate_id: str, spec_root: Path | None = None) -> IntegrationCandidate | None:
    path = candidate_path(candidate_id, spec_root)
    if not path.is_file():
        return None
    return IntegrationCandidate.from_dict(_read_yaml(path))


def save_candidate(candidate: IntegrationCandidate, spec_root: Path | None = None) -> Path:
    ensure_governance_dirs(spec_root)
    path = candidate_path(candidate.id, spec_root)
    _write_yaml(path, candidate.to_dict())
    return path


def list_candidates(spec_root: Path | None = None) -> list[IntegrationCandidate]:
    d = candidates_dir(spec_root)
    if not d.is_dir():
        return []
    out: list[IntegrationCandidate] = []
    for path in sorted(d.glob("*.yaml")):
        out.append(IntegrationCandidate.from_dict(_read_yaml(path)))
    return out


def find_open_candidate_for_package(
    package_label: str, spec_root: Path | None = None
) -> IntegrationCandidate | None:
    for c in list_candidates(spec_root):
        if c.package_label == package_label and c.state in OPEN_CANDIDATE_STATES:
            return c
    return None


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "documents" not in data:
        raise ValueError(f"Invalid sources manifest: {manifest_path}")
    docs = data["documents"]
    if not isinstance(docs, list):
        raise ValueError(f"documents must be a list in {manifest_path}")
    return data


def load_manifest_documents(manifest_path: Path) -> list[dict[str, Any]]:
    return list(load_manifest(manifest_path)["documents"])


def check_metadata_path(spec_root: Path | None = None) -> Path:
    return governance_root(spec_root) / "check-metadata.yaml"


def load_check_metadata(spec_root: Path | None = None) -> dict[str, Any]:
    path = check_metadata_path(spec_root)
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def save_check_metadata(meta: dict[str, Any], spec_root: Path | None = None) -> Path:
    ensure_governance_dirs(spec_root)
    path = check_metadata_path(spec_root)
    _write_yaml(path, meta)
    return path


def update_manifest_check_metadata(
    manifest_path: Path,
    *,
    last_check_at: str,
    last_check_status: str,
    etag: str | None = None,
    last_modified: str | None = None,
    error_message: str | None = None,
) -> None:
    """Extend sources.manifest.yaml with last-check / ETag metadata (in-place)."""
    data = load_manifest(manifest_path)
    check = dict(data.get("check_metadata") or {})
    check["last_check_at"] = last_check_at
    check["last_check_status"] = last_check_status
    if etag is not None:
        check["etag"] = etag
    if last_modified is not None:
        check["last_modified"] = last_modified
    if error_message is not None:
        check["error_message"] = error_message
    elif "error_message" in check and last_check_status == "ok":
        check.pop("error_message", None)
    data["check_metadata"] = check
    _write_yaml(manifest_path, data)


def upsert_manifest_documents(
    manifest_path: Path,
    publications: list[dict[str, Any]],
) -> list[str]:
    """Append or replace document entries by id. Returns list of upserted ids."""
    data = load_manifest(manifest_path)
    docs: list[dict[str, Any]] = list(data["documents"])
    by_id = {str(d["id"]): i for i, d in enumerate(docs)}
    upserted: list[str] = []
    for pub in publications:
        pid = str(pub["id"])
        entry = {
            "id": pid,
            "bucket": pub["bucket"],
            "filename": pub["filename"],
            "path": pub["path"],
            "version": pub["version"],
            "stand_date": pub.get("stand_date"),
        }
        if pid in by_id:
            docs[by_id[pid]] = entry
        else:
            docs.append(entry)
            by_id[pid] = len(docs) - 1
        upserted.append(pid)
    data["documents"] = docs
    _write_yaml(manifest_path, data)
    return upserted


def find_candidate_for_package(
    package_label: str, spec_root: Path | None = None
) -> IntegrationCandidate | None:
    """Return any candidate for package_label (open preferred, else first match)."""
    open_hit = find_open_candidate_for_package(package_label, spec_root)
    if open_hit is not None:
        return open_hit
    for c in list_candidates(spec_root):
        if c.package_label == package_label:
            return c
    return None
