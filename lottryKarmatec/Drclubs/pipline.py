import subprocess
import os
import sys

base_dir = os.path.dirname(__file__) + "\\etl"

files = ["request_drclub.py", "preprocess_file.py"]

for f in files:
    file_path = os.path.join(base_dir, f)
    try:
        subprocess.run([sys.executable, file_path])
    except Exception as e:
        exit()

