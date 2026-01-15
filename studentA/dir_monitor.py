from pathlib import Path

directory = "monitor_dir"

for file in Path(directory).iterdir():
    print(file.name)
