# Tasks: Automatic Format Spec Detection & Integration

**Input**: Design documents from `specs/ta5py/002-auto-spec-integration/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — Success Criteria SC-001–SC-006 and Independent Tests require fixture-based verification (including negative go-live gate).

**Organization**: Phased by user story. **MVP = Phase 1–3 (Setup + Foundation + US1 Detect)**. Full P1 = US1+US2+US3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Maps to user stories in spec.md (US1–US4)
- Exact file paths required in every task

## Path Conventions

- Spec Kit docs: `specs/ta5py/002-auto-spec-integration/`
- Format code: `packages/ta5py/src/format/`
- Governance package: `packages/ta5py/src/format/governance/`
- Scripts: `packages/ta5py/scripts/`
- Governance state: `packages/ta5py/spec/governance/`
- Tests: `packages/ta5py/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Governance directories, fixtures, and package skeleton

- [x] T001 Create governance directories `packages/ta5py/spec/governance/{detections,candidates}/` and placeholder `packages/ta5py/spec/governance/README.md` describing live binding + audit files (no Sozialdaten)
- [x] T002 [P] Create test fixture dirs and files `packages/ta5py/tests/fixtures/governance/sources_known.yaml`, `packages/ta5py/tests/fixtures/governance/sources_with_new_version.yaml`, and `packages/ta5py/tests/fixtures/governance/overview_snapshot.html`
- [x] T003 [P] Add empty package init `packages/ta5py/src/format/governance/__init__.py` exporting public governance API surface (filled in later phases)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared models, paths, live-version binding loader — MUST complete before user stories

**⚠️ CRITICAL**: No user story work until this phase completes

- [x] T004 Implement governance dataclasses/models in `packages/ta5py/src/format/governance/models.py` (OfficialPublication, DetectionRun, IntegrationCandidate, ApprovalDecision, LiveVersionBinding) per `data-model.md`
- [x] T005 [P] Implement governance path helpers + YAML read/write in `packages/ta5py/src/format/governance/store.py` under `packages/ta5py/spec/governance/`
- [x] T006 Create initial `packages/ta5py/spec/governance/live-version.yaml` binding to `v21` with bootstrap actor `bootstrap` and note that future changes require approval
- [x] T007 Update `packages/ta5py/src/format/spec_loader.py` so `DEFAULT_VERSION` / default package resolution reads `live-version.yaml` (fallback `v21` if missing); clear `load_package` cache on binding change helpers
- [x] T008 [P] Copy/adapt JSON schema validation helper for governance state against `specs/ta5py/002-auto-spec-integration/contracts/governance-state.schema.json` in `packages/ta5py/src/format/governance/validate_state.py`
- [x] T009 Add allowlist constant for in-scope buckets (`anlage-1`, `anlage-3`, `anlage-5`, `anhang-3`) in `packages/ta5py/src/format/governance/scope.py`

**Checkpoint**: Live binding loads; models/store ready — US1 can start

---

## Phase 3: User Story 1 - Detect newly published format specs (Priority: P1) 🎯 MVP

**Goal**: On-demand/fixture detection of new/changed in-scope publications with durable DetectionRun records

**Independent Test**: Run check against `sources_with_new_version.yaml` fixture → new ids reported; re-run known fixture → no new work items; out-of-scope marked ignored

### Tests for User Story 1

- [x] T010 [P] [US1] Add failing tests in `packages/ta5py/tests/test_publication_detect.py` for new-version detection, no-change, out-of-scope, and unreachable/failed check

### Implementation for User Story 1

- [x] T011 [US1] Implement publication catalog load/compare in `packages/ta5py/src/format/governance/detect.py` (manifest vs discovered; classify in/out of scope)
- [x] T012 [US1] Persist DetectionRun YAML under `packages/ta5py/spec/governance/detections/` and create `detected` candidate stubs for new in-scope package labels without duplicating open candidates
- [x] T013 [US1] Implement CLI `packages/ta5py/scripts/check_official_publications.py` (`--fixture`, `--json`) per `contracts/format-spec-governance-cli.md`
- [x] T014 [US1] Make `packages/ta5py/tests/test_publication_detect.py` pass against fixtures (no live network)

**Checkpoint**: US1 MVP — detection works offline via fixtures

---

## Phase 4: User Story 2 - Automatically prepare integration on a new branch (Priority: P1)

**Goal**: Scaffold `spec/vN/` on a new git branch without changing live default

