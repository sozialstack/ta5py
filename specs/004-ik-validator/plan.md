# Implementation Plan: Institutskennung (IK) Formal Validator

**Branch**: `004-ik-validator` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/ta5py/004-ik-validator/spec.md`.

## Summary

Add a reusable, offline formal Institutskennung (IK) validator to `ta5py`: nine-digit structure, Prüfziffer over positions 3–8 per Gemeinsames Rundschreiben IK (Wikipedia / GKV-Datenaustausch), optional seven-digit Kassennummer expansion with prefix `10`, and explicit documentation that Ersatzkennzeichen can pass the default check. No directory lookup, no billing plausibility, no certification claims.

## Technical Context

**Language/Version**: Python 3.12 (monorepo / `uv`)

**Primary Dependencies**: Existing `packages/ta5py` only for the validator core (stdlib). pytest for tests. No network libraries for the check itself.

**Storage**: N/A (pure function; no persistence)

**Testing**: pytest; synthetic IK fixtures only (including Wikipedia example `260326822` / `260326823` and Ersatzkennzeichen samples)

**Target Platform**: Library module used locally and in CI (Windows/macOS/Linux)

**Project Type**: Library enhancement inside `packages/ta5py` (Spec Kit under `specs/ta5py/004-ik-validator/`)

**Performance Goals**: Single IK formal check well under 1s (effectively microseconds); SC-002 from spec

**Constraints**: Offline; trim-only whitespace; default check does not exclude Ersatzkennzeichen; formal validity ≠ registry existence; Principle IV synthetic data only; Principle VII typed public API

**Scale/Scope**: One small public module + unit tests + short German companion note on formal vs business meaning; no Anlage package changes required for MVP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*MUST read every applicable `specs/<module>/constitution.md` before judging
this gate (project constitution Principle III).*

**Module constitutions loaded**:
- [x] `.specify/memory/constitution.md` (v8.1.1)
- [x] `specs/ta5py/constitution.md` (v2.0.1)

| Principle / gate | Status | How addressed |
|------------------|--------|---------------|
| I. English code, German companions | PASS | English identifiers/API/Spec Kit; German operator note for IK vocabulary only |
| II. Three-package architecture | PASS | Work stays in ta5py (syntactic identifier); Spec Kit under `specs/ta5py/004-…`; no dtapy/leistungen imports |
| III. Package constitutions | PASS | ta5py constitution loaded; feature is syntactic validation, not billing |
| ta5py I–II (machine-readable specs + syntactic layer) | PASS | Prüfziffer is independently testable syntactic validation; docs cite regulatory source; no plausibility |
| IV. Synthetic data only | PASS | Synthetic IKs in tests/docs; no real Sozialdaten |
| V. Certification clarity | PASS | Spec/docs: formal OK ≠ Testat / payer acceptance |
| VI. Contributor Gate | PASS | No `testate/` involvement |
| VII. Typesafe code | PASS | Annotated public functions; no untyped boundary |

**Post-design re-check**: PASS — contracts expose pure typed validators only; no cross-package dependency reversal; Ersatzkennzeichen exclusion deferred as optional policy outside default API.

## Project Structure

### Documentation (this feature)

```text
specs/ta5py/004-ik-validator/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ik-validator-api.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # /speckit-tasks (not created here)
```

### Source Code (repository root)

```text
packages/ta5py/
├── src/ta5py/
│   ├── ik.py                # is_valid_ik, expand_kassennummer, check-digit helpers
│   └── __init__.py          # re-export public IK helpers
├── docs/de/                 # short German companion note (vocabulary / formal vs business)
└── tests/
    └── test_ik.py           # synthetic cases: Wikipedia example, bad length, Ersatzkennzeichen, Kassennummer expand
```

**Structure Decision**: Small focused module `ta5py.ik` next to existing syntactic helpers (`validate_syntax.py`), exported from package `__init__` for reuse by leistungen and kassenclearing. No new package; dtapy remains unable to import ta5py (constitution) and stays out of this reuse story.

## Complexity Tracking

> No constitution violations requiring justification.
