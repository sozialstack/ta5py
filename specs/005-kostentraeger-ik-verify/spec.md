# Feature Specification: Kostenträger IK Verification (§ 302)

**Feature Branch**: `005-kostentraeger-ik-verify`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "verification for Institutionskennung of Krankenkassen und andere Kostenträger" — Kostenträgerdatei as authoritative source (GKV-Spitzenverband, EDIFACT, gkv-datenaustausch.de); contains Kostenträger IKs and links from card IK to billing/acceptance offices; correct place for § 302 because it checks existence and determines the correct recipient IK.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Confirm a card IK exists in the Kostenträgerdatei (Priority: P1)

An operator or clearing step has an Institutionskennung from a health card (or equivalent insured-side payer IK) for a Krankenkasse or other Kostenträger. Before building a § 302 billing message, they need a clear answer: is this IK present in the current Kostenträgerdatei? Formal digit checks alone are not enough—the file published by the GKV-Spitzenverband is the reliable registry for this purpose.

**Why this priority**: Sending to an unknown or outdated IK causes avoidable rejections; existence against the official file is the first gate for § 302 addressing.

**Independent Test**: Against a synthetic Kostenträgerdatei snapshot, known-present IKs verify as found and known-absent IKs verify as not found, without claiming payer Testat or live network certification.

**Acceptance Scenarios**:

1. **Given** a current ingested Kostenträgerdatei that contains synthetic IK `123456789`, **When** registry verification runs for that IK, **Then** the result is “found” (present in the file).
2. **Given** the same file, **When** registry verification runs for a synthetic IK that is not listed, **Then** the result is “not found.”
3. **Given** no usable Kostenträgerdatei is available to the verifier, **When** registry verification is requested, **Then** the system refuses to claim a positive existence result and reports that the registry is unavailable or not loaded.

---

### User Story 2 - Resolve the correct § 302 recipient IK from a card IK (Priority: P1)

For § 302, knowing the card IK exists is not enough: the operator must address the right Abrechnungs- and/or Annahmestelle. The Kostenträgerdatei links the card (Kosten-träger) IK to partner IKs for acceptance and billing. The verifier must return the recipient IK(s) determined from those links for the applicable § 302 / sonstige Leistungserbringer context—not invent addresses from elsewhere.

**Why this priority**: Wrong recipient IK is as harmful as a missing IK; this is the stated reason the Kostenträgerdatei is the right verification source for § 302.

**Independent Test**: From a synthetic file where card IK `123456789` links to acceptance IK `111222333`, verification returns that recipient (and related link metadata the product exposes) consistently.

**Acceptance Scenarios**:

1. **Given** a synthetic Kostenträgerdatei where card IK `A` has a defined acceptance/billing link to partner IK `B` for the § 302 / SLE context, **When** recipient resolution runs for `A`, **Then** the resolved recipient includes `B`.
2. **Given** a card IK that exists in the file but has no usable acceptance/billing link for that context, **When** recipient resolution runs, **Then** existence may still be “found,” but the system reports that no recipient could be determined (no silent fallback to an unrelated IK).
3. **Given** a card IK not in the file, **When** recipient resolution runs, **Then** no recipient IK is returned.

---

### User Story 3 - Use an up-to-date official file as the source of truth (Priority: P2)

Operators obtain the Kostenträgerdatei from the official GKV Datenaustausch publication channel (gkv-datenaustausch.de). The file is EDIFACT-structured and maintained by the GKV-Spitzenverband. Verification MUST treat the operator-loaded current file (or an explicitly selected validity edition) as authoritative—not a hard-coded list of IKs in product docs.

**Why this priority**: Freshness and provenance of the registry matter for trust; existence of a download/ingest path is secondary to correct verify/resolve behavior but required for real operations.

**Independent Test**: After replacing the loaded synthetic file with another synthetic edition that adds or removes an IK, verification outcomes change to match the new file; outcomes do not depend on a built-in permanent IK allow-list.

**Acceptance Scenarios**:

1. **Given** edition E1 loaded (IK X present), **When** verification runs for X, **Then** X is found.
2. **Given** edition E2 loaded instead (IK X absent), **When** verification runs for X, **Then** X is not found.
3. **Given** operator documentation for this feature, **When** an operator asks where the registry comes from, **Then** docs name the GKV-Spitzenverband Kostenträgerdatei / gkv-datenaustausch.de as the source—not an internal invented directory.

---

### User Story 4 - Separate formal shape from registry truth (Priority: P3)

Operators may already run a formal (offline Prüfziffer) check on nine-digit IKs. Registry verification answers a different question: presence and addressing in the Kostenträgerdatei. A formally valid IK can still be absent from the file; a file hit remains the business authority for § 302 addressing. Product messaging MUST NOT equate registry presence with project certification or payer Community-Testat.

**Why this priority**: Prevents false confidence and clarifies the boundary with the formal IK check feature.

**Independent Test**: Documentation and verification outcomes distinguish “formally shaped” vs “listed in Kostenträgerdatei” vs “certified/testiert.”

**Acceptance Scenarios**:

1. **Given** a synthetic nine-digit IK that is formally well-formed but not in the loaded file, **When** registry verification runs, **Then** the result is not found (formal shape does not override the file).
2. **Given** project documentation, **When** an operator asks whether a positive registry hit means Testat or payer acceptance of a specific message, **Then** the answer is no.

---

### Edge Cases

