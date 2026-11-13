#!/usr/bin/env python3
"""Final structural checks before building the book.

Usage: python3 -I final_check.py <zh_dir> <index.json>
"""
import json
import re
import sys
from pathlib import Path


def section(text: str, name: str) -> str:
    m = re.search(rf"^## {name}\s*$", text, re.M)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^## ", text[start:], re.M)
    return text[start:start + nxt.start()] if nxt else text[start:]


def main(zh_dir: str, index_path: str) -> None:
    zh = Path(zh_dir)
    idx = {x["no"]: x for x in json.load(open(index_path, encoding="utf-8"))}
    missing, problems = [], []
    seen_intros = {}
    for n in range(1, 86):
        p = zh / f"{n:02d}.md"
        if not p.exists():
            missing.append(n)
            continue
        t = p.read_text(encoding="utf-8")
        flags = []
        for name in ("背景导读", "作者倾向与观点", "译文"):
            if not section(t, name).strip():
                flags.append(f"缺{name}")
        intro = section(t, "背景导读").strip()
        key = intro[:60]
        if key and key in seen_intros:
            flags.append(f"导读与第{seen_intros[key]}篇雷同")
        elif key:
            seen_intros[key] = n
        author = idx[n]["author"].split("（")[0]
        analysis = section(t, "作者倾向与观点")
        if author and author not in analysis:
            flags.append(f"作者段未提{author}")
        if len(section(t, "译文")) < 800:
            flags.append("译文过短")
        if flags:
            problems.append(f"{n:02d}: " + "; ".join(flags))
    print("缺篇:", missing if missing else "无")
    print("问题:")
    print("\n".join(problems) if problems else "无")
    total = sum(len(re.findall(r"[一-鿿]",
                (zh / f"{n:02d}.md").read_text(encoding="utf-8")))
                for n in range(1, 86) if (zh / f"{n:02d}.md").exists())
    print(f"已完成篇目正文总汉字数（含导读与注释）：{total}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
