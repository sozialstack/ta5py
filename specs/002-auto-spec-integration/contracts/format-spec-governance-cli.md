# Contract: Format Spec Governance CLI

**Feature**: `specs/gkv-edi/002-auto-spec-integration`  
**Module**: `packages/gkv-edi`  
**Invocation**: `uv run python packages/gkv-edi/scripts/<script>.py …` (wrappers may add `make` targets)

## Commands

### `check_official_publications`

**Purpose**: Detect new/changed in-scope official publications.

| Arg | Required | Description |
|-----|----------|-------------|
| `--on-demand` | no | Explicit manual run marker (default true for CLI). Detect-only unless `--auto-integrate`. |
| `--scheduled` / `--periodic` | no | Periodic check: auto-integrate new in-scope packages (does **not** change live binding). |
| `--detect-only` | no | Opt out of auto-integrate (dry run). |
| `--auto-integrate` | no | After on-demand detection, scaffold each newly detected candidate on a branch. |
| `--fixture <path>` | no | Use local snapshot instead of network (tests/CI) |
| `--json` | no | Machine-readable DetectionRun output |

**Exit codes**: `0` success (including “no changes”); `1` check failed (unreachable/parse error); `2` usage error.

**Guarantees**: Does not change live binding. On-demand runs do not create git branches unless `--auto-integrate`. `--scheduled`/`--periodic` auto-integrate unless `--detect-only`. Writes DetectionRun under `spec/governance/detections/`.

### `integrate_spec_candidate`

**Purpose**: Start automatic integration on a **new git branch**.

| Arg | Required | Description |
|-----|----------|-------------|
| `--candidate <id>` | yes* | Candidate id from detection (*or `--from-latest-new`) |
| `--from-latest-new` | no | Pick newest detected in-scope candidate without open branch |
| `--base-package <vN>` | no | Package to copy from (default: current live or highest existing) |
| `--dry-run` | no | Show planned branch/paths; no git/fs writes |

**Exit codes**: `0` scaffolded to `awaiting_approval` (or dry-run ok); `1` failure; `2` usage; `3` duplicate open candidate.

**Guarantees**:

- Creates a new branch (unless dry-run)
- Does **not** update `live-version.yaml`
- Does **not** change encoding default until separate go-live
- Refuses out-of-scope candidates

### `approve_live_spec`

**Purpose**: Record human approval/rejection and optionally go live.

| Arg | Required | Description |
|-----|----------|-------------|
| `--candidate <id>` | yes | Candidate to decide |
| `--actor <id>` | yes | Maintainer identity |
| `--approve` / `--reject` | one required | Decision |
| `--go-live` | no | Activate live binding (only valid with `--approve`) |
| `--note <text>` | no | Rationale |

**Exit codes**: `0` ok; `1` rejected go-live (missing approval / invalid package); `2` usage.

**Guarantees**: `--go-live` without a matching approve decision for this candidate **must fail** and leave live binding unchanged.

### `status` (may be subcommand or `governance_status.py`)

**Purpose**: Show last DetectionRun, open candidates, live binding.

**Output** (human): last check time/status; table of candidates with state + branch; current live `vN`.  
**Output** (`--json`): schema-compatible with [governance-state.schema.json](./governance-state.schema.json) subset.

## Non-goals for this contract

- Automatic GitHub PR creation (optional later)
- Automatic field-level PDF transcription
- Changing cert/transfer/api defaults
