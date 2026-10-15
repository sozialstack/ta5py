# Research: LANR and BSNR Formal Validators

## Decision: Own formal LANR/BSNR validation in `ta5py` (same ownership as IK)

**Rationale**: Project constitution places independently testable syntactic validation in ta5py. LANR Prüfziffer and BSNR digit-structure checks are offline identifier syntax, not billing plausibility (leistungen) and not Trust Center/transport (dtapy). Feature specs already live under `specs/ta5py/`. Requester asked to mirror the IK pattern.

**Alternatives considered**:
- `clearing-contracts` shared helper — rejected for the same reasons as IK; would blur Principle II ownership.
- Duplicate thin checks per package — rejected; contradicts the reusable-validator ask.
- `leistungen` only — rejected; LANR/BSNR appear in message shape fields before billing.

## Decision: Mirror the `Ik` value-type API pattern

**Rationale**: `ta5py.ik` already established `Ik` as a frozen dataclass with `parse`, `is_valid`, `is_formally_valid`, `compute_check_digit`, and typed `IkError`. Operators and callers benefit from the same shape for LANR and BSNR.

**API mapping**:

| IK (`ta5py.ik`) | LANR (`ta5py.lanr`) | BSNR (`ta5py.bsnr`) |
|-----------------|---------------------|---------------------|
| `Ik` | `Lanr` | `Bsnr` |
| `IkError` | `LanrError` | `BsnrError` |
| `parse` / `is_valid` | same | same |
| `compute_check_digit` | yes (positions 1–6) | N/A (no public Prüfziffer) |
| `from_kassennummer` | N/A | N/A |
| parts | physician6 / check / specialty2 | kv_region2 / site7 |

**Alternatives considered**:
- Single module `ta5py.identifiers` housing Ik/Lanr/Bsnr — possible later refactor; for this feature keep parity with existing `ik.py` file layout.
- Bool-only helpers without value types — rejected; loses dissection and consistency with IK.

## Decision: LANR Prüfziffer = weights 4,9,4,9,4,9; complement-to-10 (no Quersumme)

**Rationale**: KBV Arztnummern-Richtlinie (§ 75 Abs. 7 SGB V): nine digits; Prüfziffer at position 7 from positions 1–6; Arztgruppenschlüssel at 8–9 excluded. Published description: multiply left-to-right with alternating 4 and 9; sum modulo 10; check = difference to 10 (zero when remainder is 0) — equivalently `(10 − (sum % 10)) % 10`. Products are **not** reduced by Quersumme (confirmed by community implementations aligned to the Richtlinie).

**Verification anchor**: Digits `123456` → check digit `6` → `123456601` valid, `123456901` invalid. Additional synthetic anchors: `234567701`, `100000601`, `987654401`, `555555501`, `999999901`.

**Alternatives considered**:
- Quersumme of each weighted product before summing — rejected; diverges from primary-source / verified anchors.
- Include Arztgruppenschlüssel in the sum — rejected; contradicts the Richtlinie.

## Decision: BSNR default formal check = nine digits only (no Prüfziffer, no KV whitelist reject)

**Rationale**: KBV Arztnummern-Richtlinie defines BSNR as nine digits (positions 1–2 KV Landes-/Bezirksstellenschlüssel; 3–9 KV-assigned) and does **not** publish a Prüfziffer. Spec FR-006. Exposing `kv_region` / `site` parts mirrors IK’s dissection without inventing a checksum. Hard-rejecting unknown KV prefixes would be a business catalog policy, not a formal structural gate (and special prefixes `35`/`75` further complicate naive whitelists).

**Alternatives considered**:
- Invent or adopt an undocumented BSNR check digit — rejected; no primary source.
- Default-reject non-Anlage-1 KV prefixes — deferred; too aggressive for a `\d{9}` formal gate; document parts only.
- Treat BSNR `is_formally_valid` as always True when parse succeeds — accepted; keeps API symmetry with `Ik`/`Lanr`.

## Decision: Source citation in docs, not a new Anlage YAML package

**Rationale**: Fixed numeric/structure rules, not a versioned segment catalog. Cite KBV Arztnummern-Richtlinie in module docstrings and German companions; no new `spec/vN` YAML required for MVP.

**Alternatives considered**:
- Encode LANR weights / BSNR KV list in YAML under `packages/ta5py/spec/` — possible later; adds no testability for v1.
