"""Tests: product_formats.py (7 Formate, contain/cover, Validierung)."""

from __future__ import annotations

import pytest
from PIL import Image

import product_formats as pf


EXPECTED = {
    "tshirt": (2000, 2000), "poster": (3000, 4000), "sticker": (1400, 1400),
    "mug": (2400, 1000), "phone": (1080, 1920), "pdf_a4": (2480, 3508),
    "social": (1080, 1080),
}


def test_seven_formats_spec() -> None:
    assert len(pf.PRODUCT_FORMATS) == 7
    for key, size in EXPECTED.items():
        assert pf.get_format(key).size == size, key


@pytest.mark.parametrize("key", list(EXPECTED))
def test_export_contain_all_formats(key, tmp_path) -> None:
    design = Image.new("RGB", (1000, 1000), (200, 40, 40))
    out = pf.export_for_product(design, key, tmp_path / f"{key}.png")
    assert Image.open(out).size == EXPECTED[key]


def test_export_cover_crops(tmp_path) -> None:
    design = Image.new("RGB", (1000, 500), (10, 200, 10))
    out = pf.export_for_product(design, "tshirt", tmp_path / "cover.png",
                                pad_mode="cover")
    assert Image.open(out).size == (2000, 2000)


def test_wide_design_contains(tmp_path) -> None:
    design = Image.new("RGB", (2000, 200), (5, 5, 200))
    out = pf.export_for_product(design, "phone", tmp_path / "wide.png")
    img = Image.open(out)
    assert img.size == (1080, 1920)
    # gestauchte Höhe: 200 * (1080/2000) = 108 → Design ist schmaler als Fläche
    assert img.size[1] == 1920


def test_invalid_format_raises(tmp_path) -> None:
    with pytest.raises(ValueError):
        pf.export_for_product(Image.new("RGB", (10, 10)), "plakat",
                              tmp_path / "x.png")


def test_invalid_pad_mode_raises(tmp_path) -> None:
    with pytest.raises(ValueError):
        pf.export_for_product(Image.new("RGB", (10, 10)), "tshirt",
                              tmp_path / "x.png", pad_mode="stretch")


def test_validate_for_platform() -> None:
    small = Image.new("RGB", (1000, 1000))
    problems = pf.validate_for_platform(small, 1500)
    assert problems and "Zu klein" in problems[0]
    ok = Image.new("RGB", (2000, 2000))
    assert pf.validate_for_platform(ok, 1500) == []
