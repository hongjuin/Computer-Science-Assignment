import time
import stat
from pathlib import Path
from datetime import datetime

LOG_FILE = "directory_log.txt"

def get_metadata(path):
    info = path.stat()
    return {
        "size": info.st_size,
        "permissions": oct(info.st_mode & 0o777),
        "mtime": info.st_mtime
    }

def snapshot(directory):
    data = {}
    for f in Path(directory).iterdir():
        data[f.name] = get_metadata(f)
    return data

def monitor_directory():
    before = snapshot("monitor_dir")
    time.sleep(5)
    after = snapshot("monitor_dir")

    with open(LOG_FILE, "a") as log:
        log.write(f"Check at {datetime.now()}\n")
        log.write(f"Before: {before}\n")
        log.write(f"After: {after}\n\n")

if __name__ == "__main__":
    monitor_directory()
