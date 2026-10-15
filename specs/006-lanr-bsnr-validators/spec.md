# Feature Specification: LANR and BSNR Formal Validators

**Feature Branch**: `006-lanr-bsnr-validators`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "I need validators for Landesärtzenummer (Lanr) and Betriebsstättennummer (Bsnr)" followed by planning guidance to use the same pattern as for IK.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Decide whether a nine-digit LANR is formally valid (Priority: P1)

An operator or upstream clearing step has a candidate Lebenslange Arztnummer (LANR; often misspoken as “Landesärztenummer”) as text and needs a clear yes/no formal check before the value is used in messages or billing handoffs. The check is offline: length, digits only, and the official Prüfziffer at position 7 over positions 1–6. Positions 8–9 (Arztgruppenschlüssel) do not enter the check. Passing formal validation does not mean the physician is licensed, assigned that specialty code, or that a payer will accept the message.

**Why this priority**: Invalid LANRs leak into every path that carries physician identifiers; a shared formal check removes avoidable rejections.

**Independent Test**: Feed known valid and invalid nine-digit synthetic LANRs (including the published KBV-style example whose physician digits `123456` yield check digit `6`); only structurally and check-digit-correct values pass.

**Acceptance Scenarios**:

1. **Given** the nine-digit value `123456601`, **When** formal LANR validation runs, **Then** the result is valid.
2. **Given** the nine-digit value `123456901` (wrong check digit), **When** formal LANR validation runs, **Then** the result is invalid.
3. **Given** a value that is not exactly nine characters or contains a non-digit after ordinary trim of leading/trailing whitespace, **When** formal LANR validation runs, **Then** the result is invalid.
4. **Given** any nine-digit synthetic LANR whose check digit matches the prescribed weighting of positions 1–6, **When** formal LANR validation runs, **Then** the result is valid regardless of the Arztgruppenschlüssel meaning.

---

### User Story 2 - Decide whether a nine-digit BSNR is formally structured (Priority: P1)

An operator or upstream step has a candidate Betriebsstättennummer (BSNR) as text and needs a clear yes/no formal structure check: exactly nine digits after trim. There is no public Prüfziffer for BSNR in the KBV Arztnummern-Richtlinie; formal validity here means digit structure only (positions 1–2 are the KV regional key, positions 3–9 identify the site). Passing does not mean the Betriebsstätte exists or that a KV assigned that number.

**Why this priority**: BSNR appears alongside LANR on the same forms and message fields; callers need a shared structural gate even without a check digit.

**Independent Test**: Feed synthetic nine-digit all-numeric BSNRs and bad-length / non-digit cases; only exactly nine digits after trim pass.

**Acceptance Scenarios**:

1. **Given** a synthetic nine-digit value such as `031234567`, **When** formal BSNR validation runs, **Then** the result is valid.
2. **Given** a value that is not exactly nine digits after trim or contains a non-digit, **When** formal BSNR validation runs, **Then** the result is invalid.
3. **Given** project documentation for this feature, **When** an operator asks whether BSNR has a Prüfziffer like LANR, **Then** the answer is no for the public formal check—structure only.

---

### User Story 3 - Reuse one LANR and one BSNR check everywhere identifiers appear (Priority: P1)

Maintainers of message formatting and related operator tooling need one documented formal rule per identifier so callers do not each reimplement a slightly different check. Callers that already depend on the GKV message-shape package can invoke the same validators, mirroring the existing Institutskennung (IK) pattern.

**Why this priority**: “Reusable” matching the IK validator pattern is the product ask; duplicated ad-hoc checks are the failure mode.

**Independent Test**: The same synthetic valid and invalid LANR/BSNR values produce identical outcomes when validated through the shared formal entry points used by package consumers in tests.

**Acceptance Scenarios**:

1. **Given** a synthetic LANR known to be formally valid, **When** two different package-facing callers invoke the shared formal LANR validator, **Then** both receive the same valid outcome.
2. **Given** a synthetic BSNR that fails structure, **When** those callers invoke the shared formal BSNR validator, **Then** both receive the same invalid outcome.

---

### User Story 4 - Understand formal OK ≠ assignment or payer acceptance (Priority: P2)

Operators need documentation that formal LANR/BSNR checks do **not** prove KV assignment, specialty correctness, Betriebsstätte existence, or payer acceptance. Specialty-code catalogs and KV-prefix business rules are separate policies—not part of the default formal validators.

**Why this priority**: Avoids false confidence; parallel to the IK “formal ≠ registry / Testat” story.

**Independent Test**: Documentation states the limits; synthetic values that only satisfy structure/Prüfziffer pass the default checks without specialty or KV-catalog lookup.

**Acceptance Scenarios**:

1. **Given** a formally valid synthetic LANR with an arbitrary two-digit Arztgruppenschlüssel, **When** the default formal validator runs, **Then** the result is valid without consulting a specialty catalog.
2. **Given** a formally structured synthetic BSNR whose first two digits are not on a curated KV whitelist, **When** the default formal validator runs, **Then** the result remains valid (no default prefix rejection).
3. **Given** project documentation, **When** an operator asks whether formal validity means Testat or registry existence, **Then** the answer is no.

---

### Edge Cases

