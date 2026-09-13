from __future__ import annotations

import json
from pathlib import Path

from ta5py.spec_loader import DEFAULT_VERSION, get_default_version, load_package
from ta5py.validate_syntax import validate_data

FIXTURE = Path(__file__).parent / "fixtures/synthetic/slla_e/happy_claim.json"


def test_default_is_v21():
    assert get_default_version() == "v21"
    assert DEFAULT_VERSION == "v21"


def test_v22_package_selectable_alongside_v21():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    ok_v21 = validate_data(claim, "v21")
    ok_v22 = validate_data(claim, "v22")
    assert ok_v21.syntax_ok, ok_v21.errors
    assert ok_v22.syntax_ok, ok_v22.errors


def test_packages_load_both():
    assert load_package("v21")["version_label"] == "v21"
    assert load_package("v22")["version_label"] == "v22"
