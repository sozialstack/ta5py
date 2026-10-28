# Contract: ta5py KVNR formal validator

**Owner**: `packages/ta5py`  
**Module**: `ta5py.kvnr` (also re-exported from `ta5py`)  
**Consumers**: leistungen, kassenclearing, ta5py tests/tooling; any caller allowed to depend on ta5py  
**Out of scope**: dtapy (must not import ta5py), insuree/kasse registry lookup, 20- and 30-character Gesamtsystem numbers, issuance-exclusion policy, billing plausibility, changes to `INV.versicherten_id` syntax

## Public type

### `Kvnr` (frozen value type)

| Field / property / method | Meaning |
|---------------------------|---------|
| `letter` | Position 1, stored as `A`–`Z` |
| `serial` | Positions 2–9 (eight digits) |
| `check_digit` | Position 10 |
| `digits` | Full 10-character string (uppercase letter) |
| `body9` | Positions 1–9 (letter + eight digits) |
| `is_formally_valid` | Prüfziffer matches the § 290 Anlage 1 rule |
| `Kvnr.parse(text)` | Dissect a 10-character candidate (Prüfziffer may be wrong) |
| `Kvnr.is_valid(text)` | Formal yes/no; bad structure → `False` |
| `Kvnr.compute_check_digit(body9)` | Prüfziffer character from letter + eight digits |

### `KvnrError`

Typed domain error (subclass of `ValueError`) for helpers that must fail fast.

### `Kvnr.parse(text: str) -> Kvnr`

- Trims leading/trailing whitespace.
- Case-folds a single leading ASCII letter (`a`–`z` → `A`–`Z`).
- Requires exactly one letter and nine digits; otherwise raises `KvnrError`.
- Does **not** require a correct Prüfziffer (inspect via `is_formally_valid`).
- Does **not** accept 20- or 30-character forms, separators, or umlauts.
- Does **not** reject issuance-excluded patterns that still satisfy the Prüfziffer.

### `Kvnr.is_valid(text: str) -> bool`

- `True` iff `Kvnr.parse(text).is_formally_valid`; structurally bad input → `False` (no exception).

### `Kvnr.compute_check_digit(body9: str) -> str`

- Input: after trim and leading-letter case-fold, exactly one ASCII letter plus eight digits.
- Returns one digit character: sum of weighted digit-sums modulo 10 (see [data-model.md](../data-model.md)).
- Raises `KvnrError` on bad input.
- Does **not** use complement-to-10.

## Error / result conventions

| Case | Behavior |
|------|----------|
| Invalid KVNR for `Kvnr.is_valid` | `False` |
| Bad input to `parse` / `compute_check_digit` | `KvnrError` |
| Formal OK | Never implies the number was issued, the person is insured, payer acceptance, or project Testat |

## Test anchors (synthetic)

| Input | Expected |
|-------|----------|
| `Kvnr.parse("A000500015")` | `letter` `A`, `serial` `00050001`, `check_digit` `5`; `is_formally_valid` True |
| `Kvnr.parse(" a000500015 ")` | Same parts; formally valid (trim + case-fold) |
| `Kvnr.parse("A000500016")` | `is_formally_valid` False |
| `Kvnr.is_valid("C000500021")` | True |
| `Kvnr.is_valid("A000000002")` | True (allowlisted synthetic series; not the complement digit `8`) |
| `Kvnr.compute_check_digit("A00050001")` | `"5"` |
| `Kvnr.compute_check_digit("A00000000")` | `"2"` |
| `Kvnr.is_valid("A0005000151099111144")` | False (20-character form; wrong length) |
| Empty, internal space, umlaut, non-letter first character | `Kvnr.is_valid` False; `parse` / `compute_check_digit` raise `KvnrError` |
