# Tasks: Convert Official PDFs to Markdown

**Input**: Design documents from `specs/ta5py/003-pdf-to-md/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not explicitly requested in the feature specification — no dedicated TDD test tasks. Validate via quickstart scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependencies and stub entry points for conversion tooling

- [x] T001 Add `pdfminer.six` dependency to `packages/ta5py/pyproject.toml` (and sync workspace lock via `uv lock` / `uv sync` at repo root)
- [x] T002 Create converter stub CLI `scripts/convert_pdfs_to_md.py` with argparse skeleton matching `specs/ta5py/003-pdf-to-md/contracts/convert-pdf-cli.md` (modes: paths, `--bulk`, `--repo-root`, `--skip-existing`)
- [x] T003 [P] Add Make target `convert-pdfs` in `Makefile` invoking `uv run python scripts/convert_pdfs_to_md.py --bulk`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared conversion core used by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement PDF text extraction + Markdown writer helpers in `scripts/convert_pdfs_to_md.py` (sibling `{stem}.md`, never delete/modify PDF bytes, empty-text notice, corrupt-file error status per `specs/ta5py/003-pdf-to-md/data-model.md`)
- [x] T005 Implement ignore-dir bulk walker and per-file `ConversionResult` reporting/exit codes in `scripts/convert_pdfs_to_md.py` per `specs/ta5py/003-pdf-to-md/contracts/convert-pdf-cli.md`
- [x] T006 [P] Add a tiny synthetic text PDF fixture under `packages/ta5py/tests/fixtures/pdf/sample_text.pdf` for manual/quickstart validation (no real Sozialdaten)

**Checkpoint**: `uv run python scripts/convert_pdfs_to_md.py packages/ta5py/tests/fixtures/pdf/sample_text.pdf` can be completed in US1

---

## Phase 3: User Story 1 - Convert a PDF to a Markdown companion (Priority: P1) 🎯 MVP

**Goal**: Single-file conversion produces a sibling `.md` and retains the PDF

**Independent Test**: Convert `packages/ta5py/tests/fixtures/pdf/sample_text.pdf`; confirm `.md` exists with readable text and PDF unchanged

### Implementation for User Story 1

- [x] T007 [US1] Wire CLI positional PDF path handling in `scripts/convert_pdfs_to_md.py` to call the foundational converter and print `ok|empty_text|error` lines
- [x] T008 [US1] Document single-file usage in `packages/ta5py/spec/official/README.md` (link retain-PDF rule and `uv run python scripts/convert_pdfs_to_md.py <pdf>`)

**Checkpoint**: US1 independently usable for one PDF

---

## Phase 4: User Story 2 - Convert every PDF already in the repository (Priority: P1)

**Goal**: `--bulk` / `make convert-pdfs` converts all in-scope repo PDFs without removing any PDF

**Independent Test**: Place/copy ≥2 PDFs under a temp folder inside the repo (or use official + fixture); run bulk; every PDF has sibling `.md`; PDF count unchanged

### Implementation for User Story 2

- [x] T009 [US2] Enable and verify `--bulk` / `--repo-root` path in `scripts/convert_pdfs_to_md.py` (skip `.venv`, `.git`, `__pycache__`, `.pytest_cache`, etc.)
- [x] T010 [US2] Run bulk conversion against the workspace once PDFs are present (`make convert-pdfs`) and confirm companions under `packages/ta5py/spec/official/**` when downloads exist
- [x] T011 [P] [US2] Note in `packages/ta5py/README.md` that `make convert-pdfs` generates Markdown companions while keeping PDFs

**Checkpoint**: US2 delivers repo-wide coverage

---

## Phase 5: User Story 3 - Download scripts also produce Markdown (Priority: P2)

**Goal**: `download_official_pdfs` ensures a Markdown companion for every fetched or already-present PDF

**Independent Test**: Run `make download-format-pdfs`; each official PDF has a sibling `.md`; PDFs retained; conversion failure leaves PDF and fails the run clearly

### Implementation for User Story 3

- [x] T012 [US3] Update `packages/ta5py/scripts/download_official_pdfs.py` to invoke conversion for each confirmed PDF path (import callable from `scripts/convert_pdfs_to_md.py` or subprocess `uv run python scripts/convert_pdfs_to_md.py`)
- [x] T013 [US3] Ensure skipped-existing PDF branch still triggers companion generation in `packages/ta5py/scripts/download_official_pdfs.py`
- [x] T014 [US3] Propagate conversion hard-failures to non-zero exit in `packages/ta5py/scripts/download_official_pdfs.py` without deleting PDFs
- [x] T015 [P] [US3] Align `Makefile` target `download-format-pdfs` docs/comments so download implies convert (script-integrated)

**Checkpoint**: Download path alone yields Markdown companions

---

## Phase 6: User Story 4 - Agent skill for PDF conversion (Priority: P3)

**Goal**: Small project skill teaches agents when/how to convert and to keep PDFs

**Independent Test**: Following only `.cursor/skills/convert-pdf-to-md/SKILL.md`, an agent uses the project CLI/Make targets and never deletes PDFs

### Implementation for User Story 4

- [x] T016 [US4] Create `.cursor/skills/convert-pdf-to-md/SKILL.md` with YAML frontmatter (`name`, `description`), triggers (after PDF download, convert one/all PDFs), commands (`make convert-pdfs`, `make download-format-pdfs`, single-file `uv run`), and explicit retain-PDF + PDF-authoritative rules
- [x] T017 [P] [US4] Keep the skill short (one screen of procedure); point to `specs/ta5py/003-pdf-to-md/quickstart.md` for details rather than duplicating the full contract

**Checkpoint**: Skill is usable without reading the full feature folder

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs and end-to-end validation

- [x] T018 [P] Update root `README.md` (if it mentions format PDF download) to mention Markdown companions / `convert-pdfs`
- [x] T019 Run quickstart validation from `specs/ta5py/003-pdf-to-md/quickstart.md` (single, bulk, download) and fix any gaps in scripts or docs
- [x] T020 [P] Confirm official PDFs remain gitignored and Markdown companions are not blanket-ignored in `.gitignore`
  - **Superseded**: official PDFs under `packages/ta5py/spec/docs/` are now tracked in git (gitignore entry removed).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on Foundational; uses same CLI as US1 (bulk flag)
- **US3 (Phase 5)**: Depends on US1 conversion callable working (Foundational + US1)
- **US4 (Phase 6)**: Can start after Make targets/commands exist (after T003 + T007); ideally after US2/US3 commands are final
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational — no dependency on other stories
- **User Story 2 (P1)**: After Foundational — bulk mode; independently testable from US1
- **User Story 3 (P2)**: Needs converter entry point (US1/Foundational)
- **User Story 4 (P3)**: Documents commands from US1–US3; independently reviewable as docs

### Parallel Opportunities

- T003 parallel with T002 after T001
- T006 parallel with T004/T005
- T011 parallel with T009/T010
- T015 parallel with T012–T014
- T017 parallel with T016
- T018/T020 parallel in polish

---

## Parallel Example: User Story 2

```bash
# After Foundational:
Task: "Enable --bulk walker in scripts/convert_pdfs_to_md.py"
Task: "Note convert-pdfs in packages/ta5py/README.md"
```

---

## Parallel Example: User Story 3

```bash
# After converter callable exists:
Task: "Wire download_official_pdfs.py to convert each PDF"
Task: "Align Makefile download-format-pdfs comments"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1–2
2. Complete Phase 3 (US1)
3. **STOP and VALIDATE**: single-file convert + PDF retained
4. Continue US2 for repo-wide value

### Incremental Delivery

1. Setup + Foundational → converter core ready
2. US1 → single-file MVP
3. US2 → bulk convert all repo PDFs (keep PDFs)
4. US3 → download scripts auto-convert
5. US4 → small skill
6. Polish → quickstart + README/gitignore checks

### Suggested MVP scope

User Story 1 only (single-file conversion script).

---

## Notes

- [P] = different files, no incomplete-task dependencies
- All tasks use checklist format with Task IDs and file paths
- Official PDF remains normative; Markdown is a reading aid
- Do not delete PDFs under any error path
