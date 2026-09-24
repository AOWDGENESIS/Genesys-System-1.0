# GENESIS SYSTEM / Zeichenwerk — V2

[![CI](https://github.com/AOWDGENESIS/Entwicklungen/actions/workflows/ci.yml/badge.svg?branch=arena/01a0750a-entwicklungen)](https://github.com/AOWDGENESIS/Entwicklungen/actions/workflows/ci.yml)

**"Zeichen setzen. Jeden Tag."**

Automatisierte Print-on-Demand Design-Pipeline (Python 3.10+, Tkinter-GUI mit 11 Tabs,
kompletter Compliance-/Markenschutz-Prüfung, Multi-Plattform-Upload-Workflow).

Dies ist der **komplette, korrigierte und getestete Neuaufbau** (V2.0) des ursprünglichen
Systems — mit portablen Pfaden, sauberem Logging, Fehlerbehandlung und einer
vollständigen Testsuite (340+ Tests, alle grün).

---

## Schnellstart

**Windows-Installation (empfohlen):**
`releases/GENESIS_SYSTEM_V2_Setup.zip` entpacken → `INSTALLIEREN.bat` doppelklicken.
Der Installer prüft/installiert Python, richtet alles ein und trägt das Programm
unter "Apps & Features" ein (Details: `installer/LIESMICH.txt`).

**Windows (direkt aus dem Repo):**
```
start_genesis.bat
```

**Linux / macOS:**
```
./start_genesis.sh
```

**Headless / CLI (ohne GUI):**
```
python validator.py --stats                 # Regelwerk-Statistik
python validator.py "But First Coffee"      # Text prüfen
python validator.py --batch                 # gesamte Text-Datenbank prüfen
python control_panel.py --selftest          # GUI-Selbsttest (braucht Display)
```

## Vollprüfung (Test-VM)

Jede Prüfung läuft **komplett von vorne** in einer frischen, isolierten VM
(`/tmp/genesis_vm` — frisches Virtualenv, eigener Storage, kein Müll im Repo):

```
bash scripts/full_check.sh
```

Ablauf je Runde: VM neu bauen → Workspace-Sauberkeit → ruff (statisch) →
pytest (340+ Tests) → CLI-Smoke → Pipeline-Smoke (Design→Mockup→7 Formate→Upload→Sales)
→ GUI-Selbsttest (falls Tkinter+Display vorhanden) → Storage entsorgen.

Ergebnis der letzten Runde: **ALLE PRÜFUNGEN GRÜN ✓**

## Struktur

| Bereich | Module |
|---|---|
| Kern | `config.py`, `control_panel.py`, `font_manager.py`, `status_io.py` |
| Design-Engines | `generator.py`, `graphics_engine.py`, `icon_engine.py`, `text_database.py` |
| Szenen | `scene_engine.py`, `scene_generator.py`, `background_engine.py`, `text_layout_engine.py`, `hybrid_scene_engine.py` |
| KI-Backends | `puter_engine.py` (+ `puter_bridge_full.html`), `huggingface_engine.py`, `gemini_engine.py` |
| Recht & Brand | `compliance_engine.py`, `compliance_rules.yaml`, `brand_check.py`, `brand_identity.py` |
| Verkauf | `upload_manager.py`, `mockup_engine.py`, `product_formats.py`, `sales_tracker.py` |
| Infra | `key_manager.py`, `api_key_detector.py`, `prompt_feedback.py`, `validator.py` |
| Qualität | `tests/` (18 Dateien), `scripts/` (VM + Vollprüfung), `ruff.toml` |

## Speicherorte

1. `GENESIS_STORAGE` Umgebungsvariable (höchste Priorität)
2. Windows: `F:\GENESIS_STORAGE` (wenn vorhanden)
3. Fallback: `~/.zeichenwerk/GENESIS_STORAGE` (Linux/macOS) bzw. `%APPDATA%\Zeichenwerk\...`

Generierte Designs, Mockups, Logs und status.csv liegen **immer** im Storage —
niemals im Repo.

## API-Keys

`config_private.ini` (gitignored) oder der API-Schlüssel-Tab in der GUI.
Formate werden automatisch erkannt: Gemini `AIza…`, HuggingFace `hf_…`, OpenAI `sk-…`.
Keys werden in Logs **maskiert** (getestet).

## Wichtige Verbesserungen gegenüber V1

- Portable Pfade statt hartkodiertem `F:\` — läuft identisch auf Windows/Linux/macOS
- Font-Fallback-Kette (Impact → DejaVu/Liberation) auf allen Systemen
- Compliance: Whitelist, Severity (block/warn), Umlaut-Folding,
  false-positive-sichere Tippfehler-Erkennung
- GUI läuft ohne Tkinter weiter (CLI), GUI-Selbsttest-Modus
- Deterministische Generierung (Seed) → reproduzierbare Tests
- 340+ Tests, statische Prüfung (ruff), atomares CSV-Schreiben, Thread-Sicherheit

Details: siehe `DOKUMENTATION.md`.
