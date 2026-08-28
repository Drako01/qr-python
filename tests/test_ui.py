import flet as ft

from qr_studio.app import _TRANSPARENT_PNG_BASE64, _create_preview_image


def test_preview_image_has_required_source_and_starts_hidden() -> None:
    preview = _create_preview_image()

    assert isinstance(preview, ft.Image)
    assert preview.src == _TRANSPARENT_PNG_BASE64
    assert preview.visible is False
    assert preview.width == 420
    assert preview.height == 420
