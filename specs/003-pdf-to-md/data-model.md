# Data Model: PDF → Markdown Companions

**Feature**: `specs/gkv-edi/003-pdf-to-md`  
**Date**: 2026-08-17

## Entities

### SourcePdf

| Field | Type | Rules |
|-------|------|-------|
| path | absolute/repo-relative path | Must exist; extension `.pdf` (case-insensitive) |
| size_bytes | int | Used for presence checks in download flow |
| magic | bytes | Prefer `%PDF` header for “valid PDF” checks |
| retained | bool | Always true after conversion attempts |

**Validation**: Non-empty file; bulk walker only yields paths under allowed roots excluding ignore dirs.

### MarkdownCompanion

| Field | Type | Rules |
|-------|------|-------|
| path | path | Same parent as SourcePdf; `{stem}.md` |
| source_pdf | path | Back-reference to SourcePdf |
| body | text | Extracted text in Markdown; or explicit empty-extraction notice |
| refreshed_at | timestamp (optional in file header) | Optional YAML/HTML comment or markdown metadata line |

**Validation**: Written atomically when practical (write temp then replace) to avoid truncated companions.

### ConversionResult

| Field | Type | Rules |
|-------|------|-------|
| source | SourcePdf path | Required |
| companion | MarkdownCompanion path or null | Null only on hard failure before write |
| status | enum | `ok` \| `empty_text` \| `skipped` \| `error` |
| message | string | Human-readable warning/error |

### ConversionRun

| Field | Type | Rules |
|-------|------|-------|
| mode | enum | `single` \| `paths` \| `bulk` |
| results | list[ConversionResult] | One per attempted PDF |
| exit_code | int | 0 if no `error`; 1 if any hard `error` |

## Relationships

- SourcePdf **1 — 0..1** MarkdownCompanion (goal state after successful run: 1—1)
- ConversionRun **contains** many ConversionResult
- Download script **produces** SourcePdf then **triggers** ConversionResult per file

## State transitions

```text
[PDF absent] --download--> [PDF present, MD absent]
[PDF present, MD absent] --convert--> [PDF present, MD present]
[PDF present, MD present] --convert (default refresh)--> [PDF present, MD refreshed]
[PDF present] --convert fail--> [PDF present, MD absent or stale]; status=error
```

No transition deletes or relocates the PDF.
