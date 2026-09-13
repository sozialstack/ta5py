# Quickstart: Anlage 1 Slice A (Ambulance / SLLA:E)

Validate that the **format** module loads a v21 ambulance Anlage 1 package and round-trips a synthetic SLLA:E claim to Nutzdaten wire text.

## Prerequisites

- Repo root: `clearing`
- Python ≥ 3.12 with [uv](https://docs.astral.sh/uv/)
- No real patient/Sozialdaten — use fixtures only

## Setup

```bash
uv sync --group dev
```

Confirm package layout exists (after implementation):

- `packages/ta5py/spec/v21/provenance.yaml`
- `packages/ta5py/spec/v21/messages/slla_e.yaml`
- `packages/ta5py/spec/v21/segments/*.yaml`
- Official PDFs via `make download-format-pdfs` → `packages/ta5py/spec/official/`

Contract references:

- [data-model.md](./data-model.md)
- [contracts/format-anlage1-api.md](./contracts/format-anlage1-api.md)
- [contracts/anlage1-package.schema.json](./contracts/anlage1-package.schema.json)

## Run Slice A tests

```bash
uv run pytest packages/ta5py/tests/test_slla_e_roundtrip.py packages/ta5py/tests/test_validate_syntax_anlage1.py -q
```

### Expected

- Spec loader accepts `v21` with `scope: krankentransport`
- At least one synthetic fixture encodes → wire text containing `KTL` and `EKT` segments and ending segments with `'`
- Decode restores logical fields for mandatory SLLA:E elements
- A deliberately broken length/order fixture fails with field-level errors
- A non-ambulance profile fixture fails as `unsupported_scope`

## Manual smoke (after API surface exists)

```bash
uv run python -c "from ta5py.spec_loader import load_package; p=load_package('v21'); print(p['provenance']['scope'], list(p['messages']))"
```

Expected: prints `krankentransport` and includes `slla_e`.

## Privacy check

```bash
# Fixtures must be synthetic; fail CI if real-looking Versichertennummer patterns are introduced
uv run pytest packages/ta5py/tests -q
```

## Out of scope for this quickstart

- Anlage 3 catalog membership  
- Anlage 5 Urbeleg checks  
- Kostenträgerdatei ingest  
- cert / transfer / api job orchestration (see `specs/kassenclearing/001-dfue-kv-api`)
- Anlage 5 Urbeleg content checks (see `packages/leistungen`)

## Next slices

After Slice A is green: add Anlage 3 catalogs → Anhang 3 Kostenträger (see [plan.md](./plan.md)). Anlage 5 Urbeleg content remains leistungen.
