import socket, os, time, json, threading
from dotenv import load_dotenv
from protocolos.validacionMensaje import firmarMensajeJSON
from protocolos.framing import enviar_json, recibir_json
from sensores import generar_datos_sensor

if not load_dotenv('.env'):
    print("Cargando variables de entorno por defecto (.env.example).")
    load_dotenv('.env.example')

# Cargar IP y puerto desde archivo de variables de entorno '.env.example', para mayor configurabilidad.
HOST = os.getenv('CLIENT_TARGET_IP') # ojo, debe ser la ip del servidor, no la del cliente
PUERTO = int(os.getenv('CLIENT_TARGET_PORT')) # puerto de envío
secret_key = os.getenv('SECRET_KEY')

# Cuántos nodos simulados se levantan y cada cuánto envían una lectura.
# Se leen desde el entorno para no tener que tocar el código; si no están
# definidas, se usan valores por defecto razonables para una demo o test.
NUM_NODOS = int(os.getenv('NUM_NODOS', '2'))
INTERVALO_SEGUNDOS = float(os.getenv('INTERVALO_ENVIO_SEGUNDOS', '5'))
"""
Voy a reutilizar esta función 
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
"""
def conectar_con_reintentos(nodo_id: str) -> socket.socket:
    #Crea el socket TCP y reintenta la conexión hasta lograrla.
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((HOST, PUERTO))
            print(f"[{nodo_id}] Conexión exitosa a {HOST}:{PUERTO}")
            return s
        except (ConnectionRefusedError, OSError):
            print(f"[{nodo_id}] Servidor no disponible en {HOST}:{PUERTO}, reintentando en 2s...")
            s.close()
            time.sleep(2)


# Prueba para generar
"""
def testMensajeFirmado() -> json:
    test_dict = {"nombreVariable" : "Temperatura",
                 "unidad" : "Celsius",
                 "valor" : 32.7}
    test_dict_json = json.dumps(test_dict)
    package = firmarMensajeJSON(test_dict_json, secret_key)
    
    return json.dumps(package)"""
def mensaje_firmado(lectura: dict) -> dict:
    """Serializa la lectura a JSON y la empaqueta junto a su firma HMAC."""
    lectura_json = json.dumps(lectura)
    return firmarMensajeJSON(lectura_json, secret_key)
    
def _mostrar_respuesta(nodo_id: str, respuesta: dict) -> None:
    if not respuesta.get("valido"):
        print(f"[{nodo_id}] Mensaje rechazado por el servidor: {respuesta.get('motivo')}")
        return

    alertas = respuesta.get("alertas", [])
    if alertas:
        print(f"[{nodo_id}] Respuesta del servidor -> ALERTAS: {alertas}")
    else:
        print(f"[{nodo_id}] Respuesta del servidor -> sin alertas, todo dentro de rango.")

def simulacion_nodo(nodo_id: str):
    # falta implementar 

if __name__ == "__main__":
    sendTestMessage()
