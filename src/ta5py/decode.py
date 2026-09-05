from __future__ import annotations

from pathlib import Path
from typing import Any

from ta5py.spec_loader import has_anlage_package, load_package, resolve_spec_version
from ta5py.uri import read_json_uri
from ta5py.wire import split_fields, split_segments


def _map_segment(seg_def: dict, fields: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    # fields[0] is tag
    values = fields[1:]
    idx = 0
    for field in seg_def.get("fields", []):
        name = field["name"]
        if name == "segment_tag":
            continue
        data[name] = values[idx] if idx < len(values) else ""
        idx += 1
    return data


def decode_wire(wire: str, spec_version: str | None = None) -> dict[str, Any]:
    spec_version = resolve_spec_version(spec_version)
    pkg = load_package(spec_version)
    una = pkg["una"]
    segments = pkg["segments"]
    claim: dict[str, Any] = {"profile": "krankentransport", "slla": []}
    current_msg: dict[str, Any] | None = None
    current_case: dict[str, Any] | None = None
    current_trip: dict[str, Any] | None = None
    current_pos: dict[str, Any] | None = None

    for raw in split_segments(wire, una):
        fields = split_fields(raw, una)
        if not fields:
            continue
        tag = fields[0]
        if tag not in segments:
            continue
        mapped = _map_segment(segments[tag], fields)
        if tag == "UNB":
            claim["unb"] = mapped
        elif tag == "UNZ":
            claim["unz"] = mapped
        elif tag == "UNH":
            current_msg = {"unh": mapped, "cases": []}
            claim["slla"].append(current_msg)
            current_case = None
            current_trip = None
            current_pos = None
        elif tag == "FKT":
            if current_msg is None:
                current_msg = {"cases": []}
                claim["slla"].append(current_msg)
            current_msg["fkt"] = mapped
        elif tag == "REC":
            if current_msg is None:
                current_msg = {"cases": []}
                claim["slla"].append(current_msg)
            current_msg["rec"] = mapped
        elif tag == "INV":
            current_case = {"inv": mapped, "trips": []}
            assert current_msg is not None
            current_msg["cases"].append(current_case)
            current_trip = None
            current_pos = None
        elif tag == "NAD" and current_case is not None:
            current_case["nad"] = mapped
        elif tag == "IMG" and current_case is not None:
            current_case["img"] = mapped
        elif tag == "EVO" and current_case is not None:
            current_case["evo"] = mapped
        elif tag == "KTL" and current_case is not None:
            current_trip = {"ktl": mapped, "positions": []}
            current_case["trips"].append(current_trip)
            current_pos = None
        elif tag == "EKT" and current_trip is not None:
            current_pos = {"ekt": mapped}
            current_trip["positions"].append(current_pos)
        elif tag == "TXT" and current_pos is not None:
            current_pos["txt"] = mapped
        elif tag == "MWS" and current_pos is not None:
            current_pos["mws"] = mapped
        elif tag == "ZUK" and current_trip is not None:
            current_trip["zuk"] = mapped
        elif tag == "ZKT" and current_case is not None:
            current_case["zkt"] = mapped
        elif tag == "SKZ" and current_case is not None:
            current_case["skz"] = mapped
        elif tag == "BES" and current_case is not None:
            current_case["bes"] = mapped
        elif tag == "UNT" and current_msg is not None:
            current_msg["unt"] = mapped

    return claim


def decode(dataset_uri: str, spec_version: str | None = None) -> dict[str, Any]:
    spec_version = resolve_spec_version(spec_version)
    path = dataset_uri.removeprefix("file:")
    if has_anlage_package(spec_version) and (
        path.endswith(".nutzdaten") or dataset_uri.startswith("wire:")
    ):
        if dataset_uri.startswith("wire:"):
            return decode_wire(dataset_uri.removeprefix("wire:"), spec_version)
        return decode_wire(Path(path).read_text(encoding="utf-8"), spec_version)
    if has_anlage_package(spec_version) and path.endswith(".json"):
        # debug JSON sidecar
        return read_json_uri(dataset_uri)
    return read_json_uri(dataset_uri)
