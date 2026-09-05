# Quickstart: Format Spec Detection & Gated Integration

Validate the governance pipeline end-to-end with fixtures (no real Sozialdaten; network optional).

## Prerequisites

- Repo checkout with `uv` available
- Git available on PATH
- Format module installable (`uv sync` from repo root / format workspace as documented in root README)

## 1. Status (baseline)

```bash
uv run python packages/gkv-edi/scripts/governance_status.py --json
```

**Expect**: Current live package label (initially `v21` after migration), empty or existing candidates list.

## 2. Detect with fixture (no network)

```bash
uv run python packages/gkv-edi/scripts/check_official_publications.py \
  --fixture packages/gkv-edi/tests/fixtures/governance/sources_with_new_version.yaml \
  --json
```

**Expect**: DetectionRun `status=ok` and `new_or_changed_ids` non-empty for the synthetic new version. Live binding unchanged.

Re-run the same fixture:

**Expect**: No duplicate open candidate for the same package identity (FR-011).

## 3. Integrate on a new branch

```bash
uv run python packages/gkv-edi/scripts/integrate_spec_candidate.py --from-latest-new
```

**Expect**:

- New git branch created (name printed)
- `packages/gkv-edi/spec/vN/` scaffold present on that branch
- Candidate state `awaiting_approval`
- `spec/governance/live-version.yaml` **unchanged**
- Encoding default still previous live version

Dry-run check:

```bash
uv run python packages/gkv-edi/scripts/integrate_spec_candidate.py --from-latest-new --dry-run
```

## 4. Reject unauthorized go-live

```bash
uv run python packages/gkv-edi/scripts/approve_live_spec.py \
  --candidate <id> --actor ci-bot --go-live
```

**Expect**: Failure (exit ≠ 0); live binding unchanged. (Missing `--approve`.)

## 5. Approve and go live

```bash
uv run python packages/gkv-edi/scripts/approve_live_spec.py \
  --candidate <id> --actor maintainer@example --approve --go-live
```

**Expect**: Candidate `live`; `live-version.yaml` points at new `vN`; `load_package` / default version reflects binding; audit fields `activated_by` / `approval_ref` set.

## 6. Automated tests

```bash
uv run pytest packages/gkv-edi/tests/test_publication_detect.py \
  packages/gkv-edi/tests/test_integrate_on_branch.py \
  packages/gkv-edi/tests/test_approve_live_gate.py -q
```

**Expect**: All pass, including negative gate tests (SC-003).

## Notes

- Prefer `--fixture` in CI. Live checks against gkv-datenaustausch.de are for maintainer machines or a scheduled job with clear failure alerting.
- Field-level YAML transcription from new PDFs remains a human review step on the integration branch; automation owns detect → branch scaffold → approval gate.
- Contracts: [format-spec-governance-cli.md](./contracts/format-spec-governance-cli.md), [governance-state.schema.json](./contracts/governance-state.schema.json).

## Daily scheduled check (auto-integrate)

Periodic detection **auto-integrates** onto a new branch by default and **never** flips `live-version.yaml`. Manual/on-demand CLI stays detect-only unless you pass `--auto-integrate`.

Maintainer / cron recipe (daily, ~06:17 UTC):

```bash
uv run python packages/gkv-edi/scripts/check_official_publications.py \
  --scheduled \
  --network \
  --update-manifest-metadata
```

Dry run (detect only, no branch scaffold):

```bash
uv run python packages/gkv-edi/scripts/check_official_publications.py \
  --scheduled --detect-only --network
```

On-demand equivalent of auto-integrate:

```bash
uv run python packages/gkv-edi/scripts/check_official_publications.py \
  --on-demand --fixture <discovered.yaml> --auto-integrate
```

GitHub Actions: [`.github/workflows/format-spec-detect.yml`](../../.github/workflows/format-spec-detect.yml) (`cron: 17 6 * * *` plus `workflow_dispatch`). Use `detect_only=true` on a manual run for a dry check.
