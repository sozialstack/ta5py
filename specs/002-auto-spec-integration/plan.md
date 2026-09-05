# Implementation Plan: Automatic Format Spec Detection & Integration

**Branch**: `002-auto-spec-integration` | **Date**: 2026-08-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/ta5py/002-auto-spec-integration/spec.md`. Planning directive: **new spec will be integrated on a new branch**.

## Summary

Add a **format-module governance pipeline** that (1) automatically checks official GKV-Datenaustausch publications for new/changed ambulance-relevant Anlage packages, (2) prepares machine-readable integration work on a **dedicated git branch** (scaffold `packages/ta5py/spec/vN/`, update `sources.manifest.yaml`, change summary), and (3) enforces a **strict human approval gate** before changing the live/default format version (`DEFAULT_VERSION` / live binding). Detection and scaffolding never flip production-facing defaults.

## Technical Context

**Language/Version**: Python 3.12 (existing monorepo / `uv`)

**Primary Dependencies**: Existing `format` module; PyYAML; stdlib `urllib` (same pattern as `download_official_pdfs.py`); pytest. Git CLI for branch creation (invoked from scripts; no new VCS library required). Optional: `httpx` only if stdlib proves insufficient for HEAD/ETag checks—prefer stdlib first.

**Storage**: File-based under `packages/ta5py/spec/`:
- `official/sources.manifest.yaml` — known official publications
- `governance/` — detection records, candidate state, approvals, live binding (no patient data)
- Version packages remain `spec/vN/`

**Testing**: pytest with synthetic publication fixtures (HTML/manifest snapshots + fake remote); no live network required for CI; synthetic claim fixtures only.

**Target Platform**: Maintainer tooling on Windows/macOS/Linux + CI scheduled/manual jobs.

**Project Type**: Library + maintainer CLI/scripts inside `packages/ta5py` (Spec Kit docs under `specs/ta5py/002-auto-spec-integration/`).

**Performance Goals**: On-demand detection completes in under 60s against fixtures / typical publication page; package scaffold for a new `vN` from previous version in under 30s locally.

**Constraints**: Ambulance/Krankentransport scope only; never auto-change live default; no Sozialdaten; English Spec Kit artifacts; constitution module path `specs/ta5py/…`; PDF remains authoritative; certification disclaimer unchanged.

**Scale/Scope**: Monitor Anlage 1, 3, 5, Anhang 3 publication entries already modeled in `sources.manifest.yaml`; support discovering a new version label (e.g. v23) and opening one integration branch per package-version identity.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How addressed |
|-----------|--------|---------------|
| I. English-First | PASS | All Spec Kit artifacts in English; German regulatory terms explained |
| II. Modular, Swappable Layers | PASS | Work stays in `format` + git/governance scripts; does not merge cert/transfer/api |
| III. Machine-Readable, Versioned Domain Specs | PASS | New versions land as `packages/ta5py/spec/vN/` via governed branch; adoption is explicit |
| IV. Dual Validation Layers | PASS | Integration still requires package validation; does not weaken syntax vs plausibility split |
| V. Privacy-by-Design & Synthetic Data Only | PASS | Governance state has no patient data; tests use fixtures |
| VI. Liability & Certification Clarity | PASS | Auto-integration prepares interpretations only; human go-live; no Testat claims |
| Tooling (`uv`) | PASS | Scripts and docs use `uv run` |

**Post-design re-check**: PASS — contracts are maintainer CLI + governance file schemas; live binding is explicit and approval-gated; branch-based integration matches constitution “governed change” for new Anlage versions.

## Project Structure

### Documentation (this feature)

```text
specs/ta5py/002-auto-spec-integration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── governance-state.schema.json
│   └── format-spec-governance-cli.md
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks (not created here)
```

### Source Code (repository root)

```text
packages/ta5py/
├── scripts/
│   ├── download_official_pdfs.py          # existing
│   ├── check_official_publications.py     # NEW: detect new/changed packages
│   ├── integrate_spec_candidate.py        # NEW: scaffold on new branch
│   └── approve_live_spec.py               # NEW: human approval + go-live
├── spec/
│   ├── official/
│   │   ├── sources.manifest.yaml          # extended with check metadata
│   │   └── README.md
│   ├── governance/                        # NEW: durable gate state (gitignored secrets none)
│   │   ├── live-version.yaml              # approved live/default binding
│   │   ├── detections/                    # check run records
│   │   └── candidates/                    # per-version candidate files
│   ├── v21/ … v22/ …                      # existing packages
│   └── vN/                                # created by integrate on branch
├── src/format/
│   ├── spec_loader.py                     # read live binding for DEFAULT_VERSION
│   └── governance/                        # NEW: load/validate governance models
│       ├── __init__.py
│       ├── models.py
│       ├── detect.py
│       ├── integrate.py
│       └── approve.py
└── tests/
    ├── test_publication_detect.py
    ├── test_integrate_on_branch.py
    ├── test_approve_live_gate.py
    └── fixtures/governance/
        ├── overview_snapshot.html
        ├── sources_known.yaml
        └── sources_with_new_version.yaml
```

**Structure Decision**: Keep detection/integration/approval inside `packages/ta5py` as maintainer scripts + a small `format.governance` package. Spec Kit feature docs live under `specs/ta5py/002-auto-spec-integration/`. Git branch creation is part of integrate (user directive), not a separate module.

## Complexity Tracking

> No constitution violations requiring justification.
