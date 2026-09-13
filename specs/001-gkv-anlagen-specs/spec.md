# Feature Specification: Ambulance GKV Anlagen Machine-Readable Specs

**Feature Branch**: `001-gkv-anlagen-specs`

**Created**: 2026-08-17

**Status**: Draft

**Input**: User description: "Implement the official GKV-Datenaustausch Sonstige Leistungserbringer Anlagen, but only the parts relevant for ambulances (Krankentransport): Anlage 1, Anlage 3, Anlage 5, and Anhang 3 (Kostenträgerdatei). Source: https://www.gkv-datenaustausch.de/leistungserbringer/sonstige_leistungserbringer/sonstige_leistungserbringer.jsp. Clarification: ambulance-only — no other SLE Leistungsbereiche."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Encode ambulance claims against Anlage 1 (Priority: P1)

A clearing integrator building Krankentransport (ambulance) claims needs a complete, versioned, machine-readable definition of the Anlage 1 Satzaufbau and segment structure **as it applies to ambulance billing**, so the format layer can encode and decode Nutzdaten that match the currently applicable published technical Anlage—not a minimal stub and not rules for other SLE types.

**Why this priority**: Without a faithful ambulance Anlage 1 field/segment model, no valid § 302 Krankentransport dataset can be produced.

**Independent Test**: Load the active ambulance Anlage 1 package; encode a full synthetic ambulance claim and verify every mandatory segment/field rule for Krankentransport; decode back to equivalent logical content—no live payer, crypto, or transport required.

**Acceptance Scenarios**:

1. **Given** synthetic ambulance claim inputs that satisfy Anlage 1 mandatory rules for Krankentransport in the active version, **When** encoding is requested, **Then** the produced dataset conforms to the ambulance Anlage 1 package for that version.
2. **Given** a synthetic ambulance dataset that violates a length, position, mandatory, or segment-order rule applicable to Krankentransport, **When** syntactic validation runs, **Then** validation fails with field- or segment-level diagnostics and does not report success.
3. **Given** a previously encoded synthetic ambulance dataset for the active version, **When** decoding is requested, **Then** structured fields match the original logical content for all mapped ambulance segments.

---

### User Story 2 - Apply ambulance-relevant Anlage 3 codes (Priority: P1)

An integrator needs the Schlüsselverzeichnisse entries required for ambulance billing (e.g. Versichertenstatus, Unfall/Sonstiges, and other codes referenced by Krankentransport fields) as structured, versioned catalogs so invalid codes are rejected before packaging.

**Why this priority**: Code validity is a core conformance requirement; wrong codes cause Absetzungen.

**Independent Test**: Validate synthetic ambulance claims against the ambulance-relevant Anlage 3 catalogs; known-good codes pass and known-bad codes fail with named catalog references.

**Acceptance Scenarios**:

1. **Given** an ambulance field that references an Anlage 3 catalog, **When** a code allowed for Krankentransport in the active catalog is supplied, **Then** syntactic validation accepts that code.
2. **Given** the same field, **When** an unknown, retired, or non-ambulance-permitted code is supplied, **Then** validation rejects it and identifies the catalog (and version) used.
3. **Given** two published Anlage 3 versions exist in the project, **When** validation is run with an explicit version selection, **Then** only that version’s ambulance-relevant codes are applied.

---

### User Story 3 - Check ambulance Urbeleg rules from Anlage 5 (Priority: P2)

An operations user or integrator wants to know whether ambulance claim inputs include the information that must appear on Verordnungen/Urbelege for Krankentransport per Anlage 5, so missing original-document content is caught before submission.

**Why this priority**: Anlage 5 content expectations affect acceptance and corrections for ambulance claims; secondary to a structurally valid dataset but still required.

**Independent Test**: Run Anlage 5 content checks on synthetic ambulance claim+document metadata fixtures; missing required Urbeleg elements produce clear failures without involving transfer.

**Acceptance Scenarios**:

