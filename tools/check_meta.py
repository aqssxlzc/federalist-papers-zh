#!/usr/bin/env python3
"""Check chapter metadata, footnotes and stray English.

Usage: python3 -I check_meta.py <zh_dir> <index.json>
"""
import json
import re
import sys
from pathlib import Path

MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5,
    "June": 6, "July": 7, "August": 8, "September": 9, "October": 10,
    "November": 11, "December": 12,
}
ZH_MONTH = {v: k for k, v in {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
    "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12,
}.items()}


def zh_date(en: str) -> str:
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", en)
    if not m or m.group(1) not in MONTHS:
        return ""
    return f"{m.group(3)}年{MONTHS[m.group(1)]}月{int(m.group(2))}日"


def main(zh_dir: str, index_path: str) -> None:
    idx = {x["no"]: x for x in json.load(open(index_path, encoding="utf-8"))}
    problems = []
    for n in range(1, 86):
        p = Path(zh_dir) / f"{n:02d}.md"
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        flags = []
        m = re.search(r"^# 第(.+?)篇　(.*)$", t, re.M)
        if not m:
            flags.append("标题格式")
        else:
            if m.group(2).strip() != idx[n]["title_zh"]:
                flags.append(f"标题不符：{m.group(2)}")
        q = re.search(r"^> (.*)$", t, re.M)
        if q:
            want_date = zh_date(idx[n]["date"])
            if want_date and want_date not in q.group(1):
                flags.append(f"日期缺{want_date}")
        else:
            flags.append("缺发表信息")
        # footnote labels consistency
        refs = re.findall(r"\[\^([^\]]+)\](?!:)", t)
        defs = re.findall(r"^\[\^([^\]]+)\]:", t, re.M)
        if sorted(refs) != sorted(defs):
            flags.append(f"脚注不配 {len(refs)}/{len(defs)}")
        # stray English in translation (allow proper names/titles)
        body = t.split("## 译文", 1)[-1].split("## 注释", 1)[0]
        eng = re.findall(r"[A-Za-z]{3,}(?:\s+[A-Za-z]{3,}){2,}", body)
        if eng:
            flags.append("译文英文串：" + "; ".join(eng[:3]))
        if flags:
            problems.append(f"{n:02d}: " + " | ".join(flags))
    print("\n".join(problems) if problems else "全部通过")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
