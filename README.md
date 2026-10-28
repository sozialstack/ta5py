# ta5py

SGB V TA5/EDIFACT encode/decode and syntactic KK validation for Krankentransport (SLLA:E).

## Institutskennung (IK) formal check

Offline Prüfziffer validation via the `Ik` value type: `Ik.parse`, `Ik.is_valid`, `Ik.compute_check_digit`, parts + `is_formally_valid`, and seven-digit Kassennummer expansion with prefix `10` (`Ik.from_kassennummer`). Formal OK does not mean registry existence or payer Testat; Ersatzkennzeichen that satisfy the check digit pass the default check. German operator note: `docs/de/ik.md`.

## LANR and BSNR formal checks

Offline formal validators mirroring the `Ik` pattern:

- **LANR** (`Lanr`): nine digits; Prüfziffer at position 7 from positions 1–6 (weights 4,9,4,9,4,9). Specialty (positions 8–9) is not catalog-validated. German operator note: `docs/de/lanr.md`.
- **BSNR** (`Bsnr`): nine digits structure only (no public Prüfziffer). KV-prefix catalogs are not enforced by default. German operator note: `docs/de/bsnr.md`.

Formal OK does not mean physician/practice assignment or payer Testat.

## Krankenversichertennummer (KVNR) formal check

Offline Prüfziffer validation of the 10-character unchanging insuree number via the `Kvnr` value type: `Kvnr.parse`, `Kvnr.is_valid`, `Kvnr.compute_check_digit`, parts + `is_formally_valid`. The check digit is sum modulo 10 per Anlage 1 zur Richtlinie nach § 290 SGB V (not the complement-to-10 rule used for IK and LANR). Formal OK does not mean the number was issued, the person is insured, or payer Testat. Issuance exclusions and the 20-/30-character fund-internal numbers are out of scope. The TA5 Versicherten-Nummer field is unchanged. German operator note: `docs/de/kvnr.md`.

## Kostenträger IK verification (§ 302)

Registry check against the loaded GKV-Spitzenverband SLE Kostenträgerdatei (EDIFACT from [gkv-datenaustausch.de](https://www.gkv-datenaustausch.de/leistungserbringer/sonstige_leistungserbringer/kostentraegerdateien_sle/kostentraegerdateien.jsp)): `verify_kostentraeger_ik` / `resolve_acceptance_ik` answer existence and the selected acceptance/billing recipient IK. Refresh with `make download-kostentraeger` (gitignored `var/kostentraeger/`); verify itself is offline against the ingested store. A registry hit is not a Testat. German operator note: `docs/de/kostentraeger-ik.md`.

## Specs

- Live/default: `src/ta5py/spec/governance/live-version.yaml` (bootstrap `v21`) — **human approve + go-live required to change**
- Preview packages: e.g. `src/ta5py/spec/v22/` (selectable explicitly; not live until approved)
- Legacy stub: `src/ta5py/spec/v20/` (non-default JSON schema)
- Official PDFs (tracked): `spec/docs/` — refresh with `make download-format-pdfs` (also writes Markdown companions; PDFs kept)
- Refresh Markdown for all local PDFs: `make convert-pdfs` (never deletes PDFs)
- Current SLE Kostenträgerdateien (gitignored cache): `make download-kostentraeger` → `var/kostentraeger/` + `store.json`

This project is **not** payer-certified (no Testat). Deployers own Trust Center registration and operational compliance.

## Spec governance (detect → branch → approve)

```bash
# Offline detect (YAML fixture or overview HTML); --on-demand is default (detect-only)
uv run python scripts/check_official_publications.py \
  --on-demand \
  --fixture tests/fixtures/governance/sources_with_new_version.yaml --json

# HTML overview snapshot (no live network)
uv run python scripts/check_official_publications.py \
  --overview-html tests/fixtures/governance/overview_snapshot.html

# On-demand auto-scaffold (still does NOT flip live)
uv run python scripts/check_official_publications.py \
  --fixture … --auto-integrate

# Scheduled/periodic check: auto-integrate is the default; live binding unchanged
uv run python scripts/check_official_publications.py \
  --scheduled --network --update-manifest-metadata

# Dry run of a scheduled check (detect only)
uv run python scripts/check_official_publications.py \
  --scheduled --detect-only --network

# Or live overview fetch (writes check metadata when --update-manifest-metadata)
uv run python scripts/check_official_publications.py --network --update-manifest-metadata

# Scaffold on a new branch (does NOT change live default); duplicate open → exit 3
uv run python scripts/integrate_spec_candidate.py --from-latest-new

# Go-live without --approve must fail
uv run python scripts/approve_live_spec.py --candidate v23 --actor you --go-live

# Approve then go live (older-over-newer requires --confirm-older)
uv run python scripts/approve_live_spec.py \
  --candidate v23 --actor you --approve --go-live

uv run python scripts/governance_status.py
```

Automatic detect/integrate never flips the live package. See `src/ta5py/spec/governance/README.md`.

## Example (v21 SLLA:E)

```python
import json
from pathlib import Path
from ta5py import encode, decode, validate_syntax, load_package

assert load_package("v21")["provenance"]["scope"] == "krankentransport"
claim = json.loads(Path("tests/fixtures/synthetic/slla_e/happy_claim.json").read_text())
result = encode(claim, "v21")
assert result.syntax_ok
decoded = decode(result.output_uri, "v21")
assert validate_syntax(result.output_uri, "v21").syntax_ok
```

Synthetic fixtures only — never use real Sozialdaten. Fixture trees are scanned by
`uv run python scripts/check_synthetic_fixtures.py` (allowlisted synthetic KVNR series
`A00000000N` / `SYNTH*` / `TEST*` only).

Install deps with `uv sync --group dev`.