1. **Given** synthetic ambulance claim data with complete Urbeleg content required for Krankentransport, **When** Anlage 5 content validation runs, **Then** the check passes.
2. **Given** synthetic ambulance claim data missing a required Krankentransport Urbeleg element, **When** Anlage 5 content validation runs, **Then** the check fails with a human-readable list of missing elements.
3. **Given** inputs that only make sense for a non-ambulance Leistungsbereich, **When** validation is requested, **Then** the system rejects them as out of product scope (unsupported claim type), not as a silent pass.

---

### User Story 4 - Resolve payers via Kostenträger file (Anhang 3) (Priority: P1)

A clearing operator needs to ingest the published Kostenträgerdatei (per Anhang 3 zur Anlage 1) and resolve Institutionskennzeichen (IK) and data-acceptance addressing so **ambulance** claims target the correct Kostenträger / Datenannahmestelle for Krankentransport.

**Why this priority**: Correct IK and acceptance addressing are mandatory for usable ambulance billing.

**Independent Test**: Ingest a synthetic (or officially published, non-patient) Kostenträger file fixture conforming to Anhang 3; look up IKs and recipient addressing for known ambulance test cases.

**Acceptance Scenarios**:

1. **Given** a valid Kostenträger file matching the active Anhang 3 specification version, **When** ingest completes, **Then** IK lookup returns the expected payer/acceptance attributes needed for ambulance delivery for fixture IKs.
2. **Given** an unknown IK, **When** lookup is requested, **Then** the system reports not-found without inventing a recipient.
3. **Given** a Kostenträger file that violates Anhang 3 structure, **When** ingest is attempted, **Then** ingest fails with structural diagnostics and does not partially overwrite a previously good directory.

---

### User Story 5 - Support parallel Anlage versions through migrations (Priority: P2)

A maintainer needs multiple published Anlage versions (currently applicable vs next announced) to coexist for the **ambulance** packages so integrators can migrate before a hard cutover date.

**Why this priority**: Official Anlagen publish with applicability windows; single-version hard-coding breaks during migrations.

**Independent Test**: Select version A vs version B for the same synthetic ambulance claim shape; observe version-specific validation outcomes without hand-swapping package files.

**Acceptance Scenarios**:

1. **Given** at least two versioned ambulance Anlage packages are present, **When** an integrator selects the currently applicable version, **Then** encode/validate use only that package.
2. **Given** a next announced version is present but not yet mandatory, **When** an integrator explicitly selects it for dry-run, **Then** validation runs against that package without changing the default.
3. **Given** a version past its published end-of-acceptance date, **When** it remains available for historical decode, **Then** documentation marks it as legacy and default encode does not target it.

---

### User Story 6 - Traceability to official GKV publications (Priority: P3)

A compliance-minded contributor wants every ambulance machine-readable package to cite the official source document title, version, stand date, and applicability notes, plus a note that only Krankentransport-relevant subsets were transcribed.

**Why this priority**: Trust and governance; required for open-source liability clarity.

**Independent Test**: Open each package’s provenance record; confirm citation fields and ambulance-scope note are populated.

**Acceptance Scenarios**:

1. **Given** a machine-readable ambulance Anlage package, **When** its provenance record is inspected, **Then** it names the official Anlage, version, stand date, source overview URL/path, and states Krankentransport-only scope.
2. **Given** an official erratum or replacement stand is adopted for ambulance-relevant content, **When** the package is updated, **Then** provenance records the new stand and retains a reference to the replaced stand.

---

### Edge Cases

