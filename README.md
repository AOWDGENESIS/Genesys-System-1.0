# Zeichenwerk / GENESIS SYSTEM

Python-basierte Windows-Desktopanwendung fuer Design-Workflows, grafische Assets und Compliance-Pruefungen. Der Installer und die tatsaechlichen Funktionen im Quellcode sind massgeblich; optionale externe Dienste koennen eigene Voraussetzungen, Kosten und Datenschutzbedingungen haben.

## Funktionen und Komponenten

- Desktop-Workflow fuer Design- und Projektdateien.
- Validierungswerkzeuge fuer konfigurierte Text-/Marken- oder Compliance-Regeln.
- Optionale Grafik- und Mockup-Funktionen, soweit die jeweilige Installation und Konfiguration sie bereitstellt.
- Windows-Installer mit Benutzerinstallation ohne Administratorrechte als Standard.
- Eigener Python-Umgebungskontext, damit Pakete nicht in die System-Python-Installation geschrieben werden.
- Nutzerdaten und Projektdateien sollen bei der Deinstallation erhalten bleiben; sichere diese Daten dennoch vor Updates und Deinstallation.

## Voraussetzungen

- Windows 10/11.
- Python 3.10 oder neuer. Der Installer kann versuchen, Python ueber winget zu installieren; dafuer kann eine Internetverbindung erforderlich sein.
- Internetverbindung fuer Erstinstallation oder optionale Provider, falls benoetigte Pakete nicht lokal verfuegbar sind.

## Installation

1. Lade das Repository als ZIP herunter und entpacke es vollstaendig.
2. Starte `INSTALLIEREN.bat`.
3. Folge den Hinweisen des Installers.
4. Starte die Anwendung ueber die angelegte Zeichenwerk-Verknuepfung oder den dokumentierten Starter im Installationsordner.

Die Standardinstallation erfolgt im Benutzerprofil. Eine systemweite Installation kann Administratorrechte erfordern. Lies vor der Installation den Installer-Code und die Dokumentation, wenn du die genauen Aenderungen nachvollziehen moechtest.

## Daten und Deinstallation

Der konfigurierte Speicherort kann `F:\GENESIS_STORAGE`, `%APPDATA%\Zeichenwerk\GENESIS_STORAGE` oder der ueber `GENESIS_STORAGE` gesetzte Pfad sein. Pruefe den tatsaechlichen Pfad in deiner Installation, bevor du Daten verschiebst oder entfernst.

Deinstallation erfolgt ueber Windows-Einstellungen > Apps oder die vom Programm angelegte Deinstallationsverknuepfung. Sichere Designs, Logs und Verkaufsdaten vorher separat.

## Entwicklung und Tests

- Einstieg: `app/` und die begleitenden Dokumentationsdateien.
- Installationsskript: `INSTALLIEREN.bat`.
- CLI-Validierung: `validator.py --stats` mit der Python-Umgebung des Projekts, sofern die Datei in deiner ausgecheckten Version vorhanden ist.
- Installer fuer die klassische Setup-Oberflaeche: `installer/genesis_setup.iss` (Inno Setup 6 erforderlich).

Testbefehle koennen je nach Projektstand variieren. Fuehre die vorhandenen Tests aus und dokumentiere Windows-Version, Python-Version und Ergebnis, bevor du eine Version als geprueft veroeffentlichst.

## Sicherheit und verantwortungsvolle Nutzung

- Verwende nur eigene oder entsprechend lizenzierte Bilder, Schriften, Logos und Vorlagen.
- Compliance-Pruefungen sind Hilfsmittel und keine Rechtsberatung oder Garantie fuer Plattformfreigaben.
- API-Schluessel und Passwoerter gehoeren nicht in Git, Screenshots oder Logs.
- Pruefe Installer und externe Downloads vor dem Ausfuehren.

## Mitwirken

Bitte melde reproduzierbare Fehler mit anonymisierten Logs. Aenderungen an Installation, Speicherpfaden, Datenloeschung und externen Providern sollten eigene Tests enthalten.

## Lizenz

Der Projektquellcode wird unter MIT lizenziert. Siehe [LICENSE](LICENSE). Mitgelieferte Drittanbieterbibliotheken, Fonts, Bilder und externe Provider koennen separaten Lizenzbedingungen unterliegen.
