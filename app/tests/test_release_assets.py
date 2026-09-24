"""Tests: Release-Assets (genesis.ico, Windows-Installer, Starter).

Die Tests funktionieren in beiden Layouts:
  - Repo:   tests/ neben installer/ (INSTALLIEREN.bat in installer/)
  - ZIP:    app/tests/ — installer/ und INSTALLIEREN.bat eine Ebene ueber app/
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent


def _asset(*rels: str) -> Path:
    """Löst einen Asset-Pfad im Repo- ODER ZIP-Layout auf (erste Alternative gewinnt)."""
    for rel in rels:
        for base in (REPO, REPO.parent):
            candidate = base / rel
            if candidate.exists():
                return candidate
    return REPO / rels[0]  # für saubere Fehlermeldungen


# ---------------------------------------------------------------- Icon
def test_genesis_ico_valid_and_multi_size() -> None:
    ico = REPO / "genesis.ico"
    assert ico.exists(), "genesis.ico fehlt"
    assert ico.stat().st_size > 1000
    img = Image.open(ico)
    assert img.size[0] >= 256  # größte enthaltene Seite
    # ICO-Container mit mehreren Größen (PIL listet sie alle auf)
    assert len(getattr(img, "info", {}).get("sizes", set())) >= 4


def test_genesis_ico_not_empty_image() -> None:
    img = Image.open(REPO / "genesis.ico").convert("RGBA")
    alpha = img.getchannel("A")
    assert alpha.getextrema()[1] > 0     # sichtbare Pixel
    colors = img.convert("RGB").getcolors(maxcolors=256000)
    assert colors and len(colors) > 4   # mehr als eine Farbe


# ---------------------------------------------------------------- Installer
def test_installer_files_present() -> None:
    candidates = (
        ("installer/INSTALLIEREN.bat", "INSTALLIEREN.bat"),  # ZIP: im Root
        ("installer/install.ps1",),
        ("installer/uninstall.ps1",),
        ("installer/genesis_setup.iss",),
        ("installer/LIESMICH.txt", "LIESMICH.txt"),  # ZIP: im Root
    )
    for rels in candidates:
        path = _asset(*rels)
        assert path.exists(), rels[0]


def test_bat_is_pure_ascii() -> None:
    """cmd.exe interpretiert .bat in der lokalen Codepage — nur ASCII ist sicher."""
    raw = _asset("installer/INSTALLIEREN.bat", "INSTALLIEREN.bat").read_bytes()
    raw.decode("ascii")


def test_install_ps1_core_steps_present() -> None:
    """Der Installer muss die Kernschritte enthalten (Update-sicher)."""
    src = _asset("installer/install.ps1").read_text(encoding="utf-8-sig")
    for must in (
        "winget",                    # Python-Nachinstallation
        "venv",                      # eigene Programm-Umgebung
        "requirements.txt",          # Paketinstallation
        "WScript.Shell",             # Verknüpfungen
        "Uninstall\\ZeichenwerkGENESIS",  # Apps-&-Features-Eintrag
        "GENESIS.cmd",               # Starter
    ):
        assert must in src, must


def test_uninstall_ps1_preserves_storage() -> None:
    src = _asset("installer/uninstall.ps1").read_text(encoding="utf-8-sig")
    assert "GENESIS_STORAGE" in src
    assert "NICHT gel" in src  # "...werden NICHT geloescht"


def test_starters_reference_control_panel() -> None:
    bat = _asset("start_genesis.bat").read_text(encoding="utf-8", errors="replace")
    sh = _asset("start_genesis.sh").read_text(encoding="utf-8")
    assert "control_panel.py" in bat
    assert "control_panel.py" in sh


def test_readme_mentions_installation() -> None:
    readme = REPO / "README.md"  # README liegt immer neben tests/
    content = readme.read_text(encoding="utf-8")
    assert "INSTALLIEREN" in content or "start_genesis" in content
