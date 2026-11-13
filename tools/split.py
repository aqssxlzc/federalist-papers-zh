#!/usr/bin/env python3
"""Split the Project Gutenberg Federalist text into per-essay files.

Usage: python3 -I split.py <source.txt> <outdir>
"""
import re
import sys
from pathlib import Path

ROMAN = {
    "I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000,
}


def roman_to_int(s: str) -> int:
    s = s.upper()
    total = 0
    prev = 0
    for ch in reversed(s):
        val = ROMAN[ch]
        if val < prev:
            total -= val
        else:
            total += val
            prev = val
    return total


def main(src: str, outdir: str) -> None:
    text = Path(src).read_text(encoding="utf-8")
    # Body starts after the table of contents: first exact "THE FEDERALIST.\nNo. I."
    start = text.index("\nTHE FEDERALIST.\nNo. I.")
    body = text[start:]
    # Cut the license boilerplate.
    end = body.find("*** END OF THE PROJECT GUTENBERG EBOOK")
    if end != -1:
        body = body[:end]

    pattern = re.compile(
        r"THE FEDERALIST\.\s*\n\s*No\.\s+([IVXL]+)\.\s*\n",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(body))
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    written = []
    for i, m in enumerate(matches):
        start_pos = m.start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = body[start_pos:end_pos]
        num = roman_to_int(m.group(1))
        if "There are two slightly different versions of No. 70" in chunk[:300]:
            # Skip the first variant; the second (complete) version is used.
            continue
        chunk = chunk.replace(
            "*There are two slightly different versions of No. 70 included "
            "here.*\n", "")
        lines = chunk.split("\n")
        # Drop the heading lines, keep the rest.
        rest = lines[2:]
        # Metadata: title = first non-empty line after optional note lines.
        cleaned = []
        skip_note = True
        for line in rest:
            if skip_note and (not line.strip() or line.strip().startswith("(")):
                continue
            skip_note = False
            cleaned.append(line)
        rest = cleaned
        # Title may wrap across lines: join until the next blank line.
        title_lines = []
        for line in rest:
            if not line.strip():
                break
            title_lines.append(line.strip())
        title = " ".join(title_lines)
        title = re.sub(r"\s+", " ", title).strip()
        # Find publication line and author line near the top.
        pub = ""
        for line in rest[:8]:
            s = line.strip()
            if s.startswith("From the") or s.startswith("For the"):
                pub = s
                break
        author = ""
        for line in rest[:20]:
            s = line.strip()
            if re.fullmatch(r"(HAMILTON|MADISON|JAY|HAMILTON OR MADISON|"
                            r"HAMILTON AND MADISON)", s):
                author = s
                break
        # Strip the title / pub / author / salutation from the body.
        body_start = 0
        for idx, line in enumerate(rest):
            if line.strip().startswith("To the People of the State of New York"):
                body_start = idx
                break
        content = "\n".join(rest[body_start:]).strip()
        content = re.sub(r"\n{3,}", "\n\n", content)

        fname = out / f"{num:02d}.md"
        meta = (
            f"# No. {num} — {title}\n\n"
            f"- 发表信息: {pub or '(未载)'}\n"
            f"- 署名: {author or '(未载)'}\n\n"
            f"## 原文\n\n{content}\n"
        )
        fname.write_text(meta, encoding="utf-8")
        written.append((num, title, author, len(content.split())))

    written.sort()
    for num, title, author, words in written:
        print(f"{num:02d}\t{author:20s}\t{words:5d}w\t{title}")
    print(f"\nTOTAL {len(written)} essays, {sum(w[3] for w in written)} words")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
