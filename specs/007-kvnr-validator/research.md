# Research: Krankenversichertennummer Formal Validator

## Decision: Own the check in ta5py, same value-type pattern as IK and LANR

**Rationale**: The project constitution places independently testable syntactic validation in ta5py. A KVNR Prüfziffer is offline identifier syntax, not billing plausibility (leistungen) and not Trust Center/transport (dtapy). `ta5py.ik` and `ta5py.lanr` already established frozen dataclasses with `parse`, `is_valid`, `is_formally_valid`, `compute_check_digit`, and a typed error. Callers benefit from the same shape.

**Alternatives considered**:

- Put the check in leistungen — rejected; it is not a Leistungsart or Testat rule.
- Only a boolean helper with no value type — rejected; IK/LANR dissection (letter, serial, check digit) is what operators and tests need.
- Auto-reject `INV.versicherten_id` unless it is a valid KVNR — rejected; Anlage 1 keeps that field `..12` alphanumeric and conditional. Unknown numbers are omitted and address plus date of birth go in NAD.

## Decision: Validate only the 10-character unchanging part

**Rationale**: That is the number on the electronic health card and the shape this repo already treats as KVNR (`letter` + 9 digits) for log redaction and synthetic-data scanning. § 290 SGB V also defines a 20-character member number and a 30-character family-member number (kasse IK, family reference, overall Prüfziffer). Those are fund-internal Gesamtsystem identifiers, not the TA5 Versicherten-Nummer.

**Alternatives considered**:

- Validate 10-, 20-, and 30-character forms in one type — rejected for this feature; different lengths and an embedded IK are a second product. The 10-character check already fails the longer forms by length.
- Treat any `..12` AN string as an insuree number — rejected; that is the message field, not the card number.

## Decision: Prüfziffer = expanded-letter weights 1,2,…, Quersumme, sum modulo 10

**Rationale**: Anlage 1 zur Richtlinie nach § 290 SGB V (calculation sheet, Stand 2 January 2023) and the Richtlinie text: letter → alphabet position `A=01` … `Z=26`; the resulting ten digits (letter expansion + positions 2–9) are multiplied left to right by `1,2,1,2,1,2,1,2,1,2`; each product is reduced by its digit sum; the check digit is the last digit of that sum (sum modulo 10). This is **not** the complement `(10 − (sum % 10)) % 10` used by IK and LANR.

**Verification anchors** (hand-checked against that rule):

| Body (no check digit) | Expanded digits’ digit-sum total | Check digit | Full number |
|-----------------------|----------------------------------|-------------|-------------|
| `A00050001` | 5 | `5` | `A000500015` (Anlage 1 illustration) |
| `C00050002` | 11 | `1` | `C000500021` (Anlage 1 family illustration’s unchanging part) |
| `A00000000` | 2 | `2` | `A000000002` (allowlisted synthetic series; complement-to-10 would yield `8`) |

`A000500016` is the wrong-digit twin of the illustration.

**Alternatives considered**:

- Copy the IK/LANR complement-to-10 helper — rejected; `A000000002` and `C000500021` would be classified wrong.
- ISO 7064 MOD 10,10 — rejected; not the procedure in Anlage 1.

## Decision: Case-fold only the leading ASCII letter; no other normalization

**Rationale**: The official character is a Großbuchstabe, but the alphabet position of `a` and `A` is the same, and operators paste either case. Trim leading/trailing whitespace, then map `a`–`z` to `A`–`Z` at position 1 only. Internal spaces, hyphens, umlauts, and letters after position 1 stay invalid, matching IK/LANR “no silent reformatting.”

**Alternatives considered**:

- Require uppercase only — rejected; it fails the same number for a casing accident without changing the check.
- Strip separators — rejected; out of scope, same as IK.

## Decision: Do not enforce issuance exclusions

**Rationale**: The Richtlinie forbids the issuing body from using umlauts, the sequence `666`, or more than three identical digits in a row. Those are generation rules, not the receiver’s Prüfziffer. Enforcing them would reject the allowlisted synthetic anchor `A000000002` (eight zeros) and would claim knowledge this check does not have. Same stance as IK: Ersatzkennzeichen that satisfy the Prüfziffer still pass the default formal check.

**Alternatives considered**:

- Reject `666` and runs of four or more — rejected as business policy, not formal syntax.

## Decision: Tests may cite the published illustration; do not put it in scanned fixture trees

**Rationale**: Principle IV forbids real Sozialdaten. `A000500015` is the public arithmetic example in Anlage 1, not an issued insuree number. Unit tests under `packages/ta5py/tests/` are not in the default roots of `scripts/check_synthetic_fixtures.py` (that scan covers fixture directories and flags non-allowlisted `[A-Z][0-9]{9}` tokens). Prefer `A000000002` if a value must live in a scanned fixture. Do not add real card numbers.

**Alternatives considered**:

- Only allowlisted `A00000000x` values — sufficient for CI fixtures, too narrow for the spec’s published-illustration acceptance scenario in unit tests.
