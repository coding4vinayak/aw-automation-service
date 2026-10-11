"""Pair orphan <label> text with the control that follows it.

Some pages render `<label>First Name *</label><input ...>` — the text is visible
but never associated, so a screen reader announces the field as bare "edit
text". This gives the control an id and the label a matching for. It only pairs
when the label carries no `for` and the very next tag is an labelless,
non-hidden form control; anything else is reported for a human.

Usage: python3 scripts/pair-labels.py [--apply]
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_TYPES = {"hidden", "submit", "button", "image", "reset"}

PATTERN = re.compile(
    r"<label(?P<lattrs>[^>]*?)>(?P<text>[^<>]*?)</label>"
    r"(?P<gap>\s*)"
    r"<(?P<ctag>input|select|textarea)(?P<cattrs>[^>]*?)>",
    re.IGNORECASE,
)


def slug(text, page, seen):
    base = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-") or "field"
    base = f"{page}-{base}"[:40].strip("-")
    name = base
    i = 2
    while name in seen:
        name = f"{base}-{i}"
        i += 1
    seen.add(name)
    return name


def pair_file(path, apply):
    html = path.read_text()
    seen = set(re.findall(r'id="([^"]+)"', html))
    page = path.stem
    edits = []

    def repl(m):
        lattrs, text, gap, ctag, cattrs = (
            m.group("lattrs"),
            m.group("text"),
            m.group("gap"),
            m.group("ctag"),
            m.group("cattrs"),
        )
        if "for=" in lattrs or "id=" in cattrs:
            return m.group(0)
        if ctag.lower() == "input":
            tm = re.search(r'type="([^"]*)"', cattrs, re.IGNORECASE)
            if tm and tm.group(1).lower() in SKIP_TYPES:
                return m.group(0)
        if not text.strip():
            return m.group(0)
        new_id = slug(text, page, seen)
        edits.append((text.strip(), new_id))
        lattrs2 = lattrs.rstrip() + f' for="{new_id}"'
        cattrs2 = cattrs.rstrip() + f' id="{new_id}"'
        return f"<label{lattrs2}>{text}</label>{gap}<{ctag}{cattrs2}>"

    new = PATTERN.sub(repl, html)
    if edits and apply:
        path.write_text(new)
    return edits


def main():
    apply = "--apply" in sys.argv
    total = 0
    for path in sorted((ROOT / "website").rglob("*.html")):
        edits = pair_file(path, apply)
        for text, new_id in edits:
            print(f"{path.relative_to(ROOT)}: {text!r} -> #{new_id}")
            total += 1
    print(f"{total} pairings {'applied' if apply else 'planned (dry run)'}")


if __name__ == "__main__":
    main()
