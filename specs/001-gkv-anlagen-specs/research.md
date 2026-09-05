# Research: Ambulance GKV Anlagen (Slice A — Anlage 1)

**Feature**: `specs/ta5py/001-gkv-anlagen-specs`  
**Date**: 2026-08-17  
**Directive**: Start with Anlage 1 (Krankentransport / SLLA:E)

## R1 — Default Anlage version

**Decision**: Default machine-readable package is **Anlage 1 Version 21** (currently applicable per official SLE overview as of 2026-08-17; accepted from 2026-01-01). Retain `v20` only as legacy/historical. Prepare layout for `v22` (announced, apply from 2027-02-01) without making it default.

**Rationale**: User originally cited v20 (Stand 24.01.2024), but that stand has exited acceptance. Shipping v20 as default would produce non-accepted datasets.

**Alternatives considered**:
- Default v20 then migrate — rejected (already past cutover).
- Jump straight to v22 — rejected (not yet mandatory).

**Implement note**: Field transcription must be verified against the **current v21 PDF** on gkv-datenaustausch.de at coding time. Structural research below used the archived v20 PDF for segment inventory (SLLA:E list is stable across nearby versions; confirm deltas).

## R2 — Ambulance-only message profile

**Decision**: Support **Sammelgruppenschlüssel E** only — Nachrichtentyp **SLLA:E (Krankentransportleistungen)**, plus the **service envelope** (UNB/UNH/UNT/UNZ) and **SLGA** pieces required to form a valid Nutzdatendatei that contains SLLA:E cases.

**Official SLLA:E segment chain** (from Anlage 1 §5.5.1 / §5.5.3.6):

`FKT, REC, INV, NAD, IMG, EVO, KTL, EKT, TXT, MWS, ZUK, ZKT, SKZ, BES`

Key composition rules (v20 wording; re-verify on v21):

- INV…BES repeats per Abrechnungsfall between LE and Kasse IK.
- After NAD (or IMG if present) comes **KTL**; then one or more **EKT [/ TXT] [/ MWS]** sequences per Gebührenposition / Fahrt grouping.
- New Fahrt → new **KTL** (new Identifikationsnummer).
- Optional **ZUK** after all Fahrten for that Identifikationsnummer when Zuzahlung withheld.
- **ZKT** once per INV (Verordnung); optional **SKZ**; mandatory **BES**.

**Rationale**: Matches product scope (ambulances only) and avoids transcribing Heilmittel/HKP/Hebammen segments.

**Alternatives considered**:
- Full multi-Sammelgruppe Anlage 1 — rejected by scope.
- SLLA:E Nutzsegmente only without UNB/SLGA — rejected; incomplete files cannot be integration-tested toward transfer.

## R3 — Artifact format for machine-readable specs

**Decision**: **YAML** segment/field definitions + a small **JSON Schema** contract for the package layout (`contracts/anlage1-package.schema.json`). Logical claims may use JSON for tests; **canonical encode output is EDIFACT-like Nutzdaten text** per Anlage 1 separators.

**Rationale**: Constitution allows YAML and/or JSON Schema; YAML is readable for long field tables; existing stub JSON Schema is too flat for segment order/repetition.

**Alternatives considered**:
- JSON Schema only — poor fit for segment repetition graphs.
- Keep JSON-only encode (current stub) — fails FR for real Nutzdaten Satzaufbau.

## R4 — Catalog / Anlage 3 dependency during Slice A

**Decision**: Slice A validates **type, length, mandatory/optional, and segment order**. Fields that cite Anlage 3 keys carry a `catalog_ref` in YAML but **membership checks are deferred to Slice B**, except where a tiny stub enum is required for a golden fixture (document as temporary).

**Rationale**: Unblocks Anlage 1 delivery without blocking on full Schlüsselverzeichnisse transcription.

**Alternatives considered**:
- Block Slice A until full Anlage 3 — rejected (user: start with Anlage 1).
- Fake-accept any string for coded fields forever — rejected; Slice B must close the gap.

## R5 — Separators and wire encoding

**Decision**: Implement UNA-defined separators as in Anlage 1 (typical: segment end `'`, element `+`, component `:`, decimal `,`, release `?`). Escaping rules follow the technical Anlage; round-trip tests must cover release characters in free text (e.g. TXT, street).

**Rationale**: Required for authentic Nutzdaten; transfer/cert modules expect bytes that Datenannahmestellen understand.

**Alternatives considered**: Proprietary binary — rejected.

## R6 — Relationship to existing stub `v20/dataset.schema.json`

**Decision**: After Slice A lands, mark stub as **legacy / non-default**; default `spec_version` becomes `v21`. Provide migration note in format README. Do not maintain two competing sources of truth (SC-008).

**Rationale**: Spec success criterion and constitution versioning.

## R7 — Digital Rettungsprotokoll / Imageverfahren

**Decision**: Out of scope for Slice A unless a SLLA:E field **requires** IMG/EVO content that cannot be modeled without those annexes. Include **IMG** and **EVO** segment shells if present in SLLA:E chain; deep Imageverfahren XML (Anhang 4) stays out.

**Rationale**: Spec FR-013; keep Slice A focused.

## R8 — Kostenträger / Urbeleg

**Decision**: Not in Slice A. Anhang 3 and Anlage 5 remain later slices; encode may accept IK strings with length checks only.

## Resolved clarifications

All Technical Context items resolved; no remaining NEEDS CLARIFICATION markers for planning.
