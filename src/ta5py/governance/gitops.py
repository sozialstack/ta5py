from __future__ import annotations

import subprocess
from pathlib import Path


class GitOpsError(RuntimeError):
    pass


def sozialstack_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` (or this file) to the sozialstack workspace root."""
    here = (start or Path(__file__)).resolve()
    for path in [here, *here.parents]:
        if (path / "packages" / "ta5py").is_dir() and (path / "pyproject.toml").is_file():
            return path
    raise FileNotFoundError("sozialstack repository root not found")


def run_git(args: list[str], *, cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise GitOpsError(proc.stderr.strip() or proc.stdout.strip() or f"git {args} failed")
    return proc.stdout.strip()


def create_branch(branch_name: str, *, repo_root: Path, dry_run: bool = False) -> str:
    if dry_run:
        return branch_name
    # create from current HEAD without switching if possible; checkout for scaffold writes
    try:
        run_git(["rev-parse", "--verify", branch_name], cwd=repo_root)
        raise GitOpsError(f"branch already exists: {branch_name}")
    except GitOpsError as exc:
        if "already exists" in str(exc):
            raise
        # rev-parse failed => branch missing, OK
    run_git(["checkout", "-b", branch_name], cwd=repo_root)
    return branch_name


def current_branch(repo_root: Path) -> str:
    return run_git(["branch", "--show-current"], cwd=repo_root)


def persist_integration_branch(
    repo_root: Path,
    *,
    message: str = "chore(ta5py): scaffold official spec integration",
    push: bool = False,
    remote: str = "origin",
) -> str | None:
    """Commit scaffolded spec files on the current branch; optionally push.

    Scheduled CI uses ``push=True`` so the integration branch is not discarded
    when the workflow workspace is deleted. Maintainers without push credentials
    can run the same detect/integrate command on a long-lived host.
    """
    status = run_git(["status", "--porcelain", "--", "packages/ta5py/spec"], cwd=repo_root)
    if not status:
        return None
    run_git(["add", "--", "packages/ta5py/spec"], cwd=repo_root)
    run_git(["commit", "-m", message], cwd=repo_root)
    branch = current_branch(repo_root)
    if push:
        run_git(["push", "-u", remote, branch], cwd=repo_root)
    return branch
