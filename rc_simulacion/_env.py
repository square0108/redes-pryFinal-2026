"""Carga robusta del .env, independiente del directorio de trabajo."""
from pathlib import Path

from dotenv import load_dotenv
from dotenv.main import find_dotenv

_DIR_PROYECTO = Path(__file__).resolve().parent.parent


def load_env_file() -> str:
    """Carga variables de entorno desde `.env` o `.env.example`.

    1. Busca un `.env` desde el directorio de trabajo actual subiendo hasta la
       raíz del sistema de archivos (comportamiento de `find_dotenv`).
    2. Si no encuentra, carga el `.env.example` que viene commiteado a la
       raíz del proyecto (útil para que la simulación arranque de una sin
       tener que copiar el archivo).

    Retorna la ruta del archivo que se cargó, o `""` si ninguno existía.
    """
    ruta_env = find_dotenv()
    if ruta_env:
        load_dotenv(dotenv_path=ruta_env)
        return ruta_env

    ejemplo = _DIR_PROYECTO / ".env.example"
    if ejemplo.exists():
        load_dotenv(dotenv_path=str(ejemplo))
        print(f"[env] .env no encontrado, usando defaults de {ejemplo.name}")
        return str(ejemplo)

    print("[env] Aviso: no se encontró .env ni .env.example; "
          "usando solo las variables de entorno del sistema.")
    return ""
