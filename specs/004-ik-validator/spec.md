# Feature Specification: Institutskennung (IK) Formal Validator

**Feature Branch**: `004-ik-validator`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "i want a reusable validator for Institutskennungen" with formal offline check-digit rules (Gemeinsames Rundschreiben IK / Wikipedia), notes on Ersatzkennzeichen, and 7-digit health-card Kassennummer expansion via prefix 10.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Decide whether a nine-digit IK is formally valid (Priority: P1)

An operator or upstream clearing step has a candidate Institutskennung (IK) as text and needs a clear yes/no formal check before the value is used in messages, directories, or billing handoffs. The check is offline: length, digits only, and the official Prüfziffer over positions 3–8 (classification digits do not enter the sum). Passing formal validation does not mean the institution exists or that a payer will accept the message.

**Why this priority**: Without a shared formal check, invalid IKs leak into every downstream path and produce avoidable rejections.

**Independent Test**: Feed known valid and invalid nine-digit synthetic IKs (including the published example whose digits 1–8 yield check digit 2); only structurally and check-digit-correct values pass.

**Acceptance Scenarios**:

1. **Given** the nine-digit value `260326822`, **When** formal IK validation runs, **Then** the result is valid.
2. **Given** the nine-digit value `260326823` (wrong check digit), **When** formal IK validation runs, **Then** the result is invalid.
3. **Given** a value that is not exactly nine characters or contains a non-digit after ordinary trim of leading/trailing whitespace, **When** formal IK validation runs, **Then** the result is invalid.
4. **Given** any nine-digit synthetic IK whose check digit matches the prescribed weighting of positions 3–8, **When** formal IK validation runs, **Then** the result is valid regardless of classification or regional meaning.

---

### User Story 2 - Reuse one IK check everywhere identifiers appear (Priority: P1)

Maintainers of message formatting, Kostenträger handling, and related operator tooling need one documented formal IK rule so callers do not each reimplement a slightly different check digit. Callers that already depend on the GKV message-shape package can invoke the same validator.

**Why this priority**: “Reusable” is the product ask; duplicated ad-hoc checks are the failure mode this feature removes.

**Independent Test**: The same synthetic valid and invalid IKs produce identical outcomes when validated through the shared formal entry point used by package consumers in tests.

**Acceptance Scenarios**:

1. **Given** a synthetic IK known to be formally valid, **When** two different package-facing callers invoke the shared formal validator, **Then** both receive the same valid outcome.
2. **Given** a synthetic IK that fails the check digit, **When** those callers invoke the shared formal validator, **Then** both receive the same invalid outcome.

---

### User Story 3 - Expand a seven-digit Kassennummer to a nine-digit IK when required (Priority: P2)

Some older health-card material shows a seven-digit Kassennummer. Operators need a documented expansion that prefixes `10` to form a nine-digit IK candidate, then applies the same formal check. Expansion alone does not invent missing digits or invent a check digit; the resulting nine digits must still satisfy the Prüfziffer rule.

**Why this priority**: Common in practice for older cards, but secondary to validating already nine-digit IKs.

**Independent Test**: From a synthetic seven-digit Kassennummer, produce the `10` + seven-digit candidate and show whether that nine-digit form passes formal validation.

**Acceptance Scenarios**:

1. **Given** a seven-digit all-numeric Kassennummer, **When** expansion with prefix `10` is requested, **Then** the candidate IK is exactly `10` followed by those seven digits.
2. **Given** that expanded nine-digit candidate, **When** formal validation runs, **Then** validity follows the same check-digit rule as for any other nine-digit IK.
3. **Given** a value that is not seven digits, **When** Kassennummer expansion is requested, **Then** expansion is refused (no silent padding or truncation).

---

### User Story 4 - Understand that Ersatzkennzeichen can pass formal checks (Priority: P3)

Operators working with Selbstzahler Ersatzkennzeichen (for example values in the `97…` pattern that are formed like ARGE IK rules) need documentation that the formal Prüfziffer check alone does **not** exclude those identifiers. Any business rule that must reject Ersatzkennzeichen is a separate, explicit policy—not part of the default formal validator.

**Why this priority**: Avoids false confidence that “formally valid” means “ordinary institution IK.”

**Independent Test**: Synthetic Ersatzkennzeichen that satisfy the check digit are reported formally valid by the default check; documentation states that exclusion requires a separate rule.

**Acceptance Scenarios**:

1. **Given** a synthetic Ersatzkennzeichen such as `970000011` or `970000099` that satisfies the Prüfziffer, **When** the default formal validator runs, **Then** the result is valid.
2. **Given** project documentation for this feature, **When** an operator asks whether formal validity excludes Selbstzahler Ersatzkennzeichen, **Then** the answer is no unless an explicit separate exclusion rule is applied.

