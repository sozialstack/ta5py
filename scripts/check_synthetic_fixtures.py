#!/usr/bin/env python3
"""Fail when fixtures contain reserved real-Sozialdaten patterns."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ta5py.synthetic_guard import scan_tree

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = [ROOT / "tests" / "fixtures"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        default=DEFAULT_ROOTS,
        help="Fixture directories to scan (default: tests/fixtures)",
    )
    args = parser.parse_args(argv)
    findings = scan_tree(list(args.roots))
    if findings:
        print("Sozialdaten pattern check FAILED:", file=sys.stderr)
        for line in findings:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print("Sozialdaten pattern check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
