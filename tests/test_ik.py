"""Synthetic formal IK validator tests (no real institution / Sozialdaten)."""

from __future__ import annotations

import pytest

import ta5py
import ta5py.ik as ik_mod
from ta5py.ik import Ik, IkError

# Fixed suite (≥10 cases) including Wikipedia anchor 260326822 / 260326823.
# All values are synthetic for tests.
SYNTHETIC_CASES: list[tuple[str, bool]] = [
    ("260326822", True),
    ("260326823", False),
    ("970000011", True),  # Ersatzkennzeichen — formally valid by design
    ("970000099", True),  # Ersatzkennzeichen — formally valid by design
    ("100326822", True),  # prefix-10 form of synthetic Kassennummer 0326822
    ("100326823", False),
    ("000000000", True),  # positions 3–8 all zero → check 0
    ("000000001", False),
    ("109500001", False),  # wrong check for body 10950000
    (" 260326822 ", True),  # trim whitespace
    ("26032682", False),  # too short
    ("2603268220", False),  # too long
    ("26032682a", False),  # non-digit
    ("", False),
]


def test_ik_is_valid_synthetic_suite() -> None:
    for value, expected in SYNTHETIC_CASES:
        assert Ik.is_valid(value) is expected, f"failed for {value!r}"


def test_ik_parse_dissects_parts() -> None:
    ik = Ik.parse("260326822")
    assert ik.classification == "26"
    assert ik.region == "03"
    assert ik.serial == "2682"
    assert ik.check_digit == "2"
    assert ik.digits == "260326822"
    assert ik.body8 == "26032682"
    assert ik.is_formally_valid is True
    assert str(ik) == "260326822"


def test_ik_parse_allows_bad_check_digit() -> None:
    ik = Ik.parse("260326823")
    assert ik.is_formally_valid is False
    assert ik.check_digit == "3"


def test_ik_parse_rejects_non_nine_digit() -> None:
    with pytest.raises(IkError):
        Ik.parse("26032682")
    with pytest.raises(IkError):
        Ik.parse("26032682a")


def test_ik_compute_check_digit_wikipedia_body() -> None:
    assert Ik.compute_check_digit("26032682") == "2"


def test_ik_compute_check_digit_rejects_bad_body() -> None:
    with pytest.raises(IkError):
        Ik.compute_check_digit("2603268")
    with pytest.raises(IkError):
        Ik.compute_check_digit("2603268x")


def test_package_and_module_exports_agree() -> None:
    for value, _ in SYNTHETIC_CASES:
        assert ta5py.Ik.is_valid(value) is ik_mod.Ik.is_valid(value)
    assert ta5py.Ik.parse("260326822") == ik_mod.Ik.parse("260326822")


def test_from_kassennummer_happy_path() -> None:
    ik = Ik.from_kassennummer("0326822")
    assert ik.digits == "100326822"
    assert ik.is_formally_valid is True
    assert Ik.from_kassennummer(" 0326822 ").digits == "100326822"
    assert Ik.is_valid(ik.digits) is True


def test_from_kassennummer_refuses_non_seven() -> None:
    with pytest.raises(IkError):
        Ik.from_kassennummer("032682")
    with pytest.raises(IkError):
        Ik.from_kassennummer("03268222")
    with pytest.raises(IkError):
        Ik.from_kassennummer("032682a")


def test_ersatzkennzeichen_pass_default_check() -> None:
    assert Ik.is_valid("970000011") is True
    assert Ik.is_valid("970000099") is True
    assert Ik.parse("970000011").is_formally_valid is True
