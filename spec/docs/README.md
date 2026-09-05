# Official GKV-Datenaustausch source PDFs

These PDFs are **authoritative**. Machine-readable YAML under `packages/ta5py/spec/vN/` is a Krankentransport-only project interpretation.

- Discovery: https://www.gkv-datenaustausch.de/leistungserbringer/sonstige_leistungserbringer/sonstige_leistungserbringer.jsp
- Scope: ambulance / SLLA:E only — do not treat other SLE Leistungsbereiche as in-product
- On conflict between YAML and PDF: **PDF wins** until a governed package correction lands
- PDFs are gitignored; Markdown companions (`.md` next to each PDF) are for reading/search — the PDF remains authoritative
- Fetch PDFs (and generate Markdown companions; PDFs are kept):

```bash
uv run python packages/ta5py/scripts/download_official_pdfs.py
# or: make download-format-pdfs
```

- Convert a single PDF or all in-repo PDFs without deleting sources:

```bash
uv run python scripts/convert_pdfs_to_md.py path/to/file.pdf
make convert-pdfs
```

See `sources.manifest.yaml` for exact URLs and stand dates.

## Checking for new publications

Use the governance check (fixture or maintainer workflow) — see `packages/ta5py/spec/governance/README.md` and:

```bash
uv run python packages/ta5py/scripts/check_official_publications.py --fixture <discovered-manifest.yaml>
```

New packages are integrated on a **new branch**; live default changes only after human approve + go-live.

Scheduled/periodic checks (`--scheduled` / `--periodic`) auto-integrate unless `--detect-only`.
On-demand CLI remains detect-only unless `--auto-integrate`. See
[`specs/ta5py/002-auto-spec-integration/quickstart.md`](../../../../specs/ta5py/002-auto-spec-integration/quickstart.md)
for the daily cron recipe.
