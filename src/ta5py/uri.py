from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json_uri(uri: str) -> dict[str, Any]:
    raw = uri
    if raw.startswith("file:"):
        raw = raw[5:]
        if raw.startswith("//"):
            raw = raw[2:]
    path = Path(raw)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"JSON URI must decode to an object: {uri}")
    return data
