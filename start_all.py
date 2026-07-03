# https://docs.python.org/3/library/asyncio-subprocess.html
import sys, subprocess, asyncio
from pathlib import Path

DIR_PROYECTO = Path(__file__).resolve().parent # obtiene ruta al directorio de este script
PYTHON_EXE = sys.executable # obtiene python desde PATH
PATH_SERVIDOR = DIR_PROYECTO / "src" / "servidor.py"
PATH_CLIENTE = DIR_PROYECTO / "src" / "clientes.py"

async def main():
  # Subproceso servidor
  await start_server()
  
  # Uno o más subprocesos clientes
  await start_clients()

# Startup de proceso servidor
async def start_server():
  print(f"Iniciando servidor ({PATH_SERVIDOR.name})...")
  proc = await asyncio.create_subprocess_exec(
    PYTHON_EXE, "-u", PATH_SERVIDOR, # comando y args
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
  )

  # Crea tareas en segundo plano para leer el output del servidor en tiempo real
  asyncio.create_task(read_stream(proc.stdout, "[SERVIDOR]"))
  asyncio.create_task(read_stream(proc.stderr, "[SERVIDOR ERR]"))
  
  return proc

# Startup de procesos clientes
async def start_clients():
  print(f"Iniciando clientes ({PATH_CLIENTE.name})...")
  proc = await asyncio.create_subprocess_exec(
    PYTHON_EXE, PATH_CLIENTE, # comando y args
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
  )

  # Crea tareas en segundo plano para leer el output del servidor en tiempo real
  asyncio.create_task(read_stream(proc.stdout, "[CLIENTE]"))
  asyncio.create_task(read_stream(proc.stderr, "[CLIENTE ERR]"))
  await proc.wait() # para evitar que start_all.py mate a todos sus subprocesos una vez que termina
  # Esto significa que la simulación sólo vive mientras vivan los clientes
  print(f'[{PATH_CLIENTE.name} terminó con {proc.returncode}]')

async def read_stream(stream, prefix):
  """Monitorea un flujo de datos continuamente y lo imprime al instante."""
  while True:
    line = await stream.readline()
    if not line: # Si el proceso muere, el flujo se cierra y rompemos el bucle
      break
    # Imprime la línea con un prefijo visual para distinguirlo del cliente
    print(f"{prefix} {line.decode().strip()}")

if __name__=="__main__":
  asyncio.run(main())