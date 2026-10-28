from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from ta5py.models_slla_e import ensure_ambulance_profile
from ta5py.result import FieldError, FormatResult
from ta5py.spec_loader import has_anlage_package, load_package, resolve_spec_version
from ta5py.validate_syntax import validate_data
from ta5py.wire import join_segment


def _seg_fields(seg_def: dict, data: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for field in seg_def.get("fields", []):
        name = field["name"]
        if name == "segment_tag":
            continue
        val = data.get(name)
        values.append("" if val is None else str(val))
    return values


def _emit(seg_code: str, data: dict[str, Any], pkg: dict, parts: list[str]) -> None:
    seg_def = pkg["segments"][seg_code]
    parts.append(join_segment(seg_code, _seg_fields(seg_def, data), pkg["una"]))


def encode_slga_wire(slga: dict[str, Any], spec_version: str | None = None) -> str:
    """Encode minimal ambulance SLGA envelope (FKT/REC/NAM/GES×n)."""
    spec_version = resolve_spec_version(spec_version)
    pkg = load_package(spec_version)
    parts: list[str] = []
    _emit("FKT", slga["fkt"], pkg, parts)
    _emit("REC", slga["rec"], pkg, parts)
    _emit("NAM", slga["nam"], pkg, parts)
    ges = slga.get("ges") or []
    if isinstance(ges, dict):
        ges = [ges]
    for row in ges:
        _emit("GES", row, pkg, parts)
    return "".join(parts)


def encode_wire(claim: dict[str, Any], spec_version: str | None = None) -> str:
    spec_version = resolve_spec_version(spec_version)
    pkg = load_package(spec_version)
    parts: list[str] = []
    if claim.get("unb"):
        _emit("UNB", claim["unb"], pkg, parts)

    if claim.get("slga"):
        # SLGA message(s) precede SLLA in a Nutzdatendatei envelope
        slga = claim["slga"]
        if claim.get("slga_unh"):
            _emit("UNH", claim["slga_unh"], pkg, parts)
        parts.append(encode_slga_wire(slga, spec_version))
        if claim.get("slga_unt"):
            _emit("UNT", claim["slga_unt"], pkg, parts)

    slla_list = claim.get("slla")
    if not slla_list:
        if claim.get("fkt"):
            slla_list = [
                {
                    "fkt": claim["fkt"],
                    "rec": claim["rec"],
                    "cases": claim.get("cases") or [],
                    "unh": claim.get("unh"),
                    "unt": claim.get("unt"),
                }
            ]
        else:
            slla_list = []

    for msg in slla_list:
        if msg.get("unh"):
            _emit("UNH", msg["unh"], pkg, parts)
        _emit("FKT", msg["fkt"], pkg, parts)
        _emit("REC", msg["rec"], pkg, parts)
        for case in msg.get("cases") or []:
            _emit("INV", case["inv"], pkg, parts)
            _emit("NAD", case["nad"], pkg, parts)
            if case.get("img"):
                _emit("IMG", case["img"], pkg, parts)
            if case.get("evo"):
                _emit("EVO", case["evo"], pkg, parts)
            for trip in case.get("trips") or []:
                _emit("KTL", trip["ktl"], pkg, parts)
                for pos in trip.get("positions") or []:
                    _emit("EKT", pos["ekt"], pkg, parts)
                    if pos.get("txt"):
                        _emit("TXT", pos["txt"], pkg, parts)
                    if pos.get("mws"):
                        _emit("MWS", pos["mws"], pkg, parts)
                if trip.get("zuk"):
                    _emit("ZUK", trip["zuk"], pkg, parts)
            _emit("ZKT", case["zkt"], pkg, parts)
            if case.get("skz"):
                _emit("SKZ", case["skz"], pkg, parts)
            _emit("BES", case["bes"], pkg, parts)
        if msg.get("unt"):
            _emit("UNT", msg["unt"], pkg, parts)

    if claim.get("unz"):
        _emit("UNZ", claim["unz"], pkg, parts)
    return "".join(parts)


def encode(
    inputs: dict[str, Any],
    spec_version: str | None = None,
    output_dir: str | Path | None = None,
) -> FormatResult:
    spec_version = resolve_spec_version(spec_version)
    dataset_id = str(inputs.get("dataset_id") or uuid4())
    payload = {k: v for k, v in inputs.items() if k != "dataset_id"}

    if has_anlage_package(spec_version):
        scope_err = ensure_ambulance_profile(payload)
        if scope_err:
            return FormatResult(
                dataset_id=dataset_id,
                output_uri=None,
                syntax_ok=False,
                errors=[FieldError("profile", scope_err)],
            )
        result = validate_data(payload, spec_version, dataset_id=dataset_id)
        if not result.syntax_ok:
            return result
        wire = encode_wire(payload, spec_version)
        out_dir = Path(output_dir or Path.cwd() / ".clearing" / "datasets")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{dataset_id}.nutzdaten"
        out_path.write_text(wire, encoding="utf-8")
        # optional debug JSON
        (out_dir / f"{dataset_id}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )
        return FormatResult(
            dataset_id=dataset_id,
            output_uri=f"file:{out_path.as_posix()}",
            syntax_ok=True,
            errors=[],
        )

    result = validate_data(payload, spec_version, dataset_id=dataset_id)
    if not result.syntax_ok:
        return result
    out_dir = Path(output_dir or Path.cwd() / ".clearing" / "datasets")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dataset_id}.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return FormatResult(
        dataset_id=dataset_id,
        output_uri=f"file:{out_path.as_posix()}",
        syntax_ok=True,
        errors=[],
    )
