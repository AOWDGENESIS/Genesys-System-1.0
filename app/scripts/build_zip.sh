#!/usr/bin/env bash
# ============================================================
#  GENESIS SYSTEM — Windows-Installations-ZIP bauen + verifizieren
#
#  Erzeugt releases/GENESIS_SYSTEM_V2_Setup.zip mit:
#    INSTALLIEREN.bat        (Doppelklick-Installer)
#    LIESMICH.txt            (Anleitung)
#    installer/              (install.ps1, uninstall.ps1, Inno-Setup)
#    app/                    (komplettes Programm, aus git)
#
#  Verifikation: Entpacken, Datei-Zahl abgleichen, komplette
#  Testsuite im entpackten Zustand laufen lassen, SHA256.
# ============================================================
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE_ROOT="/tmp/genesis_dist"
STAGE="$STAGE_ROOT/GENESIS_SYSTEM_V2"
ZIP_DIR="$REPO/releases"
ZIP="$ZIP_DIR/GENESIS_SYSTEM_V2_Setup.zip"

command -v zip >/dev/null 2>&1 || { echo "FEHLER: zip nicht installiert" >&2; exit 1; }

# CI-Diagnose: Fehlertexte als GitHub-Annotationen ausgeben (API-lesbar,
# auch wenn Log-Downloads blockiert sind)
function ci_error() { # $1=Titel, Rest=Meldung
    if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        local msg="${*:2}"
        printf '::error title=%s::%s\n' "$1" "${msg//::/../}"
    fi
}
function ci_dump_pytest_log() {
    if [[ -n "${GITHUB_ACTIONS:-}" && -f /tmp/genesis_zip_pytest.log ]]; then
        tail -15 /tmp/genesis_zip_pytest.log | while IFS= read -r l; do
            [[ -n "$l" ]] && printf '::error title=ZIP-Tests::%s\n' "${l//::/../}"
        done
    fi
}
trap 'ci_error "build_zip" "unerwarteter Fehler in Zeile $LINENO"; ci_dump_pytest_log' ERR

echo "[ZIP] Räume Staging auf …"
rm -rf "$STAGE_ROOT"
mkdir -p "$STAGE/installer" "$ZIP_DIR"

echo "[ZIP] Stagee App aus dem Arbeitsverzeichnis (git-unabhaengig, deterministisch) …"
# Quelle: Working-Tree. Bewusst KEIN 'git ls-files' — das lokale .git kann
# zwischen Sitzungen zurueckgesetzt werden; das ZIP darf davon nie abhaengen.
STAGE_EXCLUDES=(
    -path './.git' -prune -o
    -path './.github' -prune -o
    -path './installer*' -prune -o
    -path './releases*' -prune -o
    -path './dist*' -prune -o
    -path './.venv' -prune -o
    -path './venv' -prune -o
    -path './__pycache__' -prune -o
    -name '__pycache__' -prune -o
    -path './GENESIS_STORAGE' -prune -o
    -path './genesis_storage' -prune -o
    -type f \( -name '*.py' -o -name '*.yaml' -o -name '*.yml' -o -name '*.html' \
        -o -name '*.txt' -o -name '*.toml' -o -name '*.md' -o -name '*.bat' \
        -o -name '*.sh' -o -name '*.ico' -o -name '*.example' \) -print
)
COUNT=0
while IFS= read -r f; do
    rel="${f#./}"
    mkdir -p "$STAGE/app/$(dirname "$rel")"
    cp "$REPO/$rel" "$STAGE/app/$rel"
    COUNT=$((COUNT + 1))
done < <(cd "$REPO" && find "${STAGE_EXCLUDES[@]}" | LC_ALL=C sort)
if [[ "$COUNT" -lt 50 ]]; then
    ci_error "Staging" "nur $COUNT Dateien gestaged — Arbeitsverzeichnis unvollstaendig?"
    echo "FEHLER: nur $COUNT Dateien gestaged (erwartet >= 50)" >&2
    exit 1
fi
echo "[ZIP]   $COUNT Dateien nach app/ gestaged."

