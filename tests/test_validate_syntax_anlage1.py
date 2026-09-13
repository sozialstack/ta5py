from __future__ import annotations

import json
from pathlib import Path

from ta5py.encode import encode, encode_slga_wire
from ta5py.validate_syntax import validate_data, validate_slga, validate_wire_segment_order

FIXTURE = Path(__file__).parent / "fixtures/synthetic/slla_e/happy_claim.json"
ORDER_BAD = Path(__file__).parent / "fixtures/synthetic/slla_e/wrong_order_claim.json"


def test_rejects_bad_length():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["cases"][0]["trips"][0]["ktl"]["strasse_abholort"] = "X" * 40
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any("maxLength" in e.message for e in result.errors)


def test_rejects_bad_value_type():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["rec"]["datum"] = "not-a-date"
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any("value_type N" in e.message for e in result.errors)


def test_rejects_missing_ktl():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["cases"][0]["trips"] = []
    result = validate_data(claim, "v21")
    assert not result.syntax_ok


def test_unsupported_scope():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["profile"] = "heilmittel"
    result = encode(claim, "v21")
    assert not result.syntax_ok
    assert result.errors[0].message == "unsupported_scope"


def test_service_segments_validated():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["unb"]["absender_ik"] = ""  # mandatory N field empty
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any(e.field.startswith("unb.") for e in result.errors)


def test_wrong_order_logical_fixture():
    claim = json.loads(ORDER_BAD.read_text(encoding="utf-8"))
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any("order" in e.field or "order" in e.message for e in result.errors)


def test_wrong_order_wire(tmp_path):
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = encode(claim, "v21", output_dir=tmp_path)
    assert result.syntax_ok, result.errors
    wire = Path(result.output_uri.removeprefix("file:")).read_text(encoding="utf-8")
    # Swap FKT and REC segments in the SLLA body
    bad = wire.replace("FKT+", "§FKT§", 1).replace("REC+", "FKT+", 1).replace("§FKT§", "REC+", 1)
    order = validate_wire_segment_order(bad, "v21")
    assert not order.syntax_ok
    assert any("order" in e.message for e in order.errors)


def test_slga_encode_validate():
    slga = {
        "fkt": {
            "verarbeitungskennzeichen": "01",
            "ik_rechnungssteller": "123456789",
            "ik_kostentraeger": "987654321",
            "ik_krankenkasse": "987654321",
            "ik_absender": "123456789",
        },
        "rec": {
            "sammel_rechnungsnummer": "R20260001",
            "einzel_rechnungsnummer": "0",
            "datum": "20260817",
            "rechnungsart": "1",
        },
        "nam": {"name": "Synthetic Ambulance GmbH"},
        "ges": [
            {"status": "1", "gesamt_brutto": "85,50"},
            {"status": "2", "gesamt_brutto": "0,00"},
        ],
    }
    assert validate_slga(slga, "v21").syntax_ok
    wire = encode_slga_wire(slga, "v21")
    assert "NAM+" in wire and wire.count("GES+") >= 2


def test_legacy_v20_still_works(tmp_path):
    result = encode(
        {
            "ik_sender": "123456789",
            "ik_receiver": "987654321",
            "leistungsdatum": "20260817",
            "km": 12,
            "positions": [{"code": "TAX1", "amount_cents": 2500}],
        },
        "v20",
        output_dir=tmp_path,
    )
    assert result.syntax_ok


def test_rejects_missing_inv_belegnummer():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["cases"][0]["inv"]["belegnummer"] = ""
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any("belegnummer" in e.field for e in result.errors)


def test_rejects_missing_nad_geburtsdatum():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["cases"][0]["nad"]["geburtsdatum"] = ""
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any("geburtsdatum" in e.field for e in result.errors)


def test_rejects_missing_zkt_bsnr_lanr_zuzahlung():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    zkt = claim["slla"][0]["cases"][0]["zkt"]
    zkt["betriebsstaettennummer"] = ""
    zkt["lanr"] = ""
    zkt["zuzahlungskennzeichen"] = ""
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    fields = {e.field for e in result.errors}
    assert any("betriebsstaettennummer" in f for f in fields)
    assert any("lanr" in f for f in fields)
    assert any("zuzahlungskennzeichen" in f for f in fields)


def test_rejects_non_ambulance_le_art_scope():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["cases"][0]["zkt"]["le_art"] = "11"
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any(e.message == "unsupported_scope" for e in result.errors)


def test_img_evo_structured_fields():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["cases"][0]["img"] = {
        "abrechnungsjahr": "2026",
        "abrechnungsmonat": "08",
        "identifikation_stelle": "123456789",
    }
    claim["slla"][0]["cases"][0]["evo"] = {"evo_id": "E" * 22}
    result = validate_data(claim, "v21")
    assert result.syntax_ok, result.errors
    claim["slla"][0]["cases"][0]["img"]["abrechnungsjahr"] = ""
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any("abrechnungsjahr" in e.field for e in result.errors)
