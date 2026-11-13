#!/usr/bin/env python3
"""Merge chapters into one Markdown file, making footnote labels unique.

Usage: python3 -I merge.py <zh_dir> <out.md> [--with-appendix]
"""
import re
import sys
from pathlib import Path


def uniquify_footnotes(text: str, prefix: str) -> str:
    def repl(m: re.Match) -> str:
        label = m.group(1)
        if label.startswith(prefix + "-"):
            return m.group(0)
        return f"[^{prefix}-{label}]"
    return re.sub(r"\[\^([^\]]+)\]", repl, text)


def main(zh_dir: str, out_path: str, with_appendix: bool = False) -> None:
    zh = Path(zh_dir)
    parts = []
    for name in ("00-front.md", "00-intro.md", "00-toc.md"):
        p = zh / name
        if p.exists():
            parts.append(uniquify_footnotes(p.read_text(encoding="utf-8"),
                                            "front"))
    missing = []
    for n in range(1, 86):
        p = zh / f"{n:02d}.md"
        if p.exists():
            parts.append(uniquify_footnotes(p.read_text(encoding="utf-8"),
                                            f"c{n:02d}"))
        else:
            missing.append(n)
    if with_appendix:
        root = zh.parent
        for name, pref, title in (
                ("notes/authors.md", "appA", "附录一　三位作者"),
                ("notes/context.md", "appB", "附录二　批准宪法之争大事年表"),
                ("glossary.md", "appC", "附录三　统一译名表"),
                ("notes/textual.md", "appD", "附录四　底本与校勘")):
            p = root / name
            if p.exists():
                txt = p.read_text(encoding="utf-8")
                txt = re.sub(r"^# .*$", f"# {title}", txt, count=1,
                             flags=re.M)
                parts.append(uniquify_footnotes(txt, pref))
    out = Path(out_path)
    out.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"merged {len(parts)} parts -> {out}")
    if missing:
        print(f"WARNING missing chapters: {missing}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], args[1], "--with-appendix" in sys.argv)
