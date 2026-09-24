"""Scene-Engine: Cartoon-Szenen aus bekannten Figuren + Objekten + Humor-Texten.

- 25 bekannte Figuren, 21 bekannte Objekte (icon_engine)
- Humor-Datenbank für Kombinationen + Default-Fallbacks
- DE→EN-Übersetzung (60+ Wörter) für KI-Prompts
- Anatomie-Regeln für KI-Illustrations-Prompts
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from PIL import Image

import background_engine
import icon_engine
import text_layout_engine

FIGURES = icon_engine.FIGURES
OBJECTS = icon_engine.OBJECTS

# ------------------------------------------------------- Humor-Datenbank
HUMOR_DE: dict[str, str] = {
    "pinguin+eis": "Gibts auch Fisch-Eis?",
    "katze+kaffee": "Vor dem Kaffee rede ich nicht.",
    "hund+pizza": "Pizza? ICH LIEBE DICH!",
    "faultier+laptop": "Home Office Champion seit immer.",
    "roboter+kaffee": "Ich laufe auf Koffein 2.0.",
    "eule+buch": "Bildung beginnt um Mitternacht.",
    "frosch+kuchen": "Der Froschkönig bestellt zwei.",
    "baer+bier": "Ein Bier fuer den Baeren.",
    "alien+kaffee": "Auf meinem Planeten heisst das Dunkelmaterie.",
    "feuerwehrmann+eis": "Eis retten steht in der Beschreibung.",
    "astronaut+pizza": "Lieferung bis zum Mond dauert laenger.",
    "ninja+donut": "Man sieht mich nicht. Den Donut schon.",
    "pirat+handy": "Schatzkarte hat kein Empfang.",
    "einhorn+herz": "Einmal Einhorn sein, bitte.",
    "fuchs+hund": "Listig trifft treu.",
}

HUMOR_EN: dict[str, str] = {
    "pinguin+eis": "Do you have fish flavor?",
    "katze+kaffee": "I don't talk before coffee.",
    "hund+pizza": "Pizza? I LOVE YOU!",
    "faultier+laptop": "Home office champion since forever.",
    "roboter+kaffee": "I run on caffeine 2.0.",
    "eule+buch": "Education starts at midnight.",
    "frosch+kuchen": "The frog king orders two.",
    "baer+bier": "One beer for the bear.",
    "alien+kaffee": "On my planet this is dark matter.",
    "feuerwehrmann+eis": "Saving ice cream is in the job description.",
    "astronaut+pizza": "Delivery to the moon takes longer.",
    "ninja+donut": "You can't see me. The donut you can.",
    "pirat+handy": "Treasure maps have no signal.",
    "einhorn+herz": "Be a unicorn for one day.",
    "fuchs+hund": "Cunning meets loyal.",
}

DEFAULT_SPEECH_DE = [
    "Einfach mal machen.", "Montag war das.", "Kaffee zuerst.",
    "Ich bin nicht laut, ich bin deutlich.", "Alles cool hier.",
    "Plan B gibt es nicht. Nur Plan A mit Stil.",
]
DEFAULT_SPEECH_EN = [
    "Just do it already.", "That was so Monday.", "Coffee first.",
    "I'm not loud, I'm clear.", "Everything is fine here.",
    "There is no plan B. Only plan A with style.",
]

# ------------------------------------------------------- DE→EN Übersetzung
DE_EN: dict[str, str] = {
    "pinguin": "penguin", "katze": "cat", "hund": "dog", "faultier": "sloth",
    "feuerwehrmann": "firefighter", "krankenschwester": "nurse", "taucher": "diver",
    "koch": "chef", "polizist": "police officer", "astronaut": "astronaut",
    "pirat": "pirate", "ninja": "ninja", "cowboy": "cowboy", "roboter": "robot",
    "alien": "alien", "baer": "bear", "fuchs": "fox", "eule": "owl",
    "frosch": "frog", "panda": "panda", "elefant": "elephant", "affe": "monkey",
    "loewe": "lion", "einhorn": "unicorn", "drache": "dragon",
    "eis": "ice cream", "eiscreme": "ice cream", "kaffee": "coffee",
    "pizza": "pizza", "laptop": "laptop", "computer": "computer",
    "herz": "heart", "bier": "beer", "buch": "book", "handy": "phone",
    "gitarre": "guitar", "ball": "ball", "donut": "donut", "kuchen": "cake",
    "mund": "mouth", "wasser": "water", "sonne": "sun", "mond": "moon",
    "stern": "star", "wolke": "cloud", "regen": "rain", "schnee": "snow",
    "baum": "tree", "blume": "flower", "haus": "house", "auto": "car",
    "fahrrad": "bicycle", "zug": "train", "flugzeug": "airplane", "boot": "boat",
    "insel": "island", "berg": "mountain", "strand": "beach", "meer": "sea",
    "wald": "forest", "wueste": "desert", "stadt": "city", "dorf": "village",
    "bueroclam": "office clam", "kaffeebecher": "coffee cup", "tasse": "cup",
    "hut": "hat", "brille": "glasses", "schuh": "shoe", "socke": "sock",
    "uhr": "clock", "schluessel": "key", "kerze": "candle", "laterne": "lantern",
    "geschenk": "gift", "ballon": "balloon", "drachen": "kite",
    "loeffel": "spoon", "gabel": "fork", "messer": "knife", "teller": "plate",
    "topf": "pot", "pfanne": "pan", "kuehlschrank": "fridge",
    "bett": "bed", "stuhl": "chair", "tisch": "table", "lampe": "lamp",
    "teppich": "carpet", "fenster": "window", "tuer": "door",
}

# ------------------------------------------------------- Anatomie-Regeln
ANATOMY_RULES: tuple[str, ...] = (
    "full body character visible",
    "both feet and legs clearly shown",
    "front facing view",
    "complete character silhouette",
    "no cropped body parts",
    "NO text NO words NO letters in image",
)


def translate_de_en(word: str) -> str:
    """Übersetzt ein einzelnes Wort DE→EN (unbekannte Wörter unverändert)."""
    return DE_EN.get(word.lower().strip(), word)


def build_ai_prompt(figure: str, obj: str | None = None, style: str = "flat vector cartoon") -> str:
    """Baut einen KI-Illustrations-Prompt mit Anatomie-Regeln (immer englisch)."""
    fig = translate_de_en(figure)
    parts = [f"a cute {fig}"]
    if obj:
        parts.append(f"holding a {translate_de_en(obj)}")
    parts.append(style)
    parts.extend(ANATOMY_RULES)
    return ", ".join(parts)


def speech_text(figure: str, obj: str | None, lang: str = "de",
                rng: random.Random | None = None) -> str:
    """Humor-Text für eine Kombination (mit Fallback)."""
    rng = rng or random
    humor = HUMOR_DE if lang == "de" else HUMOR_EN
    if obj:
        key = f"{figure}+{obj}"
        if key in humor:
            return humor[key]
    return rng.choice(DEFAULT_SPEECH_DE if lang == "de" else DEFAULT_SPEECH_EN)


# ------------------------------------------------------- Szenen-Rendering
@dataclass
class SceneSpec:
    figure: str
    obj: str | None = None
    background: str = "clean_white"
    pattern: str | None = None
    layout: str = "speech_bubble"
    text: str | None = None
    lang: str = "de"
    style: str = "bold"
    seed: int | None = None


def render_scene(spec: SceneSpec, size: int = 2000) -> Image.Image:
    """Rendert eine komplette Cartoon-Szene (Hintergrund + Figur + Objekt + Text)."""
    rng = random.Random(spec.seed)
    if not icon_engine.is_known(spec.figure):
        raise ValueError(f"Unbekannte Figur {spec.figure!r}")
    if spec.obj and not icon_engine.is_known(spec.obj):
        raise ValueError(f"Unbekanntes Objekt {spec.obj!r}")

    bg = background_engine.create_background(spec.background, size, spec.pattern, rng)

    figure_img = icon_engine.draw_icon(spec.figure, int(size * 0.62))
    obj_img = icon_engine.draw_icon(spec.obj, int(size * 0.3)) if spec.obj else None

    canvas = bg.convert("RGBA")

    # Objekt rechts unten, Figur mittig-links
    fx = int(size * 0.06)
    canvas.alpha_composite(figure_img, (fx, int(size * 0.08)))
    if obj_img is not None:
        canvas.alpha_composite(obj_img, (int(size * 0.62), int(size * 0.55)))

    text = spec.text
    if text is None:
        text = speech_text(spec.figure, spec.obj, spec.lang, rng)

    result = text_layout_engine.draw_text_layout(
        canvas.convert("RGB"), spec.layout, text, style=spec.style,
        accent_color=(20, 20, 20),
    )
    return result


def random_scene_spec(rng: random.Random | None = None,
                      lang: str = "de") -> SceneSpec:
    """Zufällige, gültige Szenen-Spezifikation."""
    rng = rng or random
    return SceneSpec(
        figure=rng.choice(FIGURES),
        obj=rng.choice([None, *OBJECTS]),
        background=rng.choice(background_engine.BACKGROUNDS),
        pattern=background_engine.random_pattern(rng),
        layout=rng.choice(text_layout_engine.TEXT_LAYOUTS),
        lang=lang,
        style=rng.choice(font_style_list()),
        seed=rng.randint(0, 2**31 - 1),
    )


def font_style_list() -> list[str]:
    import font_manager
    return list(font_manager.FONT_STYLES)
