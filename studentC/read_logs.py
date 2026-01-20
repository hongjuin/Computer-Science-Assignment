def read_system_log(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    return lines

def read_directory_log(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    return lines

if __name__ == "__main__":
    print("Log reader module ready")
