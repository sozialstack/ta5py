#!/usr/bin/env python3
"""Convert PDF files to sibling Markdown companions (PDFs are never deleted)."""

from __future__ import annotations

import argparse
import io
import sys
from dataclasses import dataclass
from pathlib import Path

IGNORE_DIR_NAMES = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "ENV",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "node_modules",
        ".eggs",
        "dist",
        "build",
        "htmlcov",
    }
)


@dataclass(frozen=True)
class ConversionResult:
    source: Path
    companion: Path | None
    status: str  # ok | empty_text | skipped | error
    message: str = ""


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def companion_path(pdf: Path) -> Path:
    return pdf.with_suffix(".md")


def _is_pdf_magic(path: Path) -> bool:
    try:
        return path.read_bytes()[:4] == b"%PDF"
    except OSError:
        return False


def extract_pages(pdf: Path) -> list[str]:
    """Return plain text per page (may be empty strings)."""
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
    from pdfminer.pdfpage import PDFPage

    pages: list[str] = []
    laparams = LAParams()
    with pdf.open("rb") as fh:
        for page in PDFPage.get_pages(fh, check_extractable=False):
            output = io.StringIO()
            resource_manager = PDFResourceManager()
            device = TextConverter(resource_manager, output, laparams=laparams)
            interpreter = PDFPageInterpreter(resource_manager, device)
            interpreter.process_page(page)
            device.close()
            pages.append(output.getvalue())
            output.close()
    return pages


def render_markdown(pdf: Path, pages: list[str]) -> tuple[str, bool]:
    """Build markdown body. Returns (markdown, has_extractable_text)."""
    name = pdf.name
    joined = "\n".join(p.strip() for p in pages).strip()
    has_text = bool(joined)
    lines = [
        f"# {name}",
        "",
        f"<!-- source-pdf: {name} -->",
        "",
    ]
    if not has_text:
        lines.append("> No extractable text found. The source PDF was kept unchanged.")
        lines.append("")
        return "\n".join(lines), False

    for i, page_text in enumerate(pages, start=1):
        lines.append(f"## Page {i}")
        lines.append("")
        body = page_text.strip()
        lines.append(body if body else "*(empty page)*")
        lines.append("")
    return "\n".join(lines), True


def convert_one(pdf: Path, *, skip_existing: bool = False) -> ConversionResult:
    """Convert a single PDF to a sibling `.md`. Never modifies the PDF."""
    pdf = pdf.resolve()
    md = companion_path(pdf)

    if not pdf.is_file():
        return ConversionResult(pdf, None, "error", "file not found")

    if skip_existing and md.is_file():
        return ConversionResult(pdf, md, "skipped", "markdown already exists")

    if not _is_pdf_magic(pdf):
        return ConversionResult(pdf, None, "error", "not a PDF (missing %PDF magic)")

    try:
        pages = extract_pages(pdf)
    except Exception as exc:  # noqa: BLE001 — surface any extract failure as error
        return ConversionResult(pdf, None, "error", f"extract failed: {exc}")

    markdown, has_text = render_markdown(pdf, pages)
    try:
        tmp = md.with_suffix(".md.tmp")
        tmp.write_text(markdown, encoding="utf-8")
        tmp.replace(md)
    except OSError as exc:
        return ConversionResult(pdf, None, "error", f"write failed: {exc}")

    if has_text:
        return ConversionResult(pdf, md, "ok")
    return ConversionResult(pdf, md, "empty_text", "no extractable text")


def discover_pdfs(repo_root: Path) -> list[Path]:
    root = repo_root.resolve()
    found: list[Path] = []

    def walk(directory: Path) -> None:
        try:
            entries = list(directory.iterdir())
        except OSError:
            return
        for entry in entries:
            if entry.is_dir():
                if entry.name in IGNORE_DIR_NAMES:
                    continue
                walk(entry)
            elif entry.is_file() and entry.suffix.lower() == ".pdf":
                found.append(entry)

    walk(root)
    return sorted(found)


def format_result_line(result: ConversionResult, *, repo_root: Path | None = None) -> str:
    def rel(p: Path | None) -> str:
        if p is None:
            return "-"
        if repo_root is not None:
            try:
                return str(p.relative_to(repo_root))
            except ValueError:
                pass
        return str(p)

    msg = f" {result.message}" if result.message else ""
    return f"{result.status}: {rel(result.source)} -> {rel(result.companion)}{msg}"


def run_conversions(
    pdfs: list[Path],
    *,
    skip_existing: bool = False,
    quiet: bool = False,
    repo_root: Path | None = None,
) -> int:
    hard_errors = 0
    for pdf in pdfs:
        result = convert_one(pdf, skip_existing=skip_existing)
        if result.status == "error":
            hard_errors += 1
        if not quiet:
            print(format_result_line(result, repo_root=repo_root))
    return 1 if hard_errors else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Convert PDFs to sibling Markdown files (PDFs are retained)."
    )
    p.add_argument("pdfs", nargs="*", type=Path, help="PDF file path(s) to convert")
    p.add_argument(
        "--bulk",
        action="store_true",
        help="Walk the repository for *.pdf and convert each",
    )
    p.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root for --bulk (default: parent of scripts/)",
    )
    p.add_argument(
        "--skip-existing",
        action="store_true",
        help="Do not overwrite an existing .md companion",
    )
    p.add_argument("-q", "--quiet", action="store_true", help="Less stdout")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = (args.repo_root or default_repo_root()).resolve()

    pdfs: list[Path] = []
    if args.bulk:
        pdfs.extend(discover_pdfs(repo_root))
    pdfs.extend(p.resolve() for p in args.pdfs)

    if not pdfs:
        print(
            "error: provide PDF path(s) and/or --bulk",
            file=sys.stderr,
        )
        return 1

    # De-dupe while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for pdf in pdfs:
        if pdf not in seen:
            seen.add(pdf)
            unique.append(pdf)

    return run_conversions(
        unique,
        skip_existing=args.skip_existing,
        quiet=args.quiet,
        repo_root=repo_root,
    )


if __name__ == "__main__":
    raise SystemExit(main())
