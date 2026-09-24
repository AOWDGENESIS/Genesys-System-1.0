#Requires -Version 5.1
<#
.SYNOPSIS
    GENESIS SYSTEM / Zeichenwerk - Windows-Installer (wie ein echtes Programm)

.BESCHREIBUNG
    - Kopiert die Anwendung nach %LOCALAPPDATA%\Programs\Zeichenwerk
      (oder mit -AllUsers nach C:\Program Files\Zeichenwerk, dann mit Admin)
    - Prueft Python 3.10+ und installiert es fehlend via winget
    - Erstellt eine eigene virtuelle Python-Umgebung (venv) + Abhaengigkeiten
    - Erstart Startmenue- + Desktop-Verknuepfung mit Programm-Icon
    - Traegt das Programm unter "Apps & Features" ein (mit Deinstallation)
    - Erneutes Ausfuehren = Update (ueberschreibt, richtet neu ein)

.PARAMETER AllUsers
    Installation fuer alle Benutzer (Program Files + HKLM, Admin-Rechte).

.PARAMETER NoDesktopShortcut
    Keine Desktop-Verknuepfung erstellen.

.PARAMETER Silent
    Keine Rueckfragen, Programm am Ende nicht starten.

.PARAMETER SourceDir
    (Inno Setup Modus) Dateien liegen bereits im Ziel - Kopierschritt ueberspringen.

.PARAMETER InstallDir
    Abweichendes Zielverzeichnis.
#>
[CmdletBinding()]
param(
    [switch]$AllUsers,
    [switch]$NoDesktopShortcut,
    [switch]$Silent,
    [string]$SourceDir = "",
    [string]$InstallDir = ""
)

$ErrorActionPreference = 'Stop'
$AppName    = 'Zeichenwerk GENESIS SYSTEM'
$AppVersion = '2.0.0'
$Publisher  = 'Zeichenwerk'
$RegKey     = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\ZeichenwerkGENESIS'

function Write-Step { param($Msg) Write-Host ''; Write-Host ('==> ' + $Msg) -ForegroundColor Cyan }
function Write-Ok   { param($Msg) Write-Host ('    ' + $Msg) -ForegroundColor Green }
function Write-Warn2{ param($Msg) Write-Host ('    ' + $Msg) -ForegroundColor Yellow }

# ------------------------------------------------------------------ Banner
Write-Host ''
Write-Host '====================================================' -ForegroundColor Magenta
Write-Host '  ZEICHENWERK  /  GENESIS SYSTEM  v' -NoNewline -ForegroundColor Magenta
Write-Host $AppVersion -ForegroundColor Magenta
Write-Host '  "Zeichen setzen. Jeden Tag."' -ForegroundColor Magenta
Write-Host '====================================================' -ForegroundColor Magenta

# -------------------------------------------------- Admin-Relaunch (AllUsers)
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($AllUsers -and -not $isAdmin) {
    Write-Step 'Admin-Rechte werden benoetigt (Installation fuer alle Benutzer)'
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $PSCommandPath + '"'), '-AllUsers')
    if ($Silent)        { $argList += '-Silent' }
    if ($NoDesktopShortcut) { $argList += '-NoDesktopShortcut' }
    if ($SourceDir)     { $argList += ('-SourceDir "' + $SourceDir + '"') }
    if ($InstallDir)    { $argList += ('-InstallDir "' + $InstallDir + '"') }
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList ($argList -join ' ')
    exit 0
}

# ------------------------------------------------------------------ Zielpfad
if (-not $InstallDir) {
    if ($AllUsers) { $InstallDir = Join-Path $env:ProgramFiles 'Zeichenwerk' }
    else           { $InstallDir = Join-Path $env:LOCALAPPDATA 'Programs\Zeichenwerk' }
}
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$zipAppDir  = Join-Path (Split-Path -Parent $scriptRoot) 'app'

# ------------------------------------------------------------------ 1) Kopieren
if ($SourceDir) {
    Write-Step 'Dateien liegen bereits im Ziel (Inno-Setup-Modus)'
    $InstallDir = $SourceDir
} else {
    Write-Step ('Installiere nach: ' + $InstallDir)
    if (-not (Test-Path $zipAppDir)) { throw 'Ordner "app" nicht gefunden - ZIP unvollstaendig?' }
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    robocopy $zipAppDir $InstallDir /E /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw ('Dateikopie fehlgeschlagen (robocopy-Code ' + $LASTEXITCODE + ')') }
    # Installer-Skripte mitkopieren (fuer Updates + Deinstallation)
    New-Item -ItemType Directory -Force -Path (Join-Path $InstallDir 'installer') | Out-Null
    Copy-Item (Join-Path $scriptRoot 'install.ps1')   (Join-Path $InstallDir 'installer') -Force
    Copy-Item (Join-Path $scriptRoot 'uninstall.ps1') (Join-Path $InstallDir 'installer') -Force
    Write-Ok 'Programmdateien kopiert.'
}

