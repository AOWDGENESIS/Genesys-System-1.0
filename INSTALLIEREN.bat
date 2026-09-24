@echo off
REM ============================================================
REM  ZEICHENWERK / GENESIS SYSTEM - Windows-Installation
REM  Einfach diese Datei per Doppelklick starten.
REM  (Keine Admin-Rechte noetig - Installation pro Benutzer)
REM ============================================================
title Zeichenwerk GENESIS SYSTEM - Installation
cd /d "%~dp0"

where powershell >nul 2>nul
if errorlevel 1 (
    echo FEHLER: PowerShell nicht gefunden.
    echo Windows 10 oder 11 wird benoetigt.
    pause
    exit /b 1
)

echo.
echo Installation wird gestartet ...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "installer\install.ps1" %*
if errorlevel 1 (
    echo.
    echo Installation FEHLGESCHLAGEN - siehe Meldung oben.
    pause
    exit /b 1
)

exit /b 0
