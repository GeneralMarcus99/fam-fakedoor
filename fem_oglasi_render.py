# FEM oglasi: render naslova preko fotografije (feed 4:5 i story 9:16), test od 13.11.2026.
# Upotreba (iz fem-sajt\):  python fem_oglasi_render.py ..\fotografije oglasi
# Skripta sama piše u oglasi\faza1\ i oglasi\faza2\, i pravi oglasi\pregled-oglasi.jpg.
# Fontovi: fem-sajt\fonts (InterDisplay-SemiBold.otf, Inter-Bold.otf, Inter-Medium.otf). Znak: ..\Logo Final\export\znak-zlatni-1000.png
# Treba samo: pip install pillow
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
A, O = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "fonts") + os.sep  # fem-sajt\fonts, pored skripte
ZNAK = os.path.join(HERE, "..", "Logo Final", "export", "znak-zlatni-1000.png")
def fnt(n, s): return ImageFont.truetype(F + n, s)
PURPLE = (74, 32, 56); GOLD = (201, 170, 118); WHITE = (251, 247, 242); SOFT = (234, 214, 222)

_z = Image.open(ZNAK).convert("RGBA")
ZH = 52  # visina znaka u eyebrow redu
ZNAK_IM = _z.resize((max(1, round(_z.width * ZH / _z.height)), ZH), Image.LANCZOS)

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
    im = Image.alpha_composite(im.convert("RGBA"), ov)
    d = ImageDraw.Draw(im); L = 72; maxw = w - 2 * L
    hf = fnt("InterDisplay-SemiBold.otf", 84); sf = fnt("Inter-Medium.otf", 30)
    ef = fnt("Inter-Bold.otf", 27); ff = fnt("Inter-Medium.otf", 31)
    hl = [l for part in head.split("|") for l in wrap(d, part, hf, maxw)]; sl = wrap(d, small, sf, maxw) if small else []
    block = ZH + 18 + len(hl) * 96 + (14 + len(sl) * 40 if sl else 0) + 34 + 44
    y = h - bottom_pad - block
    # eyebrow red: znak (52 px) + 16 px + "FEM · USKORO", vertikalno centrirano
    im.alpha_composite(ZNAK_IM, (L, y))
    x = L + ZNAK_IM.width + 16
    eb = "FEM · USKORO"
    t0, t1 = d.textbbox((0, 0), "FEM", font=ef)[1::2]  # gornja i donja ivica velikih slova
    ty = y + (ZH - (t1 - t0)) / 2 - t0
    for ch in eb:
        d.text((x, ty), ch, font=ef, fill=GOLD); x += d.textlength(ch, font=ef) + 7
    y += ZH + 18
    for ln in hl: d.text((L, y), ln, font=hf, fill=WHITE); y += 96
    if sl:
        y += 14
        for ln in sl: d.text((L, y), ln, font=sf, fill=SOFT); y += 40
    y += 34
    foot = "Prednarudžbina prve serije"
    d.text((L, y), foot, font=ff, fill=WHITE)
    d.line([(L, y + 46), (L + d.textlength(foot, font=ff), y + 46)], fill=GOLD, width=3)
    im.convert("RGB").save(out, quality=90)

# Test 13.11: faza1 = tri formule (poruka jutro), faza2 = lepota i snaga na pobedničkoj formuli.
# Oglasi koriste fotke SA kesicom (jutro_strana, lepota_strana, snaga_oglas); stranica gore ima fotke bez kesice.
# Faza 2 "jutro" koristi slike iz faze 1. cx, cy pomeraju samo kadar (ne tekst) ako naslov pada preko lica.
F1_SMALL = "Za žene posle 40, uz 9 vitamina i minerala. Razmutiš u vodi i popiješ."
JOBS = [
    ("faza1", "f1_kk", "jutro_strana.jpg.jpeg", "Kreatin + kolagen.|Jedna kesica umesto pet bočica.", F1_SMALL, 0.5, 0.0),
    ("faza1", "f1_km", "jutro_strana.jpg.jpeg", "Kreatin + maka.|Jedna kesica umesto pet bočica.", F1_SMALL, 0.5, 0.0),
    ("faza1", "f1_mk", "jutro_strana.jpg.jpeg", "Kolagen + maka.|Jedna kesica umesto pet bočica.", F1_SMALL, 0.5, 0.0),
    ("faza2", "f2_lepota", "lepota_strana.jpg.jpeg", "Kosa, koža i nokti|posle 40.",
     "Biotin, cink i selen doprinose održavanju normalne kose.", 0.5, 0.0),
    ("faza2", "f2_snaga", "snaga_oglas.jpg.jpeg", "Trening posle 40.|Kreatin 3 g, svako jutro.",
     "Kreatin povećava fizičku sposobnost pri uzastopnim, kratkotrajnim vežbama visokog intenziteta.", 0.5, 0.0),
]
FMTS = {"feed_4x5": (1080, 1350, 70, False), "story_9x16": (1080, 1920, 280, True)}
outs = {}
for fmt, (w, h, bp, top) in FMTS.items():
    for faza, name, src, head, small, cx, cy in JOBS:
        os.makedirs(os.path.join(O, faza), exist_ok=True)
        out = os.path.join(O, faza, f"{name}_{fmt}.jpg")
        ad(os.path.join(A, src), out, head, small, w, h, cx=cx, cy=cy, bottom_pad=bp, top=top, y0=40 if top else 0)
        outs[(fmt, name)] = out

# Pregled: svih 10 na jednoj slici (gore feed, dole story)
CW, GAP = 360, 24
cols = len(JOBS)
fh, sh = round(CW * 1350 / 1080), round(CW * 1920 / 1080)
lab = fnt("Inter-Medium.otf", 20)
sheet = Image.new("RGB", (GAP + cols * (CW + GAP), GAP + 30 + fh + GAP + 30 + sh + GAP), (231, 228, 223))
sd = ImageDraw.Draw(sheet)
for r, (fmt, ch) in enumerate([("feed_4x5", fh), ("story_9x16", sh)]):
    y = GAP if r == 0 else GAP + 30 + fh + GAP
    for i, job in enumerate(JOBS):
        x = GAP + i * (CW + GAP)
        sd.text((x, y), f"{job[1]}_{fmt}", font=lab, fill=(30, 26, 31))
        sheet.paste(Image.open(outs[(fmt, job[1])]).resize((CW, ch), Image.LANCZOS), (x, y + 30))
sheet.save(os.path.join(O, "pregled-oglasi.jpg"), quality=85)
print("ok", len(outs), "oglasa")
