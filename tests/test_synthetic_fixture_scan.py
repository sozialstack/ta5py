from __future__ import annotations

from pathlib import Path

from gkv_edi.synthetic_guard import scan_text, scan_tree

FIX = Path(__file__).parent / "fixtures"


def test_fixtures_pass_sozialdaten_scan():
    findings = scan_tree([FIX])
    assert findings == [], findings


def test_scanner_flags_non_allowlisted_kvnr(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('{"versicherten_id": "Z123456789"}', encoding="utf-8")
    findings = scan_text(p.read_text(encoding="utf-8"), p)
    assert findings


def test_scanner_allows_synthetic_series(tmp_path):
    p = tmp_path / "ok.json"
    p.write_text('{"versicherten_id": "A000000001"}', encoding="utf-8")
    assert scan_text(p.read_text(encoding="utf-8"), p) == []
