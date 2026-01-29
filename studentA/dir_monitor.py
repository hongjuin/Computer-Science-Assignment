import time
import stat
import csv
from pathlib import Path
from datetime import datetime

# ================= Configuration =================
MONITOR_DIR = "monitor_dir"
LOG_FILE = "directory_log.txt"
CSV_FILE = "directory_log.csv"
POLL_INTERVAL = 5
# =================================================


def get_file_type(mode):
    if stat.S_ISREG(mode):
        return "regular file"
    elif stat.S_ISDIR(mode):
        return "directory"
    elif stat.S_ISLNK(mode):
        return "symbolic link"
    else:
        return "other"


def init_csv():
    """
    Initialize CSV file with header if not exists
    """
    if not Path(CSV_FILE).exists():
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "event", "filename", "details"])


def log_to_csv(event, filename, details):
    """
    Append one event record into CSV
    """
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event,
            filename,
            details
        ])


def snapshot(directory):
    data = {}

    if not Path(directory).exists():
        return data

    for f in Path(directory).iterdir():
        try:
            st = f.stat()
            data[f.name] = {
                "size": st.st_size,
                "mtime": st.st_mtime,
                "mode": st.st_mode,
                "type": get_file_type(st.st_mode)
            }
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
                modified.append((f, before[f], after[f]))

        with open(LOG_FILE, "a") as log:
            log.write("=================================\n")
            log.write(f"Check at {datetime.now()}\n")

            # CREATED
            if created:
                log.write("Created files:\n")
                for f in created:
                    info = after[f]
                    detail = f"Type: {info['type']}, Size: {info['size']} bytes"
                    log.write(f"  {f} | {detail}\n")
                    log_to_csv("CREATED", f, detail)

            # DELETED
            if deleted:
                log.write("Deleted files:\n")
                for f in deleted:
                    log.write(f"  {f}\n")
                    log_to_csv("DELETED", f, "File deleted")

            # MODIFIED
            if modified:
                log.write("Modified files:\n")
                for f, old, new in modified:
                    if old["size"] != new["size"]:
                        detail = f"Size {old['size']} -> {new['size']}"
                    elif old["mode"] != new["mode"]:
                        detail = "Permissions changed"
                    else:
                        detail = "Timestamp updated"

                    log.write(f"  {f}: {detail}\n")
                    log_to_csv("MODIFIED", f, detail)

            if not created and not deleted and not modified:
                log.write("No changes detected.\n")

            log.write("\n")

        before = after


if __name__ == "__main__":
    Path(MONITOR_DIR).mkdir(exist_ok=True)
    init_csv()

    print(f"[INFO] Monitoring directory: {MONITOR_DIR}")
    print(f"[INFO] TXT log file: {LOG_FILE}")
    print(f"[INFO] CSV log file: {CSV_FILE}")
    print("[INFO] Press Ctrl+C to stop\n")

    monitor_directory()

