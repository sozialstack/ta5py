# Implementation Plan: Kostenträger IK Verification (§ 302)

**Branch**: `005-kostentraeger-ik-verify` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/ta5py/005-kostentraeger-ik-verify/spec.md`.

## Summary

Expose a clear **registry verification** API on top of ta5py’s existing SLE Kostenträgerdatei ingest: confirm a card/Kostenträger IK is present in the loaded GKV-Spitzenverband file and resolve the § 302 acceptance/billing recipient IK from Verknüpfungen. Formal Prüfziffer checks stay in `004-ik-validator` / `ta5py.ik`; this feature answers existence + addressing from the official EDIFACT catalog (download/ingest already partially present).

## Technical Context

**Language/Version**: Python 3.12 (monorepo / `uv`)

**Primary Dependencies**: Existing `packages/ta5py` Kostenträger stack (`kostentraeger.py`, `kostentraeger_fetch.py`, Anhang-3 YAML under `spec/v21|v22/kostentraeger/`), stdlib + PyYAML as today. Optional composition with `ta5py.ik.is_valid_ik` (callers). pytest for tests.

**Storage**: Local ingested store (JSON `store.json` / operator cache under `var/kostentraeger/`); verification reads the loaded store only (no live network at verify time).

**Testing**: pytest; synthetic Anhang-3 EDIFACT fixtures only (extend existing `tests/fixtures/synthetic/kostentraeger/`).

**Target Platform**: Library module used locally and in CI (Windows/macOS/Linux)

**Project Type**: Library enhancement inside `packages/ta5py` (Spec Kit under `specs/ta5py/005-kostentraeger-ik-verify/`)

**Performance Goals**: Single verify/resolve from an already loaded store well under 3s (effectively sub-millisecond dictionary lookup); SC-003

**Constraints**: Offline verify against loaded file; authoritative source = official SLE Kostenträgerdatei; no Testat claims; Principle IV synthetic fixtures; Principle VII typed public API; ta5py MUST NOT import dtapy/leistungen

**Scale/Scope**: Structured verification result + thin public helpers on/near `KostentraegerStore`; German companion note for registry vs formal vs Testat; reuse existing download script / `make download-kostentraeger` for operator refresh

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*MUST read every applicable `specs/<module>/constitution.md` before judging
this gate (project constitution Principle III).*

**Module constitutions loaded**:
- [x] `.specify/memory/constitution.md` (v8.1.1)
- [x] `specs/ta5py/constitution.md` (v2.0.1)

| Principle / gate | Status | How addressed |
|------------------|--------|---------------|
| I. English code, German companions | PASS | English API/Spec Kit; German operator note for Kostenträger / § 302 addressing vocabulary |
| II. Three-package architecture | PASS | Work stays in ta5py (Kostenträger catalog for encoding/addressing); Spec Kit under `specs/ta5py/005-…`; no dtapy/leistungen imports |
| III. Package constitutions | PASS | ta5py constitution loaded; Domain Scope includes Kostenträger catalogs |
| ta5py I–II (machine-readable specs + syntactic layer) | PASS | Ingest/link selection driven by Anhang-3 YAML; verify is catalog truth for addressing, not billing plausibility |
| IV. Synthetic data only | PASS | Synthetic KOTR fixtures and IKs only in tests/docs |
| V. Certification clarity | PASS | Spec/docs: registry hit ≠ Testat / payer acceptance of message content |
| VI. Contributor Gate | PASS | No `testate/` involvement; live `.ke*` cache remains gitignored |
| VII. Typesafe code | PASS | Annotated verify/resolve surface; structured result types |

**Post-design re-check**: PASS — contracts expose typed verify/resolve over loaded store; download remains operator/CI step; formal IK check remains a separate module; no cross-package dependency reversal.

## Project Structure

### Documentation (this feature)

```text
specs/ta5py/005-kostentraeger-ik-verify/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── kostentraeger-ik-verify-api.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # /speckit-tasks (not created here)
```

### Source Code (repository root)

```text
packages/ta5py/
├── src/ta5py/
│   ├── kostentraeger.py     # Store + ingest; add verify/resolve helpers / result type
│   ├── kostentraeger_fetch.py  # existing official download (operator refresh)
│   ├── ik.py                # formal check only (compose, do not merge)
│   └── __init__.py          # re-export public verify helpers
├── docs/de/                 # German companion: registry vs formal vs Testat
├── scripts/download_kostentraeger.py
├── var/kostentraeger/       # gitignored operator cache + README
└── tests/
    ├── test_kostentraeger_lookup.py   # extend / sibling verify tests
    └── fixtures/synthetic/kostentraeger/
```

**Structure Decision**: Extend the existing `ta5py.kostentraeger` module with an explicit verification API rather than a new package. Keep formal Prüfziffer in `ta5py.ik`. Reuse Anhang-3 schema-driven `_pick_acceptance` for § 302 / SLE recipient selection. Download/fetch stays an operator refresh path, not part of the hot verify path.

## Complexity Tracking

> No constitution violations requiring justification.
