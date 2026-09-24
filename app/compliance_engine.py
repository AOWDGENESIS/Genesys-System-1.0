"""Compliance-Engine: Markenschutz- und Richtlinien-Prüfung.

Schema: PRUEFSYSTEM_SCHEMA_V1.0

Prüfreihenfolge (aus compliance_rules.yaml):
  1. Extremismus / Verfassungsfeindlich
  2. Hasssymbole
  3. Staatliche Hoheitszeichen
  4. Geschützte Marken
  5. Geschützte Figuren / Franchise
  6. Urheberrecht
  7. Diskriminierung
  8. Politik
  9. Sonstige rechtliche Risiken

Verbesserungen gegenüber V1:
- Whitelist für generische Begriffe ("apple pie" schlägt nicht auf "apple" an)
- Severity-System (block/warn) statt nur Ja/Nein
- Umlaut-Folding (Hakenkreuz == hakenkreuz == hakenkreuz mit Umlauten)
- Levenshtein-Ähnlichkeit gegen Tipp-Varianten ("adidass", "nikke")
- Rein lokale Verarbeitung, keine Netzwerk Calls
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import config

logger = logging.getLogger("genesis.compliance")

_UMLAUT_MAP = str.maketrans({
    "ä": "a", "ö": "o", "ü": "u", "ß": "ss",
    "á": "a", "à": "a", "â": "a",
    "é": "e", "è": "e", "ê": "e",
    "í": "i", "ó": "o", "ô": "o", "ú": "u",
})


def normalize(text: str) -> str:
    """Kleinbuchstaben, Umlaute falten, überflüssige Leerzeichen."""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower().translate(_UMLAUT_MAP)
    return re.sub(r"\s+", " ", text).strip()


def levenshtein(a: str, b: str) -> int:
    """Iterative Levenshtein-Distanz (ohne externe Abhängigkeit)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def similarity(a: str, b: str) -> float:
    """Ähnlichkeit 0..1 (1.0 = identisch)."""
    if not a or not b:
        return 0.0
    return 1.0 - levenshtein(a, b) / max(len(a), len(b))


@dataclass(frozen=True)
class Category:
    id: str
    name_de: str
    check_order: int
    severity: str  # "block" | "warn"
    terms: tuple[str, ...]


@dataclass(frozen=True)
class Finding:
    category: str
    category_de: str
    severity: str
    term: str
    matched_text: str
    similarity: float = 1.0
    via: str = "exact"  # "exact" | "similar" | "whitelist-exact"

    @property
    def is_block(self) -> bool:
        return self.severity == "block"


@dataclass
class ComplianceResult:
    text: str = ""
    findings: list[Finding] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        """True wenn keinerlei Findings und kein Fehler (streng)."""
        return self.error is None and not self.findings

    @property
    def blocked(self) -> bool:
        return any(f.is_block for f in self.findings)

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if not f.is_block]

    def summary(self) -> str:
        if self.error:
            return f"FEHLER: {self.error}"
        if not self.findings:
            return "OK — keine Verstöße gefunden."
        parts = []
        for f in self.findings:
            tag = "BLOCK" if f.is_block else "WARN"
            extra = f" (ähnlich zu '{f.term}', {f.similarity:.0%})" if f.via == "similar" else ""
            parts.append(f"[{tag}] {f.category_de}: '{f.matched_text}'{extra}")
        return "\n".join(parts)


