# GENESIS SYSTEM / ZEICHENWERK — Technische Dokumentation V2.0

Stand: September 2026 · Nachbau und Weiterentwicklung der V1-Spezifikation (April 2026)

================================================================
 1. SYSTEMÜBERSICHT
================================================================

Name:            GENESIS SYSTEM
Brand:           Zeichenwerk
Slogan:          "Zeichen setzen. Jeden Tag." / "Bold designs for bold people."
Zweck:           Automatisierte Print-on-Demand Design-Pipeline
Betriebsart:      Lokal (Windows PC; V2 zusätzlich Linux/macOS-fähig)
Sprache:         Python 3.10+ (getestet: 3.11, kompatibel zu 3.12)
GUI Framework:   Tkinter (11 Tabs)

Speicherorte (portable Auflösung, siehe config.py):
  1. Env-Variable GENESIS_STORAGE
  2. Windows: F:\GENESIS_STORAGE (wenn vorhanden)
  3. Fallback:  ~/.zeichenwerk/GENESIS_STORAGE  bzw. %APPDATA%\Zeichenwerk\GENESIS_STORAGE

Code liegt im Repo; ALLE Laufzeitdaten (Designs, Mockups, Logs, CSV, JSON)
liegen im Storage. Der Workspace bleibt dadurch sauber.

================================================================
 2. DATEISTRUKTUR (V2)
================================================================

genesis/
├── config.py               Zentrale Konfiguration + Logging + Key-Masking
├── control_panel.py        Haupt-GUI mit allen 11 Tabs (+ --selftest)
├── generator.py            Design-Generator (Text-Designs)
├── graphics_engine.py      9 Design-Templates + 10 Farbpaletten
├── icon_engine.py          46 geometrische Icons (Pillow)
├── text_database.py        Texte pro Keyword pro Sprache (16 EN / 11 DE)
├── scene_engine.py         Cartoon-Szenen-Engine + Humor-DB + DE→EN
├── scene_generator.py      Szenen-Orchestrierung (+ status.csv)
├── background_engine.py    15 Hintergründe + 5 Muster
├── text_layout_engine.py   8 Text-Layouts + 5 Schriftstile
├── hybrid_scene_engine.py  KI-Bild + lokaler Text + Hintergrund (1-4 Varianten)
├── puter_engine.py         Puter.js Browser-Bridge (HTTP, Port 7788)
├── puter_bridge_full.html  Browser-Seite für Puter.js
├── huggingface_engine.py   HuggingFace InferenceClient (FLUX.1-schnell u.a.)
├── gemini_engine.py        Google Gemini (google-genai SDK)
├── compliance_engine.py    Markenschutz-Prüfung (Levenshtein, Whitelist)
├── compliance_rules.yaml   YAML-Regelwerk: 9 Kategorien, 153 Begriffe
├── brand_check.py          Bequemer Wrapper (is_safe/check/is_blocked)
├── brand_identity.py       Zeichenwerk Brand-Daten + Plattform-Registry
├── upload_manager.py       Upload-Workflow (Titel/Tags/Clipboard/Browser)
├── mockup_engine.py        T-Shirt Mockup Generator (4 Farben, 1200x1400)
├── product_formats.py      7 Produktformate (contain/cover)
├── sales_tracker.py        Verkaufsanalyse + Tiers + 30-Tage-Report
├── key_manager.py          API-Key Verwaltung (INI, maskiert, nie geloggt)
├── api_key_detector.py     Auto-Erkennung (AIza…/hf_…/sk-…)
├── prompt_feedback.py      Bild-Feedback + lernender Prompt-Verbesserer
├── validator.py            CLI Compliance-Validator (Exit-Codes 0-3)
├── font_manager.py         [NEU V2] Plattform-Font-Auflösung (5 Stile)
├── status_io.py            [NEU V2] status.csv zentral (atomar, header)
├── config_private.ini.example
├── start_genesis.bat       Windows Starter (prüft/fixt Dependencies)
├── start_genesis.sh        [NEU V2] Linux/macOS Starter
├── genesis.ico             App-Icon (generiert, 6 Größen)
├── ruff.toml               Statische Codequalität
├── requirements.txt / requirements-dev.txt
├── tests/                  19 Testdateien, 348 Tests (headless + GUI unter Xvfb)
├── installer/              [NEU V2] Windows-Installationsroutine
│   ├── INSTALLIEREN.bat    Doppelklick-Installer (ruft install.ps1 auf)
│   ├── install.ps1         Python-Check/winget, venv, Starter, Shortcuts,
│   │                       Apps-&-Features-Eintrag, -AllUsers/-Silent-Modi
│   ├── uninstall.ps1       saubere Deinstallation (GENESIS_STORAGE bleibt)
│   ├── genesis_setup.iss   optionale klassische setup.exe (Inno Setup 6)
│   ├── LIESMICH.txt        Installations-Anleitung
│   └── LIESMICH_SETUP.txt  Infoseite des Inno-Assistenten
├── .github/workflows/ci.yml  [NEU V2] CI: ruff + Tests + GUI-Selbsttest
│                              (Xvfb) + ZIP-Bau, Release-Job
└── scripts/
    ├── build_vm.sh         Test-VM aufbauen (/tmp/genesis_vm, frisch)
    ├── full_check.sh       Vollprüfung von vorne (bis alles grün ist)
    └── build_zip.sh        Windows-Installations-ZIP bauen + verifizieren
                            (releases/GENESIS_SYSTEM_V2_Setup.zip)

