import sqlite3
import threading


def init_db(path: str) -> sqlite3.Connection:
    """Inicializa la BD y devuelve una conexión con WAL activado."""
    conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS lecturas (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        id_invernadero        INTEGER NOT NULL,
        nodo_id               TEXT    NOT NULL,
        timestamp             INTEGER NOT NULL,
        received_at           INTEGER NOT NULL,
        temperatura_ambiental REAL,
        humedad_suelo         REAL,
        ph_suelo              REAL,
        aire_humedad          REAL,
        aire_co2              REAL,
        aire_o2               REAL
    );
    CREATE INDEX IF NOT EXISTS idx_lecturas_inv_ts
        ON lecturas(id_invernadero, timestamp);

    CREATE TABLE IF NOT EXISTS anomalias (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        lectura_id      INTEGER NOT NULL,
        sensor          TEXT    NOT NULL,
        valor           REAL    NOT NULL,
        timestamp       INTEGER NOT NULL,
        tipo            TEXT    NOT NULL CHECK(tipo IN ('bajo','alto')),
        descripcion     TEXT,
        received_at     INTEGER NOT NULL,
        FOREIGN KEY (lectura_id) REFERENCES lecturas(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_anomalias_lectura
        ON anomalias(lectura_id);
    """)
    return conn


def insertar_lectura(conn: sqlite3.Connection, lock: threading.Lock,
                     id_invernadero: int, nodo_id: str,
                     ts: int, received_at: int, sensores: dict) -> int:
    """Inserta una lectura y devuelve su id."""
    calidad_aire = sensores.get("calidad_aire", {}) or {}
    with lock:
        cursor = conn.execute(
            """INSERT INTO lecturas
               (id_invernadero, nodo_id, timestamp, received_at,
                temperatura_ambiental, humedad_suelo, ph_suelo,
                aire_humedad, aire_co2, aire_o2)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id_invernadero, nodo_id, ts, received_at,
             sensores.get("temperatura_ambiental"),
             sensores.get("humedad_suelo"),
             sensores.get("ph_suelo"),
             calidad_aire.get("humedad"),
             calidad_aire.get("co2"),
             calidad_aire.get("o2"))
        )
        return cursor.lastrowid


def insertar_anomalia(conn: sqlite3.Connection, lock: threading.Lock,
                      lectura_id: int, sensor: str, valor: float,
                      ts: int, tipo: str, descripcion: str,
                      received_at: int) -> None:
    """Inserta una anomalía asociada a una lectura."""
    with lock:
        conn.execute(
            """INSERT INTO anomalias
               (lectura_id, sensor, valor, timestamp, tipo, descripcion, received_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (lectura_id, sensor, valor, ts, tipo, descripcion, received_at)
        )


def cerrar(conn: sqlite3.Connection) -> None:
    try:
        conn.close()
    except Exception:
        pass
