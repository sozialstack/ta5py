# Tasks: Ambulance GKV Anlagen Machine-Readable Specs

**Input**: Design documents from `specs/gkv-edi/001-gkv-anlagen-specs/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included where needed to prove Independent Test / Success Criteria (synthetic fixtures only).

**Organization**: Phased by user story. **MVP = Phase 1–3 (Setup + Foundation + US1 Anlage 1)**. User directive: download official PDFs into `packages/gkv-edi/spec/`; **start implementation with Anlage 1**.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Maps to user stories in spec.md (US1–US6)
- Exact file paths required in every task

## Path Conventions

- Spec Kit docs: `specs/gkv-edi/001-gkv-anlagen-specs/`
- Runtime packages: `packages/gkv-edi/spec/vN/`
- Official PDF sources: `packages/gkv-edi/spec/official/`
- Format code: `packages/gkv-edi/src/format/`
- Format tests: `packages/gkv-edi/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Directories, dependency, and official-source layout under `packages/gkv-edi/spec/`

- [x] T001 Create official PDF source tree `packages/gkv-edi/spec/official/{anlage-1,anlage-3,anlage-5,anhang-3}/` and empty `packages/gkv-edi/spec/official/README.md` documenting that PDFs are authoritative GKV publications (not project IP)
- [x] T002 [P] Create machine-readable package skeleton dirs `packages/gkv-edi/spec/v21/{messages,segments,catalogs}/` and leave stub note in `packages/gkv-edi/spec/v21/catalogs/README.md` (Slice B)
- [x] T003 [P] Add PyYAML dependency to `packages/gkv-edi/pyproject.toml` and sync via root `uv sync --group dev`
- [x] T004 [P] Add `packages/gkv-edi/spec/official/**/*.pdf` to root `.gitignore` (keep manifest + README tracked; PDFs fetched locally/CI)
- [x] T005 Write URL manifest `packages/gkv-edi/spec/official/sources.manifest.yaml` listing base `https://www.gkv-datenaustausch.de` and relative paths for: Anlage 1 v21 (`…/technische_anlagen_aktuell_4/Anlage_1_TP5_V21_20260115.pdf`), Anlage 1 v22 (`…/Anlage_1_TP5_V22_20260521.pdf`), Anlage 3 v21 (`…/Anlage_3_TP5_V21_20250919.pdf`), Anlage 3 v22 (`…/Anlage_3_TP5_V22_20260521.pdf`), Anlage 5 (`…/Anlage_5_TP5_V4_0_20180927.pdf`), Anhang 3 latest (`…/Anhang_03_Anlage_1_TP5_V10_20260414.pdf`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Download official PDFs into `packages/gkv-edi/spec/` and build shared loaders/wire helpers before any user story

**⚠️ CRITICAL**: No user story work until this phase completes

- [x] T006 Create download script `packages/gkv-edi/scripts/download_official_pdfs.py` that reads `packages/gkv-edi/spec/official/sources.manifest.yaml` and writes PDFs into the matching `packages/gkv-edi/spec/official/<bucket>/` folders (idempotent, verify non-empty PDF magic `%PDF`)
- [x] T007 Run `uv run python packages/gkv-edi/scripts/download_official_pdfs.py` so these files exist under `packages/gkv-edi/spec/official/`: `anlage-1/Anlage_1_TP5_V21_20260115.pdf`, `anlage-1/Anlage_1_TP5_V22_20260521.pdf`, `anlage-3/Anlage_3_TP5_V21_20250919.pdf`, `anlage-3/Anlage_3_TP5_V22_20260521.pdf`, `anlage-5/Anlage_5_TP5_V4_0_20180927.pdf`, `anhang-3/Anhang_03_Anlage_1_TP5_V10_20260414.pdf`
- [x] T008 [P] Document download + citation rules in `packages/gkv-edi/spec/official/README.md` (source overview URL, ambulance-only transcription rule, PDF wins on conflict)
- [x] T009 [P] Add Makefile or script target `scripts/download-format-pdfs` (or root `Makefile` target) invoking `packages/gkv-edi/scripts/download_official_pdfs.py`
- [x] T010 Implement package loader foundation in `packages/gkv-edi/src/format/spec_loader.py` to load version roots under `packages/gkv-edi/spec/vN/` (replace stub-only `dataset.schema.json` path assumption)
- [x] T011 [P] Implement UNA separators + escape/unescape helpers in `packages/gkv-edi/src/format/wire.py`
- [x] T012 [P] Add package layout validator against `specs/gkv-edi/001-gkv-anlagen-specs/contracts/anlage1-package.schema.json` in `packages/gkv-edi/src/format/package_validate.py`
- [x] T013 Extend `clearing_contracts` error paths if needed in `packages/clearing-contracts/src/clearing_contracts/types.py` for `unsupported_scope` without breaking existing `FormatResult`
- [x] T014 Mark legacy stub as non-default in `packages/gkv-edi/spec/v20/README.md` (subordinate to v21 per SC-008)

**Checkpoint**: PDFs on disk under `packages/gkv-edi/spec/official/`; loader/wire foundation ready — US1 can start

---

## Phase 3: User Story 1 - Encode ambulance claims against Anlage 1 (Priority: P1) 🎯 MVP

**Goal**: Krankentransport **SLLA:E** machine-readable Anlage 1 package (v21) + encode/decode/syntax validation against downloaded Anlage 1 PDF

**Independent Test**: Encode synthetic ambulance claim → Nutzdaten wire; validate; decode round-trip — using only `packages/gkv-edi` and `packages/gkv-edi/spec/v21/` (PDF at `packages/gkv-edi/spec/official/anlage-1/Anlage_1_TP5_V21_20260115.pdf` as authority)

### Implementation for User Story 1

- [x] T015 [US1] Write `packages/gkv-edi/spec/v21/provenance.yaml` citing Anlage 1 v21 Stand 2026-01-15, overview URL, `scope: krankentransport`, and local PDF path `official/anlage-1/Anlage_1_TP5_V21_20260115.pdf`
- [x] T016 [US1] Transcribe UNA / separator config into `packages/gkv-edi/spec/v21/una.yaml` from Anlage 1 PDF §5 (verify against downloaded PDF)
- [x] T017 [P] [US1] Define SLLA:E message composition in `packages/gkv-edi/spec/v21/messages/slla_e.yaml` (`FKT, REC, INV, NAD, IMG, EVO, KTL, EKT, TXT, MWS, ZUK, ZKT, SKZ, BES` + repetition rules)
- [x] T018 [P] [US1] Define SLGA message composition needed for ambulance files in `packages/gkv-edi/spec/v21/messages/slga.yaml`
- [x] T019 [P] [US1] Transcribe service segments into `packages/gkv-edi/spec/v21/segments/{UNB,UNH,UNT,UNZ}.yaml`
- [x] T020 [P] [US1] Transcribe shared/case segments into `packages/gkv-edi/spec/v21/segments/{FKT,REC,INV,NAD,IMG,EVO}.yaml` (ambulance-applicable fields only)
- [x] T021 [P] [US1] Transcribe SLLA:E individual segments into `packages/gkv-edi/spec/v21/segments/{KTL,EKT,TXT,MWS,ZUK,ZKT,SKZ,BES}.yaml` from PDF §5.5.3.6
- [x] T022 [US1] Implement logical ambulance claim model helpers in `packages/gkv-edi/src/format/models_slla_e.py` matching `specs/gkv-edi/001-gkv-anlagen-specs/data-model.md`
- [x] T023 [US1] Implement syntactic validation for SLLA:E order/lengths/M|K in `packages/gkv-edi/src/format/validate_syntax.py` using v21 package
- [x] T024 [US1] Implement Nutzdaten encode in `packages/gkv-edi/src/format/encode.py` (canonical wire text; optional JSON debug only)
- [x] T025 [US1] Implement Nutzdaten decode in `packages/gkv-edi/src/format/decode.py` with round-trip for supported fields
- [x] T026 [US1] Reject non-ambulance / non-E profiles with `unsupported_scope` in `packages/gkv-edi/src/format/validate_syntax.py` (and encode entry)
- [x] T027 [US1] Add synthetic fixtures under `packages/gkv-edi/tests/fixtures/synthetic/slla_e/` (logical JSON + expected wire excerpts; no Sozialdaten)
- [x] T028 [US1] Add tests `packages/gkv-edi/tests/test_slla_e_roundtrip.py` and `packages/gkv-edi/tests/test_validate_syntax_anlage1.py` per `specs/gkv-edi/001-gkv-anlagen-specs/quickstart.md`
- [x] T029 [US1] Update `packages/gkv-edi/README.md` to default `v21`, document PDF download step, and certification disclaimer

**Checkpoint**: US1 MVP complete — synthetic SLLA:E round-trip green against v21 package

---

## Phase 4: User Story 2 - Apply ambulance-relevant Anlage 3 codes (Priority: P1)

**Goal**: Structured Schlüsselverzeichnisse for codes referenced by SLLA:E fields; fail-closed membership checks

**Independent Test**: Validate synthetic claims against catalogs derived from `packages/gkv-edi/spec/official/anlage-3/Anlage_3_TP5_V21_20250919.pdf`

- [x] T030 [US2] Confirm Anlage 3 v21 PDF present at `packages/gkv-edi/spec/official/anlage-3/Anlage_3_TP5_V21_20250919.pdf` (re-run download script if missing)
- [x] T031 [US2] Create catalog package layout `packages/gkv-edi/spec/v21/catalogs/` with provenance note pointing at official Anlage 3 PDF
- [x] T032 [P] [US2] Transcribe ambulance-relevant catalogs (at least Sammelgruppe E / LE type 41–49, Versichertenstatus, Unfall/Sonstiges, Rechnungsart, Positionsnummer rules) into YAML under `packages/gkv-edi/spec/v21/catalogs/*.yaml`
- [x] T033 [US2] Wire `catalog_ref` resolution into `packages/gkv-edi/src/format/validate_syntax.py` (unknown/non-permitted codes fail with catalog id + version)
- [x] T034 [US2] Add catalog fixtures + tests in `packages/gkv-edi/tests/test_anlage3_catalogs.py`

**Checkpoint**: Coded ambulance fields fail closed against Anlage 3

---

## Phase 5: User Story 4 - Resolve payers via Kostenträger file (Anhang 3) (Priority: P1)

**Goal**: Ingest Kostenträgerdatei per Anhang 3; IK lookup for ambulance addressing

**Independent Test**: Ingest synthetic/official-structure fixture; lookup ≥20 IKs including not-found — using PDF `packages/gkv-edi/spec/official/anhang-3/Anhang_03_Anlage_1_TP5_V10_20260414.pdf`

- [x] T035 [US4] Confirm Anhang 3 PDF at `packages/gkv-edi/spec/official/anhang-3/Anhang_03_Anlage_1_TP5_V10_20260414.pdf`
- [x] T036 [US4] Add machine-readable Anhang 3 structure package under `packages/gkv-edi/spec/v21/kostentraeger/` (or agreed path in format module) with provenance to that PDF
- [x] T037 [US4] Implement ingest + IK lookup in `packages/gkv-edi/src/format/kostentraeger.py` (or dedicated module if plan evolves — keep contract in format for Slice D MVP)
- [x] T038 [US4] Add synthetic Kostenträger fixtures under `packages/gkv-edi/tests/fixtures/synthetic/kostentraeger/` and tests `packages/gkv-edi/tests/test_kostentraeger_lookup.py`
- [x] T039 [US4] Ensure failed structural ingest does not partially overwrite a good directory (atomic replace) in `packages/gkv-edi/src/format/kostentraeger.py`

**Checkpoint**: IK resolution works for ambulance recipient addressing

---

## Phase 6: User Story 3 - Check ambulance Urbeleg rules from Anlage 5 (Priority: P2)

**Goal**: Krankentransport Urbeleg content validation from Anlage 5

**Independent Test**: ≥5 positive and ≥5 negative synthetic fixtures using PDF `packages/gkv-edi/spec/official/anlage-5/Anlage_5_TP5_V4_0_20180927.pdf`

- [x] T040 [US3] Confirm Anlage 5 PDF at `packages/gkv-edi/spec/official/anlage-5/Anlage_5_TP5_V4_0_20180927.pdf`
- [x] T041 [US3] Transcribe ambulance Urbeleg rules into `packages/gkv-edi/spec/v21/urbeleg/anlage5_krankentransport.yaml`
- [x] T042 [US3] Implement content checks in `packages/gkv-edi/src/format/validate_urbeleg.py`
- [x] T043 [US3] Add fixtures + tests `packages/gkv-edi/tests/test_anlage5_urbeleg.py` including unsupported non-ambulance rejection

**Checkpoint**: Missing Urbeleg elements flagged for ambulance claims

---

## Phase 7: User Story 5 - Support parallel Anlage versions (Priority: P2)

**Goal**: Coexist v21 (default) and v22 (preview) ambulance packages

**Independent Test**: Same logical claim validated under v21 vs v22 with at least one version-delta fixture; PDFs already under `packages/gkv-edi/spec/official/anlage-1/` and `anlage-3/`

- [x] T044 [US5] Scaffold `packages/gkv-edi/spec/v22/` package (copy structure from v21) and set provenance to Anlage 1/3 v22 PDFs in `packages/gkv-edi/spec/official/`
- [x] T045 [US5] Transcribe material v21→v22 deltas for SLLA:E into `packages/gkv-edi/spec/v22/segments/` and `messages/` (diff against downloaded v22 PDFs)
- [x] T046 [US5] Ensure `spec_loader` default remains `v21` while explicit `v22` selection works in `packages/gkv-edi/src/format/spec_loader.py`
- [x] T047 [US5] Add version-delta fixture + test `packages/gkv-edi/tests/test_spec_version_selection.py`

**Checkpoint**: Parallel versions selectable; default unchanged

---

## Phase 8: User Story 6 - Traceability to official GKV publications (Priority: P3)

**Goal**: Every package provenance cites official identity + local PDF path + Krankentransport scope

**Independent Test**: Inspect provenance records for v21 (and v22 if present); fields complete within 5 minutes

- [x] T048 [P] [US6] Audit/complete provenance fields in `packages/gkv-edi/spec/v21/provenance.yaml` and `packages/gkv-edi/spec/v22/provenance.yaml` (stand dates, source overview, local PDF relative paths, scope)
- [x] T049 [US6] Add test `packages/gkv-edi/tests/test_provenance.py` asserting required provenance keys and `scope == krankentransport`
- [x] T050 [US6] Document provenance + PDF download in `packages/gkv-edi/README.md` and cross-link `specs/gkv-edi/001-gkv-anlagen-specs/quickstart.md`

**Checkpoint**: Audit-ready citations for all default packages

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story hardening and quickstart validation

- [x] T051 [P] Run full format test suite via `uv run pytest packages/gkv-edi/tests -q` and fix regressions
- [x] T052 [P] Execute `specs/gkv-edi/001-gkv-anlagen-specs/quickstart.md` steps; update quickstart if commands drifted
- [x] T053 Subordinate or remove conflicting stub usage so default encode path is v21 only (`packages/gkv-edi/src/format/` + README)
- [x] T054 [P] Add CI note or workflow step to run `packages/gkv-edi/scripts/download_official_pdfs.py` before format tests that need PDF presence checks (if CI asserts file existence)
- [x] T055 Verify no real Sozialdaten patterns in `packages/gkv-edi/tests/fixtures/` (manual/policy check documented in README)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Start immediately
- **Phase 2 (Foundational)**: Depends on Setup — **BLOCKS all stories**; includes **PDF downloads into `packages/gkv-edi/spec/official/`**
- **Phase 3 (US1)**: Depends on Phase 2 — **MVP**
- **Phase 4 (US2)**: Depends on Phase 2; ideally after US1 so `catalog_ref` fields exist
- **Phase 5 (US4)**: Depends on Phase 2; can parallelize with US2/US3 after foundation
- **Phase 6 (US3)**: Depends on Phase 2; better after US1 logical model exists
- **Phase 7 (US5)**: Depends on US1 package shape (v21) existing
- **Phase 8 (US6)**: Depends on packages having provenance files (after US1; completes after US5 if v22 present)
- **Phase 9 (Polish)**: After desired stories

### User Story Dependencies

- **US1**: After foundation — no story deps — **MVP**
- **US2**: After foundation; integrates with US1 field `catalog_ref`s
- **US4**: After foundation; independent of encode wire format
- **US3**: After foundation; uses US1 logical claim shape
- **US5**: After US1 (needs v21 as template)
- **US6**: After US1 provenance exists; strengthens all packages

### Parallel Opportunities

- T002, T003, T004 after T001 directory exists
- T008, T009, T011, T012 after T006/T007 PDF download
- Within US1: T017–T021 segment YAML files in parallel after T015–T016
- US2 / US4 can proceed in parallel after US1 MVP if staffed
- T048 parallel with polish docs

---

## Parallel Example: User Story 1

```bash
# After T015–T016, launch segment transcriptions in parallel:
Task: "T019 Transcribe UNB/UNH/UNT/UNZ into packages/gkv-edi/spec/v21/segments/"
Task: "T020 Transcribe FKT/REC/INV/NAD/IMG/EVO into packages/gkv-edi/spec/v21/segments/"
Task: "T021 Transcribe KTL/EKT/TXT/MWS/ZUK/ZKT/SKZ/BES into packages/gkv-edi/spec/v21/segments/"
```

---

## Parallel Example: Official PDF downloads (Foundation)

```bash
# Single script downloads all (T007); buckets are independent files:
# packages/gkv-edi/spec/official/anlage-1/*.pdf
# packages/gkv-edi/spec/official/anlage-3/*.pdf
# packages/gkv-edi/spec/official/anlage-5/*.pdf
# packages/gkv-edi/spec/official/anhang-3/*.pdf
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Phase 1 Setup  
2. Phase 2 Foundation **including PDF download into `packages/gkv-edi/spec/official/`**  
3. Phase 3 US1 Anlage 1 / SLLA:E  
4. **STOP and VALIDATE** via quickstart + `test_slla_e_roundtrip.py`  
5. Demo encode/decode on synthetic ambulance claim

### Incremental Delivery

1. US1 → working Nutzdaten for ambulances  
2. US2 → catalog fail-closed  
3. US4 → IK/Kostenträger resolution  
4. US3 → Urbeleg content rules  
5. US5 → v22 preview alongside v21  
6. US6 → provenance polish  

### Suggested MVP scope

**T001–T029** (Setup + Foundation + US1), with PDFs downloaded at T006–T007 into `C:\Users\info\dev\easy\clearing\modules\format\spec\official\`.

---

## Notes

- Official PDF base URL: `https://www.gkv-datenaustausch.de`
- Do not commit PDFs if `.gitignore` excludes them; always commit `sources.manifest.yaml` + download script
- Transcribe **Krankentransport / SLLA:E only** from shared SLE PDFs
- Synthetic fixtures only — never real Versichertendaten
- Next command after tasks: `/speckit-implement` (or implement MVP T001–T029 manually)

## Phase 10: Convergence

- [x] T056 CRITICAL: Wire clearing-format into the uv workspace (or add PyYAML to root/dev deps), lock it, and document uv-only install so `uv sync --group dev` enables `import yaml`; remove pip-primary paths in root README per Constitution Tooling / T003 (partial)
- [x] T057 Add at least one synthetic invalid catalog-code rejection test per referenced catalog_ref (versichertenstatus, rechnungsart, verarbeitungskennzeichen, abrechnungscode, tarifkennzeichen, unfall_sonstiges, zuzahlungsart, laenderkennzeichen) per SC-002 / US2/AC2 (partial)
- [x] T058 Add ≥5 distinct complete positive and ≥5 distinct negative Urbeleg fixtures/tests per SC-003 / US3 (partial)
- [x] T059 Implement automated fixture pattern check that fails CI on reserved real-Sozialdaten patterns per SC-007 / FR-011 / Constitution V (missing)
- [x] T060 Align kostentraeger/anhang3 ingest structure with published Anhang 3 layout (or prove fixture ≡ published) and add a representative real-structure fixture per FR-006 / US4/AC1 (partial)
- [x] T061 Drive syntax segment order/repetition from messages/slla_e.yaml, enforce field value_type/lengths, and add negative order fixtures per US1/AC2 / FR-010 / format-anlage1-api contract (partial)
- [x] T062 Include service segments UNB/UNH/UNT/UNZ in syntax validation and fixture coverage for mandatory fields per SC-001 / FR-002 (partial)
- [x] T063 Add Anlage 5 and Anhang 3 publication entries to package provenance.yaml publications lists per FR-009 / US6/AC1 (partial)
- [x] T064 Implement minimal SLGA encode/validate for ambulance file envelope, or explicitly narrow plan/spec if SLLA-only is intentional per plan Slice A / T018 (partial)
- [x] T065 Replace legacy plausibility shape with SLLA:E-aware plausibility checks and dedicated independent tests per Constitution IV / FR-010 (partial)
- [x] T066 Model Unfall-dependent Urbeleg conditional rules from Anlage 5 and cover with fixtures per FR-005 / edge Unfall-dependent Urbeleg (partial)
- [x] T067 Add deliberate wire/logical wrong-order negative test claimed by quickstart per US1/AC2 (partial)
- [x] T068 Update catalogs README under spec/v21 and v22 to reflect implemented fail-closed membership (Slice B done) per docs drift / T031 (partial)

## Phase 11: Convergence

- [x] T069 On stand adoption, retain prior/replaced stand identity in provenance (`replaced_stand` or equivalent) for v21/v22 packages and cover with a test per US6/AC2 / FR-009 / FR-015 (partial)
- [x] T070 Drive intra-case segment/repetition order from `messages/slla_e.yaml` (replace hardcoded `_validate_case_group_order` flow) so package and validator cannot drift per US1/AC2 / FR-010 / residual T061 (partial)
- [x] T071 Include the full `packages/gkv-edi/tests` suite (or SC-critical subset: round-trip, catalogs, Urbeleg, Kostenträger, version, provenance) in CI Focused pytest per SC-001…SC-006 (partial)