class ComplianceEngine:
    """Lädt das YAML-Regelwerk und prüft Texte."""

    def __init__(self, rules_path: Path | str | None = None) -> None:
        self.rules_path = Path(rules_path or config.RULES_FILE)
        self.categories: list[Category] = []
        self.whitelist: list[str] = []
        self.similarity_threshold: float = config.SIMILARITY_THRESHOLD
        self._load()

    # ------------------------------------------------------------ Laden
    def _load(self) -> None:
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Regelwerk nicht gefunden: {self.rules_path}")
        with open(self.rules_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not data or not data.get("categories"):
            raise ValueError("Regelwerk ungültig: 'categories' fehlt oder ist leer.")

        cats: list[Category] = []
        for c in data["categories"]:
            severity = str(c.get("severity", "block")).lower()
            if severity not in ("block", "warn"):
                raise ValueError(f"Ungültige severity {severity!r} in Kategorie {c.get('id')}")
            cats.append(Category(
                id=str(c["id"]),
                name_de=str(c.get("name_de", c["id"])),
                check_order=int(c.get("check_order", 99)),
                severity=severity,
                terms=tuple(normalize(t) for t in c.get("terms", [])),
            ))
        cats.sort(key=lambda c: c.check_order)
        self.categories = cats
        self.whitelist = [normalize(w) for w in data.get("whitelist", [])]
        self.similarity_threshold = float(
            data.get("similarity_threshold", config.SIMILARITY_THRESHOLD)
        )
        logger.info(
            "Regelwerk geladen: %d Kategorien, %d Begriffe, %d Whitelist-Einträge",
            len(cats), self.term_count(), len(self.whitelist),
        )

    # ------------------------------------------------------------ Statistik
    def term_count(self) -> int:
        return sum(len(c.terms) for c in self.categories)

    def stats(self) -> dict[str, object]:
        return {
            "schema": config.COMPLIANCE_SCHEMA,
            "categories": len(self.categories),
            "terms": self.term_count(),
            "whitelist": len(self.whitelist),
            "per_category": {c.id: len(c.terms) for c in self.categories},
            "similarity_threshold": self.similarity_threshold,
        }

    # ------------------------------------------------------------ Prüfung
    def check_text(self, text: str) -> ComplianceResult:
        """Prüft einen Text gegen alle Kategorien (in Prüfreihenfolge)."""
        if not text or not text.strip():
            return ComplianceResult(text=text)
        norm = normalize(text)
        if not norm:
            return ComplianceResult(text=text)

        # Whitelist-Phrasen aus dem Text entfernen, bevor Marken geprüft werden
        cleaned = norm
        for phrase in self.whitelist:
            cleaned = cleaned.replace(phrase, " ")

        findings: list[Finding] = []
        seen: set[tuple[str, str]] = set()

        for cat in self.categories:
            for term in cat.terms:
                if not term:
                    continue
                hit = self._match_exact(cleaned, term)
                if hit:
                    key = (cat.id, term)
                    if key not in seen:
                        seen.add(key)
                        findings.append(Finding(
                            category=cat.id, category_de=cat.name_de,
                            severity=cat.severity, term=term,
                            matched_text=hit, similarity=1.0, via="exact",
                        ))
                    continue
                sim_hit = self._match_similar(cleaned, term)
                if sim_hit:
                    word, score = sim_hit
                    key = (cat.id, term)
                    if key not in seen:
                        seen.add(key)
                        findings.append(Finding(
                            category=cat.id, category_de=cat.name_de,
                            severity=cat.severity, term=term,
                            matched_text=word, similarity=round(score, 3),
                            via="similar",
                        ))

        if findings:
            logger.debug("Compliance-Findings für %r: %s", text[:50], [f.term for f in findings])
        return ComplianceResult(text=text, findings=findings)

    def check_batch(self, texts: list[str]) -> dict[str, ComplianceResult]:
        """Prüft mehrere Texte (z.B. alle Sprüche einer Keyword-Liste)."""
        return {t: self.check_text(t) for t in texts}

    # ------------------------------------------------------------ Matcher
    @staticmethod
    def _match_exact(text: str, term: str) -> str | None:
        """Wortgrenzen-Match; liefert den tatsächlich gefundenen Textausschnitt."""
        pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
        m = re.search(pattern, text)
        if m:
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            return text[start:end].strip()
        return None

    def _match_similar(self, text: str, term: str) -> tuple[str, float] | None:
        """Levenshtein-Check pro Wort — Tippfehler-Erkennung ohne False Positives.

        Regeln:
        - Begriffe mit < 6 Zeichen: nur exakte Treffer (schützt "yoga",
          "like", "else" vor Fehlalarmen gegen "yoda", "nike", "elsa").
        - Begriffe >= 6 Zeichen: 1 Tippfehler erlaubt (bzw. mehr bei sehr
          langen Begriffen), erstes Zeichen muss übereinstimmen.
        """
        if len(term) < 6:
            return None
        allowed_dist = max(1, int((1 - self.similarity_threshold) * len(term)))
        best: tuple[str, float] | None = None
        for word in re.findall(r"[a-z0-9\-]+", text):
            if len(word) < 4 or word[0] != term[0]:
                continue
            if word == term:
                continue  # schon exakt geprüft
            dist = levenshtein(word, term)
            if dist <= allowed_dist:
                score = 1.0 - dist / max(len(word), len(term))
                if best is None or score > best[1]:
                    best = (word, score)
        return best


_DEFAULT_ENGINE: ComplianceEngine | None = None


def default_engine() -> ComplianceEngine:
    """Prozess-weite Standard-Engine (lazy, gecached)."""
    global _DEFAULT_ENGINE  # noqa: PLW0603
    if _DEFAULT_ENGINE is None:
        _DEFAULT_ENGINE = ComplianceEngine()
    return _DEFAULT_ENGINE
