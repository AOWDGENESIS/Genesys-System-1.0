"""Font-Manager: plattformübergreifende Schrift-Auflösung für 5 Schriftstile.

Stile (wie in der Spezifikation):
  impact   Impact / Ultra-Bold
  bold     Arial Bold / Calibri Bold
  rounded  Comic Sans / Trebuchet Bold
  serif    Georgia / Times New Roman
  light    Arial / Calibri (dünn)

Verbesserung gegenüber V1: Läuft auf Windows, Linux und macOS —
kandidaten werden systematisch gesucht, mit DejaVu/Liberation-Fallback.
"""

from __future__ import annotations

import logging
import sys
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

logger = logging.getLogger("genesis.fonts")

FONT_STYLES = ("impact", "bold", "rounded", "serif", "light")

# Kandidaten pro Stil (Dateinamen ohne Pfad, Reihenfolge = Priorität)
_CANDIDATES: dict[str, list[str]] = {
    "impact": [
        "impact.ttf", "Impact.ttf", "anton.ttf",
        "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf",
    ],
    "bold": [
        "arialbd.ttf", "Arial_Bold.ttf", "CalibriBold.ttf",
        "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf",
    ],
    "rounded": [
        "comicbd.ttf", "ComicSansMS-Bold.ttf", "trebuchetbold.ttf", "Trebuchet MS Bold.ttf",
        "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf",
    ],
    "serif": [
        "georgia.ttf", "Georgia.ttf", "times.ttf", "Times New Roman.ttf",
        "LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf", "DejaVuSerif.ttf",
    ],
    "light": [
        "arial.ttf", "Arial.ttf", "calibri.ttf", "Calibri-Regular.ttf",
        "LiberationSans-Regular.ttf", "DejaVuSans.ttf",
    ],
}

_FONT_DIRS: list[Path] = []
if sys.platform == "win32":
    _FONT_DIRS += [Path("C:/Windows/Fonts"), Path("C:/WinNT/Fonts")]
elif sys.platform == "darwin":
    _FONT_DIRS += [
        Path("/Library/Fonts"), Path("/System/Library/Fonts"),
        Path.home() / "Library" / "Fonts",
    ]
_FONT_DIRS += [
    Path("/usr/share/fonts/truetype"), Path("/usr/local/share/fonts"),
    Path.home() / ".fonts",
    Path(__file__).resolve().parent / "fonts",
]


@lru_cache(maxsize=64)
def _find_font_file(style: str) -> Path | None:
    """Sucht eine existierende Font-Datei für den Stil (cached)."""
    for candidate in _CANDIDATES.get(style, []):
        # 1) direkter Pfad vs. Font-Dirs
        for d in _FONT_DIRS:
            p = d / candidate
            if p.exists():
                return p
        # 2) rekursive Suche in den Font-Basen
        for base in _FONT_DIRS:
            if not base.exists():
                continue
            for hit in base.rglob(candidate):
                return hit
    return None


def available_styles() -> list[str]:
    return list(FONT_STYLES)


def has_style(style: str) -> bool:
    return _find_font_file(style.lower()) is not None


def get_font(style: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Lädt den Font für einen Stil; Fallback = PIL-Default-Bitmap-Font."""
    style = style.lower()
    if style not in _CANDIDATES:
        style = "bold"
    path = _find_font_file(style)
    if path:
        try:
            return ImageFont.truetype(str(path), size)
        except OSError as exc:  # beschädigte Datei
            logger.warning("Font %s nicht ladbar (%s), nutze Fallback.", path.name, exc)
    return ImageFont.load_default()


def text_bbox(font: ImageFont.ImageFont, text: str) -> tuple[int, int, int, int]:
    """Einheitliche Text-BBox (linken/oberen Rand ignorierend)."""
    box = font.getbbox(text)
    return box


def text_size(font: ImageFont.ImageFont, text: str) -> tuple[int, int]:
    """Text-Breite/-Höhe in Pixeln."""
    box = font.getbbox(text)
    return box[2] - box[0], box[3] - box[1]


def fit_font_size(style: str, text: str, max_width: int, max_height: int, *,
                  start: int = 400, minimum: int = 24) -> ImageFont.ImageFont:
    """Findet die größte Schriftgröße, bei der der Text in die Box passt."""
    size = start
    while size > minimum:
        font = get_font(style, size)
        w, h = text_size(font, text)
        if w <= max_width and h <= max_height:
            return font
        size = int(size * 0.9)
    return get_font(style, minimum)
