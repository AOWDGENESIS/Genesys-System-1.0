#!/usr/bin/env python3
"""GENESIS SYSTEM / Zeichenwerk — Haupt-GUI (Tkinter, 11 Tabs).

Tabs:
  1 Generator   — Text-Designs (9 Vorlagen, DE/EN, 1-20 Stück, Vorschau)
  2 Szene       — Cartoon-Szenen (Figuren, Objekte, Sprechblasen, Humor)
  3 Hybrid      — KI-Bild + lokaler Text (Hintergründe, Layouts, Varianten)
  4 Hochladen   — Metadaten kopieren, Plattform öffnen, Markieren
  5 Puter KI    — Kostenlose KI-Bilder über Browser-Bridge
  6 KI-Bilder   — HuggingFace FLUX.1-schnell (+ Stile, Übersetzung)
  7 Regelwerk   — Compliance prüfen (einzeln/Batch), Statistik, Richtlinien
  8 Rückmeldung — Bild-Feedback (10 Kategorien, Sterne, KI-Analyse)
  9 API-Schlüssel — Keys einfügen, Auto-Erkennung, Verbindungstest
 10 Verkäufe    — Sales eintragen, Tiers, 30-Tage-Analyse, Bericht
 11 Bericht     — Live-Log des Generators, Bericht kopieren

Modus --selftest: baut die komplette GUI auf, prüft alle Tabs und beendet
sich mit Exit-Code 0 — läuft überall dort, wo Tk + Display existieren.
Ohne Tkinter bleibt das Modul importierbar (Headless-/CLI-Betrieb).
"""

from __future__ import annotations

import argparse
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path

logger = __import__("logging").getLogger("genesis.gui")

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk
    TK_IMPORT_ERROR: Exception | None = None
except ImportError as _exc:  # saubere Meldung statt Traceback
    tk = None
    TK_IMPORT_ERROR = _exc

import brand_identity
import config


def _require_tk() -> None:
    """Bricht mit klarer Anleitung ab, wenn Tkinter fehlt."""
    if tk is None:
        ursache = TK_IMPORT_ERROR if TK_IMPORT_ERROR else "Tkinter zur Laufzeit deaktiviert"
        print(
            "FEHLER: Tkinter ist in dieser Python-Installation nicht verfügbar.\n"
            f"  Ursache: {ursache}\n"
            "  Windows: offizielle Python-Installation nutzen (enthält Tk).\n"
            "  Linux:   sudo apt install python3-tk\n"
            "Headless? Alle Funktionen laufen auch über die Module/CLI "
            "(validator.py, generator.py …).",
            file=sys.stderr,
        )
        raise SystemExit(2)


