"""Text-Layout-Engine: 8 Text-Layouts auf bestehende Bilder zeichnen.

Layouts:
  speech_bubble:   Sprechblase
  thought_bubble:  Denkblase (gepunktet)
  banner_top:      Farbiger Streifen oben
  banner_bottom:   Farbiger Streifen unten
  stamp:           Runder Stempel-Look
  free_top:        Freitext oben
  free_bottom:     Freitext unten
  no_text:         Nur Illustration (kein Text)

Schriftstile: impact, bold, rounded, serif, light (siehe font_manager)
"""

from __future__ import annotations

from PIL import Image, ImageDraw

import font_manager

TEXT_LAYOUTS = (
    "speech_bubble", "thought_bubble", "banner_top", "banner_bottom",
    "stamp", "free_top", "free_bottom", "no_text",
)

# Layouts, die Text benötigen (für Validierung in der GUI)
LAYOUTS_WITH_TEXT = tuple(t for t in TEXT_LAYOUTS if t != "no_text")

_PADDING = 0.06  # relative Randbreite


def draw_text_layout(
    image: Image.Image,
    layout: str,
    text: str, *,
    style: str = "bold",
    text_color: tuple[int, int, int] = (255, 255, 255),
    accent_color: tuple[int, int, int] = (20, 20, 20),
) -> Image.Image:
    """Zeichnet Text im gewählten Layout auf das Bild (gibt Kopie zurück).

    no_text gibt das Bild unverändert zurück.
    """
    if layout not in TEXT_LAYOUTS:
        raise ValueError(f"Unbekanntes Layout {layout!r}. Erlaubt: {', '.join(TEXT_LAYOUTS)}")
    img = image.copy().convert("RGBA")
    if layout == "no_text" or not text.strip():
        return img.convert("RGB")

    draw = ImageDraw.Draw(img)

    if layout == "speech_bubble":
        _speech_bubble(draw, img, text, style, accent_color)
    elif layout == "thought_bubble":
        _thought_bubble(draw, img, text, style, accent_color)
    elif layout == "banner_top":
        _banner(draw, img, text, style, text_color=text_color, accent=accent_color, top=True)
    elif layout == "banner_bottom":
        _banner(draw, img, text, style, text_color=text_color, accent=accent_color, top=False)
    elif layout == "stamp":
        _stamp(draw, img, text, style, accent_color)
    elif layout == "free_top":
        _free_text(draw, img, text, style, text_color=text_color, top=True)
    elif layout == "free_bottom":
        _free_text(draw, img, text, style, text_color=text_color, top=False)

    return img.convert("RGB")


# ------------------------------------------------------------------ Helper
def _center_font(img: Image.Image, text: str, style: str, max_w: int,
                 max_h: int) -> font_manager.ImageFont.ImageFont:
    return font_manager.fit_font_size(style, text, max_w, max_h, start=min(img.size) // 3)


def _draw_centered(draw: ImageDraw.ImageDraw, text: str, font, *,
                   color, cx: int, cy: int, outline=None, outline_w: int = 0) -> None:
    tw, th = font_manager.text_size(font, text)
    x, y = cx - tw // 2, cy - th // 2
    if outline and outline_w:
        draw.text((x, y), text, font=font, fill=color,
                  stroke_width=outline_w, stroke_fill=outline)
    else:
        draw.text((x, y), text, font=font, fill=color)


def _speech_bubble(draw: ImageDraw.ImageDraw, img: Image.Image, text: str,
                   style: str, accent) -> None:
    w, h = img.size
    bw = int(w * 0.78)
    bh = int(h * 0.24)
    x0, y0 = (w - bw) // 2, int(h * 0.58)
    x1, y1 = x0 + bw, y0 + bh
    draw.rounded_rectangle([x0, y0, x1, y1], radius=bh // 3, fill=(255, 255, 255, 235),
                           outline=accent, width=max(4, w // 400))
    cx = w // 2
    draw.polygon([(cx - bw // 8, y1 - 2), (cx + bw // 8, y1 - 2),
                  (cx, y1 + bh // 3)], fill=(255, 255, 255, 235))
    font = _center_font(img, text, style, int(bw * 0.86), int(bh * 0.6))
    _draw_centered(draw, text, font, color=(10, 10, 10),
                   cx=(x0 + x1) // 2, cy=(y0 + y1) // 2)


def _thought_bubble(draw: ImageDraw.ImageDraw, img: Image.Image, text: str,
                    style: str, accent) -> None:
    w, h = img.size
    bw = int(w * 0.72)
    bh = int(h * 0.22)
    x0, y0 = (w - bw) // 2, int(h * 0.10)
    x1, y1 = x0 + bw, y0 + bh
    draw.ellipse([x0, y0, x1, y1], fill=(255, 255, 255, 235), outline=accent,
                 width=max(3, w // 500))
    cx = w // 2
    r = max(6, w // 150)
    for i, factor in enumerate((0.30, 0.42, 0.55)):
        cy = int(y1 + bh * factor)
        rr = int(r * (1.0 - i * 0.25))
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(255, 255, 255, 235))
    font = _center_font(img, text, style, int(bw * 0.72), int(bh * 0.5))
    _draw_centered(draw, text, font, color=(10, 10, 10),
                   cx=(x0 + x1) // 2, cy=(y0 + y1) // 2)


def _banner(draw: ImageDraw.ImageDraw, img: Image.Image, text: str, style: str, *,
            text_color, accent, top: bool) -> None:
    w, h = img.size
    bh = int(h * 0.20)
    y0 = int(h * 0.05) if top else h - bh - int(h * 0.05)
    x0, x1 = int(w * 0.08), int(w * 0.92)
    draw.rounded_rectangle([x0, y0, x1, y0 + bh], radius=bh // 6, fill=accent)
    font = _center_font(img, text, style, int((x1 - x0) * 0.9), int(bh * 0.62))
    _draw_centered(draw, text, font, color=text_color,
                   cx=(x0 + x1) // 2, cy=y0 + bh // 2)


def _stamp(draw: ImageDraw.ImageDraw, img: Image.Image, text: str, style: str,
           accent) -> None:
    w, h = img.size
    cx, cy = w // 2, h // 2
    r = int(min(w, h) * 0.30)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=accent, width=max(8, w // 150))
    r2 = int(r * 0.88)
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=accent, width=max(3, w // 400))
    font = _center_font(img, text, style, int(r * 1.3), int(r * 0.5))
    _draw_centered(draw, text, font, color=accent, cx=cx, cy=cy)


def _free_text(draw: ImageDraw.ImageDraw, img: Image.Image, text: str, style: str, *,
               text_color, top: bool) -> None:
    w, h = img.size
    max_w = int(w * 0.86)
    max_h = int(h * 0.16)
    font = _center_font(img, text, style, max_w, max_h)
    cy = int(h * 0.115) if top else int(h * 0.885)
    _draw_centered(draw, text, font, color=text_color,
                   cx=w // 2, cy=cy, outline=(0, 0, 0), outline_w=max(2, w // 500))
