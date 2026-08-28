from __future__ import annotations

import base64
from pathlib import Path

import flet as ft

from qr_studio.generator import qr_to_png_bytes, save_qr
from qr_studio.models import QRConfig


_PRIMARY = "#6D28D9"
_PRIMARY_DARK = "#4C1D95"
_ACCENT = "#0891B2"
_CANVAS = "#F5F7FB"
_SURFACE = "#FFFFFF"
_SURFACE_ALT = "#F8FAFC"
_TEXT = "#0F172A"
_MUTED = "#64748B"
_BORDER = "#E2E8F0"
_SUCCESS = "#15803D"
_ERROR = "#B91C1C"
_LOGO_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]

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


def _build_footer() -> ft.Container:
    """Build the product footer with ArmoTuSitio attribution and external link."""
    return ft.Container(
        padding=ft.Padding.symmetric(vertical=18, horizontal=20),
        border=ft.Border(top=ft.BorderSide(1, _BORDER)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
            controls=[
                ft.Text(
                    "QR Studio v2.0.0 · MIT",
                    size=12,
                    color=_MUTED,
                ),
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            text="Desarrollado por ",
                            style=ft.TextStyle(color=_MUTED, size=12),
                        ),
                        ft.TextSpan(
                            text="ArmoTuSitio.com",
                            url="https://armotusitio.com.ar/",
                            style=ft.TextStyle(
                                color=_PRIMARY,
                                size=12,
                                weight=ft.FontWeight.W_600,
                                decoration=ft.TextDecoration.UNDERLINE,
                            ),
                        ),
                    ]
                ),
            ],
        ),
    )


def _section_title(title: str, subtitle: str) -> ft.Column:
    return ft.Column(
        spacing=3,
        controls=[
            ft.Text(title, size=21, weight=ft.FontWeight.BOLD, color=_TEXT),
            ft.Text(subtitle, size=12, color=_MUTED),
        ],
    )


def _field_row(*controls: ft.Control) -> ft.ResponsiveRow:
    return ft.ResponsiveRow(
        controls=[ft.Container(col={"sm": 12, "md": 6}, content=control) for control in controls],
        spacing=12,
        run_spacing=12,
    )


