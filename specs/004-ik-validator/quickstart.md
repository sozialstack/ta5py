# Quickstart: IK formal validator

Validate that the reusable offline Institutskennung check works end-to-end after implementation.

## Prerequisites

- Repo root of sozialstack
- `uv` available
- Workspace deps installed (`uv sync` as usual for this monorepo)

## Setup

No network, certificates, or Kostenträger files required. Formal IK validation is pure computation.

## Run checks

From repo root (exact test path may match `packages/ta5py/tests/test_ik.py` once implemented):

```powershell
uv run pytest packages/ta5py/tests/test_ik.py -q
```

Optional smoke from a REPL or one-liner:

```powershell
uv run python -c "from ta5py import Ik; assert Ik.is_valid('260326822'); assert not Ik.is_valid('260326823'); print('ok')"
```

## Expected outcomes

1. `260326822` is formally valid; `260326823` is not ([contracts/ik-validator-api.md](./contracts/ik-validator-api.md)).
2. Synthetic Ersatzkennzeichen that satisfy the Prüfziffer (e.g. `970000011`) are formally valid under the **default** check.
3. A seven-digit Kassennummer expands with prefix `10`; formal validity of the result follows the same Prüfziffer rule ([data-model.md](./data-model.md)).
4. Docs state that formal validity ≠ registry existence / Testat.

## Non-goals for this quickstart

- Looking up IKs in Annahmelisten or Trust Center directories
- Claiming payer certification
- Excluding Ersatzkennzeichen via a business policy filter