# ------------------------------------------------------------------ 2) Python
Write-Step 'Pruefe Python 3.10 oder neuer ...'

function Find-Python {
    $candidates = @()
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        try {
            $out = & py -3 -c 'import sys; print(sys.executable)' 2>$null
            if ($LASTEXITCODE -eq 0 -and $out) { $candidates += [string]$out }
        } catch { }
    }
    $py2 = Get-Command python -ErrorAction SilentlyContinue
    if ($py2) { $candidates += $py2.Source }
    foreach ($exe in $candidates) {
        try {
            $ver = & $exe -c 'import sys; print(sys.version_info[0]*100+sys.version_info[1])' 2>$null
            if ($LASTEXITCODE -eq 0 -and $ver) {
                if ([int]$ver -ge 310) { return $exe }
            }
        } catch { }
    }
    return $null
}

$pythonExe = Find-Python
if (-not $pythonExe) {
    Write-Warn2 'Python nicht gefunden - versuche Installation ueber winget ...'
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        & winget install --id Python.Python.3.12 -e --silent --accept-source-agreements --accept-package-agreements | Out-Null
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                    [Environment]::GetEnvironmentVariable('Path', 'User')
        $pythonExe = Find-Python
    }
}
if (-not $pythonExe) {
    Write-Host ''
    Write-Host '    Python konnte nicht automatisch installiert werden.' -ForegroundColor Red
    Write-Host '    Bitte Python 3.12 von https://www.python.org/downloads/ installieren' -ForegroundColor Red
    Write-Host '    (Haekchen bei "Add python.exe to PATH" setzen) und Installation' -ForegroundColor Red
    Write-Host '    erneut starten.' -ForegroundColor Red
    Start-Process 'https://www.python.org/downloads/'
    exit 1
}
$pyVer = & $pythonExe -c 'import sys; print("%d.%d" % sys.version_info[:2])'
Write-Ok ('Python ' + $pyVer + ' gefunden: ' + $pythonExe)

# ------------------------------------------------------------------ 3) venv + Pakete
Write-Step 'Richte Programm-Umgebung ein (venv + Pakete) ...'
$venvDir = Join-Path $InstallDir 'venv'
$venvPython = Join-Path $venvDir 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    & $pythonExe -m venv $venvDir
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) { throw 'Virtuelle Umgebung konnte nicht erstellt werden.' }
    Write-Ok 'Virtuelle Python-Umgebung erstellt.'
}
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r (Join-Path $InstallDir 'requirements.txt') --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host '    Abhaengigkeiten konnten nicht geladen werden (kein Internet?).' -ForegroundColor Red
    Write-Host '    Spater manuell nachholen:' -ForegroundColor Red
    Write-Host ('      "' + $venvPython + '" -m pip install -r "' + (Join-Path $InstallDir 'requirements.txt') + '"') -ForegroundColor Yellow
    exit 1
}
Write-Ok 'Abhaengigkeiten (Pillow, PyYAML, requests) installiert.'

# ------------------------------------------------------------------ 4) Starter
Write-Step 'Erstelle Programm-Starter ...'
$pythonw = Join-Path $venvDir 'Scripts\pythonw.exe'
$mainPy  = Join-Path $InstallDir 'control_panel.py'

$launcher = Join-Path $InstallDir 'GENESIS.cmd'
('@start "" "' + $pythonw + '" "' + $mainPy + '"') | Out-File -FilePath $launcher -Encoding ascii
$launcherDebug = Join-Path $InstallDir 'GENESIS-Debug.cmd'
('@echo off' + "`r`n" + '"' + (Join-Path $venvDir 'Scripts\python.exe') + '" "' + $mainPy + '"' + "`r`n" + 'pause') |
    Out-File -FilePath $launcherDebug -Encoding ascii
Write-Ok 'GENESIS.cmd (Programm) und GENESIS-Debug.cmd (mit Konsolen-Log) erstellt.'

