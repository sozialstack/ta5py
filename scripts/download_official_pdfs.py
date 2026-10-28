#!/usr/bin/env python3
"""Download official GKV SLE PDFs into spec/docs/."""

from __future__ import annotations

import importlib.util
import sys
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML required: uv sync / pip install PyYAML", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT
MANIFEST = ROOT / "spec" / "docs" / "sources.manifest.yaml"
OUT_ROOT = ROOT / "spec" / "docs"
CONVERT_SCRIPT = REPO_ROOT / "scripts" / "convert_pdfs_to_md.py"


def _load_converter():
    spec = importlib.util.spec_from_file_location("convert_pdfs_to_md", CONVERT_SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load converter: {CONVERT_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    # Required before exec_module so @dataclass can resolve the module namespace
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _convert_pdf(dest: Path, converter) -> int:
    """Convert one PDF; keep PDF on failure. Returns 0 on ok/empty_text/skipped, 1 on error."""
    result = converter.convert_one(dest, skip_existing=False)
    print(converter.format_result_line(result, repo_root=REPO_ROOT))
    return 1 if result.status == "error" else 0


def main() -> int:
    converter = _load_converter()
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    base = data["base_url"].rstrip("/")
    ok = 0
    convert_failures = 0
    for doc in data["documents"]:
        dest_dir = OUT_ROOT / doc["bucket"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / doc["filename"]
        url = base + doc["path"]
        if dest.is_file() and dest.stat().st_size > 1000:
            head = dest.read_bytes()[:4]
            if head == b"%PDF":
                print(f"skip (exists): {dest.relative_to(ROOT)}")
                convert_failures += _convert_pdf(dest, converter)
                ok += 1
                continue
        print(f"download: {url}")
        urllib.request.urlretrieve(url, dest)
        head = dest.read_bytes()[:4]
        if head != b"%PDF":
            dest.unlink(missing_ok=True)
            print(f"ERROR: not a PDF: {dest}", file=sys.stderr)
            return 1
        print(f"wrote: {dest} ({dest.stat().st_size} bytes)")
        convert_failures += _convert_pdf(dest, converter)
        ok += 1
    print(f"done: {ok}/{len(data['documents'])} files")
    if convert_failures:
        print(
            f"ERROR: {convert_failures} PDF(s) failed Markdown conversion "
            "(PDFs were kept)",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
