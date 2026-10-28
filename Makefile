.PHONY: install test typecheck download-format-pdfs download-kostentraeger convert-pdfs check-synthetic

install:
	uv sync --group dev

test:
	uv run pytest -q

typecheck:
	uv run mypy

download-format-pdfs:
	uv run python scripts/download_official_pdfs.py

download-kostentraeger:
	uv run python scripts/download_kostentraeger.py

convert-pdfs:
	uv run python scripts/convert_pdfs_to_md.py --bulk

check-synthetic:
	uv run python scripts/check_synthetic_fixtures.py
