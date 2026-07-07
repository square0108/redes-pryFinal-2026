"""Cliente de prueba que envía lecturas con un nodo_id específico (no el del orquestador)."""
import sys, os, socket, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from rc_simulacion._env import load_env_file
load_env_file()

from rc_simulacion.protocolos.framing import enviar_json, recibir_json
from rc_simulacion.protocolos.validacionMensaje import firmarMensajeJSON
from rc_simulacion.sensores import generar_datos_sensor

HOST = os.getenv('SERVER_BIND_IP', '127.0.0.1')
PUERTO = int(os.getenv('SERVER_BIND_PORT', '5700'))
SECRET = os.getenv('SECRET_KEY', 'abc123')
NODO_ID = sys.argv[1] if len(sys.argv) > 1 else "invernadero-99"

print(f"[cliente-test] Conectando a {HOST}:{PUERTO} con nodo_id='{NODO_ID}'...")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PUERTO))

for i in range(3):
    lectura = generar_datos_sensor(NODO_ID, probabilidad_fallo=0.0)
    sobre = firmarMensajeJSON(json.dumps(lectura), SECRET)
    enviar_json(s, sobre)
    print(f"[cliente-test] Enviado #{i+1}: nodo_id={lectura['nodo_id']}")
    s.settimeout(3)
    buf = b""
    try:
        resp, _ = recibir_json(s, buf)
        print(f"[cliente-test] Respuesta #{i+1}: {resp}")
    except Exception as e:
        print(f"[cliente-test] Error: {e}")
    time.sleep(0.5)

s.close()
print("[cliente-test] Desconectado")
