from __future__ import annotations

import subprocess
from pathlib import Path


class GitOpsError(RuntimeError):
    pass


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
