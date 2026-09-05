from __future__ import annotations


def escape(value: str, release: str, specials: str) -> str:
    out: list[str] = []
    for ch in value:
        if ch == release or ch in specials:
            out.append(release)
        out.append(ch)
    return "".join(out)


def unescape(value: str, release: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(value):
        if value[i] == release and i + 1 < len(value):
            out.append(value[i + 1])
            i += 2
            continue
        out.append(value[i])
        i += 1
    return "".join(out)


def join_segment(tag: str, fields: list[str], una: dict[str, str]) -> str:
    el = una["element"]
    release = una["release"]
    end = una["segment_end"]
    specials = el + una["component"] + end
    parts = [tag] + [escape(f, release, specials) for f in fields]
    # Drop trailing empty Kann fields
    while len(parts) > 1 and parts[-1] == "":
        parts.pop()
    return el.join(parts) + end


def split_segments(wire: str, una: dict[str, str]) -> list[str]:
    end = una["segment_end"]
    release = una["release"]
    segs: list[str] = []
    buf: list[str] = []
    i = 0
    while i < len(wire):
        ch = wire[i]
        if ch == release and i + 1 < len(wire):
            buf.append(ch)
            buf.append(wire[i + 1])
            i += 2
            continue
        if ch == end:
            segs.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if buf:
        segs.append("".join(buf))
    return [s for s in segs if s]


def split_fields(segment: str, una: dict[str, str]) -> list[str]:
    el = una["element"]
    release = una["release"]
    parts: list[str] = []
    buf: list[str] = []
    i = 0
    while i < len(segment):
        ch = segment[i]
        if ch == release and i + 1 < len(segment):
            buf.append(ch)
            buf.append(segment[i + 1])
            i += 2
            continue
        if ch == el:
            parts.append(unescape("".join(buf), release))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    parts.append(unescape("".join(buf), release))
    return parts
