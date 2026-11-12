# Research: Convert Official PDFs to Markdown

**Feature**: `specs/ta5py/003-pdf-to-md`  
**Date**: 2026-08-17

## R1 — Extraction library

**Decision**: Use **`pdfminer.six`** to extract text from PDFs, then wrap output in lightly structured Markdown (document title from filename, optional `## Page N` separators when page breaks are available).

**Rationale**: MIT-licensed, pure Python, fits `uv` workspaces, adequate for text-based GKV Anlage PDFs. Avoids AGPL concerns with PyMuPDF and avoids heavy ML converters.

**Alternatives considered**:
- **PyMuPDF / pymupdf4llm** — excellent quality; rejected for AGPL licensing friction in an open-source clearing project.
- **Microsoft MarkItDown** — convenient; rejected as heavier transitive surface for a narrow PDF-only need.
- **External `pdftotext` (poppler)** — rejected for non-portable system dependency across Windows/macOS/Linux contributors.

## R2 — Script location and CLI shape

**Decision**: One repo-root script `scripts/convert_pdfs_to_md.py` with argparse modes:
- positional PDF path(s), and/or
- `--repo-root` bulk walk (default: repository root), and/or
- `--skip-existing` optional flag (default: **refresh** Markdown from PDF per spec Assumptions).

Output path: same directory as PDF, `{stem}.md`.

**Rationale**: Download scripts and Make targets need one stable entry point; root `scripts/` matches existing `download-format-pdfs` / `check_synthetic_fixtures.py` pattern.

**Alternatives considered**:
- Only under `packages/ta5py/scripts/` — weaker for cert/other module PDFs.
- Package inside `format` library API — overkill for file tooling.

## R3 — Download script integration

**Decision**: After each successful PDF presence check/write in `download_official_pdfs.py`, call the converter for that destination path. Make target `download-format-pdfs` remains the human entry; optionally add `convert-pdfs` Make target for bulk-only runs.

**Rationale**: FR-004 — contributors who only download still get Markdown. Keep PDF on conversion failure; non-zero exit if any conversion fails after downloads (or accumulate errors and exit 1) so CI notices missing companions.

**Alternatives considered**:
- Separate manual convert step only — rejected (user required download scripts to convert).
- Shell-only Make chaining without Python call from download script — weaker for “skipped existing PDF” path that must still ensure `.md`.

## R4 — Bulk discovery rules

**Decision**: Walk from repo root; include `*.pdf` files; exclude directory names: `.git`, `.venv`, `venv`, `__pycache__`, `.pytest_cache`, `node_modules`, `.ruff_cache`, `.mypy_cache`.

**Rationale**: Matches spec edge cases and keeps tooling dirs out of scope.

## R5 — Git tracking policy for Markdown

**Decision**: Track both official PDFs and Markdown companions under `specs/docs/` (do not add a blanket ignore for either). PDFs stay authoritative; `.md` files are reading/search aids.

**Rationale**: Agents and greppable reviews benefit from text without fetching PDFs; PDF remains authoritative binary.

**Alternatives considered**:
- Gitignore all official `.md` — forces everyone to convert locally; worse for agent context.
- Commit PDFs — rejected (existing size/policy).

## R6 — Cursor skill

**Decision**: Small project skill at `.cursor/skills/convert-pdf-to-md/SKILL.md` covering: when to convert (after download, single file, repo bulk), exact `uv run` / Make commands, retain-PDF rule, and that official PDF remains normative over Markdown.

**Rationale**: FR-007; keep skill short per create-skill guidance.

## R7 — Empty / image-only PDFs

**Decision**: Always write a Markdown file; if extracted text is empty/whitespace, body includes a clear note that no extractable text was found and the PDF was kept; exit warning or count as conversion soft-failure configurable — MVP: write stub note, exit 0 for that file but print warning (bulk continues). Corrupt non-PDF: exit error for that file, keep file, bulk continues, process exit 1 if any hard failures.

**Rationale**: Matches edge cases in spec without deleting sources.
