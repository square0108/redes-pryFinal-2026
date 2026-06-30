# Código de ejemplo desde https://docs.python.org/3/howto/sockets.html
import socket
import os
from dotenv import load_dotenv

if not load_dotenv('.env'):
    print("Cargando variables de entorno por defecto (.env.example).")
    load_dotenv('.env.example')

# Obtenidos desde entorno del docker-compose.yml
BIND_IP = os.getenv('SERVER_BIND_IP')
BIND_PORT = int(os.getenv('SERVER_BIND_PORT'))

# create an INET, STREAMing socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serverSocket.bind((BIND_IP, BIND_PORT))
# become a server socket
serverSocket.listen(5)
print(f'Servidor TCP escuchando en {BIND_IP}:{BIND_PORT}', flush=True)

while True:
    conn, addr = serverSocket.accept() # bloquea
    print(f'Conexión recibida desde {addr}')
    sentence = conn.recv(1024).decode()
    conn.send(sentence.upper().encode())
    conn.close()

"""
if __name__ == "main":
    main()
"""
