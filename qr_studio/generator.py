from __future__ import annotations

from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image, ImageColor, ImageDraw

from qr_studio.models import QRConfig


_ERROR_CORRECTION = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


def generate_qr(config: QRConfig) -> Image.Image:
    """Generate a QR image from a validated configuration."""
    config.validate()

    qr = qrcode.QRCode(
        version=None,
        error_correction=_ERROR_CORRECTION[config.effective_error_correction],
        box_size=config.box_size,
        border=config.border,
    )
    qr.add_data(config.data.strip())
    qr.make(fit=True)

    image = qr.make_image(
        fill_color=config.fill_color,
        back_color=config.background_color,
    ).convert("RGBA")

    if config.logo_path is not None:
        image = _embed_logo(
            qr_image=image,
            logo_path=config.logo_path,
            scale=config.logo_scale,
            background_color=config.background_color,
        )

    return image


def save_qr(config: QRConfig) -> Path:
    """Generate and persist a PNG QR code, creating parent directories."""
    image = generate_qr(config)
    output = config.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)
    return output


def qr_to_png_bytes(config: QRConfig) -> bytes:
    """Return a QR PNG in memory; useful for previews and integrations."""
    buffer = BytesIO()
    generate_qr(config).save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _embed_logo(
    *, qr_image: Image.Image, logo_path: Path, scale: float, background_color: str
) -> Image.Image:
    logo = Image.open(logo_path).convert("RGBA")
    max_side = max(1, int(min(qr_image.size) * scale))
    logo.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

    padding = max(6, int(max_side * 0.12))
    plate_size = (logo.width + padding * 2, logo.height + padding * 2)
    plate_color = ImageColor.getcolor(background_color, "RGBA")
    plate = Image.new("RGBA", plate_size, plate_color)

    radius = max(4, int(min(plate_size) * 0.12))
    mask = Image.new("L", plate_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, plate_size[0] - 1, plate_size[1] - 1), radius=radius, fill=255)
    plate.putalpha(mask)
    plate.alpha_composite(logo, (padding, padding))

    x = (qr_image.width - plate.width) // 2
    y = (qr_image.height - plate.height) // 2
    result = qr_image.copy()
    result.alpha_composite(plate, (x, y))
    return result
