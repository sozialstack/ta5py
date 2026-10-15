# Research: Institutskennung (IK) Formal Validator

## Decision: Own formal IK validation in `ta5py`

**Rationale**: Project constitution places independently testable syntactic validation in ta5py. An IK Prüfziffer check is offline identifier syntax, not billing plausibility (leistungen) and not Trust Center/transport (dtapy). Feature specs already live under `specs/ta5py/`.

**Alternatives considered**:
- `clearing-contracts` shared helper — would maximize reuse into dtapy, but clearing-contracts today owns protocols/types, not domain algorithms; would blur Principle II ownership and lacks a Spec Kit package constitution home.
- Duplicate thin checks per package — rejected; contradicts the reusable-validator ask.
- `leistungen` only — rejected; IK appears in message shape and Kostenträger paths before billing.

## Decision: Prüfziffer algorithm (positions 3–8, weight 2/1, subtract 9 if product > 9)

**Rationale**: Matches Gemeinsames Rundschreiben IK as summarized on Wikipedia (citing IK 06/2020 on gkv-datenaustausch.de) and the requester’s verified implementation. Classification digits (1–2) are excluded. This is intentionally not the common Luhn digit-sum-of-digits variant.

**Verification anchor**: Digits `26032682` → check digit `2` → `260326822` valid, `260326823` invalid.

**Alternatives considered**:
- Classic Luhn (sum of digits of doubled values) — rejected; diverges from the circular’s “subtract 9 when product > 9” description for this domain.
- Include classification in the sum — rejected; contradicts the cited rule.

## Decision: Default API accepts Ersatzkennzeichen that pass the Prüfziffer

**Rationale**: Spec FR-004/FR-005. Values such as `970000011` / `970000099` are formed analogously to ARGE IK rules and pass formal checks. Excluding them needs an explicit business policy, not a silent formal-check side effect.

**Alternatives considered**:
- Hard-reject `97…` in `is_valid_ik` — rejected for v1; surprises operators and conflates formal vs policy.
- Optional `exclude_ersatz=True` flag in v1 — deferred; keep the default surface minimal; add later if callers need it.

## Decision: Seven-digit Kassennummer → prefix `10`

**Rationale**: Spec FR-006 and KVB-style guidance cited by the requester: older health cards show seven-digit Kassennummern; prefix `10` yields a nine-digit IK candidate that must still satisfy the Prüfziffer.

**Alternatives considered**:
- Auto-detect length inside `is_valid_ik` and expand silently — rejected; keeps formal check predictable (exactly nine digits after trim).
- Support other historical prefixes — out of scope until a regulatory cite requires them.

## Decision: Public surface = pure typed functions

**Rationale**: Principle VII; matches existing ta5py style (`validate_syntax` returns structured results for messages, but IK is a single-field helper). Prefer `is_valid_ik(str) -> bool` plus `expand_kassennummer(str) -> str` (raising or returning a clear error for bad length) so callers compose without inventing parallel algorithms.

**Alternatives considered**:
- Only a `FormatResult`-shaped API — heavier than needed for a single identifier.
- CLI-only — insufficient for reuse from encode/validate paths.

## Decision: Source citation in docs, not a new Anlage YAML package

**Rationale**: The rule is a fixed numeric algorithm, not a versioned segment catalog. Cite Gemeinsames Rundschreiben IK / Wikipedia summary in module docstring and German companion; no new `spec/vN` YAML required for MVP.

**Alternatives considered**:
- Encode weights in YAML under `packages/ta5py/spec/` — possible later for governance theater; adds no testability for v1.