**Independent Test**: Integrate synthetic candidate → new branch + package tree + change summary; live-version unchanged

### Tests for User Story 2

- [x] T015 [P] [US2] Add failing tests in `packages/ta5py/tests/test_integrate_on_branch.py` for branch creation, scaffold presence, live unchanged, duplicate refusal, dry-run

### Implementation for User Story 2

- [x] T016 [US2] Implement package scaffold + change summary writer in `packages/ta5py/src/format/governance/integrate.py` (copy base package tree to `packages/ta5py/spec/vN/`, update provenance placeholders, write `CHANGE_SUMMARY.md`)
- [x] T017 [US2] Implement git branch create/checkout helper in `packages/ta5py/src/format/governance/gitops.py` (subprocess git; branch name `format/spec-v{N}-integration`)
- [x] T018 [US2] Wire integrate flow: state `integrating` → scaffold → `awaiting_approval`; never touch `live-version.yaml`
- [x] T019 [US2] Implement CLI `packages/ta5py/scripts/integrate_spec_candidate.py` (`--candidate`, `--from-latest-new`, `--base-package`, `--dry-run`)
- [x] T020 [US2] Make `packages/ta5py/tests/test_integrate_on_branch.py` pass (use temp git repo or dry-run + isolated SPEC_ROOT override as appropriate)

**Checkpoint**: US2 — branch scaffold ready for human review; default still prior live

---

## Phase 5: User Story 3 - Strict human approval before go-live (Priority: P1)

**Goal**: Explicit approve/reject + gated go-live updating live binding and DEFAULT_VERSION

**Independent Test**: Go-live without approve fails; approve+go-live succeeds and is auditable; unapproved sibling stays non-live

### Tests for User Story 3

- [x] T021 [P] [US3] Add failing tests in `packages/ta5py/tests/test_approve_live_gate.py` for unauthorized go-live, approve+go-live, reject leaves live unchanged, only approved candidate goes live

### Implementation for User Story 3

- [x] T022 [US3] Implement approval + go-live in `packages/ta5py/src/format/governance/approve.py` (write ApprovalDecision; update `live-version.yaml` only with approve+go-live; validate package loads)
- [x] T023 [US3] Implement CLI `packages/ta5py/scripts/approve_live_spec.py` (`--candidate`, `--actor`, `--approve`/`--reject`, `--go-live`, `--note`)
- [x] T024 [US3] Ensure `spec_loader` reflects new live binding after go-live (cache clear) and encoding defaults follow binding
- [x] T025 [US3] Make `packages/ta5py/tests/test_approve_live_gate.py` pass including SC-003 negative cases

**Checkpoint**: US3 — zero unauthorized go-lives in tests

---

## Phase 6: User Story 4 - Review status of detection and pending integrations (Priority: P2)

**Goal**: Maintainer status view of last check, candidates, live version

**Independent Test**: Seed states → status shows identity, branch, gate state; rejected/out-of-scope distinguishable

### Tests for User Story 4

- [x] T026 [P] [US4] Add failing tests in `packages/ta5py/tests/test_governance_status.py` for pending vs rejected/live rendering and JSON shape

### Implementation for User Story 4

- [x] T027 [US4] Implement status aggregation in `packages/ta5py/src/format/governance/status.py`
- [x] T028 [US4] Implement CLI `packages/ta5py/scripts/governance_status.py` (human table + `--json`)
- [x] T029 [US4] Make `packages/ta5py/tests/test_governance_status.py` pass

**Checkpoint**: US4 — status usable in under 2 minutes (SC-004)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, ignore rules, quickstart validation

- [x] T030 [P] Update `packages/ta5py/README.md` with detection/integrate/approve/status commands and approval-gate warning
- [x] T031 [P] Update `packages/ta5py/spec/official/README.md` with pointer to governance check workflow
- [x] T032 [P] Ensure root `.gitignore` does not ignore committed governance YAML (only PDFs remain ignored under official/)
- [x] T033 Run quickstart validation scenarios from `specs/ta5py/002-auto-spec-integration/quickstart.md` (fixture detect → integrate dry-run/path → unauthorized go-live fail → approve go-live) and fix gaps
- [x] T034 [P] Export governance public API from `packages/ta5py/src/format/governance/__init__.py` and mention in `packages/ta5py/src/format/__init__.py` if appropriate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After Foundational; uses candidates from US1 in full flow but can be tested with seeded candidate files
- **US3 (Phase 5)**: After Foundational; full flow needs US2 candidate in `awaiting_approval`
- **US4 (Phase 6)**: After Foundational; best after US1–US3 state files exist
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

