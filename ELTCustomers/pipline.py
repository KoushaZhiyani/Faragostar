import subprocess
import os
import sys

base_dir = os.path.dirname(__file__)

files = ["request_drclub.py", "preprocess_file.py", "validator_data.py"]

for f in files:
    file_path = os.path.join(base_dir, f)
    subprocess.run([sys.executable, file_path])
    input()
