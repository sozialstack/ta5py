# Feature Specification: Convert Official PDFs to Markdown

**Feature Branch**: `003-pdf-to-md`

**Created**: 2026-08-17

**Status**: Draft

**Input**: User description: "all pdf should be converted into md files. make a script to convert pdf. convert all pdf in the repo. keep the pdf. update all scripts that download pdf to convert pdf. make a small SKILL to convert the pdf."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Convert a PDF to a Markdown companion (Priority: P1)

A contributor has an official regulatory PDF (for example an Anlage under `packages/gkv-edi/spec/official/`) and needs a readable Markdown file next to it so humans and agents can search and cite text without opening the binary PDF.

**Why this priority**: Markdown companions are the core deliverable; without conversion, nothing else in this feature delivers value.

**Independent Test**: Place one sample PDF in a known folder, run the conversion entry point for that file, and verify a Markdown file appears beside the PDF with extracted textual content while the original PDF remains unchanged.

**Acceptance Scenarios**:

1. **Given** a valid PDF at a path under the repository workspace, **When** conversion runs for that file, **Then** a Markdown file is produced at the same directory with the same base name and `.md` extension.
2. **Given** a successful conversion, **When** the contributor inspects the folder, **Then** the original PDF still exists with the same content as before conversion.
3. **Given** a PDF whose text can be extracted, **When** the Markdown is opened, **Then** it contains readable body text derived from the PDF (not an empty stub).

---

### User Story 2 - Convert every PDF already in the repository (Priority: P1)

A maintainer wants one command that finds all PDFs in the repo (excluding virtualenvs and other ignore paths) and ensures each has a Markdown companion, without deleting or replacing any PDF.

**Why this priority**: Existing local/CI-fetched PDFs must become usable as text in one pass; equal priority to single-file conversion for rollout.

**Independent Test**: With a fixture tree containing several PDFs (some already with `.md`, some without), run bulk conversion and confirm every PDF has a Markdown sibling and no PDF was removed or modified.

**Acceptance Scenarios**:

1. **Given** multiple PDFs under module `spec/` trees (and any other tracked or fetchable PDF locations in scope), **When** bulk conversion runs, **Then** each PDF has a corresponding Markdown companion.
2. **Given** a PDF that already has an up-to-date Markdown companion, **When** bulk conversion runs, **Then** the run skips or refreshes idempotently without failing and without deleting the PDF.
3. **Given** bulk conversion completes, **When** the maintainer lists PDF paths, **Then** every PDF that existed before the run still exists.

---

### User Story 3 - Download scripts also produce Markdown (Priority: P2)

When a maintainer downloads official PDFs via existing download scripts (for example `download_official_pdfs`), each newly fetched or already-present PDF is also converted to Markdown in the same workflow so contributors do not need a separate manual step after download.

**Why this priority**: Keeps Markdown in sync with the fetch path contributors already use; depends on the conversion capability from US1.

**Independent Test**: Run the updated download workflow against a manifest (or dry-run fixture); after success, each downloaded PDF path has a Markdown sibling and the PDF remains.

**Acceptance Scenarios**:

1. **Given** a download script that fetches official PDFs, **When** it completes successfully, **Then** each PDF it wrote or confirmed also has a Markdown companion.
2. **Given** a PDF that was skipped because it already existed, **When** download finishes, **Then** conversion still ensures a Markdown companion exists for that PDF.
3. **Given** conversion fails for one PDF after a successful download, **When** the script reports the outcome, **Then** the PDF is kept and the failure is clearly reported (Markdown may be missing for that file only).

---

### User Story 4 - Agent skill for PDF conversion (Priority: P3)

A Cursor agent (or contributor following agent skills) needs a small project skill that explains when and how to convert PDFs to Markdown using the project’s conversion entry point, so agents do not invent ad-hoc conversion approaches.

**Why this priority**: Improves agent consistency; secondary to scripts and bulk conversion that humans and CI use directly.

**Independent Test**: An agent or reviewer following only the skill can identify the conversion command, when to run it (after download, for a single file, for the whole repo), and that PDFs must be retained.

**Acceptance Scenarios**:

1. **Given** the skill is installed under the project skills location, **When** a contributor opens it, **Then** it states the conversion entry point, bulk vs single-file usage, and the rule that PDFs are never deleted.
2. **Given** a task “convert PDFs after download,” **When** an agent follows the skill, **Then** it uses the project conversion path rather than an unrelated external workflow.

