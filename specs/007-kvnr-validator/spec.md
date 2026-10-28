# Feature Specification: Krankenversichertennummer Formal Validator

**Feature Branch**: `007-kvnr-validator`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "we need a validator for insuree numbers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Decide whether a 10-character insuree number is formally valid (Priority: P1)

An operator or upstream clearing step has a candidate Krankenversichertennummer (KVNR; the insuree number printed on the electronic health card) as text and needs a clear yes/no formal check before the value is used in messages or billing handoffs. The check is offline and covers only the 10-character unchanging part: one letter, eight digits, and the official Prüfziffer at position 10. Passing formal validation does not mean the person is insured, that the number was issued, or that a payer will accept the message.

**Why this priority**: Invalid insuree numbers leak into every path that carries insured-person identifiers; a shared formal check removes avoidable rejections.

**Independent Test**: Feed the published Richtlinie illustration and a wrong-check-digit twin; only the check-digit-correct 10-character value passes.

**Acceptance Scenarios**:

1. **Given** the 10-character value `A000500015` (published § 290 Anlage 1 illustration), **When** formal KVNR validation runs, **Then** the result is valid.
2. **Given** the 10-character value `A000500016` (wrong check digit), **When** formal KVNR validation runs, **Then** the result is invalid.
3. **Given** a value that is not exactly one letter plus nine digits after ordinary trim of leading/trailing whitespace, **When** formal KVNR validation runs, **Then** the result is invalid.
4. **Given** the same digits with a lowercase leading letter (`a000500015`), **When** formal KVNR validation runs, **Then** the result is valid (the letter is the same alphabet position).

---

### User Story 2 - Reuse one insuree-number check everywhere the identifier appears (Priority: P1)

Maintainers of message formatting and related operator tooling need one documented formal rule so callers do not each reimplement a slightly different check. Callers that already depend on the GKV message-shape package can invoke the same validator, mirroring the existing Institutskennung (IK) and Lebenslange Arztnummer (LANR) pattern.

**Why this priority**: A reusable shared check is the product ask; duplicated ad-hoc checks are the failure mode.

**Independent Test**: The same synthetic valid and invalid KVNR values produce identical outcomes when validated through the shared formal entry points used by package consumers in tests.

**Acceptance Scenarios**:

1. **Given** a synthetic KVNR known to be formally valid, **When** two different package-facing callers invoke the shared formal validator, **Then** both receive the same valid outcome.
2. **Given** a synthetic KVNR that fails the Prüfziffer, **When** those callers invoke the shared formal validator, **Then** both receive the same invalid outcome.

---

### User Story 3 - Understand formal OK ≠ insured, issued, or payer acceptance (Priority: P2)

Operators need documentation that a formal KVNR check does **not** prove the number was issued, that the person is insured, or that a payer will accept a message. Issuance restrictions used when numbers are created (for example excluding `666` or long runs of the same digit) are separate from the default formal check. The longer 20- and 30-character fund-internal numbers (kasse IK plus an overall Prüfziffer, and the family-member form) are a different identifier and are not what this check answers.

**Why this priority**: Avoids false confidence; parallel to the IK and LANR “formal ≠ registry / Testat” story.

**Independent Test**: Documentation states the limits; a 10-character value that only satisfies structure and Prüfziffer passes without any registry lookup, including a synthetic value that would fail an issuance exclusion.

**Acceptance Scenarios**:

1. **Given** a formally valid synthetic KVNR, **When** the default formal validator runs, **Then** the result is valid without consulting an insuree registry or a Krankenkasse directory.
2. **Given** a 10-character synthetic value whose Prüfziffer is correct but which contains a long run of identical digits, **When** the default formal validator runs, **Then** the result remains valid (issuance exclusions are not applied).
3. **Given** project documentation, **When** an operator asks whether formal validity means the person is insured or the project is testiert, **Then** the answer is no.
4. **Given** a 20- or 30-character fund-internal KVNR, **When** the default formal validator for the card number runs, **Then** the result is invalid for this check (wrong length), and documentation states that the longer form is out of scope.

---

### Edge Cases

