# Quickstart: Kostenträger IK Verification (§ 302)

Validate end-to-end that a card IK can be checked against a loaded Kostenträgerdatei and that the § 302 recipient IK resolves from Verknüpfungen. See [contracts/kostentraeger-ik-verify-api.md](./contracts/kostentraeger-ik-verify-api.md) and [data-model.md](./data-model.md).

## Prerequisites

- Repo checkout with `uv` available
- Synthetic fixture (no production `.ke*` required for CI):  
  `packages/ta5py/tests/fixtures/synthetic/kostentraeger/anhang3_kotr.edifact`

## 1. Ingest synthetic file into a store

```powershell
# From repo root — after implement exposes the verify helpers, the same ingest path as today:
uv run python -c "from pathlib import Path; from ta5py.kostentraeger import ingest_kostentraeger_file; p=Path('packages/ta5py/tests/fixtures/synthetic/kostentraeger/anhang3_kotr.edifact'); s=ingest_kostentraeger_file(p,'v21'); print(len(s), s.lookup('123456789'))"
```

Expected: store length ≥ 1; lookup for synthetic `123456789` includes acceptance IK `111222333`.

## 2. Verify existence + recipient (target API)

After implementation, run the package tests (preferred) or a one-liner using `verify_kostentraeger_ik` / store method per the contract:

```powershell
uv run pytest packages/ta5py/tests/test_kostentraeger_lookup.py -q
# plus any new verify-focused tests added for this feature
```

Expected:

| Candidate | Result |
|-----------|--------|
| `123456789` | found, recipient `111222333` |
| `000000000` | not found |
| (no store) | registry unavailable |

## 3. Operator refresh from official channel (optional, network)

```powershell
uv run python packages/ta5py/scripts/download_kostentraeger.py
# or: make download-kostentraeger
```

Writes gitignored files under `packages/ta5py/var/kostentraeger/`. Re-ingest into `store.json`, then verify against that store. Do **not** commit live `.ke*` files or use them as CI fixtures.

## 4. Compose with formal IK check (optional)

```text
Ik.is_valid(card)     → formal shape / Prüfziffer (feature 004)
verify_kostentraeger_ik(store, card) → registry + § 302 recipient (this feature)
```

Formal OK does not imply registry presence; registry presence does not imply Testat.

## Success signal

- Synthetic suite matches [SC-001](./spec.md) / [SC-002](./spec.md) expectations in contract test anchors.
- Docs state Kostenträgerdatei as authoritative source and registry hit ≠ Testat ([SC-005](./spec.md)).
