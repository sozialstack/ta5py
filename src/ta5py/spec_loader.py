from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ta5py.package_validate import validate_package_dict

SPEC_ROOT = Path(__file__).resolve().parent / "spec"
_FALLBACK_DEFAULT = "v21"


def get_default_version(spec_root: Path | None = None) -> str:
    """Resolve live/default package label from governance binding."""
    root = spec_root if spec_root is not None else SPEC_ROOT
    path = root / "governance" / "live-version.yaml"
    if path.is_file():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        label = data.get("package_label")
        if isinstance(label, str) and label.strip():
            return label.strip()
    return _FALLBACK_DEFAULT


def refresh_default_version() -> str:
    """Re-read live binding and clear package caches."""
    global DEFAULT_VERSION
    load_package.cache_clear()
    load_dataset_schema.cache_clear()
    DEFAULT_VERSION = get_default_version()
    return DEFAULT_VERSION


# Snapshot at import; refresh_default_version() updates after go-live.
DEFAULT_VERSION = get_default_version()


def resolve_spec_version(spec_version: str | None = None) -> str:
    return spec_version if spec_version is not None else get_default_version()


def _norm_version(spec_version: str) -> str:
    return spec_version if spec_version.startswith("v") else f"v{spec_version}"


def version_dir(spec_version: str) -> Path:
    return SPEC_ROOT / _norm_version(spec_version)


@lru_cache(maxsize=8)
def load_dataset_schema(spec_version: str) -> dict[str, Any]:
    """Legacy v20 JSON Schema stub."""
    path = version_dir(spec_version) / "dataset.schema.json"
    if not path.is_file():
        raise FileNotFoundError(f"Unknown format spec version: {spec_version} ({path})")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"dataset schema must be a JSON object: {path}")
    return data


def has_anlage_package(spec_version: str) -> bool:
    return (version_dir(spec_version) / "provenance.yaml").is_file()


def load_package_at(package_dir: Path, *, version_label: str | None = None) -> dict[str, Any]:
    """Load and validate a package from an arbitrary directory (used by go-live gates)."""
    root = package_dir
    if not root.is_dir():
        raise FileNotFoundError(f"Unknown format spec package: {root}")

    label = version_label or root.name
    provenance = yaml.safe_load((root / "provenance.yaml").read_text(encoding="utf-8"))
    una = yaml.safe_load((root / "una.yaml").read_text(encoding="utf-8"))
    messages: dict[str, Any] = {}
    for path in sorted((root / "messages").glob("*.yaml")):
        messages[path.stem] = yaml.safe_load(path.read_text(encoding="utf-8"))
    segments: dict[str, Any] = {}
    for path in sorted((root / "segments").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        segments[data["code"]] = data

    catalogs: dict[str, Any] = {}
    cat_dir = root / "catalogs"
    if cat_dir.is_dir():
        for path in sorted(cat_dir.glob("*.yaml")):
            if path.name.lower() == "readme.md":
                continue
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data and "id" in data:
                catalogs[data["id"]] = data

    pkg = {
        "version_label": _norm_version(label),
        "provenance": provenance,
        "una": una,
        "messages": messages,
        "segments": segments,
        "catalogs": catalogs,
        "root": str(root),
    }
    errors = validate_package_dict(pkg)
    if errors:
        raise ValueError("Invalid Anlage package: " + "; ".join(errors))
    return pkg


@lru_cache(maxsize=8)
def load_package(spec_version: str | None = None) -> dict[str, Any]:
    label = resolve_spec_version(spec_version)
    return load_package_at(version_dir(label), version_label=label)
