#!/usr/bin/env bash
# ============================================================
#  GENESIS SYSTEM / Zeichenwerk — Linux/macOS Starter
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

if ! command -v "$PY" >/dev/null 2>&1; then
    echo "FEHLER: Python nicht gefunden (python3)." >&2
    exit 1
fi

if ! "$PY" -c "import PIL, yaml, requests" >/dev/null 2>&1; then
    echo "Installiere Abhängigkeiten ..."
    "$PY" -m pip install -r requirements.txt
fi

echo "Starte GENESIS SYSTEM ..."
exec "$PY" control_panel.py "$@"
