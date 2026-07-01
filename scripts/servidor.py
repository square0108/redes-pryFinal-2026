import socket
import os
from dotenv import load_dotenv

if not load_dotenv('.env'):
    print("Cargando variables de entorno por defecto (.env.example).")
    load_dotenv('.env.example')

#direccion del servidor en una IP
HOST = os.getenv('SERVER_BIND_IP')
PUERTO = int(os.getenv('SERVER_BIND_PORT'))

#bloque with para manejar el socket
# el argumento socket.AF_INET indica que se usará IPv4
# AF_INET: Protocolo de Internet versión 4 (IPv4)
# el argumento socket.SOCK_STREAM indica que se usará TCP
if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PUERTO)) # enlaza el socket a la dirección y puerto especificados
        s.listen() # pone el socket en modo escucha para aceptar conexiones entrantes
        print(f"Servidor TCP escuchando en {HOST}:{PUERTO}")
        # s.accept() acepta una conexión entrante y devuelve un nuevo socket y la dirección del cliente
        conn, addr = s.accept()
        # con es el socket, addr un string con la dirección del cliente

        with conn: # bloque with para manejar la conexión
            print(f"Conexión establecida con {addr}") # imprime la dirección del cliente que se conectó
            while True: # bucle infinito para recibir datos del cliente
                data=conn.recv(1024) # recibe el mensaje del cliente y lo desbloquea (
                if not data:
                    break # si no hay datos, rompe el bucle y cierra la conexión

                conn.sendall(data) # envía de vuelta los datos recibidos al cliente (eco)
