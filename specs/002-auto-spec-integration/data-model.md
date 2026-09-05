# Data Model: Format Spec Governance

**Feature**: `specs/ta5py/002-auto-spec-integration`  
**Date**: 2026-08-17

## Entities

### OfficialPublication

Known or discovered upstream document.

| Field | Description | Validation |
|-------|-------------|------------|
| `id` | Stable id (e.g. `anlage-1-v22`) | Required, unique in manifest |
| `bucket` | `anlage-1` \| `anlage-3` \| `anlage-5` \| `anhang-3` | Required; allowlisted |
| `filename` | Official PDF filename | Required |
| `path` | URL path on gkv-datenaustausch.de | Required |
| `version` | Upstream version number | Required integer/string as published |
| `stand_date` | Publication stand date (ISO date) | Required when known |
| `in_scope` | Ambulance product scope flag | Default true only for allowlisted buckets |

**Relationships**: Many publications may map into one **FormatPackage** (`vN`).

### DetectionRun

One execution of the publication check.

| Field | Description | Validation |
|-------|-------------|------------|
| `id` | Run id (timestamp-based) | Required |
| `started_at` / `finished_at` | ISO timestamps | Required |
| `status` | `ok` \| `failed` \| `partial` | Required |
| `error_message` | Human-readable failure | Required if failed |
| `found_publication_ids` | List of ids seen | Optional |
| `new_or_changed_ids` | Delta vs known manifest | Optional |

### IntegrationCandidate

Work item for a detected package version.

| Field | Description | Validation |
|-------|-------------|------------|
| `id` | e.g. `v23` or `anlage-1:23` | Required, unique |
| `package_label` | Target `packages/ta5py/spec/vN` label | Required (`v` + digits) |
| `branch_name` | Dedicated git branch | Required; unique while open |
| `source_publication_ids` | Publications driving this candidate | Min 1 |
| `state` | See state machine | Required |
| `change_summary_path` | Path to summary artifact | Set after scaffold |
| `created_at` / `updated_at` | ISO timestamps | Required |

### ApprovalDecision

Human gate record.

| Field | Description | Validation |
|-------|-------------|------------|
| `candidate_id` | Links to IntegrationCandidate | Required |
| `decision` | `approve` \| `reject` | Required |
| `actor` | Maintainer identifier | Required non-empty |
| `decided_at` | ISO timestamp | Required |
| `note` | Optional rationale | Optional |

### LiveVersionBinding

Production-facing default package.

| Field | Description | Validation |
|-------|-------------|------------|
| `package_label` | e.g. `v21` | Must exist under `spec/vN` with valid package |
| `activated_at` | ISO timestamp | Required on write |
| `activated_by` | Actor from approval | Required |
| `approval_ref` | Pointer to ApprovalDecision | Required |
| `previous_package_label` | Prior live version | Optional |

## State machine — IntegrationCandidate

```text
detected → integrating → awaiting_approval → live
                ↓                ↓
             failed           rejected
                ↓
            (terminal; may re-open only on new detection identity)
```

| Transition | Trigger | Guard |
|------------|---------|-------|
| → `integrating` | `integrate` command | In-scope; no other open candidate for same id |
| → `awaiting_approval` | Scaffold + branch succeed | Package directory validates structurally |
| → `failed` | Incomplete download / scaffold / git error | Diagnostics recorded |
| → `rejected` | Human reject | Live binding unchanged |
| → `live` | Human approve **and** go-live | ApprovalDecision=`approve` for this candidate; package loads |

**Invariant**: No transition to `live` without ApprovalDecision.approve for the same `candidate_id`.

## Validation rules (cross-entity)

- Out-of-scope publications never create `integrating` candidates.
- At most one non-terminal candidate per `package_label`.
- `LiveVersionBinding.package_label` must successfully `load_package`.
- Detection failure does not mutate live binding or candidates beyond writing a failed DetectionRun.
