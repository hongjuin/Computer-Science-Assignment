import time
import stat
from pathlib import Path
from datetime import datetime

LOG_FILE = "directory_log.txt"
MONITOR_DIR = "monitor_dir"

def get_file_type(path):
    if path.is_file():
        return "regular file"
    elif path.is_dir():
        return "directory"
    elif path.is_symlink():
        return "symbolic link"
    else:
        return "other"

def get_metadata(path):
    info = path.stat()
    return {
        "type": get_file_type(path),
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
    before = snapshot(MONITOR_DIR)
    time.sleep(5)
    after = snapshot(MONITOR_DIR)

    created_files = set(after.keys()) - set(before.keys())
    deleted_files = set(before.keys()) - set(after.keys())

    with open(LOG_FILE, "a") as log:
        log.write(f"Check at {datetime.now()}\n")

        if created_files:
            log.write("New files detected:\n")
            for f in created_files:
                log.write(f"  {f} -> {after[f]}\n")

        if deleted_files:
            log.write("Deleted files detected:\n")
            for f in deleted_files:
                log.write(f"  {f}\n")

        if not created_files and not deleted_files:
            log.write("No changes detected.\n")

        log.write("\n")

if __name__ == "__main__":
    monitor_directory()

