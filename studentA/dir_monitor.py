import time
import stat
from pathlib import Path

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

before = snapshot("monitor_dir")
time.sleep(5)
after = snapshot("monitor_dir")

print("Before:", before)
print("After:", after)
