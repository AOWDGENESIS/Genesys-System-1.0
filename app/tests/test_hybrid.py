"""Tests: hybrid_scene_engine.py (Varianten, Prompts, Fallback)."""

from __future__ import annotations

import pytest
from PIL import Image

import hybrid_scene_engine as hse
import prompt_feedback


def test_max_variants_constant() -> None:
    assert hse.MAX_VARIANTS == 4


def test_build_prompt_contains_anatomy_rules() -> None:
    prompt = hse.build_prompt("pinguin")
    assert "full body character visible" in prompt
    assert "NO text NO words NO letters in image" in prompt
    assert "penguin" in prompt


def test_build_prompt_with_object() -> None:
    prompt = hse.build_prompt("katze", "kaffee")
    assert "cat" in prompt and "coffee" in prompt


def test_build_prompt_appends_learned_fixes(tmp_path) -> None:
    store = prompt_feedback.FeedbackStore(tmp_path / "fb.json")
    store.add_report(["too_dark"], rating=1)
    store.add_report(["too_dark"], rating=1)
    prompt = prompt_feedback.enhance_prompt(hse.build_prompt("hund"), store)
    assert "bright even lighting" in prompt


@pytest.mark.parametrize("variants", [1, 2, 3, 4])
def test_generate_hybrid_variants(variants) -> None:
    spec = hse.HybridSpec(figure="pinguin", text="Hallo", variants=variants,
                          seed=1)
    imgs = hse.generate_hybrid(spec)
    assert len(imgs) == variants
    for img in imgs:
        assert img.size == (2000, 2000)


def test_variants_differ_with_auto_backgrounds() -> None:
    spec = hse.HybridSpec(figure="fuchs", text="Ich bin anders", variants=3,
                          seed=2)
    imgs = hse.generate_hybrid(spec)
    assert len({img.tobytes() for img in imgs}) > 1


def test_explicit_background_all_same_bg() -> None:
    spec = hse.HybridSpec(figure="baer", text="Wald", variants=2,
                          background="forest", seed=3)
    imgs = hse.generate_hybrid(spec)
    assert len(imgs) == 2


def test_own_ai_image_used() -> None:
    ai = Image.new("RGB", (512, 512), (10, 200, 120))
    spec = hse.HybridSpec(figure="hund", text="Wuff", variants=1, seed=4)
    out = hse.generate_hybrid(spec, ai_image=ai)[0]
    assert out.size == (512, 512)  # Compositing in der Größe des KI-Bildes


def test_invalid_variants_raise() -> None:
    with pytest.raises(ValueError):
        hse.generate_hybrid(hse.HybridSpec(figure="katze", variants=0))
    with pytest.raises(ValueError):
        hse.generate_hybrid(hse.HybridSpec(figure="katze", variants=5))


def test_invalid_fallback_figure_raises() -> None:
    with pytest.raises(ValueError):
        hse.generate_hybrid(hse.HybridSpec(figure="drache3d", variants=1))


def test_compose_variant_layout_applied() -> None:
    from PIL import Image as PILImage
    ai = PILImage.new("RGB", (300, 300), (200, 200, 10))
    spec = hse.HybridSpec(figure="eule", text="Hu Hu", layout="free_top")
    import random
    out = hse.compose_variant(ai, spec, "night", None, random.Random(1))
    assert out.size == (300, 300)
