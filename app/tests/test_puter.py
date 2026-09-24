"""Tests: puter_engine.py (HTTP-Bridge headless, Base64-Empfang, Fehler)."""

from __future__ import annotations

import base64
import io
import json
import threading
import urllib.request

import pytest
from PIL import Image

import puter_engine


def _png_b64(size: int = 64) -> str:
    buf = io.BytesIO()
    Image.new("RGB", (size, size), (180, 40, 90)).save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


@pytest.fixture()
def bridge() -> puter_engine.PuterBridge:
    # Port 0 = freier Port
    b = puter_engine.PuterBridge(port=0)
    b._server = None  # start_server nutzt self.port — für Port 0 anpassen:
    import http.server
    b._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
                                                puter_engine._BridgeHandler)
    b.port = b._server.server_address[1]
    b._thread = threading.Thread(target=b._server.serve_forever, daemon=True)
    b._thread.start()
    yield b
    b.stop_server()


def _get(bridge, path: str):
    with urllib.request.urlopen(f"http://127.0.0.1:{bridge.port}{path}",
                                timeout=5) as r:
        return r.status, r.read()


def _post(bridge, path: str, payload: dict):
    req = urllib.request.Request(
        f"http://127.0.0.1:{bridge.port}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ---------------------------------------------------------------- Server
def test_serves_bridge_html(bridge) -> None:
    status, body = _get(bridge, "/")
    assert status == 200
    assert b"js.puter.com" in body


def test_status_endpoint(bridge) -> None:
    status, body = _get(bridge, "/status")
    data = json.loads(body)
    assert status == 200 and data["ready"] is True


def test_job_endpoint(bridge) -> None:
    bridge.state.reset({"prompt": "test", "model": "dalle3",
                        "puter_model": "dall-e-3", "size": 64})
    status, body = _get(bridge, "/job")
    assert json.loads(body)["prompt"] == "test"


def test_404(bridge) -> None:
    import urllib.error
    with pytest.raises(urllib.error.HTTPError):
        _get(bridge, "/gibtsnicht")


# ---------------------------------------------------------------- Ergebnis
def test_result_roundtrip(bridge, tmp_path) -> None:
    bridge.state.reset({"prompt": "p", "model": "dalle3", "size": 256})
    status, _ = _post(bridge, "/result", {"image_b64": _png_b64()})
    assert status == 200
    assert bridge.state.result_event.is_set()
    assert bridge.state.image_b64

    # Bild aus State dekodieren (wie generate_image)
    img = Image.open(io.BytesIO(base64.b64decode(bridge.state.image_b64)))
    assert img.size == (64, 64)


def test_result_invalid_b64(bridge) -> None:
    bridge.state.reset({})
    status, _ = _post(bridge, "/result", {"image_b64": "kein-base64!!!"})
    assert status == 400
    assert bridge.state.error


def test_result_empty_rejected(bridge) -> None:
    bridge.state.reset({})
    status, _ = _post(bridge, "/result", {"image_b64": ""})
    assert status == 400


def test_error_endpoint(bridge) -> None:
    bridge.state.reset({})
    status, _ = _post(bridge, "/error", {"error": "puter down"})
    assert status == 200
    assert bridge.state.error == "puter down"


# ---------------------------------------------------------------- generate
def test_generate_image_headless(bridge, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(puter_engine.webbrowser, "open", lambda url: True)

    def fake_result():
        status, _ = _post(bridge, "/result", {"image_b64": _png_b64()})
        assert status == 200

    bridge.state.reset({})
    timer = threading.Timer(0.3, fake_result)
    timer.start()
    out = bridge.generate_image("test prompt", size=300, timeout=10,
                                open_browser=True, out_path=tmp_path / "out.png")
    timer.join()
    assert out.exists()
    assert Image.open(out).size == (300, 300)  # hochskaliert auf Zielpixel


def test_generate_image_invalid_model(bridge) -> None:
    with pytest.raises(ValueError):
        bridge.generate_image("x", model_key="unbekannt")


# ---------------------------------------------------------------- Registry
def test_model_lists() -> None:
    assert len(puter_engine.IMAGE_MODELS) == 6
    assert set(puter_engine.IMAGE_MODELS) == {
        "flux_11_pro_ultra", "dalle3", "gpt_image_1", "imagen_4_ultra",
        "sdxl", "seedream_3"}
    assert len(puter_engine.CHAT_MODELS) == 6
    assert "claude_sonnet_4" in puter_engine.CHAT_MODELS


def test_bridge_html_valid(bridge) -> None:
    import re
    html = puter_engine.BRIDGE_FILE.read_text(encoding="utf-8")
    assert "js.puter.com/v2/" in html
    assert "/result" in html
    assert "txt2img" in html
    assert "/job" in html
    # kein inline-event-Handler-Krampf
    assert "onclick=" not in html
    _ = re