- Official PDF and machine-readable package disagree on an ambulance field rule (PDF wins until governed correction).
- Kostenträger file published under a newer Anhang 3 version than the one the project has adopted.
- Anlage 3 code that exists for other SLE types but is not permitted for Krankentransport.
- Transition window where two Anlage 1/3 versions are both temporarily acceptable for ambulance submissions.
- Optional vs mandatory ambulance fields where the shared SLE PDF also describes other provider types.
- Empty or zero-byte Kostenträger ingest input.
- Duplicate IK rows or conflicting addressing in a Kostenträger file.
- Urbeleg rules that depend on accident vs non-accident (Unfall/Sonstiges) flags for ambulance transports.
- Any request involving non-ambulance Leistungsbereiche (Heilmittel, HKP, Hebammen, etc.) — must be rejected as out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST provide versioned, machine-readable domain packages covering **only Krankentransport (ambulance)–relevant** content from the official SLE publications for Anlage 1 (Satzaufbau, segments, and transfer-procedure hooks needed for ambulance dataset construction), Anlage 3 (ambulance-referenced Schlüsselverzeichnisse), and Anhang 3 zur Anlage 1 (Kostenträgerdatei specification for ambulance recipient resolution). Anlage 5 Urbeleg **content** rules are executed in **leistungen**, not in ta5py.
- **FR-002**: Each ambulance-mapped field (or equivalent atomic element) in Anlage 1 packages MUST capture at least: name, position/order, length or size constraint, mandatory/optional status for Krankentransport, and allowed values or catalog references where the official Anlage defines them for that use.
- **FR-003**: The **only** supported Leistungserbringer type for this feature MUST be Krankentransport (ambulance). Segments, fields, codes, and Urbeleg rules that apply exclusively to other SLE types MUST NOT be required for success and SHOULD NOT be transcribed except where needed to correctly exclude them.
- **FR-004**: Anlage 3 packages MUST expose named code catalogs for codes referenced by ambulance fields so unknown or non-permitted codes fail closed.
- **FR-005**: ta5py MUST NOT implement ambulance Urbeleg **content** validation. Those Anlage 5 checks MUST live in leistungen (`validate_urbeleg` / plausibility). ta5py MAY cite official Anlage 5 documents for exclusion/scope notes only.
- **FR-006**: Anhang 3 packages MUST define the Kostenträger file **structure** sufficiently to ingest published files. IK-based recipient **addressing strings** for ambulance dataset construction are in scope here. Recipient **certificate** resolution for encryption remains dtapy (`specs/dtapy/001-itsg-trust-center`).
- **FR-007**: Spec versioning MUST allow multiple ambulance Anlage versions to coexist (currently applicable and next announced), with an explicit default for encode/validate.
- **FR-008**: Default supported versions MUST track the currently applicable publications on the official Sonstige Leistungserbringer overview (as of feature creation: Anlage 1 and Anlage 3 Version 21 with published applicability from 2026-01-01; Kostenträger Anhang 3 at the latest adopted published version). Older stands (including Version 20) MAY remain for historical ambulance decode only.
- **FR-009**: Every machine-readable package MUST include provenance metadata citing official document identity (name, version, stand date), the GKV-Datenaustausch SLE overview as discovery source, and an explicit Krankentransport-only scope statement.
- **FR-010**: Syntactic validation against ambulance Anlage 1/3 packages MUST be independently testable from business-plausibility checks (plausibility is leistungen).
- **FR-011**: All fixtures, examples, and automated tests for this feature MUST use synthetic ambulance claim/insured data only; real Sozialdaten MUST never appear in the repository.
- **FR-012**: Non-ambulance Leistungsbereiche and their area-specific Anlagen (e.g. Heilmittel, HKP and XSD, Hebammen, Rehabilitationssport) are **OUT OF SCOPE** and MUST NOT be delivered by this feature.
- **FR-013**: Imageverfahren, digital rescue-protocol annexes (unless a field is mandatory for Krankentransport billing), and Korrekturverfahren recommendation PDFs for other areas are OUT OF SCOPE unless required to interpret a core ambulance field rule.
- **FR-014**: Documentation MUST state that packages are project interpretations of official PDFs limited to ambulance use; payer Testat / certification remains the deployer’s responsibility.
- **FR-015**: When an official publication supersedes a stand affecting ambulance content, adopting the new stand into the default package set MUST be a governed change (issue/PR), not an undocumented overwrite.
- **FR-016**: Consumers MUST be able to select an explicit Anlage version for ambulance validation/encode dry-runs during migration windows.
- **FR-017**: Requests or inputs that identify a non-ambulance Leistungsbereich MUST be rejected as unsupported product scope.

### Key Entities

