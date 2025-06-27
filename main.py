import os
import logging
import json
import zipfile
from datetime import datetime
import asyncio 
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename="archive_logs.log",
                    filemode="a",
                    )

logs = logging.getLogger(__name__)

def _get_settings(path: str = "settings.json"):
    if not os.path.exists(path):
        logs.error(f"По пути {path}, настроек не обнаружено!")
        exit(1)
    with open(path, 'r', encoding='utf-8') as file:
        result = json.load(file)
    return result


async def _archive_all_logs(LOG_PATH: str = "", ARCHIVE_DIR: str = "", CHECK_INTERVAL: int = ""):
    now = datetime.now

    for filename in os.listdir(LOG_PATH):
        if filename.endswith(".log"):
            filepath = os.path.join(LOG_PATH, filename)
            mod_time_str = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y%m%d_%H%M%S')
            archive_name = filename.replace(".log", f"_{mod_time_str}.zip")
            archive_path = os.path.join(ARCHIVE_DIR, archive_name)
            
            logs.info(f"Архивируем {filename} -> {archive_name}")

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.write(filepath, arcname=filename)
            os.remove(filepath)
            logs.info(f"{filename} удалён после архивации.")


async def main():
    settings = _get_settings()
    ARCHIVE_DIR = settings.get("ARCHIVE_DIR")
    if not os.path.exists(ARCHIVE_DIR):
        logs.warning(f"По пути {ARCHIVE_DIR}, папки для архивации логов не обнаружено!")
        os.makedirs(ARCHIVE_DIR)
    LOG_PATH = settings.get("LOG_PATH")
    CHECK_INTERVAL = settings.get("CHECK_INTERVAL")

    while True:
        datetime_now = datetime.now()
        logs.info(f"[{datetime_now}] Запуск архиватор логов.")
        await _archive_all_logs(LOG_PATH=LOG_PATH, ARCHIVE_DIR=ARCHIVE_DIR, CHECK_INTERVAL=CHECK_INTERVAL)
        logs.info(f"[{datetime.now()}] Ожидаем {CHECK_INTERVAL} секунд до следующей проверки.\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())