# Changelog

Todos los cambios relevantes de QR Studio se documentan en este archivo.

## [2.0.0] - 2026-08-28

### Added

- Arquitectura modular `qr_studio/`.
- Interfaz profesional con Flet.
- Vista previa en memoria.
- Exportación PNG configurable.
- Soporte opcional de logo centrado.
- Corrección H automática cuando existe logo.
- Control de escala del logo.
- CLI para automatización.
- Builders para URL, email, teléfono y Wi-Fi.
- Configuración tipada mediante `QRConfig`.
- Validaciones de entrada y parámetros.
- Tests con pytest.
- Ruff.
- CI para Python 3.11, 3.12 y 3.13.
- Documentación de arquitectura.
- Release notes.

### Changed

- El QR ya no fija `version=1`; ahora ajusta automáticamente su capacidad al contenido.
- El código de generación quedó desacoplado de la interfaz.
- La preview ya no necesita escribir `codigo_qr.png`.
- Dependencias documentadas y fijadas explícitamente.
- README completamente reescrito.
- Licencia normalizada a `LICENSE`.

### Removed

- Script monolítico legacy `QR_gen.py`.

## [1.0.0] - 2024-02-08

- Implementación inicial basada en Flet y `qrcode`.
- Generación básica de un archivo `codigo_qr.png`.
