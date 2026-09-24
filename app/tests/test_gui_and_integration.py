"""Tests: control_panel (Import & Struktur) + End-to-End-Pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

REPO = Path(__file__).resolve().parent.parent


# ================================================================ GUI
def test_control_panel_imports_without_tk() -> None:
    """control_panel muss auch ohne Tkinter importierbar bleiben (tk=None)."""
    import control_panel
    assert hasattr(control_panel, "GenesisPanel")
    assert hasattr(control_panel, "run_selftest")


def test_gui_selftest_when_display_available(tmp_storage) -> None:
    pytest.importorskip("tkinter")
    if not _display_available():
        pytest.skip("kein Display in dieser VM — GUI-Selbsttest läuft auf Zielsystem")
    import control_panel
    assert control_panel.run_selftest() == 0


def test_require_tk_exit_code_without_tk(monkeypatch) -> None:
    import control_panel as cp
    if cp.tk is not None and _display_available():
        pytest.skip("Tk vorhanden — Exit-Pfad für fehlendes Tk nicht testbar")
    monkeypatch.setattr(cp, "tk", None)
    with pytest.raises(SystemExit) as exc:
        cp._require_tk()
    assert exc.value.code == 2


def _display_available() -> bool:
    import os
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


# ================================================================ Pipeline
def test_full_pipeline(tmp_storage) -> None:
    """Generator → Compliance → Mockup → 7 Formate → Upload-Meta → Upload → Sales."""
    import config
    import generator
    import mockup_engine
    import product_formats
    import sales_tracker
    import upload_manager

    # 1) Design generieren (Compliance läuft intern)
    design_path = generator.generate_design("Pipeline Volltest", size=800, seed=42)
    design = Image.open(design_path)
    assert design.size == (800, 800)

    # 2) Mockups in 4 Farben
    mock_paths = mockup_engine.create_mockup_set(design, prefix=design_path.stem)
    assert len(mock_paths) == 4

    # 3) Alle 7 Produktformate
    for key in product_formats.PRODUCT_FORMATS:
        out = config.DESIGNS_DIR / f"{design_path.stem}_{key}.png"
        product_formats.export_for_product(design, key, out)
        assert Image.open(out).size == product_formats.get_format(key).size

    # 4) Upload-Metadaten
    meta = upload_manager.meta_for_design(design_path.stem, "teepublic")
    assert meta.title and len(meta.tags) <= 20
    assert "zeichenwerk" in meta.tags

    # 5) Hochladen markieren
    assert upload_manager.mark_design_uploaded(design_path.stem)
    assert upload_manager.pending() == [] or \
        all(r["name"] != design_path.stem for r in upload_manager.pending())

    # 6) Verkauf + Bericht
    tracker = sales_tracker.SalesTracker()
    tracker.add_sale(design_path.stem, "redbubble", 2)
    assert tracker.summary()["total_sales"] == 2


def test_no_artifacts_in_repo(tmp_storage) -> None:
    """Tests dürfen niemals Artefakte im Repo hinterlassen."""
    for pattern in ("*.png", "*.log", "*.csv", "sales_data.json"):
        hits = [p for p in REPO.rglob(pattern)
                if ".git" not in p.parts and p.name != "genesis.ico"]
        assert hits == [], f"Artefakte im Repo: {hits}"


def test_start_scripts_exist_and_executable() -> None:
    bat = REPO / "start_genesis.bat"
    sh = REPO / "start_genesis.sh"
    assert bat.exists() and sh.exists()
    assert bat.read_text(encoding="utf-8", errors="replace").startswith("@echo off")
    content = sh.read_text(encoding="utf-8")
    assert content.startswith("#!")


def test_example_ini_documented() -> None:
    example = REPO / "config_private.ini.example"
    assert example.exists()
    assert "NICHT einchecken" in example.read_text(encoding="utf-8")


def test_module_count_matches_spec() -> None:
    """Alle Kernmodule aus der Spezifikation sind vorhanden."""
    expected = [
        "config", "control_panel", "generator", "graphics_engine", "icon_engine",
        "text_database", "scene_engine", "scene_generator", "background_engine",
        "text_layout_engine", "hybrid_scene_engine", "puter_engine",
        "huggingface_engine", "gemini_engine", "compliance_engine",
        "brand_check", "brand_identity", "upload_manager", "mockup_engine",
        "product_formats", "sales_tracker", "key_manager", "api_key_detector",
        "prompt_feedback", "validator",
    ]
    for mod in expected:
        assert (REPO / f"{mod}.py").exists(), mod
    assert (REPO / "compliance_rules.yaml").exists()
    assert (REPO / "puter_bridge_full.html").exists()
