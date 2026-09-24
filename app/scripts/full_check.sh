#!/usr/bin/env bash
# ============================================================
#  GENESIS SYSTEM — VOLLPRÜFUNG (von vorne, jede Runde)
#
#  Ablauf jeder Runde:
#    0. VM komplett neu aufbauen (frisches venv in /tmp)
#    1. Workspace-Sauberkeit prüfen (keine Artefakte im Repo)
#    2. Statische Prüfung: ruff (Fehler & Warnungen)
#    3. Komplette Testsuite: pytest (alle Module, headless)
#    4. CLI-Smoke: validator (Stats + Batch der Text-Datenbank)
#    5. Pipeline-Smoke: Generator → Mockup → Formate → Upload-Meta
#    6. GUI-Selbsttest, falls Tkinter+Display vorhanden
#    7. Storage der Runde wegwerfen (Workspace bleibt schlank)
#
#  Exit-Code 0 nur wenn ALLES grün ist. Bei Fehlern: fixen und
#  dieses Skript erneut ausführen (Prüfung startet von vorne).
# ============================================================
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VM="/tmp/genesis_vm"
STORAGE="$VM/storage"
ROUND_LOG="$VM/last_check.log"

# ---------- 0) VM frisch aufbauen ----------
bash "$REPO/scripts/build_vm.sh" 2>&1 | tee "$ROUND_LOG"
# shellcheck disable=SC1091
source "$VM/venv/bin/activate"
cd "$REPO"

export GENESIS_STORAGE="$STORAGE"
rm -rf "$STORAGE"

echo
echo "=================================================="
echo " VOLLPRÜFUNG GENESIS SYSTEM — $(date '+%F %T')"
echo "=================================================="

# ---------- 1) Workspace-Sauberkeit ----------
echo "[1/7] Workspace-Sauberkeit …"
if find . -path ./.git -prune -o -name '__pycache__' -prune -o -type f \( -name '*.png' -o -name '*.log' -o -name '*.csv' -o -name 'sales_data.json' \) -print | grep -v './genesis.ico' | grep -q .; then
    find . -path ./.git -prune -o -name '__pycache__' -prune -o -type f \( -name '*.png' -o -name '*.log' -o -name '*.csv' -o -name 'sales_data.json' \) -print | grep -v './genesis.ico'
    echo "FEHLER: Artefakte im Repo gefunden (siehe oben)." >&2
    exit 1
fi
echo "  OK — keine Artefakte im Repo."

# ---------- 2) Statische Prüfung ----------
echo "[2/7] Statische Prüfung (ruff + Shell-Syntax) …"
ruff check .
echo "  OK — ruff ohne Befunde."
for sh_file in scripts/*.sh start_genesis.sh; do
    [[ -f "$sh_file" ]] || continue
    bash -n "$sh_file" || { echo "FEHLER: Shell-Syntax in $sh_file" >&2; exit 1; }
done
echo "  OK — Shell-Skripte syntaktisch gültig."

# ---------- 3) Testsuite ----------
echo "[3/7] Testsuite (pytest) …"
python -m pytest tests/ -q --tb=short
echo "  OK — alle Tests grün."

# ---------- 4) CLI-Smoke validator ----------
echo "[4/7] CLI-Smoke: validator …"
python validator.py --stats
python validator.py "But First Coffee" >/dev/null && echo "  OK — Safe-Text Exit 0"
python validator.py "Nike Style Shirt" >/dev/null && { echo "FEHLER: Nike sollte blockieren" >&2; exit 1; } || test $? -eq 2 && echo "  OK — Marken-Text blockiert (Exit 2)"

# ---------- 5) Pipeline-Smoke ----------
echo "[5/7] Pipeline-Smoke: Generator→Mockup→Formate→Upload …"
python - <<'PYEOF'
from pathlib import Path
from PIL import Image

import generator, mockup_engine, product_formats, upload_manager, sales_tracker, config

d = generator.generate_design("Vollprüfung Laeuft", size=1000, seed=1)
img = Image.open(d)
assert img.size == (1000, 1000), img.size

mock = mockup_engine.create_mockup(img, "black", config.MOCKUPS_DIR / "check.png")
assert mock.size == (1200, 1400), mock.size

for fmt in product_formats.PRODUCT_FORMATS:
    out = config.DESIGNS_DIR / f"check_{fmt}.png"
    product_formats.export_for_product(img, fmt, out)
    assert Image.open(out).size == product_formats.get_format(fmt).size

name = d.stem
meta = upload_manager.meta_for_design(name, "redbubble")
assert len(meta.tags) <= 15, meta.tags
assert upload_manager.mark_design_uploaded(name)

tracker = sales_tracker.SalesTracker()
tracker.add_sale(name, "redbubble", 3)
assert "VERKAUFSBERICHT" in tracker.report()

print("  OK — Pipeline komplett (Design, Mockup, 7 Formate, Upload-Meta, Sales).")
PYEOF

# ---------- 6) GUI-Selbsttest (falls möglich) ----------
echo "[6/7] GUI-Selbsttest …"
if python -c "import tkinter" 2>/dev/null; then
    if [[ -n "${DISPLAY:-}" ]] || command -v xvfb-run >/dev/null 2>&1; then
        if [[ -z "${DISPLAY:-}" ]]; then
            xvfb-run -a python control_panel.py --selftest
        else
            python control_panel.py --selftest
        fi
    else
        echo "  INFO — Tkinter vorhanden, aber kein Display/Xvfb. Selbsttest übersprungen."
    fi
else
    echo "  INFO — Kein Tkinter in der VM. GUI-Logik ist über Testsuite abgedeckt;"
    echo "         GUI-Selbsttest läuft automatisch auf dem Zielsystem (Windows)."
fi

# ---------- 7) Installations-ZIP bauen + verifizieren ----------
echo "[7/7] Windows-Installations-ZIP (build + Verifikation) …"
bash "$REPO/scripts/build_zip.sh"

# ---------- Aufräumen ----------
rm -rf "$STORAGE" /tmp/genesis_zip_test /tmp/genesis_dist /tmp/genesis_zip_storage
# Runtime-Caches entfernen → Workspace enthält nur den aktuellen Stand
find "$REPO" -path "$REPO/.git" -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "$REPO" -path "$REPO/.git" -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
find "$REPO" -path "$REPO/.git" -prune -o -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
echo
echo "=================================================="
echo " ERGEBNIS: ALLE PRÜFUNGEN GRÜN ✓"
echo " Installations-ZIP: releases/GENESIS_SYSTEM_V2_Setup.zip"
echo "=================================================="