================================================================
 3. GUI-TABS (control_panel.py)
================================================================

Tab 1  Generator   — Sprache DE/EN, Stichwort/Freitext, 9 Vorlagen, 1-20 Stück,
                     Fortschrittsbalken, Vorschau der letzten 8 Designs
Tab 2  Szene       — Figur (25) + Objekt (21) wählen, Layout, Auto-Humor,
                     Produktformate per Checkbox
Tab 3  Hybrid      — KI-Prompt anzeigen (mit Anatomie-Regeln + gelernten Fixes),
                     1-4 Varianten, lokaler Fallback ohne KI
Tab 4  Hochladen   — Liste offener Designs, Titel/Tags/Beschreibung/Alles kopieren,
                     Plattform öffnen, "als hochgeladen markieren"
Tab 5  Puter KI    — 6 Bildmodelle + 6 Chatmodelle, Bildgenerierung via Browser-Bridge
Tab 6  KI-Bilder   — HuggingFace (FLUX.1-schnell, SDXL, SD2.1, SD1.4), 10 Stile,
                     DE→EN-Übersetzung, Sprechblasen-Option
Tab 7  Regelwerk   — Einzel-/Batch-Prüfung, Statistik, Richtlinien
Tab 8  Rückmeldung — Bild laden, 10 Problemkategorien, 1-5 Sterne,
                     Gemini/GPT-4o-Analyse, aktive Prompt-Fixes
Tab 9  API-Schlüssel — Key einfügen → Auto-Erkennung, Verbindungstests
Tab 10 Verkäufe    — Verkauf eintragen, Bericht + Performance-Tiers
Tab 11 Bericht     — Live-Log, kopieren, Report-Datei öffnen

GUI-Modi: normal · --selftest (baut alles auf, prüft, Exit 0).
Ohne Tkinter: klare Fehlermeldung + Exit 2; Module/CLI bleiben nutzbar.

================================================================
 4. DESIGN-ENGINE
================================================================

4.1 Templates (9): bold_impact, vintage_retro, neon_glow, minimalist_pro,
    split_dynamic, quote_premium, grunge_street, bold_color, sticker_pop
4.2 Farbpaletten (10): midnight, crimson, ocean, forest, golden, purple,
    rose, arctic, sand, volt
4.3 Hintergründe (15): pastel_warm/cool/green/pink, sunny, sky, sunset, ocean,
    forest, night, neon_dark, vintage_warm, clean_white/cream/black
4.4 Muster (5): polka_dots, stripes_h, stripes_v, stars, confetti
4.5 Text-Layouts (8): speech_bubble, thought_bubble, banner_top, banner_bottom,
    stamp, free_top, free_bottom, no_text
4.6 Schriftstile (5): impact, bold, rounded, serif, light
    (V2: systematische Font-Suche mit Fallbacks über font_manager.py)

================================================================
 5. KI-BILDGENERIERUNG
================================================================

