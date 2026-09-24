#Requires -Version 5.1
<#
.SYNOPSIS
    Zeichenwerk GENESIS SYSTEM - Deinstallation

.BESCHREIBUNG
    - Entfernt Programmordner, Verknuepfungen und Registry-Eintrag
    - Designs/Logs/Verkaufsdaten (GENESIS_STORAGE) werden BEWAHRT
#>
[CmdletBinding()]
param([switch]$Silent)

$ErrorActionPreference = 'Stop'

function Find-InstallDir {
    foreach ($base in @('HKCU:\', 'HKLM:\')) {
        $key = $base + 'Software\Microsoft\Windows\CurrentVersion\Uninstall\ZeichenwerkGENESIS'
        if (Test-Path $key) {
            $dir = (Get-ItemProperty $key).InstallLocation
            if ($dir -and (Test-Path $dir)) { return $dir }
        }
    }
    $fallback = Join-Path $env:LOCALAPPDATA 'Programs\Zeichenwerk'
    if (Test-Path $fallback) { return $fallback }
    return $null
}

Write-Host ''
Write-Host 'Zeichenwerk GENESIS SYSTEM - Deinstallation' -ForegroundColor Magenta
Write-Host '===========================================' -ForegroundColor Magenta

$InstallDir = Find-InstallDir
if (-not $InstallDir) {
    Write-Host 'Keine Installation gefunden.' -ForegroundColor Yellow
    exit 0
}

Write-Host ('Installationsordner: ' + $InstallDir)
Write-Host 'Designs/Logs/Verkaufsdaten (GENESIS_STORAGE) werden NICHT geloescht.'
if (-not $Silent) {
    $answer = Read-Host 'Wirklich deinstallieren? (J/N)'
    if ($answer -ne 'J' -and $answer -ne 'j' -and $answer -ne 'Y' -and $answer -ne 'y') {
        Write-Host 'Abgebrochen.'
        exit 0
    }
}

# Laufende Instanz beenden (nur Prozesse aus dem Installationsordner)
Get-Process pythonw, python -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -and $_.Path.StartsWith($InstallDir, [System.StringComparison]::OrdinalIgnoreCase) } |
    Stop-Process -Force -ErrorAction SilentlyContinue

# 1) Verknuepfungen
$desktopLinks = @(
    (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Zeichenwerk.lnk'),
    (Join-Path ([Environment]::GetFolderPath('CommonDesktopDirectory')) 'Zeichenwerk.lnk')
)
foreach ($lnk in $desktopLinks) {
    if (Test-Path $lnk) { Remove-Item $lnk -Force; Write-Host ('Entfernt: ' + $lnk) }
}
foreach ($menu in @(
    (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Zeichenwerk'),
    (Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs\Zeichenwerk')
)) {
    if (Test-Path $menu) { Remove-Item $menu -Recurse -Force; Write-Host ('Entfernt: ' + $menu) }
}

# 2) Registry
foreach ($base in @('HKCU:\', 'HKLM:\')) {
    $key = $base + 'Software\Microsoft\Windows\CurrentVersion\Uninstall\ZeichenwerkGENESIS'
    if (Test-Path $key) {
        $del = $false
        try { Remove-Item $key -Force; $del = $true } catch { }
        if ($del) { Write-Host ('Registry-Eintrag entfernt: ' + $key) }
    }
}

# 3) Programmordner
if (Test-Path $InstallDir) {
    Remove-Item $InstallDir -Recurse -Force
    Write-Host ('Entfernt: ' + $InstallDir)
}

Write-Host ''
Write-Host 'Deinstallation abgeschlossen.' -ForegroundColor Green
$storageHint = Join-Path $env:APPDATA 'Zeichenwerk\GENESIS_STORAGE'
if (Test-Path $storageHint) {
    Write-Host ('Ihre Designs liegen weiterhin in: ' + $storageHint) -ForegroundColor Yellow
}
exit 0
