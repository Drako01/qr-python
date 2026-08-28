# QR Studio v2.0.0 — Professional Edition

QR Studio v2.0.0 convierte el proyecto original en una aplicación Python profesional para generar códigos QR desde una interfaz gráfica, terminal o como librería reutilizable.

## Highlights

- UI moderna y responsive con Flet.
- Core desacoplado y testeable.
- Logo opcional centrado.
- Protección de legibilidad mediante corrección H automática.
- Colores, quiet zone, tamaño y corrección configurables.
- PNG generado en memoria para preview.
- CLI completa para automatización.
- Payload helpers para URL, email, teléfono y Wi-Fi.
- CI multi-versión.
- Documentación técnica y de uso.

## Logo seguro

Al agregar un logo, QR Studio:

1. valida el archivo;
2. conserva la relación de aspecto;
3. limita su escala;
4. agrega una placa de fondo;
5. lo centra;
6. fuerza corrección de errores H.

Esto reduce el riesgo de que una personalización visual vuelva ilegible el QR.

## Ingeniería

La nueva arquitectura separa:

- `qr_studio.app`: UI;
- `qr_studio.models`: configuración e invariantes;
- `qr_studio.generator`: generación y exportación;
- `qr_studio.cli`: terminal;
- `qr_studio.payloads`: payloads interoperables.

## Compatibilidad

Requiere Python 3.11 o superior.

Dependencias de referencia de la release:

- Flet 0.86.5
- qrcode 8.2
- Pillow 12.3.0

## Migración desde v1

El antiguo `QR_gen.py` se reemplaza por `main.py` y el paquete `qr_studio`.

Antes:

```bash
python QR_gen.py
```

Ahora:

```bash
python main.py
```

O por terminal:

```bash
python -m qr_studio.cli "https://example.com"
```

## Autor

Alejandro Daniel Di Stefano — [@Drako01](https://github.com/Drako01)
