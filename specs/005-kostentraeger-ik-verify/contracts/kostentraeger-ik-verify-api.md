# Contract: ta5py Kostenträger IK verification (§ 302)

**Owner**: `packages/ta5py`  
**Module**: `ta5py.kostentraeger` (re-export public helpers from `ta5py` as appropriate)  
**Consumers**: leistungen, kassenclearing, ta5py tests/tooling; any caller allowed to depend on ta5py  
**Out of scope**: dtapy (must not import ta5py), formal Prüfziffer (`ta5py.ik`), Leistungsart billing plausibility, live Trust Center directory, message transport

## Public operations

### Load / refresh (existing + documented)

| Operation | Behavior |
|-----------|----------|
| `ingest_kostentraeger_file(path, spec_version=None, store_path=None)` | Parse one Anhang-3 EDIFACT file; optionally persist store |
| `ingest_kostentraeger_files(paths, …)` | Merge multiple files (deterministic order); later IK wins; stamp `source` |
| `load_store(store_path)` | Load previously persisted JSON store |
| Operator download | `scripts/download_kostentraeger.py` / `make download-kostentraeger` → `var/kostentraeger/` (gitignored) |

Refresh is **not** invoked inside verify.

### `verify_kostentraeger_ik(store, ik: str) -> VerificationResult` (name may be a method on the store)

- Trims leading/trailing whitespace on `ik`.
- If `store` is missing/unusable → `status=registry_unavailable` (no positive existence claim).
- If remaining `ik` is not a usable nine-digit key → treat as not a successful hit (`not_found` or documented invalid-input equivalent; must not return `found`).
- If key absent → `status=not_found`, no `recipient_ik`.
- If key present → `status=found`; set `recipient_ik` / `recipient_determined` from stored `acceptance_ik` (empty ⇒ undetermined).
- Does **not** call the network.
- Does **not** require or imply `Ik.is_valid` (callers may compose separately).

### `resolve_acceptance_ik(store, ik: str) -> str | None` (optional thin helper)

- Convenience: returns recipient IK when `verify` would yield `found` and `recipient_determined`; otherwise `None`.
- MUST NOT invent a recipient when the entry exists without a link.

### Existing `KostentraegerStore.lookup(ik) -> dict | None`

- Remains available for low-level access.
- New verify helpers are the preferred contract for “existence + § 302 recipient” semantics.

## VerificationResult (conceptual fields)

| Field | Type / values |
|-------|----------------|
| status | `found` \| `not_found` \| `registry_unavailable` |
| card_ik | `str` \| omitted when input unusable |
| recipient_ik | `str` \| empty/omitted when undetermined or not found |
| recipient_determined | `bool` |
| name / abrechnungscode / dfue_* / source | optional passthrough when found |
| provenance | optional store-level or per-entry source identity |

Exact Python shape (dataclass / TypedDict / NamedTuple) is an implementation choice; fields above are required for contract tests.

## Error / result conventions

| Case | Behavior |
|------|----------|
| IK not in store | `not_found` |
| Store not loaded | `registry_unavailable` |
| Found, no acceptance link | `found` + `recipient_determined=False` |
| Found with link | `found` + `recipient_determined=True` + recipient IK |
| Formal Prüfziffer fail but listed | Still `found` if key present (formal check is separate) |
| Formal OK but unlisted | `not_found` |
| Messages | Must not include real Sozialdaten |

## Non-goals

- Embedding live download inside verify
- Claiming Testat / Community-Testat / payer acceptance of message content
- Replacing `ta5py.ik` formal validation
- Returning every raw VKG row in MVP (selected recipient + entry metadata only)

## Test anchors (synthetic)

| Setup | Input | Expected |
|-------|-------|----------|
| Fixture store with `123456789` → acceptance `111222333` | `123456789` | `found`, recipient `111222333` |
| Same store | `000000000` | `not_found` |
| No store / unavailable | any | `registry_unavailable` |
| Synthetic entry without acceptance link | that IK | `found`, recipient undetermined |
| Swap edition removing an IK | former IK | becomes `not_found` |