- Empty, whitespace-only, or non-nine-digit input → not treated as a successful registry hit; clear invalid-input or not-found outcome (no partial match).
- Multiple link rows for one card IK → selection follows the published Kostenträgerdatei / Anhang-3 linking rules for the § 302 / SLE context; if none apply, report undetermined recipient rather than picking an arbitrary unrelated IK.
- Duplicate or conflicting entries across merged files from the same publication set → later/merged file rules for the same IK MUST be deterministic and documented for operators.
- Stale file → verification still answers against whatever edition is loaded; operators are responsible for refreshing from the official channel; the product MUST expose enough provenance (e.g. source file name / edition identity when available) so operators can see what was used.
- Real insured-person data and live production institution dumps MUST NOT appear in tests or public examples; only synthetic Kostenträgerdatei fixtures and synthetic IKs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST verify whether a candidate Institutionskennung for a Krankenkasse or other Kostenträger is present in the loaded Kostenträgerdatei (registry verification).
- **FR-002**: The Kostenträgerdatei published under the GKV-Spitzenverband / gkv-datenaustausch.de process MUST be treated as the authoritative source for this verification; the product MUST NOT use a hard-coded substitute list as the source of truth.
- **FR-003**: For § 302 use, when a card IK is found, the system MUST resolve the linked Abrechnungs- and/or Annahmestellen partner IK(s) from the file’s Verknüpfungen according to the applicable SLE / § 302 linking rules.
- **FR-004**: When the card IK is absent from the loaded file, the system MUST NOT invent a recipient IK.
- **FR-005**: When the card IK is present but no applicable acceptance/billing link exists for the § 302 context, the system MUST report that the recipient could not be determined.
- **FR-006**: Registry verification MUST be answerable from the locally loaded/ingested file without requiring a live network call at the moment of verification (operators refresh the file as a separate step).
- **FR-007**: Operators MUST be able to load or refresh the Kostenträgerdatei from the official publication channel (or from files already obtained from that channel) so verification tracks the current edition.
- **FR-008**: Registry presence MUST NOT be presented as proof of project certification, payer Community-Testat, or acceptance of a specific Leistungsnachweis content.
- **FR-009**: Tests, examples, and public artifacts MUST use synthetic Kostenträgerdatei content and synthetic IKs only.
- **FR-010**: Registry verification is distinct from formal offline Prüfziffer validation; formal shape MAY be checked separately but MUST NOT replace or override the file for existence or recipient resolution.
- **FR-011**: Ownership of this catalog verification capability MUST remain with the GKV message-shape package (Kostenträger catalog used for encoding/addressing), not with transport/crypto or Leistungsart billing packages.

### Key Entities

- **Institutionskennung (IK)**: Nine-digit institution identifier used as card/Kostenträger IK or as partner (acceptance/billing) IK.
- **Kostenträgerdatei**: Official EDIFACT registry of Kostenträger IKs and Verknüpfungen, published via gkv-datenaustausch.de by the GKV-Spitzenverband.
- **Card / Kostenträger IK**: The IK associated with the insured person’s payer on the card (lookup key into the file).
- **Recipient IK (Annahme- / Abrechnungsstelle)**: Partner IK determined from Verknüpfungen for where § 302 data should be addressed.
- **Verification result**: Outcome of registry check: found / not found / registry unavailable; plus resolved recipient information when available.
- **File edition / provenance**: Identity of the loaded publication set (e.g. validity/edition markers from official filenames) used for a given verification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a fixed suite of at least ten synthetic card IKs against a fixed synthetic Kostenträgerdatei, existence (found/not found) is classified correctly 100% of the time.
- **SC-002**: For every synthetic card IK in that suite that has a defined § 302 / SLE acceptance link, the resolved recipient IK matches the fixture expectation 100% of the time.
- **SC-003**: An operator can obtain an existence + recipient answer for one card IK from an already loaded file in under three seconds on ordinary developer hardware (no live download required for that answer).
- **SC-004**: After swapping the loaded synthetic edition, at least one previously found IK becomes not found (or the reverse), demonstrating that the file—not a built-in allow-list—controls outcomes.
- **SC-005**: Operator-facing documentation states in plain language that the Kostenträgerdatei is the authoritative source, that verification supports § 302 addressing (existence + recipient), and that a positive hit is not a Testat.

## Assumptions

- Scope for recipient resolution is § 302 / sonstige Leistungserbringer (SLE) Kostenträgerdateien and their Verknüpfung rules; other Leistungsarten’ files may share ingest machinery later but are not required for this feature’s acceptance.
- Formal Prüfziffer validation is covered by the separate formal IK validator feature; this feature does not redefine check-digit rules.
- “Verification” here means registry presence + recipient resolution from the loaded official file, not cryptographic proof of identity and not Trust Center certificate checks.
- Operators (or CI with synthetic fixtures) supply the file; production freshness SLAs (e.g. “must be less than N days old”) are an operational policy outside this feature’s core requirements, aside from exposing provenance when available.
- Selection among multiple VKG-style links follows the same published Anhang-3 / package Kostenträger schema rules already used for SLE acceptance linking; documenting that rule for operators is in scope, inventing a new conflicting selection policy is not.
- Transport endpoints (SFTP/HTTPS channels listed in the file) may be surfaced as hints when present but delivering the message remains out of scope (transport package).
- Consumers that must not import the message-shape package remain out of scope for direct reuse; they integrate via a later caller composition if needed.
