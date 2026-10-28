"""Download official SLE Kostenträgerdateien from gkv-datenaustausch.de."""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from urllib.parse import unquote, urljoin, urlparse

USER_AGENT = "sozialstack-ta5py/0.1"
BASE_URL = "https://www.gkv-datenaustausch.de"
OVERVIEW_URL = (
    "https://www.gkv-datenaustausch.de/leistungserbringer/"
    "sonstige_leistungserbringer/kostentraegerdateien_sle/kostentraegerdateien.jsp"
)

_KE_RE = re.compile(
    r"(?P<kassenart>AO|EK|BK|IK|BN|LK|GK|SB)05(?P<validity>[A-Z0-9]{4})\.ke(?P<edition>\d+)$",
    re.IGNORECASE,
)

KASSENART_LABEL = {
    "AO": "AOK",
    "EK": "Ersatzkassen (vdek)",
    "BK": "Betriebskrankenkassen",
    "IK": "Innungskrankenkassen",
    "BN": "Knappschaft-Bahn-See",
    "LK": "Landwirtschaftliche Krankenkassen (SVLFG)",
    "GK": "Gesetzliche Krankenversicherung",
    "SB": "Sonstige Kostenträger (Bitmarck)",
}

FetchFn = Callable[[str], bytes]


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


@dataclass(frozen=True)
class KostentraegerRemoteFile:
    filename: str
    path: str
    url: str
    kassenart: str
    validity: str
    edition: str

    @property
    def label(self) -> str:
        return KASSENART_LABEL.get(self.kassenart.upper(), self.kassenart)


def fetch_bytes(url: str, *, timeout: float = 30.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return body if isinstance(body, bytes) else bytes(body)
    except urllib.error.URLError as exc:
        raise ConnectionError(f"unreachable: {url} ({exc})") from exc
    except TimeoutError as exc:
        raise ConnectionError(f"unreachable: {url} (timeout)") from exc


def parse_kostentraeger_overview(html: str, *, base_url: str = BASE_URL) -> list[KostentraegerRemoteFile]:
    collector = _HrefCollector()
    collector.feed(html)
    found: dict[str, KostentraegerRemoteFile] = {}
    for href in collector.hrefs:
        parsed = urlparse(unquote(href.strip()))
        filename = Path(parsed.path).name
        match = _KE_RE.search(filename)
        if match is None:
            continue
        path = parsed.path if parsed.scheme else href
        if not path.startswith("/"):
            path = "/" + path.lstrip("/")
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        found[filename.upper()] = KostentraegerRemoteFile(
            filename=filename,
            path=path,
            url=url,
            kassenart=match.group("kassenart").upper(),
            validity=match.group("validity").upper(),
            edition=match.group("edition"),
        )
    if not found:
        raise ValueError("overview HTML contained no Kostenträger .ke* links")
    return sorted(found.values(), key=lambda item: item.filename.upper())


def download_kostentraeger_files(
    files: list[KostentraegerRemoteFile],
    dest_dir: Path,
    *,
    fetch: FetchFn | None = None,
) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    getter = fetch or fetch_bytes
    written: list[Path] = []
    for item in files:
        dest = dest_dir / item.filename
        raw = getter(item.url)
        if b"UNB+" not in raw and b"IDK+" not in raw:
            raise ValueError(f"not an Anhang-3 Kostenträger file: {item.filename}")
        dest.write_bytes(raw)
        written.append(dest)
    return written