- **US1**: Independent after foundation
- **US2**: Needs candidate records (from US1 or seeded fixtures)
- **US3**: Needs `awaiting_approval` candidate (from US2 or seeded)
- **US4**: Reads all governance state; independently testable with seeded files

### Parallel Opportunities

- T002/T003 after T001 directory exists
- T005/T008/T009 in parallel during foundation
- Test tasks T010, T015, T021, T026 can be authored in parallel before their implementations
- Polish T030/T031/T032/T034 in parallel

### Parallel Example: User Story 1

```bash
# Tests first:
Task: "Add failing tests in packages/ta5py/tests/test_publication_detect.py"

# Then implement detect + CLI sequentially (shared detect.py/store):
Task: "Implement detect.py"
Task: "Persist DetectionRun + candidates"
Task: "CLI check_official_publications.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup
2. Phase 2 Foundational
3. Phase 3 US1 Detect
4. **STOP and VALIDATE** with fixture check

### Incremental Delivery

1. Setup + Foundation
2. US1 Detect → demo
3. US2 Branch integrate → demo
4. US3 Approval gate → demo (full P1)
5. US4 Status → polish

### Suggested MVP scope

**US1 only** (detect + durable records). For this `/speckit-implement` run, deliver **US1–US4 + polish** so the full gated pipeline matches the plan.

---

## Notes

- Never auto-update `live-version.yaml` from detect/integrate
- Git operations only in integrate (and tests that opt into temp repos)
- Synthetic fixtures only — no real Sozialdaten
- PDF field transcription remains human on the integration branch; automation scaffolds only

## Phase 8: Convergence

- [x] T035 Add official-source discovery (manifest/HTML snapshot parse ± optional network) with failed DetectionRun on unreachable/parse error; stop requiring fixture-only for FR-001 / research R2 (partial)
- [x] T036 On integrate, append/adjust packages/ta5py/spec/official/sources.manifest.yaml entries for new publication ids/paths/versions/stand dates on the integration branch per plan / research R3 (missing)
- [x] T037 Before writing live-version.yaml, call load_package(candidate.package_label) (or equivalent) and refuse go-live on validation errors per FR-010 / T022 (partial)
- [x] T038 Abort candidate to failed (block go-live) when package material is incomplete/corrupt; set DetectionStatus.partial where applicable; add SC-006 fault-injection tests per FR-010 / SC-006 (missing)
- [x] T039 On re-detect of rejected/live/failed same-id candidates, link to existing terminal record without overwriting approval/rejection audit history per edge re-detect / FR-008 / FR-011 (contradicts)
- [x] T040 Auto-start integrate after detection (or --auto-integrate / documented CI chain that scaffolds on the new branch) per FR-004 / US2 (partial)
- [x] T041 Compare numeric package labels and require explicit confirmation/warning when activating an older package over a newer live binding per edge go-live older over newer (missing)
- [x] T042 Surface out_of_scope_ids / OOS gate state distinctly in governance status human+JSON output per US4/AC2 / FR-009 (partial)
- [x] T043 Write CHANGE_SUMMARY.md with detected publication deltas vs prior known version (stand dates, filenames, catalog/field notes) per US2/AC2 / research R3 (partial)
- [x] T044 Extend sources.manifest.yaml (or governance store) with last-check / ETag / check metadata as planned (missing)
- [x] T045 Align governance CLI flags/exit codes with contracts/format-spec-governance-cli.md (--on-demand; duplicate integrate exit 3) (partial)
- [x] T046 Validate governance payloads against contracts/governance-state.schema.json (or document and enforce intentional subset) per T008 (partial)

## Phase 9: Convergence

- [x] T047 Make post-detect branch integrate the default for periodic/scheduled detection (keep an explicit detect-only opt-out), leaving live binding unchanged, per FR-004 / US2 / residual T040 (partial)
- [x] T048 Document a concrete daily scheduled check recipe (and optionally add workflow `schedule:`) that runs detection with auto-integrate per FR-001 / Assumptions detection cadence (partial)
- [x] T049 Add governance gate tests (`test_publication_detect.py`, `test_integrate_on_branch.py`, `test_approve_live_gate.py`, `test_governance_status.py`) to CI Focused pytest per SC-002…SC-006 (partial)