def main(page: ft.Page) -> None:
    page.title = "QR Studio · Professional QR Generator"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=_PRIMARY,
            secondary=_ACCENT,
            surface=_SURFACE,
            outline=_BORDER,
            error=_ERROR,
        )
    )
    page.bgcolor = _CANVAS
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    data = ft.TextField(
        label="Contenido",
        hint_text="https://armotusitio.com.ar/ o cualquier texto",
        multiline=True,
        min_lines=3,
        max_lines=6,
        autofocus=True,
        border_radius=12,
    )
    output = ft.TextField(
        label="Archivo de salida",
        value="qr-code.png",
        border_radius=12,
        prefix_icon=ft.Icons.SAVE_OUTLINED,
    )
    logo = ft.TextField(
        label="Logo opcional",
        hint_text="Seleccioná una imagen o pegá una ruta manualmente",
        border_radius=12,
        prefix_icon=ft.Icons.IMAGE_OUTLINED,
        expand=True,
    )
    selected_logo = ft.Text(
        "Ningún archivo seleccionado",
        size=11,
        color=_MUTED,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )
    fill_color = ft.TextField(label="Color del QR", value="#111827", border_radius=12)
    background_color = ft.TextField(label="Color de fondo", value="#FFFFFF", border_radius=12)
    correction = ft.Dropdown(
        label="Corrección de errores",
        value="M",
        border_radius=12,
        options=[ft.DropdownOption(key=value, text=value) for value in ("L", "M", "Q", "H")],
    )
    box_size = ft.Slider(min=4, max=24, divisions=20, value=12, label="{value}")
    border = ft.Slider(min=4, max=12, divisions=8, value=4, label="{value}")
    logo_scale = ft.Slider(min=8, max=25, divisions=17, value=18, label="{value}%")

    preview = _create_preview_image()
    preview_hint = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        controls=[
            ft.Icon(ft.Icons.QR_CODE_2, size=54, color="#CBD5E1"),
            ft.Text(
                "Tu QR aparecerá aquí",
                size=17,
                weight=ft.FontWeight.W_600,
                color=_MUTED,
            ),
            ft.Text(
                "Completá el contenido y usá Vista previa.",
                size=12,
                color="#94A3B8",
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )
    status = ft.Text("Listo para generar.", color=_MUTED, size=13)

    async def pick_logo(_: ft.Event[ft.Button]) -> None:
        files = await ft.FilePicker().pick_files(
            dialog_title="Seleccionar logo",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=_LOGO_EXTENSIONS,
            allow_multiple=False,
        )
        if not files:
            return

        selected = files[0]
        if not selected.path:
            status.value = "El selector no devolvió una ruta local utilizable para este archivo."
            status.color = _ERROR
            page.update()
            return

        logo.value = selected.path
        selected_logo.value = f"Seleccionado: {selected.name}"
        selected_logo.color = _SUCCESS
        status.value = "✓ Logo cargado. La corrección H se aplicará automáticamente."
        status.color = _SUCCESS
        page.update()

    def clear_logo(_: ft.Event[ft.IconButton]) -> None:
        logo.value = ""
        selected_logo.value = "Ningún archivo seleccionado"
        selected_logo.color = _MUTED
        status.value = "Logo eliminado."
        status.color = _MUTED
        page.update()

    logo_selector = ft.Column(
        spacing=6,
        controls=[
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    logo,
                    ft.Button(
                        content="Cargar",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=pick_logo,
                        style=ft.ButtonStyle(
                            color=_PRIMARY,
                            bgcolor="#F5F3FF",
                            padding=ft.Padding.symmetric(horizontal=14, vertical=14),
                            shape=ft.RoundedRectangleBorder(radius=12),
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        tooltip="Quitar logo",
                        on_click=clear_logo,
                    ),
                ],
            ),
            selected_logo,
            ft.Text(
                "Formatos admitidos: PNG, JPG, JPEG y WEBP.",
                size=10,
                color="#94A3B8",
            ),
        ],
    )

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
            status.color = _SUCCESS
            if config.logo_path:
                correction.value = "H"
        except Exception as exc:
            status.value = f"No se pudo generar el QR: {exc}"
            status.color = _ERROR
        page.update()

    def preview_click(_: ft.Event[ft.Button]) -> None:
        try:
            update_preview(build_config())
            status.value = "✓ Vista previa actualizada."
            status.color = _ACCENT
        except Exception as exc:
            status.value = f"No se pudo generar la vista previa: {exc}"
            status.color = _ERROR
        page.update()

    hero = ft.Container(
        bgcolor=_TEXT,
        padding=ft.Padding.symmetric(horizontal=32, vertical=28),
        content=ft.ResponsiveRow(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    col={"sm": 12, "lg": 8},
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Container(
                                        width=42,
                                        height=42,
                                        alignment=ft.Alignment.CENTER,
                                        border_radius=12,
                                        bgcolor=_PRIMARY,
                                        content=ft.Icon(ft.Icons.QR_CODE_2, color=ft.Colors.WHITE, size=25),
                                    ),
                                    ft.Text(
                                        "QR Studio",
                                        size=31,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                ],
                            ),
                            ft.Text(
                                "Códigos QR profesionales, personalizables y listos para compartir.",
                                size=15,
                                color="#CBD5E1",
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    col={"sm": 12, "lg": 4},
                    alignment=ft.Alignment.CENTER_RIGHT,
                    content=ft.Container(
                        padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                        border_radius=100,
                        bgcolor="#1E293B",
                        content=ft.Text(
                            "Python · Flet · qrcode",
                            size=12,
                            color="#E2E8F0",
                            weight=ft.FontWeight.W_500,
                        ),
                    ),
                ),
            ],
        ),
    )

    preview_button = ft.Button(
        content="Vista previa",
        icon=ft.Icons.VISIBILITY,
        on_click=preview_click,
        style=ft.ButtonStyle(
            color=_PRIMARY,
            bgcolor="#F5F3FF",
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )
    generate_button = ft.Button(
        content="Generar PNG",
        icon=ft.Icons.DOWNLOAD,
        on_click=generate_click,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=_PRIMARY,
            padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    form = ft.Container(
        padding=26,
        border_radius=18,
        bgcolor=_SURFACE,
        border=ft.Border.all(1, _BORDER),
        content=ft.Column(
            spacing=18,
            controls=[
                _section_title(
                    "Configuración",
                    "Definí el contenido, apariencia y exportación del código QR.",
                ),
                ft.Divider(height=1, color=_BORDER),
                data,
                _field_row(output, logo_selector),
                _field_row(fill_color, background_color),
                correction,
                ft.Container(
                    padding=16,
                    border_radius=14,
                    bgcolor=_SURFACE_ALT,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text("Tamaño de módulos", weight=ft.FontWeight.W_600, color=_TEXT),
                            box_size,
                            ft.Text("Quiet zone / borde", weight=ft.FontWeight.W_600, color=_TEXT),
                            border,
                            ft.Text("Tamaño del logo", weight=ft.FontWeight.W_600, color=_TEXT),
                            logo_scale,
                        ],
                    ),
                ),
                ft.Container(
                    padding=14,
                    border_radius=12,
                    bgcolor="#ECFEFF",
                    border=ft.Border.all(1, "#A5F3FC"),
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=_ACCENT, size=19),
                            ft.Text(
                                "Si agregás un logo, QR Studio usa corrección H y limita su escala al 25% para preservar la lectura.",
                                size=12,
                                color="#155E75",
                                expand=True,
                            ),
                        ],
                    ),
                ),
                ft.Row(
                    controls=[preview_button, generate_button],
                    wrap=True,
                    spacing=10,
                ),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=10,
                    bgcolor=_SURFACE_ALT,
                    content=status,
                ),
            ],
        ),
    )

    preview_panel = ft.Container(
        padding=26,
        border_radius=18,
        bgcolor=_SURFACE,
        border=ft.Border.all(1, _BORDER),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                _section_title("Vista previa", "Validá el resultado antes de exportarlo."),
                ft.Container(
                    width=440,
                    height=440,
                    alignment=ft.Alignment.CENTER,
                    border_radius=18,
                    bgcolor=_SURFACE_ALT,
                    border=ft.Border.all(1, _BORDER),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[preview_hint, preview],
                    ),
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.VERIFIED_OUTLINED, color=_SUCCESS, size=17),
                        ft.Text(
                            "Probalo con más de un lector antes de imprimirlo.",
                            size=12,
                            color=_MUTED,
                        ),
                    ],
                ),
            ],
        ),
    )

    page.add(
        ft.SafeArea(
            content=ft.Column(
                spacing=0,
                controls=[
                    hero,
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=28, vertical=28),
                        content=ft.ResponsiveRow(
                            controls=[
                                ft.Container(col={"sm": 12, "xl": 7}, content=form),
                                ft.Container(col={"sm": 12, "xl": 5}, content=preview_panel),
                            ],
                            spacing=20,
                            run_spacing=20,
                        ),
                    ),
                    _build_footer(),
                ],
            )
        )
    )


if __name__ == "__main__":
    ft.run(main)
