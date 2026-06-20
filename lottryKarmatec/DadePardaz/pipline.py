import subprocess
import os
import sys

base_dir = os.path.dirname(__file__) + "\\etl"

files = ["request_dadepardaz.py", "preprocess_file.py", "merger.py"]

for f in files:
    print("run")
    file_path = os.path.join(base_dir, f)
    subprocess.run([sys.executable, file_path])
    print("done")
