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
    return json.loads(path.read_text(encoding="utf-8"))
