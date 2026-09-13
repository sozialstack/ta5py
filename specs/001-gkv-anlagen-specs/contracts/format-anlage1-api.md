# Contract: format module — Anlage 1 Slice A

**Owner**: `packages/ta5py`  
**Consumers**: kassenclearing (orchestration), tests, Kostenträger tooling (IK strings only in Slice A)  
**Out of scope**: dtapy packaging/transfer, Anlage 5 Urbeleg **content** (leistungen), full Anlage 3/Anhang 3

## Public operations (Slice A)

### `load_package(spec_version: str) -> AnlagePackage`

- Loads `packages/ta5py/spec/{spec_version}/` conforming to [anlage1-package.schema.json](./anlage1-package.schema.json).
- Default version: `v21`.
- Raises if version missing or provenance.scope ≠ `krankentransport`.

### `validate_syntax(logical_or_wire, spec_version: str) -> FormatResult`

- Accepts logical ambulance claim **or** Nutzdaten wire text.
- Checks segment order/repetition for **SLLA:E**, field lengths/types, M/K.
- Does **not** fully enforce Anlage 3 catalog membership (Slice B).
- Rejects non-ambulance profiles with `unsupported_scope`.

### `encode(logical_claim, spec_version: str) -> FormatResult`

- Validates then serializes to **Nutzdaten wire text** (file URI or returned payload).
- Optional debug JSON sidecar allowed; wire text is canonical.

### `decode(wire_uri_or_text, spec_version: str) -> logical_claim`

- Parses wire text using package UNA separators and SLLA:E grammar.
- Round-trip: `decode(encode(x))` equals `x` for supported fields (modulo empty Kann elision rules).

### `validate_plausibility(...)` — **not ta5py**

- Business plausibility and Urbeleg content validation belong in **leistungen**.
- Slice A MUST NOT grow a ta5py plausibility implementation.

## Required SLLA:E segments (package must define)

`FKT`, `REC`, `INV`, `NAD`, `IMG`, `EVO`, `KTL`, `EKT`, `TXT`, `MWS`, `ZUK`, `ZKT`, `SKZ`, `BES`  
plus service segments used in files: `UNB`, `UNH`, `UNT`, `UNZ`, and SLGA Nutzsegmente needed for a minimal valid file.

## Error shape

Reuse existing result types (`syntax_ok`, field errors). Do not add a new shared `clearing-contracts` dependency for this slice.

| Field | Meaning |
|-------|---------|
| `syntax_ok` | Passed Anlage 1 syntactic rules for ambulance profile |
| `errors[].field` | Path e.g. `slla[0].cases[0].ktl[1].strasse_abholort` |
| `errors[].message` | Stable, non-sensitive text |

## Non-goals (Slice A)

- Encrypting or transferring packages  
- Kostenträger file parse  
- Urbeleg PDF content rules  
- Other Sammelgruppen (A–D, F–…)
