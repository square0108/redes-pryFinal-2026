"""
Verifica que un mensaje firmado con el HMAC correcto es aceptado por
validarMensaje() — caso normal del handshake, sin manipulación.
"""
import json

from rc_simulacion.protocolos.validacionMensaje import firmarMensajeJSON, validarMensaje


SECRET = "test_secret_key"


def test_firma_y_validacion_redonda():
    """Firmar un mensaje y verificarlo con la misma llave debe dar True."""
    payload = {"sensor": "temperatura", "valor": 23.4}
    payload_json = json.dumps(payload)

    sobre = firmarMensajeJSON(payload_json, SECRET)
    assert sobre is not None, "firmarMensajeJSON no debería retornar None"
    assert "data" in sobre
    assert "digest" in sobre

    es_valido = validarMensaje(
        data=sobre["data"], hexdigest=sobre["digest"], secret_key=SECRET
    )
    assert es_valido is True, "Una firma válida fue rechazada"


def test_firma_valida_para_varios_payloads():
    """Distintos payloads firmados con la misma llave deben validar OK."""
    casos = [
        {"sensor": "temperatura", "valor": 0},
        {"sensor": "humedad", "valor": 100, "timestamp": 1234567890},
        {"nodo_id": "inv-1", "sensores": {"temp": 22.5, "hum": 60.0}},
        "",
    ]
    for caso in casos:
        caso_json = json.dumps(caso)
        sobre = firmarMensajeJSON(caso_json, SECRET)
        assert validarMensaje(
            data=sobre["data"], hexdigest=sobre["digest"], secret_key=SECRET
        ) is True, f"Firma rechazada para payload {caso!r}"


def test_digest_es_sha256_hex_de_64_caracteres():
    """El digest producido debe ser SHA-256 en hex (64 chars)."""
    sobre = firmarMensajeJSON('{"x": 1}', SECRET)
    assert len(sobre["digest"]) == 64
    assert all(c in "0123456789abcdef" for c in sobre["digest"])
