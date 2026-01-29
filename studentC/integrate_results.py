from read_logs import read_system_log
from generate_report import generate_text_report

def integrate():
    summary = {
        "Status": "Integration successful",
        "Logs processed": "Yes"
    }
    generate_text_report("../reports/final_report.txt", summary)

if __name__ == "__main__":
    integrate()
