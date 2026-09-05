# Data Model: Ambulance Anlage Packages (Slice A focus)

**Feature**: `specs/gkv-edi/001-gkv-anlagen-specs`  
**Date**: 2026-08-17

## Entities

### OfficialPublication

| Field | Description |
|-------|-------------|
| anlage_id | e.g. `anlage-1`, `anlage-3`, `anlage-5`, `anhang-3` |
| version | Integer version (e.g. 21) |
| stand_date | Official stand date |
| applicable_from | Published applicability start |
| applicable_until | Optional end / superseded date |
| source_url | Discovery or PDF URL |

### SpecProvenanceRecord

| Field | Description |
|-------|-------------|
| package_id | e.g. `format/v21` |
| publications | List of OfficialPublication citations used |
| scope | Always `krankentransport` / SLLA:E for this feature |
| transcribed_by | Optional contributor note |
| notes | Errata / stand replacements |

### AnlagePackage (version root)

| Field | Description |
|-------|-------------|
| version_label | `v21` |
| provenance | SpecProvenanceRecord |
| una | SeparatorConfig |
| messages | MessageType definitions (`slga`, `slla_e`, …) |
| segments | Map of segment_code → SegmentDefinition |
| catalog_refs | Declared refs (Slice A may be empty or stubbed) |

### SeparatorConfig (UNA)

| Field | Description |
|-------|-------------|
| component | e.g. `:` |
| element | e.g. `+` |
| decimal | e.g. `,` |
| release | e.g. `?` |
| segment_end | e.g. `'` |

### MessageType

| Field | Description |
|-------|-------------|
| code | `SLLA` / `SLGA` |
| profile | `E` for Krankentransport SLLA |
| segments | Ordered list of MessageSegmentRef |

### MessageSegmentRef

| Field | Description |
|-------|-------------|
| segment | Segment code (e.g. `KTL`) |
| usage | `M` or `K` |
| repeat | Max / rule (e.g. `1-n je INV`) |
| notes | Composition notes |

### SegmentDefinition

| Field | Description |
|-------|-------------|
| code | Three-letter code |
| name | Human-readable name |
| fields | Ordered FieldDefinition list |

### FieldDefinition

| Field | Description |
|-------|-------------|
| name | Stable snake_case id |
| official_label | German label from PDF |
| position | 1-based order within segment |
| max_length | Length or `n,m` decimal form |
| value_type | `AN` / `N` / group |
| usage | `M` / `K` |
| catalog_ref | Optional Anlage 3 key id (checked in Slice B) |
| description | Short English explanation |

### LogicalAmbulanceClaim (runtime / test model)

Logical tree used before wire encoding (not a second Anlage):

- `unb` / file header fields  
- `slga` (optional/required per file mode)  
- `slla_e` messages: `fkt`, `rec`, cases[`inv`, `nad`, `img?`, `evo?`, trips[`ktl`, positions[`ekt`, `txt?`, `mws?`], `zuk?`], `zkt`, `skz?`, `bes`]

### NutzdatenDocument

| Field | Description |
|-------|-------------|
| wire_text | Canonical EDIFACT-like string |
| spec_version | e.g. `v21` |
| profile | `slla_e` |

### ValidationFinding

| Field | Description |
|-------|-------------|
| path | Segment/field path |
| code | e.g. `required`, `length`, `order`, `unsupported_scope` |
| message | Human-readable |

## Relationships

```text
OfficialPublication 1──* SpecProvenanceRecord
AnlagePackage 1──1 SpecProvenanceRecord
AnlagePackage 1──* MessageType
AnlagePackage 1──* SegmentDefinition
MessageType *──* SegmentDefinition (via MessageSegmentRef)
SegmentDefinition 1──* FieldDefinition
FieldDefinition *──0..1 catalog_ref → (Slice B CodeCatalog)
LogicalAmbulanceClaim ──encode──► NutzdatenDocument
NutzdatenDocument ──decode──► LogicalAmbulanceClaim
```

## Validation rules (Slice A)

1. Reject non-`krankentransport` / non-E profile inputs (`unsupported_scope`).
2. Enforce MessageType segment order and repetition for SLLA:E.
3. Enforce FieldDefinition length, type, and M/K within present segments.
4. Kann-segments may be omitted; trailing empty Kann elements collapse per Anlage 1 separator rules.
5. Release character escaping must round-trip.
6. Catalog membership: warn/skip or stub only — full fail-closed in Slice B.
7. Plausibility (km ranges, sum BES vs EKT, etc.) is separate from syntax; may be partial in Slice A.

## State transitions

Not applicable beyond package version selection: `legacy (v20)` → `default (v21)` → optional `preview (v22)`.
