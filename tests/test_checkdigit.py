"""Kernels and FormalIdentifier contract shared by the identifier value types."""

from __future__ import annotations

import pytest

import ta5py
from ta5py.bsnr import Bsnr
from ta5py.checkdigit import (
    FormalIdentifier,
    complement_mod10,
    cross_sum_mod10,
    weighted_sum,
)
from ta5py.ik import Ik
from ta5py.kvnr import Kvnr
from ta5py.lanr import Lanr


def test_cross_sum_mod10_matches_ik_and_kvnr_anchors() -> None:
    # IK positions 3–8 of 260326822, weights 2,1,2,1,2,1 → Prüfziffer 2.
    assert cross_sum_mod10("032682", (2, 1, 2, 1, 2, 1)) == "2"
    # KVNR A00050001 expanded (A → 01) with weights 1,2,… → Prüfziffer 5.
    assert cross_sum_mod10("0100050001", (1, 2, 1, 2, 1, 2, 1, 2, 1, 2)) == "5"


def test_complement_mod10_matches_lanr_anchor() -> None:
    # 123456 × 4,9,4,9,4,9 = 144 → (10 − 4) mod 10 = 6.
    assert weighted_sum("123456", (4, 9, 4, 9, 4, 9)) == 144
    assert complement_mod10(144) == "6"
    assert complement_mod10(0) == "0"
    assert complement_mod10(10) == "0"


def test_weight_above_two_does_not_match_cross_sum() -> None:
    """Subtract-9 is not a digit sum once a product exceeds 18."""
    assert cross_sum_mod10("9", (9,)) == "2"
    assert complement_mod10(weighted_sum("9", (9,))) == "9"


def test_kernels_reject_bad_digits() -> None:
    with pytest.raises(ValueError):
        cross_sum_mod10("", (1,))
    with pytest.raises(ValueError):
        cross_sum_mod10("12", (1,))
    with pytest.raises(ValueError):
        cross_sum_mod10("1a", (1, 2))
    with pytest.raises(ValueError):
        weighted_sum("12", (1,))


def test_value_types_satisfy_formal_identifier() -> None:
    samples: list[FormalIdentifier] = [
        Ik.parse("260326822"),
        Ik.parse("260326823"),
        Lanr.parse("123456601"),
        Bsnr.parse("031234567"),
        Kvnr.parse("A000500015"),
    ]
    for value in samples:
        assert isinstance(value, FormalIdentifier)
        assert str(value) == value.digits
        assert type(value).is_valid(value.digits) is value.is_formally_valid


def test_checkdigit_is_not_a_package_export() -> None:
    assert "FormalIdentifier" not in ta5py.__all__
    assert "cross_sum_mod10" not in ta5py.__all__
    assert not hasattr(ta5py, "FormalIdentifier")
    assert not hasattr(ta5py, "cross_sum_mod10")
