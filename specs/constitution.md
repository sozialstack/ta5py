<!--
Sync Impact Report
- Version change: (new) → 1.0.0
- Modified principles: n/a (initial package constitution)
- Added sections: Core Principles, Domain Scope, Compliance, Governance
- Source: specs/format module constitution (syntactic / machine-readable rules)
  under project constitution v3.3.0 Principle II (gkv-edi)
- Follow-up TODOs: none
-->

# gkv-edi Package Constitution

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
(e.g. `packages/gkv-edi/spec/v21/`, `packages/gkv-edi/spec/v22/`). Adopting a
new published Anlage version is a governed change, not an ad-hoc code edit.

gkv-edi MAY depend on dtapy. gkv-edi MUST NOT import gkv-clearing.

### II. Syntactic Validation Layer

This package MUST provide independently testable **syntactic** validation —
conformance to the active machine-readable spec (structure, lengths, codes,
mandatory fields). Passing syntactic validation MUST NOT be treated as proof of
payer acceptance or certification.

Business plausibility and Leistungsart billing checks belong in gkv-clearing.

Feature specs for this package MUST live under `specs/gkv-edi/NNN-<slug>/`.

## Domain Scope

In scope: TA5, segments, EDIFACT types (SLLA, SLGA, and successors), KK
syntactic validation, Kostenträger catalogs used for encoding.

Out of scope: Leistungsart billing/plausibility, Community-Testate workflows,
Trust Center / PKCS#7 / DTA transport (dtapy).

## Compliance

- gkv-edi PRs MUST name the target package version label(s) and how syntactic
  tests cover them.
- New Anlage versions SHOULD be proposed via issue/PR after monitoring official
  publications.

## Governance

Amendments MUST bump semantic version, set **Last Amended** (ISO `YYYY-MM-DD`),
and include a Sync Impact Report HTML comment.

**Version**: 1.0.0 | **Ratified**: 2026-09-05 | **Last Amended**: 2026-09-05
