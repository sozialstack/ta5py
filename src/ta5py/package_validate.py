from __future__ import annotations

from typing import Any


REQUIRED_TOP = ("version_label", "provenance", "una", "messages", "segments")


def validate_package_dict(pkg: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP:
        if key not in pkg:
            errors.append(f"missing top-level key: {key}")
    prov = pkg.get("provenance") or {}
    if prov.get("scope") != "krankentransport":
        errors.append("provenance.scope must be krankentransport")
    if "slla_e" not in (pkg.get("messages") or {}):
        errors.append("messages.slla_e required")
    for code in ("FKT", "REC", "INV", "NAD", "KTL", "EKT", "ZKT", "BES"):
        if code not in (pkg.get("segments") or {}):
            errors.append(f"missing required segment definition: {code}")
    return errors
