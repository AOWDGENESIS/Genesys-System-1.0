"""Upload-Manager: Metadaten-Workflow für Redbubble/TeePublic/Spreadshirt.

Workflow:
  1. Design generieren
  2. Upload-Tab: Designs auswählen
  3. Plattform wählen
  4. Titel/Tags/Beschreibung kopieren (GUI-Knopf)
  5. "Plattform öffnen" → Browser öffnet Upload-Seite
  6. Nach Upload: "Markieren" → status.csv = uploaded

Tags-Strategie: Design-Tags + Brand-Keywords, plattformspezifisches Limit.
"""

from __future__ import annotations

import logging
import subprocess
import sys
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path

import brand_identity
import config
from status_io import get_entry, mark_uploaded, pending_designs

logger = logging.getLogger("genesis.upload")

TITLE_MAX = 60


@dataclass
class UploadMeta:
    name: str
    title: str
    tags: list[str] = field(default_factory=list)
    description: str = ""
    platform: str = "redbubble"
    design_path: Path | None = None
    mockup_path: Path | None = None

    @property
    def tags_str(self) -> str:
        return ", ".join(self.tags)


def build_title(text: str, max_len: int = TITLE_MAX) -> str:
    """Baut einen upload-fertigen Titel (Keyword zuerst, max 60 Zeichen)."""
    words = text.strip().split()
    # Wichtigste Wörter (längsten Wörter) nach vorn ist riskant —
    # besser: Originaltext kürzen, aber erste Wörter behalten.
    title = " ".join(w.capitalize() if w.islower() else w for w in words)
    if len(title) > max_len:
        title = title[: max_len - 1].rsplit(" ", 1)[0] + "…"
    return title


def build_tags(design_tags: list[str], platform: str = "redbubble",
              brand: str = "en") -> list[str]:
    """Design-Tags + Brand-Keywords, dedupliziert, auf Plattform-Limit gekürzt."""
    plat = brand_identity.PLATFORMS.get(platform)
    limit = plat.max_tags if plat else 15
    brand_kws = brand_identity.BRAND_KEYWORDS if brand == "en" else brand_identity.BRAND_KEYWORDS
    seen: set[str] = set()
    tags: list[str] = []
    for tag in [*design_tags, *brand_kws]:
        t = tag.strip().lower()
        if t and t not in seen:
            seen.add(t)
            tags.append(t)
        if len(tags) >= limit:
            break
    return tags


def build_description(text: str, lang: str = "en") -> str:
    """Kurze Beschreibung (1-3 Sätze, plattformfreundlich)."""
    if lang == "de":
        return (f"{text} — ausdrucksstarkes Design von Zeichenwerk. "
                "Perfekt für Alltag, Gym und Büro.")
    return (f"{text} — bold wearable art by Zeichenwerk. "
            "Perfect for everyday, gym and office.")


def meta_for_design(name: str, platform: str = "redbubble",
                    lang: str = "en") -> UploadMeta:
    """Baut Upload-Metadaten aus status.csv + Metadaten-TXT."""
    entry = get_entry(name)
    if entry is None:
        raise ValueError(f"Design {name!r} nicht im Status-Tracking gefunden.")
    text = entry.get("text", "")
    design_path = Path(entry["path"]) if entry.get("path") else None
    tags = _tags_from_metadata(name)
    return UploadMeta(
        name=name,
        title=build_title(text),
        tags=build_tags(tags, platform),
        description=build_description(text, lang),
        platform=platform,
        design_path=design_path,
        mockup_path=_find_mockup(name),
    )


def _tags_from_metadata(name: str) -> list[str]:
    meta_file = config.UPLOAD_READY_DIR / f"{name}.txt"
    if meta_file.exists():
        for line in meta_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("tags:"):
                return [t.strip() for t in line[5:].split(",") if t.strip()]
    return []


def _find_mockup(name: str) -> Path | None:
    for color in ("black", "white"):
        p = config.MOCKUPS_DIR / f"{name}_mockup_{color}.png"
        if p.exists():
            return p
    return None


def copy_to_clipboard(text: str) -> bool:
    """Kopiert Text in die Zwischenablage (Windows/Linux/macOS)."""
    try:
        if sys.platform == "win32":
            subprocess.run(["clip"], input=text.encode("utf-8"), check=True,
                           timeout=5)
        elif sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True,
                           timeout=5)
        else:
            for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
                try:
                    subprocess.run(cmd, input=text.encode("utf-8"), check=True,
                                   timeout=5)
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            else:
                logger.warning("Kein Clipboard-Tool gefunden (xclip/xsel).")
                return False
        return True
    except (subprocess.SubprocessError, OSError) as exc:
        logger.warning("Clipboard-Fehler: %s", exc)
        return False


def open_platform(platform: str) -> bool:
    """Öffnet die Upload-Seite der Plattform im Browser."""
    plat = brand_identity.PLATFORMS.get(platform)
    if plat is None or not plat.upload_url:
        logger.error("Unbekannte/inaktive Plattform: %s", platform)
        return False
    try:
        webbrowser.open(plat.upload_url)
        return True
    except webbrowser.Error as exc:
        logger.warning("Browser konnte nicht geöffnet werden: %s", exc)
        return False


def mark_design_uploaded(name: str) -> bool:
    """Setzt Design auf uploaded (Delegation an status_io)."""
    ok = mark_uploaded(name)
    if ok:
        logger.info("Design als hochgeladen markiert: %s", name)
    return ok


def pending() -> list[dict[str, str]]:
    """Noch nicht hochgeladene Designs."""
    return pending_designs()


def platform_guideline(platform: str) -> str:
    return brand_identity.PLATFORM_GUIDELINES.get(
        platform, "Keine Richtlinien für diese Plattform hinterlegt.")