5.1 Puter.js Bridge (puter_engine.py + puter_bridge_full.html)
    Python startet lokalen HTTP-Server (127.0.0.1:7788, Thread-sicher),
    Browser öffnet Bridge-Seite, Puter.js generiert Bild, Bridge POSTet
    Base64 an /result, Python validiert + speichert PNG (2000x2000).
    Endpunkte: GET / (HTML) · GET /job · GET /status · POST /result · POST /error
    Bildmodelle (6): FLUX 1.1 Pro Ultra, DALL-E 3, GPT Image 1, Imagen 4 Ultra,
                      Stable Diffusion XL, Seedream 3
    Chatmodelle (6):  Claude Sonnet 4, GPT-4o, Gemini 2.5 Flash/Pro,
                      Llama 4 Maverick, DeepSeek R1
    Hinweis: Prompt-Verbesserung via Chat braucht Browser-Session (headless
    gibt improve_prompt_with_chat() den Original-Prompt zurück).

5.2 HuggingFace (huggingface_engine.py)
    InferenceClient (NICHT die alte API-URL — die gibt 404, bekannte V1-Einschränkung).
    Modelle: FLUX.1-schnell, SDXL, SD2.1, SD1.4. Ohne Token/SDK: saubere
    HuggingFaceUnavailable-Fehlermeldung. Bytes- und PIL-Rückgaben werden behandelt.

5.3 Google Gemini (gemini_engine.py)
    google-genai SDK, gemini-2.5-flash/2.0-flash. EU-Bildgenerierung bleibt
    eingeschränkt → GeminiUnavailable mit klarem Hinweis, kein Crash.
    translate_de_en() fällt auf das lokale Wörterbuch zurück.

5.4 Hybrid Scene Engine (hybrid_scene_engine.py)
    1) KI-Illustration OHNE Text (oder lokaler Icon-Fallback, damit der
       Workflow auch ohne Netz/API testbar bleibt)
    2) Hintergrundwahl (automatisch aus 15 oder fest)
    3) Illustration einpassen (72 % Fläche, zentriert)
    4) Text mit perfekter Typografie (8 Layouts × 5 Stile)
    5) 1-4 Varianten
    Anatomie-Regeln im Prompt: full body character visible · both feet and
    legs clearly shown · front facing view · complete character silhouette ·
    no cropped body parts · NO text NO words NO letters in image

================================================================
 6. MARKENSCHUTZ (COMPLIANCE)
================================================================

Schema: PRUEFSYSTEM_SCHEMA_V1.0 · Regelwerk: compliance_rules.yaml (V2)

Prüfreihenfolge (check_order): 1 Extremismus · 2 Hasssymbole · 3 Hoheitszeichen ·
4 Marken (Tech/Sport/Luxury/Food/Entertainment, 49 Begriffe) · 5 Figuren/Franchise ·
6 Urheberrecht · 7 Diskriminierung · 8 Politik · 9 Sonstige Risiken

Statistik: 9 Kategorien · 153 geschützte Begriffe · 12 Whitelist-Einträge
Ähnlichkeit: Levenshtein, Schwelle 0,88 — V2-Regel gegen False Positives:
  - Begriffe < 6 Zeichen: nur exakte Treffer ("yoga" schlägt NICHT auf "yoda" an,
    "like" nicht auf "nike")
  - Begriffe >= 6 Zeichen: 1 Tippfehler erlaubt, erstes Zeichen muss passen
    ("adidass" WIRD erkannt)
Severity: block (Upload stoppen) oder warn (nur Hinweis, z.B. Hoheitszeichen).
Whitelist: generische Begriffe wie "apple pie", "amazon rainforest",
"jokes champion" — die Marke selbst ("apple") bleibt geschützt.

Erlaubte Inhalte: eigene Sprüche, Illustrationen, abstrakte Formen, Tiere,
Natur, generische Berufe, Humor, Kaffee, Montag, Katze, Hund, Pizza, Bier,
Coding, Gym … (die komplette eigene Text-Datenbank ist per Test abgesichert).

================================================================
 7. BRAND / SHOP
================================================================

Name: Zeichenwerk · Slogans: DE "Zeichen setzen. Jeden Tag." / EN "Bold designs
for bold people." · Bios + 10 Brand-Keywords: brand_identity.py