- Leading or trailing whitespace around an otherwise valid 10-character KVNR is ignored; internal spaces, hyphens, or other separators are not accepted.
- Empty input, all spaces, umlauts, digits in the letter position, or a letter after the first character → formally invalid.
- Values shorter or longer than 10 characters after trim (including the 20- and 30-character fund-internal forms) → formally invalid for this check.
- The Prüfziffer is the last digit of the weighted sum (sum modulo 10), not the complement to the next multiple of 10.
- A lowercase ASCII leading letter is treated as the same letter as its uppercase form. Any other character in position 1 is invalid.
- Formal validity never asserts that the number was issued, that the person is insured, or that a payer will accept the message.
- The TA5 field Versicherten-Nummer stays up to 12 characters. This validator does not become a mandatory gate on that field; unknown numbers may still be omitted in favor of address and date of birth.
- Real insured-person data MUST NOT appear in tests or public examples; only synthetic identifiers and the published arithmetic illustration.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a reusable formal (offline) Krankenversichertennummer validator that answers whether a candidate string is a formally valid 10-character unchanging insuree number (the number on the electronic health card).
- **FR-002**: A formally valid KVNR MUST be exactly 10 characters after trimming leading and trailing whitespace: one ASCII letter `A`–`Z` (lowercase accepted as the same letter) followed by nine digits, with no other characters.
- **FR-003**: The Prüfziffer (tenth character) MUST be computed as follows. Replace the leading letter by its alphabet position as two digits (`A` = `01` … `Z` = `26`). Together with positions 2–9 this yields ten digits. Multiply those digits left to right by weights `1,2,1,2,1,2,1,2,1,2`. Replace each product by its digit sum (Quersumme). The check digit MUST equal the sum of those digit sums modulo 10. This is the Modulo-10 rule in Anlage 1 to the Richtlinie nach § 290 SGB V for the unchanging part (Stelle 10). It is **not** the complement-to-10 rule used for Institutskennung or LANR.
- **FR-004**: The validator MUST accept as formally valid any string that meets FR-002 and FR-003, including values that would be excluded when a number is first issued (such as the digit sequence `666` or more than three identical digits in a row).
- **FR-005**: The default formal check MUST NOT validate the 20-character member number or the 30-character family-member number (kasse Institutskennung, family reference, and the overall Prüfziffer). Those forms fail this check by length.
- **FR-006**: Formal validation MUST be usable offline without network access and without looking up insuree registries, Krankenkasse directories, or certificates.
- **FR-007**: Passing formal validation MUST NOT be presented as proof that the number was issued, that the person is insured, that a payer will accept a message, or that this project is certified / testiert.
- **FR-008**: Tests, examples, and public artifacts MUST use synthetic KVNR values only. The published Anlage 1 illustration `A000500015` is an arithmetic example, not a real insuree number, and MAY be used as a calculation anchor.
- **FR-009**: The shared validator MUST live in the GKV message-shape package so dependents that already consume that package reuse one implementation, following the same value-type pattern as the Institutskennung (IK) and LANR formal validators.
- **FR-010**: This feature MUST NOT change the existing TA5 rule that Versicherten-Nummer is optional alphanumeric text of at most 12 characters. Callers opt in when they have a candidate 10-character KVNR.

### Key Entities

- **Krankenversichertennummer (unchanging part)**: Ten-character insuree identifier on the electronic health card: one letter, eight digits, one check digit.
- **KVNR Prüfziffer result**: Formal outcome of the weighted digit-sum over the expanded letter plus positions 2–9, compared to position 10 (sum modulo 10).
- **Fund-internal KVNR (out of scope)**: The 20- or 30-character number that adds kasse membership and, for family members, a reference to the member, plus an overall Prüfziffer. Not validated here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a fixed suite of at least eight synthetic 10-character KVNR cases (including `A000500015` valid and `A000500016` invalid), every case is classified correctly 100% of the time.
- **SC-002**: A caller can obtain a formal yes/no for one KVNR in under one second on ordinary developer hardware (offline, no registry lookup).
- **SC-003**: Two independent callers using the shared validator agree on validity for 100% of the fixed synthetic suite.
- **SC-004**: Operator-facing documentation states in plain language that formal validity covers only the 10-character card number, that the check digit is sum modulo 10, that issuance exclusions are not applied, that the 20- and 30-character forms are out of scope, and that formal OK does not mean insured, issued, or testiert.

## Assumptions

- “Insuree number” in this project means the 10-character unchanging Krankenversichertennummer after § 290 SGB V (letter + eight digits + Prüfziffer), which is the number read from the electronic health card and the shape already treated as KVNR for synthetic-data scanning. It does not mean the Rentenversicherungsnummer, which § 290 says must not be used as the Krankenversichertennummer.
- Ownership is the GKV message-shape package (`ta5py`): formal KVNR checking is syntactic identifier validation, not billing plausibility and not Trust Center / transport.
- The Prüfziffer rule is Anlage 1 to the Richtlinie nach § 290 SGB V (Stand used as the public calculation sheet dated 2 January 2023): letter to `01`–`26`, weights `1,2` alternating, Quersumme of each product, check digit = sum modulo 10. Worked anchors: `A000500015` (valid) and `C000500021` (valid).
- Default scope is that 10-character formal check only. The 20- and 30-character Gesamtsystem numbers, live issuance lookup, and generation bans (`666`, more than three identical digits in a row) are out of scope for the default accept/reject result.
- The TA5 segment field Versicherten-Nummer remains `..12` alphanumeric and conditional. This validator is an opt-in formal check of a candidate card number, not a new syntax rejection of other contents of that field.
- API shape mirrors the existing IK and LANR pattern: a frozen value type with parse, formal yes/no, parts, and a check-digit helper.
- Whitespace handling is trim-only, plus ASCII case-folding of the single leading letter. Formatted display with spaces or hyphens is not accepted without a prior normalize step outside this feature’s default behavior.
- Consumers that cannot depend on `ta5py` (for example packages forbidden from importing it) are out of scope for this reuse story.
