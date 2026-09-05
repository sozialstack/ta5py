from __future__ import annotations

IN_SCOPE_BUCKETS: frozenset[str] = frozenset(
    {"anlage-1", "anlage-3", "anlage-5", "anhang-3"}
)


def is_in_scope_bucket(bucket: str) -> bool:
    return bucket in IN_SCOPE_BUCKETS
