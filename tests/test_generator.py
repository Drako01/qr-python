from pathlib import Path

import pytest
from PIL import Image

from qr_studio.generator import generate_qr, qr_to_png_bytes, save_qr
from qr_studio.models import QRConfig


def test_generate_basic_qr() -> None:
    image = generate_qr(QRConfig(data="https://example.com"))
    assert image.width > 0
    assert image.height > 0
    assert image.width == image.height


def test_logo_forces_high_error_correction(tmp_path: Path) -> None:
    logo = tmp_path / "logo.png"
    Image.new("RGBA", (120, 80), (255, 0, 0, 255)).save(logo)
    config = QRConfig(data="logo-test", logo_path=logo, error_correction="L")
    assert config.effective_error_correction == "H"
    image = generate_qr(config)
    assert image.width == image.height


def test_save_creates_parent_directory(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "code.png"
    saved = save_qr(QRConfig(data="persist", output=output))
    assert saved == output.resolve()
    assert output.is_file()


def test_png_bytes_are_valid_png() -> None:
    data = qr_to_png_bytes(QRConfig(data="memory"))
    assert data.startswith(b"\x89PNG\r\n\x1a\n")


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"data": ""}, "vacío"),
        ({"data": "x", "border": 2}, "borde"),
        ({"data": "x", "box_size": 1}, "box_size"),
        ({"data": "x", "logo_scale": 0.30}, "logo_scale"),
        ({"data": "x", "error_correction": "X"}, "corrección"),
    ],
)
def test_invalid_configurations(kwargs: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        QRConfig(**kwargs).validate()
