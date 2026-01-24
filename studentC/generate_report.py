def generate_text_report(output_path, summary):
    with open(output_path, "w") as f:
        f.write("System Monitoring Summary\n")
        f.write("-------------------------\n")
        for key, value in summary.items():
            f.write(f"{key}: {value}\n")

if __name__ == "__main__":
    summary_data = {
        "Average CPU Usage": "30%",
        "Average Memory Usage": "65%",
        "Disk Usage": "70%"
    }
    generate_text_report("../reports/summary_report.txt", summary_data)
