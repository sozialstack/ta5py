"""Reserved real-Sozialdaten pattern checks for fixtures (SC-007 / FR-011)."""

from __future__ import annotations

import re
from pathlib import Path

# Allowlisted synthetic insured IDs used in format fixtures
_SYNTH_KVNR = re.compile(r"\b(?:A00000000\d|SYNTH[A-Z0-9]*|TEST[A-Z0-9]*)\b")
_KVNR_SHAPE = re.compile(r"\b([A-Z][0-9]{9})\b")
_FORBIDDEN_MARKERS = re.compile(
    r"(?i)\b(REAL_PATIENT|ECHTE_SOZIALDATEN|PRODUCTION_VERSICHERTER|LIVE_VERSICHERTE[NR]?)\b"
)
_SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".bin"}


def scan_text(text: str, path: Path | str) -> list[str]:
    path = Path(path)
    findings: list[str] = []
    if _FORBIDDEN_MARKERS.search(text):
        findings.append(f"{path}: forbidden Sozialdaten marker")
    for m in _KVNR_SHAPE.finditer(text):
        token = m.group(1)
        if _SYNTH_KVNR.fullmatch(token):
            continue
        findings.append(f"{path}: non-allowlisted KVNR-shaped token {token}")
    return findings


def scan_tree(roots: list[Path]) -> list[str]:
    findings: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() in _SKIP_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            findings.extend(scan_text(text, path))
    return findings
