# Implementation Plan: Convert Official PDFs to Markdown

**Branch**: `003-pdf-to-md` | **Date**: 2026-08-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/gkv-edi/003-pdf-to-md/spec.md`

## Summary

Add a reusable PDF→Markdown conversion script, run it for every in-scope PDF in the repo (keeping PDFs), wire it into `download_official_pdfs.py` / Make targets so downloads always produce companions, and ship a small Cursor skill documenting the workflow.

## Technical Context

**Language/Version**: Python 3.12+ (repo standard via `uv`)

**Primary Dependencies**: `pdfminer.six` (text extraction; MIT/BSD-friendly); existing `PyYAML` for format scripts; stdlib `pathlib`/`argparse`

**Storage**: Filesystem only — PDF binaries + sibling `.md` companions under module `spec/` trees (notably `packages/gkv-edi/spec/official/`)

**Testing**: pytest under `packages/gkv-edi/tests/` with tiny synthetic PDF fixtures (no real Sozialdaten)

**Target Platform**: Contributor/CI workstations (Windows, macOS, Linux) via `uv run`

**Project Type**: Repository tooling scripts + agent skill (format-module adjacent)

**Performance Goals**: Typical multi-page Anlage PDF converts in under 2 minutes (SC-002); bulk over ~6–20 PDFs finishes in one interactive run

**Constraints**: Never delete/move/overwrite PDFs; skip `.venv`/`.git`/cache dirs; English project artifacts; `uv`-only toolchain; Markdown is additive

**Scale/Scope**: All PDFs under the repo workspace in scope for bulk mode; one existing download script today; one small project skill

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| I. English-First | PASS | Spec, plan, skill, script messages/docs in English |
| II. Modular layers | PASS | Tooling lives as scripts + skill; no cross-layer merge of format/cert/transfer/api |
| III. Module constitutions | PASS | Feature under `specs/gkv-edi/003-pdf-to-md/`; does not weaken format dual-validation rules |
| IV. Synthetic data only | PASS | Tests use synthetic tiny PDFs; no real claim/PII content |
| V. Certification clarity | PASS | Markdown is a reading aid; official PDF remains authority; no Testat claims |
| Tooling (`uv`) | PASS | All run/docs use `uv run` / Make targets |
| Domain path layout | PASS | Specs under `specs/gkv-edi/NNN-…` |

**Post-design re-check**: PASS — design adds files only under `scripts/`, `packages/gkv-edi/scripts/`, `.cursor/skills/`, and this feature folder; PDF remains authoritative source.

## Project Structure

### Documentation (this feature)

```text
specs/gkv-edi/003-pdf-to-md/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── convert-pdf-cli.md
└── tasks.md              # /speckit-tasks
```

### Source Code (repository root)

```text
scripts/
└── convert_pdfs_to_md.py          # CLI: single file, paths, or repo-wide bulk

packages/gkv-edi/
├── scripts/
│   └── download_official_pdfs.py  # invoke conversion after each PDF
├── tests/
│   ├── fixtures/pdf/              # tiny synthetic PDF(s)
│   └── test_convert_pdfs_to_md.py
└── pyproject.toml                 # add pdfminer.six

.cursor/skills/
└── convert-pdf-to-md/
    └── SKILL.md                   # small agent skill

Makefile                           # convert-pdfs target; download chains convert
```

**Structure Decision**: Shared converter at repo `scripts/convert_pdfs_to_md.py` so any module can call it; format download script imports/subprocesses that entry point; skill documents the same commands. No new Python package required for MVP.

## Complexity Tracking

> No constitution violations requiring justification.
