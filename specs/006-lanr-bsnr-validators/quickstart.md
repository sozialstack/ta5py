# Quickstart: LANR and BSNR formal validators

Validate that the reusable offline Lebenslange Arztnummer and Betriebsstättennummer checks work end-to-end after implementation (same pattern as the IK quickstart).

## Prerequisites

- Repo root of sozialstack
- `uv` available
- Workspace deps installed (`uv sync` as usual for this monorepo)

## Setup

No network, certificates, or KV registries required. Formal LANR/BSNR validation is pure computation.

## Run checks

From repo root (exact test paths may match once implemented):

```powershell
uv run pytest packages/ta5py/tests/test_lanr.py packages/ta5py/tests/test_bsnr.py -q
```

Optional smoke from a REPL or one-liner:

```powershell
uv run python -c "from ta5py import Lanr, Bsnr; assert Lanr.is_valid('123456601'); assert not Lanr.is_valid('123456901'); assert Bsnr.is_valid('031234567'); print('ok')"
```

## Expected outcomes

1. `123456601` is a formally valid LANR; `123456901` is not ([contracts/lanr-bsnr-validator-api.md](./contracts/lanr-bsnr-validator-api.md)).
2. A synthetic nine-digit BSNR such as `031234567` is formally valid; wrong length / non-digits are not.
3. Docs state that LANR formal validity ≠ specialty/assignment correctness, that BSNR has no public Prüfziffer (structure only), and that neither implies Testat ([data-model.md](./data-model.md)).
4. Public API shape matches the IK pattern (`parse` / `is_valid` / value parts).

## Non-goals for this quickstart

- Looking up physicians or Betriebsstätten in KV registries
- Claiming payer certification
- Enforcing Arztgruppenschlüssel or KV-prefix business catalogs
