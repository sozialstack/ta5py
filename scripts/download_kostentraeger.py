#!/usr/bin/env python3
"""Download current SLE Kostenträgerdateien and optionally ingest them."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ta5py.kostentraeger import ingest_kostentraeger_files
from ta5py.kostentraeger_fetch import (
    OVERVIEW_URL,
    download_kostentraeger_files,
    fetch_bytes,
    parse_kostentraeger_overview,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEST = ROOT / "var" / "kostentraeger"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overview-html",
        type=Path,
        help="Overview HTML snapshot (offline; skips live fetch of the listing page)",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help=f"Directory for .ke* files (default: {DEFAULT_DEST})",
    )
    parser.add_argument(
        "--ingest",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write combined lookup store.json next to the files (default: true)",
    )
    parser.add_argument("--spec-version", default=None, help="ta5py package label (default: live)")
    parser.add_argument("--json", action="store_true", help="Machine-readable listing")
    args = parser.parse_args()

    if args.overview_html is not None:
        html = args.overview_html.read_text(encoding="utf-8")
    else:
        html = fetch_bytes(OVERVIEW_URL).decode("utf-8", errors="replace")

    files = parse_kostentraeger_overview(html)
    print(f"discovered={len(files)} dest={args.dest}")
    paths = download_kostentraeger_files(files, args.dest)
    for item, path in zip(files, paths, strict=True):
        print(f"wrote {item.kassenart} {item.label}: {path.name} ({path.stat().st_size} bytes)")

    store = None
    if args.ingest:
        store_path = args.dest / "store.json"
        store = ingest_kostentraeger_files(paths, spec_version=args.spec_version, store_path=store_path)
        entries = store.as_dict()
        acceptance = {row.get("acceptance_ik") for row in entries.values() if row.get("acceptance_ik")}
        with_dfue = sum(1 for row in entries.values() if row.get("dfue_hint"))
        print(
            f"ingested entries={len(store)} unique_acceptance_ik={len(acceptance)} "
            f"with_dfue_hint={with_dfue} store={store_path}"
        )

    if args.json:
        payload = {
            "files": [
                {
                    "filename": item.filename,
                    "kassenart": item.kassenart,
                    "label": item.label,
                    "url": item.url,
                    "bytes": (args.dest / item.filename).stat().st_size,
                }
                for item in files
            ],
            "entries": len(store) if store is not None else None,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
