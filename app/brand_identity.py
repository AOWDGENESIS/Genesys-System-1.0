"""Zeichenwerk Brand-Daten (Name, Slogans, Bios, Keywords, Plattformen)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:
    key: str
    name: str
    active: bool
    upload_url: str
    max_tags: int
    min_size_px: int
    format_hint: str


REDBUBBLE = Platform(
    key="redbubble", name="Redbubble", active=True,
    upload_url="https://www.redbubble.com/portfolio/new_work",
    max_tags=15, min_size_px=1500, format_hint="PNG (transparent) oder JPG, RGB",
)
TEEPUBLIC = Platform(
    key="teepublic", name="TeePublic", active=True,
    upload_url="https://www.teepublic.com/dashboard/designs/new",
    max_tags=20, min_size_px=1500, format_hint="PNG transparent bevorzugt",
)
SPREADSHIRT = Platform(
    key="spreadshirt", name="Spreadshirt", active=True,
    upload_url="https://partner.spreadshirt.de/designs/new",
    max_tags=25, min_size_px=2000, format_hint="PNG transparent Pflicht, DE+EN Tags",
)
MERCH_AMAZON = Platform(
    key="merch_amazon", name="Merch Amazon", active=False,
    upload_url="https://merch.amazon.com/dashboard",
    max_tags=15, min_size_px=4500, format_hint="Vorbereitet, nicht aktiv",
)

PLATFORMS: dict[str, Platform] = {
    p.key: p for p in (REDBUBBLE, TEEPUBLIC, SPREADSHIRT, MERCH_AMAZON)
}

BRAND_NAME = "Zeichenwerk"
SLOGAN_DE = "Zeichen setzen. Jeden Tag."
SLOGAN_EN = "Bold designs for bold people."

BIO_EN = (
    "Bold designs, dry humor and wearable attitude. "
    "From minimal to statement graphics — Zeichenwerk creates designs that speak."
)
BIO_DE = (
    "Zeichenwerk steht für ausdrucksstarke Designs mit Haltung. "
    "Von Humor bis Aussage, von minimal bis markant."
)

BRAND_KEYWORDS: list[str] = [
    "zeichenwerk", "statement shirt", "graphic design", "humor shirt",
    "typography", "wearable art", "minimal design", "bold style",
    "sarcasm shirt", "retro design",
]

# Tags, die automatisch zu Upload-Metadaten hinzugefügt werden (max. 3)
AUTO_BRAND_TAGS: list[str] = ["zeichenwerk", "typography", "bold design"]

PLATFORM_GUIDELINES: dict[str, str] = {
    "redbubble": (
        "Redbubble: Min. 1500px, empfohlen 3500px+. PNG (transparent) oder JPG, RGB. "
        "Titel max. 60 Zeichen, Keyword zuerst. Tags max. 15, kommagetrennt. "
        "Beschreibung 1-3 Sätze. Verboten: Marken, Hate, Gewalt, Politik. "
        "Tipp: Design auf hell UND dunkel testen."
    ),
    "teepublic": (
        "TeePublic: Min. 1500px, empfohlen 4000px. Tags max. 20. "
        "PNG transparent bevorzugt."
    ),
    "spreadshirt": (
        "Spreadshirt: Min. 2000px. PNG transparent Pflicht. "
        "Deutsche und englische Tags verwenden."
    ),
}


def active_platforms() -> list[Platform]:
    """Liefert alle aktiven Plattformen."""
    return [p for p in PLATFORMS.values() if p.active]