Plattformen (Registry mit Limits):
  Redbubble    aktiv · max 15 Tags · min 1500px
  TeePublic    aktiv · max 20 Tags · min 1500px
  Spreadshirt  aktiv · max 25 Tags · min 2000px (DE+EN-Tags)
  Merch Amazon vorbereitet (inaktiv)

Richtlinien (im System hinterlegt): brand_identity.PLATFORM_GUIDELINES

================================================================
 8. TEXT-DATENBANK
================================================================

EN: 16 Keywords · DE: 11 Keywords · 6-18 Sprüche pro Keyword (206 Texte total,
alle compliance-geprüft per Test). Beispiele wie in V1:
"But First Coffee", "Error 404 Motivation Not Found", "Sarcasm Is My Love
Language", "Monday Should Be Illegal", "Erstmal Kaffee", "Montag Sollte
Verboten Sein", "Meine Geduld Hat Gekuendigt", "Retten Loeschen Bergen Schuetzen".

================================================================
 9. SCENE ENGINE
================================================================

Figuren (25): pinguin, katze, hund, faultier, feuerwehrmann, krankenschwester,
taucher, koch, polizist, astronaut, pirat, ninja, cowboy, roboter, alien,
baer, fuchs, eule, frosch, panda, elefant, affe, loewe, einhorn, drache

Objekte (21, mit Aliasen eiscreme/coffee/heart/beer/book/phone/guitar/cake):
eis, eiscreme, kaffee, coffee, pizza, laptop, computer, herz, heart, bier,
beer, buch, book, handy, phone, gitarre, guitar, ball, donut, kuchen, cake

Humor-DB (V1-Inhalte erhalten): pinguin+eis "Gibts auch Fisch-Eis?" ·
katze+kaffee "Vor dem Kaffee rede ich nicht." · hund+pizza "Pizza? ICH LIEBE
DICH!" · faultier+laptop "Home Office Champion seit immer." · + 11 weitere
Kombinationen + Default-Fallbacks (DE/EN).

DE→EN-Wörterbuch: 92 Einträge (>= 60 lt. Spezifikation).

================================================================
 10. PRODUKT-FORMATE
================================================================

tshirt 2000x2000 · poster 3000x4000 · sticker 1400x1400 · mug 2400x1000 ·
phone 1080x1920 · pdf_a4 2480x3508 · social 1080x1080
Export-Modi: contain (auffüllen) und cover (beschneiden).
validate_for_platform() prüft Plattform-Mindestgrößen.

================================================================
 11. FEEDBACK-SYSTEM
================================================================

10 Kategorien: missing_foot, text_in_image, wrong_text, bad_anatomy,
wrong_character, too_dark, blurry, bad_background, wrong_style, too_complex

Lern-Regel: ab 2x gleichem Problem wird der Fix automatisch in Prompts
eingefügt (z.B. 2x missing_foot → "both feet clearly visible, full body shot").
Speicher: feedback_store.json (thread-sicher, defekte Dateien starten leer).
KI-Analyse: Gemini/GPT-4o nur wenn Key vorhanden — sonst leere Antwort, kein Crash.

================================================================
 12. SALES TRACKER
================================================================

sales_data.json · Felder: name, total, platforms{}, history[{date,platform,count}]
Tiers: STAR >= 70 % · GOOD >= 35 % · OK >= 10 % · WEAK < 10 % (vom Bestseller)
30-Tage-Analyse: per Design/Plattform/Tag + Top-10 · Bericht als Text.

================================================================
 13. UPLOAD-WORKFLOW
================================================================

1 Design generieren → 2 Upload-Tab (Liste offener Designs aus status.csv) →
3 Plattform wählen → 4 Titel/Tags/Beschreibung/Alles kopieren (Tags:
Design-Tags + Brand-Keywords, dedupliziert, plattformspezifisches Limit) →
5 Plattform öffnen (Browser) → 6 hochladen → 7 "Markieren" → status=uploaded.
Titel: max 60 Zeichen, wortgrenzen-sicher gekürzt, kapitalisiert.

================================================================
 14. MOCKUP ENGINE
================================================================

4 Shirt-Farben (black/white/navy/gray) · 1200x1400 px · Design auf Brust
(skaliert, zentriert) · "ZEICHENWERK"-Branding unten rechts · Set-Funktion.

================================================================
 15. TECHNISCHE SPEZIFIKATIONEN (V2)
