"""Icon-Engine: geometrische Icons für Figuren & Objekte (Pillow, vektorartig).

Bekannte Figuren (25):
  pinguin, katze, hund, faultier, feuerwehrmann, krankenschwester, taucher,
  koch, polizist, astronaut, pirat, ninja, cowboy, roboter, alien, baer, fuchs,
  eule, frosch, panda, elefant, affe, loewe, einhorn, drache

Bekannte Objekte (21):
  eis, eiscreme, kaffee, coffee, pizza, laptop, computer, herz, heart, bier,
  beer, buch, book, handy, phone, gitarre, guitar, ball, donut, kuchen, cake

Alle Icons werden als RGBA-Bild mit transparentem Hintergrund erzeugt.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

FIGURES = (
    "pinguin", "katze", "hund", "faultier", "feuerwehrmann", "krankenschwester",
    "taucher", "koch", "polizist", "astronaut", "pirat", "ninja", "cowboy",
    "roboter", "alien", "baer", "fuchs", "eule", "frosch", "panda", "elefant",
    "affe", "loewe", "einhorn", "drache",
)

OBJECTS = (
    "eis", "eiscreme", "kaffee", "coffee", "pizza", "laptop", "computer",
    "herz", "heart", "bier", "beer", "buch", "book", "handy", "phone",
    "gitarre", "guitar", "ball", "donut", "kuchen", "cake",
)

KNOWN_ICONS = FIGURES + OBJECTS

# Aliase (deutsch -> dieselbe Zeichnung wie englisch bzw. Dubletten)
_ALIASES = {
    "eiscreme": "eis", "coffee": "kaffee", "heart": "herz", "beer": "bier",
    "book": "buch", "phone": "handy", "guitar": "gitarre", "cake": "kuchen",
}

_DARK = (35, 35, 40, 255)
_WHITE = (255, 255, 255, 255)


def _c(rgb: tuple[int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    return (rgb[0], rgb[1], rgb[2], alpha)


def draw_icon(name: str, size: int = 1000) -> Image.Image:
    """Erzeugt ein Icon als RGBA-Bild (transparent)."""
    name = name.lower().strip()
    name = _ALIASES.get(name, name)
    if name not in KNOWN_ICONS:
        raise ValueError(f"Unbekanntes Icon {name!r}. Erlaubt: {', '.join(KNOWN_ICONS)}")
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    drawer = _DRAWERS[name]
    drawer(d, size)
    return img


def is_known(name: str) -> bool:
    name = name.lower().strip()
    return name in KNOWN_ICONS or name in _ALIASES


# ------------------------------------------------------------------ Primitiven
def _ow(d: ImageDraw.ImageDraw, box, fill, *, outline=_DARK, w_f: float = 0.02) -> None:
    """Ellipse mit Outline (Breite relativ zur Icon-Größe)."""
    d.ellipse(box, fill=fill, outline=outline, width=max(2, int((box[2] - box[0]) * w_f)))


def _rw(d: ImageDraw.ImageDraw, box, fill, *, outline=_DARK, radius=None, w_f: float = 0.02) -> None:
    """Rechteck (rounded) mit Outline."""
    kwargs = {"fill": fill, "outline": outline, "width": max(2, int((box[2] - box[0]) * w_f))}
    if radius is not None:
        kwargs["radius"] = radius
    d.rounded_rectangle(box, **kwargs)


def _pw(d: ImageDraw.ImageDraw, pts, fill, *, outline=_DARK, w_f: float = 0.006, s: int = 1000) -> None:
    d.polygon(pts, fill=fill, outline=outline, width=max(2, int(s * w_f)))


def _eyes(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int, *,
          spread: float = 0.12, pupil_right: bool = True) -> None:
    """Zwei Augen mit Pupillen."""
    dx = int(r * spread * 4)
    for sx in (-dx, dx):
        _ow(d, (cx + sx - r // 3, cy - r // 3, cx + sx + r // 3, cy + r // 3), _WHITE, w_f=0.1)
        pr = r // 8
        px = cx + sx + (pr // 2 if pupil_right else -pr // 2)
        d.ellipse((px - pr, cy - pr, px + pr, cy + pr), fill=_DARK)


def _smile(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int) -> None:
    d.arc((cx - r, cy - r, cx + r, cy + r), start=20, end=160, fill=_DARK,
          width=max(3, r // 6))


# ------------------------------------------------------------------ Figuren
def _pinguin(d, S: int) -> None:
    _ow(d, (S * 0.2, S * 0.15, S * 0.8, S * 0.9), _c((30, 40, 60)))
    _ow(d, (S * 0.3, S * 0.35, S * 0.7, S * 0.88), _c((245, 245, 250)))
    _ow(d, (S * 0.3, S * 0.08, S * 0.7, S * 0.38), _c((30, 40, 60)))
    _eyes(d, S // 2, int(S * 0.24), int(S * 0.12))
    d.polygon([(S * 0.46, S * 0.28), (S * 0.54, S * 0.28), (S * 0.5, S * 0.35)],
              fill=_c((240, 140, 30)))
    _ow(d, (S * 0.12, S * 0.85, S * 0.34, S * 0.97), _c((240, 140, 30)))
    _ow(d, (S * 0.66, S * 0.85, S * 0.88, S * 0.97), _c((240, 140, 30)))


def _katze(d, S: int) -> None:
    _ow(d, (S * 0.15, S * 0.28, S * 0.85, S * 0.95), _c((250, 170, 90)))
    _pw(d, [(S * 0.2, S * 0.35), (S * 0.28, S * 0.05), (S * 0.45, S * 0.28)], _c((250, 170, 90)), s=S)
    _pw(d, [(S * 0.55, S * 0.28), (S * 0.72, S * 0.05), (S * 0.8, S * 0.35)], _c((250, 170, 90)), s=S)
    _ow(d, (S * 0.25, S * 0.12, S * 0.75, S * 0.55), _c((250, 170, 90)))
    _eyes(d, S // 2, int(S * 0.3), int(S * 0.13))
    _smile(d, S // 2, int(S * 0.42), int(S * 0.07))
    for _, dx in enumerate((-1, 0, 1)):
        d.line([(S * 0.5 + dx * S * 0.09, S * 0.42), (S * 0.5 + dx * S * 0.16, S * 0.40)],
               fill=_DARK, width=max(2, S // 200))
    _ow(d, (S * 0.84, S * 0.4, S * 1.0, S * 0.7), _c((250, 170, 90)))


def _hund(d, S: int) -> None:
    _ow(d, (S * 0.2, S * 0.15, S * 0.8, S * 0.9), _c((170, 120, 80)))
    _ow(d, (S * 0.08, S * 0.25, S * 0.3, S * 0.7), _c((140, 95, 60)))
    _ow(d, (S * 0.7, S * 0.25, S * 0.92, S * 0.7), _c((140, 95, 60)))
    _ow(d, (S * 0.28, S * 0.08, S * 0.72, S * 0.5), _c((170, 120, 80)))
    _ow(d, (S * 0.4, S * 0.34, S * 0.6, S * 0.55), _c((240, 200, 170)))
    _eyes(d, S // 2, int(S * 0.25), int(S * 0.1))
    d.ellipse((S * 0.45, S * 0.36, S * 0.55, S * 0.48), fill=_DARK)
    _smile(d, S // 2, int(S * 0.5), int(S * 0.06))


def _faultier(d, S: int) -> None:
    _ow(d, (S * 0.18, S * 0.22, S * 0.82, S * 0.92), _c((180, 150, 110)))
    _ow(d, (S * 0.3, S * 0.08, S * 0.7, S * 0.44), _c((200, 175, 135)))
    d.arc((S * 0.3, S * 0.18, S * 0.7, S * 0.5), 180, 360, fill=_c((120, 100, 70)),
          width=max(3, S // 120))
    _eyes(d, S // 2, int(S * 0.28), int(S * 0.12), pupil_right=False)
    d.line([(S * 0.3, S * 0.55), (S * 0.7, S * 0.55)], fill=_DARK, width=max(3, S // 150))
    _smile(d, S // 2, int(S * 0.6), int(S * 0.06))


def _feuerwehrmann(d, S: int) -> None:
    _rw(d, (S * 0.28, S * 0.42, S * 0.72, S * 0.92), _c((200, 60, 40)), radius=int(S * 0.08))
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.48), _c((245, 210, 175)))
    _ow(d, (S * 0.28, S * 0.02, S * 0.72, S * 0.18), _c((200, 60, 40)))
    d.rectangle((S * 0.1, S * 0.16, S * 0.9, S * 0.24), fill=_c((200, 60, 40)))
    _eyes(d, S // 2, int(S * 0.28), int(S * 0.1))
    _smile(d, S // 2, int(S * 0.4), int(S * 0.06))


def _krankenschwester(d, S: int) -> None:
    _rw(d, (S * 0.3, S * 0.44, S * 0.7, S * 0.92), _c((90, 160, 220)), radius=int(S * 0.08))
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.48), _c((248, 225, 205)))
    # Schwesternhaube mit rotem Kreuz
    _ow(d, (S * 0.32, S * 0.0, S * 0.68, S * 0.2), _WHITE)
    d.rectangle((S * 0.47, S * 0.04, S * 0.53, S * 0.16), fill=_c((220, 50, 60)))
    d.rectangle((S * 0.41, S * 0.07, S * 0.59, S * 0.13), fill=_c((220, 50, 60)))
    _eyes(d, S // 2, int(S * 0.3), int(S * 0.1))
    _smile(d, S // 2, int(S * 0.4), int(S * 0.06))


def _taucher(d, S: int) -> None:
    _rw(d, (S * 0.3, S * 0.42, S * 0.7, S * 0.9), _c((20, 30, 50)), radius=int(S * 0.08))
    _ow(d, (S * 0.28, S * 0.1, S * 0.72, S * 0.5), _c((235, 195, 160)))
    _ow(d, (S * 0.34, S * 0.2, S * 0.66, S * 0.42), _c((120, 200, 230)))
    _ow(d, (S * 0.4, S * 0.24, S * 0.52, S * 0.38), _WHITE)
    d.rectangle((S * 0.12, S * 0.55, S * 0.3, S * 0.75), fill=_c((240, 150, 40)))


def _koch(d, S: int) -> None:
    _rw(d, (S * 0.3, S * 0.44, S * 0.7, S * 0.92), _WHITE, radius=int(S * 0.08))
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.48), _c((240, 205, 175)))
    _rw(d, (S * 0.26, S * 0.0, S * 0.74, S * 0.2), _WHITE, radius=int(S * 0.09))
    _ow(d, (S * 0.18, S * 0.52, S * 0.82, S * 0.66), _c((220, 50, 60)))
    _eyes(d, S // 2, int(S * 0.3), int(S * 0.1))
    _smile(d, S // 2, int(S * 0.4), int(S * 0.06))
    d.ellipse((S * 0.44, S * 0.34, S * 0.56, S * 0.44), fill=_c((200, 110, 90)))


def _polizist(d, S: int) -> None:
    _rw(d, (S * 0.28, S * 0.42, S * 0.72, S * 0.92), _c((40, 60, 110)), radius=int(S * 0.08))
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.48), _c((240, 205, 175)))
    _pw(d, [(S * 0.26, S * 0.16), (S * 0.5, S * 0.02), (S * 0.74, S * 0.16),
            (S * 0.26, S * 0.16)], _c((30, 40, 80)), s=S)
    _ow(d, (S * 0.42, S * 0.04, S * 0.58, S * 0.16), _c((250, 200, 60)))
    _eyes(d, S // 2, int(S * 0.28), int(S * 0.1))
    _smile(d, S // 2, int(S * 0.4), int(S * 0.06))
    d.ellipse((S * 0.45, S * 0.75, S * 0.55, S * 0.83), fill=_c((250, 200, 60)))


def _astronaut(d, S: int) -> None:
    _rw(d, (S * 0.28, S * 0.4, S * 0.72, S * 0.92), _WHITE, radius=int(S * 0.08))
    _ow(d, (S * 0.26, S * 0.06, S * 0.74, S * 0.5), _WHITE)
    _ow(d, (S * 0.32, S * 0.14, S * 0.68, S * 0.44), _c((150, 220, 255)))
    _eyes(d, S // 2, int(S * 0.28), int(S * 0.09))
    _smile(d, S // 2, int(S * 0.36), int(S * 0.05))
    d.ellipse((S * 0.06, S * 0.5, S * 0.22, S * 0.66), fill=_c((220, 60, 60)))
    d.ellipse((S * 0.78, S * 0.5, S * 0.94, S * 0.66), fill=_c((220, 60, 60)))


def _pirat(d, S: int) -> None:
    _rw(d, (S * 0.28, S * 0.42, S * 0.72, S * 0.92), _c((120, 70, 40)), radius=int(S * 0.08))
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.48), _c((235, 190, 155)))
    _rw(d, (S * 0.2, S * 0.14, S * 0.8, S * 0.26), _DARK, radius=int(S * 0.03))
    _ow(d, (S * 0.36, S * 0.27, S * 0.5, S * 0.37), _WHITE)
    d.line([(S * 0.53, S * 0.28), (S * 0.63, S * 0.36)], fill=_DARK, width=max(3, S // 120))
    _smile(d, S // 2, int(S * 0.42), int(S * 0.05))


def _ninja(d, S: int) -> None:
    _rw(d, (S * 0.28, S * 0.42, S * 0.72, S * 0.92), _c((50, 50, 60)), radius=int(S * 0.08))
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.48), _c((40, 40, 48)))
    _rw(d, (S * 0.32, S * 0.26, S * 0.68, S * 0.34), _WHITE)
    d.rectangle((S * 0.1, S * 0.5, S * 0.9, S * 0.56), fill=_c((160, 30, 40)))


def _cowboy(d, S: int) -> None:
    _rw(d, (S * 0.28, S * 0.42, S * 0.72, S * 0.92), _c((90, 60, 140)), radius=int(S * 0.08))
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.48), _c((240, 200, 165)))
    d.ellipse((S * 0.1, S * 0.08, S * 0.9, S * 0.22), fill=_c((150, 100, 60)))
    _rw(d, (S * 0.38, S * 0.06, S * 0.62, S * 0.2), _c((150, 100, 60)), radius=int(S * 0.06))
    d.rectangle((S * 0.1, S * 0.16, S * 0.9, S * 0.22), fill=_c((90, 60, 35)))
    _eyes(d, S // 2, int(S * 0.3), int(S * 0.1))
    _smile(d, S // 2, int(S * 0.4), int(S * 0.06))


def _roboter(d, S: int) -> None:
    _rw(d, (S * 0.28, S * 0.42, S * 0.72, S * 0.92), _c((150, 160, 175)), radius=int(S * 0.06))
    _rw(d, (S * 0.28, S * 0.1, S * 0.72, S * 0.46), _c((180, 190, 200)), radius=int(S * 0.1))
    _ow(d, (S * 0.36, S * 0.2, S * 0.48, S * 0.34), _c((80, 220, 120)))
    _ow(d, (S * 0.52, S * 0.2, S * 0.64, S * 0.34), _c((80, 220, 120)))
    d.rectangle((S * 0.44, S * 0.36, S * 0.56, S * 0.4), fill=_DARK)
    d.line([(S * 0.5, S * 0.1), (S * 0.5, S * 0.02)], fill=_DARK, width=max(3, S // 100))
    d.ellipse((S * 0.46, S * 0.0, S * 0.54, S * 0.06), fill=_c((230, 70, 60)))


def _alien(d, S: int) -> None:
    _ow(d, (S * 0.22, S * 0.12, S * 0.78, S * 0.72), _c((110, 210, 120)))
    _ow(d, (S * 0.28, S * 0.7, S * 0.72, S * 0.95), _c((110, 210, 120)))
    _ow(d, (S * 0.34, S * 0.24, S * 0.46, S * 0.4), (10, 10, 10, 255))
    _ow(d, (S * 0.54, S * 0.24, S * 0.66, S * 0.4), (10, 10, 10, 255))
    _smile(d, S // 2, int(S * 0.5), int(S * 0.05))


def _baer(d, S: int) -> None:
    _ow(d, (S * 0.18, S * 0.25, S * 0.82, S * 0.92), _c((150, 105, 65)))
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.52), _c((150, 105, 65)))
    _ow(d, (S * 0.14, S * 0.02, S * 0.4, S * 0.26), _c((130, 88, 52)))
    _ow(d, (S * 0.6, S * 0.02, S * 0.86, S * 0.26), _c((130, 88, 52)))
    _ow(d, (S * 0.4, S * 0.38, S * 0.6, S * 0.52), _c((220, 180, 140)))
    _eyes(d, S // 2, int(S * 0.28), int(S * 0.1))
    _ow(d, (S * 0.46, S * 0.4, S * 0.54, S * 0.46), _DARK)
    _smile(d, S // 2, int(S * 0.48), int(S * 0.04))


def _fuchs(d, S: int) -> None:
    _pw(d, [(S * 0.1, S * 0.95), (S * 0.5, S * 0.25), (S * 0.9, S * 0.95)], _c((230, 120, 50)), s=S)
    _pw(d, [(S * 0.18, S * 0.28), (S * 0.32, S * 0.02), (S * 0.44, S * 0.26)], _c((230, 120, 50)), s=S)
    _pw(d, [(S * 0.56, S * 0.26), (S * 0.68, S * 0.02), (S * 0.82, S * 0.28)], _c((230, 120, 50)), s=S)
    _pw(d, [(S * 0.2, S * 0.95), (S * 0.5, S * 0.5), (S * 0.8, S * 0.95)], _WHITE, s=S)
    _eyes(d, S // 2, int(S * 0.5), int(S * 0.08))


def _eule(d, S: int) -> None:
    _ow(d, (S * 0.2, S * 0.12, S * 0.8, S * 0.94), _c((140, 100, 70)))
    _ow(d, (S * 0.3, S * 0.42, S * 0.7, S * 0.9), _c((200, 170, 130)))
    _ow(d, (S * 0.28, S * 0.14, S * 0.52, S * 0.38), _WHITE)
    _ow(d, (S * 0.48, S * 0.14, S * 0.72, S * 0.38), _WHITE)
    d.ellipse((S * 0.36, S * 0.22, S * 0.44, S * 0.3), fill=_DARK)
    d.ellipse((S * 0.56, S * 0.22, S * 0.64, S * 0.3), fill=_DARK)
    _pw(d, [(S * 0.5, S * 0.32), (S * 0.44, S * 0.42), (S * 0.56, S * 0.42)], _c((240, 150, 40)), s=S)
    _ow(d, (S * 0.08, S * 0.5, S * 0.24, S * 0.62), _c((140, 100, 70)))
    _ow(d, (S * 0.76, S * 0.5, S * 0.92, S * 0.62), _c((140, 100, 70)))


def _frosch(d, S: int) -> None:
    _ow(d, (S * 0.15, S * 0.3, S * 0.85, S * 0.95), _c((110, 190, 90)))
    _ow(d, (S * 0.05, S * 0.08, S * 0.42, S * 0.44), _c((110, 190, 90)))
    _ow(d, (S * 0.58, S * 0.08, S * 0.95, S * 0.44), _c((110, 190, 90)))
    d.ellipse((S * 0.16, S * 0.18, S * 0.3, S * 0.32), fill=_DARK)
    d.ellipse((S * 0.7, S * 0.18, S * 0.84, S * 0.32), fill=_DARK)
    _smile(d, S // 2, int(S * 0.58), int(S * 0.16))
    _ow(d, (S * 0.08, S * 0.9, S * 0.32, S * 0.98), _c((110, 190, 90)))
    _ow(d, (S * 0.68, S * 0.9, S * 0.92, S * 0.98), _c((110, 190, 90)))


def _panda(d, S: int) -> None:
    _ow(d, (S * 0.18, S * 0.25, S * 0.82, S * 0.92), _WHITE)
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.52), _WHITE)
    _ow(d, (S * 0.2, S * 0.02, S * 0.44, S * 0.24), _DARK)
    _ow(d, (S * 0.56, S * 0.02, S * 0.8, S * 0.24), _DARK)
    _ow(d, (S * 0.3, S * 0.24, S * 0.48, S * 0.4), _DARK)
    _ow(d, (S * 0.52, S * 0.24, S * 0.7, S * 0.4), _DARK)
    d.ellipse((S * 0.46, S * 0.4, S * 0.54, S * 0.47), fill=_DARK)
    _smile(d, S // 2, int(S * 0.5), int(S * 0.04))
    _ow(d, (S * 0.1, S * 0.6, S * 0.26, S * 0.78), _DARK)
    _ow(d, (S * 0.74, S * 0.6, S * 0.9, S * 0.78), _DARK)


def _elefant(d, S: int) -> None:
    _ow(d, (S * 0.2, S * 0.2, S * 0.8, S * 0.9), _c((150, 150, 170)))
    _ow(d, (S * 0.1, S * 0.3, S * 0.3, S * 0.7), _c((150, 150, 170)))
    _ow(d, (S * 0.7, S * 0.3, S * 0.9, S * 0.7), _c((150, 150, 170)))
    _ow(d, (S * 0.3, S * 0.05, S * 0.7, S * 0.45), _c((150, 150, 170)))
    d.line([(S * 0.5, S * 0.45), (S * 0.5, S * 0.75)], fill=_DARK, width=max(4, S // 90))
    _eyes(d, S // 2, int(S * 0.22), int(S * 0.09))


def _affe(d, S: int) -> None:
    _ow(d, (S * 0.18, S * 0.28, S * 0.82, S * 0.92), _c((150, 105, 70)))
    _ow(d, (S * 0.3, S * 0.1, S * 0.7, S * 0.52), _c((150, 105, 70)))
    _ow(d, (S * 0.36, S * 0.2, S * 0.64, S * 0.46), _c((225, 190, 155)))
    _eyes(d, S // 2, int(S * 0.3), int(S * 0.09))
    _smile(d, S // 2, int(S * 0.4), int(S * 0.05))
    _ow(d, (S * 0.22, S * 0.02, S * 0.4, S * 0.18), _c((225, 190, 155)))
    _ow(d, (S * 0.6, S * 0.02, S * 0.78, S * 0.18), _c((225, 190, 155)))


def _loewe(d, S: int) -> None:
    _ow(d, (S * 0.12, S * 0.12, S * 0.88, S * 0.88), _c((220, 160, 50)))
    _ow(d, (S * 0.26, S * 0.26, S * 0.74, S * 0.74), _c((245, 200, 110)))
    _eyes(d, S // 2, int(S * 0.44), int(S * 0.08))
    _ow(d, (S * 0.45, S * 0.52, S * 0.55, S * 0.6), _c((230, 170, 80)))
    _smile(d, S // 2, int(S * 0.58), int(S * 0.05))


def _einhorn(d, S: int) -> None:
    _ow(d, (S * 0.2, S * 0.3, S * 0.8, S * 0.95), _WHITE)
    _ow(d, (S * 0.28, S * 0.05, S * 0.72, S * 0.5), _WHITE)
    _eyes(d, S // 2, int(S * 0.24), int(S * 0.09))
    _pw(d, [(S * 0.46, S * 0.12), (S * 0.54, S * 0.12), (S * 0.5, S * -0.06)], _c((250, 180, 240)), s=S)
    _ow(d, (S * 0.14, S * 0.32, S * 0.24, S * 0.5), _c((250, 150, 200)))
    _ow(d, (S * 0.76, S * 0.32, S * 0.86, S * 0.5), _c((250, 150, 200)))


def _drache(d, S: int) -> None:
    _ow(d, (S * 0.25, S * 0.25, S * 0.75, S * 0.9), _c((70, 130, 80)))
    _ow(d, (S * 0.32, S * 0.08, S * 0.68, S * 0.46), _c((70, 130, 80)))
    _eyes(d, S // 2, int(S * 0.24), int(S * 0.09))
    _pw(d, [(S * 0.68, S * 0.2), (S * 0.95, S * 0.1), (S * 0.75, S * 0.4)], _c((70, 130, 80)), s=S)
    _pw(d, [(S * 0.35, S * 0.9), (S * 0.15, S * 0.75), (S * 0.25, S * 0.95)], _c((70, 130, 80)), s=S)
    _smile(d, S // 2, int(S * 0.38), int(S * 0.05))


# ------------------------------------------------------------------ Objekte
def _eis(d, S: int) -> None:
    _pw(d, [(S * 0.3, S * 0.55), (S * 0.7, S * 0.55), (S * 0.5, S * 0.98)], _c((225, 180, 130)), s=S)
    _ow(d, (S * 0.22, S * 0.08, S * 0.52, S * 0.5), _c((250, 170, 190)))
    _ow(d, (S * 0.42, S * 0.02, S * 0.72, S * 0.44), _c((150, 220, 190)))
    _ow(d, (S * 0.55, S * 0.12, S * 0.85, S * 0.54), _c((250, 220, 160)))
    _ow(d, (S * 0.42, S * 0.0, S * 0.5, S * 0.1), _c((200, 60, 60)))


def _kaffee(d, S: int) -> None:
    _rw(d, (S * 0.25, S * 0.35, S * 0.75, S * 0.9), _WHITE, radius=int(S * 0.06))
    d.arc((S * 0.68, S * 0.45, S * 0.95, S * 0.75), 270, 90, fill=_DARK, width=max(4, S // 80))
    _rw(d, (S * 0.3, S * 0.4, S * 0.7, S * 0.55), _c((110, 70, 40)), radius=int(S * 0.04))
    for i, x in enumerate((S * 0.42, S * 0.52)):
        d.arc((x, S * 0.12 + i * S * 0.05, x + S * 0.08, S * 0.4 + i * S * 0.05),
              180, 360, fill=(200, 200, 210, 160), width=max(3, S // 150))


def _pizza(d, S: int) -> None:
    _pw(d, [(S * 0.5, S * 0.05), (S * 0.08, S * 0.9), (S * 0.92, S * 0.9)],
        _c((240, 190, 90)), s=S)
    d.line([(S * 0.5, S * 0.05), (S * 0.08, S * 0.9)], fill=_DARK, width=max(3, S // 100))
    d.line([(S * 0.5, S * 0.05), (S * 0.92, S * 0.9)], fill=_DARK, width=max(3, S // 100))
    for x, y, r in ((S * 0.4, S * 0.45, S * 0.05), (S * 0.6, S * 0.55, S * 0.05),
                    (S * 0.5, S * 0.72, S * 0.05), (S * 0.32, S * 0.68, S * 0.045),
                    (S * 0.68, S * 0.75, S * 0.045)):
        _ow(d, (x - r, y - r, x + r, y + r), _c((210, 90, 70)))


def _laptop(d, S: int) -> None:
    _rw(d, (S * 0.2, S * 0.15, S * 0.8, S * 0.65), _c((70, 80, 100)), radius=int(S * 0.03))
    _rw(d, (S * 0.24, S * 0.19, S * 0.76, S * 0.61), _c((90, 200, 250)), radius=int(S * 0.02))
    _pw(d, [(S * 0.1, S * 0.65), (S * 0.9, S * 0.65), (S * 0.82, S * 0.85),
            (S * 0.18, S * 0.85)], _c((90, 100, 120)), s=S)


def _computer(d, S: int) -> None:
    _rw(d, (S * 0.15, S * 0.1, S * 0.85, S * 0.65), _c((60, 65, 85)), radius=int(S * 0.04))
    _rw(d, (S * 0.2, S * 0.15, S * 0.8, S * 0.6), _c((90, 200, 250)), radius=int(S * 0.02))
    _rw(d, (S * 0.4, S * 0.65, S * 0.6, S * 0.8), _c((80, 85, 105)))
    _rw(d, (S * 0.22, S * 0.8, S * 0.78, S * 0.9), _c((60, 65, 85)), radius=int(S * 0.04))


def _herz(d, S: int) -> None:
    color = _c((230, 60, 90))
    _pw(d, [(S * 0.5, S * 0.92), (S * 0.06, S * 0.45), (S * 0.06, S * 0.25),
            (S * 0.2, S * 0.08), (S * 0.38, S * 0.1), (S * 0.5, S * 0.28),
            (S * 0.62, S * 0.1), (S * 0.8, S * 0.08), (S * 0.94, S * 0.25),
            (S * 0.94, S * 0.45)], color, s=S)
    _ow(d, (S * 0.24, S * 0.2, S * 0.36, S * 0.34), (255, 255, 255, 120), outline=None)


def _bier(d, S: int) -> None:
    _pw(d, [(S * 0.28, S * 0.3), (S * 0.72, S * 0.3), (S * 0.66, S * 0.95),
            (S * 0.34, S * 0.95)], _c((250, 200, 60)), s=S)
    _pw(d, [(S * 0.28, S * 0.3), (S * 0.72, S * 0.3), (S * 0.7, S * 0.5),
            (S * 0.3, S * 0.5)], _WHITE, s=S)
    _ow(d, (S * 0.2, S * 0.05, S * 0.8, S * 0.4), _c((250, 200, 60)))
    _ow(d, (S * 0.35, S * 0.0, S * 0.65, S * 0.3), (255, 255, 255, 200))


def _buch(d, S: int) -> None:
    _pw(d, [(S * 0.5, S * 0.15), (S * 0.12, S * 0.08), (S * 0.12, S * 0.9),
            (S * 0.5, S * 0.96)], _c((190, 60, 60)), s=S)
    _pw(d, [(S * 0.5, S * 0.15), (S * 0.88, S * 0.08), (S * 0.88, S * 0.9),
            (S * 0.5, S * 0.96)], _c((210, 80, 70)), s=S)
    d.line([(S * 0.5, S * 0.15), (S * 0.5, S * 0.96)], fill=_DARK, width=max(4, S // 100))
    d.line([(S * 0.24, S * 0.3), (S * 0.4, S * 0.33)], fill=(255, 255, 255, 180),
           width=max(3, S // 150))
    d.line([(S * 0.24, S * 0.45), (S * 0.4, S * 0.48)], fill=(255, 255, 255, 180),
           width=max(3, S // 150))


def _handy(d, S: int) -> None:
    _rw(d, (S * 0.3, S * 0.05, S * 0.7, S * 0.95), _c((40, 45, 60)), radius=int(S * 0.08))
    _rw(d, (S * 0.33, S * 0.12, S * 0.67, S * 0.82), _c((120, 210, 240)), radius=int(S * 0.03))
    _ow(d, (S * 0.46, S * 0.84, S * 0.54, S * 0.9), _c((90, 95, 110)))


def _gitarre(d, S: int) -> None:
    _ow(d, (S * 0.2, S * 0.5, S * 0.8, S * 0.98), _c((200, 140, 60)))
    _ow(d, (S * 0.32, S * 0.62, S * 0.68, S * 0.9), _c((160, 90, 40)))
    _ow(d, (S * 0.44, S * 0.72, S * 0.56, S * 0.82), _DARK)
    _rw(d, (S * 0.44, S * 0.02, S * 0.56, S * 0.6), _c((120, 75, 40)), radius=int(S * 0.02))
    d.rectangle((S * 0.47, S * 0.05, S * 0.53, S * 0.12), fill=_WHITE)


def _ball(d, S: int) -> None:
    _ow(d, (S * 0.1, S * 0.1, S * 0.9, S * 0.9), _WHITE)
    d.polygon([(S * 0.5, S * 0.28), (S * 0.38, S * 0.55), (S * 0.62, S * 0.55)], fill=_DARK)
    for x, y in ((S * 0.5, S * 0.18), (S * 0.25, S * 0.6), (S * 0.75, S * 0.6)):
        _ow(d, (x - S * 0.05, y - S * 0.05, x + S * 0.05, y + S * 0.05), _DARK)
    d.arc((S * 0.1, S * 0.55, S * 0.9, S * 1.1), 200, 340, fill=_DARK, width=max(4, S // 90))


def _donut(d, S: int) -> None:
    _ow(d, (S * 0.1, S * 0.1, S * 0.9, S * 0.9), _c((235, 180, 120)))
    _ow(d, (S * 0.16, S * 0.16, S * 0.84, S * 0.84), _c((250, 170, 200)))
    for x, y in ((S * 0.3, S * 0.3), (S * 0.65, S * 0.28), (S * 0.3, S * 0.68),
                 (S * 0.68, S * 0.65), (S * 0.5, S * 0.48)):
        _ow(d, (x - S * 0.035, y - S * 0.035, x + S * 0.035, y + S * 0.035), _WHITE)
    _ow(d, (S * 0.4, S * 0.4, S * 0.6, S * 0.6), (0, 0, 0, 0), outline=None)


def _kuchen(d, S: int) -> None:
    _rw(d, (S * 0.15, S * 0.45, S * 0.85, S * 0.9), _c((250, 200, 140)), radius=int(S * 0.03))
    _rw(d, (S * 0.15, S * 0.38, S * 0.85, S * 0.55), _c((240, 150, 190)), radius=int(S * 0.05))
    for x in (S * 0.3, S * 0.5, S * 0.7):
        _ow(d, (x - S * 0.05, S * 0.18, x + S * 0.05, S * 0.38), _c((230, 60, 70)))
        d.line([(x, S * 0.22), (x, S * 0.3)], fill=_WHITE, width=max(2, S // 200))


_DRAWERS = {
    "pinguin": _pinguin, "katze": _katze, "hund": _hund, "faultier": _faultier,
    "feuerwehrmann": _feuerwehrmann, "krankenschwester": _krankenschwester,
    "taucher": _taucher, "koch": _koch, "polizist": _polizist, "astronaut": _astronaut,
    "pirat": _pirat, "ninja": _ninja, "cowboy": _cowboy, "roboter": _roboter,
    "alien": _alien, "baer": _baer, "fuchs": _fuchs, "eule": _eule, "frosch": _frosch,
    "panda": _panda, "elefant": _elefant, "affe": _affe, "loewe": _loewe,
    "einhorn": _einhorn, "drache": _drache,
    "eis": _eis, "kaffee": _kaffee, "pizza": _pizza, "laptop": _laptop,
    "computer": _computer, "herz": _herz, "bier": _bier, "buch": _buch,
    "handy": _handy, "gitarre": _gitarre, "ball": _ball, "donut": _donut,
    "kuchen": _kuchen,
}
