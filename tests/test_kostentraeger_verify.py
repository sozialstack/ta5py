"""Synthetic Kostenträgerdatei registry verification tests (§ 302)."""

from __future__ import annotations

from pathlib import Path

import ta5py
from ta5py.ik import Ik
from ta5py.kostentraeger import (
    VerificationStatus,
    ingest_kostentraeger_file,
    resolve_acceptance_ik,
    verify_kostentraeger_ik,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures/synthetic/kostentraeger"
E1 = FIXTURE_DIR / "anhang3_kotr.edifact"
E2 = FIXTURE_DIR / "edition_e2_subset.edifact"
NO_LINK = FIXTURE_DIR / "no_acceptance_link.edifact"

# ≥10 synthetic card IKs present in E1 (existence suite)
PRESENT_IKS = [
    "123456789",
    "987654321",
    "111111111",
    "000000004",
    "000000005",
    "000000006",
    "000000007",
    "000000008",
    "000000009",
    "000000010",
    "000000011",
]


def test_verify_found_and_not_found_suite():
    store = ingest_kostentraeger_file(E1, "v21")
    for ik in PRESENT_IKS:
        result = verify_kostentraeger_ik(store, ik)
        assert result.status == VerificationStatus.FOUND
        assert result.card_ik == ik
    missing = verify_kostentraeger_ik(store, "000000000")
    assert missing.status == VerificationStatus.NOT_FOUND
    assert missing.recipient_ik == ""
    assert missing.recipient_determined is False


def test_verify_registry_unavailable():
    result = verify_kostentraeger_ik(None, "123456789")
    assert result.status == VerificationStatus.REGISTRY_UNAVAILABLE
    assert result.recipient_determined is False


def test_verify_rejects_non_nine_digit_as_not_found():
    store = ingest_kostentraeger_file(E1, "v21")
    for bad in ("", "   ", "123", "12345678a", "1234567890"):
        result = verify_kostentraeger_ik(store, bad)
        assert result.status == VerificationStatus.NOT_FOUND


def test_verify_trims_whitespace():
    store = ingest_kostentraeger_file(E1, "v21")
    result = verify_kostentraeger_ik(store, "  123456789  ")
    assert result.status == VerificationStatus.FOUND
    assert result.card_ik == "123456789"


def test_resolve_recipient_from_link():
    store = ingest_kostentraeger_file(E1, "v21")
    result = store.verify("123456789")
    assert result.status == VerificationStatus.FOUND
    assert result.recipient_determined is True
    assert result.recipient_ik == "111222333"
    assert "Synthetic Ambulance" in result.name
    assert resolve_acceptance_ik(store, "123456789") == "111222333"


def test_found_but_recipient_undetermined():
    store = ingest_kostentraeger_file(NO_LINK, "v21")
    result = verify_kostentraeger_ik(store, "555555555")
    assert result.status == VerificationStatus.FOUND
    assert result.recipient_determined is False
    assert result.recipient_ik == ""
    assert resolve_acceptance_ik(store, "555555555") is None


def test_resolve_absent_returns_none():
    store = ingest_kostentraeger_file(E1, "v21")
    assert resolve_acceptance_ik(store, "000000000") is None
    assert resolve_acceptance_ik(None, "123456789") is None


def test_edition_swap_changes_outcomes():
    e1 = ingest_kostentraeger_file(E1, "v21")
    assert verify_kostentraeger_ik(e1, "123456789").status == VerificationStatus.FOUND
    e2 = ingest_kostentraeger_file(E2, "v21")
    assert verify_kostentraeger_ik(e2, "123456789").status == VerificationStatus.NOT_FOUND
    assert verify_kostentraeger_ik(e2, "987654321").status == VerificationStatus.FOUND
    assert "edition_e2_subset.edifact" in e2.provenance


def test_provenance_on_verify():
    store = ingest_kostentraeger_file(E1, "v21")
    result = verify_kostentraeger_ik(store, "123456789")
    assert "anhang3_kotr.edifact" in result.provenance


def test_formal_ok_but_unlisted_is_not_found():
    store = ingest_kostentraeger_file(E1, "v21")
    formal = "260326822"
    assert Ik.is_valid(formal)
    result = verify_kostentraeger_ik(store, formal)
    assert result.status == VerificationStatus.NOT_FOUND


def test_package_exports_agree():
    store = ingest_kostentraeger_file(E1, "v21")
    a = ta5py.verify_kostentraeger_ik(store, "123456789")
    b = verify_kostentraeger_ik(store, "123456789")
    assert a.status == b.status == VerificationStatus.FOUND
    assert ta5py.resolve_acceptance_ik(store, "123456789") == "111222333"
