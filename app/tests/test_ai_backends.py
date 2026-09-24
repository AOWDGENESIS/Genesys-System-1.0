"""Tests: huggingface_engine.py + gemini_engine.py (mit Mocks, ohne Netz)."""

from __future__ import annotations

import base64
import io
import sys
import types

import pytest
from PIL import Image

import gemini_engine
import huggingface_engine as hf
import key_manager


# ================================================================ HuggingFace
def test_model_registry() -> None:
    assert set(hf.MODELS) == {"flux_schnell", "sdxl", "sd21", "sd14"}
    assert "FLUX.1-schnell" in hf.MODELS["flux_schnell"]


def test_unavailable_without_token(tmp_ini) -> None:
    pytest.importorskip("huggingface_hub")
    assert not hf.available()
    with pytest.raises(hf.HuggingFaceUnavailable, match="Token"):
        hf.generate_image("test")


def test_unavailable_message_without_module(tmp_path, monkeypatch) -> None:
    # simuliere fehlendes Modul
    monkeypatch.setitem(sys.modules, "huggingface_hub", None)
    monkeypatch.setattr(key_manager, "get_key", lambda s: "hf_" + "x" * 30)
    with pytest.raises(hf.HuggingFaceUnavailable, match="nicht installiert"):
        hf.generate_image("test")


def test_generate_with_mock_client(tmp_path, tmp_ini, monkeypatch) -> None:
    img = Image.new("RGB", (512, 512), (90, 120, 200))
    calls = {}

    class FakeClient:
        def __init__(self, token=None):
            calls["token"] = token

        def text_to_image(self, prompt, model=None, **kw):
            calls["prompt"] = prompt
            calls["model"] = model
            return img

    fake_hub = types.ModuleType("huggingface_hub")
    fake_hub.InferenceClient = FakeClient
    monkeypatch.setitem(sys.modules, "huggingface_hub", fake_hub)
    key_manager.set_key("huggingface", "hf_" + "z" * 30)

    out = hf.generate_image("a penguin", "flux_schnell", size=512,
                            out_path=tmp_path / "hf.png")
    assert out.exists()
    assert Image.open(out).size == (512, 512)
    assert "FLUX" in calls["model"]
    assert calls["token"].startswith("hf_")


def test_generate_with_bytes_result(tmp_path, tmp_ini, monkeypatch) -> None:
    buf = io.BytesIO()
    Image.new("RGB", (512, 512), (1, 2, 3)).save(buf, "PNG")

    class FakeClient:
        def __init__(self, token=None): ...

        def text_to_image(self, prompt, model=None, **kw):
            return buf.getvalue()

    fake_hub = types.ModuleType("huggingface_hub")
    fake_hub.InferenceClient = FakeClient
    monkeypatch.setitem(sys.modules, "huggingface_hub", fake_hub)
    key_manager.set_key("huggingface", "hf_" + "y" * 30)

    out = hf.generate_image("x", "sdxl", size=512, out_path=tmp_path / "b.png")
    assert Image.open(out).size == (512, 512)


def test_invalid_model_raises(tmp_path, monkeypatch) -> None:
    with pytest.raises(ValueError):
        hf.generate_image("x", model_key="midjourney")


# ================================================================ Gemini
def test_gemini_models() -> None:
    assert set(gemini_engine.MODELS) == {"gemini-2.5-flash", "gemini-2.0-flash"}


def test_unavailable_without_key(tmp_ini) -> None:
    pytest.importorskip("google.genai")
    with pytest.raises(gemini_engine.GeminiUnavailable, match="Key"):
        gemini_engine.generate_image("test")


def test_unavailable_without_module(monkeypatch, tmp_ini) -> None:
    monkeypatch.setitem(sys.modules, "google", None)
    with pytest.raises(gemini_engine.GeminiUnavailable, match="nicht installiert"):
        gemini_engine.generate_image("test")


def _fake_genai_module(monkeypatch, response):
    fake_genai = types.ModuleType("genai")

    class FakeClient:
        def __init__(self, api_key=None): ...

        class models:  # noqa: N801
            @staticmethod
            def generate_content(model=None, contents=None):
                return response

    fake_genai.Client = FakeClient
    google_pkg = types.ModuleType("google")
    google_pkg.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", google_pkg)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    return fake_genai


def test_generate_image_with_image_response(tmp_path, tmp_ini, monkeypatch) -> None:
    key_manager.set_key("gemini", "AIzaSy" + "k" * 34)
    buf = io.BytesIO()
    Image.new("RGB", (700, 700), (5, 200, 8)).save(buf, "PNG")
    inline = types.SimpleNamespace(
        mime_type="image/png",
        data=base64.b64encode(buf.getvalue()).decode())
    part = types.SimpleNamespace(inline_data=inline)
    cand = types.SimpleNamespace(content=types.SimpleNamespace(parts=[part]))
    resp = types.SimpleNamespace(candidates=[cand])
    _fake_genai_module(monkeypatch, resp)

    out = gemini_engine.generate_image("a cat", size=512,
                                       out_path=tmp_path / "g.png")
    assert Image.open(out).size == (512, 512)


def test_generate_image_without_image_raises(tmp_path, tmp_ini, monkeypatch) -> None:
    key_manager.set_key("gemini", "AIzaSy" + "k" * 34)
    part = types.SimpleNamespace(inline_data=None, text="nur text")
    cand = types.SimpleNamespace(content=types.SimpleNamespace(parts=[part]))
    resp = types.SimpleNamespace(candidates=[cand])
    _fake_genai_module(monkeypatch, resp)
    with pytest.raises(gemini_engine.GeminiUnavailable, match="kein Bild"):
        gemini_engine.generate_image("a cat")


def test_gemini_invalid_model_raises(tmp_ini) -> None:
    with pytest.raises(ValueError):
        gemini_engine.generate_image("x", model="gemini-99")


def test_translate_fallback_local(tmp_ini, monkeypatch) -> None:
    # ohne Client: lokale Wörterbuch-Übersetzung
    monkeypatch.setitem(sys.modules, "google", None)
    result = gemini_engine.translate_de_en("pinguin trinkt kaffee")
    assert "penguin" in result and "coffee" in result
