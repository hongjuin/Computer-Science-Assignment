import time
from pathlib import Path
from datetime import datetime

LOG_FILE = "directory_log.txt"
MONITOR_DIR = "monitor_dir"
POLL_INTERVAL = 5   # 新增：监控间隔（秒）

def snapshot(directory):
    data = {}
    if not Path(directory).exists():
        return data

    for f in Path(directory).iterdir():
        try:
            info = f.stat()
            data[f.name] = (info.st_size, info.st_mtime, info.st_mode)
        except:
            pass
    return data

def monitor_directory():
    before = snapshot(MONITOR_DIR)

    while True:
        time.sleep(POLL_INTERVAL)
        after = snapshot(MONITOR_DIR)

        created = set(after.keys()) - set(before.keys())
        deleted = set(before.keys()) - set(after.keys())
        modified = []

        for f in before.keys() & after.keys():
            if before[f] != after[f]:
                modified.append(f)

        with open(LOG_FILE, "a") as log:
            log.write("=================================\n")
            log.write(f"Check at {datetime.now()}\n")

            if created:
                log.write("Created files:\n")
                for f in created:
                    log.write(f"  {f}\n")

            if deleted:
                log.write("Deleted files:\n")
                for f in deleted:
                    log.write(f"  {f}\n")

            if modified:
                log.write("Modified files:\n")
                for f in modified:
                    log.write(f"  {f}\n")

            if not created and not deleted and not modified:
                log.write("No changes detected.\n")

            log.write("\n")

        before = after

if __name__ == "__main__":
    Path(MONITOR_DIR).mkdir(exist_ok=True)
    monitor_directory()