- Leading or trailing whitespace around an otherwise valid nine-digit LANR or BSNR is ignored for the check; internal spaces or separators are not accepted as part of the digit string.
- Empty input, all spaces, or non-digit characters → formally invalid.
- Values shorter or longer than nine digits (after trim) → formally invalid.
- For LANR, Arztgruppenschlüssel (positions 8–9) does not affect the Prüfziffer calculation.
- For BSNR, there is no Prüfziffer; unusual KV prefixes do not fail the default structural check.
- Formal validity never asserts that the physician or Betriebsstätte is assigned, reachable, or accepted by a payer.
- Real physician, practice, or patient data MUST NOT appear in tests or public examples; only synthetic identifiers.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a reusable formal (offline) Lebenslange Arztnummer (LANR) validator that answers whether a candidate string is a formally valid nine-digit LANR.
- **FR-002**: A formally valid LANR MUST be exactly nine digits after trimming leading and trailing whitespace, with no other characters.
- **FR-003**: The LANR Prüfziffer (seventh digit) MUST be computed from positions 1 through 6 only (1-based), using left-to-right weights 4,9,4,9,4,9; the check digit MUST equal `(10 − (sum of weighted products modulo 10)) modulo 10`. Positions 8–9 (Arztgruppenschlüssel) MUST NOT enter the sum. This is the KBV Arztnummern-Richtlinie / published Modulo-10 rule (no Quersumme of products).
- **FR-004**: The validator MUST accept as formally valid any nine-digit string that meets FR-002 and FR-003 regardless of Arztgruppenschlüssel semantics.
- **FR-005**: The system MUST provide a reusable formal (offline) Betriebsstättennummer (BSNR) validator that answers whether a candidate string is a formally structured nine-digit BSNR.
- **FR-006**: A formally valid BSNR MUST be exactly nine digits after trimming leading and trailing whitespace, with no other characters. The default formal check MUST NOT apply a Prüfziffer (none is published for BSNR) and MUST NOT reject based on KV-prefix catalogs.
- **FR-007**: Exclusion of specialty codes, KV prefixes, or other business classes MUST NOT be part of the default formal checks; such policies MAY be documented as optional separate rules outside this feature’s default behavior.
- **FR-008**: Formal validation MUST be usable offline without network access and without looking up directories, KV registries, or certificates.
- **FR-009**: Passing formal validation MUST NOT be presented as proof of physician/practice assignment, payer acceptance, or project certification / Testat.
- **FR-010**: Tests, examples, and public artifacts MUST use synthetic LANR and BSNR values only.
- **FR-011**: The shared validators MUST live in the GKV message-shape package so dependents that already consume that package reuse one implementation, following the same value-type pattern as the Institutskennung (IK) formal validator.

### Key Entities

- **Lebenslange Arztnummer (LANR)**: Nine-digit physician identifier: six-digit physician serial, one check digit, two-digit Arztgruppenschlüssel.
- **LANR Prüfziffer result**: Formal outcome of the weighted sum over positions 1–6 compared to digit 7.
- **Betriebsstättennummer (BSNR)**: Nine-digit practice-site identifier: two-digit KV regional key, seven-digit site assignment (no public check digit).
- **Formal structure result (BSNR)**: Outcome of length and digit-only checks only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a fixed suite of at least eight synthetic nine-digit LANR cases (including `123456601` valid and `123456901` invalid), every case is classified correctly 100% of the time.
- **SC-002**: For a fixed suite of at least six synthetic BSNR cases (valid nine-digit and invalid length/non-digit), every case is classified correctly 100% of the time.
- **SC-003**: A caller can obtain a formal yes/no for one LANR or one BSNR in under one second on ordinary developer hardware (offline, no registry lookup).
- **SC-004**: Two independent callers using the shared validators agree on validity for 100% of the fixed synthetic suites.
- **SC-005**: Operator-facing docs state in plain language that formal LANR validity ≠ assignment/specialty correctness, that BSNR has no public Prüfziffer (structure only), and that neither implies Testat / payer acceptance.

## Assumptions

- Ownership is the GKV message-shape package (`ta5py`): formal LANR/BSNR checking is syntactic identifier validation, not billing plausibility and not Trust Center / transport.
- The requester’s “Landesärtzenummer” means the Lebenslange Arztnummer (LANR) under KBV Arztnummern-Richtlinie (§ 75 Abs. 7 SGB V).
- Default LANR scope is formal structure + Prüfziffer only; semantic meaning of Arztgruppenschlüssel and live KV lookups are out of scope.
- Default BSNR scope is nine-digit structure only; KV-prefix whitelists and special prefixes such as `35` / `75` (besondere Versorgungsbereiche) are documented as structural parts but not enforced as accept/reject catalogs in the default check.
- API shape mirrors the existing IK pattern: frozen value types with `parse`, `is_valid`, `is_formally_valid`, and (for LANR) `compute_check_digit`.
- Whitespace handling is trim-only; formatted display with spaces or hyphens is not accepted without a prior normalize step outside this feature’s default API.
- Consumers that cannot depend on `ta5py` (e.g. packages forbidden from importing it) are out of scope for this reuse story.
- Pseudonym / Ersatz physician numbers used in some billing contexts are out of scope unless they satisfy the same formal LANR rule; no special-case filter in v1.
