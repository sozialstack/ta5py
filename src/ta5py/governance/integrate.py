"""Scaffold detected format packages on a new git branch."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from gkv_edi.governance.gitops import GitOpsError, create_branch
from gkv_edi.governance.models import IntegrationCandidate
from gkv_edi.governance.store import (
    list_candidates,
    load_candidate,
    load_live_binding,
    load_manifest_documents,
    save_candidate,
    upsert_manifest_documents,
)
from gkv_edi.spec_loader import SPEC_ROOT, load_package_at


class DuplicateCandidateError(ValueError):
    """Raised when an open candidate already exists for the same package identity."""


class IntegrateError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _highest_existing_package(spec_root: Path) -> str:
    versions: list[int] = []
    for path in spec_root.iterdir():
        if path.is_dir() and path.name.startswith("v") and path.name[1:].isdigit():
            versions.append(int(path.name[1:]))
    if not versions:
        binding = load_live_binding(spec_root)
        return binding.package_label if binding else "v21"
    return f"v{max(versions)}"


def _copy_package_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        raise FileExistsError(f"package already exists: {dest}")
    shutil.copytree(src, dest)


def _update_provenance(
    package_dir: Path,
    package_label: str,
    pubs: list[dict[str, Any]],
) -> None:
    prov_path = package_dir / "provenance.yaml"
    if not prov_path.is_file():
        return
    data = yaml.safe_load(prov_path.read_text(encoding="utf-8")) or {}
    data["version_label"] = package_label
    existing = list(data.get("publications") or [])
    prior_by_anlage = {p.get("anlage_id"): p for p in existing if p.get("anlage_id")}
    if pubs:
        publications: list[dict[str, Any]] = []
        updated_ids: set[str] = set()
        for pub in pubs:
            anlage_id = pub.get("bucket")
            prior = prior_by_anlage.get(anlage_id) or {}
            entry: dict[str, Any] = {
                "anlage_id": anlage_id,
                "version": pub.get("version"),
                "stand_date": pub.get("stand_date"),
                "source_url": "https://www.gkv-datenaustausch.de/leistungserbringer/"
                "sonstige_leistungserbringer/sonstige_leistungserbringer.jsp",
                "local_pdf": f"official/{pub.get('bucket')}/{pub.get('filename')}",
            }
            if prior.get("applicable_from"):
                entry["applicable_from"] = prior["applicable_from"]
            prior_stand = prior.get("stand_date")
            if prior_stand and prior_stand != pub.get("stand_date"):
                entry["replaced_stand"] = prior_stand
            elif prior.get("replaced_stand"):
                entry["replaced_stand"] = prior["replaced_stand"]
            publications.append(entry)
            if anlage_id:
                updated_ids.add(str(anlage_id))
        for prior in existing:
            aid = prior.get("anlage_id")
            if aid and str(aid) not in updated_ids:
                publications.append(prior)
        data["publications"] = publications
    notes = data.get("notes") or ""
    prefix = f"Scaffolded integration candidate for {package_label}. "
    data["notes"] = prefix + str(notes)
    prov_path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _publication_deltas(
    *,
    base_label: str,
    new_pubs: list[dict[str, Any]],
    known_docs: list[dict[str, Any]] | None,
) -> list[str]:
    lines: list[str] = []
    known_by_bucket: dict[str, dict[str, Any]] = {}
    if known_docs:
        for doc in known_docs:
            bucket = str(doc.get("bucket"))
            # Prefer matching base package version when possible
            ver = doc.get("version")
            if base_label.startswith("v") and str(ver) == base_label[1:]:
                known_by_bucket[bucket] = doc
            elif bucket not in known_by_bucket:
                known_by_bucket[bucket] = doc

    for pub in new_pubs:
        bucket = str(pub.get("bucket"))
        prev = known_by_bucket.get(bucket)
        if prev is None:
            lines.append(
                f"- **New** `{pub.get('id')}`: `{pub.get('filename')}` "
                f"(stand {pub.get('stand_date')}, version {pub.get('version')})"
            )
            continue
        parts: list[str] = []
        if prev.get("stand_date") != pub.get("stand_date"):
            parts.append(f"stand `{prev.get('stand_date')}` → `{pub.get('stand_date')}`")
        if prev.get("filename") != pub.get("filename"):
            parts.append(f"file `{prev.get('filename')}` → `{pub.get('filename')}`")
        if prev.get("version") != pub.get("version"):
            parts.append(f"version `{prev.get('version')}` → `{pub.get('version')}`")
        if prev.get("path") != pub.get("path"):
            parts.append(f"path changed")
        if parts:
            lines.append(f"- **Changed** `{bucket}`: " + "; ".join(parts))
        else:
            lines.append(f"- `{pub.get('id')}` listed (no field delta vs known `{bucket}`)")
    return lines


def _write_change_summary(
    package_dir: Path,
    *,
    package_label: str,
    base_label: str,
    source_ids: list[str],
    new_pubs: list[dict[str, Any]],
    known_docs: list[dict[str, Any]] | None,
) -> Path:
    path = package_dir / "CHANGE_SUMMARY.md"
    delta_lines = _publication_deltas(
        base_label=base_label, new_pubs=new_pubs, known_docs=known_docs
    )
    lines = [
        f"# Change summary: {package_label}",
        "",
        f"- Base package: `{base_label}`",
        f"- Source publication ids: {', '.join(source_ids) if source_ids else '(none)'}",
        "",
        "## Detected publication deltas",
        "",
    ]
    if delta_lines:
        lines.extend(delta_lines)
    else:
        lines.append("- (no publication metadata available on candidate)")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "This tree is an automated scaffold. Field-level YAML transcription from official",
            "PDFs remains a human review step. Catalog/message/segment field notes should be",
            "updated on this branch after PDF review. Live/default version is **unchanged** until",
            "explicit approve + go-live.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _official_manifest_path(spec_root: Path) -> Path:
    return spec_root / "official" / "sources.manifest.yaml"


def _mark_failed(cand: IntegrationCandidate, root: Path, message: str) -> IntegrationCandidate:
    cand.state = "failed"
    cand.error_message = message
    cand.updated_at = _utc_now()
    save_candidate(cand, root)
    return cand


def integrate_candidate(
    candidate_id: str | None = None,
    *,
    from_latest_new: bool = False,
    base_package: str | None = None,
    dry_run: bool = False,
    create_git_branch: bool = True,
    known_manifest: Path | None = None,
    repo_root: Path | None = None,
    spec_root: Path | None = None,
) -> IntegrationCandidate:
    root = spec_root if spec_root is not None else SPEC_ROOT
    repo = repo_root if repo_root is not None else root.resolve().parents[3]  # packages/gkv-edi/spec -> repo

    cand: IntegrationCandidate | None = None
    if candidate_id:
        cand = load_candidate(candidate_id, root)
    elif from_latest_new:
        detected = [c for c in list_candidates(root) if c.state == "detected"]
        if not detected:
            raise ValueError("no detected candidates available")
        cand = sorted(detected, key=lambda c: c.created_at)[-1]
    else:
        raise ValueError("candidate id or --from-latest-new required")

    if cand is None:
        raise ValueError(f"candidate not found: {candidate_id}")

    if cand.state in {"rejected", "live"}:
        raise IntegrateError(
            f"candidate {cand.id} is terminal ({cand.state}); will not re-integrate"
        )

    open_others = [
        c
        for c in list_candidates(root)
        if c.package_label == cand.package_label
        and c.id != cand.id
        and c.state in {"detected", "integrating", "awaiting_approval", "live"}
    ]
    if open_others:
        raise DuplicateCandidateError(
            f"duplicate open candidate for {cand.package_label}: {open_others[0].id}"
        )

    dest_dir = root / cand.package_label
    if dest_dir.exists() and cand.state == "detected":
        raise DuplicateCandidateError(
            f"duplicate open candidate for {cand.package_label}: package dir exists"
        )

    base_label = base_package
    if not base_label:
        binding = load_live_binding(root)
        base_label = binding.package_label if binding else _highest_existing_package(root)
    assert isinstance(base_label, str)

    base_dir = root / base_label
    if not base_dir.is_dir():
        raise FileNotFoundError(f"base package missing: {base_dir}")

    if dry_run:
        cand.state = "detected"
        cand.updated_at = _utc_now()
        return cand

    now = _utc_now()
    cand.state = "integrating"
    cand.updated_at = now
    save_candidate(cand, root)

    try:
        if create_git_branch:
            create_branch(cand.branch_name, repo_root=repo, dry_run=False)
        if dest_dir.exists():
            raise FileExistsError(f"target package exists: {dest_dir}")
        _copy_package_tree(base_dir, dest_dir)

        pubs = list(cand.source_publications or [])
        _update_provenance(dest_dir, cand.package_label, pubs)

        known_docs: list[dict[str, Any]] | None = None
        manifest = known_manifest or _official_manifest_path(root)
        if pubs:
            if manifest.is_file():
                known_docs = load_manifest_documents(manifest)
            else:
                known_docs = []
                manifest.parent.mkdir(parents=True, exist_ok=True)
                manifest.write_text(
                    yaml.safe_dump(
                        {
                            "base_url": "https://www.gkv-datenaustausch.de",
                            "overview_url": (
                                "https://www.gkv-datenaustausch.de/leistungserbringer/"
                                "sonstige_leistungserbringer/sonstige_leistungserbringer.jsp"
                            ),
                            "documents": [],
                        },
                        sort_keys=False,
                        allow_unicode=True,
                    ),
                    encoding="utf-8",
                )
            upsert_manifest_documents(manifest, pubs)
        elif manifest.is_file():
            known_docs = load_manifest_documents(manifest)

        summary = _write_change_summary(
            dest_dir,
            package_label=cand.package_label,
            base_label=base_label,
            source_ids=cand.source_publication_ids,
            new_pubs=pubs,
            known_docs=known_docs,
        )
        cand.change_summary_path = str(summary.relative_to(root))

        # Structural package validation — incomplete/corrupt → failed (FR-010 / SC-006)
        try:
            load_package_at(dest_dir, version_label=cand.package_label)
        except (OSError, ValueError, FileNotFoundError, KeyError, TypeError) as exc:
            _mark_failed(cand, root, f"incomplete or corrupt package material: {exc}")
            raise IntegrateError(cand.error_message or str(exc)) from exc

        cand.state = "awaiting_approval"
        cand.error_message = None
        cand.updated_at = _utc_now()
        save_candidate(cand, root)
        return cand
    except DuplicateCandidateError:
        raise
    except IntegrateError:
        raise
    except (GitOpsError, OSError, FileExistsError) as exc:
        _mark_failed(cand, root, str(exc))
        raise
