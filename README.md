# ta5py

SGB V TA5/EDIFACT encode/decode and syntactic KK validation for Krankentransport (SLLA:E).

## Specs

- Live/default: `spec/governance/live-version.yaml` (bootstrap `v21`) — **human approve + go-live required to change**
- Preview packages: e.g. `spec/v22/` (selectable explicitly; not live until approved)
- Legacy stub: `spec/v20/` (non-default JSON schema)
- Official PDFs (gitignored): `spec/docs/` — fetch with `make download-format-pdfs` (also writes Markdown companions; PDFs kept)
- Refresh Markdown for all local PDFs: `make convert-pdfs` (never deletes PDFs)

This project is **not** payer-certified (no Testat). Deployers own Trust Center registration and operational compliance.

## Spec governance (detect → branch → approve)

```bash
# Offline detect (YAML fixture or overview HTML); --on-demand is default (detect-only)
uv run python packages/ta5py/scripts/check_official_publications.py \
  --on-demand \
  --fixture packages/ta5py/tests/fixtures/governance/sources_with_new_version.yaml --json

# HTML overview snapshot (no live network)
uv run python packages/ta5py/scripts/check_official_publications.py \
  --overview-html packages/ta5py/tests/fixtures/governance/overview_snapshot.html

# On-demand auto-scaffold (still does NOT flip live)
uv run python packages/ta5py/scripts/check_official_publications.py \
  --fixture … --auto-integrate

# Scheduled/periodic check: auto-integrate is the default; live binding unchanged
uv run python packages/ta5py/scripts/check_official_publications.py \
  --scheduled --network --update-manifest-metadata

# Dry run of a scheduled check (detect only)
uv run python packages/ta5py/scripts/check_official_publications.py \
  --scheduled --detect-only --network

# Or live overview fetch (writes check metadata when --update-manifest-metadata)
uv run python packages/ta5py/scripts/check_official_publications.py --network --update-manifest-metadata

# Scaffold on a new branch (does NOT change live default); duplicate open → exit 3
uv run python packages/ta5py/scripts/integrate_spec_candidate.py --from-latest-new

# Go-live without --approve must fail
uv run python packages/ta5py/scripts/approve_live_spec.py --candidate v23 --actor you --go-live

# Approve then go live (older-over-newer requires --confirm-older)
uv run python packages/ta5py/scripts/approve_live_spec.py \
  --candidate v23 --actor you --approve --go-live

uv run python packages/ta5py/scripts/governance_status.py
```

Automatic detect/integrate never flips the live package. See `spec/governance/README.md`.

## Example (v21 SLLA:E)

```python
import json
from pathlib import Path
from ta5py import encode, decode, validate_syntax, load_package

assert load_package("v21")["provenance"]["scope"] == "krankentransport"
claim = json.loads(Path("packages/ta5py/tests/fixtures/synthetic/slla_e/happy_claim.json").read_text())
result = encode(claim, "v21")
assert result.syntax_ok
decoded = decode(result.output_uri, "v21")
assert validate_syntax(result.output_uri, "v21").syntax_ok
```

Synthetic fixtures only — never use real Sozialdaten. Fixture trees are scanned by
`uv run python scripts/check_synthetic_fixtures.py` (allowlisted synthetic KVNR series
`A00000000N` / `SYNTH*` / `TEST*` only).

Install deps with `uv sync --group dev` (workspace includes `ta5py` + PyYAML).
