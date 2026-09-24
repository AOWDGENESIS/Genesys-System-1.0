@echo off
REM ============================================================
REM  GENESIS SYSTEM / Zeichenwerk - Windows Starter
REM  Startet das Control Panel mit allen 11 Tabs
REM ============================================================
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden. Bitte von python.org installieren.
    pause
    exit /b 1
)

REM Abhaengigkeiten pruefen (bestehende Installation wird nicht angefasst)
python -c "import PIL, yaml, requests" >nul 2>nul
if errorlevel 1 (
    echo Installiere Abhaengigkeiten ...
    python -m pip install -r requirements.txt
)

echo Starte GENESIS SYSTEM ...
python control_panel.py
if errorlevel 1 pause
endlocal
