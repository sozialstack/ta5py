# Feature Specification: Automatic Format Spec Detection & Integration

**Feature Branch**: `002-auto-spec-integration`

**Created**: 2026-08-17

**Status**: Draft

**Input**: User description: "check for new specs automatically. new format specs need to get integrated automatically. strict human approval to go live. new spec will be integrated on a new branch."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Detect newly published format specs (Priority: P1)

A maintainer needs the project to notice when official GKV Datenaustausch publications introduce a new or updated ambulance-relevant Anlage (or Kostenträger) package, so the team does not rely on manual webpage watching to discover mandatory format changes.

**Why this priority**: Missed publications delay compliant encoding and cause avoidable Absetzungen after cutover dates.

**Independent Test**: With a controlled fixture of “current known versions” vs “newly published versions,” run detection and confirm the system reports exactly the new/changed packages—no live payer traffic required.

**Acceptance Scenarios**:

1. **Given** the project’s recorded set of known official package versions, **When** a check finds a newer published ambulance-relevant package, **Then** the system records a detectable “new/changed package” event with package identity and version identifiers.
2. **Given** no change since the last successful check, **When** detection runs, **Then** it reports “no new packages” and does not create an integration work item.
3. **Given** a publication that is out of ambulance (Krankentransport) product scope, **When** detection runs, **Then** that publication is ignored or marked out-of-scope and is not treated as an integration candidate.

---

### User Story 2 - Automatically prepare integration on a new branch (Priority: P1)

When a new in-scope format package is detected, a maintainer needs the project to automatically start integration work on a **new dedicated branch**—including drafting machine-readable package artifacts and change notes—so reviewers can inspect a complete proposed update without touching the live default version.

**Why this priority**: Automatic preparation removes repetitive setup while keeping live encoding unchanged until approved.

**Independent Test**: Trigger integration for a synthetic “new package” fixture; verify a new branch exists with proposed machine-readable artifacts and a clear summary of what changed vs the prior version—without activating that version as live.

**Acceptance Scenarios**:

1. **Given** a newly detected in-scope package, **When** automatic integration starts, **Then** work is created on a new branch distinct from the default/mainline branch and contains the proposed machine-readable package materials for review.
2. **Given** that integration branch, **When** a reviewer inspects it, **Then** they can see what was added/changed relative to the previously known version (fields, catalogs, effective dates, or equivalent change summary).
3. **Given** integration has prepared a branch, **When** no human approval has been granted, **Then** the live/default ambulance format version used for encoding and validation remains the previously approved version.

---

### User Story 3 - Strict human approval before go-live (Priority: P1)

A maintainer must explicitly approve promotion of an integrated package to “live” (the default or selectable production-facing version for ambulance clearing). No automatic go-live is allowed.

**Why this priority**: Incorrect or incomplete Anlage adoption in production is a compliance and liability risk; human gate is mandatory.

**Independent Test**: Complete an integration branch for a synthetic package; attempt go-live without approval (must fail); approve then go-live (must succeed and become the active selectable version).

**Acceptance Scenarios**:

1. **Given** a prepared integration branch that has not been approved, **When** anyone requests go-live / default activation, **Then** the request is rejected and the live version is unchanged.
2. **Given** an authorized human approval recorded for that specific package version on that branch, **When** go-live is requested, **Then** the package becomes available as the live/default (or explicitly selectable) ambulance version and this activation is auditable.
3. **Given** two candidate versions pending review, **When** only one is approved, **Then** only the approved version can go live; the other remains non-live.

---

### User Story 4 - Review status of detection and pending integrations (Priority: P2)

A maintainer wants a clear view of last check time, detected candidates, open integration branches, and approval/go-live state so they know what needs human attention.

**Why this priority**: Operational visibility supports the approval gate; secondary to detection + gated promotion.

**Independent Test**: Seed detection and integration states; open the status view and verify each candidate’s state (detected, integrating, awaiting approval, live, rejected/out-of-scope).

**Acceptance Scenarios**:

1. **Given** at least one pending integration, **When** a maintainer opens status, **Then** they see package identity, branch reference, and current gate state.
2. **Given** a package that was rejected or marked out-of-scope, **When** status is viewed, **Then** it is distinguishable from awaiting-approval and live items.

---

### Edge Cases

