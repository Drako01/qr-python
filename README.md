# QR Studio — Professional QR Generator

<p align="center">
  <strong>Generador profesional de códigos QR con Python, Flet y Pillow.</strong><br>
  Interfaz de escritorio, CLI, personalización visual y logo opcional con protección de legibilidad.
</p>

<p align="center">
  <strong>Autor:</strong> <a href="https://github.com/Drako01">Alejandro Daniel Di Stefano</a>
</p>

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Flet](https://img.shields.io/badge/Flet-0.86.5-6C63FF)
![qrcode](https://img.shields.io/badge/qrcode-8.2-black)
![Pillow](https://img.shields.io/badge/Pillow-12.3.0-orange)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/badge/release-v2.0.0-blueviolet)

## Qué es QR Studio

QR Studio transforma el antiguo script de demostración del repositorio en una aplicación modular y reutilizable para generar códigos QR desde una interfaz gráfica o desde terminal.

La prioridad del proyecto es producir códigos QR **claros, configurables y exportables**, sin sacrificar capacidad de lectura por estética.

## Funcionalidades

- interfaz de escritorio construida con Flet;
- diseño responsive para distintos tamaños de ventana;
- generación automática del tamaño/version QR según el contenido;
- exportación PNG optimizada;
- vista previa antes de guardar;
- color del QR configurable;
- color de fondo configurable;
- tamaño de módulo configurable;
- quiet zone configurable con mínimo seguro de 4 módulos;
- corrección de errores L/M/Q/H;
- **logo opcional centrado**;
- resize proporcional del logo;
- soporte PNG, JPG, JPEG y WEBP para logos;
- transparencia de logo;
- placa de protección detrás del logo;
- escala de logo limitada al 25%;
- corrección H automática cuando hay logo;
- CLI para automatización y scripting;
- builders reutilizables para URL, email, teléfono y Wi-Fi;
- validación de parámetros;
- suite de tests;
- Ruff;
- CI en Python 3.11, 3.12 y 3.13;
- documentación de arquitectura;
- changelog y release notes.

## Por qué el logo fuerza corrección H

Un logo tapa parte de los módulos del QR. `qrcode` 8.x establece corrección de errores alta para códigos con imágenes embebidas. QR Studio aplica esa regla automáticamente: aunque se seleccione L, M o Q, al incluir un logo el nivel efectivo pasa a **H**.

Además, el logo queda limitado a un máximo del 25% del lado menor del código. Aun así, cualquier QR destinado a impresión o producción debe probarse con varios lectores y dispositivos.

## Arquitectura

```text
qr-python/
├── main.py
├── qr_studio/
│   ├── __init__.py
│   ├── app.py
│   ├── cli.py
│   ├── generator.py
│   ├── models.py
│   └── payloads.py
├── tests/
│   ├── test_generator.py
│   └── test_payloads.py
├── docs/
│   └── ARCHITECTURE.md
├── .github/workflows/ci.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── CHANGELOG.md
├── RELEASE_NOTES_v2.0.0.md
└── LICENSE
```

La generación no depende de Flet: `qr_studio.generator` puede reutilizarse desde cualquier aplicación Python.

Más detalle: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Requisitos

- Python 3.11 o superior;
- pip;
- Windows, Linux o macOS para la aplicación de escritorio.

## Instalación

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux / macOS

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecutar la aplicación

```bash
python main.py
```

También puede utilizarse el runner de Flet:

```bash
flet run main.py
```

## Generar un QR básico

1. Escribí el texto, URL o payload.
2. Elegí el archivo de salida.
3. Ajustá colores y parámetros si lo necesitás.
4. Presioná **Vista previa**.
5. Presioná **Generar PNG**.

El archivo se crea únicamente en la ruta indicada por el usuario.

## Agregar un logo

En **Logo opcional**, ingresá la ruta de una imagen local:

```text
assets/mi-logo.png
```

Formatos permitidos:

```text
.png
.jpg
.jpeg
.webp
```

QR Studio centra el logo, conserva su relación de aspecto, crea una placa visual para separarlo de los módulos y fuerza corrección H.

## CLI

La misma lógica puede usarse sin interfaz gráfica.

### QR simple

```bash
python -m qr_studio.cli "https://armotusitio.com.ar" -o output/armotusitio.png
```

### QR con logo

```bash
python -m qr_studio.cli "https://armotusitio.com.ar" \
  --logo assets/logo.png \
  --output output/armotusitio-logo.png
```

### Personalización

```bash
python -m qr_studio.cli "Mi contenido" \
  --fill "#0F172A" \
  --background "#FFFFFF" \
  --box-size 14 \
  --border 4 \
  --error-correction Q
```

Opciones principales:

```text
-o, --output
--logo
--fill
--background
--box-size
--border
--error-correction {L,M,Q,H}
--logo-scale
```

Para ver todas:

```bash
python -m qr_studio.cli --help
```

## Uso como librería

```python
from pathlib import Path

from qr_studio.generator import save_qr
from qr_studio.models import QRConfig

config = QRConfig(
    data="https://example.com",
    output=Path("output/example.png"),
    fill_color="#111827",
    background_color="#FFFFFF",
)

save_qr(config)
```

Con logo:

```python
config = QRConfig(
    data="https://example.com",
    output=Path("output/branded.png"),
    logo_path=Path("assets/logo.png"),
    logo_scale=0.18,
)

save_qr(config)
```

## Payloads especializados

El paquete incorpora helpers para construir payloads compatibles:

```python
from qr_studio.payloads import email_payload, phone_payload, url_payload, wifi_payload

url_payload("example.com")
phone_payload("+54 11 1234 5678")
email_payload("hola@example.com", subject="Consulta")
wifi_payload("MiWifi", "mi-clave", security="WPA")
```

## Calidad y tests

Instalación de desarrollo:

```bash
pip install -r requirements-dev.txt
```

Ejecutar tests:

```bash
pytest -q
```

Lint:

```bash
ruff check .
```

Compilación sintáctica:

```bash
python -m compileall -q qr_studio main.py
```

GitHub Actions ejecuta estas verificaciones en Python 3.11, 3.12 y 3.13 para cada PR hacia `main`.

## Decisiones de diseño

### QR con versión automática

No se fija `version=1`. El motor calcula la versión necesaria según el payload y la corrección elegida. Esto evita fallos cuando el contenido supera la capacidad de una versión pequeña.

### Quiet zone mínima

QR Studio no permite un borde inferior a cuatro módulos. Esa zona libre alrededor del QR es fundamental para que un lector identifique correctamente el símbolo.

### Sin archivos temporales para preview

La vista previa se genera en memoria y se entrega a Flet como PNG Base64. Sólo **Generar PNG** escribe el archivo final.

### Core desacoplado de la UI

`generator.py` no importa Flet. La interfaz, CLI y futuras APIs pueden compartir exactamente la misma implementación.

## Limitaciones

La legibilidad final depende de factores externos:

- tamaño físico de impresión;
- calidad de impresión;
- contraste;
- cantidad de datos;
- tamaño del logo;
- material/superficie;
- cámara y software lector.

Generar sin error no garantiza que un diseño extremo sea legible en cualquier contexto. Para producción, validar siempre el PNG final con varios dispositivos.

## Roadmap posible

- exportación SVG;
- vCard/MECARD desde UI;
- formulario Wi-Fi guiado;
- presets de branding;
- historial local;
- generación batch;
- verificación automática con decoder;
- empaquetado instalable para Windows/macOS/Linux;
- drag & drop para logos.

## Contribuciones

Issues y pull requests son bienvenidos. Antes de proponer cambios estructurales, conviene ejecutar Ruff y la suite completa.

## Licencia

MIT. Ver [LICENSE](LICENSE).

---

Desarrollado y mantenido por **[Alejandro Daniel Di Stefano](https://github.com/Drako01)**.
