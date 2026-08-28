from __future__ import annotations

import base64
from pathlib import Path

import flet as ft

from qr_studio.generator import qr_to_png_bytes, save_qr
from qr_studio.models import QRConfig


# Flet 0.86+ requires Image.src at construction time. A transparent 1x1 PNG
# keeps the preview control valid while remaining invisible until a QR exists.
_TRANSPARENT_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M/wHwAF"
    "gAI/6Mv5WQAAAABJRU5ErkJggg=="
)


def _create_preview_image() -> ft.Image:
    """Create a valid, initially hidden preview control for current Flet APIs."""
    return ft.Image(
        src=_TRANSPARENT_PNG_BASE64,
        width=420,
        height=420,
        fit=ft.BoxFit.CONTAIN,
        border_radius=ft.BorderRadius.all(18),
        visible=False,
    )


def main(page: ft.Page) -> None:
    page.title = "QR Studio · Professional QR Generator"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO

    data = ft.TextField(
        label="Contenido",
        hint_text="https://armotusitio.com.ar/ o cualquier texto",
        multiline=True,
        min_lines=3,
        max_lines=6,
        autofocus=True,
    )
    output = ft.TextField(label="Archivo de salida", value="qr-code.png")
    logo = ft.TextField(
        label="Logo opcional",
        hint_text="Ruta a un archivo PNG, JPG o WEBP",
    )
    fill_color = ft.TextField(label="Color del QR", value="#111827")
    background_color = ft.TextField(label="Color de fondo", value="#FFFFFF")
    correction = ft.Dropdown(
        label="Corrección de errores",
        value="M",
        options=[ft.DropdownOption(key=value, text=value) for value in ("L", "M", "Q", "H")],
    )
    box_size = ft.Slider(min=4, max=24, divisions=20, value=12, label="{value}")
    border = ft.Slider(min=4, max=12, divisions=8, value=4, label="{value}")
    logo_scale = ft.Slider(min=8, max=25, divisions=17, value=18, label="{value}%")

    preview = _create_preview_image()
    preview_hint = ft.Text(
        "Tu QR aparecerá aquí",
        size=18,
        weight=ft.FontWeight.W_600,
        color=ft.Colors.GREY_600,
    )
    status = ft.Text("Listo para generar.", color=ft.Colors.GREY_700)

    def build_config() -> QRConfig:
        logo_value = (logo.value or "").strip()
        return QRConfig(
            data=data.value or "",
            output=Path((output.value or "qr-code.png").strip()),
            fill_color=(fill_color.value or "#111827").strip(),
            background_color=(background_color.value or "#FFFFFF").strip(),
            box_size=int(box_size.value or 12),
            border=int(border.value or 4),
            error_correction=correction.value or "M",
            logo_path=Path(logo_value).expanduser() if logo_value else None,
            logo_scale=float(logo_scale.value or 18) / 100,
        )

    def update_preview(config: QRConfig) -> None:
        png = qr_to_png_bytes(config)
        preview.src = base64.b64encode(png).decode("ascii")
        preview.visible = True
        preview_hint.visible = False

    def generate_click(_: ft.Event[ft.Button]) -> None:
        try:
            config = build_config()
            update_preview(config)
            saved = save_qr(config)
            status.value = f"✓ QR generado y guardado en {saved}"
            status.color = ft.Colors.GREEN_700
            if config.logo_path:
                correction.value = "H"
        except Exception as exc:
            status.value = f"No se pudo generar el QR: {exc}"
            status.color = ft.Colors.RED_700
        page.update()

    def preview_click(_: ft.Event[ft.Button]) -> None:
        try:
            update_preview(build_config())
            status.value = "✓ Vista previa actualizada."
            status.color = ft.Colors.BLUE_700
        except Exception as exc:
            status.value = f"No se pudo generar la vista previa: {exc}"
            status.color = ft.Colors.RED_700
        page.update()

    header = ft.Column(
        controls=[
            ft.Text("QR Studio", size=34, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Generador profesional de códigos QR con personalización y logo opcional.",
                size=16,
                color=ft.Colors.GREY_700,
            ),
        ],
        spacing=4,
    )

    form = ft.Container(
        padding=24,
        border_radius=20,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(
            controls=[
                ft.Text("Configuración", size=22, weight=ft.FontWeight.BOLD),
                data,
                output,
                logo,
                ft.Row(controls=[fill_color, background_color], wrap=True),
                correction,
                ft.Text("Tamaño de módulos", weight=ft.FontWeight.W_600),
                box_size,
                ft.Text("Quiet zone / borde", weight=ft.FontWeight.W_600),
                border,
                ft.Text("Tamaño del logo", weight=ft.FontWeight.W_600),
                logo_scale,
                ft.Text(
                    "Al usar logo, QR Studio fuerza corrección H y limita el logo al 25% para proteger la lectura.",
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
                ft.Row(
                    controls=[
                        ft.Button(content="Vista previa", icon=ft.Icons.VISIBILITY, on_click=preview_click),
                        ft.Button(content="Generar PNG", icon=ft.Icons.DOWNLOAD, on_click=generate_click),
                    ],
                    wrap=True,
                ),
                status,
            ],
            spacing=14,
        ),
    )

    preview_panel = ft.Container(
        padding=24,
        border_radius=20,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Vista previa", size=22, weight=ft.FontWeight.BOLD),
                preview_hint,
                preview,
                ft.Text(
                    "Consejo: probá siempre el código con más de un lector antes de imprimirlo.",
                    size=12,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=16,
        ),
    )

    page.bgcolor = ft.Colors.GREY_100
    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    header,
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(col={"sm": 12, "lg": 7}, content=form),
                            ft.Container(col={"sm": 12, "lg": 5}, content=preview_panel),
                        ],
                        spacing=20,
                        run_spacing=20,
                    ),
                    ft.Text(
                        "QR Studio v2.0.0 · Alejandro Daniel Di Stefano · MIT",
                        size=12,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                spacing=24,
            )
        )
    )


if __name__ == "__main__":
    ft.run(main)
