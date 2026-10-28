from __future__ import annotations

from pathlib import Path

import pytest

from ta5py.kostentraeger import ingest_kostentraeger_files, read_kotr_text
from ta5py.kostentraeger_fetch import download_kostentraeger_files, parse_kostentraeger_overview

OVERVIEW = Path(__file__).parent / "fixtures" / "kostentraeger" / "overview.html"
SYNTH = Path(__file__).parent / "fixtures" / "synthetic" / "kostentraeger" / "anhang3_kotr.edifact"


def test_parse_overview_lists_ke_files():
    files = parse_kostentraeger_overview(OVERVIEW.read_text(encoding="utf-8"))
    names = [item.filename for item in files]
    assert names == [
        "AO05Q326.ke3",
        "BK05Q326.ke1",
        "BN050526.ke0",
        "EK05Q226.ke0",
        "EK05Q426.ke0",
        "IK05Q326.ke1",
        "LK05Q226.ke0",
    ]
    aok = next(item for item in files if item.kassenart == "AO")
    assert aok.label == "AOK"
    assert aok.url.endswith("/AO05Q326.ke3")


def test_parse_overview_without_ke_links_fails():
    with pytest.raises(ValueError, match="no Kostenträger"):
        parse_kostentraeger_overview("<html><body>no files</body></html>")


def test_download_uses_injected_fetch(tmp_path: Path):
    files = parse_kostentraeger_overview(OVERVIEW.read_text(encoding="utf-8"))
    payload = SYNTH.read_bytes()

    def fetch(url: str) -> bytes:
        assert url.startswith("https://www.gkv-datenaustausch.de/")
        return payload

    written = download_kostentraeger_files(files[:1], tmp_path, fetch=fetch)
    assert written[0].is_file()
    assert b"UNB+" in written[0].read_bytes()


def test_download_rejects_non_edifact(tmp_path: Path):
    files = parse_kostentraeger_overview(OVERVIEW.read_text(encoding="utf-8"))

    def fetch(_url: str) -> bytes:
        return b"<html>not edifact</html>"

    with pytest.raises(ValueError, match="not an Anhang-3"):
        download_kostentraeger_files(files[:1], tmp_path, fetch=fetch)


def test_read_kotr_text_latin1(tmp_path: Path):
    path = tmp_path / "LK05Q226.ke0"
    path.write_bytes("UNB+UNOC:3+1+2+250101:0000+1++X'\nIDK+101308719+99+Weißenstein'\n".encode("latin-1"))
    text = read_kotr_text(path)
    assert "Weißenstein" in text


def test_ingest_files_later_source_wins(tmp_path: Path):
    first = tmp_path / "AO05Q226.ke0"
    second = tmp_path / "AO05Q426.ke0"
    payload = SYNTH.read_bytes()
    first.write_bytes(payload)
    second.write_bytes(payload)
    store = ingest_kostentraeger_files([first, second], "v21", store_path=tmp_path / "store.json")
    hit = store.lookup("123456789")
    assert hit is not None
    assert hit["source"] == "AO05Q426.ke0"
    assert (tmp_path / "store.json").is_file()
