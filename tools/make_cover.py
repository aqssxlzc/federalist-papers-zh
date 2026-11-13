#!/usr/bin/env python3
"""Generate a simple cover image for the EPUB."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 1800
NAVY = (18, 28, 46)
GOLD = (198, 164, 92)
CREAM = (238, 232, 218)
FONT = "/system/fonts/NotoSansCJK-Regular.ttc"

img = Image.new("RGB", (W, H), NAVY)
d = ImageDraw.Draw(img)

# Border
d.rectangle([48, 48, W - 48, H - 48], outline=GOLD, width=3)
d.rectangle([66, 66, W - 66, H - 66], outline=GOLD, width=1)

def font(size):
    return ImageFont.truetype(FONT, size, index=0)

def center(text, y, f, fill=CREAM, spacing=0):
    bbox = d.textbbox((0, 0), text, font=f)
    x = (W - (bbox[2] - bbox[0])) // 2
    d.text((x, y), text, font=f, fill=fill)

center("联邦党人文集", 380, font(116), CREAM)
center("THE FEDERALIST PAPERS", 560, font(44), GOLD)

d.line([330, 700, 870, 700], fill=GOLD, width=2)

center("亚历山大·汉密尔顿", 800, font(46), CREAM)
center("詹姆斯·麦迪逊", 880, font(46), CREAM)
center("约翰·杰伊", 960, font(46), CREAM)

center("普布利乌斯", 1130, font(40), GOLD)
center("1787—1788", 1230, font(34), (170, 178, 190))

center("英 译 中 · 全 译 本", 1480, font(34), CREAM)

img.save("build/cover.png")
print("saved build/cover.png")
