import subprocess
import time
import shutil
import json
from threading import Thread, Lock
from queue import Queue
import os

CONFIG_FILE = "config.json"


def load_config(path):
    with open(path, "r") as f:
        return json.load(f)


def get_free_vram():
    try:
        result = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free",
                "--format=csv,nounits,noheader"]
        )
        free_vram = int(result.decode().split("\n")[0].strip())
        return free_vram
    except Exception as e:
        print(f"Erro ao consultar VRAM: {e}")
        return 0


def notify(title, message):
    """Notifica via notify-send se disponível, senão imprime."""
    if shutil.which("notify-send"):
        subprocess.Popen(["notify-send", title, message])
    else:
        print(f"[NOTIFICAÇÃO] {title} - {message}")


def launch_command(cmd, running_processes, lock):
    proc = subprocess.Popen(cmd["cmd"], shell=True)
    with lock:
        running_processes.append((proc, cmd["vram"]))
    proc.wait()
    with lock:
        running_processes.remove((proc, cmd["vram"]))
    notify("Comando Finalizado", f"{cmd['cmd']} terminou")


def scheduler(commands, max_vram_mb, check_interval):
    running_processes = []
    lock = Lock()
    queue = Queue()

    for cmd in commands:
        queue.put(cmd)

    while not queue.empty() or running_processes:
        free_vram = get_free_vram()

        with lock:
            used_vram = sum(p[1] for p in running_processes)
            available_vram = max_vram_mb - used_vram

        while not queue.empty():
            cmd = queue.queue[0]
            if cmd["vram"] <= available_vram:
                queue.get()
                t = Thread(target=launch_command, args=(
                    cmd, running_processes, lock))
                t.start()
                available_vram -= cmd["vram"]
            else:
                break

        time.sleep(check_interval)

    notify("Agendamento Finalizado", "Todos os comandos foram executados.")
