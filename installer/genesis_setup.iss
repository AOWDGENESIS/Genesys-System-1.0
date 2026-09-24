; ============================================================
;  ZEICHENWERK / GENESIS SYSTEM — Klassischer Setup.exe-Assistent
;  (OPTIONAL — Inno Setup 6)
;
;  Was ist das?
;    Diese Datei erzeugt mit Inno Setup 6 eine klassische
;    setup.exe mit Assistent (Weiter/Zurueck, Lizenzseite,
;    Fortschrittsbalken) — wie bei "richtigen" Windows-Programmen.
;
;  So bauen Sie die setup.exe:
;    1. Inno Setup 6 kostenlos laden: https://jrsoftware.org/isdl.php
;    2. Diese Datei (genesis_setup.iss) in Inno Setup oeffnen
;    3. Strg+F9 (Kompilieren) → setup.exe liegt im Ordner Output\
;
;  Wichtig: Der Ordner dieser ISS-Datei muss beim Kompilieren so
;  aussehen wie im ZIP (app\ und installer\ neben dieser Datei).
;  Der Assistent entpackt und ruft danach dieselbe install.ps1
;  auf wie INSTALLIEREN.bat (eine einzige Installations-Logik:
;  Python-Check, venv, Pakete, Verknuepfungen, Apps&Features).
; ============================================================

#define MyAppName "Zeichenwerk GENESIS SYSTEM"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Zeichenwerk"
#define MyAppExeName "GENESIS.cmd"
#define MyAppId "{7C4A1E52-9B3D-4F6A-8E21-2D5C9B7A4E01}"

[Setup]
AppId={{#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Zeichenwerk
DefaultGroupName=Zeichenwerk
; Installation pro Benutzer (kein Admin noetig, wie INSTALLIEREN.bat).
; Fuer alle Benutzer: PrivilegesRequired=admin + DefaultDirName={autopf}\Zeichenwerk
PrivilegesRequired=lowest
Uninstallable=no
CreateUninstallRegKey=no
; Deinstallation uebernimmt install.ps1/uninstall.ps1 (Apps & Features)
OutputDir=Output
OutputBaseFilename=Zeichenwerk_Setup
SetupIconFile=..\app\genesis.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=..\app\README.md
InfoBeforeFile=LIESMICH_SETUP.txt

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "desktopicon\common"; Description: "{cm:ForAllUsers}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: exclusive unchecked

[Files]
Source: "..\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "install.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion
Source: "uninstall.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion

[Run]
; Einrichtung (Python, venv, Pakete, Verknuepfungen, Registry) nach dem Entpacken
Filename: "powershell.exe"; `
    Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installer\install.ps1"" -SourceDir ""{app}"" -Silent"; `
    Description: "{#MyAppName} einrichten (Python-Umgebung, Verknuepfungen)"; `
    Flags: runasoriginaluser postinstall; WorkingDir: "{app}"
