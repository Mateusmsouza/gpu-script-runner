import shutil

from vram_scheduler import load_config, scheduler

if __name__ == "__main__":
    CONFIG_FILE = "./config.json"
    if not shutil.which("nvidia-smi"):
        print("Erro: nvidia-smi não encontrado. Este script só funciona com GPUs NVIDIA.")
    else:
        config = load_config(CONFIG_FILE)
        scheduler(
            commands=config["commands"],
            max_vram_mb=config["MAX_VRAM_MB"],
            check_interval=config["CHECK_INTERVAL"]
        )
