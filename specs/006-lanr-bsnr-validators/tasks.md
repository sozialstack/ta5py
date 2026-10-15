# Tasks: LANR and BSNR Formal Validators

**Input**: Design documents from `specs/ta5py/006-lanr-bsnr-validators/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included — SC-001/SC-002 / quickstart require fixed synthetic suites and pytest validation; TDD mirrors `004-ik-validator`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Library package: `packages/ta5py/src/ta5py/`, tests under `packages/ta5py/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm package layout for the new modules and tests

- [x] T001 Verify `packages/ta5py/src/ta5py/` and `packages/ta5py/tests/` exist per plan.md; create placeholders only if missing
- [x] T002 [P] Confirm `.gitignore` covers Python artifacts (`__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `*.egg-info/`) at repo root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Domain error types and LANR Prüfziffer helper shared by LANR stories; BSNR module skeleton for structure-only checks

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `LanrError` and `Lanr` frozen value-type skeleton with `compute_check_digit(body6)` (weights 4,9,4,9,4,9; `(10 - sum % 10) % 10`) in `packages/ta5py/src/ta5py/lanr.py`
- [x] T004 [P] Add `BsnrError` and `Bsnr` frozen value-type skeleton (`kv_region` / `site` parts) in `packages/ta5py/src/ta5py/bsnr.py`

**Checkpoint**: Foundation ready — user story implementation can begin

---

## Phase 3: User Story 1 — Formal nine-digit LANR validity (Priority: P1) 🎯 MVP

**Goal**: Callers get a clear yes/no formal check for a nine-digit LANR (structure + Prüfziffer).

**Independent Test**: `123456601` valid, `123456901` invalid; bad length/non-digits invalid; ≥8 synthetic LANR cases in suite.

### Tests for User Story 1

> Write these tests FIRST; they should fail until `Lanr.is_valid` / `parse` exist.

- [x] T005 [P] [US1] Add synthetic LANR suite (≥8 nine-digit cases including `123456601`/`123456901`) and `Lanr` parse / `is_valid` / `compute_check_digit` tests in `packages/ta5py/tests/test_lanr.py`

### Implementation for User Story 1

- [x] T006 [US1] Implement `Lanr.parse`, `is_formally_valid`, and `Lanr.is_valid` in `packages/ta5py/src/ta5py/lanr.py` (trim; exactly nine digits; Prüfziffer via `compute_check_digit`; `is_valid` returns False on bad structure)
- [x] T007 [US1] Document KBV Arztnummern-Richtlinie citation and formal≠assignment disclaimer in module docstring of `packages/ta5py/src/ta5py/lanr.py`

**Checkpoint**: User Story 1 fully functional and testable independently

---

## Phase 4: User Story 2 — Formal nine-digit BSNR structure (Priority: P1)

**Goal**: Callers get a clear yes/no formal structure check for a nine-digit BSNR (no Prüfziffer).

**Independent Test**: Synthetic `031234567` valid; wrong length / non-digits invalid; ≥6 synthetic BSNR cases; docs/API state no public Prüfziffer.

### Tests for User Story 2

- [x] T008 [P] [US2] Add synthetic BSNR suite (≥6 cases) and `Bsnr` parse / `is_valid` tests in `packages/ta5py/tests/test_bsnr.py`

### Implementation for User Story 2

- [x] T009 [US2] Implement `Bsnr.parse`, `is_formally_valid` (True when parsed), and `Bsnr.is_valid` in `packages/ta5py/src/ta5py/bsnr.py` (trim; exactly nine digits; no Prüfziffer; no KV-prefix reject)
- [x] T010 [US2] Document structure-only formal check (no public Prüfziffer) in module docstring of `packages/ta5py/src/ta5py/bsnr.py`

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 — Reuse shared entry points (Priority: P1)

**Goal**: One public package export for `Lanr` and `Bsnr` so callers do not reimplement checks (same pattern as `Ik`).

**Independent Test**: Importing from `ta5py` and `ta5py.lanr` / `ta5py.bsnr` yields identical outcomes on the synthetic suites.

### Tests for User Story 3

- [x] T011 [P] [US3] Assert `ta5py.Lanr` / `ta5py.Bsnr` agree with module exports on synthetic suites in `packages/ta5py/tests/test_lanr.py` and `packages/ta5py/tests/test_bsnr.py`

### Implementation for User Story 3

- [x] T012 [US3] Re-export `Lanr`, `LanrError`, `Bsnr`, `BsnrError` from `packages/ta5py/src/ta5py/__init__.py` and update `__all__`
- [x] T013 [P] [US3] Mention the shared LANR/BSNR formal validators in `packages/ta5py/README.md` (English; link to German companions when present)

**Checkpoint**: User Stories 1–3 independently functional

---

## Phase 6: User Story 4 — Formal OK ≠ assignment / Testat docs (Priority: P2)

**Goal**: Operators understand formal LANR/BSNR checks do not prove assignment, specialty correctness, or Testat; specialty/KV catalogs are separate policies.

**Independent Test**: Arbitrary specialty on valid LANR still passes; non-curated BSNR prefix still passes; German/English docs state limits.

### Tests for User Story 4

- [x] T014 [P] [US4] Assert formally valid LANR with specialty `99` and BSNR with uncommon prefix remain valid via default checks in `packages/ta5py/tests/test_lanr.py` and `packages/ta5py/tests/test_bsnr.py`

### Implementation for User Story 4

- [x] T015 [P] [US4] Add German companion notes in `packages/ta5py/docs/de/lanr.md` and `packages/ta5py/docs/de/bsnr.md`; link from `packages/ta5py/docs/de/README.md`

**Checkpoint**: All user stories independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation against quickstart and typing

- [x] T016 [P] Run `uv run pytest packages/ta5py/tests/test_lanr.py packages/ta5py/tests/test_bsnr.py -q` and fix failures
- [x] T017 [P] Run quickstart smoke (`from ta5py import Lanr, Bsnr; …`) per `specs/ta5py/006-lanr-bsnr-validators/quickstart.md`
- [x] T018 Confirm public APIs in `packages/ta5py/src/ta5py/lanr.py` and `packages/ta5py/src/ta5py/bsnr.py` are fully type-annotated (Principle VII)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on Foundational (T004); independent of US1 code
- **US3 (Phase 5)**: Depends on US1 + US2 public APIs
- **US4 (Phase 6)**: Depends on US1 + US2; docs can parallelize with US3
- **Polish (Phase 7)**: Depends on desired stories complete

### User Story Dependencies

- **US1 (P1)**: After Foundational (T003) — no other story deps
- **US2 (P1)**: After Foundational (T004) — parallel with US1
- **US3 (P1)**: After US1 + US2 APIs exist
- **US4 (P2)**: After US1 + US2; docs independent of US3 export timing once modules exist

### Parallel Opportunities

- T002 parallel with T001
- T003 / T004 parallel (different files)
- T005 / T008 parallel after foundation
- T006 / T009 parallel after their tests
- T011 / T013 / T014 / T015 parallel after APIs exist
- T016 / T017 parallel in polish

---

## Parallel Example: User Stories 1 and 2

```bash
# After T003–T004 foundation:
Task: "Add synthetic LANR suite in packages/ta5py/tests/test_lanr.py"
Task: "Add synthetic BSNR suite in packages/ta5py/tests/test_bsnr.py"
# Then implement in parallel:
Task: "Implement Lanr.parse / is_valid in packages/ta5py/src/ta5py/lanr.py"
Task: "Implement Bsnr.parse / is_valid in packages/ta5py/src/ta5py/bsnr.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup → Phase 2 Foundational
2. Phase 3 US1 (`Lanr` + suite)
3. **STOP and VALIDATE** with KBV-style `123456601` / `123456901`

### Incremental Delivery

1. Setup + Foundational
2. US1 → LANR formal check MVP
3. US2 → BSNR structure check (parallelizable with US1)
4. US3 → package re-exports / README
5. US4 → German companion docs + non-catalog tests
6. Polish / quickstart

---

## Notes

- Synthetic LANR/BSNR only (Principle IV)
- Default formal checks MUST NOT enforce specialty or KV-prefix catalogs
- BSNR has no public Prüfziffer — structure only
- dtapy must not import ta5py — out of scope for reuse
- Commit after each logical group if requested by user
