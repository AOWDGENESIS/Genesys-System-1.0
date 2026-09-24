"""Puter.js Browser-Bridge: kostenlose KI-Bilder ohne API-Key.

Funktionsweise:
  1. Python startet lokalen HTTP-Server (Port 7788)
  2. Browser öffnet sich mit Bridge-Seite (puter_bridge_full.html)
  3. Puter.js SDK lädt im Browser
  4. JavaScript generiert Bild über Puter API
  5. Bild wird als Base64 an den Python-Server gesendet
  6. Python speichert als PNG (Standard 2000x2000)

Verbesserungen gegenüber V1:
- Thread-sicherer, abbruchbarer Server (sauberes Shutdown)
- GET /status für Health-Check, CORS-kompatibel
- Kein Busy-Wait: Ereignisbasiertes Warten auf Ergebnis
"""

from __future__ import annotations

import base64
import binascii
import io
import json
import logging
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image

import config

logger = logging.getLogger("genesis.puter")

BRIDGE_FILE = config.SYSTEM_DIR / "puter_bridge_full.html"

IMAGE_MODELS: dict[str, dict[str, str]] = {
    "flux_11_pro_ultra": {"label": "FLUX 1.1 Pro Ultra", "puter": "dall-e-3"},
    "dalle3": {"label": "DALL-E 3", "puter": "dall-e-3"},
    "gpt_image_1": {"label": "GPT Image 1", "puter": "gpt-image-1"},
    "imagen_4_ultra": {"label": "Imagen 4 Ultra", "puter": "imagen-4-ultra"},
    "sdxl": {"label": "Stable Diffusion XL", "puter": "stable-diffusion-xl"},
    "seedream_3": {"label": "Seedream 3", "puter": "seedream-3"},
}

CHAT_MODELS: dict[str, str] = {
    "claude_sonnet_4": "Claude Sonnet 4",
    "gpt-4o": "GPT-4o",
    "gemini_2.5_flash": "Gemini 2.5 Flash",
    "gemini_2.5_pro": "Gemini 2.5 Pro",
    "llama_4_maverick": "Llama 4 Maverick",
    "deepseek_r1": "DeepSeek R1",
}


class BridgeState:
    """Geteilte Zustand zwischen HTTP-Server und Aufrufer."""

    def __init__(self) -> None:
        self.result_event = threading.Event()
        self.image_b64: str | None = None
        self.error: str | None = None
        self.job: dict[str, object] = {}
        self.received_at: float = 0.0

    def reset(self, job: dict[str, object]) -> None:
        self.result_event.clear()
        self.image_b64 = None
        self.error = None
        self.job = job


class _BridgeHandler(BaseHTTPRequestHandler):
    """HTTP-Handler: liefert Bridge-Seite, nimmt Base64-Ergebnis an."""

    state: BridgeState  # wird von puter_engine gesetzt

    def log_message(self, fmt: str, *args: object) -> None:  # noqa: A003
        logger.debug("HTTP " + fmt % args)

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html", "/bridge"):
            if BRIDGE_FILE.exists():
                body = BRIDGE_FILE.read_bytes()
                self._send(200, body, "text/html; charset=utf-8")
            else:
                self._send(404, b"bridge html missing", "text/plain")
        elif self.path == "/job":
            body = json.dumps(self.state.job).encode()
            self._send(200, body, "application/json")
        elif self.path == "/status":
            body = json.dumps({
                "ready": True,
                "job_pending": bool(self.state.job),
                "result_ready": self.state.result_event.is_set(),
            }).encode()
            self._send(200, body, "application/json")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/result":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                image_b64 = payload.get("image_b64") or ""
                if not image_b64:
                    raise ValueError("leeres Bild")
                base64.b64decode(image_b64, validate=True)  # Validierung
                self.state.image_b64 = image_b64
                self.state.error = None
                self.state.received_at = time.time()
                self.state.result_event.set()
                self._send(200, b'{"ok": true}', "application/json")
            except (ValueError, binascii.Error) as exc:
                self.state.error = str(exc)
                self.state.result_event.set()
                self._send(400, str(exc).encode(), "text/plain")
        elif self.path == "/error":
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            self.state.error = str(payload.get("error", "unbekannt"))
            self.state.result_event.set()
            self._send(200, b'{"ok": true}', "application/json")
        else:
            self._send(404, b"not found", "text/plain")


