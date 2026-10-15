# Contract: ta5py IK formal validator

**Owner**: `packages/ta5py`  
**Module**: `ta5py.ik` (also re-exported from `ta5py`)  
**Consumers**: leistungen, kassenclearing, ta5py tests/tooling; any caller allowed to depend on ta5py  
**Out of scope**: dtapy (must not import ta5py), directory/certificate lookup, Ersatzkennzeichen business exclusion, billing plausibility, semantic validation of classification/region catalogs

## Public type

### `Ik` (frozen value type)

| Field / property / method | Meaning |
|---------------------------|---------|
| `classification` | Positions 1–2 (digit string); not used in Prüfziffer |
| `region` | Positions 3–4 |
| `serial` | Positions 5–8 |
| `check_digit` | Position 9 |
| `digits` | Full nine-digit string |
| `body8` | Positions 1–8 |
| `is_formally_valid` | Prüfziffer matches positions 3–8 |
| `Ik.parse(text)` | Dissect nine digits (Prüfziffer may be wrong) |
| `Ik.is_valid(text)` | Formal yes/no; bad structure → `False` |
| `Ik.compute_check_digit(body8)` | Prüfziffer character from eight-digit body |
| `Ik.from_kassennummer(kn)` | Prefix `10` → `Ik` candidate |

### `Ik.parse(text: str) -> Ik`

- Trims leading/trailing whitespace.
- Requires exactly nine digits; otherwise raises `IkError`.
- Does **not** require a correct Prüfziffer (inspect via `is_formally_valid`).
- Does **not** expand seven-digit Kassennummern.
- Does **not** reject Ersatzkennzeichen that satisfy the Prüfziffer.

### `Ik.is_valid(text: str) -> bool`

- `True` iff `Ik.parse(text).is_formally_valid`; structurally bad input → `False` (no exception).

### `Ik.compute_check_digit(body8: str) -> str`

- Input: exactly eight digits after trim; returns one digit character.
- Raises `IkError` on bad input.

### `Ik.from_kassennummer(kassennummer: str) -> Ik`

- Trims; requires exactly seven digits or raises `IkError`.
- Equivalent to `Ik.parse("10" + kassennummer)`.
- Does not assert Prüfziffer validity.

## Error / result conventions

| Case | Behavior |
|------|----------|
| Invalid IK for `Ik.is_valid` | `False` |
| Bad input to `parse` / `from_kassennummer` / `compute_check_digit` | `IkError` |
| Formal OK | Never implies registry existence, payer acceptance, or project Testat |

## Test anchors (synthetic)

| Input | Expected |
|-------|----------|
| `Ik.parse("260326822")` | parts `26`/`03`/`2682`/`2`; `is_formally_valid` True |
| `Ik.parse("260326823")` | `is_formally_valid` False |
| `Ik.compute_check_digit("26032682")` | `"2"` |
| `970000011`, `970000099` | `Ik.is_valid` True |
| `Ik.from_kassennummer("0326822")` | digits `100326822`, formally valid |
