# Robado de diapos del curso, RC_U3, diapo 20
# ─── CLIENTE TCP ────────────────────────────── 
import socket, os, time

# Obtenidos desde entorno del docker-compose.yml
# Ambos son los mismos del servidor
TARGET_IP = os.getenv('TARGET_IP')
TARGET_PORT = int(os.getenv('TARGET_PORT'))

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Reintentar conexión continuamente (PLACEHOLDER)
while True:
    try:
        clientSocket.connect((TARGET_IP, TARGET_PORT))
        print(f"Conexión exitosa a {TARGET_IP}:{TARGET_PORT}")
        break # Exit the loop once connected
    except ConnectionRefusedError:
        print(f"Conexión fallida a {TARGET_IP}:{TARGET_PORT}")
        time.sleep(2)

sentence = str("holaaaaaa")
print(f"Mensaje enviado: {sentence}")
clientSocket.send(sentence.encode()) 
resp = clientSocket.recv(1024) 
print('Resp:', resp.decode()) 
clientSocket.close()
