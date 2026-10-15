# Data Model: LANR and BSNR Formal Validators

## Entities

### Lebenslange Arztnummer (LANR)

Immutable value type (`Lanr`) dissected from a nine-digit string:

| Field | Description | Validation |
|-------|-------------|------------|
| `digits` | Nine decimal digit characters (derived) | After trim: `len == 9` and all digits to parse |
| `physician` | Positions 1–6 (1-based) | Exactly six digits; used in Prüfziffer |
| `check_digit` | Position 7 | Exactly one digit; formal OK iff equals computed Prüfziffer |
| `specialty` | Positions 8–9 (Arztgruppenschlüssel) | Exactly two digits; **not** used in Prüfziffer |

**Relationships**: Standalone identifier value; may appear on messages and billing handoffs. This feature does not model physician master data or specialty catalogs.

**State**: Frozen value. `Lanr.parse` accepts structurally nine-digit candidates even when the Prüfziffer is wrong; `is_formally_valid` reports the Prüfziffer outcome.

### LANR Prüfziffer computation (derived)

Inputs: characters at positions 1–6.

1. Index those six digits left-to-right as `i = 0..5`.
2. Weight = `4` if `i` even, else `9` (sequence 4,9,4,9,4,9).
3. `product = digit * weight` (no Quersumme / no subtract-9 reduction).
4. `check = (10 - (sum(products) % 10)) % 10`.
5. Valid iff `check == int(position 7)`.

### Betriebsstättennummer (BSNR)

Immutable value type (`Bsnr`) dissected from a nine-digit string:

| Field | Description | Validation |
|-------|-------------|------------|
| `digits` | Nine decimal digit characters (derived) | After trim: `len == 9` and all digits to parse |
| `kv_region` | Positions 1–2 (KV Landes-/Bezirksstellenschlüssel; or special-prefix layout for besondere Versorgungsbereiche) | Exactly two digits; **not** catalog-validated by default |
| `site` | Positions 3–9 | Exactly seven digits |

**Relationships**: Standalone practice-site identifier. No Prüfziffer entity.

**State**: Frozen value. `Bsnr.parse` requires nine digits; `is_formally_valid` is `True` whenever parse succeeded (structure-only formal check).

## Validation rules (summary)

| Rule | Applies to |
|------|------------|
| Trim leading/trailing whitespace before length/digit checks | LANR, BSNR |
| Reject non-digit or wrong length | LANR ≠ 9; BSNR ≠ 9 |
| Prüfziffer over positions 1–6 only (weights 4,9,4,9,4,9; complement-to-10) | LANR |
| No Prüfziffer; no default KV-prefix reject | BSNR |
| Do not consult specialty or KV assignment catalogs | Both |
| Synthetic identifiers only in tests/docs | All fixtures |

## Out of model

- Live physician / Betriebsstätte registries
- Arztgruppenschlüssel semantic catalogs
- KV-prefix accept/reject lists (including special `35` / `75` layouts as business rules)
- Payer acceptance / Testat
- Pseudonym / Ersatz physician number special cases
