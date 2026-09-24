#!/usr/bin/env python3
"""CLI Compliance-Validator für das GENESIS SYSTEM.

Nutzung:
    python validator.py "But First Coffee"          # Einzeltext prüfen
    python validator.py --file texte.txt            # Datei (eine Zeile pro Text)
    python validator.py --stats                     # Regelwerk-Statistik
    python validator.py --batch                     # ganze Text-Datenbank prüfen

Exit-Codes: 0 = OK, 1 = Warnungen, 2 = blockiert, 3 = Fehler
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from compliance_engine import ComplianceEngine
import text_database


def _run(text: str, engine: ComplianceEngine) -> int:
    result = engine.check_text(text)
    print(f"Text:     {text!r}")
    print(f"Ergebnis: {'BLOCKIERT' if result.blocked else ('WARNUNG' if result.warnings else 'OK')}")
    if result.findings:
        print(result.summary())
    return 2 if result.blocked else (1 if result.warnings else 0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validator",
        description="GENESIS Compliance-Validator (Schema PRUEFSYSTEM_SCHEMA_V1.0)",
    )
    parser.add_argument("text", nargs="*", help="Zu prüfender Text (in Anführungszeichen)")
    parser.add_argument("--file", type=Path, help="Textdatei (eine Zeile pro Text)")
    parser.add_argument("--stats", action="store_true", help="Regelwerk-Statistik ausgeben")
    parser.add_argument("--batch", action="store_true", help="Gesamte Text-Datenbank prüfen")
    parser.add_argument("--rules", type=Path, default=None, help="Pfad zum Regelwerk (YAML)")
    args = parser.parse_args(argv)

    try:
        engine = ComplianceEngine(args.rules)
    except (FileNotFoundError, ValueError) as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 3

    if args.stats:
        stats = engine.stats()
        print(f"Schema:      {stats['schema']}")
        print(f"Kategorien:  {stats['categories']}")
        print(f"Begriffe:    {stats['terms']}")
        print(f"Whitelist:   {stats['whitelist']} Einträge")
        print(f"Ähnlichkeit: {stats['similarity_threshold']:.2f}")
        print("Pro Kategorie:")
        for cat_id, count in stats["per_category"].items():  # type: ignore[union-attr]
            print(f"  {cat_id:15s} {count}")
        return 0

    if args.batch:
        worst = 0
        total = 0
        for lang in text_database.SUPPORTED_LANGUAGES:
            for kw in text_database.keywords(lang):
                for text in text_database.texts_for(lang, kw):
                    total += 1
                    result = engine.check_text(text)
                    if result.blocked:
                        print(f"[BLOCK] ({lang}/{kw}) {text}")
                        worst = 2
                    elif result.warnings:
                        print(f"[WARN]  ({lang}/{kw}) {text}")
                        worst = max(worst, 1)
        print(f"\nGeprüft: {total} Texte — {'BLOCKIERT' if worst == 2 else ('WARNUNGEN' if worst == 1 else 'alle OK')}")
        return worst

    texts: list[str] = []
    if args.text:
        texts.append(" ".join(args.text))
    if args.file:
        if not args.file.exists():
            print(f"FEHLER: Datei nicht gefunden: {args.file}", file=sys.stderr)
            return 3
        texts.extend(
            line.strip() for line in args.file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        )
    if not texts:
        parser.print_help()
        return 3

    worst = 0
    for text in texts:
        worst = max(worst, _run(text, engine))
        print()
    return worst


if __name__ == "__main__":
    sys.exit(main())
