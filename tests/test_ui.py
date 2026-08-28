import flet as ft

from qr_studio.app import (
    _LOGO_EXTENSIONS,
    _TRANSPARENT_PNG_BASE64,
    _build_footer,
    _create_preview_image,
)


def test_preview_image_has_required_source_and_starts_hidden() -> None:
    preview = _create_preview_image()

    assert isinstance(preview, ft.Image)
    assert preview.src == _TRANSPARENT_PNG_BASE64
    assert preview.visible is False
    assert preview.width == 420
    assert preview.height == 420


def test_footer_links_to_armotusitio() -> None:
    footer = _build_footer()

    assert isinstance(footer, ft.Container)
    assert isinstance(footer.content, ft.Row)

    attribution = footer.content.controls[1]
    assert isinstance(attribution, ft.Text)
    assert attribution.spans is not None

    link = attribution.spans[1]
    assert isinstance(link, ft.TextSpan)
    assert link.text == "ArmoTuSitio.com"
    assert link.url == "https://armotusitio.com.ar/"


def test_logo_picker_supports_expected_image_formats() -> None:
    assert _LOGO_EXTENSIONS == ["png", "jpg", "jpeg", "webp"]
