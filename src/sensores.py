import random
import time

def generar_datos_sensor(nodo_id: str = "invernadero-1"):
    return {
        "nodo_id": nodo_id,
        "timestamp": time.time(),
        "sensores": {
            "temperatura_ambiental": round(random.uniform(15, 35), 2),
            "humedad_suelo": round(random.uniform(20, 80), 2),
            "ph_suelo": round(random.uniform(5.5, 7.5), 2),
            "calidad_aire": {
                "humedad": round(random.uniform(40, 80), 2),
                "co2": round(random.uniform(300, 800), 2),
                "o2": round(random.uniform(19, 22), 2)
            }
        }
    }


#@param datos: dict con la misma forma que retorna generar_datos_sensor().
#@return: tupla (alertas, acciones, anomalias)
# - alertas: lista de strings legibles, pensados para logs/informe.
# - acciones: lista de códigos cortos, pensados para un actuador ficticio.
# - anomalias: lista de dicts con {sensor, valor, tipo, descripcion}, pensados
#   para persistir en BD.

def procesar_datos_sensor(datos):
    alertas = []
    acciones = []
    anomalias = []
    sensores = datos["sensores"]

    if sensores["temperatura_ambiental"] > 25:
        alertas.append("Temperatura alta - Activar ventilación")
        acciones.append("ACTIVAR_VENTILACION")
        anomalias.append({
            "sensor": "temperatura_ambiental",
            "valor": sensores["temperatura_ambiental"],
            "tipo": "alto",
            "descripcion": "Temperatura alta - Activar ventilación",
        })

    if sensores["humedad_suelo"] < 30:
        alertas.append("Humedad de suelo baja - Activar riego")
        acciones.append("ACTIVAR_RIEGO")
        anomalias.append({
            "sensor": "humedad_suelo",
            "valor": sensores["humedad_suelo"],
            "tipo": "bajo",
            "descripcion": "Humedad de suelo baja - Activar riego",
        })

    if sensores["ph_suelo"] < 6.0:
        alertas.append("pH del suelo bajo - Aplicar corrector (cal)")
        acciones.append("APLICAR_CAL")
        anomalias.append({
            "sensor": "ph_suelo",
            "valor": sensores["ph_suelo"],
            "tipo": "bajo",
            "descripcion": "pH del suelo bajo - Aplicar corrector (cal)",
        })

    calidad_aire = sensores["calidad_aire"]
    co2_alto = calidad_aire["co2"] > 700
    o2_bajo = calidad_aire["o2"] < 19.5
    if co2_alto or o2_bajo:
        alertas.append("Calidad de aire mala - Activar ventilación/purificación")
        acciones.append("ACTIVAR_PURIFICACION_AIRE")
    if co2_alto:
        anomalias.append({
            "sensor": "aire_co2",
            "valor": calidad_aire["co2"],
            "tipo": "alto",
            "descripcion": "CO2 alto",
        })
    if o2_bajo:
        anomalias.append({
            "sensor": "aire_o2",
            "valor": calidad_aire["o2"],
            "tipo": "bajo",
            "descripcion": "O2 bajo",
        })

    return alertas, acciones, anomalias

if __name__ == "__main__":
    # Prueba rápida y manual del módulo: py sensores.py
    lectura = generar_datos_sensor("invernadero-test")
    print("Lectura generada:", lectura)
    alertas, acciones, anomalias = procesar_datos_sensor(lectura)
    print("Alertas:", alertas)
    print("Acciones:", acciones)
    print("Anomalias:", anomalias)