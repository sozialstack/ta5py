# Implementation Plan: LANR and BSNR Formal Validators

**Branch**: `006-lanr-bsnr-validators` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/ta5py/006-lanr-bsnr-validators/spec.md`. Planning guidance: use the same pattern as for IK (`004-ik-validator` / `ta5py.ik`).

## Summary

Add reusable, offline formal validators for Lebenslange Arztnummer (LANR) and Betriebsstättennummer (BSNR) to `ta5py`, mirroring the Institutskennung (`Ik`) value-type pattern: frozen dataclasses, `parse` / `is_valid` / `is_formally_valid`, LANR Prüfziffer helpers, structure-only BSNR (no public check digit), German companion notes, and synthetic tests. No registry lookup, no specialty/KV catalog enforcement, no certification claims.

## Technical Context

**Language/Version**: Python 3.12 (monorepo / `uv`)

**Primary Dependencies**: Existing `packages/ta5py` only for the validator core (stdlib). pytest for tests. No network libraries for the checks themselves.

**Storage**: N/A (pure functions; no persistence)

**Testing**: pytest; synthetic LANR fixtures (KBV-style `123456601` / wrong check `123456901`) and synthetic nine-digit BSNRs only

**Target Platform**: Library modules used locally and in CI (Windows/macOS/Linux)

**Project Type**: Library enhancement inside `packages/ta5py` (Spec Kit under `specs/ta5py/006-lanr-bsnr-validators/`)

**Performance Goals**: Single LANR/BSNR formal check well under 1s (effectively microseconds); SC-003 from spec

**Constraints**: Offline; trim-only whitespace; LANR Prüfziffer per KBV Arztnummern-Richtlinie; BSNR structure-only (no Prüfziffer); formal validity ≠ assignment / Testat; Principle IV synthetic data only; Principle VII typed public API

**Scale/Scope**: Two small public modules (or one shared module with two types) + unit tests + short German companion notes; no Anlage package changes required for MVP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*MUST read every applicable `specs/<module>/constitution.md` before judging
this gate (project constitution Principle III).*

**Module constitutions loaded**:
- [x] `.specify/memory/constitution.md` (v8.2.0)
- [x] `specs/ta5py/constitution.md` (v2.0.1)

| Principle / gate | Status | How addressed |
|------------------|--------|---------------|
| I. English code, German companions | PASS | English identifiers/API/Spec Kit; German operator notes for LANR/BSNR vocabulary only |
| II. Three-package architecture | PASS | Work stays in ta5py (syntactic identifiers); Spec Kit under `specs/ta5py/006-…`; no dtapy/leistungen imports |
| III. Package constitutions | PASS | ta5py constitution loaded; feature is syntactic validation, not billing |
| ta5py I–II (machine-readable specs + syntactic layer) | PASS | Prüfziffer / structure checks are independently testable syntactic validation; docs cite KBV Richtlinie; no plausibility |
| IV. Synthetic data only | PASS | Synthetic LANR/BSNR in tests/docs; no real Sozialdaten |
| V. Certification clarity | PASS | Spec/docs: formal OK ≠ Testat / payer acceptance |
| VI. Contributor Gate | PASS | No `testate/` involvement |
| VII. Typesafe code | PASS | Annotated public types/functions; no untyped boundary |

**Post-design re-check**: PASS — contracts expose pure typed value types only (same shape as `Ik`); no cross-package dependency reversal; specialty/KV catalog exclusion deferred as optional policy outside default API.

## Project Structure

### Documentation (this feature)

```text
specs/ta5py/006-lanr-bsnr-validators/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── lanr-bsnr-validator-api.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # /speckit-tasks (not created here)
```

### Source Code (repository root)

```text
packages/ta5py/
├── src/ta5py/
│   ├── lanr.py              # Lanr value type (parse, is_valid, compute_check_digit)
│   ├── bsnr.py              # Bsnr value type (parse, is_valid; structure only)
│   └── __init__.py          # re-export public Lanr / Bsnr helpers
├── docs/de/                 # short German companion notes (vocabulary / formal vs business)
└── tests/
    ├── test_lanr.py         # synthetic Prüfziffer cases
    └── test_bsnr.py         # synthetic structure cases
```

**Structure Decision**: Mirror `ta5py.ik` with focused modules `ta5py.lanr` and `ta5py.bsnr` (separate files keep check-digit vs structure-only docs clear), exported from package `__init__` for reuse by leistungen and kassenclearing. No new package; dtapy remains unable to import ta5py (constitution) and stays out of this reuse story.

## Complexity Tracking

> No constitution violations requiring justification.
