from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

from gkv_edi.spec_loader import resolve_spec_version, version_dir
from gkv_edi.wire import split_fields, split_segments


class KostentraegerStore:
    def __init__(self, entries: dict[str, dict[str, str]]):
        self._entries = entries

    def lookup(self, ik: str) -> dict[str, str] | None:
        return self._entries.get(ik)

    def __len__(self) -> int:
        return len(self._entries)


def _default_una(schema: dict[str, Any]) -> dict[str, str]:
    una = schema.get("una") or {}
    return {
        "component": una.get("component", ":"),
        "element": una.get("element", "+"),
        "decimal": una.get("decimal", ","),
        "release": una.get("release", "?"),
        "segment_end": una.get("segment_end", "'"),
    }


def _pick_acceptance(
    vkgs: list[dict[str, str]],
    schema: dict[str, Any],
) -> tuple[str, str]:
    link_types = set(schema.get("acceptance_link_types") or ["02", "03"])
    amb_codes = set(schema.get("ambulance_abrechnungscodes") or [])
    preferred: list[dict[str, str]] = []
    fallback: list[dict[str, str]] = []
    for v in vkgs:
        if v.get("art_verknuepfung") not in link_types:
            continue
        code = v.get("abrechnungscode") or ""
        if not code or code in amb_codes:
            preferred.append(v)
        else:
            fallback.append(v)
    chosen = (preferred or fallback or [None])[0]
    if not chosen:
        return "", ""
    return chosen.get("partner_ik", ""), chosen.get("abrechnungscode", "")


def _parse_kotr_edifact(text: str, schema: dict[str, Any]) -> dict[str, dict[str, str]]:
    una = _default_una(schema)
    if "UNB+" not in text and "IDK+" not in text:
        raise ValueError("Kostentraeger file is not Anhang-3 EDIFACT (missing UNB+/IDK+)")

    entries: dict[str, dict[str, str]] = {}
    current: dict[str, Any] | None = None
    vkgs: list[dict[str, str]] = []
    dfu_channel = ""

    def flush() -> None:
        nonlocal current, vkgs, dfu_channel
        if current is None:
            return
        ik = current.get("ik", "")
        if not ik or len(ik) != 9 or not ik.isdigit():
            raise ValueError(f"invalid IK in KOTR message: {ik!r}")
        if ik in entries:
            raise ValueError(f"duplicate IK {ik}")
        acceptance_ik, abr_code = _pick_acceptance(vkgs, schema)
        entries[ik] = {
            "ik": ik,
            "name": current.get("name", ""),
            "acceptance_ik": acceptance_ik,
            "dfue_hint": dfu_channel,
            "abrechnungscode": abr_code,
        }
        current = None
        vkgs = []
        dfu_channel = ""

    for raw in split_segments(text.replace("\r\n", "").replace("\n", ""), una):
        fields = split_fields(raw, una)
        if not fields:
            continue
        tag = fields[0]
        vals = fields[1:]
        if tag == "UNH":
            flush()
            current = {}
            vkgs = []
            dfu_channel = ""
        elif tag == "IDK":
            if current is None:
                current = {}
            current["ik"] = vals[0] if vals else ""
            if len(vals) > 2:
                current["name"] = vals[2]
        elif tag == "NAM":
            if current is None:
                raise ValueError("NAM without UNH/IDK")
            # NAM+01+Name...
            name = vals[1] if len(vals) > 1 else (vals[0] if vals else "")
            current["name"] = name or current.get("name", "")
        elif tag == "VKG":
            row = {
                "art_verknuepfung": vals[0] if len(vals) > 0 else "",
                "partner_ik": vals[1] if len(vals) > 1 else "",
                "le_gruppe": vals[2] if len(vals) > 2 else "",
                "abrechnungsstelle_ik": vals[3] if len(vals) > 3 else "",
                "art_datenlieferung": vals[4] if len(vals) > 4 else "",
                "uebermittlungsmedium": vals[5] if len(vals) > 5 else "",
                "bundesland": vals[6] if len(vals) > 6 else "",
                "kv_bezirk": vals[7] if len(vals) > 7 else "",
                "abrechnungscode": vals[8] if len(vals) > 8 else "",
                "tarifkennzeichen": vals[9] if len(vals) > 9 else "",
                "unterverfahren": vals[10] if len(vals) > 10 else "",
            }
            vkgs.append(row)
        elif tag == "DFU":
            if vals:
                if len(vals) >= 7:
                    dfu_channel = vals[6]
                else:
                    dfu_channel = next((v for v in reversed(vals) if v), "")
        elif tag == "UNT":
            flush()
        elif tag in ("UNB", "UNZ", "UNA", "VDT", "FKT", "ANS", "ASP", "UEM", "KTO"):
            continue
        else:
            # Unknown segment — structural tolerance for optional future keys
            continue

    flush()
    if not entries:
        raise ValueError("Kostentraeger file contained no KOTR/IDK entries")
    return entries


def ingest_kostentraeger_file(
    path: str | Path,
    spec_version: str | None = None,
    store_path: str | Path | None = None,
) -> KostentraegerStore:
    """Ingest an Anhang-3 EDIFACT Kostenträger file; atomically replace store_path if provided."""
    spec_version = resolve_spec_version(spec_version)
    root = version_dir(spec_version)
    schema = yaml.safe_load((root / "kostentraeger" / "anhang3.yaml").read_text(encoding="utf-8"))
    text = Path(path).read_text(encoding=schema.get("encoding", "utf-8"))
    if not text.strip():
        raise ValueError("Kostentraeger file is empty")

    entries = _parse_kotr_edifact(text, schema)
    store = KostentraegerStore(entries)
    if store_path is not None:
        dest = Path(store_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix="kt-", suffix=".json", dir=str(dest.parent))
        os.close(fd)
        tmp_path = Path(tmp)
        try:
            tmp_path.write_text(json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8")
            os.replace(tmp_path, dest)
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
    return store


def load_store(store_path: str | Path) -> KostentraegerStore:
    data = json.loads(Path(store_path).read_text(encoding="utf-8"))
    return KostentraegerStore(data)
