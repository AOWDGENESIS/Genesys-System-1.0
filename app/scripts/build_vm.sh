#!/usr/bin/env bash
# ============================================================
#  GENESIS SYSTEM — Test-VM aufbauen (isoliert, außerhalb des Repos)
#
#  Die "VM" ist eine frische, reproduzierbare Umgebung:
#    - Eigenes Python-Virtualenv  (/tmp/genesis_vm/venv)
#    - Eigene Pakete (Pillow, PyYAML, requests, pytest, ruff)
#    - Eigener Storage            (/tmp/genesis_vm/storage)
#    - Optional: Xvfb-Display, falls verfügbar (GUI-Selbsttest)
#
#  Nichts davon landet im Repo → Workspace bleibt sauber.
# ============================================================
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VM="/tmp/genesis_vm"
VENV="$VM/venv"

mkdir -p "$VM"

if [[ "${GENESIS_VM_FRESH:-1}" == "1" && -d "$VENV" ]]; then
    echo "[VM] Frischer Aufbau: lösche altes venv …"
    rm -rf "$VENV"
fi

PY_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PY_BIN" >/dev/null 2>&1; then
    echo "[VM] FEHLER: python3 nicht gefunden" >&2
    exit 1
fi

if [[ ! -d "$VENV" ]]; then
    echo "[VM] Erzeuge Virtualenv …"
    VENV_OPTS=()
    # GENESIS_VM_SYSTEM_SITE=1 → --system-site-packages (für CI: Tkinter aus
    # python3-tk ist dann im venv sichtbar, GUI-Selbsttest läuft mit Xvfb)
    if [[ "${GENESIS_VM_SYSTEM_SITE:-0}" == "1" ]]; then
        VENV_OPTS+=(--system-site-packages)
    fi
    "$PY_BIN" -m venv "${VENV_OPTS[@]}" "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
echo "[VM] Installiere Abhängigkeiten …"
pip install --quiet --upgrade pip
pip install --quiet -r "$REPO/requirements-dev.txt"
echo "[VM] Python:  $(python --version)"
echo "[VM] Pakete:  $(pip list --format=freeze | grep -iE 'pillow|yaml|requests|pytest|ruff' | tr '\n' ' ')"
echo "[VM] Tkinter: $(python -c 'import tkinter; print("verfügbar")' 2>/dev/null || echo 'NICHT verfügbar (GUI-Selbsttest wird übersprungen)')"
echo "[VM] bereit."
