"""Mockup-Engine: T-Shirt-Mockups mit Design-Platzierung + Branding.

- 4 Shirt-Farben: black, white, navy, gray
- Design auf Brust-Bereich platziert
- Zeichenwerk-Branding unten rechts
- 1200x1400 Pixel
"""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw

import config
import font_manager

logger = logging.getLogger("genesis.mockup")

MOCKUP_SIZE = (1200, 1400)  # w, h

SHIRT_COLORS: dict[str, tuple[int, int, int]] = {
    "black": (28, 28, 30),
    "white": (242, 242, 240),
    "navy": (30, 42, 82),
    "gray": (150, 150, 155),
}

SHIRT_NAMES = {
    "black": "Schwarz", "white": "Weiß", "navy": "Navy", "gray": "Grau",
}


def _draw_shirt(color: tuple[int, int, int]) -> Image.Image:
    """Zeichnet ein stilisiertes T-Shirt."""
    w, h = MOCKUP_SIZE
    img = Image.new("RGB", (w, h), (250, 250, 250))
    d = ImageDraw.Draw(img)
    shade = tuple(max(0, c - 25) for c in color)
    highlight = tuple(min(255, c + 20) for c in color)

    # Körper
    d.rounded_rectangle([int(w * 0.22), int(h * 0.16), int(w * 0.78), int(h * 0.94)],
                        radius=int(w * 0.06), fill=color)
    # Ärmel
    d.polygon([(int(w * 0.24), int(h * 0.20)), (int(w * 0.06), int(h * 0.34)),
               (int(w * 0.12), int(h * 0.48)), (int(w * 0.25), int(h * 0.34))],
              fill=shade)
    d.polygon([(int(w * 0.76), int(h * 0.20)), (int(w * 0.94), int(h * 0.34)),
               (int(w * 0.88), int(h * 0.48)), (int(w * 0.75), int(h * 0.34))],
              fill=shade)
    # Kragen
    d.ellipse([int(w * 0.40), int(h * 0.10), int(w * 0.60), int(h * 0.24)],
              fill=shade, outline=highlight, width=4)
    # Falten angedeutet
    d.line([(int(w * 0.26), int(h * 0.45)), (int(w * 0.35), int(h * 0.70))],
           fill=shade, width=6)
    d.line([(int(w * 0.74), int(h * 0.45)), (int(w * 0.65), int(h * 0.70))],
           fill=shade, width=6)
    return img


def create_mockup(
    design: Image.Image,
    shirt_color: str = "black",
    out_path: Path | None = None,
    design_scale: float = 0.46,
) -> Image.Image:
    """Setzt ein Design auf ein Shirt. Gibt das Mockup zurück (optional mit Save)."""
    if shirt_color not in SHIRT_COLORS:
        raise ValueError(f"Unbekannte Shirt-Farbe {shirt_color!r}. "
                         f"Erlaubt: {', '.join(SHIRT_COLORS)}")
    w, h = MOCKUP_SIZE
    img = _draw_shirt(SHIRT_COLORS[shirt_color])

    # Design auf Brust skaliert (leicht perspektivisch schmaler unten wirkt nicht
    # glaubwürdig bei stilisiertem Shirt → simple Zentrierung)
    dw = int(w * design_scale)
    dh = int(design.size[1] * (dw / max(design.size[0], 1)))
    dh = min(dh, int(h * 0.5))
    dw_final = int(design.size[0] * (dh / max(design.size[1], 1)))
    thumb = design.convert("RGBA").resize((dw_final, dh), Image.LANCZOS)
    img.paste(thumb, ((w - dw_final) // 2, int(h * 0.30)), thumb)

    # Branding unten rechts
    d = ImageDraw.Draw(img)
    font = font_manager.get_font("bold", max(16, w // 45))
    brand = "ZEICHENWERK"
    tw, th = font_manager.text_size(font, brand)
    x, y = w - tw - int(w * 0.04), h - th - int(h * 0.025)
    d.text((x + 2, y + 2), brand, font=font, fill=(120, 120, 120))
    d.text((x, y), brand, font=font, fill=(90, 90, 90))

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "PNG", optimize=True)
        logger.info("Mockup gespeichert: %s", out_path.name)
    return img


def create_mockup_set(design: Image.Image, out_dir: Path | None = None,
                      prefix: str = "design") -> list[Path]:
    """Erzeugt Mockups in allen 4 Farben."""
    out_dir = out_dir or config.MOCKUPS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for color in SHIRT_COLORS:
        p = out_dir / f"{prefix}_mockup_{color}.png"
        create_mockup(design, color, p)
        paths.append(p)
    return paths
