# Data Model: Kostenträger IK Verification (§ 302)

## Entities

### Institutionskennung (IK)

| Field | Rules |
|-------|--------|
| value | Exactly nine digits for registry keys (after ordinary trim). Formal Prüfziffer is out of band (`ta5py.ik`). |

Used as **card / Kostenträger IK** (lookup key) or **recipient IK** (resolved partner).

### Kostenträgerdatei (edition)

Official SLE EDIFACT KOTR publication set (GKV-Spitzenverband via gkv-datenaustausch.de).

| Attribute | Meaning |
|-----------|---------|
| files | One or more `.ke*` (or synthetic EDIFACT) inputs for a validity/edition |
| schema | Machine-readable Anhang-3 rules (`acceptance_link_types`, segment field lists) |
| provenance | Filenames / edition markers used at ingest time |

### Kostenträger entry (per card IK)

Normalized record produced by ingest (conceptual; storage may be JSON store).

| Field | Meaning |
|-------|---------|
| ik | Card / Kostenträger IK (key) |
| name | Institution short/display name from IDK/NAM |
| acceptance_ik | Selected partner IK for acceptance/billing (§ 302 / SLE rules), or empty if none |
| abrechnungscode | Code associated with the selected link when present |
| dfue_hint / dfue_protocol | Optional transport hints from DFU (not required for existence) |
| source | Origin filename when multi-file merge is used |

### Verknüpfung (VKG) — selection input

| Field (conceptual) | Role in verification |
|--------------------|----------------------|
| art_verknuepfung | Must be in schema `acceptance_link_types` (default `02`, `03`) to be eligible |
| partner_ik | Candidate recipient IK |
| abrechnungscode | Preference when in ambulance/SLE preferred set vs fallback |
| other VKG fields | Retained for future filtering; not required for MVP selected recipient |

**Selection rule (MVP)**: Among eligible link types, prefer rows whose Abrechnungscode is empty or in the schema preferred set; otherwise first fallback; if none, `acceptance_ik` empty → recipient undetermined.

### Verification result

| Field | Meaning |
|-------|---------|
| status | `found` \| `not_found` \| `registry_unavailable` |
| card_ik | Normalized candidate that was checked (when input usable) |
| recipient_ik | Resolved acceptance/billing IK when determined; absent/empty when undetermined or not found |
| recipient_determined | Boolean: whether a non-empty recipient was resolved |
| entry | Optional catalog fields (name, abrechnungscode, dfue hints, source) when found |
| provenance | What edition/files the store was built from (when known) |

## State / transitions

```text
[no store loaded] --verify--> registry_unavailable

[store loaded] + unknown IK --verify--> not_found
[store loaded] + known IK + acceptance_ik set --verify--> found + recipient_determined
[store loaded] + known IK + acceptance_ik empty --verify--> found + recipient undetermined
```

Ingest/refresh replaces the store; subsequent verifies use the new edition only (no implicit merge with previous editions unless multi-file ingest was requested).

## Validation rules

1. Candidate IK for successful `found` MUST exist as a key in the loaded store.
2. `recipient_ik` MUST come from the file’s selected Verknüpfung; never invented when absent.
3. Tests MUST use synthetic EDIFACT and synthetic IKs only.
4. Positive `found` MUST NOT be interpreted as Testat or message-content acceptance.