echo "[ZIP] Stagee Installer …"
cp "$REPO/installer/INSTALLIEREN.bat"   "$STAGE/"
cp "$REPO/installer/LIESMICH.txt"       "$STAGE/"
cp "$REPO/installer/install.ps1"        "$STAGE/installer/"
cp "$REPO/installer/uninstall.ps1"      "$STAGE/installer/"
cp "$REPO/installer/genesis_setup.iss"  "$STAGE/installer/"
cp "$REPO/installer/LIESMICH_SETUP.txt" "$STAGE/installer/"

echo "[ZIP] Baue Archiv …"
rm -f "$ZIP"
(cd "$STAGE_ROOT" && zip -r -q "$ZIP" GENESIS_SYSTEM_V2)

# ---------------------------------------------------------- Verifikation
echo "[ZIP] Verifikation 1: Entpacken + Datei-Zahl …"
TESTDIR="/tmp/genesis_zip_test"
rm -rf "$TESTDIR"
mkdir -p "$TESTDIR"
unzip -q "$ZIP" -d "$TESTDIR"
APPFILES=$(find "$TESTDIR/GENESIS_SYSTEM_V2/app" -type f | wc -l)
if [[ "$APPFILES" -ne "$COUNT" ]]; then
    echo "FEHLER: $APPFILES entpackte Dateien != $COUNT gestagte Dateien" >&2
    ci_error "Datei-Zahl" "$APPFILES entpackt != $COUNT gestaged"
    exit 1
fi
for must in "INSTALLIEREN.bat" "LIESMICH.txt" "installer/install.ps1" \
            "installer/uninstall.ps1" "installer/genesis_setup.iss" \
            "app/control_panel.py" "app/genesis.ico" "app/requirements.txt" \
            "app/compliance_rules.yaml" "app/puter_bridge_full.html"; do
    [[ -f "$TESTDIR/GENESIS_SYSTEM_V2/$must" ]] || {
        echo "FEHLER: fehlt im ZIP: $must" >&2
        ci_error "ZIP unvollstaendig" "fehlt: $must"
        exit 1; }
done
echo "[ZIP]   OK — alle $COUNT App-Dateien + Installer vollständig."

echo "[ZIP] Verifikation 2: Nur ASCII in INSTALLIEREN.bat (Codepage-sicher) …"
if LC_ALL=C grep -qP '[^\x00-\x7F]' "$TESTDIR/GENESIS_SYSTEM_V2/INSTALLIEREN.bat"; then
    echo "FEHLER: INSTALLIEREN.bat enthält Nicht-ASCII-Zeichen" >&2
    ci_error "ASCII" "INSTALLIEREN.bat hat Nicht-ASCII-Zeichen"
    exit 1
fi
echo "[ZIP]   OK — .bat ist ASCII-rein."

echo "[ZIP] Verifikation 3: Testsuite im entpackten Zustand …"
if [[ -x /tmp/genesis_vm/venv/bin/python ]]; then
    export GENESIS_STORAGE="/tmp/genesis_zip_storage"
    rm -rf "$GENESIS_STORAGE"
    (cd "$TESTDIR/GENESIS_SYSTEM_V2/app" && /tmp/genesis_vm/venv/bin/python -m pytest tests/ -q --tb=line >/tmp/genesis_zip_pytest.log 2>&1) \
        || { tail -20 /tmp/genesis_zip_pytest.log; echo "FEHLER: Tests im ZIP fehlgeschlagen" >&2
             ci_error "ZIP-Tests" "Testsuite im entpackten ZIP fehlgeschlagen"; ci_dump_pytest_log
             exit 1; }
    tail -1 /tmp/genesis_zip_pytest.log | sed 's/^/[ZIP]   /'
    rm -rf "$GENESIS_STORAGE"
else
    echo "[ZIP]   INFO — VM nicht vorhanden, Testsuite übersprungen (siehe full_check.sh)."
fi

echo "[ZIP] Verifikation 4: Checksumme …"
SIZE=$(du -h "$ZIP" | cut -f1)
SHA=$(sha256sum "$ZIP" | cut -d' ' -f1)
echo "[ZIP]   $ZIP  ($SIZE)"
echo "[ZIP]   SHA256: $SHA"
echo "[ZIP] Fertig."
