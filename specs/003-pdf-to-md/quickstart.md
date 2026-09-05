# Quickstart: PDF → Markdown

**Feature**: `specs/gkv-edi/003-pdf-to-md`

## Prerequisites

- Repo checkout with `uv` available
- Dependencies synced (`uv sync`) including `pdfminer.six` once added
- Optional: official PDFs via download

## 1. Convert a single PDF

```powershell
uv run python scripts/convert_pdfs_to_md.py path\to\file.pdf
```

**Expect**: `path\to\file.md` created; `file.pdf` unchanged.

## 2. Convert all PDFs in the repo

```powershell
make convert-pdfs
# or
uv run python scripts/convert_pdfs_to_md.py --bulk
```

**Expect**: Every in-scope `*.pdf` has a sibling `.md`; PDFs retained; tooling dirs skipped.

## 3. Download official format PDFs (with conversion)

```powershell
make download-format-pdfs
```

**Expect**: PDFs under `packages/gkv-edi/spec/official/**` plus Markdown companions for each; PDFs kept.

## 4. Agent skill

See `.cursor/skills/convert-pdf-to-md/SKILL.md` for when to run conversion and the retain-PDF rule.

## Validation checklist

- [ ] Single-file conversion produces non-empty `.md` for a text PDF fixture
- [ ] Bulk run does not modify PDF bytes
- [ ] Download script leaves companions beside each official PDF
- [ ] Image-only/empty extraction writes an explicit notice in Markdown
- [ ] Corrupt `.pdf` reports error without deleting the file

Details: [convert-pdf-cli.md](./contracts/convert-pdf-cli.md), [data-model.md](./data-model.md).
