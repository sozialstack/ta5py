"""Human approval gate and go-live for format package candidates."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from ta5py.governance.integrate import _candidate_in_scope
from ta5py.governance.models import ApprovalDecision, IntegrationCandidate, LiveVersionBinding
from ta5py.governance.store import load_candidate, load_live_binding, save_candidate, save_live_binding
from ta5py.spec_loader import SPEC_ROOT, load_package, load_package_at, refresh_default_version

_LABEL_RE = re.compile(r"^v(\d+)$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class ApprovalError(RuntimeError):
    pass


def package_label_number(label: str) -> int | None:
    match = _LABEL_RE.match(label.strip())
    return int(match.group(1)) if match else None


def older_over_newer_warning(candidate_label: str, live_label: str) -> str | None:
    cand_n = package_label_number(candidate_label)
    live_n = package_label_number(live_label)
    if cand_n is None or live_n is None:
        return None
    if cand_n < live_n:
        return (
            f"activating older package {candidate_label} over newer live {live_label}; "
            "explicit confirmation required"
        )
    return None


def approve_candidate(
    candidate_id: str,
    *,
    actor: str,
    decision: str,
    note: str | None = None,
    spec_root: Path | None = None,
) -> IntegrationCandidate:
    if not actor or not str(actor).strip():
        raise ApprovalError("actor is required")
    if decision not in {"approve", "reject"}:
        raise ApprovalError("decision must be approve or reject")

    root = spec_root if spec_root is not None else SPEC_ROOT
    cand = load_candidate(candidate_id, root)
    if cand is None:
        raise ApprovalError(f"candidate not found: {candidate_id}")

    now = _utc_now()
    cand.approval = ApprovalDecision(
        decision=decision,  # type: ignore[arg-type]
        actor=actor.strip(),
        decided_at=now,
        note=note,
    )
    if decision == "reject":
        cand.state = "rejected"
    elif cand.state != "failed":
        cand.state = "awaiting_approval"
    cand.updated_at = now
    save_candidate(cand, root)
    return cand


def go_live(
    candidate_id: str,
    *,
    actor: str,
    spec_root: Path | None = None,
    require_approval: bool = True,
    confirm_older: bool = False,
) -> LiveVersionBinding:
    """Activate live binding. Requires prior approve decision when require_approval=True."""
    root = spec_root if spec_root is not None else SPEC_ROOT
    cand = load_candidate(candidate_id, root)
    if cand is None:
        raise ApprovalError(f"candidate not found: {candidate_id}")

    if cand.state == "failed":
        raise ApprovalError(
            f"go-live rejected: candidate is failed ({cand.error_message or 'no detail'})"
        )

    if not _candidate_in_scope(cand):
        raise ApprovalError(
            f"go-live rejected: candidate {cand.id} is out of ambulance product scope"
        )

    if require_approval:
        if cand.approval is None or cand.approval.decision != "approve":
            raise ApprovalError(
                "go-live rejected: missing human approval for this candidate"
            )

    previous = load_live_binding(root)
    if previous is not None:
        warning = older_over_newer_warning(cand.package_label, previous.package_label)
        if warning and not confirm_older:
            raise ApprovalError(warning)

    pkg_dir = root / cand.package_label
    if not pkg_dir.is_dir():
        cand.state = "failed"
        cand.error_message = f"package directory missing: {pkg_dir}"
        cand.updated_at = _utc_now()
        save_candidate(cand, root)
        raise ApprovalError(f"package not ready for go-live: {pkg_dir}")

    # FR-010 / T037: validate package loads before writing live-version.yaml
    try:
        if root.resolve() == SPEC_ROOT.resolve():
            load_package(cand.package_label)
        else:
            load_package_at(pkg_dir, version_label=cand.package_label)
    except (OSError, ValueError, FileNotFoundError, KeyError, TypeError) as exc:
        cand.state = "failed"
        cand.error_message = f"incomplete or corrupt package material: {exc}"
        cand.updated_at = _utc_now()
        save_candidate(cand, root)
        raise ApprovalError(cand.error_message) from exc

    now = _utc_now()
    note = f"go-live for candidate {cand.id}"
    if previous is not None:
        warning = older_over_newer_warning(cand.package_label, previous.package_label)
        if warning:
            note = f"{note}; WARNING: {warning}"

    binding = LiveVersionBinding(
        package_label=cand.package_label,
        activated_at=now,
        activated_by=actor,
        approval_ref=f"{cand.id}:{cand.approval.decided_at if cand.approval else now}",
        previous_package_label=previous.package_label if previous else None,
        note=note,
    )
    save_live_binding(binding, root)

    cand.state = "live"
    cand.updated_at = now
    save_candidate(cand, root)

    if root.resolve() == SPEC_ROOT.resolve():
        refresh_default_version()
    return binding