---

### Edge Cases

- PDF with no extractable text (scanned/image-only): produce a Markdown file that clearly states text extraction was empty or limited; keep the PDF; do not treat as a silent success with empty useful content unmarked.
- Corrupt or non-PDF file with `.pdf` extension: fail that file with a clear error; do not delete the file; continue other files in bulk mode when reasonable.
- Very large PDF: conversion completes or fails with a clear resource/timeout message; PDF remains.
- Path outside the repository or under ignored tooling dirs (e.g. `.venv`): bulk conversion does not traverse those directories.
- Markdown companion already exists and is newer or identical: idempotent behavior (skip or overwrite consistently as documented in Assumptions).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST provide a conversion entry point that turns a PDF into a Markdown file alongside the PDF (same directory, same base name, `.md` extension).
- **FR-002**: Conversion MUST NOT delete, move, or overwrite the source PDF.
- **FR-003**: The project MUST provide a bulk mode that discovers PDFs under the repository (respecting standard ignore paths such as `.venv`, `.git`, and similar) and converts each missing or stale companion as defined in Assumptions.
- **FR-004**: All scripts that download PDFs into the repository MUST invoke conversion for each PDF they fetch or confirm, so Markdown companions stay aligned with downloads.
- **FR-005**: Converted Markdown MUST preserve extractable text content in a form useful for search and citation (headings where detectable are desirable but plain structured text is acceptable).
- **FR-006**: Conversion failures MUST be reported clearly per file without removing the PDF.
- **FR-007**: The project MUST include a small Cursor Agent Skill documenting when and how to run PDF→Markdown conversion and that PDFs are retained.
- **FR-008**: Existing official PDF locations under module `spec/` trees (notably format official Anlagen) MUST be in scope for bulk conversion once PDFs are present locally.
- **FR-009**: Bulk and download-triggered conversion MUST be runnable via the project’s standard contributor toolchain entry points (documented commands / Make targets as already used for PDF download).

### Key Entities

- **Source PDF**: Official or local PDF document stored in the repository workspace; retained after conversion.
- **Markdown Companion**: Text extraction sibling of a Source PDF; same base name, `.md` extension; used for reading, search, and agent context.
- **Download Script**: Existing or future script that fetches PDFs into the repo; must trigger companion generation.
- **Conversion Skill**: Short agent skill describing conversion usage and retention rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After bulk conversion on a workspace that contains N in-scope PDFs, N Markdown companions exist (100% coverage) and N PDFs remain unchanged in place.
- **SC-002**: A single-file conversion completes for a typical multi-page regulatory PDF in under 2 minutes on a standard developer machine.
- **SC-003**: After running an updated PDF download workflow, every successfully obtained PDF has a Markdown companion without a separate manual conversion step.
- **SC-004**: A new contributor following project docs or the skill can produce a Markdown companion for one PDF on the first attempt without deleting the PDF.
- **SC-005**: At least 95% of text-extractable PDFs in the official format set yield Markdown whose body is non-empty and human-readable (image-only PDFs are excluded from this rate and labeled per edge cases).

## Assumptions

- Scope is repository tooling and official/spec PDFs (especially `packages/gkv-edi` download path and any other module PDFs under `spec/`); not a general end-user document product.
- “Keep the PDF” means retain the binary; Markdown is additive.
- If a Markdown companion already exists, conversion may overwrite it to refresh from the PDF (idempotent refresh), unless the run is explicitly skip-if-present—default is refresh-from-PDF for consistency with re-downloads.
- Bulk conversion skips `.venv`, `.git`, `__pycache__`, `.pytest_cache`, and similar tooling directories.
- Text extraction quality follows what the chosen converter can obtain from text-based PDFs; perfect layout fidelity is not required.
- Only one download script currently exists (`packages/gkv-edi/scripts/download_official_pdfs.py`); FR-004 applies to that script and any future PDF download scripts.
- The Cursor skill lives under the project’s `.cursor/skills/` (or equivalent project skills path) and is intentionally small (when to run, commands, retention rule).
- PDFs may remain gitignored while Markdown companions MAY be gitignored or tracked per existing official-spec policy; this feature does not require committing large binaries.
