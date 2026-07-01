import socket

HOST = '192.168.1.14' #ojo, debe ser la ip del servidor, no la del cliente
PUERTO = 65123 # puerto de envío

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PUERTO)) # una vez establecida la conexión, se puede enviar y recibir datos

    s.sendall(b'Hola, servidor!') # envía un mensaje al servidor en binario (por eso la b)

    data=s.recv(1024) # recibe la respuesta del servidor (eco)

print("Recibido", repr(data)) # imprime la respuesta del servidor en formato legible

