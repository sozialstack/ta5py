"""Detect new/changed official GKV format publications."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from gkv_edi.governance.discover import (
    fetch_overview,
    load_overview_html,
    parse_overview_html,
    publications_to_docs,
)
from gkv_edi.governance.models import DetectionRun, IntegrationCandidate, OfficialPublication
from gkv_edi.governance.scope import is_in_scope_bucket
from gkv_edi.governance.store import (
    find_candidate_for_package,
    find_open_candidate_for_package,
    load_manifest,
    load_manifest_documents,
    save_candidate,
    save_check_metadata,
    save_detection_run,
    update_manifest_check_metadata,
)
from gkv_edi.spec_loader import SPEC_ROOT

TERMINAL_CANDIDATE_STATES = frozenset({"rejected", "live", "failed"})


def should_auto_integrate(
    *,
    scheduled: bool = False,
    detect_only: bool = False,
    auto_integrate: bool = False,
) -> bool:
    """Scheduled/periodic detection auto-integrates; on-demand stays detect-only unless opted in.

    Live binding is never flipped here — integrate only scaffolds a branch.
    """
    if detect_only:
        return False
    if scheduled:
        return True
    return auto_integrate


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _package_label_for_version(version: int | str) -> str:
    text = str(version)
    return text if text.startswith("v") else f"v{text}"


def publications_from_docs(docs: list[dict[str, Any]]) -> list[OfficialPublication]:
    out: list[OfficialPublication] = []
    for doc in docs:
        bucket = str(doc["bucket"])
        out.append(OfficialPublication.from_dict(doc, in_scope=is_in_scope_bucket(bucket)))
    return out


def compare_publications(
    known: list[OfficialPublication], discovered: list[OfficialPublication]
) -> tuple[list[str], list[str], list[str]]:
    known_by_id = {p.id: p for p in known}
    found_ids: list[str] = []
    new_or_changed: list[str] = []
    out_of_scope: list[str] = []

    for pub in discovered:
        found_ids.append(pub.id)
        if not pub.in_scope:
            out_of_scope.append(pub.id)
            continue
        prev = known_by_id.get(pub.id)
        if prev is None:
            new_or_changed.append(pub.id)
            continue
        if (
            prev.version != pub.version
            or prev.stand_date != pub.stand_date
            or prev.filename != pub.filename
            or prev.path != pub.path
        ):
            new_or_changed.append(pub.id)
    return found_ids, new_or_changed, out_of_scope


def _ensure_detected_candidate(
    package_label: str,
    pubs: list[OfficialPublication],
    spec_root: Path,
) -> IntegrationCandidate:
    """Create or link a candidate. Never overwrite rejected/live/failed audit records."""
    existing_open = find_open_candidate_for_package(package_label, spec_root)
    if existing_open is not None:
        return existing_open

    prior = find_candidate_for_package(package_label, spec_root)
    if prior is not None:
        # Terminal or same-id record: preserve approval/rejection history (FR-008 / FR-011)
        return prior

    now = _utc_now()
    cand = IntegrationCandidate(
        id=package_label,
        package_label=package_label,
        branch_name=f"gkv-edi/spec-{package_label}-integration",
        source_publication_ids=[p.id for p in pubs],
        state="detected",
        created_at=now,
        updated_at=now,
        source_publications=publications_to_docs(pubs),
    )
    save_candidate(cand, spec_root)
    return cand


def _resolve_discovered(
    *,
    known_manifest: Path,
    discovered_manifest: Path | None,
    fixture: Path | None,
    overview_html: Path | None,
    allow_network: bool,
) -> tuple[list[OfficialPublication], dict[str, str | None], str]:
    """
    Return (discovered pubs, fetch metadata, source_kind).
    source_kind is 'manifest' | 'html' | 'network'.
    """
    meta: dict[str, str | None] = {
        "etag": None,
        "last_modified": None,
        "content_length": None,
    }

    disc_path = fixture or discovered_manifest or overview_html
    if disc_path is not None:
        suffix = disc_path.suffix.lower()
        if suffix in {".html", ".htm"}:
            html = load_overview_html(disc_path)
            return parse_overview_html(html), meta, "html"
        if suffix in {".yaml", ".yml"}:
            docs = load_manifest_documents(disc_path)
            return publications_from_docs(docs), meta, "manifest"
        # Peek content: HTML vs YAML
        text = disc_path.read_text(encoding="utf-8", errors="replace")
        if "<html" in text.lower() or "<!doctype" in text.lower():
            return parse_overview_html(text), meta, "html"
        docs = load_manifest_documents(disc_path)
        return publications_from_docs(docs), meta, "manifest"

    if not allow_network:
        raise ValueError(
            "discovered_manifest, fixture, or overview_html is required when network is disabled"
        )

    known = load_manifest(known_manifest)
    overview_url = known.get("overview_url")
    if not overview_url:
        raise ValueError(f"known manifest missing overview_url: {known_manifest}")
    body, meta = fetch_overview(str(overview_url))
    return parse_overview_html(body), meta, "network"


def _create_candidates_for_new(
    new_pubs: list[OfficialPublication],
    root: Path,
) -> list[IntegrationCandidate]:
    created: list[IntegrationCandidate] = []
    anlage1_new = [p for p in new_pubs if p.bucket == "anlage-1"]
    handled: set[str] = set()
    for a1 in anlage1_new:
        label = _package_label_for_version(a1.version)
        related = [
            p
            for p in new_pubs
            if _package_label_for_version(p.version) == label
            and p.bucket in {"anlage-1", "anlage-3"}
        ]
        created.append(_ensure_detected_candidate(label, related or [a1], root))
        handled.add(label)

    for pub in new_pubs:
        label = _package_label_for_version(pub.version)
        if pub.bucket in {"anlage-1", "anlage-3"} and label in handled:
            continue
        if pub.bucket in {"anlage-5", "anhang-3"}:
            if label not in handled:
                created.append(_ensure_detected_candidate(label, [pub], root))
                handled.add(label)
        elif pub.bucket == "anlage-3" and label not in handled:
            created.append(_ensure_detected_candidate(label, [pub], root))
            handled.add(label)
    return created


def run_detection(
    *,
    known_manifest: Path,
    discovered_manifest: Path | None = None,
    fixture: Path | None = None,
    overview_html: Path | None = None,
    allow_network: bool = False,
    update_manifest_metadata: bool = False,
    spec_root: Path | None = None,
    fail: bool = False,
    fail_message: str = "publication source unreachable",
) -> DetectionRun:
    """Compare known vs discovered publications (manifest, HTML snapshot, or network)."""
    root = spec_root if spec_root is not None else SPEC_ROOT
    started = _utc_now()
    run_id = started.replace(":", "").replace("+", "p")
    fetch_meta: dict[str, str | None] = {
        "etag": None,
        "last_modified": None,
        "content_length": None,
    }

    def _persist_check_meta(status: str, error: str | None = None) -> None:
        meta = {
            "last_check_at": _utc_now(),
            "last_check_status": status,
            "etag": fetch_meta.get("etag"),
            "last_modified": fetch_meta.get("last_modified"),
            "content_length": fetch_meta.get("content_length"),
            "error_message": error,
        }
        save_check_metadata(meta, root)
        if update_manifest_metadata and known_manifest.is_file():
            try:
                update_manifest_check_metadata(
                    known_manifest,
                    last_check_at=meta["last_check_at"],  # type: ignore[arg-type]
                    last_check_status=status,
                    etag=fetch_meta.get("etag"),
                    last_modified=fetch_meta.get("last_modified"),
                    error_message=error,
                )
            except OSError:
                pass

    if fail:
        run = DetectionRun(
            id=run_id,
            started_at=started,
            finished_at=_utc_now(),
            status="failed",
            error_message=fail_message,
        )
        save_detection_run(run, root)
        _persist_check_meta("failed", fail_message)
        return run

    try:
        known_docs = load_manifest_documents(known_manifest)
        known = publications_from_docs(known_docs)
        discovered, fetch_meta, _kind = _resolve_discovered(
            known_manifest=known_manifest,
            discovered_manifest=discovered_manifest,
            fixture=fixture,
            overview_html=overview_html,
            allow_network=allow_network,
        )
        found_ids, new_ids, oos_ids = compare_publications(known, discovered)

        status: str = "ok"
        error_message = None
        in_scope_found = [p for p in discovered if p.in_scope]
        if not found_ids:
            status = "failed"
            error_message = "discovery returned zero publications"
        elif not in_scope_found:
            status = "partial"
            error_message = "discovery found publications but none in ambulance product scope"

        run = DetectionRun(
            id=run_id,
            started_at=started,
            finished_at=_utc_now(),
            status=status,  # type: ignore[arg-type]
            error_message=error_message,
            found_publication_ids=found_ids,
            new_or_changed_ids=new_ids,
            out_of_scope_ids=oos_ids,
        )
        save_detection_run(run, root)
        _persist_check_meta(status, error_message)

        if status != "failed":
            new_pubs = [p for p in discovered if p.id in new_ids and p.in_scope]
            _create_candidates_for_new(new_pubs, root)

        return run
    except Exception as exc:  # noqa: BLE001 — surface as failed detection
        run = DetectionRun(
            id=run_id,
            started_at=started,
            finished_at=_utc_now(),
            status="failed",
            error_message=str(exc),
        )
        save_detection_run(run, root)
        _persist_check_meta("failed", str(exc))
        return run


def write_discovered_manifest(path: Path, pubs: list[OfficialPublication], *, base_url: str = "") -> None:
    """Helper for tests/CI to materialize a discovered catalog YAML."""
    data = {
        "base_url": base_url or "https://www.gkv-datenaustausch.de",
        "documents": publications_to_docs(pubs),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
