"""Kostenträgerdatei ingest and § 302 registry verification.

The GKV-Spitzenverband SLE Kostenträgerdatei (EDIFACT KOTR via
gkv-datenaustausch.de) is the authoritative source for card/Kostenträger IK
existence and acceptance/billing recipient resolution. Verification reads a
locally loaded store only — refresh/download is a separate operator step.

This module does **not** run formal Prüfziffer checks (see ``ta5py.ik``) and a
registry hit is **not** a project Testat or payer Community-Testat.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml

from ta5py.spec_loader import resolve_spec_version, version_dir
from ta5py.wire import split_fields, split_segments


class VerificationStatus(StrEnum):
    """Outcome of Kostenträgerdatei registry verification."""

    FOUND = "found"
    NOT_FOUND = "not_found"
    REGISTRY_UNAVAILABLE = "registry_unavailable"


@dataclass(frozen=True, slots=True)
class KostentraegerVerificationResult:
    """Result of verifying a card/Kostenträger IK against a loaded store."""

    status: VerificationStatus
    card_ik: str | None = None
    recipient_ik: str = ""
    recipient_determined: bool = False
    name: str = ""
    abrechnungscode: str = ""
    dfue_hint: str = ""
    dfue_protocol: str = ""
    source: str = ""
    provenance: tuple[str, ...] = ()


class KostentraegerStore:
    def __init__(
        self,
        entries: dict[str, dict[str, str]],
        provenance: list[str] | tuple[str, ...] | None = None,
    ):
        self._entries = entries
        self._provenance = tuple(provenance or ())

    @property
    def provenance(self) -> tuple[str, ...]:
        """Filenames (or other edition markers) used when this store was built."""
        return self._provenance

    def lookup(self, ik: str) -> dict[str, str] | None:
        return self._entries.get(ik)

    def as_dict(self) -> dict[str, dict[str, str]]:
        return dict(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def verify(self, ik: str) -> KostentraegerVerificationResult:
        """Verify a card IK against this store (existence + § 302 recipient)."""
        return verify_kostentraeger_ik(self, ik)


def verify_kostentraeger_ik(
    store: KostentraegerStore | None,
    ik: str,
) -> KostentraegerVerificationResult:
    """Registry-verify a card/Kostenträger IK for § 302 addressing.

    Does not call the network and does not perform formal Prüfziffer validation.
    ``store is None`` yields ``registry_unavailable`` (never a positive hit).
    """
    if store is None:
        return KostentraegerVerificationResult(status=VerificationStatus.REGISTRY_UNAVAILABLE)

    cleaned = ik.strip()
    provenance = store.provenance
    if len(cleaned) != 9 or not cleaned.isdigit():
        return KostentraegerVerificationResult(
            status=VerificationStatus.NOT_FOUND,
            card_ik=cleaned or None,
            provenance=provenance,
        )

    entry = store.lookup(cleaned)
    if entry is None:
        return KostentraegerVerificationResult(
            status=VerificationStatus.NOT_FOUND,
            card_ik=cleaned,
            provenance=provenance,
        )

    acceptance = (entry.get("acceptance_ik") or "").strip()
    determined = bool(acceptance)
    return KostentraegerVerificationResult(
        status=VerificationStatus.FOUND,
        card_ik=cleaned,
        recipient_ik=acceptance,
        recipient_determined=determined,
        name=entry.get("name", ""),
        abrechnungscode=entry.get("abrechnungscode", ""),
        dfue_hint=entry.get("dfue_hint", ""),
        dfue_protocol=entry.get("dfue_protocol", ""),
        source=entry.get("source", ""),
        provenance=provenance,
    )


def resolve_acceptance_ik(store: KostentraegerStore | None, ik: str) -> str | None:
    """Return the § 302 recipient IK when found and determined; otherwise ``None``."""
    result = verify_kostentraeger_ik(store, ik)
    if result.status != VerificationStatus.FOUND or not result.recipient_determined:
        return None
    return result.recipient_ik


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
    chosen = preferred[0] if preferred else (fallback[0] if fallback else None)
    if chosen is None:
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
    dfu_protocol = ""

    def flush() -> None:
        nonlocal current, vkgs, dfu_channel, dfu_protocol
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
            "dfue_protocol": dfu_protocol,
            "abrechnungscode": abr_code,
        }
        current = None
        vkgs = []
        dfu_channel = ""
        dfu_protocol = ""

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
            dfu_protocol = ""
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
                if len(vals) > 1:
                    dfu_protocol = vals[1]
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


def read_kotr_text(path: str | Path, encoding: str | None = None) -> str:
    """Read a Kostenträger file. Official UNOC:3 files are ISO-8859-1; fixtures may be UTF-8."""
    raw = Path(path).read_bytes()
    if encoding:
        return raw.decode(encoding)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def _write_store(entries: dict[str, dict[str, str]], store_path: str | Path) -> None:
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


def ingest_kostentraeger_file(
    path: str | Path,
    spec_version: str | None = None,
    store_path: str | Path | None = None,
) -> KostentraegerStore:
    """Ingest an Anhang-3 EDIFACT Kostenträger file; atomically replace store_path if provided."""
    spec_version = resolve_spec_version(spec_version)
    root = version_dir(spec_version)
    schema = yaml.safe_load((root / "kostentraeger" / "anhang3.yaml").read_text(encoding="utf-8"))
    encoding = schema.get("encoding")
    text = read_kotr_text(path, encoding if isinstance(encoding, str) else None)
    if not text.strip():
        raise ValueError("Kostentraeger file is empty")

    entries = _parse_kotr_edifact(text, schema)
    source_name = Path(path).name
    store = KostentraegerStore(entries, provenance=(source_name,))
    if store_path is not None:
        _write_store(entries, store_path)
    return store


def ingest_kostentraeger_files(
    paths: list[str | Path],
    spec_version: str | None = None,
    store_path: str | Path | None = None,
) -> KostentraegerStore:
    """Ingest several Kostenträger files; later files overwrite the same IK."""
    merged: dict[str, dict[str, str]] = {}
    ordered = sorted(paths, key=lambda p: Path(p).name.upper())
    provenance: list[str] = []
    for path in ordered:
        store = ingest_kostentraeger_file(path, spec_version=spec_version)
        source = Path(path).name
        provenance.append(source)
        for ik, entry in store.as_dict().items():
            merged[ik] = {**entry, "source": source}
    store = KostentraegerStore(merged, provenance=tuple(provenance))
    if store_path is not None:
        _write_store(merged, store_path)
    return store


def load_store(store_path: str | Path) -> KostentraegerStore:
    data = json.loads(Path(store_path).read_text(encoding="utf-8"))
    return KostentraegerStore(data, provenance=(Path(store_path).name,))
