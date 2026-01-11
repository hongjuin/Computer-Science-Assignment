from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
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