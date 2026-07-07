"""
Verifica que un mensaje con HMAC inválido es rechazado por validarMensaje().
Cubre los escenarios de ataque más comunes:
  - firma con una llave distinta (atacante sin la llave compartida)
  - digest corrupto (truncado, alterado)
  - payload modificado después de firmado (man-in-the-middle)
"""
import json

from rc_simulacion.protocolos.validacionMensaje import firmarMensajeJSON, validarMensaje


SECRET = "test_secret_key"


def test_firma_con_llave_incorrecta_rechazada():
    """Firmar con una llave y validar con otra debe fallar."""
    payload = {"sensor": "temperatura", "valor": 23.4}
    payload_json = json.dumps(payload)

    sobre = firmarMensajeJSON(payload_json, "llave_atacante")
    es_valido = validarMensaje(
        data=sobre["data"], hexdigest=sobre["digest"], secret_key=SECRET
    )
    assert es_valido is False, "Firma con llave incorrecta no fue rechazada"


def test_digest_corrupto_rechazado():
    """Reemplazar el digest por uno falso debe hacer fallar la validación."""
    payload = {"sensor": "temperatura", "valor": 23.4}
    sobre = firmarMensajeJSON(json.dumps(payload), SECRET)

    digest_falso = "0" * 64
    es_valido = validarMensaje(
        data=sobre["data"], hexdigest=digest_falso, secret_key=SECRET
    )
    assert es_valido is False, "Digest corrupto no fue rechazado"


def test_payload_tampered_rechazado():
    """Modificar el payload dejando el digest original debe fallar."""
    payload_original = {"sensor": "temperatura", "valor": 23.4}
    sobre = firmarMensajeJSON(json.dumps(payload_original), SECRET)

    payload_tampered = json.dumps({"sensor": "temperatura", "valor": 999.9})
    es_valido = validarMensaje(
        data=payload_tampered, hexdigest=sobre["digest"], secret_key=SECRET
    )
    assert es_valido is False, "Payload modificado no fue rechazado"


def test_digest_truncado_rechazado():
    """Un digest más corto (longitud incorrecta) no debe coincidir con ninguno real."""
    payload = {"x": 1}
    sobre = firmarMensajeJSON(json.dumps(payload), SECRET)

    digest_truncado = sobre["digest"][:32]
    es_valido = validarMensaje(
        data=sobre["data"], hexdigest=digest_truncado, secret_key=SECRET
    )
    assert es_valido is False, "Digest truncado no fue rechazado"
