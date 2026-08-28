from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ERROR_CORRECTION_LEVELS = {"L", "M", "Q", "H"}


@dataclass(frozen=True, slots=True)
class QRConfig:
    data: str
    output: Path = Path("qr-code.png")
    fill_color: str = "#111827"
    background_color: str = "#FFFFFF"
    box_size: int = 12
    border: int = 4
    error_correction: str = "M"
    logo_path: Path | None = None
    logo_scale: float = 0.18

    def validate(self) -> None:
        if not self.data.strip():
            raise ValueError("El contenido del QR no puede estar vacío.")
        if self.box_size < 2 or self.box_size > 40:
            raise ValueError("box_size debe estar entre 2 y 40.")
        if self.border < 4 or self.border > 20:
            raise ValueError("El borde debe estar entre 4 y 20 módulos.")
        if self.error_correction.upper() not in ERROR_CORRECTION_LEVELS:
            raise ValueError("Nivel de corrección inválido. Use L, M, Q o H.")
        if not 0.08 <= self.logo_scale <= 0.25:
            raise ValueError("logo_scale debe estar entre 0.08 y 0.25.")
        if self.logo_path is not None:
            if not self.logo_path.is_file():
                raise ValueError(f"No se encontró el logo: {self.logo_path}")
            if self.logo_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                raise ValueError("El logo debe ser PNG, JPG, JPEG o WEBP.")
        if self.output.suffix.lower() != ".png":
            raise ValueError("La salida debe utilizar extensión .png.")

    @property
    def effective_error_correction(self) -> str:
        return "H" if self.logo_path is not None else self.error_correction.upper()
