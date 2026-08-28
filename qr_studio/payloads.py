from __future__ import annotations

import re
from urllib.parse import quote


_WIFI_ESCAPE = re.compile(r"([\\;,:"])")


def text_payload(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("El texto no puede estar vacío.")
    return value


def url_payload(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("La URL no puede estar vacía.")
    if not value.lower().startswith(("http://", "https://")):
        value = f"https://{value}"
    return value


def email_payload(email: str, subject: str = "", body: str = "") -> str:
    email = email.strip()
    if not email or "@" not in email:
        raise ValueError("Ingrese un email válido.")
    query = []
    if subject.strip():
        query.append(f"subject={quote(subject.strip())}")
    if body.strip():
        query.append(f"body={quote(body.strip())}")
    suffix = f"?{'&'.join(query)}" if query else ""
    return f"mailto:{email}{suffix}"


def phone_payload(number: str) -> str:
    number = number.strip().replace(" ", "")
    if not number:
        raise ValueError("El teléfono no puede estar vacío.")
    return f"tel:{number}"


def wifi_payload(ssid: str, password: str = "", security: str = "WPA", hidden: bool = False) -> str:
    ssid = ssid.strip()
    if not ssid:
        raise ValueError("El SSID no puede estar vacío.")
    security = security.upper()
    if security not in {"WPA", "WEP", "NOPASS"}:
        raise ValueError("Seguridad Wi-Fi inválida.")

    def esc(value: str) -> str:
        return _WIFI_ESCAPE.sub(r"\\\1", value)

    password_part = "" if security == "NOPASS" else f"P:{esc(password)};"
    return f"WIFI:T:{security};S:{esc(ssid)};{password_part}H:{str(hidden).lower()};;"
