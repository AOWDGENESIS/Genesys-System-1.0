"""Produkt-Formate: 7 Ausgabeformate mit Resize/Pad-Logik.

  tshirt:    2000x2000  T-Shirt quadratisch
  poster:    3000x4000  Hochformat Poster
  sticker:   1400x1400  Sticker quadratisch
  mug:       2400x1000  Tassen-Design breit
  phone:     1080x1920  Handyhülle Hochformat
  pdf_a4:    2480x3508  A4 Druckformat 300dpi
  social:    1080x1080  Instagram / Social Post
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

import background_engine


@dataclass(frozen=True)
class ProductFormat:
    key: str
    name_de: str
    width: int
    height: int
    background: str  # Füll-Hintergrund beim Padden

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)


PRODUCT_FORMATS: dict[str, ProductFormat] = {
    f.key: f for f in (
        ProductFormat("tshirt", "T-Shirt quadratisch", 2000, 2000, "clean_white"),
        ProductFormat("poster", "Hochformat Poster", 3000, 4000, "clean_white"),
        ProductFormat("sticker", "Sticker quadratisch", 1400, 1400, "clean_white"),
        ProductFormat("mug", "Tassen-Design breit", 2400, 1000, "clean_white"),
        ProductFormat("phone", "Handyhülle Hochformat", 1080, 1920, "clean_black"),
        ProductFormat("pdf_a4", "A4 Druckformat 300dpi", 2480, 3508, "clean_white"),
        ProductFormat("social", "Instagram / Social Post", 1080, 1080, "clean_white"),
    )
}


def get_format(key: str) -> ProductFormat:
    if key not in PRODUCT_FORMATS:
        raise ValueError(f"Unbekanntes Format {key!r}. Erlaubt: {', '.join(PRODUCT_FORMATS)}")
    return PRODUCT_FORMATS[key]


def export_for_product(
    design: Image.Image,
    product_key: str,
    out_path: Path,
    pad_mode: str = "contain",
) -> Path:
    """Exportiert ein Design in ein Produktformat.

    pad_mode:
      contain — Design komplett sichtbar, Rest wird aufgefüllt
      cover   — Design füllt Fläche, Rand wird beschnitten
    """
    fmt = get_format(product_key)
    if pad_mode not in ("contain", "cover"):
        raise ValueError(f"Unbekannter pad_mode {pad_mode!r}")

    design = design.convert("RGB")
    if pad_mode == "cover":
        result = _cover(design, fmt.size)
    else:
        bg = background_engine.create_background(fmt.background, 2).resize(fmt.size)
        result = bg
        fitted = _contain(design, fmt.size)
        result.paste(fitted, ((fmt.width - fitted.width) // 2,
                              (fmt.height - fitted.height) // 2))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path, "PNG", optimize=True)
    return out_path


def _contain(img: Image.Image, box: tuple[int, int]) -> Image.Image:
    w, h = img.size
    scale = min(box[0] / w, box[1] / h)
    return img.resize((max(1, int(w * scale)), max(1, int(h * scale))),
                      Image.LANCZOS)


def _cover(img: Image.Image, box: tuple[int, int]) -> Image.Image:
    w, h = img.size
    scale = max(box[0] / w, box[1] / h)
    resized = img.resize((max(1, int(w * scale)), max(1, int(h * scale))),
                         Image.LANCZOS)
    x = (resized.width - box[0]) // 2
    y = (resized.height - box[1]) // 2
    return resized.crop((x, y, x + box[0], y + box[1]))


def validate_for_platform(design: Image.Image, min_size_px: int) -> list[str]:
    """Prüft, ob ein Design die Plattform-Mindestgröße erfüllt. Gibt Probleme zurück."""
    problems: list[str] = []
    w, h = design.size
    if min(w, h) < min_size_px:
        problems.append(
            f"Zu klein: {w}x{h} (Minimum {min_size_px}px auf der kürzeren Seite)"
        )
    return problems
