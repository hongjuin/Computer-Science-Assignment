import time
import stat
from pathlib import Path
from datetime import datetime

# ================= Configuration =================
MONITOR_DIR = "monitor_dir"
LOG_FILE = "directory_log.txt"
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


def snapshot(directory):
    """
    Take a snapshot of current directory state.
    Store file size, modification time, and permission mode.
    """
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
                    log.write(
                        f"  {f} | Type: {info['type']} | Size: {info['size']} bytes\n"
                    )

            # DELETED
            if deleted:
                log.write("Deleted files:\n")
                for f in deleted:
                    log.write(f"  {f}\n")

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

            if not created and not deleted and not modified:
                log.write("No changes detected.\n")

            log.write("\n")

        before = after


if __name__ == "__main__":
    Path(MONITOR_DIR).mkdir(exist_ok=True)
    print(f"[INFO] Monitoring directory: {MONITOR_DIR}")
    print("[INFO] Press Ctrl+C to stop\n")
    monitor_directory()

