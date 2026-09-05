<!--
Sync Impact Report
- Version change: 2.0.0 → 2.0.1
- Modified principles:
  - I — MUST NOT import dtapy, leistungen, or kassenclearing
  - II — billing checks belong in leistungen
- Added sections: none
- Removed sections: none
- Follow-up TODOs: none
-->

# ta5py Package Constitution

Subordinate to `.specify/memory/constitution.md`. On conflict with cross-cutting
project rules, the project constitution wins.

## Core Principles

### I. Machine-Readable, Versioned Domain Specifications

Formal regulatory sources (Anlage 1 Satzaufbau, Anlage 3 Schlüsselverzeichnisse,
and successors used for TA5/EDIFACT) MUST be prepared as structured,
machine-readable artifacts (YAML and/or JSON Schema per segment/field), not only
as free-text documentation.

Each field definition MUST capture at least: name, position, length,
mandatory/optional, and allowed values where defined. Mandatory vs optional rules
MUST reflect Leistungserbringer type differences where the TA5 defines them.

Spec versioning MUST be explicit and owned under this package’s spec tree
(e.g. `packages/ta5py/spec/v21/`, `packages/ta5py/spec/v22/`). Adopting a
new published Anlage version is a governed change, not an ad-hoc code edit.

This package MUST own UNA handling and `wire.py` (`join_segment` / `split_*`).
It MAY wrap pydifact behind `wire.py`; it MUST NOT require pydifact when the
local tokenizer is sufficient.

ta5py MUST NOT import dtapy, leistungen, or kassenclearing.

### II. Syntactic Validation Layer

This package MUST provide independently testable **syntactic** validation —
conformance to the active machine-readable spec (structure, lengths, codes,
mandatory fields). Passing syntactic validation MUST NOT be treated as proof of
payer acceptance or certification.

Business plausibility and Leistungsart billing checks belong in leistungen.

Feature specs for this package MUST live under `specs/ta5py/NNN-<slug>/`.

## Domain Scope

In scope: TA5, segments, EDIFACT types (SLLA, SLGA, and successors), KK
syntactic validation, Kostenträger catalogs used for encoding.

Out of scope: Leistungsart billing/plausibility, Community-Testate workflows,
Trust Center / PKCS#7 / DTA transport (dtapy).

## Compliance

- ta5py PRs MUST name the target package version label(s) and how syntactic
  tests cover them.
- New Anlage versions SHOULD be proposed via issue/PR after monitoring official
  publications.

## Governance

Amendments MUST bump semantic version, set **Last Amended** (ISO `YYYY-MM-DD`),
and include a Sync Impact Report HTML comment.

**Version**: 2.0.1 | **Ratified**: 2026-09-05 | **Last Amended**: 2026-09-05
