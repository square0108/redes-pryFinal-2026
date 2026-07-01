import socket, os, time
from dotenv import load_dotenv

if not load_dotenv('.env'):
    print("Cargando variables de entorno por defecto (.env.example).")
    load_dotenv('.env.example')

# Cargar IP y puerto desde archivo de variables de entorno '.env.example', para mayor configurabilidad.
HOST = os.getenv('CLIENT_TARGET_IP') # ojo, debe ser la ip del servidor, no la del cliente
PUERTO = int(os.getenv('CLIENT_TARGET_PORT')) # puerto de envío

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Reintentar conexión continuamente
        while True:
            try:
                s.connect((HOST, PUERTO))
                print(f"Conexión exitosa a {HOST}:{PUERTO}")
                break # Exit the loop once connected
            except ConnectionRefusedError:
                print(f"Conexión fallida a {HOST}:{PUERTO}")
                time.sleep(2)

        s.sendall(b'Hola, servidor!') # envía un mensaje al servidor en binario (por eso la b)

        data=s.recv(1024) # recibe la respuesta del servidor (eco)

    print("Recibido", repr(data)) # imprime la respuesta del servidor en formato legible

