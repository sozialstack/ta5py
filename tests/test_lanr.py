"""Synthetic formal LANR validator tests (no real physician / Sozialdaten)."""

from __future__ import annotations

import pytest

import ta5py
import ta5py.lanr as lanr_mod
from ta5py.lanr import Lanr, LanrError

# Fixed suite (≥8 cases) including KBV-style anchor 123456601 / 123456901.
# All values are synthetic for tests.
SYNTHETIC_CASES: list[tuple[str, bool]] = [
    ("123456601", True),
    ("123456901", False),
    ("234567701", True),
    ("100000601", True),
    ("987654401", True),
    ("555555501", True),
    ("999999901", True),
    ("123456699", True),  # valid Prüfziffer with specialty 99 (no catalog reject)
    (" 123456601 ", True),  # trim whitespace
    ("12345660", False),  # too short
    ("1234566010", False),  # too long
    ("12345660a", False),  # non-digit
    ("", False),
]


def test_lanr_is_valid_synthetic_suite() -> None:
    for value, expected in SYNTHETIC_CASES:
        assert Lanr.is_valid(value) is expected, f"failed for {value!r}"


def test_lanr_parse_dissects_parts() -> None:
    lanr = Lanr.parse("123456601")
    assert lanr.physician == "123456"
    assert lanr.check_digit == "6"
    assert lanr.specialty == "01"
    assert lanr.digits == "123456601"
    assert lanr.body6 == "123456"
    assert lanr.is_formally_valid is True
    assert str(lanr) == "123456601"


def test_lanr_parse_allows_bad_check_digit() -> None:
    lanr = Lanr.parse("123456901")
    assert lanr.is_formally_valid is False
    assert lanr.check_digit == "9"


def test_lanr_parse_rejects_non_nine_digit() -> None:
    with pytest.raises(LanrError):
        Lanr.parse("12345660")
    with pytest.raises(LanrError):
        Lanr.parse("12345660a")


def test_lanr_compute_check_digit_kbv_body() -> None:
    assert Lanr.compute_check_digit("123456") == "6"


def test_lanr_compute_check_digit_rejects_bad_body() -> None:
    with pytest.raises(LanrError):
        Lanr.compute_check_digit("12345")
    with pytest.raises(LanrError):
        Lanr.compute_check_digit("12345x")


def test_package_and_module_exports_agree() -> None:
    for value, _ in SYNTHETIC_CASES:
        assert ta5py.Lanr.is_valid(value) is lanr_mod.Lanr.is_valid(value)
    assert ta5py.Lanr.parse("123456601") == lanr_mod.Lanr.parse("123456601")


def test_specialty_99_not_excluded_by_default() -> None:
    assert Lanr.is_valid("123456699") is True
