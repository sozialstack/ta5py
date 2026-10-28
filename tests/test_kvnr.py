"""Synthetic formal KVNR validator tests (no real insuree / Sozialdaten)."""

from __future__ import annotations

import pytest

import ta5py
import ta5py.kvnr as kvnr_mod
from ta5py.kvnr import Kvnr, KvnrError

# Fixed suite (≥8 cases). A000500015 is the published Anlage 1 illustration.
# A000000002 is the allowlisted synthetic series (complement-to-10 would be 8).
SYNTHETIC_CASES: list[tuple[str, bool]] = [
    ("A000500015", True),
    ("A000500016", False),
    ("C000500021", True),
    ("A000000002", True),
    ("A000000008", False),
    ("Z999999997", True),
    ("B123456782", True),
    ("a000500015", True),
    (" A000500015 ", True),
    ("A00050001", False),
    ("A0005000150", False),
    ("", False),
    ("1000500015", False),
    ("A0005 0015", False),
    ("Ä000500015", False),
]


def test_kvnr_is_valid_synthetic_suite() -> None:
    for value, expected in SYNTHETIC_CASES:
        assert Kvnr.is_valid(value) is expected, f"failed for {value!r}"


def test_kvnr_parse_dissects_parts() -> None:
    kvnr = Kvnr.parse("A000500015")
    assert kvnr.letter == "A"
    assert kvnr.serial == "00050001"
    assert kvnr.check_digit == "5"
    assert kvnr.digits == "A000500015"
    assert kvnr.body9 == "A00050001"
    assert kvnr.is_formally_valid is True
    assert str(kvnr) == "A000500015"


def test_kvnr_parse_casefolds_and_trims() -> None:
    kvnr = Kvnr.parse(" a000500015 ")
    assert kvnr.letter == "A"
    assert kvnr.digits == "A000500015"
    assert kvnr.is_formally_valid is True


def test_kvnr_parse_allows_bad_check_digit() -> None:
    kvnr = Kvnr.parse("A000500016")
    assert kvnr.is_formally_valid is False
    assert kvnr.check_digit == "6"


def test_kvnr_parse_rejects_bad_structure() -> None:
    with pytest.raises(KvnrError):
        Kvnr.parse("A00050001")
    with pytest.raises(KvnrError):
        Kvnr.parse("A0005000150")
    with pytest.raises(KvnrError):
        Kvnr.parse("Ä000500015")


def test_kvnr_compute_check_digit_anchors() -> None:
    assert Kvnr.compute_check_digit("A00050001") == "5"
    assert Kvnr.compute_check_digit("a00050001") == "5"
    assert Kvnr.compute_check_digit("A00000000") == "2"
    assert Kvnr.compute_check_digit("C00050002") == "1"


def test_kvnr_compute_check_digit_rejects_bad_body() -> None:
    with pytest.raises(KvnrError):
        Kvnr.compute_check_digit("A0005000")
    with pytest.raises(KvnrError):
        Kvnr.compute_check_digit("A0005000x")


def test_package_and_module_exports_agree() -> None:
    for value, _expected in SYNTHETIC_CASES:
        assert ta5py.Kvnr.is_valid(value) is kvnr_mod.Kvnr.is_valid(value)
    assert ta5py.Kvnr.parse("A000500015") == kvnr_mod.Kvnr.parse("A000500015")
    assert ta5py.KvnrError is kvnr_mod.KvnrError


def test_issuance_exclusions_are_not_applied() -> None:
    assert Kvnr.is_valid("M000066602") is True
    assert Kvnr.is_valid("K111111115") is True


def test_twenty_character_form_is_invalid() -> None:
    assert Kvnr.is_valid("A0005000151099111144") is False
    with pytest.raises(KvnrError):
        Kvnr.parse("A0005000151099111144")


def test_inv_versicherten_id_stays_max_length_12() -> None:
    from ta5py.spec_loader import SPEC_ROOT

    spec_root = SPEC_ROOT
    for version in ("v21", "v22"):
        text = (spec_root / version / "segments" / "INV.yaml").read_text(encoding="utf-8")
        assert "name: versicherten_id" in text
        assert "max_length: 12" in text
        assert "value_type: AN" in text
