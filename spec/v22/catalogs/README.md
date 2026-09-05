# Anlage 3 catalogs (Slice B) — fail-closed membership

Ambulance-referenced Schlüsselverzeichnisse live in this directory as `*.yaml`.
Each catalog has an `id` matching `catalog_ref` values on segment fields.

`format.validate_syntax` resolves `catalog_ref` against these files and **rejects
unknown or non-permitted codes** (fail closed) with the catalog id + version in
the error message.

Out of scope: non-Krankentransport Sammelgruppen and codes not referenced by
SLLA:E fields.
