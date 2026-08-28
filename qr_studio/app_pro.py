from __future__ import annotations

import base64
import logging
import re
from pathlib import Path

import flet as ft
from flet_color_pickers import ColorLabelType, ColorPicker

from qr_studio.generator import qr_to_png_bytes, save_qr
from qr_studio.models import QRConfig

PRIMARY = "#6D28D9"
PRIMARY_SOFT = "#F5F3FF"
ACCENT = "#0891B2"
CANVAS = "#F4F6FA"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F8FAFC"
TEXT = "#0F172A"
MUTED = "#64748B"
BORDER = "#E2E8F0"
SUCCESS = "#15803D"
ERROR = "#B91C1C"
LOGO_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]
_HEX_RE = re.compile(r"^[0-9A-F]+$")

TRANSPARENT_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M/wHwAF"
    "gAI/6Mv5WQAAAABJRU5ErkJggg=="
)

logger = logging.getLogger("qr_studio")


def _configure_logging() -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def _normalize_picker_color(value: object, fallback: str = "#000000") -> str:
    """Normalize ColorPicker output to #RRGGBB.

    flet-color-pickers may emit an 8-digit ARGB value (#AARRGGBB), even with
    alpha disabled. Pillow/qrcode interpret 8-digit hex differently, so the
    alpha byte must be removed before the color reaches the QR generator.
    """
    raw = str(value or fallback).strip().upper()
    if raw.startswith("#"):
        raw = raw[1:]

    if len(raw) == 8:
        raw = raw[2:]  # AARRGGBB -> RRGGBB
    elif len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)

    if len(raw) != 6 or not _HEX_RE.fullmatch(raw):
        logger.warning("Color inválido recibido del picker: %r; usando %s", value, fallback)
        fallback_raw = fallback.strip().lstrip("#").upper()
        if len(fallback_raw) == 8:
            fallback_raw = fallback_raw[2:]
        if len(fallback_raw) != 6 or not _HEX_RE.fullmatch(fallback_raw):
            fallback_raw = "000000"
        return f"#{fallback_raw}"

    return f"#{raw}"


