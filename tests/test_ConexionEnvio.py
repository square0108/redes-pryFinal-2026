import pytest
import socket
import threading

# utilizando src como pythonpath
from rc_simulacion import clientes
from rc_simulacion.protocolos.framing import enviar_json, recibir_json

"""
Este test inicia un servidor dummy mediante una llamada a `dummy_server()`, crea un cliente socket de prueba, y envía un mensaje al servidor.
El envío y recepción de mensajes utilizan `enviar_json()` y `recibir_json()`.
El test aprueba sólo si el cliente recibe el eco y verifica los contenidos como los mismos que envió.
"""
@pytest.fixture
def dummy_server(monkeypatch):
    """
    Crea un socket dummy que usa sus propias variables de entorno
    """
    sv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sv_socket.bind(('127.0.0.1', 0)) # puerto 0 hace que S.O. le asigne un puerto efímero al servidor
    sv_socket.listen(1)
    host, port = sv_socket.getsockname()
    print(f"[{host}:{port}] Dummy server activo!")

    # Sobreescribe las variables en clients.py de forma no permanente
    monkeypatch.setattr(clientes, "HOST", host)
    monkeypatch.setattr(clientes, "PUERTO", port)

    yield sv_socket
    sv_socket.close()

def dummy_server_eco(sv_socket: socket.socket):
    """Acepta una conexión, recibe JSON, y hace eco del mensaje."""
    try:
        conn, addr = sv_socket.accept()
        host, port = sv_socket.getsockname()
        print(f"[{host}:{port}] Conexión recibida desde {addr}")
        with conn:
            buffer = b""
            mensaje, buffer = recibir_json(conn, buffer)
            
            print(f"[{host}:{port}] Mensaje JSON recibido: \'{mensaje}\'. Realizando eco a {addr}...")
            if mensaje:
                enviar_json(conn, mensaje) # eco
    except OSError:
        pass

def test_conexion_y_envio_basico(dummy_server):
    sv_socket = dummy_server

    # Correr servidor en hebra separada
    server_thread = threading.Thread(
        target=dummy_server_eco, 
        args=(sv_socket,), 
        daemon=True
    )
    server_thread.start()

    # Reintentar conexión en bucle
    client_sock = clientes.conectar_con_reintentos("test-node")
    assert client_sock is not None # verificar que se retornó el socket cliente

    # Enviar mensaje y esperar respuesta
    test_payload = {"data": "test", "digest": "dummy_hash"}
    enviar_json(client_sock, test_payload)
    buffer = b""
    client_sock.settimeout(5.0) 
    respuesta, buffer = recibir_json(client_sock, buffer)

    # Verificar que el servidor reenvió el mensaje del cliente
    assert respuesta.get("data") == "test"
    assert respuesta.get("digest") == "dummy_hash"

    client_sock.close()
    server_thread.join(timeout=1.0)