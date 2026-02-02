import pandas as pd

# File paths
system_file = "system_performance_log.csv"
directory_file = "directory_log.csv"

# ==============================
# SYSTEM PERFORMANCE STATISTICS
# ==============================
system_df = pd.read_csv(system_file)

# ---- CPU Statistics ----
cpu_min = system_df["cpu_percent"].min()
cpu_avg = system_df["cpu_percent"].mean()
cpu_max = system_df["cpu_percent"].max()

# ---- Memory Statistics ----
mem_avg = system_df["mem_percent"].mean()
mem_max = system_df["mem_percent"].max()

# =========================
# DIRECTORY ACTIVITY STATS
# =========================
dir_df = pd.read_csv(directory_file)

files_created = (dir_df["event"] == "CREATED").sum()
files_modified = (dir_df["event"] == "MODIFIED").sum()
files_deleted = (dir_df["event"] == "DELETED").sum()

# =================
# DISPLAY RESULTS
# =================
print("System Monitoring Summary")
print("=" * 30)

print("\nCPU Statistics")
print("-" * 20)
print(f"Minimum CPU Usage: {cpu_min:.2f}%")
print(f"Average CPU Usage: {cpu_avg:.2f}%")
print(f"Maximum CPU Usage: {cpu_max:.2f}%")

print("\nMemory Statistics")
print("-" * 20)
print(f"Average Memory Usage: {mem_avg:.2f}%")
print(f"Maximum Memory Usage: {mem_max:.2f}%")

print("\nDirectory Activity Summary")
print("-" * 25)
print(f"Files Created: {files_created}")
print(f"Files Modified: {files_modified}")
print(f"Files Deleted: {files_deleted}")
