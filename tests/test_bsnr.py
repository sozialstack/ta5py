"""Synthetic formal BSNR validator tests (no real practice / Sozialdaten)."""

from __future__ import annotations

import pytest

import ta5py
import ta5py.bsnr as bsnr_mod
from ta5py.bsnr import Bsnr, BsnrError

# Fixed suite (≥6 cases). All values are synthetic for tests.
SYNTHETIC_CASES: list[tuple[str, bool]] = [
    ("031234567", True),
    ("991234567", True),  # uncommon prefix — not rejected by default
    ("351234567", True),  # special-prefix-shaped synthetic
    (" 031234567 ", True),  # trim whitespace
    ("03123456", False),  # too short
    ("0312345670", False),  # too long
    ("03123456a", False),  # non-digit
    ("", False),
]


def test_bsnr_is_valid_synthetic_suite() -> None:
    for value, expected in SYNTHETIC_CASES:
        assert Bsnr.is_valid(value) is expected, f"failed for {value!r}"


def test_bsnr_parse_dissects_parts() -> None:
    bsnr = Bsnr.parse("031234567")
    assert bsnr.kv_region == "03"
    assert bsnr.site == "1234567"
    assert bsnr.digits == "031234567"
    assert bsnr.is_formally_valid is True
    assert str(bsnr) == "031234567"


def test_bsnr_parse_rejects_non_nine_digit() -> None:
    with pytest.raises(BsnrError):
        Bsnr.parse("03123456")
    with pytest.raises(BsnrError):
        Bsnr.parse("03123456a")


def test_package_and_module_exports_agree() -> None:
    for value, _ in SYNTHETIC_CASES:
        assert ta5py.Bsnr.is_valid(value) is bsnr_mod.Bsnr.is_valid(value)
    assert ta5py.Bsnr.parse("031234567") == bsnr_mod.Bsnr.parse("031234567")


def test_uncommon_prefix_not_excluded_by_default() -> None:
    assert Bsnr.is_valid("991234567") is True
