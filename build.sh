#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p build dist
if [ ! -f build/cover.png ]; then
  python3 -I tools/make_cover.py
fi

python3 -I tools/merge.py zh build/book.md --with-appendix

pandoc build/book.md \
  -o "dist/联邦党人文集.epub" \
  --toc --toc-depth=1 \
  --split-level=1 \
  --epub-cover-image=build/cover.png \
  --css build/style.css \
  --metadata title="联邦党人文集" \
  --metadata subtitle="The Federalist Papers" \
  --metadata author="亚历山大·汉密尔顿、詹姆斯·麦迪逊、约翰·杰伊" \
  --metadata lang=zh-CN \
  --metadata date="2026"

pandoc build/book.md \
  -o "dist/联邦党人文集.html" \
  --standalone --toc --toc-depth=1 \
  --css build/style.css \
  --metadata title="联邦党人文集" \
  --metadata lang=zh-CN

pandoc build/book.md \
  -o "dist/联邦党人文集.docx" \
  --toc --toc-depth=1 \
  --metadata title="联邦党人文集" \
  --metadata author="亚历山大·汉密尔顿、詹姆斯·麦迪逊、约翰·杰伊" \
  --metadata lang=zh-CN

echo "built:"
ls -lh dist/
