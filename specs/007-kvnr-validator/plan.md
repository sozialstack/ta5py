# Implementation Plan: Krankenversichertennummer Formal Validator

**Branch**: `007-kvnr-validator` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/ta5py/007-kvnr-validator/spec.md`.

## Summary

Add a reusable, offline formal validator for the 10-character unchanging Krankenversichertennummer (KVNR) to `ta5py`, mirroring the Institutskennung (`Ik`) and LANR value-type pattern: a frozen dataclass, `parse` / `is_valid` / `is_formally_valid`, a Prüfziffer helper, German companion notes, and synthetic tests. The check digit is Anlage 1 zur Richtlinie nach § 290 SGB V (sum modulo 10), not the complement-to-10 rule used by IK and LANR. No registry lookup, no issuance-exclusion enforcement, no 20-/30-character Gesamtsystem number, no change to the TA5 Versicherten-Nummer field, no certification claims.

## Technical Context

**Language/Version**: Python 3.12 (monorepo / `uv`)

**Primary Dependencies**: Existing `packages/ta5py` only for the validator core (stdlib). pytest for tests. No network libraries for the check itself.

**Storage**: N/A (pure functions; no persistence)

**Testing**: pytest; synthetic KVNR fixtures only. Anchors: published illustration `A000500015` (valid) / `A000500016` (invalid), second published-style anchor `C000500021` (valid), and allowlisted `A000000002` (valid; distinguishes sum-modulo-10 from complement-to-10)

**Target Platform**: Library module used locally and in CI (Windows/macOS/Linux)

**Project Type**: Library enhancement inside `packages/ta5py` (Spec Kit under `specs/ta5py/007-kvnr-validator/`)

**Performance Goals**: Single KVNR formal check well under 1s (effectively microseconds); SC-002 from spec

**Constraints**: Offline; trim plus ASCII case-fold of the leading letter only; Prüfziffer per § 290 Anlage 1 for the 10-character unchanging part; formal validity ≠ issued / insured / Testat; Principle IV synthetic data only; Principle VII typed public API; do not tighten `INV.versicherten_id`

**Scale/Scope**: One small public module + unit tests + a short German companion note; no Anlage package or syntax-validator changes for this feature

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*MUST read every applicable `specs/<module>/constitution.md` before judging
this gate (project constitution Principle III).*

**Module constitutions loaded**:
- [x] `.specify/memory/constitution.md` (v8.2.0)
- [x] `specs/ta5py/constitution.md` (v2.0.1)

| Principle / gate | Status | How addressed |
|------------------|--------|---------------|
| I. English code, German companions | PASS | English identifiers/API/Spec Kit; German operator note for KVNR vocabulary only |
| II. Three-package architecture | PASS | Work stays in ta5py (syntactic identifier); Spec Kit under `specs/ta5py/007-…`; no dtapy/leistungen imports |
| III. Package constitutions | PASS | ta5py constitution loaded; feature is syntactic validation, not billing |
| ta5py I–II (machine-readable specs + syntactic layer) | PASS | Prüfziffer check is independently testable syntactic validation; docs cite § 290 Anlage 1; no plausibility; INV field schema unchanged |
| IV. Synthetic data only | PASS | Synthetic KVNR and the published arithmetic illustration only; no real Sozialdaten |
| V. Certification clarity | PASS | Spec/docs: formal OK ≠ issued, insured, or Testat |
| VI. Contributor Gate | PASS | No `testate/` involvement |
| VII. Typesafe code | PASS | Annotated public type/functions; no untyped boundary |

**Post-design re-check**: PASS — contract exposes one pure typed value type (same shape as `Ik` / `Lanr`); no cross-package dependency reversal; 20-/30-character forms, issuance exclusions, and INV syntax changes stay outside the default API.

## Project Structure

### Documentation (this feature)

```text
specs/ta5py/007-kvnr-validator/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── kvnr-validator-api.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # /speckit-tasks (not created here)
```

### Source Code (repository root)

```text
packages/ta5py/
├── src/ta5py/
│   ├── kvnr.py              # Kvnr value type (parse, is_valid, compute_check_digit)
│   └── __init__.py          # re-export public Kvnr / KvnrError
├── docs/de/
│   ├── kvnr.md              # German companion: vocabulary, Prüfziffer, limits
│   └── README.md            # link the new note
└── tests/
    └── test_kvnr.py         # synthetic Prüfziffer cases
```

**Structure Decision**: Mirror `ta5py.ik` / `ta5py.lanr` with one module `ta5py.kvnr`, exported from the package `__init__` for reuse by leistungen and kassenclearing. No new package. dtapy remains unable to import ta5py (constitution) and stays out of this reuse story. Do not call the validator from `validate_syntax` for `INV.versicherten_id`.

## Complexity Tracking

> No constitution violations requiring justification.
