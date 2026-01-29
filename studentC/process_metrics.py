def calculate_average(values):
    return sum(values) / len(values) if values else 0

def count_events(log_lines, keyword):
    return sum(1 for line in log_lines if keyword in line)

if __name__ == "__main__":
    cpu_samples = [20, 30, 25, 40]
    print("Average CPU usage:", calculate_average(cpu_samples))