---

### Edge Cases

- Leading or trailing whitespace around an otherwise valid nine-digit IK is ignored for the check; internal spaces or separators are not accepted as part of the digit string.
- Empty input, all spaces, or non-digit characters → formally invalid.
- Values shorter or longer than nine digits (after trim) → formally invalid for the nine-digit check; seven-digit expansion is a separate step and only for exactly seven digits.
- Classification digits (positions 1–2) do not affect the Prüfziffer calculation even when unusual.
- Formal validity never asserts that the IK is assigned, reachable, or accepted by a payer.
- Real insured-person or live institution data MUST NOT appear in tests or public examples; only synthetic identifiers.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a reusable formal (offline) Institutskennung validator that answers whether a candidate string is a formally valid nine-digit IK.
- **FR-002**: A formally valid IK MUST be exactly nine digits after trimming leading and trailing whitespace, with no other characters.
- **FR-003**: The Prüfziffer (ninth digit) MUST be computed from positions 3 through 8 only (1-based), using left-to-right weights 2,1,2,1,2,1; each weighted product greater than 9 MUST be reduced by 9; the check digit MUST equal that sum modulo 10. Classification positions 1–2 MUST NOT enter the sum. This is the Gemeinsames Rundschreiben / Wikipedia rule (not the common Luhn digit-sum variant).
- **FR-004**: The validator MUST accept as formally valid any nine-digit string that meets FR-002 and FR-003, including synthetic Ersatzkennzeichen that satisfy the Prüfziffer.
- **FR-005**: Exclusion of Ersatzkennzeichen or other business classes MUST NOT be part of the default formal check; such policies MAY be documented as optional separate rules outside this feature’s default behavior.
- **FR-006**: The system MUST support expanding an exactly seven-digit numeric Kassennummer to a nine-digit candidate by prefixing `10`, then allowing the same formal check on the result.
- **FR-007**: Formal validation and expansion MUST be usable offline without network access and without looking up directories or certificates.
- **FR-008**: Passing formal validation MUST NOT be presented as proof of institution existence, payer acceptance, or project certification / Testat.
- **FR-009**: Tests, examples, and public artifacts MUST use synthetic IK values only.
- **FR-010**: The shared validator MUST live in the GKV message-shape package so dependents that already consume that package reuse one implementation.

### Key Entities

- **Institutskennung (IK)**: Nine-digit institution identifier: two classification digits, two regional digits, four serial digits, one check digit.
- **Prüfziffer result**: Formal outcome of the weighted sum over positions 3–8 compared to digit 9.
- **Kassennummer (legacy card form)**: Seven-digit numeric identifier that may be expanded to an IK candidate by prefixing `10`.
- **Ersatzkennzeichen**: Special IK-shaped identifiers (e.g. Selbstzahler) that may pass the Prüfziffer; not excluded by default formal validation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a fixed suite of at least ten synthetic nine-digit cases (including `260326822` valid and `260326823` invalid), every case is classified correctly 100% of the time.
- **SC-002**: A caller can obtain a formal yes/no for one IK in under one second on ordinary developer hardware (offline, no directory lookup).
- **SC-003**: Two independent callers using the shared validator agree on validity for 100% of the fixed synthetic suite.
- **SC-004**: Seven-digit expansion with prefix `10` is demonstrated for at least one synthetic Kassennummer, with formal validity of the expanded form reported consistently with FR-003.
- **SC-005**: Operator-facing docs state in plain language that formal validity ≠ registry existence and that Ersatzkennzeichen can pass the default check.

## Assumptions

- Ownership is the GKV message-shape package (`ta5py`): formal IK checking is syntactic identifier validation, not billing plausibility and not Trust Center / transport.
- Default scope is formal structure + Prüfziffer only; semantic meaning of classification/region codes and live directory lookups are out of scope.
- Ersatzkennzeichen remain formally valid under the default check; a dedicated exclusion filter is deferred unless a later feature asks for it.
- Seven-digit → nine-digit expansion uses only the documented `10` prefix (KVB-style guidance cited by the requester); other historical prefixes are out of scope.
- The algorithm description follows the Wikipedia presentation of Gemeinsames Rundschreiben IK 06/2020 (gkv-datenaustausch.de); implementation planning may cite that circular for confirmation.
- Whitespace handling is trim-only; formatted display with spaces or hyphens is not accepted without a prior normalize step outside this feature’s default API.
- Consumers that cannot depend on `ta5py` (e.g. packages forbidden from importing it) are out of scope for this reuse story; they keep their own thin checks or a later shared-contracts feature.
