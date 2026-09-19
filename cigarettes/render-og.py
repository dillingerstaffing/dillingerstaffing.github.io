#!/usr/bin/env python3
"""Render cigarettes/og-image.png (1200x630) in the notebook design language."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
PAPER = (233, 227, 213)
INK = (29, 28, 24)
SANGUINE = (139, 62, 47)
SOFT = (93, 87, 76)
LINE = (165, 155, 135)
GHOST = (29, 28, 24)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img, "RGBA")

# left margin hairline
d.line([(28, 0), (28, H)], fill=GHOST + (22,), width=1)

x0 = 96
f_stamp = ImageFont.truetype(MONO, 20)
f_head = ImageFont.truetype(SERIF, 150)
f_sub = ImageFont.truetype(SERIF, 34)
f_meta = ImageFont.truetype(MONO, 17)
f_meta_b = ImageFont.truetype(MONO_B, 17)

y = 64
d.text((x0, y), "FOLIO 10 / BRAND LEDGER", font=f_stamp, fill=SANGUINE)

y = 118
d.text((x0, y), "Cigarette", font=f_head, fill=INK)
y2 = y + 132
d.text((x0, y2), "Comparison.", font=f_head, fill=SANGUINE)

y = y2 + 172
d.text((x0, y), "Fifty-three brands, nineteen factors.", font=f_sub, fill=INK)
d.text((x0, y + 44), "Machine measurements kept apart from human dose.", font=f_sub, fill=SOFT)

# bottom strip
strip_y = H - 78
d.line([(x0, strip_y), (W - 80, strip_y)], fill=LINE, width=1)
y = strip_y + 24
d.text((x0, y), "53", font=f_meta_b, fill=SANGUINE)
d.text((x0 + 44, y), "BRANDS", font=f_meta, fill=SOFT)
d.text((x0 + 215, y), "19", font=f_meta_b, fill=SANGUINE)
d.text((x0 + 259, y), "FACTORS", font=f_meta, fill=SOFT)
d.text((x0 + 450, y), "TAR", font=f_meta, fill=SOFT)
d.text((x0 + 520, y), "NICOTINE", font=f_meta, fill=SOFT)
d.text((x0 + 660, y), "CO", font=f_meta, fill=SOFT)
url = "dillingerstaffing.github.io/cigarettes/"
bw = d.textlength(url, font=f_meta)
d.text((W - 80 - bw, y), url, font=f_meta, fill=SOFT)

img.save("/home/hatch/workspace/deploy/index-site/cigarettes/og-image.png")
print("wrote og-image.png", img.size)
