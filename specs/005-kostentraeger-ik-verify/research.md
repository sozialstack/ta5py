# Research: Kostenträger IK Verification (§ 302)

## Decision: Own registry verification in `ta5py.kostentraeger`

**Rationale**: Project constitution Domain Scope for ta5py includes “Kostenträger catalogs used for encoding.” § 302 addressing (card IK → Annahmestelle/Abrechnungsstelle) is message-shape / catalog knowledge, not Leistungsart billing (leistungen) and not Trust Center/transport (dtapy). Ingest + `KostentraegerStore.lookup` already live in ta5py.

**Alternatives considered**:
- `leistungen` only — rejected; billing packages should consume resolved recipient IKs, not own the official file parse.
- `dtapy` — rejected; dtapy owns Annahmelisten/crypto/transport and MUST NOT import ta5py; Kostenträgerdatei is EDIFACT KOTR, not the Trust Center directory.
- New shared package — rejected; unnecessary fourth ownership for an existing ta5py capability.

## Decision: Authoritative source = SLE Kostenträgerdatei (GKV-Spitzenverband / gkv-datenaustausch.de)

**Rationale**: Spec FR-002 and requester statement: the Kostenträgerdatei is the reliable source for existence **and** Verknüpfungen to Abrechnungs-/Annahmestellen for § 302. Official SLE listing is already wired in `kostentraeger_fetch.py` and `make download-kostentraeger`.

**Alternatives considered**:
- ITSG Trust Center directory as existence source — rejected for this feature; different purpose (certificates/endpoints), and requester explicitly named Kostenträgerdatei for § 302.
- Hard-coded IK allow-list — rejected; contradicts FR-002 and SC-004.
- Live HTTP lookup on every verify — rejected; FR-006 requires offline verify against a loaded edition; refresh is a separate operator step.

## Decision: Explicit `verify` / resolve API over raw `lookup` dict

**Rationale**: Today `lookup` returns `dict[str, str] | None`. Spec needs distinguishable outcomes: found, not found, registry unavailable, and “found but recipient undetermined.” A small typed result (or documented helpers) makes FR-003–FR-005 testable without callers reinterpreting empty `acceptance_ik` strings.

**Alternatives considered**:
- Leave only `lookup` — insufficient for “registry unavailable” vs “not found” and for clear recipient-undetermined semantics.
- Merge formal `is_valid_ik` into the same function — rejected; FR-010 keeps formal shape separate so formally valid but unlisted IKs stay “not found.”

## Decision: Reuse Anhang-3 `acceptance_link_types` / `_pick_acceptance` for § 302 recipient

**Rationale**: Schema already defines `acceptance_link_types: ["02", "03"]` and ambulance Abrechnungscode preference. Spec Assumptions say not to invent a conflicting selection policy. Document the rule for operators; keep selection in one place.

**Alternatives considered**:
- Always prefer `abrechnungsstelle_ik` field over `partner_ik` — defer unless Anhang-3 / product call sites require a second resolution mode; current store surfaces `acceptance_ik` from partner selection.
- Return all VKG rows to every caller — deferred; MVP returns the selected recipient plus enough metadata (name, abrechnungscode, dfue hints) for addressing; full raw VKG export can be a later enhancement.

## Decision: Provenance via source filename / edition markers when merged

**Rationale**: SC and FR require operators to see which edition was used. Multi-file ingest already stamps `source` on entries. Store-level provenance (list of ingested filenames / download overview metadata) should be available when verifying so stale-file risk is visible without enforcing a hard max-age SLA in v1.

**Alternatives considered**:
- Enforce “file must be < N days old” in verify — rejected for v1; operational policy, not core product rule (Assumptions).
- Embed full remote HTML overview in every verify result — overkill; filename/edition identity suffices.

## Decision: Synthetic fixtures only; live `.ke*` gitignored

**Rationale**: Principle IV. Existing fixture `anhang3_kotr.edifact` already covers lookup of synthetic `123456789` → acceptance `111222333`. Extend with cases for missing links and edition swap rather than committing production files.

**Alternatives considered**:
- Commit a redacted production slice — rejected; high risk of real institution/Sozialdaten leakage and Contributor Gate issues.
