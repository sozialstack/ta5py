from __future__ import annotations

from typing import Any


def ensure_ambulance_profile(claim: dict[str, Any]) -> str | None:
    profile = claim.get("profile", "krankentransport")
    if profile not in ("krankentransport", "slla_e", "E"):
        return "unsupported_scope"
    if claim.get("sammelgruppe") not in (None, "E", "e"):
        return "unsupported_scope"
    return None


def _as_case_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def iter_slla_cases(claim: dict[str, Any]) -> list[dict[str, Any]]:
    slla = claim.get("slla") or claim.get("slla_e")
    if isinstance(slla, dict):
        return _as_case_list(slla.get("cases"))
    if isinstance(slla, list) and slla:
        first = slla[0]
        if isinstance(first, dict) and "cases" in first:
            return _as_case_list(first["cases"])
        return _as_case_list(slla)
    return _as_case_list(claim.get("cases"))
