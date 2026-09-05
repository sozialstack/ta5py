# Implementation Plan: Ambulance GKV Anlagen Machine-Readable Specs

**Branch**: `001-gkv-anlagen-specs` | **Date**: 2026-08-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/ta5py/001-gkv-anlagen-specs/spec.md`. User planning directive: **start with Anlage 1**.

## Summary

Replace the minimal `packages/ta5py/spec/v20` stub with governed, versioned, **Krankentransport-only** machine-readable packages derived from official GKV-Datenaustausch Sonstige Leistungserbringer publications.

**Delivery sequencing (mandatory):**

| Slice | Scope | Status in this plan |
|-------|--------|---------------------|
| **A — Anlage 1 first** | Separators, file/message structure, service segments, SLGA (ambulance-needed), **SLLA:E** segments/fields, logical model ↔ EDIFACT-like Nutzdaten encode/decode, syntactic validation | **Primary MVP — implement first** |
| B — Anlage 3 | Ambulance-referenced Schlüsselverzeichnisse (e.g. Sammelgruppe E, Versichertenstatus, Unfall, Positionsnummern) | Planned after A |
| C — Anlage 5 | Krankentransport Urbeleg content rules | Planned after B |
| D — Anhang 3 | Kostenträgerdatei ingest + IK lookup | Planned after A (can parallelize with B/C) |

Technical approach: YAML segment/field definitions under `packages/ta5py/spec/v21/` (default), with provenance; `format` loads them for syntax validation and wire serialization; JSON remains an optional logical interchange, not a substitute for Nutzdaten wire form.

## Technical Context

**Language/Version**: Python 3.12 (existing monorepo / `uv`)

**Primary Dependencies**: Existing `format` + `clearing-contracts`; PyYAML for segment packages; pytest for fixtures. No new web frameworks for this feature.

**Storage**: Versioned files under `packages/ta5py/spec/vN/` (and later Kostenträger artifacts under the kostenträger/sync owner when Slice D lands). No production patient DB.

**Testing**: pytest; synthetic ambulance fixtures only; golden Nutzdaten strings for SLLA:E round-trips.

**Target Platform**: Library module used locally and in CI (Windows/macOS/Linux); same as rest of clearing monorepo.

**Project Type**: Domain-spec + library enhancement inside `packages/ta5py` (Spec Kit docs under `specs/ta5py/001-gkv-anlagen-specs/`).

**Performance Goals**: Validate and encode a typical single-case ambulance message (one INV…BES) in under 1s locally; load default spec package in under 500ms cold.

**Constraints**: Ambulance/SLLA:E only; no real Sozialdaten; official PDFs authoritative; English Spec Kit artifacts; no payer-certification claims; parallel Anlage versions supported.

**Scale/Scope**: Slice A covers full SLLA:E segment inventory for default **v21** (re-verified against current PDF at implement time). Shared SLE segments used by E are included; other Sammelgruppen (A–D, F–…) are out of scope. Anlage 3/5/Anhang 3 deferred per sequencing table.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How addressed |
|-----------|--------|---------------|
| I. English-First | PASS | Plan/research/data-model/contracts/quickstart in English; German terms explained |
| II. Modular, Swappable Layers | PASS | Work stays in `format` (core encoding); Spec Kit feature docs under `specs/ta5py/001-…`; Kostenträger later remains swappable |
| III. Machine-Readable, Versioned Domain Specs | PASS | `packages/ta5py/spec/v21/` (and future `v22/`) own Anlage packages; fields capture name, order, length, M/K, catalogs |
| IV. Dual Validation Layers | PASS | Slice A delivers syntactic validation; plausibility remains separate and may stay thin until later slices |
| V. Privacy-by-Design & Synthetic Data Only | PASS | Synthetic fixtures; CI policy in quickstart |
| VI. Liability & Certification Clarity | PASS | Provenance + README disclaimer; packages are interpretations, not Testat |

**Post-design re-check**: PASS — contracts describe format package layout and encode/validate interfaces only; no layer merge; ambulance-only scope enforced.

## Project Structure

### Documentation (this feature)

```text
specs/ta5py/001-gkv-anlagen-specs/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── anlage1-package.schema.json
│   └── format-anlage1-api.md
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks (not created here)
```

### Source Code (repository root)

```text
packages/ta5py/
├── pyproject.toml
├── README.md
├── spec/
│   ├── v20/                          # Legacy stub — subordinate or archive after v21 lands
│   │   └── dataset.schema.json
│   └── v21/                          # Default Slice A package
│       ├── provenance.yaml           # Official citation + Krankentransport-only note
│       ├── una.yaml                  # Separators / service syntax constants
│       ├── messages/
│       │   ├── slga.yaml             # SLGA segment order (ambulance file needs)
│       │   └── slla_e.yaml           # SLLA:E composition + repetition rules
│       ├── segments/                 # One file per segment used by ambulance path
│       │   ├── UNB.yaml
│       │   ├── UNH.yaml
│       │   ├── UNT.yaml
│       │   ├── UNZ.yaml
│       │   ├── FKT.yaml
│       │   ├── REC.yaml
│       │   ├── INV.yaml
│       │   ├── NAD.yaml
│       │   ├── IMG.yaml
│       │   ├── EVO.yaml
│       │   ├── KTL.yaml
│       │   ├── EKT.yaml
│       │   ├── TXT.yaml
│       │   ├── MWS.yaml
│       │   ├── ZUK.yaml
│       │   ├── ZKT.yaml
│       │   ├── SKZ.yaml
│       │   └── BES.yaml
│       └── catalogs/                 # Slice A: optional stubs / refs only
│           └── README.md             # Points to Slice B (Anlage 3)
├── src/format/
│   ├── spec_loader.py                # Load vN packages (segments + messages)
│   ├── encode.py                     # Logical claim → Nutzdaten wire (+ optional JSON debug)
│   ├── decode.py                     # Nutzdaten wire → logical claim
│   ├── validate_syntax.py            # Structure/length/M|K/order against package
│   ├── validate_plausibility.py      # Separate layer (thin in Slice A)
│   ├── wire.py                       # Separators, escaping, segment join/split
│   └── uri.py
└── tests/
    ├── fixtures/synthetic/slla_e/    # Golden wire + logical pairs
    ├── test_spec_loader.py
    ├── test_slla_e_roundtrip.py
    └── test_validate_syntax_anlage1.py
```

**Structure Decision**: Extend existing `packages/ta5py` rather than a new module. Spec Kit governance lives under `specs/ta5py/001-gkv-anlagen-specs/` per constitution Principle II. Runtime machine-readable artifacts live under `packages/ta5py/spec/vN/`.

## Complexity Tracking

> No constitution violations requiring justification.
