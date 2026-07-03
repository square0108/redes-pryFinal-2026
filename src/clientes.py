import socket, os, time, json
from dotenv import load_dotenv
from protocolos.validacionMensaje import firmarMensajeJSON

if not load_dotenv('.env'):
    print("Cargando variables de entorno por defecto (.env.example).")
    load_dotenv('.env.example')

# Cargar IP y puerto desde archivo de variables de entorno '.env.example', para mayor configurabilidad.
HOST = os.getenv('CLIENT_TARGET_IP') # ojo, debe ser la ip del servidor, no la del cliente
PUERTO = int(os.getenv('CLIENT_TARGET_PORT')) # puerto de envío
secret_key = os.getenv('SECRET_KEY')

def sendTestMessage():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        while True:  # Reintentar conexión continuamente
            try:
                s.connect((HOST, PUERTO))
                print(f"Conexión exitosa a {HOST}:{PUERTO}")
                break
            except ConnectionRefusedError:
                print(f"Conexión fallida a {HOST}:{PUERTO}")
                time.sleep(2)
        
        # JSON de prueba para probar autenticación de mensajes
        testMessage = testMensajeFirmado()
        s.sendall(testMessage.encode('utf-8'))

        data=s.recv(1024) # recibe la respuesta del servidor (eco)
        data=data.decode('utf-8')

    print("Respuesta de servidor: ", repr(data)) # imprime la respuesta del servidor en formato legible

# Prueba para generar
def testMensajeFirmado() -> json:
    test_dict = {"nombreVariable" : "Temperatura",
                 "unidad" : "Celsius",
                 "valor" : 32.7}
    test_dict_json = json.dumps(test_dict)
    package = firmarMensajeJSON(test_dict_json, secret_key)
    
    return json.dumps(package)
    

if __name__ == "__main__":
    sendTestMessage()
