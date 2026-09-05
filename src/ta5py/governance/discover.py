"""Discover official publications from HTML overview snapshots or network."""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from gkv_edi.governance.models import OfficialPublication
from gkv_edi.governance.scope import is_in_scope_bucket

# Filename patterns seen on gkv-datenaustausch.de SLE technische Anlagen pages.
_PDF_RE = re.compile(
    r"(?P<name>"
    r"Anlage_1_TP5_V(?P<a1_ver>\d+)(?:_(?P<a1_stand>\d{8}))?|"
    r"Anlage_3_TP5_V(?P<a3_ver>\d+)(?:_(?P<a3_stand>\d{8}))?|"
    r"Anlage_5_TP5_V(?P<a5_ver>[\d_]+)(?:_(?P<a5_stand>\d{8}))?|"
    r"Anhang_03_Anlage_1_TP5_V(?P<anh_ver>\d+)(?:_(?P<anh_stand>\d{8}))?"
    r")\.pdf",
    re.IGNORECASE,
)


class _HrefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.hrefs.append(value)


def _stand_iso(yyyymmdd: str | None) -> str | None:
    if not yyyymmdd or len(yyyymmdd) != 8 or not yyyymmdd.isdigit():
        return None
    return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


def _normalize_version(raw: str) -> int | str:
    if raw.isdigit():
        return int(raw)
    # Anlage 5 style e.g. 4_0 → keep string, prefer leading int when possible
    head = raw.split("_")[0]
    return int(head) if head.isdigit() else raw


def publication_from_pdf_path(path: str) -> OfficialPublication | None:
    """Map a PDF URL path/filename to an OfficialPublication, or None if unrecognized."""
    cleaned = unquote(path.strip())
    filename = Path(cleaned).name
    match = _PDF_RE.search(filename)
    if not match:
        return None

    if match.group("a1_ver"):
        bucket = "anlage-1"
        version = _normalize_version(match.group("a1_ver"))
        stand = _stand_iso(match.group("a1_stand"))
        pub_id = f"anlage-1-v{version}"
    elif match.group("a3_ver"):
        bucket = "anlage-3"
        version = _normalize_version(match.group("a3_ver"))
        stand = _stand_iso(match.group("a3_stand"))
        pub_id = f"anlage-3-v{version}"
    elif match.group("a5_ver"):
        bucket = "anlage-5"
        version = _normalize_version(match.group("a5_ver"))
        stand = _stand_iso(match.group("a5_stand"))
        pub_id = "anlage-5"
    elif match.group("anh_ver"):
        bucket = "anhang-3"
        version = _normalize_version(match.group("anh_ver"))
        stand = _stand_iso(match.group("anh_stand"))
        pub_id = f"anhang-3-v{version}"
    else:
        return None

    # Prefer path-only (no scheme/host) for manifest compatibility
    parsed = urlparse(cleaned)
    path_only = parsed.path if parsed.scheme else cleaned
    if not path_only.startswith("/"):
        path_only = "/" + path_only.lstrip("/")

    return OfficialPublication(
        id=pub_id,
        bucket=bucket,
        filename=filename,
        path=path_only,
        version=version,
        stand_date=stand,
        in_scope=is_in_scope_bucket(bucket),
    )


def parse_overview_html(html: str) -> list[OfficialPublication]:
    """Parse overview HTML into publications. Raises ValueError if no PDF links found."""
    collector = _HrefCollector()
    try:
        collector.feed(html)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"failed to parse overview HTML: {exc}") from exc

    pubs: dict[str, OfficialPublication] = {}
    for href in collector.hrefs:
        if ".pdf" not in href.lower():
            continue
        pub = publication_from_pdf_path(href)
        if pub is None:
            # Unrecognized PDF — record as out-of-scope bucket when possible
            filename = Path(unquote(href)).name
            parsed = urlparse(href)
            path_only = parsed.path if parsed.scheme else href
            if not path_only.startswith("/"):
                path_only = "/" + path_only.lstrip("/")
            oos = OfficialPublication(
                id=f"oos-{filename}",
                bucket="other",
                filename=filename,
                path=path_only,
                version="unknown",
                stand_date=None,
                in_scope=False,
            )
            pubs[oos.id] = oos
            continue
        pubs[pub.id] = pub

    if not pubs:
        raise ValueError("overview HTML contained no recognizable publication PDF links")
    return list(pubs.values())


def load_overview_html(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"empty overview HTML: {path}")
    return text


def fetch_overview(
    url: str,
    *,
    timeout: float = 30.0,
) -> tuple[str, dict[str, str | None]]:
    """Fetch overview page; return (body, metadata with etag/last-modified)."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "clearing-format-governance/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            headers = {k.lower(): v for k, v in resp.headers.items()}
            meta = {
                "etag": headers.get("etag"),
                "last_modified": headers.get("last-modified"),
                "content_length": headers.get("content-length"),
            }
            return body, meta
    except urllib.error.URLError as exc:
        raise ConnectionError(f"publication source unreachable: {url} ({exc})") from exc
    except TimeoutError as exc:
        raise ConnectionError(f"publication source unreachable: {url} (timeout)") from exc


def head_check_url(
    url: str,
    *,
    timeout: float = 15.0,
) -> dict[str, str | None]:
    """Optional freshness probe (ETag / Last-Modified / Content-Length)."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "clearing-format-governance/1.0"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return {
                "etag": headers.get("etag"),
                "last_modified": headers.get("last-modified"),
                "content_length": headers.get("content-length"),
            }
    except Exception:  # noqa: BLE001 — optional probe
        return {"etag": None, "last_modified": None, "content_length": None}


def publications_to_docs(pubs: list[OfficialPublication]) -> list[dict[str, Any]]:
    return [
        {
            "id": p.id,
            "bucket": p.bucket,
            "filename": p.filename,
            "path": p.path,
            "version": p.version,
            "stand_date": p.stand_date,
        }
        for p in pubs
    ]