- **Official Publication**: A GKV-Datenaustausch SLE Anlage or Anhang identified by title, version, stand date, and applicability window (source of ambulance-relevant excerpts).
- **Ambulance Anlage Package**: Structured project artifact set representing Krankentransport-relevant rules from one Official Publication version.
- **Segment / Field Definition**: Atomic Anlage 1 structural element applicable to ambulance billing, with constraints and catalog links.
- **Code Catalog**: Named Anlage 3 Schlüsselverzeichnis subset used by ambulance fields for a given version.
- **Urbeleg Content Rule**: Owned by leistungen (Anlage 5); not a ta5py runtime validator.
- **Kostenträger Directory Entry**: IK-centric payer/acceptance addressing record derived from a Kostenträgerdatei per Anhang 3, used for ambulance recipient resolution.
- **Spec Provenance Record**: Citation linking an Ambulance Anlage Package to its Official Publication and declaring Krankentransport-only scope.
- **Krankentransport Profile**: The sole supported Leistungserbringer profile selecting ambulance mandatory/optional subsets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of mandatory Anlage 1 segments/fields required for Krankentransport in the default version are represented in the ambulance package and covered by at least one synthetic encode or validation fixture.
- **SC-002**: 100% of Anlage 3 catalogs referenced by ambulance fields are present and reject at least one synthetic invalid or non-permitted code in automated tests.
- **SC-003**: Anlage 5 ambulance Urbeleg content validation is **not** a ta5py success criterion. It is covered by leistungen tests (`packages/leistungen/tests/`, at least 5 synthetic negative and 5 positive fixtures).
- **SC-004**: Kostenträger ingest + IK lookup succeeds for a representative synthetic (or published non-patient) file with at least 20 fixture IK lookups usable for ambulance addressing, including at least 3 not-found cases.
- **SC-005**: A contributor can determine the official source version, stand date, and ambulance-only scope for each default package within 5 minutes from provenance records alone.
- **SC-006**: Switching the selected Anlage version in a dry-run changes ambulance validation outcomes for at least one known version-delta fixture without editing package files by hand.
- **SC-007**: CI fails if any fixture in this feature’s suite contains patterns reserved for real Versichertennummern/Sozialdaten checks defined by project policy.
- **SC-008**: After delivery, the prior minimal stub dataset definition is either replaced by or explicitly subordinated to the default ambulance Anlage-derived package so integrators are not left with two conflicting “sources of truth.”
- **SC-009**: Automated tests include at least one case that attempts a non-ambulance Leistungsbereich and asserts an unsupported-scope rejection.

## Assumptions

- Product scope is **ambulance / Krankentransport only**. Other SLE Leistungsbereiche are permanently out of scope for this feature (not deferred).
- “Implement these specs” means producing governed, versioned, machine-readable **ambulance** packages and the validation/encode behavior that consumes them—not re-hosting official PDFs as the only artifact, and not transcribing the full multi-area SLE Anlagen verbatim.
- Shared SLE PDFs may describe many provider types; implementers extract and test only Krankentransport-applicable rules.
- User-cited Anlage 1 Version 20 (Stand 24.01.2024) is historical context; as of 2026-08-17 the official overview marks Version 21 as accepted from 2026-01-01, with Version 22 announced for a later date—defaults follow currently applicable publications for ambulance use.
- Official PDFs remain authoritative; if a transcription conflict is found, the PDF wins until a governed package correction lands.
- Kostenträger sync may live in a separate replaceable module, but Anhang 3 structural rules and ingest semantics needed for ambulance recipient resolution are in scope.
- Transfer-procedure text in Anlage 1 that overlaps crypto/transport is referenced for ambulance dataset/procedure hooks only; full DFÜ and Trust Center workflows remain owned by dtapy (see `specs/dtapy/` and the HTTP caller `specs/kassenclearing/001-dfue-kv-api`).
- Anlage 5 Urbeleg content validation is owned by leistungen, not this feature.
- English is used for Spec Kit governance artifacts; German official terms appear as domain vocabulary with English explanations.
- Source discovery path: GKV-Datenaustausch → Leistungserbringer → Sonstige Leistungserbringer (`sonstige_leistungserbringer.jsp`).
