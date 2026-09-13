from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ta5py.validate_syntax import validate_data

FIXTURE = Path(__file__).parent / "fixtures/synthetic/slla_e/happy_claim.json"

_INVALID_BY_CATALOG = {
    "versichertenstatus": (("slla", 0, "cases", 0, "inv", "versichertenstatus"), "99999"),
    "rechnungsart": (("slla", 0, "rec", "rechnungsart"), "9"),
    "verarbeitungskennzeichen": (("slla", 0, "fkt", "verarbeitungskennzeichen"), "99"),
    "abrechnungscode": (("slla", 0, "cases", 0, "trips", 0, "positions", 0, "ekt", "abrechnungscode"), "XX"),
    "tarifkennzeichen": (("slla", 0, "cases", 0, "trips", 0, "positions", 0, "ekt", "tarifkennzeichen"), "BAD99"),
    "unfall_sonstiges": (("slla", 0, "cases", 0, "zkt", "unfallkennzeichen"), "9"),
    "zuzahlungsart": (("slla", 0, "cases", 0, "trips", 0, "zuk", "zuzahlungsart"), "99"),
    "laenderkennzeichen": (("slla", 0, "cases", 0, "trips", 0, "ktl", "laenderkennzeichen_abholort"), "XX"),
    "beleginformation": (("slla", 0, "cases", 0, "inv", "beleginformation"), "9"),
    "zuzahlungskennzeichen": (("slla", 0, "cases", 0, "zkt", "zuzahlungskennzeichen"), "9"),
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


def test_catalog_accepts_known_abrechnungscode():
    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = validate_data(claim, "v21")
    assert result.syntax_ok, result.errors


def test_missing_catalog_fail_closed(monkeypatch):
    import importlib

    claim = json.loads(FIXTURE.read_text(encoding="utf-8"))
    from ta5py.spec_loader import load_package as real_load

    vs = importlib.import_module("ta5py.validate_syntax")

    def fake_load(spec_version):
        pkg = copy.deepcopy(real_load(spec_version))
        pkg["catalogs"].pop("versichertenstatus", None)
        return pkg

    monkeypatch.setattr(vs, "load_package", fake_load)
    result = vs.validate_data(claim, "v21")
    assert not result.syntax_ok
    assert any("versichertenstatus" in e.message and "missing" in e.message for e in result.errors)
