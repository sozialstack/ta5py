from __future__ import annotations

import json
from pathlib import Path

from ta5py import encode, decode, validate_syntax
from ta5py.spec_loader import load_package

FIXTURE = Path(__file__).parent / "fixtures/synthetic/slla_e/happy_claim.json"


def test_load_v21_package():
    pkg = load_package("v21")
    assert pkg["provenance"]["scope"] == "krankentransport"
    assert "slla_e" in pkg["messages"]
    assert "KTL" in pkg["segments"]


def test_slla_e_roundtrip(tmp_path):
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = encode(claim, "v21", output_dir=tmp_path)
    assert result.syntax_ok, result.errors
    assert result.output_uri and result.output_uri.endswith(".nutzdaten")
    wire = Path(result.output_uri.removeprefix("file:")).read_text(encoding="utf-8")
    assert "KTL+" in wire
    assert "EKT+" in wire
    assert wire.endswith("'") or "'" in wire
    decoded = decode(result.output_uri, "v21")
    assert decoded["profile"] == "krankentransport"
    assert decoded["slla"][0]["fkt"]["ik_rechnungssteller"] == "123456789"
    assert decoded["slla"][0]["cases"][0]["trips"][0]["ktl"]["strasse_abholort"] == "Hauptstrasse 1"
    assert decoded["slla"][0]["cases"][0]["trips"][0]["positions"][0]["ekt"]["positionsnummer"] == "110100"
    syntax = validate_syntax(result.output_uri, "v21")
    assert syntax.syntax_ok, syntax.errors


def test_escape_roundtrip_in_txt(tmp_path):
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["cases"][0]["trips"][0]["positions"][0]["txt"]["text"] = "A+B?C'D"
    result = encode(claim, "v21", output_dir=tmp_path)
    assert result.syntax_ok, result.errors
    decoded = decode(result.output_uri, "v21")
    assert decoded["slla"][0]["cases"][0]["trips"][0]["positions"][0]["txt"]["text"] == "A+B?C'D"