def _footer() -> ft.Container:
    return ft.Container(
        height=38,
        padding=ft.Padding.symmetric(horizontal=18),
        border=ft.Border(top=ft.BorderSide(1, BORDER)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("QR Studio v2.0.0 · MIT", size=11, color=MUTED),
                ft.Text(
                    spans=[
                        ft.TextSpan("Desarrollado por ", style=ft.TextStyle(color=MUTED, size=11)),
                        ft.TextSpan(
                            "ArmoTuSitio.com",
                            url="https://armotusitio.com.ar/",
                            style=ft.TextStyle(
                                color=PRIMARY,
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


def _title(title: str, subtitle: str) -> ft.Column:
    return ft.Column(
        spacing=2,
        controls=[
            ft.Text(title, size=19, weight=ft.FontWeight.BOLD, color=TEXT),
            ft.Text(subtitle, size=11, color=MUTED),
        ],
    )


def main(page: ft.Page) -> None:
    _configure_logging()
    logger.info("Iniciando QR Studio")

    page.title = "QR Studio · Professional QR Generator"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = CANVAS
    page.padding = 0
    page.scroll = ft.ScrollMode.HIDDEN
    page.window.min_width = 760
    page.window.min_height = 640
    page.window.maximized = True
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            secondary=ACCENT,
            surface=SURFACE,
            outline=BORDER,
            error=ERROR,
        )
    )

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
        prefix_icon=ft.Icons.SAVE_OUTLINED,
        border_radius=12,
        dense=True,
    )
    logo = ft.TextField(
        label="Logo opcional",
        hint_text="Seleccioná una imagen o pegá una ruta",
        prefix_icon=ft.Icons.IMAGE_OUTLINED,
        border_radius=12,
        dense=True,
        expand=True,
    )
    selected_logo = ft.Text(
        "Ningún archivo seleccionado",
        size=10,
        color=MUTED,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )
    fill_color = ft.TextField(
        label="Color del QR",
        value="#111827",
        read_only=True,
        border_radius=12,
        dense=True,
        expand=True,
    )
    background_color = ft.TextField(
        label="Color de fondo",
        value="#FFFFFF",
        read_only=True,
        border_radius=12,
        dense=True,
        expand=True,
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

    preview = ft.Image(
        src=TRANSPARENT_PNG_BASE64,
        width=420,
        height=420,
        fit=ft.BoxFit.CONTAIN,
        visible=False,
    )
    preview_hint = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        controls=[
            ft.Icon(ft.Icons.QR_CODE_2, size=58, color="#CBD5E1"),
            ft.Text("Tu QR aparecerá aquí", size=18, weight=ft.FontWeight.W_600, color=MUTED),
            ft.Text(
                "Completá el contenido y generá una vista previa.",
                size=12,
                color="#94A3B8",
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )
    status = ft.Text(
        "Listo para generar.",
        color=MUTED,
        size=12,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    def build_config() -> QRConfig:
        logo_value = (logo.value or "").strip()
        qr_color = _normalize_picker_color(fill_color.value, "#111827")
        bg_color = _normalize_picker_color(background_color.value, "#FFFFFF")
        fill_color.value = qr_color
        background_color.value = bg_color
        config = QRConfig(
            data=data.value or "",
            output=Path((output.value or "qr-code.png").strip()),
            fill_color=qr_color,
            background_color=bg_color,
            box_size=int(box_size.value or 12),
            border=int(border.value or 4),
            error_correction=correction.value or "M",
            logo_path=Path(logo_value).expanduser() if logo_value else None,
            logo_scale=float(logo_scale.value or 18) / 100,
        )
        logger.debug(
            "Config QR | data_len=%d fill=%s bg=%s correction=%s logo=%s",
            len(config.data),
            config.fill_color,
            config.background_color,
            config.error_correction,
            bool(config.logo_path),
        )
        return config

    def update_preview(config: QRConfig) -> None:
        png = qr_to_png_bytes(config)
        preview.src = base64.b64encode(png).decode("ascii")
        preview.visible = True
        preview_hint.visible = False
        logger.info("Preview actualizado | fill=%s bg=%s", config.fill_color, config.background_color)

    def refresh_preview() -> None:
        if not (data.value or "").strip():
            logger.debug("Preview omitido: contenido vacío")
            return
        try:
            update_preview(build_config())
        except Exception:
            logger.exception("Error al refrescar preview")

    def make_color_selector(label: str, field: ft.TextField, initial: str) -> ft.Row:
        swatch = ft.Container(
            width=38,
            height=38,
            border_radius=10,
            bgcolor=initial,
            border=ft.Border.all(1, BORDER),
        )
        picker = ColorPicker(
            color=initial,
            enable_alpha=False,
            hex_input_bar=True,
            color_picker_width=320,
            label_types=[ColorLabelType.HEX, ColorLabelType.RGB],
            color_history=[
                "#111827",
                "#FFFFFF",
                "#000000",
                "#2563EB",
                "#16A34A",
                "#DC2626",
            ],
        )
        pending = {"value": _normalize_picker_color(initial, initial)}

        def color_changed(event: ft.ControlEvent) -> None:
            raw = event.data or picker.color or pending["value"]
            pending["value"] = _normalize_picker_color(raw, pending["value"])
            logger.debug("Picker %s cambió | raw=%r normalized=%s", label, raw, pending["value"])

        def apply_color(_: ft.Event[ft.Button]) -> None:
            try:
                selected = _normalize_picker_color(pending["value"], field.value or initial)
                field.value = selected
                swatch.bgcolor = selected
                logger.info("%s aplicado: %s", label, selected)
                page.pop_dialog()
                refresh_preview()
                page.update()
            except Exception:
                logger.exception("No se pudo aplicar %s", label)
                status.value = f"No se pudo aplicar {label.lower()}."
                status.color = ERROR
                page.update()

        def cancel_color(_: ft.Event[ft.TextButton]) -> None:
            logger.info("Selección cancelada: %s", label)
            page.pop_dialog()

        picker.on_color_change = color_changed
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Elegir {label.lower()}"),
            content=picker,
            actions=[
                ft.TextButton(content="Cancelar", on_click=cancel_color),
                ft.Button(content="Aplicar", icon=ft.Icons.CHECK, on_click=apply_color),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def open_picker(_: ft.Event[ft.Button]) -> None:
            current = _normalize_picker_color(field.value, initial)
            pending["value"] = current
            picker.color = current
            logger.info("Abriendo selector %s | actual=%s", label, current)
            page.show_dialog(dialog)

        return ft.Row(
            spacing=7,
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

    fill_selector = make_color_selector("Color del QR", fill_color, "#111827")
    background_selector = make_color_selector("Color de fondo", background_color, "#FFFFFF")

    async def pick_logo(_: ft.Event[ft.Button]) -> None:
        logger.info("Abriendo selector de logo")
        try:
            files = await ft.FilePicker().pick_files(
                dialog_title="Seleccionar logo",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=LOGO_EXTENSIONS,
                allow_multiple=False,
            )
            if not files:
                logger.info("Selección de logo cancelada")
                return
            selected = files[0]
            if not selected.path:
                status.value = "No se obtuvo una ruta local utilizable."
                status.color = ERROR
                logger.error("FilePicker devolvió un archivo sin ruta local")
                page.update()
                return
            logo.value = selected.path
            selected_logo.value = f"Seleccionado: {selected.name}"
            selected_logo.color = SUCCESS
            status.value = "✓ Logo cargado · corrección H automática"
            status.color = SUCCESS
            logger.info("Logo seleccionado: %s", selected.path)
            refresh_preview()
            page.update()
        except Exception:
            logger.exception("Error al seleccionar logo")
            status.value = "No se pudo cargar el logo."
            status.color = ERROR
            page.update()

    def clear_logo(_: ft.Event[ft.IconButton]) -> None:
        logger.info("Logo eliminado")
        logo.value = ""
        selected_logo.value = "Ningún archivo seleccionado"
        selected_logo.color = MUTED
        status.value = "Logo eliminado."
        status.color = MUTED
        refresh_preview()
        page.update()

    logo_picker = ft.Column(
        spacing=3,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Row(
                spacing=6,
                controls=[
                    logo,
                    ft.Button(
                        content="Cargar",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=pick_logo,
                        style=ft.ButtonStyle(
                            color=PRIMARY,
                            bgcolor=PRIMARY_SOFT,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Quitar logo", on_click=clear_logo),
                ],
            ),
            selected_logo,
        ],
    )

    def preview_click(_: ft.Event[ft.Button]) -> None:
        logger.info("Solicitada vista previa")
        try:
            update_preview(build_config())
            status.value = "✓ Vista previa actualizada"
            status.color = ACCENT
        except Exception as exc:
            logger.exception("Error al generar vista previa")
            status.value = f"No se pudo previsualizar: {exc}"
            status.color = ERROR
        page.update()

    def generate_click(_: ft.Event[ft.Button]) -> None:
        logger.info("Solicitada generación PNG")
        try:
            config = build_config()
            update_preview(config)
            saved = save_qr(config)
            status.value = f"✓ Guardado en {saved}"
            status.color = SUCCESS
            if config.logo_path:
                correction.value = "H"
            logger.info("PNG generado correctamente: %s", saved)
        except Exception as exc:
            logger.exception("Error al generar PNG")
            status.value = f"No se pudo generar: {exc}"
            status.color = ERROR
        page.update()

    hero = ft.Container(
        height=70,
        bgcolor=TEXT,
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
                            bgcolor=PRIMARY,
                            content=ft.Icon(ft.Icons.QR_CODE_2, color=ft.Colors.WHITE, size=24),
                        ),
                        ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=1,
                            controls=[
                                ft.Text("QR Studio", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text("Generador profesional de códigos QR", size=11, color="#CBD5E1"),
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
            color=PRIMARY,
            bgcolor=PRIMARY_SOFT,
            padding=ft.Padding.symmetric(horizontal=18, vertical=11),
            shape=ft.RoundedRectangleBorder(radius=11),
        ),
    )
    generate_button = ft.Button(
        content="Generar PNG",
        icon=ft.Icons.DOWNLOAD,
        on_click=generate_click,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=PRIMARY,
            padding=ft.Padding.symmetric(horizontal=20, vertical=11),
            shape=ft.RoundedRectangleBorder(radius=11),
        ),
    )

    fields_two_columns = ft.ResponsiveRow(
        spacing=12,
        run_spacing=10,
        controls=[
            ft.Container(col={"sm": 12, "md": 6}, content=output),
            ft.Container(col={"sm": 12, "md": 6}, content=logo_picker),
            ft.Container(col={"sm": 12, "md": 6}, content=fill_selector),
            ft.Container(col={"sm": 12, "md": 6}, content=background_selector),
        ],
    )

    sliders = ft.ResponsiveRow(
        spacing=12,
        run_spacing=8,
        controls=[
            ft.Container(
                col={"sm": 12, "md": 4},
                content=ft.Column(
                    spacing=0,
                    controls=[ft.Text("Tamaño de módulos", size=11, weight=ft.FontWeight.W_600), box_size],
                ),
            ),
            ft.Container(
                col={"sm": 12, "md": 4},
                content=ft.Column(
                    spacing=0,
                    controls=[ft.Text("Quiet zone / borde", size=11, weight=ft.FontWeight.W_600), border],
                ),
            ),
            ft.Container(
                col={"sm": 12, "md": 4},
                content=ft.Column(
                    spacing=0,
                    controls=[ft.Text("Tamaño del logo", size=11, weight=ft.FontWeight.W_600), logo_scale],
                ),
            ),
        ],
    )

    actions = ft.ResponsiveRow(
        spacing=12,
        run_spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                col={"sm": 12, "md": 7},
                content=ft.Row(controls=[preview_button, generate_button], spacing=10, wrap=True),
            ),
            ft.Container(
                col={"sm": 12, "md": 5},
                alignment=ft.Alignment.CENTER_RIGHT,
                padding=ft.Padding.symmetric(horizontal=12, vertical=9),
                border_radius=10,
                bgcolor=SURFACE_ALT,
                content=status,
            ),
        ],
    )

    form_column = ft.Column(
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            _title("Configuración", "Definí contenido, apariencia y exportación."),
            ft.Divider(height=1, color=BORDER),
            data,
            fields_two_columns,
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=8,
                controls=[
                    ft.Container(col={"sm": 12, "md": 3}, content=correction),
                    ft.Container(
                        col={"sm": 12, "md": 9},
                        padding=ft.Padding.symmetric(horizontal=6),
                        content=sliders,
                    ),
                ],
            ),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                border_radius=11,
                bgcolor="#ECFEFF",
                border=ft.Border.all(1, "#A5F3FC"),
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=ACCENT, size=17),
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
    )

    form_card = ft.Container(
        padding=22,
        border_radius=18,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        content=form_column,
    )

    preview_frame = ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        border_radius=18,
        bgcolor=SURFACE_ALT,
        border=ft.Border.all(1, BORDER),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[preview_hint, preview],
        ),
    )
    preview_card = ft.Container(
        padding=22,
        border_radius=18,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        content=ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=14,
            controls=[
                _title("Vista previa", "Validá el resultado antes de exportarlo."),
                preview_frame,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.VERIFIED_OUTLINED, color=SUCCESS, size=16),
                        ft.Text("Probalo con más de un lector antes de imprimirlo.", size=10, color=MUTED),
                    ],
                ),
            ],
        ),
    )

    form_slot = ft.Container(col={"sm": 12, "lg": 7}, content=form_card)
    preview_slot = ft.Container(col={"sm": 12, "lg": 5}, content=preview_card)
    grid = ft.ResponsiveRow(spacing=16, run_spacing=16, controls=[form_slot, preview_slot])
    workspace_scroller = ft.Column(scroll=ft.ScrollMode.AUTO, controls=[grid])
    workspace = ft.Container(height=700, padding=ft.Padding.all(16), content=workspace_scroller)
    footer = _footer()
    shell = ft.Column(spacing=0, controls=[hero, workspace, footer])

    def adapt(_: ft.PageResizeEvent | None = None) -> None:
        width = float(page.width or 1280)
        height = float(page.height or 800)
        desktop = width >= 1050

        workspace.height = max(500.0, height - hero.height - footer.height)
        workspace.padding = ft.Padding.all(12 if height < 760 else 16)

        if desktop:
            card_height = max(470.0, workspace.height - 32)
            form_slot.height = card_height
            preview_slot.height = card_height
            form_card.height = card_height
            preview_card.height = card_height

            available_width = max(320.0, width * 0.34)
            available_height = max(300.0, card_height - 155)
            preview_size = min(520.0, available_width, available_height)
            preview.width = preview_size
            preview.height = preview_size
        else:
            form_slot.height = None
            preview_slot.height = None
            form_card.height = None
            preview_card.height = None
            preview_size = max(250.0, min(380.0, width * 0.62))
            preview.width = preview_size
            preview.height = preview_size

        page.update()

    page.on_resize = adapt
    page.add(ft.SafeArea(content=shell))
    adapt()
    logger.info("QR Studio listo")
