#!/usr/bin/env python3
"""Build notes/index.json with Chinese titles, dates and authorship.

Usage: python3 -I make_index.py <essays_dir> <meta.json> <out.json>
"""
import json
import re
import sys
from pathlib import Path

TITLES = {
1: "总论",
2: "论外来武力与影响之危险",
3: "续论外来武力与影响之危险",
4: "续论外来武力与影响之危险（二）",
5: "续论外来武力与影响之危险（三）",
6: "论各州之间纷争的危险",
7: "续论各州之间纷争的危险",
8: "论各州之间敌对行动的后果",
9: "论联邦作为防止国内派系与叛乱的保障",
10: "续论联邦作为防止国内派系与叛乱的保障",
11: "论联邦在商业关系与海军方面的效用",
12: "论联邦在财政收入方面的效用",
13: "论联邦在节省政府开支方面的优势",
14: "驳以疆域辽阔为由反对拟议宪法的意见",
15: "论现行邦联不足以维护联邦",
16: "续论现行邦联不足以维护联邦",
17: "续论现行邦联不足以维护联邦（二）",
18: "续论现行邦联不足以维护联邦（三）",
19: "续论现行邦联不足以维护联邦（四）",
20: "续论现行邦联不足以维护联邦（五）",
21: "现行邦联的其他缺陷",
22: "续论现行邦联的其他缺陷",
23: "论建立与拟议政府同样强有力的政府的必要性",
24: "续论为共同防务所必需的权力",
25: "续论为共同防务所必需的权力（二）",
26: "论对立法机关在共同防务方面权力的限制",
27: "续论对立法机关在共同防务方面权力的限制",
28: "续论对立法机关在共同防务方面权力的限制（二）",
29: "论民兵",
30: "论征税的一般权力",
31: "续论征税的一般权力",
32: "续论征税的一般权力（二）",
33: "续论征税的一般权力（三）",
34: "续论征税的一般权力（四）",
35: "续论征税的一般权力（五）",
36: "续论征税的一般权力（六）",
37: "论制宪会议设计适当政府形式的困难",
38: "续论制宪会议的困难，并揭示对新方案的反对意见之支离破碎",
39: "论拟议宪法与共和原则的符合",
40: "论制宪会议组成混合政府的权力：考察与辩护",
41: "宪法所授予权力的总览",
42: "续论宪法所授予的权力",
43: "续论宪法所授予的权力（二）",
44: "对各州权力的限制",
45: "论所谓联邦权力对州政府的危险",
46: "论州政府与联邦政府影响力的比较",
47: "论新政府的特殊结构及权力在各部门间的分配",
48: "论各部门不应分离到彼此之间没有任何宪法制约",
49: "论通过制宪会议诉诸人民以防止任何部门侵权的办法",
50: "论定期诉诸人民",
51: "论政府结构必须提供各部门之间的适当制约与平衡",
52: "论众议院",
53: "续论众议院",
54: "论各州之间众议员席位的分配",
55: "论众议院议员的总数",
56: "续论众议院议员的总数",
57: "论所谓新方案倾向于以牺牲多数为代价抬高少数：结合代表制考察",
58: "驳“议员人数不会随人口增长而增加”的反对意见",
59: "论国会有权规定议员选举",
60: "续论国会有权规定议员选举",
61: "续论国会有权规定议员选举（二）",
62: "论参议院",
63: "续论参议院",
64: "论参议院的权力",
65: "续论参议院的权力",
66: "续论对参议院作为弹劾法庭之权力的反对意见",
67: "论行政部门",
68: "论总统的选举方式",
69: "论行政部门的真实性质",
70: "续论行政部门",
71: "论行政部门的任期",
72: "续论行政部门的任期，并论总统的连任问题",
73: "论行政部门的经费与否决权",
74: "论总统对陆海军力量的指挥权与赦免权",
75: "论总统的缔约权",
76: "论总统的任命权",
77: "续论总统的任命权及行政部门的其他权力",
78: "论司法部门",
79: "续论司法部门",
80: "论司法部门的权力",
81: "续论司法部门，并论司法权的分配",
82: "续论司法部门（二）",
83: "续论司法部门，兼论陪审团审判",
84: "对宪法若干一般性与杂项反对意见的考察与答复",
85: "结语",
}

DISPUTED = {}
for n in range(49, 59):
    DISPUTED[n] = "麦迪逊（旧题“汉密尔顿或麦迪逊”）"
for n in (62, 63):
    DISPUTED[n] = "麦迪逊（旧题“汉密尔顿或麦迪逊”）"
for n in (18, 19, 20):
    DISPUTED[n] = "汉密尔顿（与麦迪逊合作，取材于麦迪逊札记）"


def author(n: int) -> str:
    if n in DISPUTED:
        return DISPUTED[n]
    if n in (2, 3, 4, 5, 64):
        return "杰伊"
    if n in (10, 14) or 37 <= n <= 58:
        return "麦迪逊"
    return "汉密尔顿"


def main(essays_dir: str, meta_path: str, out_path: str) -> None:
    meta = {int(x[0]): x for x in json.load(open(meta_path, encoding="utf-8"))}
    rows = []
    for n in range(1, 86):
        p = Path(essays_dir) / f"{n:02d}.md"
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"^# No\. \d+ — (.*)$", txt, re.M)
        english = m.group(1).strip() if m else ""
        wiki_date = meta[n][1]
        # Prefer the date printed in the newspaper line, when present.
        pub = re.search(r"^- 发表信息: (.*)$", txt, re.M)
        pub_line = pub.group(1).strip() if pub else ""
        dm = re.search(
            r"(January|February|March|April|May|June|July|August|"
            r"September|October|November|December)\s+(\d{1,2}),\s*(\d{4})",
            pub_line)
        date = f"{dm.group(1)} {dm.group(2)}, {dm.group(3)}" if dm else wiki_date
        paper = ""
        if pub_line.startswith("For the Independent Journal"):
            paper = "《独立报》（The Independent Journal）"
        elif pub_line.startswith("From the New York Packet"):
            paper = "《纽约邮船报》（The New York Packet）"
        elif pub_line.startswith("From the Daily Advertiser"):
            paper = "《每日广告报》（The Daily Advertiser）"
        rows.append({
            "no": n,
            "title_zh": TITLES[n],
            "title_en": english,
            "date": date,
            "date_wiki": wiki_date,
            "paper": paper,
            "author": author(n),
            "file": f"{n:02d}.md",
        })
    Path(out_path).write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
