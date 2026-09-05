from __future__ import annotations

from pathlib import Path

from gkv_edi.spec_loader import load_package


def test_provenance_required_keys():
    for ver in ("v21", "v22"):
        pkg = load_package(ver)
        prov = pkg["provenance"]
        assert prov["scope"] == "krankentransport"
        assert prov.get("publications")
        ids = {p["anlage_id"] for p in prov["publications"]}
        assert {"anlage-1", "anlage-3", "anlage-5", "anhang-3"} <= ids
        for pub in prov["publications"]:
            assert pub.get("anlage_id")
            assert pub.get("version")
            assert pub.get("stand_date")
            assert pub.get("local_pdf")
            pdf = Path(__file__).resolve().parents[1] / "spec" / pub["local_pdf"]
            assert pdf.is_file(), f"missing PDF {pdf} — run download_official_pdfs.py"


def test_replaced_stand_retained_on_v22():
    v21 = {p["anlage_id"]: p for p in load_package("v21")["provenance"]["publications"]}
    v22 = {p["anlage_id"]: p for p in load_package("v22")["provenance"]["publications"]}
    assert v22["anlage-1"]["replaced_stand"] == v21["anlage-1"]["stand_date"]
    assert v22["anlage-3"]["replaced_stand"] == v21["anlage-3"]["stand_date"]
    assert "replaced_stand" not in v21["anlage-1"]
