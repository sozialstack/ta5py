# Tasks: Kostenträger IK Verification (§ 302)

**Input**: Design documents from `specs/ta5py/005-kostentraeger-ik-verify/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included — SC-001/SC-002 require a fixed synthetic suite (≥10 existence cases + recipient expectations) and pytest validation per quickstart.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Library package: `packages/ta5py/src/ta5py/`, tests under `packages/ta5py/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm package layout and ignore rules for Kostenträger cache

- [x] T001 Verify `packages/ta5py/src/ta5py/kostentraeger.py`, `packages/ta5py/tests/`, and synthetic fixture dir `packages/ta5py/tests/fixtures/synthetic/kostentraeger/` exist per plan.md
- [x] T002 [P] Confirm repo `.gitignore` covers Python artifacts and `packages/ta5py/var/kostentraeger/*.ke*` / `store.json` (operator cache)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Typed verification result and store provenance used by all stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `VerificationStatus` / `KostentraegerVerificationResult` (dataclass or equivalent) in `packages/ta5py/src/ta5py/kostentraeger.py` per `specs/ta5py/005-kostentraeger-ik-verify/data-model.md`
- [x] T004 Extend `KostentraegerStore` in `packages/ta5py/src/ta5py/kostentraeger.py` to carry optional provenance (ingested source filenames) and expose it on verify results

**Checkpoint**: Foundation ready — user story implementation can begin

---

## Phase 3: User Story 1 — Confirm card IK exists (Priority: P1) 🎯 MVP

**Goal**: Callers get found / not_found / registry_unavailable for a card IK against the loaded Kostenträgerdatei.

**Independent Test**: Synthetic fixture: `123456789` found; absent IK not found; `store=None` → registry_unavailable.

### Tests for User Story 1

> Write these tests FIRST; they should fail until `verify_kostentraeger_ik` exists.

- [x] T005 [P] [US1] Add existence / unavailable tests (≥10 synthetic card IKs from fixture) in `packages/ta5py/tests/test_kostentraeger_verify.py`

### Implementation for User Story 1

- [x] T006 [US1] Implement `verify_kostentraeger_ik(store, ik)` (module function and/or store method) in `packages/ta5py/src/ta5py/kostentraeger.py` returning found/not_found/registry_unavailable; trim; refuse positive hit for non-nine-digit input
- [x] T007 [US1] Re-export `verify_kostentraeger_ik`, `KostentraegerVerificationResult`, and related types from `packages/ta5py/src/ta5py/__init__.py`

**Checkpoint**: User Story 1 fully functional and testable independently

---

## Phase 4: User Story 2 — Resolve § 302 recipient IK (Priority: P1)

**Goal**: When found, surface selected acceptance/billing recipient IK (or undetermined); never invent recipients.

**Independent Test**: Fixture `123456789` → recipient `111222333`; entry without usable VKG → found + recipient undetermined; absent IK → no recipient.

### Tests for User Story 2

- [x] T008 [P] [US2] Add recipient-resolution tests (linked, undetermined, absent) in `packages/ta5py/tests/test_kostentraeger_verify.py`; add synthetic no-link fixture under `packages/ta5py/tests/fixtures/synthetic/kostentraeger/` if needed
- [x] T009 [P] [US2] Add `resolve_acceptance_ik` convenience tests in `packages/ta5py/tests/test_kostentraeger_verify.py`

### Implementation for User Story 2

- [x] T010 [US2] Populate `recipient_ik` / `recipient_determined` and entry metadata on `KostentraegerVerificationResult` in `packages/ta5py/src/ta5py/kostentraeger.py` from store `acceptance_ik` (empty ⇒ undetermined)
- [x] T011 [US2] Implement `resolve_acceptance_ik(store, ik) -> str | None` in `packages/ta5py/src/ta5py/kostentraeger.py` and export from `packages/ta5py/src/ta5py/__init__.py`

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 — Official file as source of truth (Priority: P2)

**Goal**: Verification tracks the loaded edition; docs name GKV-Spitzenverband / gkv-datenaustausch.de; download remains operator refresh.

**Independent Test**: Edition E1 finds IK X; edition E2 without X does not; no hard-coded allow-list.

### Tests for User Story 3

- [x] T012 [P] [US3] Add edition-swap test (second synthetic EDIFACT without a formerly present IK) in `packages/ta5py/tests/test_kostentraeger_verify.py` using `packages/ta5py/tests/fixtures/synthetic/kostentraeger/`

### Implementation for User Story 3

- [x] T013 [US3] Ensure multi-file ingest stamps `source` and store provenance is returned on verify in `packages/ta5py/src/ta5py/kostentraeger.py`
- [x] T014 [P] [US3] Document official source + download/ingest refresh in `packages/ta5py/README.md` and confirm `packages/ta5py/var/kostentraeger/README.md` names gkv-datenaustausch.de

**Checkpoint**: User Stories 1–3 independently functional

---

## Phase 6: User Story 4 — Formal shape vs registry truth (Priority: P3)

**Goal**: Formally valid but unlisted IK is not found; docs state registry hit ≠ Testat.

**Independent Test**: Formally valid synthetic IK absent from store → not_found; German/English docs distinguish formal / registry / Testat.

### Tests for User Story 4

- [x] T015 [P] [US4] Assert formally valid (`is_valid_ik`) but unlisted IK yields `not_found` in `packages/ta5py/tests/test_kostentraeger_verify.py`

### Implementation for User Story 4

- [x] T016 [P] [US4] Add German companion `packages/ta5py/docs/de/kostentraeger-ik.md` (registry vs formal vs Testat; § 302 addressing) and link from `packages/ta5py/docs/de/README.md` / `packages/ta5py/docs/de/ik.md`
- [x] T017 [US4] Note in `packages/ta5py/src/ta5py/kostentraeger.py` module docstring that verify does not perform Prüfziffer checks and does not claim Testat

**Checkpoint**: All user stories independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story docs and validation

- [x] T018 [P] Align English README section with contract names (`verify_kostentraeger_ik`, `resolve_acceptance_ik`) in `packages/ta5py/README.md`
- [x] T019 Run quickstart validation: `uv run pytest packages/ta5py/tests/test_kostentraeger_lookup.py packages/ta5py/tests/test_kostentraeger_verify.py -q`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–6)**: Depend on Foundational; US1 → US2 share result type; US3/US4 can follow once verify exists
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — MVP
- **US2 (P1)**: After US1 verify skeleton (extends same result)
- **US3 (P2)**: After US1 (edition swap uses verify)
- **US4 (P3)**: After US1 (compose with `is_valid_ik`)

### Parallel Opportunities

- T002 with T001; T005 with fixture prep; T008/T009; T012/T014/T015/T016 once verify exists

### Parallel Example: User Story 2

```bash
Task: "Add recipient-resolution tests in packages/ta5py/tests/test_kostentraeger_verify.py"
Task: "Add resolve_acceptance_ik tests in packages/ta5py/tests/test_kostentraeger_verify.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Setup + Foundational
2. US1 verify existence / unavailable
3. Stop and validate with pytest

### Incremental Delivery

1. US1 existence → US2 recipient → US3 edition/docs → US4 formal boundary → polish

---

## Notes

- Do not merge formal Prüfziffer into verify; compose via `ta5py.ik` in tests/docs only
- Synthetic fixtures only; never commit live `.ke*` files
- Existing `lookup` remains; prefer verify for § 302 semantics
