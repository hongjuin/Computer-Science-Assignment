import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)

system_df = pd.read_csv("system_performance_log.csv")
system_df["timestamp"] = pd.to_datetime(system_df["timestamp"])

plt.figure()
plt.plot(system_df["timestamp"], system_df["cpu_percent"])
plt.xlabel("Time")
plt.ylabel("CPU Usage (%)")
plt.title("CPU Usage Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output/cpu_usage.png")
plt.close()

plt.figure()
plt.plot(system_df["timestamp"], system_df["mem_percent"])
plt.xlabel("Time")
plt.ylabel("Memory Usage (%)")
plt.title("Memory Usage Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output/memory_usage.png")
plt.close()

directory_df = pd.read_csv("directory_log.csv")

event_counts = directory_df["event"].value_counts()

plt.figure()
event_counts.plot(kind="bar")
plt.xlabel("Event Type")
plt.ylabel("Count")
plt.title("Directory Change Events")
plt.tight_layout()
plt.savefig("output/directory_changes.png")
plt.close()

print("Visualisation completed. Charts saved in output/ folder.")
