#!/usr/bin/env python3
"""Search the skill's design patterns. Standard library only.

Usage: python3 design_patterns.py [query words] [--room kitchen] [--limit 8]

Three kinds of entry, all read straight from the reference markdown so the
references stay the one source of truth:
  pattern    tables whose first column is "Pattern" (room modules, whole-home, regional)
  fix        "Symptom | Usual fix" diagnostic tables (bedroom, kitchen, bathroom, living)
  archetype  the bedroom archetype layouts (## A. … in rooms/bedroom/patterns.md)
Each cited video ([YT-K1], [HT-I2, I4], [DI 66] or a "Seen in" list of Short
numbers) is linked to its YouTube page using references/video_sources.json. The MCP server exposes this as
find_design_patterns.
"""
import json
import re
import sys
from pathlib import Path

REFS = Path(__file__).resolve().parent.parent / "references"
ROOM_OF = {  # reference file → room key
    "kitchen": "kitchen", "bathroom": "bathroom", "living-dining": "living", "home-office": "office",
    "balcony-laundry": "utility", "entry-circulation": "entry", "exterior": "exterior", "whole-home": "whole-home",
    "india": "india", "western": "western",
}
ROOMS = sorted(set(ROOM_OF.values()) | {"bedroom"})
STOP = {"a", "an", "the", "and", "or", "for", "to", "of", "in", "on", "with", "my", "is", "it", "how", "what", "do", "i"}


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _clean(text):
    return re.sub(r"\*\*|`", "", text).strip()


def video_ids(text, seen_in=False):
    """IDs cited in text: '[HT-I1, I2, W4]' → HT-I1, HT-I2, HT-W4; '[YT-K1]'; '[DI 66, 9]' → DI-66, DI-9.
    With seen_in, a bare number list ('20, 33, 67') is read as Dreamy Interior Short numbers."""
    ids = []
    if seen_in:
        ids += [f"DI-{n}" for n in re.findall(r"\b(\d{1,3})\b", text)]
    for group in re.findall(r"\[DI ([\d,\s]+)\]", text):
        ids += [f"DI-{n}" for n in re.findall(r"\d+", group)]
    for group in re.findall(r"\[((?:HT|YT)-[^\]]+)\]", text):
        prefix = None
        for part in (p.strip() for p in group.split(",")):
            m = re.match(r"(HT|YT)-([A-Z]\d+)$", part)
            if m:
                prefix = m.group(1)
                ids.append(f"{prefix}-{m.group(2)}")
            elif prefix and re.match(r"[A-Z]\d+$", part):
                ids.append(f"{prefix}-{part}")
    return list(dict.fromkeys(ids))


def load():
    """Every pattern row in the references, with its room, section and linked videos."""
    videos = json.loads((REFS / "video_sources.json").read_text())["videos"]
    rows = []
    def link(ids):
        return [dict(id=i, **videos[i]) for i in ids if i in videos]

    for path in sorted(REFS.rglob("*.md")):
        room = ROOM_OF.get(path.stem, "bedroom" if path.parent.name == "bedroom" else None)
        if room is None:
            continue
        section, header, lines = None, None, path.read_text().splitlines()
        for k, line in enumerate(lines):
            if line.startswith("#"):
                section, header = line.lstrip("#").strip(), None
                m = re.match(r"##\s+([A-Z])\.\s+(.+)", line)
                if path.name == "patterns.md" and room == "bedroom" and m:
                    body = next((l for l in lines[k + 1:] if l.strip()), "")
                    rows.append({"kind": "archetype", "room": room, "section": "Archetype layouts",
                                 "file": str(path.relative_to(REFS.parent)), "pattern": _clean(m.group(2)),
                                 "how": _clean(body), "sources": "bedroom archetype", "videos": link(video_ids(body))})
                continue
            if not line.startswith("|"):
                header = None
                continue
            cells = _cells(line)
            if header is None:
                header = cells if cells and cells[0].lower() in ("pattern", "symptom") else []
                continue
            if not header or set(line) <= set("|-: "):
                continue
            fix = header[0].lower() == "symptom"
            if len(cells) < (2 if fix else 3):
                continue
            src = cells[2] if len(cells) > 2 else ""
            ids = video_ids(cells[1] + " " + src, seen_in=fix and len(cells) > 2 and "[" not in src)
            rows.append({
                "kind": "fix" if fix else "pattern", "room": room, "section": section,
                "file": str(path.relative_to(REFS.parent)), "pattern": _clean(cells[0]), "how": _clean(cells[1]),
                "sources": (_clean(src) if not (fix and src and "[" not in src) else f"[DI {_clean(src)}]")
                or " ".join(re.findall(r"\[[^\]]+\]", cells[1])),
                "videos": link(ids),
            })
    return rows


def _words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 1}


def search(query="", room=None, limit=8):
    """Patterns ranked by how many query words they share (pattern name counts double)."""
    if room is not None and room not in ROOMS:
        raise ValueError(f"unknown room {room!r}; rooms are {ROOMS}")
    q = _words(query or "")
    hits = []
    for r in load():
        if room and r["room"] != room:
            continue
        name, body = _words(r["pattern"]), _words(r["how"] + " " + r["section"])
        score = 2 * len(q & name) + len(q & body) if q else 1
        # light stemming: "drawers" finds "drawer"
        score += sum(1 for w in q if any(t.startswith(w[:5]) for t in name | body) and w not in name | body) * 0.5 if q else 0
        if score > 0:
            hits.append((score, r))
    hits.sort(key=lambda h: -h[0])
    return [r for _, r in hits[:max(1, min(limit, 30))]]


def main():
    args, opts = [], {}
    it = iter(sys.argv[1:])
    for a in it:
        if a in ("--room", "--limit"):
            opts[a] = next(it, None)
        elif a in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        else:
            args.append(a)
    try:
        found = search(" ".join(args), opts.get("--room"), int(opts.get("--limit") or 8))
    except ValueError as e:
        sys.exit(str(e))
    for r in found:
        vids = ", ".join(v["url"] for v in r["videos"])
        print(f"[{r['room']}] {r['pattern']}: {r['how']}  ({r['sources']}){'  ' + vids if vids else ''}")


if __name__ == "__main__":
    main()
