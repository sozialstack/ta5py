from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from clearing_contracts.types import FieldError, FormatResult

from gkv_edi.models_slla_e import ensure_ambulance_profile, iter_slla_cases
from gkv_edi.spec_loader import has_anlage_package, load_dataset_schema, load_package
from gkv_edi.uri import read_json_uri
from gkv_edi.wire import split_fields, split_segments

def _type_ok(value: Any, expected: str) -> bool:
    return {
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
    }.get(expected, True)


def _validate_node(node: Any, schema: dict, path: str, errors: list[FieldError]) -> None:
    expected_type = schema.get("type")
    if expected_type and not _type_ok(node, expected_type):
        errors.append(FieldError(path or "$", f"expected type {expected_type}"))
        return

    if "pattern" in schema and isinstance(node, str):
        if not re.fullmatch(schema["pattern"], node):
            errors.append(FieldError(path or "$", "does not match required pattern"))

    if "minLength" in schema and isinstance(node, str) and len(node) < schema["minLength"]:
        errors.append(FieldError(path or "$", f"minLength {schema['minLength']}"))
    if "maxLength" in schema and isinstance(node, str) and len(node) > schema["maxLength"]:
        errors.append(FieldError(path or "$", f"maxLength {schema['maxLength']}"))

    if "minimum" in schema and isinstance(node, int) and node < schema["minimum"]:
        errors.append(FieldError(path or "$", f"minimum {schema['minimum']}"))
    if "maximum" in schema and isinstance(node, int) and node > schema["maximum"]:
        errors.append(FieldError(path or "$", f"maximum {schema['maximum']}"))

    if expected_type == "object" and isinstance(node, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in node:
                errors.append(FieldError(f"{path}.{key}" if path else key, "required field missing"))
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in node:
                if key not in props:
                    errors.append(FieldError(f"{path}.{key}" if path else key, "additional property not allowed"))
        for key, subschema in props.items():
            if key in node:
                _validate_node(node[key], subschema, f"{path}.{key}" if path else key, errors)

    if expected_type == "array" and isinstance(node, list):
        if "minItems" in schema and len(node) < schema["minItems"]:
            errors.append(FieldError(path or "$", f"minItems {schema['minItems']}"))
        item_schema = schema.get("items")
        if item_schema:
            for idx, item in enumerate(node):
                _validate_node(item, item_schema, f"{path}[{idx}]", errors)


def _max_len(spec: str | int) -> int:
    if isinstance(spec, int):
        return spec
    if "," in str(spec):
        whole, frac = str(spec).split(",", 1)
        whole = whole.lstrip(".")
        return int(whole) + 1 + int(frac)  # include decimal comma
    return int(str(spec).lstrip("."))


def _min_len(spec: str | int | None) -> int | None:
    if spec is None:
        return None
    if isinstance(spec, int):
        return spec
    s = str(spec)
    if "," in s:
        return None  # decimal forms: length checked via max only
    return int(s.lstrip("."))


_N_RE = re.compile(r"^[0-9]+(,[0-9]+)?$")


def _check_field(value: Any, field: dict, path: str, errors: list[FieldError], catalogs: dict) -> None:
    usage = field.get("usage", "K")
    if value is None or value == "":
        if usage == "M":
            errors.append(FieldError(path, "required field missing"))
        return
    s = str(value)
    max_length = field.get("max_length")
    if max_length is not None and len(s) > _max_len(max_length):
        errors.append(FieldError(path, f"maxLength {max_length}"))
    min_length = field.get("min_length")
    ml = _min_len(min_length if min_length is not None else None)
    if ml is not None and len(s) < ml:
        errors.append(FieldError(path, f"minLength {ml}"))

    value_type = field.get("value_type")
    if value_type == "N" and not _N_RE.fullmatch(s):
        errors.append(FieldError(path, "value_type N expected numeric"))

    catalog_ref = field.get("catalog_ref")
    if catalog_ref and catalog_ref in catalogs:
        allowed = {str(c.get("code") if isinstance(c, dict) else c) for c in catalogs[catalog_ref].get("codes", [])}
        if s not in allowed:
            errors.append(
                FieldError(path, f"code not in catalog {catalog_ref} v{catalogs[catalog_ref].get('version', '?')}")
            )


def _validate_segment_dict(data: dict, seg_def: dict, path: str, errors: list[FieldError], catalogs: dict) -> None:
    for field in seg_def.get("fields", []):
        name = field["name"]
        if name == "segment_tag":
            continue
        _check_field(data.get(name), field, f"{path}.{name}", errors, catalogs)


def _message_segment_codes(pkg: dict) -> list[str]:
    msg = pkg.get("messages", {}).get("slla_e") or {}
    return [row["segment"] for row in msg.get("segments", [])]


def _collect_logical_segment_order(msg: dict) -> list[str]:
    """Flatten logical SLLA message into expected segment tag sequence (body only)."""
    order: list[str] = []
    if msg.get("fkt"):
        order.append("FKT")
    if msg.get("rec"):
        order.append("REC")
    for case in msg.get("cases") or []:
        if case.get("inv"):
            order.append("INV")
        if case.get("nad"):
            order.append("NAD")
        if case.get("img"):
            order.append("IMG")
        if case.get("evo"):
            order.append("EVO")
        for trip in case.get("trips") or []:
            if trip.get("ktl"):
                order.append("KTL")
            for pos in trip.get("positions") or []:
                if pos.get("ekt"):
                    order.append("EKT")
                if pos.get("txt"):
                    order.append("TXT")
                if pos.get("mws"):
                    order.append("MWS")
            if trip.get("zuk"):
                order.append("ZUK")
        if case.get("zkt"):
            order.append("ZKT")
        if case.get("skz"):
            order.append("SKZ")
        if case.get("bes"):
            order.append("BES")
    return order


def _validate_order_against_message(order: list[str], allowed: list[str], path: str, errors: list[FieldError]) -> None:
    """Validate SLLA:E / SLGA segment order allowing documented case/trip repeats."""
    if not allowed or not order:
        return
    rank = {tag: i for i, tag in enumerate(allowed)}
    for tag in order:
        if tag not in rank:
            errors.append(FieldError(path, f"unexpected segment {tag} for message"))

    # Header segments must lead (FKT before REC before first INV/NAM/GES).
    header = [t for t in order if t in ("FKT", "REC")]
    if header != [t for t in ("FKT", "REC") if t in header]:
        errors.append(FieldError(path, "segment order violation near REC/FKT"))

    # Split into case groups starting at each INV (SLLA) or treat whole body (SLGA).
    if "INV" in order:
        groups: list[list[str]] = []
        cur: list[str] = []
        for tag in order:
            if tag in ("FKT", "REC"):
                continue
            if tag == "INV":
                if cur:
                    groups.append(cur)
                cur = [tag]
            else:
                if not cur:
                    errors.append(FieldError(path, f"segment order violation near {tag}"))
                    cur = [tag]
                else:
                    cur.append(tag)
        if cur:
            groups.append(cur)
        for g in groups:
            _validate_case_group_order(g, rank, path, errors)
    else:
        last = -1
        for tag in order:
            idx = rank.get(tag, -1)
            if idx < last and tag not in ("GES",):
                # GES may repeat; other SLGA tags must be non-decreasing
                if not (tag == "GES" and allowed[last] == "GES" if 0 <= last < len(allowed) else False):
                    if tag != "GES":
                        errors.append(FieldError(path, f"segment order violation near {tag}"))
            if tag == "GES":
                last = rank.get("GES", last)
            else:
                last = max(last, idx)


def _validate_case_group_order(
    group: list[str],
    rank: dict[str, int],
    path: str,
    errors: list[FieldError],
) -> None:
    """Intra-case order from messages/slla_e.yaml rank; KTL/EKT may restart trips/positions."""
    last = -1
    ktl_rank = rank.get("KTL")
    ekt_rank = rank.get("EKT")
    for tag in group:
        idx = rank.get(tag)
        if idx is None:
            errors.append(FieldError(path, f"unexpected segment {tag} for SLLA:E"))
            continue
        # Allow restarting a trip at KTL after ZUK/EKT/TXT/MWS; allow new EKT after TXT/MWS.
        if tag == "KTL" and ktl_rank is not None and last >= ktl_rank:
            last = ktl_rank
            continue
        if tag == "EKT" and ekt_rank is not None and last >= ekt_rank:
            last = ekt_rank
            continue
        if idx < last:
            errors.append(FieldError(path, f"segment order violation near {tag}"))
        last = idx


def _validate_service_segments(
    claim: dict[str, Any],
    segments: dict,
    catalogs: dict,
    errors: list[FieldError],
    *,
    require_envelope: bool,
) -> None:
    if require_envelope or claim.get("unb"):
        if not claim.get("unb"):
            errors.append(FieldError("unb", "required field missing"))
        else:
            _validate_segment_dict(claim["unb"], segments["UNB"], "unb", errors, catalogs)
    if require_envelope or claim.get("unz"):
        if not claim.get("unz"):
            errors.append(FieldError("unz", "required field missing"))
        else:
            _validate_segment_dict(claim["unz"], segments["UNZ"], "unz", errors, catalogs)

    slla_list = claim.get("slla") or []
    for mi, msg in enumerate(slla_list):
        base = f"slla[{mi}]"
        if require_envelope or msg.get("unh"):
            if not msg.get("unh"):
                errors.append(FieldError(f"{base}.unh", "required field missing"))
            else:
                _validate_segment_dict(msg["unh"], segments["UNH"], f"{base}.unh", errors, catalogs)
        if require_envelope or msg.get("unt"):
            if not msg.get("unt"):
                errors.append(FieldError(f"{base}.unt", "required field missing"))
            else:
                _validate_segment_dict(msg["unt"], segments["UNT"], f"{base}.unt", errors, catalogs)


def validate_slga(slga: dict[str, Any], spec_version: str, dataset_id: str = "slga") -> FormatResult:
    """Validate minimal ambulance SLGA envelope against messages/slga.yaml + segment defs."""
    pkg = load_package(spec_version)
    catalogs = pkg.get("catalogs") or {}
    segments = pkg["segments"]
    errors: list[FieldError] = []
    msg_def = pkg.get("messages", {}).get("slga") or {}
    required = {row["segment"] for row in msg_def.get("segments", []) if row.get("usage") == "M"}

    mapping = {
        "FKT": "fkt",
        "REC": "rec",
        "NAM": "nam",
        "GES": "ges",
    }
    for code, key in mapping.items():
        if code in required and not slga.get(key):
            errors.append(FieldError(key, "required field missing"))
        elif slga.get(key):
            if code == "GES" and isinstance(slga[key], list):
                for i, row in enumerate(slga[key]):
                    _validate_segment_dict(row, segments[code], f"ges[{i}]", errors, catalogs)
            else:
                data = slga[key]
                if code == "GES" and isinstance(data, dict):
                    _validate_segment_dict(data, segments[code], key, errors, catalogs)
                elif code != "GES":
                    _validate_segment_dict(data, segments[code], key, errors, catalogs)

    ges = slga.get("ges")
    if isinstance(ges, list) and len(ges) < 2:
        errors.append(FieldError("ges", "SLGA requires at least 2 GES segments"))

    order = []
    for code, key in (("FKT", "fkt"), ("REC", "rec"), ("NAM", "nam")):
        if slga.get(key):
            order.append(code)
    if isinstance(ges, list):
        order.extend(["GES"] * len(ges))
    elif ges:
        order.append("GES")
    allowed = [row["segment"] for row in msg_def.get("segments", [])]
    _validate_order_against_message(order, allowed, "slga", errors)

    return FormatResult(dataset_id=dataset_id, output_uri=None, syntax_ok=len(errors) == 0, errors=errors)


def validate_slla_e_claim(claim: dict[str, Any], spec_version: str, dataset_id: str = "dataset") -> FormatResult:
    scope_err = ensure_ambulance_profile(claim)
    if scope_err:
        return FormatResult(
            dataset_id=dataset_id,
            output_uri=None,
            syntax_ok=False,
            errors=[FieldError("profile", scope_err)],
        )

    pkg = load_package(spec_version)
    catalogs = pkg.get("catalogs") or {}
    segments = pkg["segments"]
    errors: list[FieldError] = []
    allowed = _message_segment_codes(pkg)

    # Full Nutzdatendatei shape when service envelope keys are present
    require_envelope = bool(claim.get("unb") or claim.get("unz"))
    _validate_service_segments(claim, segments, catalogs, errors, require_envelope=require_envelope)

    if claim.get("slga"):
        slga_result = validate_slga(claim["slga"], spec_version, dataset_id=f"{dataset_id}.slga")
        errors.extend(slga_result.errors)

    slla_list = claim.get("slla")
    if not slla_list:
        # allow single-message shape
        slla_list = [
            {
                "fkt": claim.get("fkt"),
                "rec": claim.get("rec"),
                "cases": iter_slla_cases(claim),
            }
        ]

    for mi, msg in enumerate(slla_list):
        base = f"slla[{mi}]"
        if not msg.get("fkt"):
            errors.append(FieldError(f"{base}.fkt", "required field missing"))
        else:
            _validate_segment_dict(msg["fkt"], segments["FKT"], f"{base}.fkt", errors, catalogs)
        if not msg.get("rec"):
            errors.append(FieldError(f"{base}.rec", "required field missing"))
        else:
            _validate_segment_dict(msg["rec"], segments["REC"], f"{base}.rec", errors, catalogs)

        cases = msg.get("cases") or []
        if not cases:
            errors.append(FieldError(f"{base}.cases", "required field missing"))
        for ci, case in enumerate(cases):
            cpath = f"{base}.cases[{ci}]"
            for req, code in (("inv", "INV"), ("nad", "NAD"), ("zkt", "ZKT"), ("bes", "BES")):
                if not case.get(req):
                    errors.append(FieldError(f"{cpath}.{req}", "required field missing"))
                else:
                    _validate_segment_dict(case[req], segments[code], f"{cpath}.{req}", errors, catalogs)
            for opt, code in (("img", "IMG"), ("evo", "EVO"), ("skz", "SKZ")):
                if case.get(opt):
                    _validate_segment_dict(case[opt], segments[code], f"{cpath}.{opt}", errors, catalogs)
            trips = case.get("trips") or []
            if not trips:
                errors.append(FieldError(f"{cpath}.trips", "required field missing"))
            for ti, trip in enumerate(trips):
                tpath = f"{cpath}.trips[{ti}]"
                if not trip.get("ktl"):
                    errors.append(FieldError(f"{tpath}.ktl", "required field missing"))
                else:
                    _validate_segment_dict(trip["ktl"], segments["KTL"], f"{tpath}.ktl", errors, catalogs)
                positions = trip.get("positions") or []
                if not positions:
                    errors.append(FieldError(f"{tpath}.positions", "required field missing"))
                for pi, pos in enumerate(positions):
                    ppath = f"{tpath}.positions[{pi}]"
                    if not pos.get("ekt"):
                        errors.append(FieldError(f"{ppath}.ekt", "required field missing"))
                    else:
                        _validate_segment_dict(pos["ekt"], segments["EKT"], f"{ppath}.ekt", errors, catalogs)
                    if pos.get("txt"):
                        _validate_segment_dict(pos["txt"], segments["TXT"], f"{ppath}.txt", errors, catalogs)
                    if pos.get("mws"):
                        _validate_segment_dict(pos["mws"], segments["MWS"], f"{ppath}.mws", errors, catalogs)
                if trip.get("zuk"):
                    _validate_segment_dict(trip["zuk"], segments["ZUK"], f"{tpath}.zuk", errors, catalogs)

        order = _collect_logical_segment_order(msg)
        if msg.get("segment_order_override"):
            order = list(msg["segment_order_override"])
        _validate_order_against_message(order, allowed, f"{base}.order", errors)

    return FormatResult(dataset_id=dataset_id, output_uri=None, syntax_ok=len(errors) == 0, errors=errors)


def validate_wire_segment_order(wire: str, spec_version: str, dataset_id: str = "wire") -> FormatResult:
    """Validate SLLA:E body segment order on raw Nutzdaten wire text."""
    pkg = load_package(spec_version)
    una = pkg["una"]
    allowed = _message_segment_codes(pkg)
    body_tags = {"FKT", "REC", "INV", "NAD", "IMG", "EVO", "KTL", "EKT", "TXT", "MWS", "ZUK", "ZKT", "SKZ", "BES"}
    service = {"UNA", "UNB", "UNH", "UNT", "UNZ", "NAM", "GES"}
    order: list[str] = []
    errors: list[FieldError] = []
    for raw in split_segments(wire, una):
        fields = split_fields(raw, una)
        if not fields:
            continue
        tag = fields[0]
        if tag in body_tags:
            order.append(tag)
        elif tag in service or tag.startswith("UNA"):
            continue
        else:
            errors.append(FieldError("wire", f"unexpected segment {tag}"))
    _validate_order_against_message(order, allowed, "wire.order", errors)
    return FormatResult(dataset_id=dataset_id, output_uri=None, syntax_ok=len(errors) == 0, errors=errors)


def validate_data(data: dict[str, Any], spec_version: str, dataset_id: str = "dataset") -> FormatResult:
    if has_anlage_package(spec_version):
        return validate_slla_e_claim(data, spec_version, dataset_id=dataset_id)
    schema = load_dataset_schema(spec_version)
    errors: list[FieldError] = []
    _validate_node(data, schema, "", errors)
    return FormatResult(
        dataset_id=dataset_id,
        output_uri=None,
        syntax_ok=len(errors) == 0,
        errors=errors,
    )


def validate_syntax(dataset_uri: str, spec_version: str) -> FormatResult:
    path = dataset_uri.removeprefix("file:")
    if dataset_uri.startswith("wire:"):
        claim = _wire_to_minimal_claim(dataset_uri.removeprefix("wire:"), spec_version)
        result = validate_data(claim, spec_version, dataset_id="wire")
        order = validate_wire_segment_order(dataset_uri.removeprefix("wire:"), spec_version)
        if not order.syntax_ok:
            return FormatResult(
                dataset_id="wire",
                output_uri=None,
                syntax_ok=False,
                errors=result.errors + order.errors,
            )
        return result
    if path.endswith(".nutzdaten"):
        raw = Path(path).read_text(encoding="utf-8")
        claim = _wire_to_minimal_claim(raw, spec_version)
        result = validate_data(claim, spec_version, dataset_id=Path(path).stem)
        order = validate_wire_segment_order(raw, spec_version, dataset_id=Path(path).stem)
        if not order.syntax_ok:
            return FormatResult(
                dataset_id=Path(path).stem,
                output_uri=None,
                syntax_ok=False,
                errors=result.errors + order.errors,
            )
        return result
    data = read_json_uri(dataset_uri)
    dataset_id = Path(dataset_uri).stem
    return validate_data(data, spec_version, dataset_id=dataset_id)


def _wire_to_minimal_claim(wire: str, spec_version: str) -> dict[str, Any]:
    """Best-effort parse for syntax checks on wire files."""
    from gkv_edi.decode import decode_wire

    return decode_wire(wire, spec_version)
