from __future__ import annotations

from pathlib import Path

from ta5py.kostentraeger import ingest_kostentraeger_file

FIXTURE = Path(__file__).parent / "fixtures/synthetic/kostentraeger/anhang3_kotr.edifact"
LEGACY_ALIAS = Path(__file__).parent / "fixtures/synthetic/kostentraeger/sample_kt.txt"


def test_ingest_anhang3_edifact_and_lookup(tmp_path):
    store_path = tmp_path / "kt-store.json"
    store = ingest_kostentraeger_file(FIXTURE, "v21", store_path=store_path)
    assert len(store) >= 20
    hit = store.lookup("123456789")
    assert hit is not None
    assert hit["acceptance_ik"] == "111222333"
    assert "Synthetic Ambulance" in hit["name"]
    assert store.lookup("000000000") is None
    assert store.lookup("900000001") is None
    assert store.lookup("900000002") is None
    assert store.lookup("900000003") is None
    assert store_path.is_file()


def test_sample_alias_is_edifact():
    text = LEGACY_ALIAS.read_text(encoding="ascii")
    assert "UNB+" in text and "IDK+" in text and "KOTR:" in text


def test_bad_structure_does_not_clobber(tmp_path):
    store_path = tmp_path / "kt-store.json"
    ingest_kostentraeger_file(FIXTURE, "v21", store_path=store_path)
    before = store_path.read_text(encoding="utf-8")
    bad = tmp_path / "bad.txt"
    bad.write_text("short\n", encoding="ascii")
    try:
        ingest_kostentraeger_file(bad, "v21", store_path=store_path)
        assert False, "expected ValueError"
    except ValueError:
        pass
    assert store_path.read_text(encoding="utf-8") == before
