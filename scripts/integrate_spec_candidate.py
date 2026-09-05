#!/usr/bin/env python3
"""Scaffold a detected format package on a new git branch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gkv_edi.governance.integrate import DuplicateCandidateError, integrate_candidate
from gkv_edi.governance.store import load_live_binding
from gkv_edi.spec_loader import SPEC_ROOT

REPO_ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", help="Candidate id")
    parser.add_argument("--from-latest-new", action="store_true")
    parser.add_argument("--base-package", help="Base package to copy (default: live)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git branch creation (tests / dry local scaffold)",
    )
    args = parser.parse_args()

    if not args.candidate and not args.from_latest_new:
        print("ERROR: provide --candidate or --from-latest-new", file=sys.stderr)
        return 2

    try:
        before = load_live_binding(SPEC_ROOT)
        cand = integrate_candidate(
            args.candidate,
            from_latest_new=args.from_latest_new,
            base_package=args.base_package,
            dry_run=args.dry_run,
            create_git_branch=not args.no_git and not args.dry_run,
            repo_root=REPO_ROOT,
            spec_root=SPEC_ROOT,
        )
        after = load_live_binding(SPEC_ROOT)
        if before and after and before.package_label != after.package_label:
            print("ERROR: live binding changed during integrate", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(cand.to_dict(), indent=2))
        else:
            print(
                f"candidate={cand.id} state={cand.state} branch={cand.branch_name} "
                f"package={cand.package_label}"
            )
        return 0 if cand.state != "failed" else 1
    except DuplicateCandidateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