# ================================================================== Panel
if tk is not None:

    class GenesisPanel(tk.Tk):
        """Hauptfenster mit allen 11 Tabs."""

        def __init__(self) -> None:
            super().__init__()
            self.title(f"{config.APP_NAME} — {config.BRAND} v{config.VERSION}")
            self.geometry("1060x760")
            self.minsize(900, 640)
            try:
                ico = config.SYSTEM_DIR / "genesis.ico"
                if ico.exists():
                    self.iconbitmap(str(ico))
            except tk.TclError:
                pass

            self.notebook = ttk.Notebook(self)
            self.notebook.pack(fill="both", expand=True, padx=6, pady=6)

            self._report_lines: list[str] = []
            self._build_tabs()
            self.log(f"{config.APP_NAME} {config.VERSION} bereit — "
                     f"Storage: {config.STORAGE_DIR}")

        # -------------------------------------------------------- Helpers
        def log(self, msg: str) -> None:
            """Schreibt in den Bericht-Tab und ins Logfile."""
            line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
            self._report_lines.append(line)
            logger.info(msg)
            widget = getattr(self, "report_text", None)
            if widget is not None:
                widget.configure(state="normal")
                widget.insert("end", line + "\n")
                widget.see("end")
                widget.configure(state="disabled")

        def _frame(self, title: str) -> ttk.Frame:
            frame = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(frame, text=title)
            return frame

        @staticmethod
        def _err(exc: Exception) -> str:
            traceback.print_exc()
            return f"{type(exc).__name__}: {exc}"

        # -------------------------------------------------------- Tabs
        def _build_tabs(self) -> None:
            self._tab_generator()
            self._tab_scene()
            self._tab_hybrid()
            self._tab_upload()
            self._tab_puter()
            self._tab_ai_images()
            self._tab_compliance()
            self._tab_feedback()
            self._tab_keys()
            self._tab_sales()
            self._tab_report()

        # ----- Tab 1: Generator ------------------------------------
        def _tab_generator(self) -> None:
            import graphics_engine
            import text_database

            f = self._frame("Generator")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Sprache:").pack(side="left")
            self.gen_lang = tk.StringVar(value="de")
            lang_box = ttk.Combobox(top, textvariable=self.gen_lang,
                                    values=list(text_database.SUPPORTED_LANGUAGES),
                                    width=5, state="readonly")
            lang_box.pack(side="left", padx=4)
            self.gen_kw_box = ttk.Combobox(top, width=16)  # wird via trace gefüllt
            ttk.Label(top, text="Stichwort:").pack(side="left", padx=(10, 0))
            self.gen_keyword = tk.StringVar(value="coffee")
            self.gen_kw_box.configure(textvariable=self.gen_keyword)
            self.gen_kw_box.pack(side="left", padx=4)
            ttk.Label(top, text="Vorlage:").pack(side="left", padx=(10, 0))
            self.gen_template = tk.StringVar(value=graphics_engine.TEMPLATES[0])
            ttk.Combobox(top, textvariable=self.gen_template,
                         values=list(graphics_engine.TEMPLATES), width=16,
                         state="readonly").pack(side="left", padx=4)
            ttk.Label(top, text="Anzahl:").pack(side="left", padx=(10, 0))
            self.gen_count = tk.IntVar(value=2)
            ttk.Spinbox(top, from_=1, to=20, textvariable=self.gen_count,
                        width=4).pack(side="left", padx=4)

            mid = ttk.Frame(f)
            mid.pack(fill="x", pady=6)
            ttk.Label(mid, text="Freier Text (optional, eine Zeile pro Design):").pack(anchor="w")
            self.gen_free = tk.Text(mid, height=3, width=90)
            self.gen_free.pack(fill="x")

            bar = ttk.Frame(f)
            bar.pack(fill="x", pady=6)
            self.gen_progress = ttk.Progressbar(bar, mode="determinate")
            self.gen_progress.pack(side="left", fill="x", expand=True)
            ttk.Button(bar, text="Generieren",
                       command=self._run_generator).pack(side="left", padx=6)

            self.gen_lang.trace_add("write", lambda *_: self._refresh_keywords())
            self._refresh_keywords()

            ttk.Label(f, text="Vorschau (letzte 8):").pack(anchor="w")
            self.gen_preview = tk.Label(f, bg="#202028")
            self.gen_preview.pack(fill="both", expand=True)

        def _refresh_keywords(self) -> None:
            import text_database
            kws = text_database.keywords(self.gen_lang.get())
            self.gen_kw_box["values"] = kws
            if self.gen_keyword.get() not in kws:
                self.gen_keyword.set(kws[0])

        def _run_generator(self) -> None:
            def work() -> None:
                import generator
                try:
                    free_raw = self.gen_free.get("1.0", "end").strip()
                    free_texts = [line for line in free_raw.splitlines() if line.strip()] or None
                    count = max(1, min(20, int(self.gen_count.get())))
                    self.gen_progress["maximum"] = count
                    self.gen_progress["value"] = 0
                    paths: list[Path] = []
                    for i in range(count):
                        paths += generator.generate_batch(
                            lang=self.gen_lang.get(),
                            keyword=None if free_texts else self.gen_keyword.get(),
                            free_texts=free_texts[i:i + 1] if free_texts else None,
                            count=1,
                            template=self.gen_template.get(),
                            size=1000,
                        )
                        self.gen_progress["value"] = i + 1
                    self.log(f"Generator: {len(paths)} Design(s) erzeugt.")
                    self._show_preview(paths[-8:])
                except Exception as exc:  # noqa: BLE001
                    self.log("Generator-Fehler: " + self._err(exc))

            threading.Thread(target=work, daemon=True).start()

        def _show_preview(self, paths: list[Path]) -> None:
            try:
                from PIL import Image, ImageTk
                tiles = []
                for p in paths:
                    img = Image.open(p)
                    img.thumbnail((160, 160))
                    tiles.append(img)
                if not tiles:
                    return
                cols = min(4, len(tiles))
                rows = (len(tiles) + cols - 1) // cols
                w, h = 168, 190
                sheet = Image.new("RGB", (cols * w, rows * h), (32, 32, 40))
                for i, img in enumerate(tiles):
                    x, y = (i % cols) * w, (i // cols) * h
                    sheet.paste(img, (x + (w - img.width) // 2, y + 4))
                self._preview_photo = ImageTk.PhotoImage(sheet)
                self.gen_preview.configure(image=self._preview_photo, text="")
            except Exception as exc:  # noqa: BLE001
                self.log("Vorschau-Fehler: " + self._err(exc))

        # ----- Tab 2: Szene ----------------------------------------
        def _tab_scene(self) -> None:
            import scene_engine
            import text_layout_engine

            f = self._frame("Szene")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Figur:").pack(side="left")
            self.scene_figure = tk.StringVar(value="pinguin")
            ttk.Combobox(top, textvariable=self.scene_figure,
                         values=list(scene_engine.FIGURES), width=14,
                         state="readonly").pack(side="left", padx=4)
            ttk.Label(top, text="Objekt:").pack(side="left", padx=(10, 0))
            self.scene_obj = tk.StringVar(value="(keins)")
            objs = ["(keins)", *scene_engine.OBJECTS]
            ttk.Combobox(top, textvariable=self.scene_obj, values=objs, width=14,
                         state="readonly").pack(side="left", padx=4)
            ttk.Label(top, text="Layout:").pack(side="left", padx=(10, 0))
            self.scene_layout = tk.StringVar(value="speech_bubble")
            ttk.Combobox(top, textvariable=self.scene_layout,
                         values=list(text_layout_engine.TEXT_LAYOUTS),
                         width=14, state="readonly").pack(side="left", padx=4)
            self.scene_auto_speech = tk.BooleanVar(value=True)
            ttk.Checkbutton(top, text="Humor-Spruch automatisch",
                            variable=self.scene_auto_speech).pack(side="left", padx=8)

            mid = ttk.Frame(f)
            mid.pack(fill="x", pady=4)
            ttk.Label(mid, text="Spruch:").pack(side="left")
            self.scene_text = tk.StringVar(
                value=scene_engine.speech_text("pinguin", "eis", "de"))
            ttk.Entry(mid, textvariable=self.scene_text, width=60).pack(
                side="left", padx=4, fill="x", expand=True)

            bar = ttk.Frame(f)
            bar.pack(fill="x", pady=4)
            ttk.Button(bar, text="Szene generieren",
                       command=self._run_scene).pack(side="left", padx=4)
            ttk.Label(bar, text="Produkte:").pack(side="left", padx=(14, 0))
            self.scene_products = {k: tk.BooleanVar(value=k == "tshirt")
                                   for k in ("tshirt", "sticker", "mug", "social")}
            for k, var in self.scene_products.items():
                ttk.Checkbutton(bar, text=k, variable=var).pack(side="left", padx=2)

            self.scene_preview = tk.Label(f, bg="#202028")
            self.scene_preview.pack(fill="both", expand=True, pady=6)

        def _run_scene(self) -> None:
            def work() -> None:
                try:
                    from PIL import Image

                    import product_formats
                    import scene_generator
                    from scene_engine import SceneSpec
                    obj = self.scene_obj.get()
                    text = None if self.scene_auto_speech.get() else self.scene_text.get()
                    spec = SceneSpec(figure=self.scene_figure.get(),
                                     obj=None if obj == "(keins)" else obj,
                                     layout=self.scene_layout.get(), text=text)
                    path = scene_generator.generate_scene(spec, size=1000)
                    self.log(f"Szene erzeugt: {path.name}")
                    self._show_scene_preview(path)
                    for product, var in self.scene_products.items():
                        if var.get() and product != "tshirt":
                            out = config.DESIGNS_DIR / f"{path.stem}_{product}.png"
                            product_formats.export_for_product(
                                Image.open(path), product, out)
                            self.log(f"Produktformat {product}: {out.name}")
                except Exception as exc:  # noqa: BLE001
                    self.log("Szenen-Fehler: " + self._err(exc))

            threading.Thread(target=work, daemon=True).start()

        def _show_scene_preview(self, path: Path) -> None:
            try:
                from PIL import Image, ImageTk
                img = Image.open(path)
                img.thumbnail((520, 520))
                self._scene_photo = ImageTk.PhotoImage(img)
                self.scene_preview.configure(image=self._scene_photo, text="")
            except Exception as exc:  # noqa: BLE001
                self.log("Szenen-Vorschau-Fehler: " + self._err(exc))

        # ----- Tab 3: Hybrid-Szene ---------------------------------
        def _tab_hybrid(self) -> None:
            import hybrid_scene_engine
            import scene_engine
            import text_layout_engine

            f = self._frame("Hybrid-Szene")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Figur (KI-Prompt):").pack(side="left")
            self.hy_figure = tk.StringVar(value="pinguin")
            ttk.Combobox(top, textvariable=self.hy_figure,
                         values=list(scene_engine.FIGURES), width=14,
                         state="readonly").pack(side="left", padx=4)
            ttk.Label(top, text="Text:").pack(side="left", padx=(10, 0))
            self.hy_text = tk.StringVar(value="Erstmal Kaffee")
            ttk.Entry(top, textvariable=self.hy_text, width=30).pack(
                side="left", padx=4, fill="x", expand=True)
            ttk.Label(top, text="Layout:").pack(side="left", padx=(10, 0))
            self.hy_layout = tk.StringVar(value="free_bottom")
            ttk.Combobox(top, textvariable=self.hy_layout,
                         values=list(text_layout_engine.TEXT_LAYOUTS), width=14,
                         state="readonly").pack(side="left", padx=4)
            ttk.Label(top, text="Varianten:").pack(side="left", padx=(10, 0))
            self.hy_variants = tk.IntVar(value=2)
            ttk.Spinbox(top, from_=1, to=hybrid_scene_engine.MAX_VARIANTS,
                        textvariable=self.hy_variants, width=3).pack(side="left", padx=4)

            info = ttk.Label(
                f, text=("Workflow: 1) KI generiert Illustration OHNE Text  "
                         "2) GENESIS wählt Hintergrund  3) Illustration auflegen  "
                         "4) Text mit perfekter Typografie  5) Varianten wählen"))
            info.pack(anchor="w", pady=4)

            bar = ttk.Frame(f)
            bar.pack(fill="x", pady=4)
            ttk.Button(bar, text="Varianten generieren (lokaler Fallback)",
                       command=self._run_hybrid).pack(side="left", padx=4)
            ttk.Button(bar, text="KI-Prompt anzeigen",
                       command=self._show_hybrid_prompt).pack(side="left", padx=4)

            self.hy_preview = tk.Label(f, bg="#202028")
            self.hy_preview.pack(fill="both", expand=True, pady=6)
            self.hy_paths: list[Path] = []

        def _show_hybrid_prompt(self) -> None:
            import hybrid_scene_engine
            prompt = hybrid_scene_engine.build_prompt(self.hy_figure.get())
            self.log("KI-Prompt:\n" + prompt)
            messagebox.showinfo("KI-Prompt (Anatomie-Regeln aktiv)", prompt)

        def _run_hybrid(self) -> None:
            def work() -> None:
                try:
                    import hybrid_scene_engine
                    from hybrid_scene_engine import HybridSpec
                    spec = HybridSpec(figure=self.hy_figure.get(),
                                      text=self.hy_text.get(),
                                      layout=self.hy_layout.get(),
                                      variants=max(1, min(4, int(self.hy_variants.get()))))
                    imgs = hybrid_scene_engine.generate_hybrid(spec)
                    self.hy_paths = []
                    for i, img in enumerate(imgs):
                        p = config.DESIGNS_DIR / f"hybrid_{self.hy_figure.get()}_{i}.png"
                        p.parent.mkdir(parents=True, exist_ok=True)
                        img.save(p, "PNG", optimize=True)
                        self.hy_paths.append(p)
                    self.log(f"Hybrid: {len(imgs)} Variante(n) erzeugt.")
                    self._show_hybrid_preview(self.hy_paths)
                except Exception as exc:  # noqa: BLE001
                    self.log("Hybrid-Fehler: " + self._err(exc))

            threading.Thread(target=work, daemon=True).start()

        def _show_hybrid_preview(self, paths: list[Path]) -> None:
            try:
                from PIL import Image, ImageTk
                tiles = []
                for p in paths:
                    img = Image.open(p)
                    img.thumbnail((300, 300))
                    tiles.append(img)
                if not tiles:
                    return
                w = max(t.width for t in tiles)
                h = max(t.height for t in tiles)
                sheet = Image.new("RGB", (w * len(tiles), h), (32, 32, 40))
                for i, t in enumerate(tiles):
                    sheet.paste(t, (i * w + (w - t.width) // 2, (h - t.height) // 2))
                self._hy_photo = ImageTk.PhotoImage(sheet)
                self.hy_preview.configure(image=self._hy_photo, text="")
            except Exception as exc:  # noqa: BLE001
                self.log("Hybrid-Vorschau-Fehler: " + self._err(exc))

        # ----- Tab 4: Hochladen ------------------------------------
        def _tab_upload(self) -> None:
            import upload_manager
            f = self._frame("Hochladen")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Button(top, text="Aktualisieren",
                       command=self._refresh_upload).pack(side="left", padx=4)
            ttk.Label(top, text="Plattform:").pack(side="left", padx=(12, 0))
            self.up_platform = tk.StringVar(value="redbubble")
            ttk.Combobox(top, textvariable=self.up_platform,
                         values=[p.key for p in brand_identity.active_platforms()],
                         width=12, state="readonly").pack(side="left", padx=4)
            ttk.Button(top, text="Plattform öffnen",
                       command=lambda: upload_manager.open_platform(
                           self.up_platform.get())).pack(side="left", padx=4)

            self.up_list = tk.Listbox(f, selectmode="extended", height=8)
            self.up_list.pack(fill="both", expand=True, pady=6)

            meta = ttk.Frame(f)
            meta.pack(fill="x")
            ttk.Label(meta, text="Titel:").grid(row=0, column=0, sticky="w")
            self.up_title = tk.StringVar()
            ttk.Entry(meta, textvariable=self.up_title, width=70).grid(
                row=0, column=1, padx=4, pady=2)
            ttk.Label(meta, text="Tags:").grid(row=1, column=0, sticky="w")
            self.up_tags = tk.StringVar()
            ttk.Entry(meta, textvariable=self.up_tags, width=70).grid(
                row=1, column=1, padx=4, pady=2)
            ttk.Label(meta, text="Beschreibung:").grid(row=2, column=0, sticky="w")
            self.up_desc = tk.StringVar()
            ttk.Entry(meta, textvariable=self.up_desc, width=70).grid(
                row=2, column=1, padx=4, pady=2)

            bar = ttk.Frame(f)
            bar.pack(fill="x", pady=4)
            for label, attr in (("Titel", "up_title"), ("Tags", "up_tags"),
                                ("Beschreibung", "up_desc"), ("Alles", None)):
                ttk.Button(bar, text=f"{label} kopieren",
                           command=lambda a=attr: self._copy_meta(a)).pack(
                    side="left", padx=3)
            ttk.Button(bar, text="Als hochgeladen markieren",
                       command=self._mark_uploaded).pack(side="left", padx=10)
            self._refresh_upload()

        def _refresh_upload(self) -> None:
            import upload_manager
            self.up_list.delete(0, "end")
            self.up_items = upload_manager.pending()
            for row in self.up_items:
                self.up_list.insert("end", f"{row['name']}  —  {row.get('text', '')[:40]}")
            if not self.up_items:
                self.up_list.insert("end", "(keine offenen Designs — zuerst generieren)")

        def _selected_upload(self) -> str | None:
            sel = self.up_list.curselection()
            idx = sel[0] if sel else 0
            if not getattr(self, "up_items", None) or idx >= len(self.up_items):
                return None
            return self.up_items[idx]["name"]

        def _load_meta(self) -> None:
            import upload_manager
            name = self._selected_upload()
            if not name:
                return
            try:
                meta = upload_manager.meta_for_design(name, self.up_platform.get())
                self.up_title.set(meta.title)
                self.up_tags.set(meta.tags_str)
                self.up_desc.set(meta.description)
            except ValueError as exc:
                self.log(f"Upload: {exc}")

        def _copy_meta(self, attr: str | None) -> None:
            import upload_manager
            self._load_meta()
            if attr is None:
                text = (f"{self.up_title.get()}\n\n{self.up_desc.get()}\n\n"
                        f"{self.up_tags.get()}")
            else:
                text = getattr(self, attr).get()
            ok = upload_manager.copy_to_clipboard(text)
            self.log("Zwischenablage: " +
                     ("kopiert" if ok else "fehlgeschlagen (xclip/xsel installieren)"))

        def _mark_uploaded(self) -> None:
            import upload_manager
            name = self._selected_upload()
            if name and upload_manager.mark_design_uploaded(name):
                self.log(f"Als hochgeladen markiert: {name}")
                self._refresh_upload()
            else:
                self.log("Markieren fehlgeschlagen (Design unbekannt?)")

        # ----- Tab 5: Puter KI -------------------------------------
        def _tab_puter(self) -> None:
            import puter_engine
            f = self._frame("Puter KI")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Modell:").pack(side="left")
            self.puter_model = tk.StringVar(value="flux_11_pro_ultra")
            ttk.Combobox(top, textvariable=self.puter_model,
                         values=list(puter_engine.IMAGE_MODELS), width=22,
                         state="readonly").pack(side="left", padx=4)
            ttk.Label(top, text="Modell (Chat):").pack(side="left", padx=(10, 0))
            self.puter_chat = tk.StringVar(value="claude_sonnet_4")
            ttk.Combobox(top, textvariable=self.puter_chat,
                         values=list(puter_engine.CHAT_MODELS), width=20,
                         state="readonly").pack(side="left", padx=4)

            mid = ttk.Frame(f)
            mid.pack(fill="x", pady=6)
            ttk.Label(mid, text="Prompt:").pack(side="left")
            self.puter_prompt = tk.StringVar(value="a cute penguin holding coffee")
            ttk.Entry(mid, textvariable=self.puter_prompt, width=70).pack(
                side="left", padx=4, fill="x", expand=True)

            bar = ttk.Frame(f)
            bar.pack(fill="x", pady=4)
            ttk.Button(bar, text="Bild generieren (Browser öffnet sich)",
                       command=self._run_puter).pack(side="left", padx=4)
            ttk.Button(bar, text="Prompt verbessern (Chat)",
                       command=self._run_puter_improve).pack(side="left", padx=4)
            ttk.Label(f, text=("Puter.js: keine API-Keys nötig. Der Standard-Browser "
                               "öffnet die Bridge-Seite; Seite offen lassen. "
                               "FLUX/DALL-E/Imagen/SDXL/Seedream kostenlos."),
                      foreground="#556").pack(anchor="w")

        def _run_puter(self) -> None:
            def work() -> None:
                try:
                    import puter_engine
                    bridge = puter_engine.default_bridge()
                    path = bridge.generate_image(
                        prompt=self.puter_prompt.get(),
                        model_key=self.puter_model.get(),
                        size=1000,
                    )
                    self.log(f"Puter-Bild gespeichert: {path.name}")
                except Exception as exc:  # noqa: BLE001
                    self.log("Puter-Fehler: " + self._err(exc))

            threading.Thread(target=work, daemon=True).start()

        def _run_puter_improve(self) -> None:
            import puter_engine
            improved = puter_engine.improve_prompt_with_chat(
                self.puter_prompt.get(), self.puter_chat.get())
            self.puter_prompt.set(improved)
            self.log("Puter-Prompt verbessert (Chat-Modell: "
                     + self.puter_chat.get() + ")")

        # ----- Tab 6: KI-Bilder (HuggingFace) ----------------------
        def _tab_ai_images(self) -> None:
            import huggingface_engine
            f = self._frame("KI-Bilder")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Modell:").pack(side="left")
            self.ai_model = tk.StringVar(value=huggingface_engine.DEFAULT_MODEL)
            ttk.Combobox(top, textvariable=self.ai_model,
                         values=list(huggingface_engine.MODELS), width=28,
                         state="readonly").pack(side="left", padx=4)
            self.ai_style = tk.StringVar(value="flat vector")
            ttk.Label(top, text="Stil:").pack(side="left", padx=(10, 0))
            ttk.Combobox(top, textvariable=self.ai_style,
                         values=["flat vector", "cartoon", "watercolor", "pixel art",
                                 "line art", "comic", "3d render", "sketch",
                                 "neon", "vintage"], width=14).pack(side="left", padx=4)

            mid = ttk.Frame(f)
            mid.pack(fill="x", pady=6)
            ttk.Label(mid, text="Prompt (DE ok — wird übersetzt):").pack(side="left")
            self.ai_prompt = tk.StringVar(value="pinguin mit kaffee")
            ttk.Entry(mid, textvariable=self.ai_prompt, width=60).pack(
                side="left", padx=4, fill="x", expand=True)

            bar = ttk.Frame(f)
            bar.pack(fill="x", pady=4)
            ttk.Button(bar, text="HuggingFace-Bild generieren",
                       command=self._run_ai_image).pack(side="left", padx=4)
            self.ai_speech = tk.BooleanVar(value=False)
            ttk.Checkbutton(bar, text="Sprechblase danach",
                            variable=self.ai_speech).pack(side="left", padx=8)
            ttk.Label(f, foreground="#556",
                      text="Übersetzung DE→EN: 60+ Wörter lokal, sonst Gemini "
                           "(wenn Key vorhanden). 1000 Bilder/Tag gratis mit "
                           "kostenlosem HF-Token.").pack(anchor="w")

        def _run_ai_image(self) -> None:
            def work() -> None:
                try:
                    from PIL import Image as PILImage

                    import huggingface_engine
                    import scene_engine
                    import text_layout_engine
                    prompt = self.ai_prompt.get()
                    en = " ".join(scene_engine.translate_de_en(w) for w in prompt.split())
                    style = self.ai_style.get()
                    path = huggingface_engine.generate_image(
                        prompt=f"{en}, {style}", model_key=self.ai_model.get(),
                        size=1024)
                    self.log(f"HuggingFace-Bild gespeichert: {path.name}")
                    if self.ai_speech.get():
                        img = PILImage.open(path)
                        laid = text_layout_engine.draw_text_layout(
                            img, "speech_bubble", "But First Coffee")
                        out = path.with_name(path.stem + "_speech.png")
                        laid.save(out, "PNG", optimize=True)
                        self.log(f"Sprechblasen-Version: {out.name}")
                except Exception as exc:  # noqa: BLE001
                    self.log("HuggingFace-Fehler: " + self._err(exc))

            threading.Thread(target=work, daemon=True).start()

        # ----- Tab 7: Regelwerk ------------------------------------
        def _tab_compliance(self) -> None:
            f = self._frame("Regelwerk")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Text prüfen:").pack(side="left")
            self.comp_text = tk.StringVar(value="But First Coffee")
            ttk.Entry(top, textvariable=self.comp_text, width=50).pack(
                side="left", padx=4, fill="x", expand=True)
            ttk.Button(top, text="Prüfen",
                       command=self._run_compliance).pack(side="left", padx=4)
            ttk.Button(top, text="Batch (Text-Datenbank)",
                       command=self._run_compliance_batch).pack(side="left", padx=4)

            self.comp_result = scrolledtext.ScrolledText(f, height=10)
            self.comp_result.pack(fill="both", expand=True, pady=6)

            self.comp_stats = ttk.Label(f, text="")
            self.comp_stats.pack(anchor="w")
            self._refresh_comp_stats()

        def _refresh_comp_stats(self) -> None:
            try:
                from compliance_engine import default_engine
                s = default_engine().stats()
                self.comp_stats.configure(
                    text=(f"Regelwerk: {s['categories']} Kategorien, "
                          f"{s['terms']} geschützte Begriffe, "
                          f"Whitelist: {s['whitelist']} — Schema {s['schema']}"))
            except Exception as exc:  # noqa: BLE001
                self.comp_stats.configure(text="Regelwerk-Fehler: " + str(exc))

        def _run_compliance(self) -> None:
            from compliance_engine import default_engine
            result = default_engine().check_text(self.comp_text.get())
            self.comp_result.delete("1.0", "end")
            self.comp_result.insert("end", result.summary())
            self.log("Compliance-Prüfung: " +
                     ("BLOCKIERT" if result.blocked else "OK"))

        def _run_compliance_batch(self) -> None:
            import text_database
            from compliance_engine import default_engine
            engine = default_engine()
            blocked = warned = total = 0
            for lang in text_database.SUPPORTED_LANGUAGES:
                for kw in text_database.keywords(lang):
                    for t in text_database.texts_for(lang, kw):
                        total += 1
                        r = engine.check_text(t)
                        if r.blocked:
                            blocked += 1
                        elif r.warnings:
                            warned += 1
            self.comp_result.delete("1.0", "end")
            self.comp_result.insert(
                "end", f"Batch geprüft: {total} Texte\nBlockiert: {blocked}\n"
                       f"Warnungen: {warned}\nOK: {total - blocked - warned}")
            self.log(f"Compliance-Batch: {total} geprüft, {blocked} blockiert")

        # ----- Tab 8: Rückmeldung ----------------------------------
        def _tab_feedback(self) -> None:
            import prompt_feedback
            f = self._frame("Rückmeldung")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Button(top, text="Bild laden",
                       command=self._load_feedback_image).pack(side="left", padx=4)
            self.fb_path: Path | None = None
            self.fb_image_label = ttk.Label(top, text="(kein Bild geladen)")
            self.fb_image_label.pack(side="left", padx=8)

            self.fb_problems = {k: tk.BooleanVar()
                                for k in prompt_feedback.PROBLEM_CATEGORIES}
            grid = ttk.Frame(f)
            grid.pack(fill="x", pady=6)
            for i, (key, label) in enumerate(prompt_feedback.PROBLEM_CATEGORIES.items()):
                ttk.Checkbutton(grid, text=f"{key} — {label}",
                                variable=self.fb_problems[key]).grid(
                    row=i // 2, column=i % 2, sticky="w", padx=6)

            bar = ttk.Frame(f)
            bar.pack(fill="x")
            ttk.Label(bar, text="Bewertung:").pack(side="left")
            self.fb_rating = tk.IntVar(value=3)
            ttk.Spinbox(bar, from_=1, to=5, textvariable=self.fb_rating,
                        width=3).pack(side="left", padx=4)
            ttk.Button(bar, text="Feedback speichern",
                       command=self._save_feedback).pack(side="left", padx=8)
            ttk.Button(bar, text="Bildanalyse (Gemini/GPT-4o)",
                       command=self._ai_analyze).pack(side="left", padx=4)
            ttk.Button(bar, text="Aktive Prompt-Fixes anzeigen",
                       command=self._show_fixes).pack(side="left", padx=4)
            self.fb_result = ttk.Label(f, text="", foreground="#345")
            self.fb_result.pack(anchor="w", pady=4)

        def _load_feedback_image(self) -> None:
            path = filedialog.askopenfilename(
                title="Design öffnen", filetypes=[("Bilder", "*.png *.jpg *.jpeg")])
            if path:
                self.fb_path = Path(path)
                self.fb_image_label.configure(text=self.fb_path.name)
                self.log("Feedback-Bild geladen: " + self.fb_path.name)

        def _save_feedback(self) -> None:
            import prompt_feedback
            problems = [k for k, v in self.fb_problems.items() if v.get()]
            try:
                prompt_feedback.default_store().add_report(
                    problems, rating=int(self.fb_rating.get()), note="", prompt="")
                counts = prompt_feedback.default_store().problem_counts()
                active = prompt_feedback.default_store().active_fixes()
                self.fb_result.configure(
                    text=f"Gespeichert. Zähler: {counts} | Aktive Fixes: {len(active)}")
                self.log(f"Feedback gespeichert (Probleme: {problems or 'keine'})")
            except ValueError as exc:
                messagebox.showerror("Feedback", str(exc))

        def _ai_analyze(self) -> None:
            import prompt_feedback
            if not self.fb_path:
                messagebox.showinfo("KI-Analyse", "Bitte zuerst ein Bild laden.")
                return

            def work() -> None:
                answer = prompt_feedback.analyze_with_ai(self.fb_path, provider="gemini")
                self.log("KI-Analyse: " + (answer[:400] if answer else
                                           "kein Backend verfügbar (Key/SDK fehlt)"))

            threading.Thread(target=work, daemon=True).start()

        def _show_fixes(self) -> None:
            import prompt_feedback
            fixes = prompt_feedback.default_store().active_fixes()
            messagebox.showinfo(
                "Aktive Prompt-Fixes",
                "\n".join(fixes) if fixes else
                "Noch keine aktiven Fixes (ab 2x gleichem Problem aktiv).")

        # ----- Tab 9: API-Schlüssel --------------------------------
        def _tab_keys(self) -> None:
            import key_manager
            f = self._frame("API-Schlüssel")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Key einfügen:").pack(side="left")
            self.key_input = tk.StringVar()
            ttk.Entry(top, textvariable=self.key_input, width=50,
                      show="•").pack(side="left", padx=4, fill="x", expand=True)
            ttk.Button(top, text="Erkennen & speichern",
                       command=self._store_key).pack(side="left", padx=4)

            self.keys_state = ttk.Label(f, text="")
            self.keys_state.pack(anchor="w", pady=4)
            bar = ttk.Frame(f)
            bar.pack(fill="x")
            for service in key_manager.SERVICES:
                ttk.Button(bar, text=f"Verbindungstest {service}",
                           command=lambda s=service: self._test_key(s)).pack(
                    side="left", padx=4)
            self._refresh_keys()

        def _refresh_keys(self) -> None:
            import key_manager
            self.keys_state.configure(
                text="Gespeichert: " + " | ".join(
                    f"{s}: {masked}" for s, masked in key_manager.mask_all().items()))

        def _store_key(self) -> None:
            import api_key_detector
            service, msg = api_key_detector.detect_and_store(self.key_input.get())
            if service:
                self.key_input.set("")
                self._refresh_keys()
                self.log(f"API-Key gespeichert: {service}")
            else:
                messagebox.showwarning("Key-Erkennung", msg)

        def _test_key(self, service: str) -> None:
            import key_manager

            def work() -> None:
                ok, msg = key_manager.test_connection(service)
                self.log(msg + (" ✓" if ok else ""))

            threading.Thread(target=work, daemon=True).start()

        # ----- Tab 10: Verkäufe ------------------------------------
        def _tab_sales(self) -> None:
            f = self._frame("Verkäufe")
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Design:").pack(side="left")
            self.sales_design = tk.StringVar(value="")
            ttk.Entry(top, textvariable=self.sales_design, width=30).pack(
                side="left", padx=4)
            ttk.Label(top, text="Plattform:").pack(side="left", padx=(8, 0))
            self.sales_platform = tk.StringVar(value="redbubble")
            ttk.Combobox(top, textvariable=self.sales_platform, width=12,
                         values=[p.key for p in brand_identity.active_platforms()],
                         state="readonly").pack(side="left", padx=4)
            ttk.Label(top, text="Anzahl:").pack(side="left", padx=(8, 0))
            self.sales_count = tk.IntVar(value=1)
            ttk.Spinbox(top, from_=1, to=999, textvariable=self.sales_count,
                        width=5).pack(side="left", padx=4)
            ttk.Button(top, text="Eintragen",
                       command=self._add_sale).pack(side="left", padx=6)
            ttk.Button(top, text="Bericht generieren",
                       command=self._sales_report).pack(side="left", padx=6)

            self.sales_result = scrolledtext.ScrolledText(f, height=14)
            self.sales_result.pack(fill="both", expand=True, pady=6)

        def _add_sale(self) -> None:
            import sales_tracker
            name = self.sales_design.get().strip()
            if not name:
                messagebox.showinfo("Verkäufe", "Bitte Design-Namen eingeben.")
                return
            sales_tracker.SalesTracker().add_sale(
                name, self.sales_platform.get(), max(1, int(self.sales_count.get())))
            self.log(f"Verkauf eingetragen: {name} +{self.sales_count.get()}")
            self._sales_report()

        def _sales_report(self) -> None:
            import sales_tracker
            tracker = sales_tracker.SalesTracker()
            tiers = tracker.tiers()
            lines = [tracker.report(), "", "Performance-Tiers:",
                     *(f"  {n:40s} {t}" for n, t in sorted(tiers.items()))]
            self.sales_result.delete("1.0", "end")
            self.sales_result.insert("end", "\n".join(lines))

        # ----- Tab 11: Bericht -------------------------------------
        def _tab_report(self) -> None:
            f = self._frame("Bericht")
            self.report_text = scrolledtext.ScrolledText(f, height=24,
                                                         state="disabled")
            self.report_text.pack(fill="both", expand=True)
            for line in self._report_lines:
                self.report_text.configure(state="normal")
                self.report_text.insert("end", line + "\n")
                self.report_text.configure(state="disabled")
            bar = ttk.Frame(f)
            bar.pack(fill="x", pady=4)
            ttk.Button(bar, text="Bericht kopieren",
                       command=self._copy_report).pack(side="left", padx=4)
            ttk.Button(bar, text="Report-Datei öffnen",
                       command=self._open_report_file).pack(side="left", padx=4)

        def _copy_report(self) -> None:
            import upload_manager
            text = self.report_text.get("1.0", "end").strip()
            ok = upload_manager.copy_to_clipboard(text)
            self.log("Bericht " + ("kopiert." if ok else "kopieren fehlgeschlagen."))

        def _open_report_file(self) -> None:
            import subprocess
            log_file = config.LOGS_DIR / "generator.log"
            if not log_file.exists():
                messagebox.showinfo("Bericht", "Noch keine Report-Datei vorhanden.")
                return
            try:
                if sys.platform == "win32":
                    subprocess.Popen(["notepad", str(log_file)])
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", str(log_file)])
                else:
                    subprocess.Popen(["xdg-open", str(log_file)])
            except OSError:
                messagebox.showinfo("Bericht", f"Datei: {log_file}")


else:

    class GenesisPanel:  # Platzhalter ohne Tkinter
        """Fallback, wenn Tkinter fehlt — alle Funktionen via CLI nutzbar."""

        def __init__(self) -> None:
            raise RuntimeError(
                "Tkinter ist nicht verfügbar. GUI kann nicht starten. "
                "Alle Funktionen laufen über die Module/CLI.")


# ================================================================== Selftest
def run_selftest() -> int:
    """Baut die GUI komplett auf und testet alle Tabs (Display nötig)."""
    _require_tk()
    print("GUI-Selftest: erzeuge Panel …")
    panel = GenesisPanel()
    panel.withdraw()

    checks = 0
    try:
        # Alle Tabs wurden gebaut
        assert panel.notebook.index("end") == 11, "erwartet 11 Tabs"
        checks += 1

        # Generator-Logik (kleines Design, deterministisch)
        import generator
        path = generator.generate_design("Selftest Design", size=400, seed=42)
        assert path.exists()
        checks += 1

        # Szene
        import scene_generator
        from scene_engine import SceneSpec
        spath = scene_generator.generate_scene(
            SceneSpec(figure="pinguin", obj="eis", background="sky"), size=400)
        assert spath.exists()
        checks += 1

        # Hybrid
        import hybrid_scene_engine
        from hybrid_scene_engine import HybridSpec
        imgs = hybrid_scene_engine.generate_hybrid(
            HybridSpec(figure="katze", text="Miau", variants=2))
        assert len(imgs) == 2
        checks += 1

        # Compliance-GUI
        panel.comp_text.set("But First Coffee")
        panel._run_compliance()
        checks += 1

        # Sales
        panel.sales_design.set("selftest_design")
        panel._sales_report()
        checks += 1

        # Feedback
        import prompt_feedback
        prompt_feedback.default_store().add_report(["missing_foot"], rating=2)
        checks += 1

        # Upload-Metadaten
        import upload_manager
        title = upload_manager.build_title("But First Coffee")
        assert 0 < len(title) <= 60
        checks += 1
    finally:
        panel.destroy()

    print(f"GUI-Selftest OK — {checks} Checks bestanden (11 Tabs, alle Module).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="control_panel", description="GENESIS SYSTEM / Zeichenwerk GUI")
    parser.add_argument("--selftest", action="store_true",
                        help="GUI aufbauen, alle Tabs testen, beenden")
    args = parser.parse_args(argv)

    config.ensure_directories()

    if args.selftest:
        return run_selftest()

    _require_tk()
    panel = GenesisPanel()
    panel.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
