from __future__ import annotations

import base64
from pathlib import Path

import flet as ft
from flet_color_pickers import ColorLabelType, ColorPicker

from qr_studio.generator import qr_to_png_bytes, save_qr
from qr_studio.models import QRConfig

_PRIMARY = "#6D28D9"
_PRIMARY_SOFT = "#F5F3FF"
_ACCENT = "#0891B2"
_CANVAS = "#F4F6FA"
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
        width=420,
        height=420,
        fit=ft.BoxFit.CONTAIN,
        border_radius=ft.BorderRadius.all(18),
        visible=False,
    )


def _build_footer() -> ft.Container:
    return ft.Container(
        height=38,
        padding=ft.Padding.symmetric(horizontal=18),
        border=ft.Border(top=ft.BorderSide(1, _BORDER)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("QR Studio v2.0.0 · MIT", size=11, color=_MUTED),
                ft.Text(
                    spans=[
                        ft.TextSpan("Desarrollado por ", style=ft.TextStyle(color=_MUTED, size=11)),
                        ft.TextSpan(
                            "ArmoTuSitio.com",
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
        spacing=2,
        controls=[
            ft.Text(title, size=19, weight=ft.FontWeight.BOLD, color=_TEXT),
            ft.Text(subtitle, size=11, color=_MUTED),
        ],
    )


def _field_row(*controls: ft.Control) -> ft.ResponsiveRow:
    return ft.ResponsiveRow(
        spacing=12,
        run_spacing=12,
        controls=[ft.Container(col={"sm": 12, "md": 6}, content=control) for control in controls],
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
        multiline=True,
        min_lines=2,
        max_lines=3,
        autofocus=True,
        border_radius=12,
    )
    output = ft.TextField(
        label="Archivo de salida",
        value="qr-code.png",
        prefix_icon=ft.Icons.SAVE_OUTLINED,
        border_radius=12,
    )
    logo = ft.TextField(
        label="Logo opcional",
        hint_text="Seleccioná una imagen o pegá una ruta",
        prefix_icon=ft.Icons.IMAGE_OUTLINED,
        border_radius=12,
        expand=True,
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
        read_only=True,
        border_radius=12,
        expand=True,
    )
    background_color = ft.TextField(
        label="Color de fondo",
        value="#FFFFFF",
        read_only=True,
        border_radius=12,
        expand=True,
    )
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
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        controls=[
            ft.Icon(ft.Icons.QR_CODE_2, size=58, color="#CBD5E1"),
            ft.Text("Tu QR aparecerá aquí", size=18, weight=ft.FontWeight.W_600, color=_MUTED),
            ft.Text(
                "Completá el contenido y generá una vista previa.",
                size=12,
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
            width=42,
            height=42,
            border_radius=10,
            bgcolor=initial,
            border=ft.Border.all(1, _BORDER),
        )
        picker = ColorPicker(
            color=initial,
            enable_alpha=False,
            hex_input_bar=True,
            color_picker_width=330,
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
            actions=[ft.Button(content="Aplicar", icon=ft.Icons.CHECK, on_click=lambda _: page.pop_dialog())],
        )

        def open_picker(_: ft.Event[ft.Button]) -> None:
            picker.color = field.value or initial
            page.show_dialog(dialog)

        return ft.Row(
            spacing=8,
            controls=[
                field,
                ft.Button(
                    content=swatch,
                    tooltip=f"Elegir {label.lower()}",
                    on_click=open_picker,
                    style=ft.ButtonStyle(padding=4, shape=ft.RoundedRectangleBorder(radius=12)),
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
        spacing=4,
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
                            bgcolor=_PRIMARY_SOFT,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                            shape=ft.RoundedRectangleBorder(radius=12),
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
        height=70,
        bgcolor=_TEXT,
        padding=ft.Padding.symmetric(horizontal=22),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=40,
                            height=40,
                            alignment=ft.Alignment.CENTER,
                            border_radius=11,
                            bgcolor=_PRIMARY,
                            content=ft.Icon(ft.Icons.QR_CODE_2, color=ft.Colors.WHITE, size=24),
                        ),
                        ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=1,
                            controls=[
                                ft.Text("QR Studio", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(
                                    "Generador profesional de códigos QR",
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
            bgcolor=_PRIMARY_SOFT,
            padding=ft.Padding.symmetric(horizontal=18, vertical=12),
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
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    slider_group = ft.Container(
        padding=14,
        border_radius=14,
        bgcolor=_SURFACE_ALT,
        border=ft.Border.all(1, "#EEF2F7"),
        content=ft.ResponsiveRow(
            spacing=12,
            run_spacing=10,
            controls=[
                ft.Container(
                    col={"sm": 12, "md": 4},
                    content=ft.Column(spacing=2, controls=[ft.Text("Tamaño de módulos", size=11, weight=ft.FontWeight.W_600), box_size]),
                ),
                ft.Container(
                    col={"sm": 12, "md": 4},
                    content=ft.Column(spacing=2, controls=[ft.Text("Quiet zone / borde", size=11, weight=ft.FontWeight.W_600), border]),
                ),
                ft.Container(
                    col={"sm": 12, "md": 4},
                    content=ft.Column(spacing=2, controls=[ft.Text("Tamaño del logo", size=11, weight=ft.FontWeight.W_600), logo_scale]),
                ),
            ],
        ),
    )

    actions = ft.ResponsiveRow(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        run_spacing=10,
        controls=[
            ft.Container(
                col={"sm": 12, "md": 7},
                content=ft.Row(controls=[preview_button, generate_button], spacing=10, wrap=True),
            ),
            ft.Container(
                col={"sm": 12, "md": 5},
                alignment=ft.Alignment.CENTER_RIGHT,
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                border_radius=10,
                bgcolor=_SURFACE_ALT,
                content=status,
            ),
        ],
    )

    form_card = ft.Container(
        expand=True,
        padding=22,
        border_radius=18,
        bgcolor=_SURFACE,
        border=ft.Border.all(1, _BORDER),
        content=ft.Column(
            expand=True,
            spacing=14,
            controls=[
                _section_title("Configuración", "Definí contenido, apariencia y exportación."),
                ft.Divider(height=1, color=_BORDER),
                data,
                _field_row(output, logo_selector),
                _field_row(fill_color_selector, background_color_selector),
                correction,
                slider_group,
                ft.Container(
                    padding=12,
                    border_radius=12,
                    bgcolor="#ECFEFF",
                    border=ft.Border.all(1, "#A5F3FC"),
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=_ACCENT, size=17),
                            ft.Text(
                                "Con logo se usa corrección H y una escala máxima del 25% para preservar la lectura.",
                                size=11,
                                color="#155E75",
                                expand=True,
                            ),
                        ]
                    ),
                ),
                ft.Container(expand=True),
                actions,
            ],
        ),
    )

    preview_frame = ft.Container(
        expand=True,
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

    preview_card = ft.Container(
        expand=True,
        padding=22,
        border_radius=18,
        bgcolor=_SURFACE,
        border=ft.Border.all(1, _BORDER),
        content=ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
            controls=[
                _section_title("Vista previa", "Validá el resultado antes de exportarlo."),
                preview_frame,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.VERIFIED_OUTLINED, color=_SUCCESS, size=16),
                        ft.Text("Probalo con más de un lector antes de imprimirlo.", size=10, color=_MUTED),
                    ],
                ),
            ],
        ),
    )

    desktop_workspace = ft.Row(
        expand=True,
        spacing=16,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Container(expand=7, content=form_card),
            ft.Container(expand=5, content=preview_card),
        ],
    )
    mobile_workspace = ft.Column(
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        controls=[form_card, preview_card],
    )
    workspace = ft.Container(expand=True, padding=ft.Padding.all(16), content=desktop_workspace)
    shell = ft.Column(expand=True, spacing=0, controls=[hero, workspace, _build_footer()])

    def adapt_to_viewport(_: ft.PageResizeEvent | None = None) -> None:
        width = float(page.width or 1280)
        height = float(page.height or 800)
        desktop = width >= 1050

        workspace.content = desktop_workspace if desktop else mobile_workspace
        workspace.padding = ft.Padding.all(12 if height < 760 else 16)

        if desktop:
            usable_height = max(380.0, height - 190)
            usable_width = max(360.0, width * 0.36)
            size = max(300.0, min(520.0, usable_height * 0.72, usable_width * 0.78))
            preview.width = size
            preview.height = size
            form_card.padding = 18 if height < 760 else 22
            preview_card.padding = 18 if height < 760 else 22
        else:
            size = max(250.0, min(380.0, width * 0.66))
            preview.width = size
            preview.height = size

        page.update()

    page.on_resize = adapt_to_viewport
    page.add(ft.SafeArea(content=shell, expand=True))
    adapt_to_viewport()


if __name__ == "__main__":
    ft.run(main)
