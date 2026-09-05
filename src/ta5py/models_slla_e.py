from __future__ import annotations

from typing import Any


def ensure_ambulance_profile(claim: dict[str, Any]) -> str | None:
    profile = claim.get("profile", "krankentransport")
    if profile not in ("krankentransport", "slla_e", "E"):
        return "unsupported_scope"
    if claim.get("sammelgruppe") not in (None, "E", "e"):
        return "unsupported_scope"
    return None


def iter_slla_cases(claim: dict[str, Any]) -> list[dict[str, Any]]:
    slla = claim.get("slla") or claim.get("slla_e")
    if isinstance(slla, dict):
        return slla.get("cases") or []
    if isinstance(slla, list) and slla:
        first = slla[0]
        if "cases" in first:
            return first["cases"]
        return slla
    return claim.get("cases") or []
