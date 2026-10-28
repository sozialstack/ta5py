#!/usr/bin/env python3
"""Detect new/changed official GKV format publications."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ta5py.governance.detect import run_detection, should_auto_integrate
from ta5py.governance.integrate import DuplicateCandidateError, integrate_candidate
from ta5py.governance.gitops import persist_integration_branch
from ta5py.governance.store import list_candidates, load_live_binding
from ta5py.spec_loader import SPEC_ROOT

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KNOWN = ROOT / "spec" / "docs" / "sources.manifest.yaml"
REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--on-demand",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Explicit manual run marker (default: true)",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        help="Discovered sources: YAML manifest or overview HTML snapshot",
    )
    parser.add_argument(
        "--overview-html",
        type=Path,
        help="Overview HTML snapshot (alternative to --fixture)",
    )
    parser.add_argument(
        "--known",
        type=Path,
        default=DEFAULT_KNOWN,
        help="Known sources manifest (default: spec/docs/sources.manifest.yaml)",
    )
    parser.add_argument(
        "--network",
        action="store_true",
        help="Fetch overview_url from known manifest when no fixture is provided",
    )
    parser.add_argument(
        "--update-manifest-metadata",
        action="store_true",
        help="Write last-check / ETag metadata into the known sources.manifest.yaml",
    )
    parser.add_argument(
        "--scheduled",
        "--periodic",
        dest="scheduled",
        action="store_true",
        help="Periodic/scheduled check: auto-integrate new packages (does not change live binding)",
    )
    parser.add_argument(
        "--detect-only",
        action="store_true",
        help="Do not auto-integrate after detection (dry run; default for on-demand)",
    )
    parser.add_argument(
        "--auto-integrate",
        action="store_true",
        help="After on-demand detection, scaffold each newly detected candidate on a branch",
    )
    parser.add_argument("--no-git", action="store_true", help="Skip git when auto-integrating")
    parser.add_argument(
        "--push",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="After auto-integrate, commit and push the integration branch (scheduled CI should pass --push)",
    )
    parser.add_argument("--json", action="store_true", help="Machine-readable DetectionRun")
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Simulate unreachable source (for tests)",
    )
    args = parser.parse_args()

    if args.fixture is None and args.overview_html is None and not args.fail and not args.network:
        print(
            "ERROR: provide --fixture / --overview-html, or --network to fetch overview_url",
            file=sys.stderr,
        )
        return 2

    # --on-demand is a contract marker; all CLI invocations are on-demand by default.
    _ = args.on_demand

    run = run_detection(
        known_manifest=args.known,
        fixture=args.fixture,
        overview_html=args.overview_html,
        allow_network=args.network,
        update_manifest_metadata=args.update_manifest_metadata,
        fail=args.fail,
        spec_root=SPEC_ROOT,
    )
    if args.json:
        print(json.dumps(run.to_dict(), indent=2))
    else:
        print(f"status={run.status} new={run.new_or_changed_ids} oos={run.out_of_scope_ids}")
        if run.error_message:
            print(f"error={run.error_message}")

    if run.status == "failed":
        return 1

    auto = should_auto_integrate(
        scheduled=args.scheduled,
        detect_only=args.detect_only,
        auto_integrate=args.auto_integrate,
    )
    live_before = load_live_binding(SPEC_ROOT)
    if auto and run.new_or_changed_ids:
        detected = [c for c in list_candidates(SPEC_ROOT) if c.state == "detected"]
        for cand in detected:
            try:
                result = integrate_candidate(
                    cand.id,
                    create_git_branch=not args.no_git,
                    repo_root=REPO_ROOT,
                    spec_root=SPEC_ROOT,
                    known_manifest=args.known,
                )
                print(
                    f"auto-integrate candidate={result.id} state={result.state} "
                    f"branch={result.branch_name}"
                )
            except DuplicateCandidateError as exc:
                print(f"auto-integrate skip duplicate: {exc}", file=sys.stderr)
            except Exception as exc:  # noqa: BLE001
                print(f"auto-integrate ERROR: {exc}", file=sys.stderr)
                return 1
        if not args.no_git:
            try:
                persisted = persist_integration_branch(REPO_ROOT, push=args.push)
                if persisted:
                    print(f"persisted integration branch={persisted}")
            except Exception as exc:  # noqa: BLE001
                print(f"persist integration branch ERROR: {exc}", file=sys.stderr)
                return 1
        live_after = load_live_binding(SPEC_ROOT)
        before_label = live_before.package_label if live_before else None
        after_label = live_after.package_label if live_after else None
        if before_label != after_label:
            print(
                f"ERROR: live binding changed during detect/integrate "
                f"({before_label!r} → {after_label!r})",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