- Detection cannot reach the official publication source: report failure clearly; do not invent versions or silently skip without a recorded failed check.
- Partial or corrupt download of a newly published package: abort integration for that candidate; do not commit incomplete machine-readable artifacts as ready-for-approval.
- Re-detection of an already integrated or already rejected version: do not open duplicate integration branches; link to the existing record.
- Conflicting simultaneous detections for the same package identity: at most one open integration branch per package version.
- Human rejects an integration: branch/work remains non-live; live default stays unchanged; rejection is recorded so auto-retry does not re-promote without a new approval.
- Attempt to go live an older version over a newer live version: allowed only with explicit human approval and a clear warning in the approval/go-live flow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST periodically (and on-demand) check official GKV Datenaustausch publication sources for new or updated ambulance-relevant format packages (Anlage 1, Anlage 3, Anlage 5, and Anhang 3 Kostenträger materials in product scope).
- **FR-002**: System MUST compare discovered publications against the project’s recorded known package versions and emit a durable detection record when a new or changed in-scope package is found.
- **FR-003**: System MUST ignore or classify as out-of-scope publications that do not apply to Krankentransport / ambulance product scope.
- **FR-004**: When a new in-scope package is detected, System MUST automatically start integration on a **new dedicated branch**, preparing proposed machine-readable package artifacts for review.
- **FR-005**: Automatic integration MUST NOT change the live/default ambulance format version used for encoding or validation.
- **FR-006**: System MUST require explicit human approval before any newly integrated package can go live (become the default or production-facing selectable version).
- **FR-007**: System MUST reject go-live requests that lack a recorded human approval for that exact package version.
- **FR-008**: System MUST keep an auditable history of detections, integration branches, approvals, rejections, and go-live activations (who/when/what version)—without storing Sozialdaten.
- **FR-009**: System MUST present maintainer-visible status for last check outcome, pending candidates, approval state, and live version identity.
- **FR-010**: System MUST handle unreachable sources and incomplete package material as failures that block promotion, with human-readable diagnostics.
- **FR-011**: System MUST avoid duplicate open integration branches for the same package version identity.

### Key Entities

- **Official Package Publication**: A discovered upstream publication identity (Anlage/Kostenträger family, version/label, publication/effective markers as available).
- **Detection Record**: Result of a check run (time, success/failure, packages found, in-scope vs out-of-scope).
- **Integration Candidate**: Link between a detected publication, its dedicated branch, prepared machine-readable artifacts, and review summary.
- **Approval Decision**: Human allow/deny for a specific candidate version, with actor and timestamp.
- **Live Version Binding**: Which package version is currently live/default (or listed as selectable production-facing) for ambulance format use.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a synthetic “new in-scope package” appears in the monitored source fixture, detection surfaces it within one scheduled check cycle (or one on-demand run) with 100% identification of the new version identity.
- **SC-002**: 100% of automatic integrations for new packages land on a new branch and leave the prior live/default version unchanged until approval.
- **SC-003**: 0 go-live activations occur without a recorded human approval in verification tests (including negative tests that attempt unauthorized promotion).
- **SC-004**: Maintainers can determine check health and every pending candidate’s gate state in under 2 minutes from the status view alone.
- **SC-005**: Out-of-scope publications never become live ambulance format versions in acceptance tests.
- **SC-006**: Failed source access or incomplete package material blocks go-live in 100% of fault-injection cases and produces a clear failure reason.

## Assumptions

- “Specs” means official GKV Datenaustausch / Sonstige Leistungserbringer Anlage and related Kostenträger publications in the same product scope as the existing ambulance format work—not Spec Kit feature specs under `specs/`.
- Ambulance-only scope continues: other SLE Leistungsbereiche remain out of product scope.
- “Integrated automatically” means preparing machine-readable artifacts and review materials on a new branch; it does not mean unsupervised activation.
- “Go live” means making a version the live/default (or explicitly production-selectable) ambulance format package for encoding/validation.
- Human approvers are project maintainers (or roles with equivalent authority); end-user clearing operators do not approve project-wide format adoption.
- Parallel version support from the existing format feature remains: older versions may stay available after a new version goes live, unless a later feature explicitly retires them.
- Detection cadence defaults to at least daily scheduled checks plus manual on-demand runs; exact hosting of the scheduler is an implementation concern.
- Official PDFs/binaries may be fetched for derivation; only synthetic claim data is used in tests.
