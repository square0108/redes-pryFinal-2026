# https://docs.python.org/3/library/asyncio-subprocess.html
import sys, os, asyncio, argparse, signal
from pathlib import Path

DIR_PROYECTO = Path(__file__).resolve().parent
PYTHON_EXE = sys.executable
PATH_SERVIDOR = DIR_PROYECTO / "src" / "servidor.py"
PATH_CLIENTE = DIR_PROYECTO / "src" / "clientes.py"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Levanta server + cliente y muestra su salida intercalada en una sola terminal."
    )
    p.add_argument(
        "--num-nodos", type=int,
        default=int(os.getenv("NUM_NODOS", "3")),
        help="Cantidad de nodos a simular (default: env NUM_NODOS o 3)",
    )
    p.add_argument(
        "--intervalo-seg", type=float,
        default=float(os.getenv("INTERVALO_ENVIO_SEGUNDOS", "2")),
        help="Segundos entre envíos de cada nodo (default: env INTERVALO_ENVIO_SEGUNDOS o 2)",
    )
    p.add_argument(
        "--limpiar-bd", action="store_true",
        help="Borra data/monitoring.db antes de empezar (útil para demos)",
    )
    p.add_argument(
        "--solo-server", action="store_true",
        help="Levanta solo el server (para conectarte con otro cliente aparte)",
    )
    p.add_argument(
        "--solo-cliente", action="store_true",
        help="Levanta solo el cliente (asume que el server ya está corriendo)",
    )
    p.add_argument(
        "--probabilidad-fallo", type=float,
        default=float(os.getenv("PROBABILIDAD_FALLO", "0.0")),
        help="Probabilidad (0-1) de que cada lectura tenga un sensor fuera de rango (default: 0.0)",
    )
    return p.parse_args()


def limpiar_bd() -> None:
    for nombre in ("monitoring.db", "monitoring.db-wal", "monitoring.db-shm"):
        ruta = DIR_PROYECTO / "data" / nombre
        if ruta.exists():
            ruta.unlink()
            print(f"[setup] Borrado {ruta.name}")


async def read_stream(stream, prefix: str) -> None:
    """Lee líneas de un stream y las imprime con prefijo hasta que se cierre."""
    while True:
        line = await stream.readline()
        if not line:
            return
        print(f"{prefix} {line.decode(errors='replace').rstrip()}")


async def start_subprocess(cmd: list[str], env: dict, prefix_err: str):
    """Lanza un subproceso y devuelve (proc, [read_tasks])."""
    proc = await asyncio.create_subprocess_exec(
        *cmd, env=env, cwd=DIR_PROYECTO,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    tasks = [
        asyncio.create_task(read_stream(proc.stdout, f"[{prefix_err}]")),
        asyncio.create_task(read_stream(proc.stderr, f"[{prefix_err} ERR]")),
    ]
    return proc, tasks


async def run(args) -> int:
    if args.limpiar_bd and not args.solo_cliente:
        limpiar_bd()

    env = {
        **os.environ,
        "PYTHONPATH": str(DIR_PROYECTO / "src"),
        "NUM_NODOS": str(args.num_nodos),
        "INTERVALO_ENVIO_SEGUNDOS": str(args.intervalo_seg),
        "PROBABILIDAD_FALLO": str(args.probabilidad_fallo),
    }

    server_proc = None
    server_tasks: list = []
    client_proc = None
    client_tasks: list = []

    if not args.solo_cliente:
        print(f"[setup] Iniciando server ({PATH_SERVIDOR.name})...")
        server_proc, server_tasks = await start_subprocess(
            [PYTHON_EXE, "-u", str(PATH_SERVIDOR)], env, "SERVIDOR"
        )
        await asyncio.sleep(1.5)
        if server_proc.returncode is not None:
            print(f"❌ Server murió al arrancar (código {server_proc.returncode})")
            return 1
        print(f"✅ Server listo, PID {server_proc.pid}")

    if not args.solo_server:
        print(f"[setup] Iniciando cliente ({PATH_CLIENTE.name}) "
              f"con {args.num_nodos} nodos, intervalo {args.intervalo_seg}s...")
        client_proc, client_tasks = await start_subprocess(
            [PYTHON_EXE, "-u", str(PATH_CLIENTE)], env, "CLIENTE"
        )
        if client_proc.returncode is not None:
            print(f"❌ Cliente murió al arrancar (código {client_proc.returncode})")
        else:
            print(f"✅ Cliente listo, PID {client_proc.pid}")

    print(f"[setup] Simulación en curso. Ctrl+C para detener todo.\n")

    procs = [(p, t) for p, t in [(server_proc, server_tasks), (client_proc, client_tasks)] if p is not None]

    try:
        await asyncio.gather(*[p.wait() for p, _ in procs], return_exceptions=True)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass

    for proc, _ in procs:
        if proc.returncode is None:
            try:
                proc.terminate()
            except ProcessLookupError:
                pass
    for proc, _ in procs:
        if proc.returncode is None:
            try:
                await asyncio.wait_for(proc.wait(), timeout=3)
            except asyncio.TimeoutError:
                try: proc.kill()
                except ProcessLookupError: pass

    for _, tasks in procs:
        for t in tasks:
            t.cancel()
    await asyncio.gather(
        *[t for _, tasks in procs for t in tasks],
        return_exceptions=True,
    )

    print(f"\n[setup] Limpieza completa.")
    return 0


def main() -> int:
    try:
        return asyncio.run(run(parse_args()))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
