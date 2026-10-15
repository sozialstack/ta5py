# Contract: ta5py LANR and BSNR formal validators

**Owner**: `packages/ta5py`  
**Modules**: `ta5py.lanr`, `ta5py.bsnr` (also re-exported from `ta5py`)  
**Pattern**: Same as `ta5py.ik` / `Ik`  
**Consumers**: leistungen, kassenclearing, ta5py tests/tooling; any caller allowed to depend on ta5py  
**Out of scope**: dtapy (must not import ta5py), directory/KV registry lookup, specialty-code / KV-prefix business exclusion, billing plausibility

## Public type: `Lanr` (frozen value type)

| Field / property / method | Meaning |
|---------------------------|---------|
| `physician` | Positions 1–6 (digit string); used in Prüfziffer |
| `check_digit` | Position 7 |
| `specialty` | Positions 8–9 (Arztgruppenschlüssel); not used in Prüfziffer |
| `digits` | Full nine-digit string |
| `body6` | Positions 1–6 |
| `is_formally_valid` | Prüfziffer matches positions 1–6 |
| `Lanr.parse(text)` | Dissect nine digits (Prüfziffer may be wrong) |
| `Lanr.is_valid(text)` | Formal yes/no; bad structure → `False` |
| `Lanr.compute_check_digit(body6)` | Prüfziffer character from six-digit physician body |

### `Lanr.parse(text: str) -> Lanr`

- Trims leading/trailing whitespace.
- Requires exactly nine digits; otherwise raises `LanrError`.
- Does **not** require a correct Prüfziffer (inspect via `is_formally_valid`).
- Does **not** validate Arztgruppenschlüssel catalogs.

### `Lanr.is_valid(text: str) -> bool`

- `True` iff `Lanr.parse(text).is_formally_valid`; structurally bad input → `False` (no exception).

### `Lanr.compute_check_digit(body6: str) -> str`

- Input: exactly six digits after trim; returns one digit character.
- Algorithm: weights 4,9,4,9,4,9; `check = (10 - (sum % 10)) % 10`.
- Raises `LanrError` on bad input.

## Public type: `Bsnr` (frozen value type)

| Field / property / method | Meaning |
|---------------------------|---------|
| `kv_region` | Positions 1–2 |
| `site` | Positions 3–9 |
| `digits` | Full nine-digit string |
| `is_formally_valid` | Always `True` for a successfully parsed `Bsnr` (structure-only) |
| `Bsnr.parse(text)` | Dissect nine digits |
| `Bsnr.is_valid(text)` | Formal yes/no; bad structure → `False` |

### `Bsnr.parse(text: str) -> Bsnr`

- Trims leading/trailing whitespace.
- Requires exactly nine digits; otherwise raises `BsnrError`.
- Does **not** apply a Prüfziffer.
- Does **not** reject unknown KV prefixes.

### `Bsnr.is_valid(text: str) -> bool`

- `True` iff `Bsnr.parse(text)` succeeds; structurally bad input → `False` (no exception).

## Error / result conventions

| Case | Behavior |
|------|----------|
| Invalid LANR/BSNR for `is_valid` | `False` |
| Bad input to `parse` / `Lanr.compute_check_digit` | `LanrError` / `BsnrError` |
| Formal OK | Never implies KV assignment, specialty correctness, payer acceptance, or project Testat |

## Test anchors (synthetic)

| Input | Expected |
|-------|----------|
| `Lanr.parse("123456601")` | parts `123456` / `6` / `01`; `is_formally_valid` True |
| `Lanr.parse("123456901")` | `is_formally_valid` False |
| `Lanr.compute_check_digit("123456")` | `"6"` |
| `234567701`, `100000601`, `987654401` | `Lanr.is_valid` True |
| `Bsnr.parse("031234567")` | parts `03` / `1234567`; `is_formally_valid` True |
| `Bsnr.is_valid("03123456")` | False (wrong length) |
| `Bsnr.is_valid("03123456a")` | False |
