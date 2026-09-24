"""Graphics-Engine: 9 professionelle Design-Templates (Text-Designs).

Templates:
  bold_impact, vintage_retro, neon_glow, minimalist_pro, split_dynamic,
  quote_premium, grunge_street, bold_color, sticker_pop

Farbpaletten (10):
  midnight, crimson, ocean, forest, golden, purple, rose, arctic, sand, volt
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import font_manager

TEMPLATES = (
    "bold_impact", "vintage_retro", "neon_glow", "minimalist_pro",
    "split_dynamic", "quote_premium", "grunge_street", "bold_color",
    "sticker_pop",
)


@dataclass(frozen=True)
class Palette:
    name: str
    bg_top: tuple[int, int, int]
    bg_bottom: tuple[int, int, int]
    fg: tuple[int, int, int]
    accent: tuple[int, int, int]

    def bg_image(self, size: int) -> Image.Image:
        img = Image.new("RGB", (size, size))
        d = ImageDraw.Draw(img)
        for y in range(size):
            t = y / max(size - 1, 1)
            c = tuple(int(self.bg_top[i] + (self.bg_bottom[i] - self.bg_top[i]) * t)
                      for i in range(3))
            d.line([(0, y), (size, y)], fill=c)
        return img


PALETTES: dict[str, Palette] = {
    p.name: p for p in (
        Palette("midnight", (15, 15, 35), (40, 45, 90), (255, 255, 255), (120, 140, 255)),
        Palette("crimson", (120, 10, 30), (190, 30, 60), (255, 235, 235), (255, 200, 90)),
        Palette("ocean", (10, 60, 110), (30, 130, 180), (240, 250, 255), (255, 210, 80)),
        Palette("forest", (12, 60, 35), (40, 120, 70), (240, 255, 240), (255, 190, 60)),
        Palette("golden", (200, 150, 20), (255, 200, 60), (60, 40, 10), (40, 30, 10)),
        Palette("purple", (40, 10, 70), (110, 40, 170), (245, 235, 255), (255, 150, 240)),
        Palette("rose", (150, 40, 90), (230, 110, 160), (255, 240, 246), (255, 220, 130)),
        Palette("arctic", (200, 230, 245), (240, 250, 255), (20, 40, 70), (70, 130, 200)),
        Palette("sand", (222, 205, 170), (245, 235, 210), (70, 55, 35), (150, 110, 70)),
        Palette("volt", (20, 25, 20), (35, 45, 35), (204, 255, 0), (255, 255, 255)),
    )
}

DEFAULT_PALETTE = "midnight"


def get_palette(name: str) -> Palette:
    if name not in PALETTES:
        raise ValueError(f"Unbekannte Palette {name!r}. Erlaubt: {', '.join(PALETTES)}")
    return PALETTES[name]


# ------------------------------------------------------------------ public
def render_template(template: str, text: str, palette: str = DEFAULT_PALETTE,
                    size: int = 2000, seed: int | None = None) -> Image.Image:
    """Rendert ein Template. seed != None => reproduzierbar."""
    if template not in TEMPLATES:
        raise ValueError(f"Unbekanntes Template {template!r}. Erlaubt: {', '.join(TEMPLATES)}")
    pal = get_palette(palette)
    rng = random.Random(seed)
    render = _RENDERERS[template]
    return render(text, pal, size, rng)


# ------------------------------------------------------------------ Helpers
def _fitted(img: Image.Image, text: str, max_w_frac: float, max_h_frac: float,
            style: str = "impact") -> ImageFont.ImageFont:
    w, h = img.size
    return font_manager.fit_font_size(style, text, int(w * max_w_frac),
                                      int(h * max_h_frac), start=min(w, h) // 2)


def _center_text(d: ImageDraw.ImageDraw, text: str, font, *,
                  color, cx: int, cy: int, stroke: tuple | None = None,
                  stroke_w: int = 0) -> None:
    tw, th = font_manager.text_size(font, text)
    x, y = cx - tw // 2, cy - th // 2
    if stroke and stroke_w:
        d.text((x, y), text, font=font, fill=color, stroke_width=stroke_w,
               stroke_fill=stroke)
    else:
        d.text((x, y), text, font=font, fill=color)


def _split_lines(text: str, max_words: int = 3) -> list[str]:
    """Lange Texte in Zeilen zu max. max_words Wörtern splitten."""
    words = text.split()
    if len(words) <= max_words:
        return [text]
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == max_words:
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))
    return lines


def _draw_multiline(d: ImageDraw.ImageDraw, lines: list[str], font, *,
                    color, cx: int, cy: int, line_gap: float = 1.15,
                    stroke: tuple | None = None, stroke_w: int = 0) -> None:
    heights = [font_manager.text_size(font, line)[1] for line in lines]
    total = int(sum(heights) * line_gap)
    y = cy - total // 2
    for line, lh in zip(lines, heights, strict=False):
        tw, _ = font_manager.text_size(font, line)
        if stroke and stroke_w:
            d.text((cx - tw // 2, y), line, font=font, fill=color,
                   stroke_width=stroke_w, stroke_fill=stroke)
        else:
            d.text((cx - tw // 2, y), line, font=font, fill=color)
        y += int(lh * line_gap)


# ------------------------------------------------------------------ Templates
def _tpl_bold_impact(text: str, pal: Palette, size: int, rng: random.Random) -> Image.Image:
    """Großer Text + Polka-Muster + Eckverzierungen."""
    img = pal.bg_image(size)
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    dot = tuple(min(255, c) for c in pal.accent) + (45,)
    step = size // 14
    for row, y in enumerate(range(0, size, step)):
        offset = step // 2 if row % 2 else 0
        for x in range(-step, size, step):
            r = step // 8
            od.ellipse([x + offset - r, y - r, x + offset + r, y + r], fill=dot)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)
    # Eckverzierungen
    m, lw = size // 10, max(6, size // 200)
    for corner in ((m, m), (size - m, m), (m, size - m), (size - m, size - m)):
        d.line([corner, (corner[0] + size // 12 * (1 if corner[0] < size // 2 else -1),
                         corner[1])], fill=pal.accent, width=lw)
        d.line([corner, (corner[0],
                         corner[1] + size // 12 * (1 if corner[1] < size // 2 else -1))],
               fill=pal.accent, width=lw)
    lines = _split_lines(text)
    font = _fitted(img, max(lines, key=len), 0.84 if len(lines) == 1 else 0.72, 0.5)
    _draw_multiline(d, lines, font, color=pal.fg, cx=size // 2, cy=size // 2,
                    stroke=pal.accent, stroke_w=max(3, size // 250))
    return img


def _tpl_vintage_retro(text: str, pal: Palette, size: int, rng: random.Random) -> Image.Image:
    """Retro-Stempel (Kreis oder Hexagon)."""
    img = pal.bg_image(size)
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r = int(size * 0.40)
    lw = max(10, size // 90)
    shape = rng.choice(["circle", "hexagon"])
    if shape == "circle":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=pal.fg, width=lw)
        r2 = r - lw * 3
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=pal.accent, width=lw // 2)
    else:
        pts = [(cx + r * math.cos(math.pi / 3 * i - math.pi / 2),
                cy + r * math.sin(math.pi / 3 * i - math.pi / 2)) for i in range(6)]
        d.polygon(pts, outline=pal.fg, width=lw)
        r2 = r - lw * 3
        pts2 = [(cx + r2 * math.cos(math.pi / 3 * i - math.pi / 2),
                 cy + r2 * math.sin(math.pi / 3 * i - math.pi / 2)) for i in range(6)]
        d.polygon(pts2, outline=pal.accent, width=lw // 2)
    lines = _split_lines(text, 2)
    font = _fitted(img, max(lines, key=len), 0.5, 0.28)
    _draw_multiline(d, lines, font, color=pal.fg, cx=cx, cy=cy)
    # Sterne als Zierelemente
    for dy in (-r + lw * 4, r - lw * 4):
        d.text((cx - size // 40, cy + dy - size // 80), "*", font=font_manager.get_font("serif", size // 14),
               fill=pal.accent)
    return img


def _tpl_neon_glow(text: str, pal: Palette, size: int, rng: random.Random) -> Image.Image:
    """Echter Neon-Glow via GaussianBlur."""
    dark = (10, 5, 25)
    img = Image.new("RGB", (size, size), dark)
    d = ImageDraw.Draw(img)
    # dezente Grid-Linien
    step = size // 10
    for i in range(step, size, step):
        d.line([(i, 0), (i, size)], fill=(25, 15, 50), width=2)
        d.line([(0, i), (size, i)], fill=(25, 15, 50), width=2)

    lines = _split_lines(text)
    font = _fitted(img, max(lines, key=len), 0.8 if len(lines) == 1 else 0.7, 0.42)
    glow = Image.new("RGB", (size, size), dark)
    gd = ImageDraw.Draw(glow)
    _draw_multiline(gd, lines, font, color=pal.accent, cx=size // 2, cy=size // 2)
    for blur in (size // 80, size // 160, size // 320):
        glow_layer = glow.filter(ImageFilter.GaussianBlur(blur))
        img = Image.blend(img, glow_layer, 0.55)
    d = ImageDraw.Draw(img)
    _draw_multiline(d, lines, font, color=(255, 255, 255), cx=size // 2, cy=size // 2)
    return img


def _tpl_minimalist_pro(text: str, pal: Palette, size: int, rng: random.Random) -> Image.Image:
    """Eleganter Doppelrahmen."""
    img = pal.bg_image(size)
    d = ImageDraw.Draw(img)
    m1, m2 = size // 8, size // 8 + size // 60
    lw = max(4, size // 300)
    d.rectangle([m1, m1, size - m1, size - m1], outline=pal.fg, width=lw)
    d.rectangle([m2, m2, size - m2, size - m2], outline=pal.accent, width=max(2, lw // 2))
    lines = _split_lines(text, 2)
    font = _fitted(img, max(lines, key=len), 0.62, 0.36, style="serif")
    _draw_multiline(d, lines, font, color=pal.fg, cx=size // 2, cy=size // 2)
    # feine Linie unter dem Text
    d.line([(size // 3, int(size * 0.66)), (2 * size // 3, int(size * 0.66))],
           fill=pal.accent, width=lw)
    return img


def _tpl_split_dynamic(text: str, pal: Palette, size: int, rng: random.Random) -> Image.Image:
    """Diagonaler Farbschnitt."""
    img = pal.bg_image(size)
    d = ImageDraw.Draw(img)
    accent_poly = [(0, 0), (size, 0), (0, int(size * 0.55))]
    d.polygon(accent_poly, fill=pal.accent)
    lines = _split_lines(text, 2)
    font = _fitted(img, max(lines, key=len), 0.7, 0.4)
    # Textblock mittig-unten auf Hauptfarbe
    _draw_multiline(d, lines, font, color=pal.fg, cx=size // 2, cy=int(size * 0.62),
                    stroke=pal.bg_top, stroke_w=max(3, size // 300))
    return img


def _tpl_quote_premium(text: str, pal: Palette, size: int, rng: random.Random) -> Image.Image:
    """Große Anführungszeichen + Rahmen."""
    img = pal.bg_image(size)
    d = ImageDraw.Draw(img)
    m = size // 10
    d.rectangle([m, m, size - m, size - m], outline=pal.accent, width=max(6, size // 150))
    qfont = font_manager.get_font("serif", size // 3)
    d.text((int(size * 0.16), int(size * 0.12)), "“", font=qfont, fill=pal.accent)
    d.text((int(size * 0.78), int(size * 0.55)), "”", font=qfont, fill=pal.accent)
    lines = _split_lines(text, 3)
    font = _fitted(img, max(lines, key=len), 0.6, 0.3, style="serif")
    _draw_multiline(d, lines, font, color=pal.fg, cx=size // 2, cy=int(size * 0.48))
    return img


def _tpl_grunge_street(text: str, pal: Palette, size: int, rng: random.Random) -> Image.Image:
    """Kratzer + Rotation + Textur."""
    img = pal.bg_image(size)
    d = ImageDraw.Draw(img)
    # Kratzer
    for _ in range(46):
        x, y = rng.randint(0, size), rng.randint(0, size)
        x2 = x + rng.randint(-size // 4, size // 4)
        y2 = y + rng.randint(-size // 4, size // 4)
        d.line([(x, y), (x2, y2)], fill=pal.accent, width=rng.randint(2, max(3, size // 500)))
    # Text-Karte rotiert
    card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    lines = _split_lines(text, 2)
    font = _fitted(card, max(lines, key=len), 0.72, 0.4)
    _draw_multiline(cd, lines, font, color=pal.fg, cx=size // 2, cy=size // 2,
                    stroke=pal.bg_bottom, stroke_w=max(4, size // 200))
    angle = rng.uniform(-7, 7)
    card = card.rotate(angle, resample=Image.BICUBIC, center=(size // 2, size // 2))
    img = Image.alpha_composite(img.convert("RGBA"), card).convert("RGB")
    # Körnung (rng-basiert statt Image.effect_noise → deterministisch bei seed)
    d = ImageDraw.Draw(img)
    for _ in range(size // 2):
        x, y = rng.randint(0, size - 1), rng.randint(0, size - 1)
        shade = rng.randint(0, 60)
        d.point((x, y), fill=(shade, shade, shade))
        if rng.random() < 0.3:
            d.point((min(x + 1, size - 1), y), fill=(shade, shade, shade))
    return img


def _tpl_bold_color(text: str, pal: Palette, size: int, rng: random.Random) -> Image.Image:
    """Farbblock + diagonaler Schnitt."""
    img = Image.new("RGB", (size, size), pal.bg_top)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (size, 0), (size, int(size * 0.42)), (0, int(size * 0.58))],
              fill=pal.accent)
    lines = _split_lines(text, 2)
    font = _fitted(img, max(lines, key=len), 0.74, 0.36)
    _draw_multiline(d, lines, font, color=pal.fg, cx=size // 2, cy=int(size * 0.52),
                    stroke=pal.bg_top, stroke_w=max(3, size // 250))
    return img


def _tpl_sticker_pop(text: str, pal: Palette, size: int, rng: random.Random) -> Image.Image:
    """Bunter Sticker-Ring."""
    img = Image.new("RGB", (size, size), (250, 250, 250))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r = int(size * 0.42)
    # gestreifter Ring
    segs = 18
    for i in range(segs):
        a0, a1 = i * 360 / segs, (i + 1) * 360 / segs
        color = pal.accent if i % 2 else pal.bg_bottom
        d.pieslice([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=color)
    r2 = int(r * 0.82)
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(255, 255, 255))
    lines = _split_lines(text, 2)
    font = _fitted(img, max(lines, key=len), 0.5, 0.34)
    _draw_multiline(d, lines, font, color=pal.bg_bottom, cx=cx, cy=cy)
    return img


_RENDERERS = {
    "bold_impact": _tpl_bold_impact,
    "vintage_retro": _tpl_vintage_retro,
    "neon_glow": _tpl_neon_glow,
    "minimalist_pro": _tpl_minimalist_pro,
    "split_dynamic": _tpl_split_dynamic,
    "quote_premium": _tpl_quote_premium,
    "grunge_street": _tpl_grunge_street,
    "bold_color": _tpl_bold_color,
    "sticker_pop": _tpl_sticker_pop,
}
