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
#@return: tupla (alertas, acciones)
# - alertas: lista de strings legibles, pensados para logs/informe.
# - acciones: lista de códigos cortos, pensados para un actuador ficticio. 

def procesar_datos_sensor(datos):
    alertas = []
    acciones = []
    sensores= datos["sensores"]

    # ¿Temperatura muy alta/baja? -> Activar calefacción/aire acondicionado
    # (por simplicidad solo controlamos el caso de temperatura alta, que es
    # el escenario típico de un invernadero mal ventilado)
    if sensores["temperatura_ambiental"] > 25:
        alertas.append("Temperatura alta - Activar ventilación")
        acciones.append("ACTIVAR_VENTILACION")

    # ¿Humedad de suelo baja? -> Irrigar automáticamente
    if sensores["humedad_suelo"] < 30:
        alertas.append("Humedad de suelo baja - Activar riego")
        acciones.append("ACTIVAR_RIEGO")

    # ¿pH bajo? -> Inserción de minerales correspondientes
    if sensores["ph_suelo"] < 6.0:
        alertas.append("pH del suelo bajo - Aplicar corrector (cal)")
        acciones.append("APLICAR_CAL")

    # ¿Calidad de aire mala? -> Activar ventilación o purificación de aire
    calidad_aire = sensores["calidad_aire"]
    if calidad_aire["co2"] > 700 or calidad_aire["o2"] < 19.5:
        alertas.append("Calidad de aire mala - Activar ventilación/purificación")
        acciones.append("ACTIVAR_PURIFICACION_AIRE")

    return alertas, acciones

if __name__ == "__main__":
    # Prueba rápida y manual del módulo: py sensores.py 
    lectura = generar_datos_sensor("invernadero-test")
    print("Lectura generada:", lectura)
    alertas, acciones = procesar_datos_sensor(lectura)
    print("Alertas:", alertas)
    print("Acciones:", acciones)