# ------------------------------------------------------------------ 5) Verknuepfungen
Write-Step 'Erstelle Verknuepfungen ...'
$sh = New-Object -ComObject WScript.Shell
if ($AllUsers) {
    $startMenu = Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs\Zeichenwerk'
    $desktop   = [Environment]::GetFolderPath('CommonDesktopDirectory')
} else {
    $startMenu = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Zeichenwerk'
    $desktop   = [Environment]::GetFolderPath('Desktop')
}
New-Item -ItemType Directory -Force -Path $startMenu | Out-Null

function New-Shortcut { param($Path, $Target, $Arguments, $Icon)
    $lnk = $sh.CreateShortcut($Path)
    $lnk.TargetPath = $Target
    if ($Arguments)   { $lnk.Arguments = $Arguments }
    if ($Icon)        { $lnk.IconLocation = $Icon }
    $lnk.WorkingDirectory = $InstallDir
    $lnk.Save()
}
$ico = Join-Path $InstallDir 'genesis.ico'
New-Shortcut (Join-Path $startMenu 'Zeichenwerk.lnk') $launcher '' $ico
New-Shortcut (Join-Path $startMenu 'Zeichenwerk deinstallieren.lnk') 'powershell.exe' `
    ('-NoProfile -ExecutionPolicy Bypass -File "' + (Join-Path $InstallDir 'installer\uninstall.ps1') + '"') 'powershell.exe,0'
if (-not $NoDesktopShortcut) {
    New-Shortcut (Join-Path $desktop 'Zeichenwerk.lnk') $launcher '' $ico
    Write-Ok 'Desktop-Verknuepfung erstellt.'
}
Write-Ok 'Startmenue-Ordner "Zeichenwerk" erstellt (inkl. Deinstallation).'

# ------------------------------------------------------------------ 6) Registry
Write-Step 'Trage Programm in "Apps & Features" ein ...'
$regBase = if ($AllUsers) { 'HKLM:\' + $RegKey } else { 'HKCU:\' + $RegKey }
New-Item -Path $regBase -Force | Out-Null
$sizeKB = [math]::Round(((Get-ChildItem $InstallDir -Recurse -File -ErrorAction SilentlyContinue |
    Measure-Object -Property Length -Sum).Sum) / 1KB)
Set-ItemProperty $regBase -Name DisplayName     -Value 'Zeichenwerk (GENESIS SYSTEM)'
Set-ItemProperty $regBase -Name DisplayVersion  -Value $AppVersion
Set-ItemProperty $regBase -Name Publisher       -Value $Publisher
Set-ItemProperty $regBase -Name InstallLocation -Value $InstallDir
Set-ItemProperty $regBase -Name DisplayIcon     -Value $ico
Set-ItemProperty $regBase -Name EstimatedSize   -Value $sizeKB
Set-ItemProperty $regBase -Name NoModify        -Value 1
Set-ItemProperty $regBase -Name InstallDate     -Value (Get-Date -Format 'yyyyMMdd')
Set-ItemProperty $regBase -Name UninstallString -Value ('powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + (Join-Path $InstallDir 'installer\uninstall.ps1') + '"')
Write-Ok ('Registriert (' + $sizeKB + ' KB). Deinstallation ueber "Apps & Features" moeglich.')

# ------------------------------------------------------------------ 7) Speicherorte
Write-Step 'Speicherort fuer Designs ...'
if (Test-Path 'F:\GENESIS_STORAGE') {
    Write-Ok 'F:\GENESIS_STORAGE vorhanden - wird automatisch genutzt (wie bisher).'
} else {
    $defaultStorage = Join-Path $env:APPDATA 'Zeichenwerk\GENESIS_STORAGE'
    Write-Ok ('Standard: ' + $defaultStorage)
    Write-Warn2 'Alternativ: Umgebungsvariable GENESIS_STORAGE setzen oder F:\GENESIS_STORAGE anlegen.'
}

# ------------------------------------------------------------------ Fertig
Write-Host ''
Write-Host '====================================================' -ForegroundColor Green
Write-Host '  INSTALLATION ERFOLGREICH' -ForegroundColor Green
Write-Host ('  Ort:        ' + $InstallDir)
Write-Host ('  Startmenue: Zeichenwerk')
Write-Host '  Deinstallation: Apps & Features -> Zeichenwerk'
Write-Host '====================================================' -ForegroundColor Green

if (-not $Silent) {
    $answer = Read-Host 'Jetzt starten? (J/N)'
    if ($answer -eq 'J' -or $answer -eq 'j' -or $answer -eq 'Y' -or $answer -eq 'y') {
        Start-Process $launcher
    }
}
exit 0
