import csv
import matplotlib.pyplot as plt

time = []
cpu = []

with open("../system_performance_log.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        time.append(row["timestamp"])
        cpu.append(float(row["cpu_percent"]))

plt.plot(time, cpu)
plt.title("CPU Usage Trend Over Time")
plt.xlabel("Time")
plt.ylabel("CPU Usage (%)")
plt.tight_layout()
plt.savefig("../reports/cpu_usage.png")
plt.close()

memory = []

with open("../system_performance_log.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        memory.append(float(row["mem_percent"]))

plt.bar(time, memory)
plt.title("Memory Usage Over Time")
plt.xlabel("Time")
plt.ylabel("Memory Usage (%)")
plt.tight_layout()
plt.savefig("../reports/memory_usage.png")
plt.close()

events = {"created": 0, "modified": 0, "deleted": 0}

with open("../directory_log.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        event = row["event"]
        if event in events:
            events[event] += 1

plt.bar(events.keys(), events.values())
plt.title("Directory Change Events Summary")
plt.xlabel("Event Type")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("../reports/directory_events.png")
plt.close()
