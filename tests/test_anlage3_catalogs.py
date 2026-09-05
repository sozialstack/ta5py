from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ta5py.validate_syntax import validate_data

FIXTURE = Path(__file__).parent / "fixtures/synthetic/slla_e/happy_claim.json"

# catalog_ref → (path into claim dict as tuple of keys, invalid code)
_INVALID_BY_CATALOG = {
    "versichertenstatus": (("slla", 0, "cases", 0, "inv", "versichertenstatus"), "99999"),
    "rechnungsart": (("slla", 0, "rec", "rechnungsart"), "9"),
    "verarbeitungskennzeichen": (("slla", 0, "fkt", "verarbeitungskennzeichen"), "99"),
    "abrechnungscode": (("slla", 0, "cases", 0, "trips", 0, "positions", 0, "ekt", "abrechnungscode"), "XX"),
    "tarifkennzeichen": (("slla", 0, "cases", 0, "trips", 0, "positions", 0, "ekt", "tarifkennzeichen"), "BAD99"),
    "unfall_sonstiges": (("slla", 0, "cases", 0, "zkt", "unfallkennzeichen"), "9"),
    "zuzahlungsart": (("slla", 0, "cases", 0, "trips", 0, "zuk", "zuzahlungsart"), "99"),
    "laenderkennzeichen": (("slla", 0, "cases", 0, "trips", 0, "ktl", "laenderkennzeichen_abholort"), "XX"),
}


def _set_path(obj, path, value):
    cur = obj
    for key in path[:-1]:
        cur = cur[key]
    cur[path[-1]] = value


@pytest.mark.parametrize("catalog_id,path_and_code", list(_INVALID_BY_CATALOG.items()))
def test_rejects_invalid_code_per_catalog(catalog_id, path_and_code):
    path, bad = path_and_code
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if catalog_id == "zuzahlungsart":
        claim["slla"][0]["cases"][0]["trips"][0]["zuk"] = {
            "identifikationsnummer": "1",
            "bruttobetrag": "10,00",
            "zuzahlungsart": "01",
        }
    _set_path(claim, path, bad)
    result = validate_data(claim, "v21")
    assert not result.syntax_ok, f"expected rejection for {catalog_id}"
    assert any(catalog_id in e.message for e in result.errors), result.errors


def test_catalog_accepts_known_le_art():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = validate_data(claim, "v21")
    assert result.syntax_ok, result.errors


def test_catalog_rejects_unknown_code():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["cases"][0]["zkt"]["le_art"] = "99"
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any("catalog le_art_krankentransport" in e.message for e in result.errors)


def test_catalog_rejects_bad_positionsnummer():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    claim["slla"][0]["cases"][0]["trips"][0]["positions"][0]["ekt"]["positionsnummer"] = "999999"
    result = validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any("positionsnummer_kt" in e.message for e in result.errors)
