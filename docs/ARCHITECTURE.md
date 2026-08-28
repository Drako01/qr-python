# Arquitectura de QR Studio

QR Studio v2 separa deliberadamente interfaz, dominio y persistencia de archivos para que el proyecto pueda evolucionar sin volver a un script monolítico.

## Capas

```text
main.py
  │
  └── qr_studio.app           # UI Flet
         │
         ├── qr_studio.models     # Configuración tipada y validaciones
         └── qr_studio.generator  # Generación, logo, PNG y bytes

qr_studio.cli                 # Interfaz alternativa de terminal
qr_studio.payloads            # Builders para URL, email, teléfono y Wi-Fi
```

## `models.py`

`QRConfig` concentra los parámetros de generación y sus invariantes:

- contenido no vacío;
- salida PNG;
- quiet zone mínima de 4 módulos;
- límites razonables de `box_size`;
- niveles L/M/Q/H;
- formato y existencia del logo;
- escala máxima del logo.

Cuando existe logo, `effective_error_correction` devuelve `H` independientemente del nivel solicitado. Esto sigue la recomendación del paquete `qrcode` para imágenes embebidas.

## `generator.py`

Es una capa libre de Flet. Puede utilizarse desde:

- la aplicación de escritorio;
- la CLI;
- tests;
- futuros servicios HTTP;
- scripts de automatización.

`generate_qr()` devuelve una imagen Pillow en memoria. `save_qr()` persiste el PNG y crea directorios padre. `qr_to_png_bytes()` expone bytes PNG para previews o integraciones.

### Logo

El logo:

1. se abre como RGBA;
2. se escala manteniendo proporción;
3. se limita a un porcentaje del lado menor del QR;
4. recibe una placa redondeada con el color de fondo;
5. se compone exactamente en el centro.

El objetivo no es decorar a cualquier costo: se preserva primero la capacidad de lectura.

## `payloads.py`

Contiene builders reutilizables para producir payloads QR interoperables:

- URL;
- email (`mailto:`);
- teléfono (`tel:`);
- Wi-Fi (`WIFI:`).

La UI actual permite contenido libre; estos builders quedan disponibles para CLI, integraciones y futuras pantallas especializadas.

## Dependencias

- **Flet**: interfaz multiplataforma.
- **qrcode**: matriz QR y codificación.
- **Pillow**: composición, resize, transparencia y exportación PNG.

## Calidad

GitHub Actions ejecuta la matriz Python 3.11/3.12/3.13 con:

1. instalación reproducible de dependencias;
2. Ruff;
3. `compileall`;
4. pytest.

## Extensiones recomendadas

La arquitectura permite agregar sin reescribir el core:

- SVG;
- vCard/MECARD;
- QR Wi-Fi guiado desde UI;
- presets de marca;
- batch generation;
- lectura/validación automática con decoder;
- empaquetado nativo con `flet build`;
- historial local de proyectos.
