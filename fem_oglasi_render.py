# FEM oglasi: render naslova preko fotografije (feed 4:5 i story 9:16). Upotreba: python fem_oglasi_render.py <folder_sa_fotografijama> <izlazni_folder>
# F = FEM\fonts (InterDisplay-SemiBold.otf, Inter-Bold.otf, Inter-Medium.otf), stoji u paketu. Treba samo: pip install pillow
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
A, O = sys.argv[1], sys.argv[2]
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep  # FEM\fonts, pored skripte
def fnt(n, s): return ImageFont.truetype(F + n, s)
PURPLE = (74, 32, 56); GOLD = (201, 170, 118); WHITE = (251, 247, 242); SOFT = (234, 214, 222)

def fit(src, w, h, cx=0.5, cy=0.5):
    im = Image.open(src).convert("RGB"); W, H = im.size; r = w / h
    if W / H > r: nw = int(H * r); x = int((W - nw) * cx); im = im.crop((x, 0, x + nw, H))
    else: nh = int(W / r); y = int((H - nh) * cy); im = im.crop((0, y, W, y + nh))
    return im.resize((w, h), Image.LANCZOS)

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def fit_top(src, w, h, y0=0):
    # Story: fotka u punoj širini gore, ispod ljubičasta podloga. Manje uvećanja, a donji deo fotke ostaje iznad teksta.
    ph = Image.open(src).convert("RGB"); ph = ph.resize((w, int(ph.height * w / ph.width)), Image.LANCZOS)
    im = Image.new("RGB", (w, h), PURPLE); im.paste(ph, (0, y0))
    fade = Image.new("L", (1, 160)); [fade.putpixel((0, i), int(255 * i / 159)) for i in range(160)]
    im.paste(Image.new("RGB", (w, 160), PURPLE), (0, y0 + ph.height - 160), fade.resize((w, 160)))
    return im

def ad(src, out, head, small, w, h, cx=0.5, cy=0.5, bottom_pad=150, top=False, y0=0):
    im = fit_top(src, w, h, y0) if top else fit(src, w, h, cx, cy)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))  # blago izoštravanje posle uvećanja
    # gradient
    g0 = int(h * 0.48)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for y in range(g0, h):
        t = (y - g0) / (h - g0); a = int(235 * min(1, t * 1.6))
        od.line([(0, y), (w, y)], fill=PURPLE + (a,))
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(im); L = 72; maxw = w - 2 * L
    hf = fnt("InterDisplay-SemiBold.otf", 84); sf = fnt("Inter-Medium.otf", 30)
    ef = fnt("Inter-Bold.otf", 27); ff = fnt("Inter-Medium.otf", 31)
    hl = [l for part in head.split("|") for l in wrap(d, part, hf, maxw)]; sl = wrap(d, small, sf, maxw) if small else []
    block = 40 + 18 + len(hl) * 96 + (14 + len(sl) * 40 if sl else 0) + 34 + 44
    y = h - bottom_pad - block
    x = L
    for ch in "FEM · USKORO":
        d.text((x, y), ch, font=ef, fill=GOLD); x += d.textlength(ch, font=ef) + 7
    y += 40 + 18
    for ln in hl: d.text((L, y), ln, font=hf, fill=WHITE); y += 96
    if sl:
        y += 14
        for ln in sl: d.text((L, y), ln, font=sf, fill=SOFT); y += 40
    y += 34
    foot = "Lista čekanja · 15% na prvu narudžbinu"
    d.text((L, y), foot, font=ff, fill=WHITE)
    d.line([(L, y + 46), (L + d.textlength(foot, font=ff), y + 46)], fill=GOLD, width=3)
    im.save(out, quality=90)

# FEM v3: snaga / lepota / jutro. cx, cy pomeraju kadar (ne tekst) ako se naslov preklapa sa licem.
JOBS = [
    ("snaga",  "snaga_oglas.jpg",  "Snaga posle 40.|nije samo za teretanu.",
     "Kreatin povećava fizičku sposobnost pri uzastopnim, kratkotrajnim vežbama visokog intenziteta.", 0.5, 0.0),
    ("lepota", "lepota_oglas.jpg", "Kosa, koža i nokti|posle 40.",
     "Vitamin C doprinosi normalnom stvaranju kolagena za normalnu funkciju kože.", 0.5, 0.0),
    ("jutro",  "jutro_oglas.jpg",  "Jedna kesica|umesto pet bočica.",
     "Kreatin, kolagen i 9 vitamina i minerala. Razmutiš u vodi i popiješ.", 0.5, 0.0),
]
for fmt, (w, h, bp, top) in {"feed_4x5": (1080, 1350, 70, False), "story_9x16": (1080, 1920, 280, True)}.items():
    for name, src, head, small, cx, cy in JOBS:
        ad(f"{A}/{src}", f"{O}/{name}_{fmt}.jpg", head, small, w, h, cx=cx, cy=cy, bottom_pad=bp, top=top, y0=40 if top else 0)
print("ok")
