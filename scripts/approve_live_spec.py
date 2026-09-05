#!/usr/bin/env python3
"""Human approval / rejection and gated go-live for format packages."""

from __future__ import annotations

import argparse
import json
import sys

from gkv_edi.governance.approve import ApprovalError, approve_candidate, go_live
from gkv_edi.governance.store import load_live_binding
from gkv_edi.spec_loader import SPEC_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--actor", required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--approve", action="store_true")
    group.add_argument("--reject", action="store_true")
    parser.add_argument("--go-live", action="store_true")
    parser.add_argument(
        "--confirm-older",
        action="store_true",
        help="Required when activating an older package over a newer live binding",
    )
    parser.add_argument("--note")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.approve and not args.reject and not args.go_live:
        print("ERROR: provide --approve, --reject, and/or --go-live", file=sys.stderr)
        return 2

    try:
        cand = None
        if args.approve or args.reject:
            decision = "approve" if args.approve else "reject"
            cand = approve_candidate(
                args.candidate,
                actor=args.actor,
                decision=decision,
                note=args.note,
                spec_root=SPEC_ROOT,
            )
        binding = None
        if args.go_live:
            binding = go_live(
                args.candidate,
                actor=args.actor,
                spec_root=SPEC_ROOT,
                require_approval=True,
                confirm_older=args.confirm_older,
            )
        if args.json:
            payload = {
                "candidate": cand.to_dict() if cand else None,
                "live": binding.to_dict() if binding else load_live_binding(SPEC_ROOT),
            }
            if payload["live"] and hasattr(payload["live"], "to_dict"):
                payload["live"] = payload["live"].to_dict()
            print(json.dumps(payload, indent=2, default=str))
        else:
            if cand:
                print(f"candidate={cand.id} state={cand.state} approval={cand.approval}")
            if binding:
                print(f"live={binding.package_label} by={binding.activated_by}")
                if binding.note and "WARNING" in (binding.note or ""):
                    print(f"warning={binding.note}")
            elif args.go_live is False and cand and cand.state == "rejected":
                live = load_live_binding(SPEC_ROOT)
                print(f"live_unchanged={live.package_label if live else None}")
        return 0
    except ApprovalError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
