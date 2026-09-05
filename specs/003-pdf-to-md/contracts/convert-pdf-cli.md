# Contract: `convert_pdfs_to_md` CLI

**Feature**: `specs/gkv-edi/003-pdf-to-md`  
**Entry point**: `uv run python scripts/convert_pdfs_to_md.py`

## Invocation

```text
uv run python scripts/convert_pdfs_to_md.py [OPTIONS] [PDF_PATH ...]
```

### Options

| Option | Default | Meaning |
|--------|---------|---------|
| `PDF_PATH` | (none) | One or more PDF files to convert |
| `--bulk` | off | Walk repository for `*.pdf` and convert each |
| `--repo-root PATH` | auto-detect (script → repo root) | Root for `--bulk` |
| `--skip-existing` | off | If set, do not overwrite an existing `.md`; default refreshes from PDF |
| `-q` / `--quiet` | off | Less stdout |

### Behavior

1. For each PDF, write `{stem}.md` in the same directory.
2. Never delete, rename, or overwrite the PDF.
3. Print one line per file: `ok|empty_text|skipped|error` and paths.
4. Exit `0` when no hard errors; exit `1` if any file is `error` (corrupt/unreadable).

### Markdown shape (minimum)

```markdown
# {original_filename}

<!-- source-pdf: {filename} -->

## Page 1

{extracted text...}
```

If no text extracted:

```markdown
# {original_filename}

<!-- source-pdf: {filename} -->

> No extractable text found. The source PDF was kept unchanged.
```

## Download script contract

`packages/gkv-edi/scripts/download_official_pdfs.py` MUST, for each document that ends as a present valid PDF:

1. Invoke conversion for that PDF path (import function or subprocess to the CLI).
2. Leave the PDF in place if conversion fails.
3. Surface conversion failures in the process exit code.

## Make targets

| Target | Behavior |
|--------|----------|
| `convert-pdfs` | `uv run python scripts/convert_pdfs_to_md.py --bulk` |
| `download-format-pdfs` | Download PDFs then ensure companions (via download script integration and/or explicit convert) |
