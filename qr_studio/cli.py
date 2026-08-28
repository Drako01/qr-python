from __future__ import annotations

import argparse
from pathlib import Path

from qr_studio.generator import save_qr
from qr_studio.models import QRConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qr-studio",
        description="Generador profesional de códigos QR con soporte opcional de logo.",
    )
    parser.add_argument("data", help="Texto, URL o payload a codificar.")
    parser.add_argument("-o", "--output", default="qr-code.png", help="Archivo PNG de salida.")
    parser.add_argument("--logo", help="PNG/JPG/WEBP opcional para centrar dentro del QR.")
    parser.add_argument("--fill", default="#111827", help="Color del QR.")
    parser.add_argument("--background", default="#FFFFFF", help="Color de fondo.")
    parser.add_argument("--box-size", type=int, default=12, help="Tamaño de cada módulo.")
    parser.add_argument("--border", type=int, default=4, help="Quiet zone en módulos (mínimo 4).")
    parser.add_argument(
        "--error-correction",
        choices=("L", "M", "Q", "H"),
        default="M",
        help="Corrección de errores. Con logo se fuerza H automáticamente.",
    )
    parser.add_argument(
        "--logo-scale",
        type=float,
        default=0.18,
        help="Proporción máxima del logo respecto del QR (0.08-0.25).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = QRConfig(
        data=args.data,
        output=Path(args.output),
        fill_color=args.fill,
        background_color=args.background,
        box_size=args.box_size,
        border=args.border,
        error_correction=args.error_correction,
        logo_path=Path(args.logo) if args.logo else None,
        logo_scale=args.logo_scale,
    )

    try:
        output = save_qr(config)
    except (ValueError, OSError) as exc:
        raise SystemExit(f"Error: {exc}") from exc

    print(f"QR generado correctamente: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
