# Anlage 3 catalogs (Slice B) — fail-closed membership

Ambulance-referenced Schlüsselverzeichnisse live in this directory as `*.yaml`.
Each catalog has an `id` matching `catalog_ref` values on segment fields.

`ta5py.validate_syntax` resolves `catalog_ref` against these files and **rejects
unknown or non-permitted codes** (fail closed) with the catalog id + version in
the error message. A `catalog_ref` whose YAML cannot be loaded also fails closed.

Leistungsarten (`le_art_krankentransport`) and Positionsnummer membership live in
`packages/leistungen/spec/vN/catalogs/` — ta5py only enforces wire/shape and
ambulance-scope (LE types 41–49).

Out of scope: non-Krankentransport Sammelgruppen and codes not referenced by
SLLA:E fields.
