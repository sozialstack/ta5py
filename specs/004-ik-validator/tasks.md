# Tasks: Institutskennung (IK) Formal Validator

**Input**: Design documents from `specs/ta5py/004-ik-validator/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included — SC-001 / quickstart require a fixed synthetic suite (≥10 cases) and pytest validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Library package: `packages/ta5py/src/ta5py/`, tests under `packages/ta5py/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm package layout for the new module and tests

- [x] T001 Verify `packages/ta5py/src/ta5py/` and `packages/ta5py/tests/` exist per plan.md; create placeholders only if missing
- [x] T002 [P] Confirm `.gitignore` covers Python artifacts (`__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `*.egg-info/`) at repo root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared Prüfziffer algorithm and domain error type used by all stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `IkError` (or equivalent typed domain error) and private Prüfziffer helper over positions 3–8 (weights 2,1,2,1,2,1; subtract 9 if product > 9; sum mod 10) in `packages/ta5py/src/ta5py/ik.py`
- [x] T004 Implement `ik_check_digit(body8: str) -> str` in `packages/ta5py/src/ta5py/ik.py` (trim; require eight digits; raise `IkError` on bad input; return single check-digit character)

**Checkpoint**: Foundation ready — user story implementation can begin

---

## Phase 3: User Story 1 — Formal nine-digit IK validity (Priority: P1) 🎯 MVP

**Goal**: Callers get a clear yes/no formal check for a nine-digit IK (structure + Prüfziffer).

**Independent Test**: `260326822` valid, `260326823` invalid; bad length/non-digits invalid; ≥10 synthetic cases in suite.

### Tests for User Story 1

> Write these tests FIRST; they should fail until `is_valid_ik` exists.

- [x] T005 [P] [US1] Add synthetic suite (≥10 nine-digit cases including `260326822`/`260326823`) and `is_valid_ik` / `ik_check_digit` tests in `packages/ta5py/tests/test_ik.py`

### Implementation for User Story 1

- [x] T006 [US1] Implement `is_valid_ik(ik: str) -> bool` in `packages/ta5py/src/ta5py/ik.py` (trim; exactly nine digits; Prüfziffer via shared helper; no exceptions for ordinary invalid input)
- [x] T007 [US1] Document algorithm citation (Gemeinsames Rundschreiben IK / Wikipedia) and formal≠registry disclaimer in module docstring of `packages/ta5py/src/ta5py/ik.py`

**Checkpoint**: User Story 1 fully functional and testable independently

---

## Phase 4: User Story 2 — Reuse shared entry point (Priority: P1)

**Goal**: One public package export so callers do not reimplement check digits.

**Independent Test**: Importing from `ta5py` and `ta5py.ik` yields identical outcomes on the synthetic suite.

### Tests for User Story 2

- [x] T008 [P] [US2] Assert `ta5py.is_valid_ik` and `ta5py.ik.is_valid_ik` agree on the synthetic suite in `packages/ta5py/tests/test_ik.py`

### Implementation for User Story 2

- [x] T009 [US2] Re-export `is_valid_ik`, `ik_check_digit` (and later `expand_kassennummer`) from `packages/ta5py/src/ta5py/__init__.py` and update `__all__`
- [x] T010 [P] [US2] Mention the shared IK formal validator in `packages/ta5py/README.md` (English; link to German companion when present)

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 — Seven-digit Kassennummer expansion (Priority: P2)

**Goal**: Expand exactly seven-digit Kassennummer with prefix `10`, then validate with the same formal check.

**Independent Test**: Expansion of a synthetic seven-digit value equals `10` + digits; non-seven-digit input refused; `is_valid_ik` on result follows Prüfziffer.

### Tests for User Story 3

- [x] T011 [P] [US3] Add `expand_kassennummer` tests (happy path, refuse non-7-digit, compose with `is_valid_ik`) in `packages/ta5py/tests/test_ik.py`

### Implementation for User Story 3

- [x] T012 [US3] Implement `expand_kassennummer(kassennummer: str) -> str` in `packages/ta5py/src/ta5py/ik.py` (trim; exactly seven digits or raise `IkError`; return `"10" + digits`; do not assert Prüfziffer)
- [x] T013 [US3] Ensure `expand_kassennummer` is exported from `packages/ta5py/src/ta5py/__init__.py`

**Checkpoint**: User Stories 1–3 independently functional

---

## Phase 6: User Story 4 — Ersatzkennzeichen documentation (Priority: P3)

**Goal**: Operators understand Ersatzkennzeichen can pass the default formal check; exclusion is a separate policy.

**Independent Test**: Synthetic `970000011` / `970000099` formally valid; German/English docs state exclusion is not default.

### Tests for User Story 4

- [x] T014 [P] [US4] Assert Ersatzkennzeichen `970000011` and `970000099` are formally valid via default `is_valid_ik` in `packages/ta5py/tests/test_ik.py`

### Implementation for User Story 4

- [x] T015 [P] [US4] Add German companion note (formal vs registry / Testat; Ersatzkennzeichen not excluded by default) in `packages/ta5py/docs/de/ik.md` and link from `packages/ta5py/docs/de/README.md`

**Checkpoint**: All user stories independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation against quickstart and typing

- [x] T016 [P] Run `uv run pytest packages/ta5py/tests/test_ik.py -q` and fix failures
- [x] T017 [P] Run quickstart smoke (`from ta5py import is_valid_ik; …`) per `specs/ta5py/004-ik-validator/quickstart.md`
- [x] T018 Confirm public functions in `packages/ta5py/src/ta5py/ik.py` are fully type-annotated (Principle VII)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on US1 implementation (`is_valid_ik` exists)
- **US3 (Phase 5)**: Depends on Foundational + US1 (`is_valid_ik` for composition tests); can start after T006
- **US4 (Phase 6)**: Depends on US1 (`is_valid_ik`); docs can parallelize with US3
- **Polish (Phase 7)**: Depends on desired stories complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no other story deps
- **US2 (P1)**: After US1 public API exists
- **US3 (P2)**: After Foundational; composition with `is_valid_ik` after T006
- **US4 (P3)**: After `is_valid_ik`; docs independent of US3 code

### Parallel Opportunities

- T002 parallel with T001
- T005 before/alongside T006 (TDD)
- T008 / T010 parallel after export
- T011 parallel with T014 once `is_valid_ik` works
- T015 parallel with US3 implementation
- T016 / T017 parallel in polish

---

## Parallel Example: User Story 1

```bash
# After T003–T004 foundation:
Task: "Add synthetic suite and is_valid_ik tests in packages/ta5py/tests/test_ik.py"
# Then implement:
Task: "Implement is_valid_ik in packages/ta5py/src/ta5py/ik.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup → Phase 2 Foundational
2. Phase 3 US1 (`is_valid_ik` + suite)
3. **STOP and VALIDATE** with Wikipedia example cases

### Incremental Delivery

1. Setup + Foundational
2. US1 → formal check MVP
3. US2 → package re-exports / README
4. US3 → Kassennummer expansion
5. US4 → Ersatzkennzeichen docs + tests
6. Polish / quickstart

---

## Notes

- Synthetic IKs only (Principle IV)
- Default formal check MUST NOT exclude Ersatzkennzeichen
- dtapy must not import ta5py — out of scope for reuse
- Commit after each logical group if requested by user
