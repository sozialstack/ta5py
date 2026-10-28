"""Syntax results owned by ta5py.

Field names match the clearing-contracts types sozialstack maps at its boundary.
This package does not depend on that monorepo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldError:
    field: str
    message: str


@dataclass
class FormatResult:
    dataset_id: str
    output_uri: str | None
    syntax_ok: bool
    plausibility_ok: bool | None = None
    errors: list[FieldError] = field(default_factory=list)
    payload: dict[str, Any] | None = None
