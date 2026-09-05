#!/usr/bin/env python3
"""Show format spec governance status."""

from __future__ import annotations

import argparse
import json

from ta5py.governance.status import format_status_human, gather_status
from ta5py.spec_loader import SPEC_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = gather_status(SPEC_ROOT)
    if args.json:
        clean = {k: v for k, v in payload.items() if not k.startswith("_")}
        print(json.dumps(clean, indent=2))
    else:
        print(format_status_human(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
