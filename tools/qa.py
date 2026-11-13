#!/usr/bin/env python3
"""QA check for translated essays.

Usage: python3 -I qa.py <src_dir> <zh_dir> [--fix-list]
"""
import re
import sys
from pathlib import Path


def blocks(text: str) -> list[str]:
    out = []
    for b in re.split(r"\n\s*\n", text):
        s = b.strip()
        if not s:
            continue
        # Exclude the opening salutation and the closing signature.
        if re.fullmatch(r"致.*人民[:：]", s) or s == "普布利乌斯":
            continue
        out.append(s)
    return out


def section(text: str, name: str) -> str:
    m = re.search(rf"^## {name}\s*$", text, re.M)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^## ", text[start:], re.M)
    return text[start:start + nxt.start()] if nxt else text[start:]


def main(src_dir: str, zh_dir: str) -> None:
    src = Path(src_dir)
    zh = Path(zh_dir)
    problems = []
    for n in range(1, 86):
        sf = src / f"{n:02d}.md"
        zf = zh / f"{n:02d}.md"
        if not zf.exists():
            problems.append(f"{n:02d}: 未译")
            continue
        st = sf.read_text(encoding="utf-8")
        zt = zf.read_text(encoding="utf-8")
        src_body = st.split("## 原文", 1)[1]
        sb = blocks(src_body)
        trans = section(zt, "译文")
        tb = blocks(trans)
        zh_chars = len(re.findall(r"[一-鿿]", trans))
        en_words = len(src_body.split())
        ratio = zh_chars / max(en_words, 1)
        flags = []
        for name in ("背景导读", "作者倾向与观点", "译文"):
            if not section(zt, name):
                flags.append(f"缺{name}")
        if tb and not (0.6 <= len(tb) / max(len(sb), 1) <= 2.0):
            flags.append(f"段数 {len(tb)}/{len(sb)}")
        if ratio < 1.05 or ratio > 2.8:
            flags.append(f"字词比 {ratio:.2f}")
        status = "OK " if not flags else "!! "
        print(f"{status}{n:02d}  原文{en_words:5d}词  {len(sb):2d}段  "
              f"译文{zh_chars:5d}字  {len(tb):2d}段  比{ratio:.2f}"
              + ("  " + "; ".join(flags) if flags else ""))
        if flags:
            problems.append(f"{n:02d}: " + "; ".join(flags))
    print("\n==== 问题汇总 ====")
    print("\n".join(problems) if problems else "无")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
