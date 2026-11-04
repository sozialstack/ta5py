from __future__ import annotations

import subprocess
from pathlib import Path


class GitOpsError(RuntimeError):
    pass


class RemoteAheadError(GitOpsError):
    """Push rejected because the remote branch contains commits not present locally."""


def sozialstack_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` (or this file) to the ta5py repository root."""
    here = (start or Path(__file__)).resolve()
    for path in [here, *here.parents]:
        if (path / "src" / "ta5py").is_dir() and (path / "pyproject.toml").is_file():
            return path
    raise FileNotFoundError("ta5py repository root not found")


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


def local_branch_exists(branch_name: str, *, repo_root: Path) -> bool:
    try:
        run_git(["rev-parse", "--verify", branch_name], cwd=repo_root)
    except GitOpsError:
        return False
    return True


def remote_branch_exists(branch_name: str, *, repo_root: Path, remote: str = "origin") -> bool:
    """True when ``remote`` already has ``branch_name``. Missing remotes count as absent."""
    proc = subprocess.run(
        ["git", "ls-remote", "--heads", remote, f"refs/heads/{branch_name}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        lowered = err.lower()
        if (
            "does not appear to be a git repository" in lowered
            or "no such remote" in lowered
            or "does not appear to be a git repo" in lowered
        ):
            return False
        raise GitOpsError(err or f"git ls-remote {remote} {branch_name} failed")
    return bool(proc.stdout.strip())


def create_branch(branch_name: str, *, repo_root: Path, dry_run: bool = False) -> str:
    if dry_run:
        return branch_name
    # create from current HEAD without switching if possible; checkout for scaffold writes
    if local_branch_exists(branch_name, repo_root=repo_root) or remote_branch_exists(
        branch_name, repo_root=repo_root
    ):
        raise GitOpsError(f"branch already exists: {branch_name}")
    run_git(["checkout", "-b", branch_name], cwd=repo_root)
    return branch_name


def checkout_branch(branch_name: str, *, repo_root: Path) -> None:
    run_git(["checkout", branch_name], cwd=repo_root)


def return_to_branch(branch_name: str, *, repo_root: Path, spec_relpath: str) -> None:
    """Return to ``branch_name``, discarding uncommitted spec scaffold files if needed."""
    if current_branch(repo_root) == branch_name:
        return
    try:
        checkout_branch(branch_name, repo_root=repo_root)
    except GitOpsError:
        run_git(["checkout", "-f", branch_name], cwd=repo_root)
        run_git(["clean", "-fd", "--", spec_relpath], cwd=repo_root)


def current_branch(repo_root: Path) -> str:
    return run_git(["branch", "--show-current"], cwd=repo_root)


def _push_rejected(message: str) -> bool:
    lowered = message.lower()
    return (
        "[rejected]" in lowered
        or "fetch first" in lowered
        or "non-fast-forward" in lowered
        or "updates were rejected" in lowered
    )


def persist_integration_branch(
    repo_root: Path,
    *,
    message: str = "chore(ta5py): scaffold official spec integration",
    push: bool = False,
    remote: str = "origin",
    spec_relpath: str = "src/ta5py/spec",
) -> str | None:
    """Commit scaffolded spec files on the current branch; optionally push.

    Scheduled CI uses ``push=True`` so the integration branch is not discarded
    when the workflow workspace is deleted. Maintainers without push credentials
    can run the same detect/integrate command on a long-lived host.

    A non-fast-forward rejection is raised as ``RemoteAheadError`` and does not
    overwrite the remote branch. Callers skip that candidate and continue.
    """
    status = run_git(["status", "--porcelain", "--", spec_relpath], cwd=repo_root)
    if not status:
        return None
    run_git(["add", "--", spec_relpath], cwd=repo_root)
    run_git(["commit", "-m", message], cwd=repo_root)
    branch = current_branch(repo_root)
    if push:
        try:
            run_git(["push", "-u", remote, branch], cwd=repo_root)
        except GitOpsError as exc:
            if _push_rejected(str(exc)):
                raise RemoteAheadError(
                    f"{remote}/{branch} has commits not in the local branch; "
                    "left the remote unchanged"
                ) from exc
            raise
    return branch