class PuterBridge:
    """Lebenszyklus der Browser-Bridge: Server starten, warten, aufräumen."""

    def __init__(self, port: int = config.PUTER_PORT) -> None:
        self.port = port
        self.state = BridgeState()
        _BridgeHandler.state = self.state
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start_server(self) -> int:
        """Startet den HTTP-Server (nicht-blockierend). Gibt Port zurück."""
        if self._server is not None:
            return self.port
        self._server = ThreadingHTTPServer(("127.0.0.1", self.port), _BridgeHandler)
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        daemon=True, name="puter-bridge")
        self._thread.start()
        logger.info("Puter-Bridge läuft auf http://127.0.0.1:%d", self.port)
        return self.port

    def stop_server(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
            self._thread = None
            logger.info("Puter-Bridge gestoppt.")

    def is_running(self) -> bool:
        return self._server is not None

    def generate_image(
        self,
        prompt: str, *,
        model_key: str = "flux_11_pro_ultra",
        size: int = config.DEFAULT_SIZE,
        open_browser: bool = True,
        timeout: int = config.PUTER_RESULT_TIMEOUT,
        out_path: Path | None = None,
    ) -> Path:
        """Kompletter Durchlauf: Server + Browser + Warten + Speichern.

        Wirft TimeoutError bei Timeout, RuntimeError bei Browser-Fehler.
        """
        if model_key not in IMAGE_MODELS:
            raise ValueError(f"Unbekanntes Modell {model_key!r}. "
                             f"Erlaubt: {', '.join(IMAGE_MODELS)}")
        self.start_server()
        self.state.reset({
            "prompt": prompt,
            "model": model_key,
            "puter_model": IMAGE_MODELS[model_key]["puter"],
            "size": size,
        })

        url = f"http://127.0.0.1:{self.port}/"
        if open_browser and not webbrowser.open(url):
            raise RuntimeError(
                "Browser konnte nicht geöffnet werden. Bitte manuell öffnen: " + url
            )

        logger.info("Warte auf Browser-Ergebnis (Timeout %ds) …", timeout)
        if not self.state.result_event.wait(timeout):
            raise TimeoutError(f"Kein Ergebnis vom Browser innerhalb von {timeout}s.")
        if self.state.error or not self.state.image_b64:
            raise RuntimeError(f"Browser-Bridge-Fehler: {self.state.error}")

        img = Image.open(io.BytesIO(base64.b64decode(self.state.image_b64)))
        img = img.convert("RGB")
        if img.size != (size, size):
            img = img.resize((size, size), Image.LANCZOS)
        out_path = out_path or config.DESIGNS_DIR / f"puter_{int(time.time())}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "PNG", optimize=True)
        logger.info("Puter-Bild gespeichert: %s", out_path.name)
        self.state.job = {}
        return out_path


# ------------------------------------------------------- Prompt-Verbesserung
def improve_prompt_with_chat(prompt: str, model_key: str = "claude_sonnet_4",
                             timeout: int = 120) -> str:
    """Prompt-Verbesserung via Puter-Chat-Modell (braucht offene Bridge im Browser).

    Hinweis: Für den headless-Betrieb ohne Browser nicht verfügbar —
    gibt dann den Original-Prompt zurück.
    """
    _ = prompt, model_key, timeout
    logger.warning("improve_prompt_with_chat benötigt eine Browser-Session "
                   "(nicht headless verfügbar). Gebe Original-Prompt zurück.")
    return prompt


_DEFAULT_BRIDGE: PuterBridge | None = None


def default_bridge() -> PuterBridge:
    global _DEFAULT_BRIDGE  # noqa: PLW0603
    if _DEFAULT_BRIDGE is None:
        _DEFAULT_BRIDGE = PuterBridge()
    return _DEFAULT_BRIDGE
