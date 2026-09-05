# Research: Automatic Format Spec Detection & Integration

**Feature**: `specs/ta5py/002-auto-spec-integration`  
**Date**: 2026-08-17  
**Directive**: Integrate new specs on a **new branch**; strict human approval before go-live.

## R1 — What “new specs” means

**Decision**: Track **official GKV-Datenaustausch SLE publications** listed for ambulance-relevant documents (Anlage 1, Anlage 3, Anlage 5, Anhang 3), not Spec Kit feature folders under `specs/`.

**Rationale**: Matches product domain and existing `packages/ta5py/spec/official/sources.manifest.yaml` + constitution Principle III.

**Alternatives considered**:
- Watch Spec Kit `specs/**` — rejected (wrong layer; user intent is format Anlagen).
- Full multi-SLE monitoring — rejected (ambulance-only constitution/product scope).

## R2 — Detection mechanism

**Decision**: Two-layer check:

1. **Manifest diff**: Compare remote publication identifiers (path/filename/version/stand_date) against `sources.manifest.yaml` using a **discoverable catalog** derived from the official overview page and/or a maintained remote index file the project controls after human curation of URL patterns.
2. **Content freshness**: For known URLs, optional HTTP HEAD/GET size/ETag/Last-Modified (when available) to detect replaced files at the same path.

MVP focuses on **new document ids / version numbers / stand dates** appearing relative to the committed manifest. Full HTML scraping robustness is secondary: ship a parser for the known overview page structure with fixture snapshots; if parse fails, record a failed detection (FR-010).

**Rationale**: Manifest is already the project’s source of truth for downloads; extending it keeps one registry.

**Alternatives considered**:
- Manual-only issue filing — rejected (user asked for automatic checks).
- Depend on unofficial third-party mirrors — rejected (authoritative site preferred).

## R3 — Automatic integration on a new branch

**Decision**: `integrate_spec_candidate` MUST:

1. Create/switch to a **new git branch** named `format/spec-v{N}-integration` (or `002-spec-v{N}` if already on a feature branch workflow—final pattern documented in CLI contract; must be unique per package version).
2. Copy previous closest package tree (e.g. `v22` → `v23`) under `packages/ta5py/spec/v{N}/`.
3. Update `provenance.yaml` placeholders (version, stand dates, PDF paths) and add/adjust `sources.manifest.yaml` entries for the new PDFs.
4. Write a `CHANGE_SUMMARY.md` (or governance candidate file) listing detected upstream deltas vs prior version.
5. **Not** change `live-version.yaml` / `DEFAULT_VERSION`.

Human maintainers still transcribe field-level YAML deltas from PDFs; automation provides scaffold + branch + provenance hooks so work is reviewable.

**Rationale**: User planning directive; constitution requires governed adoption; scaffolding removes boilerplate without unsupervised semantic transcription (PDF remains authoritative).

**Alternatives considered**:
- Commit directly to main — rejected (go-live risk; conflicts with approval gate).
- Fully automated PDF→YAML field extraction — deferred (high error risk; out of MVP scope).
- PR-only without local branch script — rejected as sole path; branch creation is required; opening a PR can be a later optional step.

## R4 — Live version binding & approval gate

**Decision**: Introduce `packages/ta5py/spec/governance/live-version.yaml` as the **single source of truth** for the live/default package label. `spec_loader.DEFAULT_VERSION` (or equivalent) loads from that file at import/runtime with a safe fallback only for missing file during migration (`v21` until first binding commit).

Go-live path:

1. Candidate status `awaiting_approval`
2. `approve_live_spec --version vN --actor <id>` writes an approval record
3. Explicit `--go-live` (same or follow-up command) updates `live-version.yaml` **only if** approval exists for that version
4. Tests assert unauthorized go-live fails

**Rationale**: Spec FR-005–FR-007; prevents silent DEFAULT_VERSION edits in integrate.

**Alternatives considered**:
- Change DEFAULT_VERSION constant in code during integrate — rejected (too easy to merge accidentally).
- Rely only on GitHub CODEOWNERS / branch protection — helpful but insufficient alone for local/CI clarity; keep explicit approval artifact.

## R5 — Scheduler vs on-demand

**Decision**: Provide CLI entry points runnable from CI cron or maintainer machines (`check`, `integrate`, `status`, `approve`/`go-live`). Document a suggested daily schedule in quickstart; do not require a specific CI vendor in MVP.

**Rationale**: Spec assumes at least daily + on-demand; hosting is an implementation detail.

## R6 — Deduping candidates

**Decision**: Candidate identity key = `{anlage_family}:{version}` (e.g. `anlage-1:23`) or composite package label `v23` when the project versions packages as a coordinated set. One open candidate file + at most one integration branch per identity. Re-detection links to existing candidate.

**Rationale**: FR-011; matches how `v21`/`v22` packages already bundle Anlage 1+3.

## R7 — Out-of-scope publications

**Decision**: Classifier uses allowlist of document buckets already in product scope (`anlage-1`, `anlage-3`, `anlage-5`, `anhang-3`). Other SLE PDFs are recorded as `out_of_scope` when discovered, never integrated.

**Rationale**: Constitution + existing feature ambulance-only scope.

## Resolved clarifications

All Technical Context items resolved; no remaining NEEDS CLARIFICATION markers for planning.
