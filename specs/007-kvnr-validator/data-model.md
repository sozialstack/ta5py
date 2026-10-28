# Data Model: Krankenversichertennummer Formal Validator

## Entities

### Krankenversichertennummer (unchanging part)

Immutable value type (`Kvnr`) dissected from a 10-character string:

| Field | Description | Validation |
|-------|-------------|------------|
| `letter` | Position 1 | One ASCII letter stored as `A`–`Z`; input `a`–`z` folds to uppercase |
| `serial` | Positions 2–9 | Exactly eight digits; used in the Prüfziffer |
| `check_digit` | Position 10 | Exactly one digit; formal OK iff it equals the computed Prüfziffer |
| `digits` | Full 10-character string (derived) | Uppercase letter + nine digits |
| `body9` | Positions 1–9 without Prüfziffer (derived) | Uppercase letter + eight digits |

**Relationships**: Standalone card-number value. May be offered by a caller who already holds a candidate KVNR. This feature does not model insuree master data, kasse membership, or the TA5 `INV` field.

**State**: Frozen value. `Kvnr.parse` accepts a structurally 10-character candidate even when the Prüfziffer is wrong; `is_formally_valid` reports the Prüfziffer outcome.

### KVNR Prüfziffer computation (derived)

Inputs: the leading letter and positions 2–9 (the body without position 10).

1. Map the letter to two digits: `A`/`a` = `01` … `Z`/`z` = `26`.
2. Concatenate those two digits with positions 2–9. Result: ten digits.
3. Multiply left to right by weights `1,2,1,2,1,2,1,2,1,2`.
4. Replace each product by its digit sum (for a product of a single digit times 1 or 2, that is the product itself when ≤ 9, otherwise the product minus 9).
5. `check = sum(digit sums) % 10`.
6. Valid iff `check == int(position 10)`.

Worked results: body `A00050001` → `5`; body `C00050002` → `1`; body `A00000000` → `2`.

## Validation rules (summary)

| Rule | Applies to |
|------|------------|
| Trim leading/trailing whitespace, then case-fold position 1 | KVNR |
| Reject unless one ASCII letter plus exactly nine digits | KVNR |
| Prüfziffer = sum modulo 10 over expanded letter + positions 2–9 | KVNR |
| Do not apply issuance bans (`666`, runs of more than three identical digits) | KVNR |
| Do not accept 20- or 30-character Gesamtsystem numbers | KVNR |
| Do not consult insuree or Krankenkasse registries | KVNR |
| Do not change `INV.versicherten_id` (`..12` AN, conditional) | Message syntax |
| Synthetic identifiers only in tests and docs | All fixtures |

## Out of model

- 20-character member KVNR and 30-character family-member KVNR (embedded IK and overall Prüfziffer)
- Rentenversicherungsnummer
- Live issuance / Versichertenverzeichnis lookup
- Issuance exclusions as accept/reject rules
- Payer acceptance / Testat
- Mandatory validation of the TA5 Versicherten-Nummer field
