#!/usr/bin/env python3
"""
COMPLETE FILE ACTIVITY MONITOR
Tracks: Creation, Modification, Deletion
Logs: Owner, Timestamp, User, Permissions, Size
"""

import os
import sys

if os.name != "posix":
    print("pwd module not supported on this OS")
    sys.exit(1)
import time
import stat
import pwd
import grp
from datetime import datetime
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileActivityTracker(FileSystemEventHandler):
    """Main class to track all file activities"""
    
    def __init__(self, log_file="file_activity_log.csv"):
        self.log_file = log_file
        self.setup_log_file()
        
    def setup_log_file(self):
        """Create CSV file with headers if it doesn't exist"""
        headers = [
            'timestamp', 'event_type', 'file_path', 'file_name',
            'file_size_bytes', 'file_type', 'owner_user', 'owner_group',
            'permissions', 'last_modified', 'last_accessed', 'created_time',
            'current_user', 'process_id'
        ]
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def get_file_metadata(self, filepath):
        """Extract ALL metadata from a file"""
        try:
            # Get file statistics
            file_stat = os.stat(filepath)
            
            # Get owner user and group names (not just numbers)
            owner_uid = file_stat.st_uid
            group_gid = file_stat.st_gid
            
            try:
                owner_name = pwd.getpwuid(owner_uid).pw_name
            except:
                owner_name = str(owner_uid)
                
            try:
                group_name = grp.getgrgid(group_gid).gr_name
            except:
                group_name = str(group_gid)
            
            # Determine file type
            if stat.S_ISDIR(file_stat.st_mode):
                file_type = "directory"
            elif stat.S_ISLNK(file_stat.st_mode):
                file_type = "symbolic link"
            elif stat.S_ISREG(file_stat.st_mode):
                file_type = "regular file"
            else:
                file_type = "special file"
            
            # Convert permissions to readable format (like 'rwxr-xr--')
            permission_bits = stat.filemode(file_stat.st_mode)
            
            # Get current user (who might have made the change)
            current_user = os.getlogin()
            
            return {
                'size': file_stat.st_size,
                'type': file_type,
                'owner': owner_name,
                'group': group_name,
                'permissions': permission_bits,
                'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'accessed': datetime.fromtimestamp(file_stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'created': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'current_user': current_user,
                'process_id': os.getpid()
            }
            
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def log_event(self, event_type, src_path):
        """Record file event with ALL details"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Millisecond precision
        
        # For deleted files, we can't get metadata
        if event_type == "DELETED" and not os.path.exists(src_path):
            metadata = {
                'size': "N/A",
                'type': "N/A",
                'owner': "N/A",
                'group': "N/A",
                'permissions': "N/A",
                'modified': "N/A",
                'accessed': "N/A",
                'created': "N/A",
                'current_user': os.getlogin(),
                'process_id': os.getpid()
            }
        else:
            metadata = self.get_file_metadata(src_path)
            if not metadata:
                return
        
        # Prepare data for CSV
        row = [
            timestamp,                            # 1. Exact timestamp
            event_type,                           # 2. Event type
            src_path,                             # 3. Full path
            os.path.basename(src_path),           # 4. Filename only
            metadata['size'],                     # 5. File size
            metadata['type'],                     # 6. File type
            metadata['owner'],                    # 7. Owner user
            metadata['group'],                    # 8. Owner group
            metadata['permissions'],              # 9. Permissions
            metadata['modified'],                 # 10. Last modified
            metadata['accessed'],                 # 11. Last accessed
            metadata['created'],                   # 12. Created time
            metadata['current_user'],             # 13. Current user (who made change)
            metadata['process_id']                # 14. Process ID
        ]
        
        # Append to CSV file
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        # Also print to console for immediate feedback
        print(f"[{timestamp}] {event_type}: {src_path}")
        print(f"  Owner: {metadata['owner']}, Current User: {metadata['current_user']}")
    
    # ========== EVENT HANDLERS ==========
    
    def on_created(self, event):
        """When new file/directory is created"""
        if not event.is_directory:
            self.log_event("CREATED", event.src_path)
    
    def on_deleted(self, event):
        """When file/directory is deleted"""
        if not event.is_directory:
            self.log_event("DELETED", event.src_path)
    
    def on_modified(self, event):
        """When file is modified"""
        # Ignore directory modifications (too noisy)
        if not event.is_directory:
            self.log_event("MODIFIED", event.src_path)
            
            # For modification, also check what changed
            self.check_modification_details(event.src_path)
    
    def on_moved(self, event):
        """When file is moved/renamed"""
        if not event.is_directory:
            self.log_event("MOVED_FROM", event.src_path)
            self.log_event("MOVED_TO", event.dest_path)
    
    def check_modification_details(self, filepath):
        """Check what specifically changed in the file"""
        try:
            current_stat = os.stat(filepath)
            
            # Check file size change
            size_changed = current_stat.st_size
            
            # Check permission change
            perm_changed = stat.filemode(current_stat.st_mode)
            
            # Log detailed modification info
            with open("modification_details.log", "a") as f:
                f.write(f"{datetime.now()}: {filepath}\n")
                f.write(f"  Size: {size_changed} bytes\n")
                f.write(f"  Permissions: {perm_changed}\n")
                f.write(f"  Last Modified: {datetime.fromtimestamp(current_stat.st_mtime)}\n")
                f.write("-" * 50 + "\n")
                
        except Exception as e:
            print(f"Could not check modification details: {e}")

def monitor_directory(path_to_watch="."):
    """Start monitoring a directory for file activities"""
    
    print(f"Starting file activity monitor on: {os.path.abspath(path_to_watch)}")
    print("Monitoring: CREATE, DELETE, MODIFY, MOVE")
    print("Log file: file_activity_log.csv")
    print("Press Ctrl+C to stop\n")
    
    # Create event handler
    event_handler = FileActivityTracker()
    
    # Create observer
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    
    # Start monitoring
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nFile monitoring stopped.")
    
    observer.join()

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    # You can specify which directory to monitor
    directory_to_watch = input("Enter directory to monitor (press Enter for current): ").strip()
    
    if not directory_to_watch:
        directory_to_watch = "."
    
    monitor_directory(directory_to_watch)
    
    monitor_directory(directory_to_watch)
