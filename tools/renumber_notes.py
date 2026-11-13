#!/usr/bin/env python3
"""Renumber footnote labels within each chapter by order of first reference,
and sort the definitions accordingly.

Usage: python3 -I renumber_notes.py <zh_dir>
"""
import re
import sys
from pathlib import Path


def split_notes(text: str):
    """Return (body, notes) where notes is a list of (label, block)."""
    starts = [m.start() for m in re.finditer(r"^\[\^([^\]]+)\]:", text, re.M)]
    if not starts:
        return text, []
    body = text[:starts[0]].rstrip() + "\n"
    notes = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(text)
        block = text[s:e].strip()
        label = re.match(r"^\[\^([^\]]+)\]:", block).group(1)
        notes.append((label, block))
    return body, notes


def renumber(text: str) -> str:
    body, notes = split_notes(text)
    order = []
    for m in re.finditer(r"\[\^([^\]]+)\](?!:)", body):
        label = m.group(1)
        if label not in order:
            order.append(label)
    mapping = {old: str(i + 1) for i, old in enumerate(order)}

    def repl(m: re.Match) -> str:
        label = m.group(1)
        return f"[^{mapping.get(label, label)}]"

    body = re.sub(r"\[\^([^\]]+)\]", repl, body)
    new_notes = []
    for label, block in notes:
        new_label = mapping.get(label, label)
        block = re.sub(r"^\[\^[^\]]+\]:", f"[^{new_label}]:", block)
        new_notes.append((new_label, block))
    # Sort numeric labels; non-numeric keep relative order at the end.
    def key(item):
        lab = item[0]
        return (0, int(lab)) if lab.isdigit() else (1, lab)
    new_notes.sort(key=key)
    return body.rstrip() + "\n\n" + "\n\n".join(b for _, b in new_notes) + "\n"


def main(zh_dir: str) -> None:
    changed = 0
    for p in sorted(Path(zh_dir).glob("[0-9][0-9].md")):
        t = p.read_text(encoding="utf-8")
        new = renumber(t)
        if new != t:
            p.write_text(new, encoding="utf-8")
            changed += 1
    print(f"renumbered {changed} files")


if __name__ == "__main__":
    main(sys.argv[1])
