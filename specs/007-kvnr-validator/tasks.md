# Tasks: Krankenversichertennummer Formal Validator

**Input**: Design documents from `specs/ta5py/007-kvnr-validator/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — SC-001 / quickstart require a fixed synthetic suite and pytest validation; TDD mirrors `004-ik-validator` and `006-lanr-bsnr-validators`.

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

**Purpose**: Domain error type and KVNR Prüfziffer helper shared by every story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `KvnrError` and `Kvnr` frozen value-type skeleton with `compute_check_digit(body9)` (letter → `01`–`26`; weights `1,2,…`; Quersumme; sum modulo 10) in `packages/ta5py/src/ta5py/kvnr.py`

**Checkpoint**: Foundation ready — user story implementation can begin

---

## Phase 3: User Story 1 — Formal 10-character KVNR validity (Priority: P1) 🎯 MVP

**Goal**: Callers get a clear yes/no formal check for the 10-character unchanging insuree number (structure + Prüfziffer).

**Independent Test**: `A000500015` valid, `A000500016` invalid; lowercase and trim accepted; bad length/non-letters invalid; ≥8 synthetic cases; `A000000002` valid (not the complement digit `8`).

### Tests for User Story 1

> Write these tests FIRST; they should fail until `Kvnr.is_valid` / `parse` exist.

- [x] T004 [P] [US1] Add synthetic KVNR suite (≥8 cases including `A000500015`/`A000500016`/`A000000002`/`C000500021`) and `Kvnr` parse / `is_valid` / `compute_check_digit` tests in `packages/ta5py/tests/test_kvnr.py`

### Implementation for User Story 1

- [x] T005 [US1] Implement `Kvnr.parse`, `is_formally_valid`, and `Kvnr.is_valid` in `packages/ta5py/src/ta5py/kvnr.py` (trim; case-fold leading letter; exactly one letter plus nine digits; Prüfziffer via `compute_check_digit`; `is_valid` returns False on bad structure)
- [x] T006 [US1] Document § 290 Anlage 1 citation, sum-modulo-10 (not complement-to-10), and formal≠issued/insured disclaimer in the module docstring of `packages/ta5py/src/ta5py/kvnr.py`

**Checkpoint**: User Story 1 fully functional and testable independently

---

## Phase 4: User Story 2 — Reuse one shared entry point (Priority: P1)

**Goal**: One public package export for `Kvnr` so callers do not reimplement the check (same pattern as `Ik` / `Lanr`).

**Independent Test**: Importing from `ta5py` and `ta5py.kvnr` yields identical outcomes on the synthetic suite.

### Tests for User Story 2

- [x] T007 [US2] Assert `ta5py.Kvnr` agrees with `ta5py.kvnr.Kvnr` on the synthetic suite in `packages/ta5py/tests/test_kvnr.py`

### Implementation for User Story 2

- [x] T008 [US2] Re-export `Kvnr` and `KvnrError` from `packages/ta5py/src/ta5py/__init__.py` and update `__all__`
- [x] T009 [P] [US2] Mention the shared KVNR formal validator in `packages/ta5py/README.md` (English; link to the German companion)

**Checkpoint**: User Stories 1 and 2 independently functional

---

## Phase 5: User Story 3 — Formal OK ≠ issued / insured / Testat (Priority: P2)

**Goal**: Operators understand the check covers only the 10-character card number, does not apply issuance bans, and does not change the TA5 Versicherten-Nummer field.

**Independent Test**: A value with `666` or a long identical-digit run still passes when the Prüfziffer is correct; a 20-character form fails; `INV.versicherten_id` stays max length 12; German/English docs state the limits.

### Tests for User Story 3

- [x] T010 [US3] Assert issuance-shaped synthetics (`M000066602`, `K111111115`) stay valid, the 20-character form is invalid, and `versicherten_id` remains `max_length: 12` in `packages/ta5py/spec/v21/segments/INV.yaml` and `packages/ta5py/spec/v22/segments/INV.yaml`, in `packages/ta5py/tests/test_kvnr.py`

### Implementation for User Story 3

- [x] T011 [P] [US3] Add the German companion note in `packages/ta5py/docs/de/kvnr.md` and link it from `packages/ta5py/docs/de/README.md`

**Checkpoint**: All user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation against quickstart and typing

- [x] T012 [P] Run `uv run pytest packages/ta5py/tests/test_kvnr.py -q` and fix failures
- [x] T013 [P] Run quickstart smoke (`from ta5py import Kvnr; …`) per `specs/ta5py/007-kvnr-validator/quickstart.md`
- [x] T014 Confirm the public API in `packages/ta5py/src/ta5py/kvnr.py` is fully type-annotated (Principle VII)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on US1 public API (`parse` / `is_valid`)
- **US3 (Phase 5)**: Depends on US1; docs can proceed once the module exists
- **Polish (Phase 6)**: Depends on desired stories complete

### User Story Dependencies

- **US1 (P1)**: After Foundational (T003) — no other story deps
- **US2 (P1)**: After US1 — package re-export of the same type
- **US3 (P2)**: After US1; German note independent of the package re-export

### Parallel Opportunities

- T002 parallel with T001
- T004 parallel with other files once T003 exists (tests fail until T005)
- T009 parallel with T008 (different files)
- T011 parallel with T010 once `kvnr.py` exists (different files)
- T012 / T013 parallel in polish after tests and exports exist

---

## Parallel Example: User Story 2

```bash
# After Kvnr.is_valid exists:
Task: "Re-export Kvnr from packages/ta5py/src/ta5py/__init__.py"
Task: "Mention KVNR validator in packages/ta5py/README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup → Phase 2 Foundational
2. Phase 3 US1 (`Kvnr` + suite)
3. **STOP and VALIDATE** with `A000500015` / `A000500016` and `A000000002`

### Incremental Delivery

1. Setup + Foundational
2. US1 → 10-character formal check MVP
3. US2 → package re-export / README
4. US3 → limits tests + German companion
5. Polish / quickstart

---

## Notes

- Synthetic KVNR only, plus the published Anlage 1 illustration `A000500015` (Principle IV)
- Check digit is sum modulo 10, not complement-to-10
- Do not enforce issuance bans (`666`, runs of more than three identical digits)
- Do not validate 20- or 30-character Gesamtsystem numbers
- Do not change `INV.versicherten_id` syntax
- dtapy must not import ta5py — out of scope for reuse
- Commit after each logical group if requested by the user
