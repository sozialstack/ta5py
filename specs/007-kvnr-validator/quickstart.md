# Quickstart: Krankenversichertennummer formal validator

Validate that the reusable offline 10-character KVNR check works end-to-end after implementation (same pattern as the IK and LANR quickstarts).

## Prerequisites

- Repo root of sozialstack
- `uv` available
- Workspace deps installed (`uv sync` as usual for this monorepo)

## Setup

No network, insuree registry, or Krankenkasse directory is required. Formal KVNR validation is pure computation.

## Run checks

From repo root (exact test path matches once implemented):

```powershell
uv run pytest packages/ta5py/tests/test_kvnr.py -q
```

Optional smoke from a one-liner:

```powershell
uv run python -c "from ta5py import Kvnr; assert Kvnr.is_valid('A000500015'); assert not Kvnr.is_valid('A000500016'); assert Kvnr.is_valid('A000000002'); assert Kvnr.compute_check_digit('A00050001') == '5'; print('ok')"
```

## Expected outcomes

1. `A000500015` is formally valid; `A000500016` is not ([contracts/kvnr-validator-api.md](./contracts/kvnr-validator-api.md)).
2. `A000000002` is formally valid. That digit is sum modulo 10; the complement-to-10 digit would be `8`.
3. A 20-character fund-internal number is not valid for this check.
4. Docs state that formal validity covers only the 10-character card number, does not apply issuance exclusions, and does not mean issued, insured, or testiert ([data-model.md](./data-model.md)).
5. Public API shape matches the IK/LANR pattern (`parse` / `is_valid` / value parts / `compute_check_digit`).
6. `INV.versicherten_id` syntax is unchanged (`..12` alphanumeric, conditional).

## Non-goals for this quickstart

- Looking up insurees or Krankenkassen
- Checking 20- or 30-character Gesamtsystem numbers
- Rejecting `666` or long identical-digit runs
- Claiming payer certification
