import pytest

from qr_studio.payloads import email_payload, phone_payload, url_payload, wifi_payload


def test_url_payload_adds_https() -> None:
    assert url_payload("example.com") == "https://example.com"


def test_email_payload_encodes_subject() -> None:
    value = email_payload("test@example.com", subject="Hola mundo")
    assert value == "mailto:test@example.com?subject=Hola%20mundo"


def test_phone_payload() -> None:
    assert phone_payload("+54 11 1234 5678") == "tel:+541112345678"


def test_wifi_payload() -> None:
    assert wifi_payload("MiWifi", "clave", "WPA") == "WIFI:T:WPA;S:MiWifi;P:clave;H:false;;"


def test_wifi_requires_ssid() -> None:
    with pytest.raises(ValueError, match="SSID"):
        wifi_payload("")
