# Contribuir a QR Studio

Gracias por colaborar.

## Flujo recomendado

1. Crear una rama desde `main`.
2. Mantener la lógica de generación desacoplada de Flet.
3. Agregar o actualizar tests para cualquier cambio funcional.
4. Ejecutar antes de abrir un PR:

```bash
pip install -r requirements-dev.txt
ruff check .
python -m compileall -q qr_studio main.py
pytest -q
```

## Convenciones

- Python 3.11+.
- Type hints en APIs públicas y lógica de dominio.
- Funciones pequeñas y de responsabilidad única.
- No introducir I/O de UI dentro de `generator.py`.
- Mantener el quiet zone mínimo de 4 módulos.
- Cualquier cambio relacionado con logos debe priorizar legibilidad sobre estética.
- Preferir Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).

## Pull requests

Describí:

- problema que resuelve;
- comportamiento anterior/nuevo;
- tests ejecutados;
- impacto sobre QR existentes;
- capturas si cambia la UI.

## Seguridad y privacidad

QR Studio procesa los datos localmente. No agregues telemetría, uploads o llamadas externas sin documentarlo de forma explícita y justificarlo en el PR.
