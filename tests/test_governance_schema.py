from __future__ import annotations

import pytest

from ta5py.governance.validate_state import SCHEMA_PATH, load_governance_schema


def test_governance_schema_path_exists_and_loads():
    assert SCHEMA_PATH.is_file(), SCHEMA_PATH
    schema = load_governance_schema()
    assert schema.get("type") == "object"
    assert "live" in schema.get("properties", {})


def test_load_governance_schema_fails_when_missing(monkeypatch, tmp_path):
    import ta5py.governance.validate_state as vs

    monkeypatch.setattr(vs, "SCHEMA_PATH", tmp_path / "missing.json")
    with pytest.raises(FileNotFoundError):
        vs.load_governance_schema()
