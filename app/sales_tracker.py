"""Sales-Tracker: Verkaufsanalyse pro Design.

Datenformat: JSON (sales_data.json) im GENESIS_STORAGE

Felder pro Design:
  name, total, platforms {plattform: anzahl}, history [{date, platform, count}]

Performance-Tiers (relativ zum Bestseller):
  STAR:  >= 70 % des Bestsellers
  GOOD:  >= 35 %
  OK:    >= 10 %
  WEAK:  <  10 %
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

import config

logger = logging.getLogger("genesis.sales")

TIERS = ("STAR", "GOOD", "OK", "WEAK")


@dataclass
class SaleEntry:
    date: str          # ISO yyyy-mm-dd
    platform: str
    count: int


@dataclass
class DesignSales:
    name: str
    total: int = 0
    platforms: dict[str, int] = field(default_factory=dict)
    history: list[SaleEntry] = field(default_factory=list)


def tier_for(total: int, best: int) -> str:
    """Performance-Tier relativ zum Bestseller."""
    if best <= 0:
        return "WEAK" if total <= 0 else "STAR"
    ratio = total / best
    if ratio >= 0.70:
        return "STAR"
    if ratio >= 0.35:
        return "GOOD"
    if ratio >= 0.10:
        return "OK"
    return "WEAK"


class SalesTracker:
    """Zentrale Verkaufsanalyse."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or config.STORAGE_DIR / "sales_data.json"
        self.designs: dict[str, DesignSales] = {}
        self.load()

    # -------------------------------------------------- Persistenz
    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            for name, d in data.get("designs", {}).items():
                self.designs[name] = DesignSales(
                    name=name,
                    total=int(d.get("total", 0)),
                    platforms={k: int(v) for k, v in d.get("platforms", {}).items()},
                    history=[SaleEntry(h["date"], h["platform"], int(h["count"]))
                             for h in d.get("history", [])],
                )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            logger.warning("Sales-Daten defekt, starte leer: %s", exc)
            self.designs = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"designs": {
            name: {
                "name": d.name, "total": d.total, "platforms": d.platforms,
                "history": [
                    {"date": h.date, "platform": h.platform, "count": h.count}
                    for h in d.history
                ],
            } for name, d in self.designs.items()
        }}
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                             encoding="utf-8")

    # -------------------------------------------------- Erfassung
    def add_sale(self, design: str, platform: str, count: int = 1,
                 day: str | None = None) -> DesignSales:
        """Trägt count Verkäufe für ein Design ein."""
        if count <= 0:
            raise ValueError("count muss > 0 sein")
        d = self.designs.setdefault(design, DesignSales(design))
        d.total += count
        d.platforms[platform] = d.platforms.get(platform, 0) + count
        d.history.append(SaleEntry(
            day or date.today().isoformat(), platform, count))
        self.save()
        logger.info("Verkauf erfasst: %s +%d (%s)", design, count, platform)
        return d

    def set_total(self, design: str, total: int) -> DesignSales:
        """Setzt Gesamtzahl direkt (korrigiert Plattformverteilung nicht rückwärtig)."""
        if total < 0:
            raise ValueError("total muss >= 0 sein")
        d = self.designs.setdefault(design, DesignSales(design))
        d.total = total
        self.save()
        return d

    # -------------------------------------------------- Analyse
    def bestseller(self) -> int:
        return max((d.total for d in self.designs.values()), default=0)

    def tiers(self) -> dict[str, str]:
        """Tier pro Design."""
        best = self.bestseller()
        return {name: tier_for(d.total, best) for name, d in self.designs.items()}

    def summary(self) -> dict[str, object]:
        totals = [d.total for d in self.designs.values()]
        return {
            "designs": len(self.designs),
            "total_sales": sum(totals),
            "bestseller": max(self.designs.items(), key=lambda kv: kv[1].total,
                              default=None)[0] if self.designs else None,
            "bestseller_total": self.bestseller(),
        }

    def analyze_last_days(self, days: int = 30) -> dict[str, object]:
        """30-Tage-Analyse (Standard): Verkäufe, Tops, Plattformen."""
        cutoff = (date.today() - timedelta(days=days)).isoformat()
        entries = [
            (name, h) for name, d in self.designs.items() for h in d.history
            if h.date >= cutoff
        ]
        per_design: dict[str, int] = {}
        per_platform: dict[str, int] = {}
        per_day: dict[str, int] = {}
        for name, h in entries:
            per_design[name] = per_design.get(name, 0) + h.count
            per_platform[h.platform] = per_platform.get(h.platform, 0) + h.count
            per_day[h.date] = per_day.get(h.date, 0) + h.count
        top = sorted(per_design.items(), key=lambda kv: -kv[1])[:10]
        return {
            "days": days,
            "total": sum(h.count for _, h in entries),
            "per_design": per_design,
            "per_platform": per_platform,
            "per_day": dict(sorted(per_day.items())),
            "top_designs": top,
        }

    def report(self, days: int = 30) -> str:
        """Menschenlesbarer Bericht."""
        s = self.summary()
        a = self.analyze_last_days(days)
        lines = [
            "=== ZEICHENWERK VERKAUFSBERICHT ===",
            f"Erstellt:      {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Designs:       {s['designs']}",
            f"Gesamtverkäufe:{s['total_sales']}",
            f"Bestseller:    {s['bestseller']} ({s['bestseller_total']})",
            "",
            f"--- Letzte {days} Tage ---",
            f"Verkäufe:      {a['total']}",
        ]
        if a["per_platform"]:
            lines.append("Plattformen:")
            for p, c in sorted(a["per_platform"].items(), key=lambda kv: -kv[1]):
                lines.append(f"  {p:15s} {c}")
        if a["top_designs"]:
            lines.append("Top-Designs:")
            tiers = self.tiers()
            for name, c in a["top_designs"][:5]:
                lines.append(f"  {name[:40]:42s} {c:4d}  [{tiers.get(name, '-')}]")
        return "\n".join(lines)

    def reset(self) -> None:
        self.designs.clear()
        self.save()
