import argparse, sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # backend sin pantalla: solo generamos archivos PNG
import matplotlib.pyplot as plt

"""
Generamos gráficos con matplotlib a partir de los datos que el servidor fue
guardando en la base de datos SQLite.
Este script es independiente del servidor: se ejecuta DESPUÉS de correr
una simulación.
Uso:
    python -m rc_simulacion.graficas
Genera, por cada variable ambiental, un gráfico de líneas con una serie
por cada invernadero (nodo_id), y además un gráfico de barras con el
conteo de anomalías detectadas por sensor. Todo se guarda como PNG.
"""

DIR_PROYECTO = Path(__file__).resolve().parent.parent

# Columna de la tabla con nombres de graficos, unidades, limites y colores para rangos aceptables
VARIABLES = {
    "temperatura_ambiental": ("Temperatura ambiental", "°C", 18.0, 25.0),
    "humedad_suelo": ("Humedad de suelo", "%", 20.0, 60.0),
    "ph_suelo": ("pH del suelo", "pH", 5.8, 6.8),
    "aire_humedad": ("Humedad del aire", "%", 50.0, 75.0),
    "aire_co2": ("CO2 del aire", "ppm", 350.0, 700.0),
    "aire_o2": ("O2 del aire", "%", 20.0, 21.5),
}
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--db", default=str(DIR_PROYECTO / "data" / "monitoring.db"),
        help="Ruta a la base de datos SQLite (default: data/monitoring.db)",
    )
    p.add_argument(
        "--salida", default=str(DIR_PROYECTO / "graficos"),
        help="Carpeta donde guardar los PNG generados (default: graficos/)",
    )
    p.add_argument(
        "--no-limites", action="store_true",
        help="Ocultar líneas de límites en los gráficos",
    )
    return p.parse_args()

def cargar_lecturas(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return conn.execute(
        "SELECT * FROM lecturas ORDER BY timestamp ASC"
    ).fetchall()

def cargar_anomalias(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return conn.execute(
        "SELECT * FROM anomalias ORDER BY timestamp ASC"
    ).fetchall()

def graficar_variable(lecturas: list[sqlite3.Row], columna: str,
                       nombre_bonito: str, unidad: str, dir_salida: Path,
                       limite_bajo: float = None, limite_alto: float = None,
                       mostrar_limites: bool = True) -> None:
    """Un gráfico de líneas: tiempo (eje X) vs valor del sensor (eje Y),
    con una línea distinta por cada invernadero (nodo_id).
    Si mostrar_limites es True, dibuja líneas horizontales para los límites."""
    series = defaultdict(lambda: ([], []))  # nodo_id -> (tiempos, valores)


    for fila in lecturas:
        valor = fila[columna]
        if valor is None:
            continue
        tiempo = datetime.fromtimestamp(fila["timestamp"])
        series[fila["nodo_id"]][0].append(tiempo)
        series[fila["nodo_id"]][1].append(valor)

    if not series:
        print(f"[graficos] Sin datos para '{columna}', se omite.")
        return

    
    plt.figure(figsize=(9, 5))
    for nodo_id, (tiempos, valores) in sorted(series.items()):
        plt.plot(tiempos, valores, marker="o", markersize=3, label=nodo_id)

    # Añadir líneas de límites si se solicita
    if mostrar_limites and limite_bajo is not None and limite_alto is not None:
        plt.axhline(y=limite_bajo, color='red', linestyle='--', alpha=0.5, linewidth=1.5,
                   label=f'Límite inferior ({limite_bajo}{unidad})')
        plt.axhline(y=limite_alto, color='orange', linestyle='--', alpha=0.5, linewidth=1.5,
                   label=f'Límite superior ({limite_alto}{unidad})')
        # Rellenar zona normal (opcional, descomentar si se quiere)
        # all_times = []
        # for tiempos, _ in series.values():
        #     all_times.extend(tiempos)
        # if all_times:
        #     plt.axvspan(min(all_times), max(all_times), ymin=0.1, ymax=0.9,
        #                alpha=0.05, color='green')

    plt.title(f"{nombre_bonito} en el tiempo")
    plt.xlabel("Hora")
    plt.ylabel(f"{nombre_bonito} ({unidad})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    ruta = dir_salida / f"{columna}.png"
    plt.savefig(ruta, dpi=120)
    plt.close()
    print(f"[graficos] Generado {ruta}")


def graficar_anomalias(anomalias: list[sqlite3.Row], dir_salida: Path) -> None:
    """Barras con el conteo de anomalías detectadas, agrupadas por sensor."""
    conteo = defaultdict(int)
    for a in anomalias:
        conteo[a["sensor"]] += 1

    if not conteo:
        print("[graficos] No se registraron anomalías, se omite ese gráfico.")
        return

    sensores = sorted(conteo.keys())
    valores = [conteo[s] for s in sensores]

    plt.figure(figsize=(8, 5))
    plt.bar(sensores, valores, color="tomato")
    plt.title("Anomalías detectadas por sensor")
    plt.xlabel("Sensor")
    plt.ylabel("Cantidad de anomalías")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    ruta = dir_salida / "anomalias_por_sensor.png"
    plt.savefig(ruta, dpi=120)
    plt.close()
    print(f"[graficos] Generado {ruta}")

def main() -> None:
    args = parse_args()

    if not Path(args.db).exists():
        print(f"[graficos] No se encontró la base de datos en {args.db}. "
              f"¿Corriste el servidor al menos una vez?")
        return

    dir_salida = Path(args.salida)
    dir_salida.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(args.db)
    lecturas = cargar_lecturas(conn)
    anomalias = cargar_anomalias(conn)
    conn.close()

    print(f"[graficos] {len(lecturas)} lecturas y {len(anomalias)} anomalías cargadas.")

    if not lecturas:
        print("[graficos] La base de datos está vacía, no hay nada que graficar.")
        return

    for columna, (nombre_bonito, unidad, limite_bajo, limite_alto) in VARIABLES.items():
        graficar_variable(lecturas, columna, nombre_bonito, unidad, dir_salida,
                         limite_bajo, limite_alto)

    graficar_anomalias(anomalias, dir_salida)

    print(f"[graficos] Listo. Revisa la carpeta '{dir_salida}'.")


if __name__ == "__main__":
    main()
