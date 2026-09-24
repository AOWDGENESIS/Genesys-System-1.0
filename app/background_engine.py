"""Background-Engine: 15 Hintergründe + 4 Muster-Overlays.

Hintergründe (15):
  pastel_warm, pastel_cool, pastel_green, pastel_pink,
  sunny, sky, sunset, ocean, forest,
  night, neon_dark, vintage_warm,
  clean_white, clean_cream, clean_black

Muster (Overlay):
  polka_dots, stripes_h, stripes_v, stars, confetti
"""

from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

BACKGROUNDS = (
    "pastel_warm", "pastel_cool", "pastel_green", "pastel_pink",
    "sunny", "sky", "sunset", "ocean", "forest",
    "night", "neon_dark", "vintage_warm",
    "clean_white", "clean_cream", "clean_black",
)

PATTERNS = ("polka_dots", "stripes_h", "stripes_v", "stars", "confetti")

# (Farbverlauf oben RGB, unten RGB)
_GRADIENTS: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    "pastel_warm":    ((255, 236, 210), (255, 205, 178)),
    "pastel_cool":    ((214, 234, 248), (190, 218, 240)),
    "pastel_green":   ((219, 242, 219), (188, 230, 193)),
    "pastel_pink":    ((255, 226, 236), (250, 200, 220)),
    "sunny":          ((255, 234, 0), (255, 140, 0)),
    "sky":            ((120, 190, 255), (210, 240, 255)),
    "sunset":         ((255, 94, 77), (255, 200, 100)),
    "ocean":          ((8, 68, 130), (60, 150, 200)),
    "forest":         ((16, 74, 44), (88, 158, 92)),
    "night":          ((8, 10, 30), (40, 46, 90)),
    "neon_dark":      ((12, 0, 30), (60, 0, 90)),
    "vintage_warm":   ((240, 220, 180), (200, 170, 120)),
    "clean_white":    ((255, 255, 255), (245, 245, 245)),
    "clean_cream":    ((255, 250, 235), (248, 236, 210)),
    "clean_black":    ((10, 10, 10), (30, 30, 30)),
}

_PATTERN_COLORS: dict[str, tuple[int, int, int, int]] = {
    # Hintergrund: Pattern-Farbe RGBA
    "pastel_warm": (214, 120, 90, 55),
    "pastel_cool": (60, 120, 180, 55),
    "pastel_green": (40, 130, 60, 55),
    "pastel_pink": (210, 80, 140, 55),
    "sunny": (255, 255, 255, 70),
    "sky": (255, 255, 255, 90),
    "sunset": (90, 30, 80, 70),
    "ocean": (255, 255, 255, 45),
    "forest": (255, 255, 255, 40),
    "night": (255, 255, 255, 45),
    "neon_dark": (255, 0, 190, 70),
    "vintage_warm": (150, 110, 60, 60),
    "clean_white": (0, 0, 0, 30),
    "clean_cream": (170, 130, 80, 40),
    "clean_black": (255, 255, 255, 35),
}


def create_background(name: str, size: int = 2000, pattern: str | None = None,
                      rng: random.Random | None = None) -> Image.Image:
    """Erzeugt einen Hintergrund (optional mit Muster-Overlay)."""
    rng = rng or random
    if name not in _GRADIENTS:
        raise ValueError(f"Unbekannter Hintergrund {name!r}. Erlaubt: {', '.join(BACKGROUNDS)}")
    top, bottom = _GRADIENTS[name]

    img = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(img)
    for y in range(size):
        t = y / max(size - 1, 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (size, y)], fill=color)

    if pattern:
        if pattern not in PATTERNS:
            raise ValueError(f"Unbekanntes Muster {pattern!r}. Erlaubt: {', '.join(PATTERNS)}")
        _apply_pattern(img, name, pattern, rng)
    return img


def _apply_pattern(img: Image.Image, bg_name: str, pattern: str,
                   rng: random.Random) -> None:
    """Zeichnet das Muster als halbtransparentes Overlay."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    color = _PATTERN_COLORS.get(bg_name, (255, 255, 255, 50))
    w, h = img.size
    step = max(w // 12, 20)
    r = max(step // 6, 6)

    if pattern == "polka_dots":
        offset = False
        for y in range(step // 2, h, step):
            for x in range(step // 2, w, step):
                dx = x + (step // 2 if offset else 0)
                draw.ellipse([dx - r, y - r, dx + r, y + r], fill=color)
            offset = not offset

    elif pattern == "stripes_h":
        for i, y in enumerate(range(0, h, step)):
            if i % 2 == 0:
                draw.rectangle([0, y, w, y + step // 2], fill=color)

    elif pattern == "stripes_v":
        for i, x in enumerate(range(0, w, step)):
            if i % 2 == 0:
                draw.rectangle([x, 0, x + step // 2, h], fill=color)

    elif pattern == "stars":
        for _ in range(28):
            cx, cy = rng.randint(0, w), rng.randint(0, h)
            _star(draw, cx, cy, rng.randint(step // 5, step // 3), color)

    elif pattern == "confetti":
        palette = [color, (255, 200, 60, 160), (60, 180, 255, 160),
                   (255, 100, 140, 160), (90, 230, 160, 160)]
        for _ in range(140):
            cx, cy = rng.randint(0, w), rng.randint(0, h)
            s = rng.randint(step // 12, step // 7)
            c = rng.choice(palette)
            for _rot in range(3):
                draw.rectangle(
                    [cx - s, cy - s // 2, cx + s, cy + s // 2], fill=c,
                )
                cx += s
                cy += rng.randint(-s, s)

    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))


def _star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int,
          color: tuple[int, int, int, int], *, points: int = 5) -> None:
    coords: list[tuple[float, float]] = []
    for i in range(points * 2):
        radius = r if i % 2 == 0 else r * 0.45
        angle = math.pi * i / points - math.pi / 2
        coords.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    draw.polygon(coords, fill=color)


def random_background(rng: random.Random | None = None) -> str:
    """Zufälliger Hintergrund-Name."""
    rng = rng or random
    return rng.choice(BACKGROUNDS)


def random_pattern(rng: random.Random | None = None) -> str | None:
    """Zufälliges Muster (oder None = kein Muster)."""
    rng = rng or random
    return rng.choice([None, *PATTERNS])  # type: ignore[return-value]
