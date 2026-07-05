import json
import socket
import struct

HEADER_FMT = "!I"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
MAX_PAYLOAD = 1 * 1024 * 1024


def enviar_json(sock: socket.socket, obj: dict) -> None:
    """Serializa `obj` a JSON UTF-8 y lo envía por `sock` con framing de
    longitud prefija: 4 bytes big-endian con el tamaño del payload,
    seguidos del payload en sí.
    """
    payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    sock.sendall(struct.pack(HEADER_FMT, len(payload)) + payload)


def recibir_json(sock: socket.socket, buffer: bytes) -> tuple[dict | None, bytes]:
    """Lee del socket hasta armar un mensaje con framing de longitud
    prefija, lo decodifica como JSON y lo retorna junto con el buffer
    restante (que puede contener el inicio del próximo mensaje).

    Retorna:
      - (dict, buffer)   mensaje completo. Si la conexión se cerró o el
                         payload estaba corrupto, el dict trae una clave
                         "error" describiendo el motivo.
      - (None, buffer)   aún no hay suficientes bytes; el llamador debe
                         invocar de nuevo cuando haya nuevos datos.
    """
    if len(buffer) < HEADER_SIZE:
        chunk = sock.recv(HEADER_SIZE - len(buffer))
        if not chunk:
            return {"error": "conexion_cerrada"}, buffer
        buffer += chunk
        if len(buffer) < HEADER_SIZE:
            return None, buffer

    longitud = struct.unpack(HEADER_FMT, buffer[:HEADER_SIZE])[0]
    buffer = buffer[HEADER_SIZE:]

    if longitud > MAX_PAYLOAD:
        return {"error": f"payload_demasiado_grande: {longitud}"}, buffer

    while len(buffer) < longitud:
        chunk = sock.recv(longitud - len(buffer))
        if not chunk:
            return {"error": "conexion_cerrada"}, buffer
        buffer += chunk

    payload, buffer = buffer[:longitud], buffer[longitud:]

    try:
        mensaje = json.loads(payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return {"error": f"json_invalido: {e}"}, buffer

    return mensaje, buffer
