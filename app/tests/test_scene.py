"""Tests: scene_engine.py (Szenen, Humor-DB, Übersetzung, Prompts)."""

from __future__ import annotations

import random

import pytest
from PIL import Image

import scene_engine


# ---------------------------------------------------------------- Figuren/Objekte
def test_25_figures_21_objects() -> None:
    assert len(scene_engine.FIGURES) == 25
    assert len(scene_engine.OBJECTS) == 21
    assert "pinguin" in scene_engine.FIGURES
    assert "kaffee" in scene_engine.OBJECTS


# ---------------------------------------------------------------- Humor-DB
def test_documented_humor_examples() -> None:
    assert scene_engine.HUMOR_DE["pinguin+eis"] == "Gibts auch Fisch-Eis?"
    assert scene_engine.HUMOR_DE["katze+kaffee"] == "Vor dem Kaffee rede ich nicht."
    assert scene_engine.HUMOR_DE["hund+pizza"] == "Pizza? ICH LIEBE DICH!"
    assert scene_engine.HUMOR_DE["faultier+laptop"] == "Home Office Champion seit immer."


def test_speech_text_known_combo() -> None:
    assert scene_engine.speech_text("hund", "pizza", "de") == "Pizza? ICH LIEBE DICH!"


def test_speech_text_fallback() -> None:
    rng = random.Random(1)
    text = scene_engine.speech_text("eule", "ball", "de", rng)
    assert text in scene_engine.DEFAULT_SPEECH_DE


def test_speech_text_english() -> None:
    assert scene_engine.speech_text("hund", "pizza", "en") == "Pizza? I LOVE YOU!"


# ---------------------------------------------------------------- Übersetzung
def test_translation_documented_words() -> None:
    assert scene_engine.translate_de_en("pinguin") == "penguin"
    assert scene_engine.translate_de_en("katze") == "cat"
    assert scene_engine.translate_de_en("kaffee") == "coffee"
    assert scene_engine.translate_de_en("unbekannteswort") == "unbekannteswort"


def test_translation_dict_size() -> None:
    # Spezifikation: 60+ Wörter automatisch übersetzt
    assert len(scene_engine.DE_EN) >= 60


# ---------------------------------------------------------------- KI-Prompt
def test_build_ai_prompt_contains_anatomy_rules() -> None:
    prompt = scene_engine.build_ai_prompt("pinguin", "eis")
    for rule in ("full body character visible", "both feet and legs clearly shown",
                 "front facing view", "no cropped body parts",
                 "NO text NO words NO letters in image"):
        assert rule in prompt, rule
    assert "penguin" in prompt and "ice cream" in prompt


# ---------------------------------------------------------------- Rendering
def test_render_scene_basic() -> None:
    spec = scene_engine.SceneSpec(figure="pinguin", obj="eis",
                                  background="sky", text="Hallo")
    img = scene_engine.render_scene(spec, 500)
    assert img.size == (500, 500)


def test_render_scene_all_layouts_deterministic() -> None:
    for layout in ("speech_bubble", "free_bottom", "no_text", "banner_top"):
        spec = scene_engine.SceneSpec(figure="katze", obj=None,
                                      background="clean_white",
                                      layout=layout, text="Miau", seed=3)
        img = scene_engine.render_scene(spec, 400)
        assert img.size == (400, 400)


def test_render_scene_same_seed_same_output() -> None:
    spec = scene_engine.SceneSpec(figure="hund", obj="ball", background="sunset",
                                  pattern="polka_dots", text="Wuff", seed=11)
    a = scene_engine.render_scene(spec, 400)
    b = scene_engine.render_scene(spec, 400)
    assert a.tobytes() == b.tobytes()


def test_render_scene_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        scene_engine.render_scene(scene_engine.SceneSpec(figure="drache3d"), 400)
    with pytest.raises(ValueError):
        scene_engine.render_scene(
            scene_engine.SceneSpec(figure="katze", obj="raumschiff"), 400)


def test_random_scene_spec_valid() -> None:
    rng = random.Random(2)
    for _ in range(10):
        spec = scene_engine.random_scene_spec(rng)
        img = scene_engine.render_scene(spec, 300)
        assert isinstance(img, Image.Image)