================================================================

Python >= 3.10 (Empfehlung 3.12; VM testet auf 3.11)
Pillow >= 10 (getestet 12.3) · PyYAML >= 6 · requests >= 2.31
Optional: huggingface_hub, google-genai (System läuft auch ohne)
Design-Auflösung 2000x2000 · PNG optimiert · status.csv (Header, atomar)
Metadaten TXT pro Design · Keys in config_private.ini (INI, nie geloggt)
Logs: generator.log (+ Console) mit automatischem Key-Masking
Statische Prüfung: ruff (ruff.toml) · Tests: pytest, 348 Cases

================================================================
 16. EINSCHRÄNKUNGEN & BEHOBENE PUNKTE (V1 → V2)
================================================================

Behoben in V2:
  - Hartkodierte F:\-Pfade → portable Auflösung mit Env-Override
  - Fehlende Font-Abhängigkeit von Windows-Fonts → Fallback-Ketten
  - Compliance-False-Positives bei normalen Wörtern → Kurzbegriffs-Regel
  - undefiniertes Verhalten ohne API-Keys/SDKs → saubere *Unavailable-Fehler
  - ungeschützte Logs → Keys werden maskiert (Filter, getestet)
  - kein Test → 348 Tests + Vollprüfungs-VM (scripts/full_check.sh)
  - GUI crashte ohne Tkinter → Platzhalter + --selftest
  - nicht reproduzierbare Generierung → Seed-Unterstützung überall

Bestehende Einschränkungen (wie V1, dokumentiert):
  - Gemini-Bildgenerierung in der EU eingeschränkt (403/429) → Fallbacks vorhanden
  - HuggingFace alte Inference-URL tot → InferenceClient wird genutzt
  - Puter.js braucht echte Browser-Session (kein Headless-HTTP)
  - NAS-Speicher (G:\) hatte Schreibprobleme → lokaler Storage ist Standard

================================================================
 17. QUALITÄTSSICHERUNG (NEU IN V2)
================================================================

scripts/build_vm.sh    baut eine frische Test-VM in /tmp/genesis_vm
                       (eigenes Virtualenv + Storage; nichts im Repo)
scripts/full_check.sh  VOLLPRÜFUNG, jede Runde komplett von vorne:
                       VM neu → Workspace-Sauberkeit → ruff + Shell-Syntax →
                       pytest → CLI-Smoke → Pipeline-Smoke → GUI-Selbsttest
                       (falls Display) → ZIP-Bau mit Verifikation →
                       Storage/Caches entsorgen. Grün erst wenn ALLES passt.
scripts/build_zip.sh   baut releases/GENESIS_SYSTEM_V2_Setup.zip (Installer +
                       komplette App) und verifiziert: Entpack-Test,
                       Dateivollständigkeit, ASCII-Sicherheit der BAT,
                       komplette Testsuite im entpackten Zustand, SHA256.

CI (.github/workflows/ci.yml) — läuft bei jedem Push:
  Job "Vollprüfung": python3-tk + Xvfb installieren → ruff → komplette
  Testsuite MIT echten GUI-Tests → GUI-Selbsttest (11 Tabs) → CLI-Smoke →
  ZIP-Bau + Verifikation → ZIP als Download-Artefakt.
  Job "Release": bei Commits mit "release:"-Präfix (oder manuellem Dispatch)
  wird das GitHub-Release v2.0.0 mit frischem ZIP aktualisiert.
  → https://github.com/AOWDGENESIS/Entwicklungen/releases/tag/v2.0.0

Windows-Installation: releases/GENESIS_SYSTEM_V2_Setup.zip entpacken →
INSTALLIEREN.bat doppelklicken (Details: installer/LIESMICH.txt).

Testabdeckung u.a.: alle 9 Templates, 10 Paletten, 15 Hintergründe, 5 Muster,
8 Layouts, 46 Icons, 206 Datenbank-Texte, Compliance-Ecken (Whitelist,
Tippfehler, Severity), Puter-HTTP-Server (real auf localhost), HF/Gemini mit
Mocks, Sales-Tiers, Keys/Masking, Upload-Grenzen, End-to-End-Pipeline,
Release-Assets (Icon, Installer-Inhalte, ASCII-Sicherheit),
"keine Artefakte im Repo"-Regression.
