from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import stat
from pathlib import Path
import time

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"File created: {event.src_path}")

    def on_deleted(self, event):
        print(f"File deleted: {event.src_path}")

    def on_modified(self, event):
        print(f"File modified: {event.src_path}")

observer = Observer()
observer.schedule(MyHandler(), path='.', recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()

def get_file_metadata(filepath):
    p = Path(filepath)
    stat_info = p.stat()
    
    return {
        "filename": p.name,
        "type": "dir" if p.is_dir() else "file",
        "size": stat_info.st_size,
        "owner": stat_info.st_uid,
        "group": stat_info.st_gid,
        "permissions": stat.filemode(stat_info.st_mode),
        "created": time.ctime(stat_info.st_ctime),
        "modified": time.ctime(stat_info.st_mtime),
        "accessed": time.ctime(stat_info.st_atime)
    }

