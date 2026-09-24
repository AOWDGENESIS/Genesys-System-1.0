"""Prompt-Feedback-System: Bild-Kritik erfassen → Prompts automatisch verbessern.

10 Problemkategorien:
  missing_foot, text_in_image, wrong_text, bad_anatomy, wrong_character,
  too_dark, blurry, bad_background, wrong_style, too_complex

Lern-Regel: Nach 2x gleichem Problem wird der Fix automatisch in
zukünftige Prompts eingefügt (z.B. 2x missing_foot →
"both feet clearly visible, full body shot").

Speicher: JSON im GENESIS_STORAGE (feedback_store.json).
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path

import config

logger = logging.getLogger("genesis.feedback")

PROBLEM_CATEGORIES: dict[str, str] = {
    "missing_foot": "Fehlender Fuß",
    "text_in_image": "Ungewollter Text",
    "wrong_text": "Falscher Text in Sprechblase",
    "bad_anatomy": "Schlechte Proportionen",
    "wrong_character": "Falsche Figur",
    "too_dark": "Zu dunkel",
    "blurry": "Unscharf",
    "bad_background": "Störender Hintergrund",
    "wrong_style": "Falscher Stil",
    "too_complex": "Zu detailliert",
}

TRIGGER_THRESHOLD = 2  # ab so vielen Meldungen wird der Fix aktiv

# Automatische Prompt-Fixes pro Problemkategorie
AUTO_FIXES: dict[str, str] = {
    "missing_foot": "both feet clearly visible, full body shot",
    "text_in_image": "absolutely no text, no letters, no typography in image",
    "wrong_text": "no speech bubbles, no captions",
    "bad_anatomy": "correct proportions, anatomically accurate cartoon character",
    "wrong_character": "exactly one clearly recognizable main character",
    "too_dark": "bright even lighting, vivid colors",
    "blurry": "sharp focus, crisp edges, high detail",
    "bad_background": "plain white background, no background elements",
    "wrong_style": "flat vector cartoon style, bold outlines",
    "too_complex": "minimalist simple design, few elements",
}


class FeedbackStore:
    """Persistenter Feedback-Speicher (JSON, thread-sicher)."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or config.STORAGE_DIR / "feedback_store.json"
        self._lock = threading.Lock()
        self._reports: list[dict] = []
        self.load()

    # -------------------------------------------------- Persistenz
    def load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self._reports = data.get("reports", [])
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Feedback-Speicher defekt, starte leer: %s", exc)
                self._reports = []

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps({"reports": self._reports}, ensure_ascii=False, indent=1),
                encoding="utf-8",
            )

    # -------------------------------------------------- API
    def add_report(self, problems: list[str], rating: int = 3,
                   note: str = "", prompt: str = "") -> dict:
        """Erfasst einen Bild-Report. Gibt den Report zurück."""
        invalid = [p for p in problems if p not in PROBLEM_CATEGORIES]
        if invalid:
            raise ValueError(f"Unbekannte Problemkategorien: {invalid}")
        if not 1 <= rating <= 5:
            raise ValueError("rating muss 1..5 sein")
        report = {
            "problems": problems,
            "rating": rating,
            "note": note,
            "prompt": prompt,
        }
        with self._lock:
            self._reports.append(report)
        self.save()
        logger.info("Feedback erfasst: Probleme=%s Bewertung=%d", problems, rating)
        return report

    def problem_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {k: 0 for k in PROBLEM_CATEGORIES}
        for r in self._reports:
            for p in r.get("problems", []):
                counts[p] = counts.get(p, 0) + 1
        return counts

    def active_fixes(self) -> list[str]:
        """Alle AUTO_FIXES, deren Problem den Schwellwert erreicht hat."""
        counts = self.problem_counts()
        return [AUTO_FIXES[p] for p, c in counts.items()
                if c >= TRIGGER_THRESHOLD and p in AUTO_FIXES]

    def reset(self) -> None:
        with self._lock:
            self._reports = []
        self.save()

    @property
    def reports(self) -> list[dict]:
        with self._lock:
            return list(self._reports)


_DEFAULT_STORE: FeedbackStore | None = None


def default_store() -> FeedbackStore:
    global _DEFAULT_STORE  # noqa: PLW0603
    if _DEFAULT_STORE is None:
        _DEFAULT_STORE = FeedbackStore()
    return _DEFAULT_STORE


def enhance_prompt(base_prompt: str, store: FeedbackStore | None = None) -> str:
    """Fügt gelernte Fixes an einen Basis-Prompt an."""
    store = store or default_store()
    fixes = store.active_fixes()
    if not fixes:
        return base_prompt
    additions = [f for f in fixes if f not in base_prompt]
    if not additions:
        return base_prompt
    return base_prompt + ", " + ", ".join(additions)


def analyze_with_ai(image_path: Path, provider: str = "gemini",
                    question: str = "List problems with this design image.") -> str:
    """Optional: Bildanalyse via Gemini/GPT-4o (nur wenn API-Key vorhanden).

    Gibt "" zurück, wenn kein Backend verfügbar ist (kein Crash).
    """
    try:
        if provider == "gemini":
            import gemini_engine
            return gemini_engine.analyze_image(image_path, question)
        if provider in ("gpt-4o", "openai"):
            return _analyze_openai(image_path, question)
    except Exception as exc:  # noqa: BLE001 — GUI darf nie crashen
        logger.warning("KI-Analyse fehlgeschlagen (%s): %s", provider, exc)
    return ""


def _analyze_openai(image_path: Path, question: str) -> str:
    import base64

    import key_manager

    api_key = key_manager.get_key("openai")
    if not api_key:
        return ""
    import requests

    b64 = base64.b64encode(image_path.read_bytes()).decode()
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "gpt-4o",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ],
            }],
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
