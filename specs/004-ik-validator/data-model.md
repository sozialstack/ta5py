# Data Model: Institutskennung (IK) Formal Validator

## Entities

### Institutskennung (IK)

Immutable value type (`Ik`) dissected from a nine-digit string:

| Field | Description | Validation |
|-------|-------------|------------|
| `digits` | Nine decimal digit characters (derived) | After trim: `len == 9` and all digits to parse |
| `classification` | Positions 1–2 (1-based) | Exactly two digits; **not** used in Prüfziffer |
| `region` | Positions 3–4 | Exactly two digits; used in Prüfziffer |
| `serial` | Positions 5–8 | Exactly four digits; used in Prüfziffer |
| `check_digit` | Position 9 | Exactly one digit; formal OK iff equals computed Prüfziffer |

**Relationships**: Standalone identifier value; may appear on messages, directories, and billing handoffs. This feature does not model institution master data.

**State**: Frozen value. `Ik.parse` accepts structurally nine-digit candidates even when the Prüfziffer is wrong; `is_formally_valid` reports the Prüfziffer outcome. Expansion helpers raise on bad length.

### Prüfziffer computation (derived)

Inputs: characters at positions 3–8.

1. Index those six digits left-to-right as `i = 0..5`.
2. Weight = `2` if `i` even, else `1`.
3. `product = digit * weight`; if `product > 9` then `product -= 9`.
4. `check = sum(products) % 10`.
5. Valid iff `check == int(position 9)`.

### Kassennummer (legacy)

| Field | Description | Validation |
|-------|-------------|------------|
| `digits` | Seven decimal digits | After trim: `len == 7` and all digits |

**Expansion**: Candidate IK = `"10" + digits`. Formal validity of the candidate is independent and uses the same Prüfziffer rule.

### Ersatzkennzeichen

IK-shaped nine-digit values (e.g. Selbstzahler patterns such as `97…`) that may satisfy the Prüfziffer. No distinct stored type in v1: they are ordinary IK strings for the formal check. Policy exclusion is out of model scope.

## Validation rules (summary)

| Rule | Applies to |
|------|------------|
| Trim leading/trailing whitespace before length/digit checks | IK, Kassennummer |
| Reject non-digit or wrong length | IK ≠ 9; Kassennummer ≠ 7 |
| Prüfziffer over positions 3–8 only | IK |
| Do not auto-expand inside the nine-digit check | IK |
| Synthetic identifiers only in tests/docs | All fixtures |

## Out of model

- Live institution registry / Annahmeliste membership
- Classification or Bundesland semantic catalogs
- Payer acceptance / Testat
- Optional Ersatzkennzeichen exclusion policy
