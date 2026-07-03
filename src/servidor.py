import socket
import os
import json
from dotenv import load_dotenv
from protocolos.validacionMensaje import validarMensaje

if not load_dotenv('.env'):
    print("Cargando variables de entorno por defecto (.env.example).")
    load_dotenv('.env.example')

#direccion del servidor en una IP
HOST = os.getenv('SERVER_BIND_IP')
PUERTO = int(os.getenv('SERVER_BIND_PORT'))
secret_key = os.getenv('SECRET_KEY')

def serverLoop():
    """
    bloque with para manejar el socket
    el argumento socket.AF_INET indica que se usará IPv4
    AF_INET: Protocolo de Internet versión 4 (IPv4)
    el argumento socket.SOCK_STREAM indica que se usará TCP 
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PUERTO)) # enlaza el socket a la dirección y puerto especificados
        s.listen() # pone el socket en modo escucha para aceptar conexiones entrantes
        print(f"Servidor TCP escuchando en {HOST}:{PUERTO}")
        # s.accept() acepta una conexión entrante y devuelve un nuevo socket y la dirección del cliente
        conn, addr = s.accept()

        with conn: # bloque with para manejar la conexión
            print(f"Conexión establecida con {addr}") # imprime la dirección del cliente que se conectó
            while True: # bucle infinito para recibir datos del cliente
                data=conn.recv(1024) # recibe el mensaje del cliente y lo desbloquea
                if not data:
                    break # si no hay datos, rompe el bucle y cierra la conexión

                data = json.loads((data.decode('utf-8'))) # decodificar msj del cliente
                testValidez(data, conn)

def testValidez(msg: json, conn):
    esValido: bool = validarMensaje(data=msg['data'], hexdigest=msg['digest'], secret_key=secret_key)
    print(f'Mensaje recibido: {msg}')
    if (esValido):
        t = 'Mensaje válido'
        conn.sendall(t.encode('utf-8'))
    else:
        t = 'Mensaje inválido'
        conn.sendall(t.encode('utf-8'))


if __name__ == "__main__":
    serverLoop()