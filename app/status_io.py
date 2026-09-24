"""Status-Tracking aller Designs (status.csv) — zentrale Lese-/Schreib-API.

Verbesserung gegenüber V1: CSV mit Header, sauberes Quoting,
atomares Schreiben, keine Duplikate pro Design-Name.
"""

from __future__ import annotations

import contextlib
import csv
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

import config

logger = logging.getLogger("genesis.status")

FIELDS = ("name", "kind", "status", "text", "path", "created", "uploaded")


def read_status(csv_path: Path | None = None) -> list[dict[str, str]]:
    """Liest alle Status-Einträge."""
    csv_path = csv_path or config.STATUS_CSV
    if not csv_path.exists():
        return []
    with open(csv_path, encoding="utf-8", newline="") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def get_entry(name: str, csv_path: Path | None = None) -> dict[str, str] | None:
    for row in read_status(csv_path):
        if row.get("name") == name:
            return row
    return None


def append_status(name: str, kind: str, status: str = "generated",
                  text: str = "", path: Path | None = None, *,
                  csv_path: Path | None = None) -> None:
    """Fügt einen Eintrag hinzu oder aktualisiert Status/Text eines Namens."""
    csv_path = csv_path or config.STATUS_CSV
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = read_status(csv_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    updated = False
    for row in rows:
        if row.get("name") == name:
            row["status"] = status
            row["text"] = text or row.get("text", "")
            row["path"] = str(path) if path else row.get("path", "")
            if status == "uploaded" and not row.get("uploaded"):
                row["uploaded"] = now
            updated = True
            break
    if not updated:
        rows.append({
            "name": name, "kind": kind, "status": status, "text": text,
            "path": str(path or ""), "created": now, "uploaded": "",
        })

    _write_rows(rows, csv_path)


def mark_uploaded(name: str, csv_path: Path | None = None) -> bool:
    """Setzt Status auf 'uploaded'. Gibt False zurück, wenn Design unbekannt."""
    rows = read_status(csv_path)
    for row in rows:
        if row.get("name") == name:
            row["status"] = "uploaded"
            row["uploaded"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _write_rows(rows, csv_path or config.STATUS_CSV)
            return True
    return False


def pending_designs(csv_path: Path | None = None) -> list[dict[str, str]]:
    """Alle Designs mit Status 'generated' (noch nicht hochgeladen)."""
    return [r for r in read_status(csv_path) if r.get("status") == "generated"]


def _write_rows(rows: list[dict[str, str]], csv_path: Path) -> None:
    """Atomares Schreiben (erst temp, dann umbenennen)."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_name = tempfile.mkstemp(dir=csv_path.parent, suffix=".tmp")
    try:
        with open(tmp_fd, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(tmp_name, csv_path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise
