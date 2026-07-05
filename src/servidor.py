import socket, os, json, threading
from dotenv import load_dotenv
from protocolos.validacionMensaje import validarMensaje
from protocolos.framing import enviar_json, recibir_json
from sensores import procesar_datos_sensor
from datetime import datetime
from pathlib import Path

if not load_dotenv('.env'):
    print("Cargando variables de entorno por defecto (.env.example).")
    load_dotenv('.env.example')

#direccion del servidor en una IP
HOST = os.getenv('SERVER_BIND_IP')
PUERTO = int(os.getenv('SERVER_BIND_PORT'))
secret_key = os.getenv('SECRET_KEY')

# Carpeta donde se guarda la evidencia de lo recibido y procesado
DIR_LOGS = Path(__file__).resolve().parent.parent / "registros"
DIR_LOGS.mkdir(exist_ok=True)
ARCHIVO_LOG = DIR_LOGS / "registro_invernadero.log"

# Dos hilos podrían intentar escribir al log al mismo tiempo; el Lock evita
# que las líneas se entremezclen o se corte una escritura a la mitad.
_lock_log = threading.Lock()

def serverLoop() -> None:
    """
    bloque with para manejar el socket
    el argumento socket.AF_INET indica que se usará IPv4
    AF_INET: Protocolo de Internet versión 4 (IPv4)
    el argumento socket.SOCK_STREAM indica que se usará TCP 
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Permite volver a levantar el servidor rápido sin que el SO se
        # queje de que el puerto "sigue en uso" (estado TIME_WAIT).
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PUERTO)) # enlaza el socket a la dirección y puerto especificados
        s.listen() # pone el socket en modo escucha para aceptar conexiones entrantes
        print(f"Servidor TCP escuchando en {HOST}:{PUERTO}")
        # s.accept() acepta una conexión entrante y devuelve un nuevo socket y la dirección del cliente
        conn, addr = s.accept()
        """
        with conn: # bloque with para manejar la conexión
            print(f"Conexión establecida con {addr}") # imprime la dirección del cliente que se conectó
            while True: # bucle infinito para recibir datos del cliente
                data=conn.recv(1024) # recibe el mensaje del cliente y lo desbloquea
                if not data:
                    break # si no hay datos, rompe el bucle y cierra la conexión

                data = json.loads((data.decode('utf-8'))) # decodificar msj del cliente
                testValidez(data, conn)
                """
        try:
            while True:
                # s.accept() se bloquea hasta que llega una conexión nueva.
                # Como cada conexión se atiende en su propio hilo, el
                # servidor puede seguir aceptando nodos nuevos mientras
                # atiende a los que ya estaban conectados.
                conn, addr = s.accept()
                hilo = threading.Thread(
                    target=manejar_cliente, args=(conn, addr), daemon=True
                )
                hilo.start()
        except KeyboardInterrupt:
            print("\nServidor detenido manualmente (Ctrl+C).")

def registrar(linea: str) -> None:
    """Imprime en consola y además deja constancia en el archivo de log."""
    marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea_completa = f"[{marca_tiempo}] {linea}"
    print(linea_completa)
    with _lock_log:
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
            f.write(linea_completa + "\n")

def procesar_mensaje(mensaje: dict, addr) -> dict:
    """
    Valida la firma de `mensaje` y, si corresponde, aplica las reglas de
    negocio sobre la lectura de sensores que trae adentro.

    `mensaje` corresponde al "sobre" generado por firmarMensajeJSON():
        {"data": "<json de la lectura, como texto>", "digest": "<hmac hex>"}
    """
    data_str = mensaje.get("data")
    digest = mensaje.get("digest")

    # Mensaje anómalo: no trae las claves que esperábamos.
    if data_str is None or digest is None:
        registrar(f"Mensaje con formato inesperado desde {addr}: {mensaje}")
        return {"valido": False, "motivo": "formato_inesperado"}

    es_valido = validarMensaje(data=data_str, hexdigest=digest, secret_key=SECRET_KEY)

    if not es_valido:
        registrar(f"Firma inválida en mensaje recibido desde {addr} -> se descarta")
        return {"valido": False, "motivo": "firma_invalida"}

    # A partir de acá confiamos en el contenido, porque la firma coincide.
    try:
        lectura = json.loads(data_str)
        alertas, acciones = procesar_datos_sensor(lectura)
    except (json.JSONDecodeError, KeyError) as e:
        # La firma era válida pero el contenido no tiene la forma esperada.
        registrar(f"Error al procesar datos desde {addr}: {e}")
        return {"valido": False, "motivo": "datos_invalidos"}

    nodo_id = lectura.get("nodo_id", "desconocido")
    registrar(
        f"Lectura válida de '{nodo_id}' desde {addr} -> {lectura['sensores']} "
        f"| Alertas: {alertas if alertas else 'ninguna'}"
    )

    return {
        "valido": True,
        "nodo_id": nodo_id,
        "alertas": alertas,
        "acciones": acciones,
    }


def manejar_cliente(conn: socket.socket, addr) -> None:
    # Esta función corre en un hilo por cada conexión aceptada
    registrar(f"Conexión establecida con {addr}")
    buffer = b""

    with conn:
        while True:
            mensaje, buffer = recibir_json(conn, buffer)

            if "error" in mensaje:
                if mensaje["error"] == "conexion_cerrada":
                    registrar(f"Conexión cerrada por {addr}")
                    break
                # JSON corrupto / mensaje anómalo: se avisa y se sigue
                # escuchando (no se cae el hilo por un mensaje raro).
                registrar(f"Mensaje malformado recibido desde {addr}: {mensaje['error']}")
                enviar_json(conn, {"valido": False, "motivo": mensaje["error"]})
                continue

            respuesta = procesar_mensaje(mensaje, addr)

            try:
                enviar_json(conn, respuesta)
            except (BrokenPipeError, ConnectionResetError):
                registrar(f"No se pudo responder a {addr} (conexión ya cerrada)")
                break

"""
def testValidez(msg: json, conn):
    esValido: bool = validarMensaje(data=msg['data'], hexdigest=msg['digest'], secret_key=secret_key)
    print(f'Mensaje recibido: {msg}')
    if (esValido):
        t = 'Mensaje válido'
        conn.sendall(t.encode('utf-8'))
    else:
        t = 'Mensaje inválido'
        conn.sendall(t.encode('utf-8'))
"""

if __name__ == "__main__":
    serverLoop()