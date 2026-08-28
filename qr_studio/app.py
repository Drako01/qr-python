from __future__ import annotations

import base64
from pathlib import Path

import flet as ft
from flet_color_pickers import ColorLabelType, ColorPicker

from qr_studio.generator import qr_to_png_bytes, save_qr
from qr_studio.models import QRConfig

_PRIMARY = "#6D28D9"
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

_TRANSPARENT_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M/wHwAF"
    "gAI/6Mv5WQAAAABJRU5ErkJggg=="
)


def _create_preview_image() -> ft.Image:
    return ft.Image(
        src=_TRANSPARENT_PNG_BASE64,
        width=380,
        height=380,
        fit=ft.BoxFit.CONTAIN,
        border_radius=ft.BorderRadius.all(16),
        visible=False,
    )


def _build_footer() -> ft.Container:
    return ft.Container(
        padding=ft.Padding.symmetric(vertical=8, horizontal=18),
        border=ft.Border(top=ft.BorderSide(1, _BORDER)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
            controls=[
                ft.Text("QR Studio v2.0.0 · MIT", size=11, color=_MUTED),
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            text="Desarrollado por ",
                            style=ft.TextStyle(color=_MUTED, size=11),
                        ),
                        ft.TextSpan(
                            text="ArmoTuSitio.com",
                            url="https://armotusitio.com.ar/",
                            style=ft.TextStyle(
                                color=_PRIMARY,
                                size=11,
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
        spacing=1,
        controls=[
            ft.Text(title, size=19, weight=ft.FontWeight.BOLD, color=_TEXT),
            ft.Text(subtitle, size=11, color=_MUTED),
        ],
    )


def _field_row(*controls: ft.Control) -> ft.ResponsiveRow:
    return ft.ResponsiveRow(
        controls=[ft.Container(col={"sm": 12, "md": 6}, content=control) for control in controls],
        spacing=10,
        run_spacing=10,
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
    page.scroll = ft.ScrollMode.HIDDEN
    page.window.min_width = 720
    page.window.min_height = 620
    page.window.maximized = True

    data = ft.TextField(
        label="Contenido",
        hint_text="https://armotusitio.com.ar/ o cualquier texto",
        multiline=False,
        autofocus=True,
        border_radius=12,
        dense=True,
    )
    output = ft.TextField(
        label="Archivo de salida",
        value="qr-code.png",
        border_radius=12,
        prefix_icon=ft.Icons.SAVE_OUTLINED,
        dense=True,
    )
    logo = ft.TextField(
        label="Logo opcional",
        hint_text="Seleccioná una imagen o pegá una ruta manualmente",
        border_radius=12,
        prefix_icon=ft.Icons.IMAGE_OUTLINED,
        expand=True,
        dense=True,
    )
    selected_logo = ft.Text(
        "Ningún archivo seleccionado",
        size=10,
        color=_MUTED,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    fill_color = ft.TextField(
        label="Color del QR",
        value="#111827",
        border_radius=12,
        read_only=True,
        expand=True,
        dense=True,
    )
    background_color = ft.TextField(
        label="Color de fondo",
        value="#FFFFFF",
        border_radius=12,
        read_only=True,
        expand=True,
        dense=True,
    )
    correction = ft.Dropdown(
        label="Corrección de errores",
        value="M",
        border_radius=12,
        dense=True,
        options=[ft.DropdownOption(key=value, text=value) for value in ("L", "M", "Q", "H")],
    )
    box_size = ft.Slider(min=4, max=24, divisions=20, value=12, label="{value}")
    border = ft.Slider(min=4, max=12, divisions=8, value=4, label="{value}")
    logo_scale = ft.Slider(min=8, max=25, divisions=17, value=18, label="{value}%")

    preview = _create_preview_image()
    preview_hint = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
        controls=[
            ft.Icon(ft.Icons.QR_CODE_2, size=46, color="#CBD5E1"),
            ft.Text("Tu QR aparecerá aquí", size=16, weight=ft.FontWeight.W_600, color=_MUTED),
            ft.Text(
                "Completá el contenido y usá Vista previa.",
                size=11,
                color="#94A3B8",
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )
    status = ft.Text("Listo para generar.", color=_MUTED, size=12, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)

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

    def refresh_preview_if_possible() -> None:
        if not (data.value or "").strip():
            return
        try:
            update_preview(build_config())
        except Exception:
            return

    def build_color_selector(label: str, field: ft.TextField, initial: str) -> ft.Row:
        swatch = ft.Container(
            width=36,
            height=36,
            border_radius=9,
            bgcolor=initial,
            border=ft.Border.all(1, _BORDER),
        )
        picker = ColorPicker(
            color=initial,
            enable_alpha=False,
            hex_input_bar=True,
            color_picker_width=320,
            label_types=[ColorLabelType.HEX, ColorLabelType.RGB],
            color_history=["#111827", "#FFFFFF", "#000000", "#2563EB", "#16A34A", "#DC2626"],
        )

        def on_color_change(event: ft.ControlEvent) -> None:
            selected = str(event.data or picker.color or initial).upper()
            field.value = selected
            swatch.bgcolor = selected
            refresh_preview_if_possible()
            page.update()

        picker.on_color_change = on_color_change
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Elegir {label.lower()}"),
            content=picker,
            actions=[ft.Button(content="Listo", icon=ft.Icons.CHECK, on_click=lambda _: page.pop_dialog())],
        )

        def open_picker(_: ft.Event[ft.Button]) -> None:
            picker.color = field.value or initial
            page.show_dialog(dialog)

        return ft.Row(
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                field,
                ft.Button(
                    content=swatch,
                    tooltip=f"Elegir {label.lower()}",
                    on_click=open_picker,
                    style=ft.ButtonStyle(padding=3, shape=ft.RoundedRectangleBorder(radius=10)),
                ),
            ],
        )

    fill_color_selector = build_color_selector("Color del QR", fill_color, "#111827")
    background_color_selector = build_color_selector("Color de fondo", background_color, "#FFFFFF")

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
            status.value = "No se obtuvo una ruta local utilizable."
            status.color = _ERROR
            page.update()
            return
        logo.value = selected.path
        selected_logo.value = f"Seleccionado: {selected.name}"
        selected_logo.color = _SUCCESS
        status.value = "✓ Logo cargado · corrección H automática"
        status.color = _SUCCESS
        refresh_preview_if_possible()
        page.update()

    def clear_logo(_: ft.Event[ft.IconButton]) -> None:
        logo.value = ""
        selected_logo.value = "Ningún archivo seleccionado"
        selected_logo.color = _MUTED
        status.value = "Logo eliminado."
        status.color = _MUTED
        refresh_preview_if_possible()
        page.update()

    logo_selector = ft.Column(
        spacing=3,
        controls=[
            ft.Row(
                spacing=6,
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
                            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Quitar logo", on_click=clear_logo),
                ],
            ),
            selected_logo,
        ],
    )

    def generate_click(_: ft.Event[ft.Button]) -> None:
        try:
            config = build_config()
            update_preview(config)
            saved = save_qr(config)
            status.value = f"✓ Guardado en {saved}"
            status.color = _SUCCESS
            if config.logo_path:
                correction.value = "H"
        except Exception as exc:
            status.value = f"No se pudo generar: {exc}"
            status.color = _ERROR
        page.update()

    def preview_click(_: ft.Event[ft.Button]) -> None:
        try:
            update_preview(build_config())
            status.value = "✓ Vista previa actualizada"
            status.color = _ACCENT
        except Exception as exc:
            status.value = f"No se pudo previsualizar: {exc}"
            status.color = _ERROR
        page.update()

    hero = ft.Container(
        bgcolor=_TEXT,
        padding=ft.Padding.symmetric(horizontal=24, vertical=12),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=9,
                    controls=[
                        ft.Container(
                            width=36,
                            height=36,
                            alignment=ft.Alignment.CENTER,
                            border_radius=10,
                            bgcolor=_PRIMARY,
                            content=ft.Icon(ft.Icons.QR_CODE_2, color=ft.Colors.WHITE, size=22),
                        ),
                        ft.Column(
                            spacing=0,
                            controls=[
                                ft.Text("QR Studio", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(
                                    "Códigos QR profesionales, personalizables y listos para compartir.",
                                    size=11,
                                    color="#CBD5E1",
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Text("Python · Flet · qrcode", size=10, color="#CBD5E1"),
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
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )
    generate_button = ft.Button(
        content="Generar PNG",
        icon=ft.Icons.DOWNLOAD,
        on_click=generate_click,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=_PRIMARY,
            padding=ft.Padding.symmetric(horizontal=18, vertical=10),
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

    sliders = ft.ResponsiveRow(
        spacing=10,
        run_spacing=8,
        controls=[
            ft.Container(
                col={"sm": 12, "md": 4},
                content=ft.Column(
                    spacing=0,
                    controls=[ft.Text("Módulos", size=11, weight=ft.FontWeight.W_600, color=_TEXT), box_size],
                ),
            ),
            ft.Container(
                col={"sm": 12, "md": 4},
                content=ft.Column(
                    spacing=0,
                    controls=[ft.Text("Quiet zone", size=11, weight=ft.FontWeight.W_600, color=_TEXT), border],
                ),
            ),
            ft.Container(
                col={"sm": 12, "md": 4},
                content=ft.Column(
                    spacing=0,
                    controls=[ft.Text("Logo", size=11, weight=ft.FontWeight.W_600, color=_TEXT), logo_scale],
                ),
            ),
        ],
    )

    actions_status = ft.ResponsiveRow(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        run_spacing=8,
        controls=[
            ft.Container(
                col={"sm": 12, "md": 7},
                content=ft.Row(controls=[preview_button, generate_button], wrap=True, spacing=8),
            ),
            ft.Container(
                col={"sm": 12, "md": 5},
                alignment=ft.Alignment.CENTER_RIGHT,
                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                border_radius=10,
                bgcolor=_SURFACE_ALT,
                content=status,
            ),
        ],
    )

    form = ft.Container(
        padding=18,
        border_radius=18,
        bgcolor=_SURFACE,
        border=ft.Border.all(1, _BORDER),
        content=ft.Column(
            spacing=10,
            controls=[
                _section_title("Configuración", "Definí el contenido, apariencia y exportación del código QR."),
                ft.Divider(height=1, color=_BORDER),
                data,
                _field_row(output, logo_selector),
                _field_row(fill_color_selector, background_color_selector),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    border_radius=12,
                    bgcolor=_SURFACE_ALT,
                    content=ft.ResponsiveRow(
                        spacing=10,
                        run_spacing=8,
                        controls=[
                            ft.Container(col={"sm": 12, "md": 3}, content=correction),
                            ft.Container(col={"sm": 12, "md": 9}, content=sliders),
                        ],
                    ),
                ),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    border_radius=10,
                    bgcolor="#ECFEFF",
                    border=ft.Border.all(1, "#A5F3FC"),
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=_ACCENT, size=16),
                            ft.Text(
                                "Con logo se usa corrección H y una escala máxima del 25% para preservar la lectura.",
                                size=10,
                                color="#155E75",
                                expand=True,
                            ),
                        ],
                    ),
                ),
                actions_status,
            ],
        ),
    )

    preview_frame = ft.Container(
        width=380,
        height=380,
        alignment=ft.Alignment.CENTER,
        border_radius=18,
        bgcolor=_SURFACE_ALT,
        border=ft.Border.all(1, _BORDER),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[preview_hint, preview],
        ),
    )

    preview_panel = ft.Container(
        padding=18,
        border_radius=18,
        bgcolor=_SURFACE,
        border=ft.Border.all(1, _BORDER),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                _section_title("Vista previa", "Validá el resultado antes de exportarlo."),
                preview_frame,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.VERIFIED_OUTLINED, color=_SUCCESS, size=15),
                        ft.Text("Probalo con más de un lector antes de imprimirlo.", size=10, color=_MUTED),
                    ],
                ),
            ],
        ),
    )

    body_row = ft.ResponsiveRow(
        expand=True,
        controls=[
            ft.Container(col={"sm": 12, "lg": 7}, content=form),
            ft.Container(col={"sm": 12, "lg": 5}, content=preview_panel),
        ],
        spacing=14,
        run_spacing=14,
    )

    body = ft.Container(
        expand=True,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        content=ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[body_row]),
    )
    shell = ft.Column(expand=True, spacing=0, controls=[hero, body, _build_footer()])

    def adapt_to_viewport(_: ft.PageResizeEvent | None = None) -> None:
        width = float(page.width or 1280)
        height = float(page.height or 800)
        compact = height < 820

        if width >= 1100:
            available = min(width * 0.31, height - (255 if compact else 285))
            size = max(260.0, min(390.0, available))
        else:
            size = max(240.0, min(360.0, width * 0.7))

        preview.width = size - 18
        preview.height = size - 18
        preview_frame.width = size
        preview_frame.height = size
        form.padding = 14 if compact else 18
        preview_panel.padding = 14 if compact else 18
        body.padding = ft.Padding.symmetric(
            horizontal=12 if width < 900 else 16,
            vertical=8 if compact else 12,
        )
        page.update()

    page.on_resize = adapt_to_viewport
    page.add(ft.SafeArea(content=shell, expand=True))
    adapt_to_viewport()


if __name__ == "__main__":
    ft.run(main)
