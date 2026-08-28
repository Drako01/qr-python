from qr_studio.app_v3 import _normalize_color


def test_normalize_color_strips_argb_alpha() -> None:
    assert _normalize_color("#FF2563EB") == "#2563EB"


def test_normalize_color_preserves_rgb() -> None:
    assert _normalize_color("#2563EB") == "#2563EB"


def test_normalize_color_expands_short_hex() -> None:
    assert _normalize_color("#ABC") == "#AABBCC"


def test_normalize_color_uses_fallback_for_invalid_value() -> None:
    assert _normalize_color("not-a-color", "#FFFFFF") == "#FFFFFF"
