JOB_ID = '854ccca8a1324abdab9f5c92337ccdaa'
RANGES = [{'gpu_index': 0, 'start': 46197080552636416, 'end': 46478555529347072}, {'gpu_index': 1, 'start': 46478555529347072, 'end': 46760030506057728}]
MINUTES = 680.0
THREADS = 2
from pathlib import Path
import runpy
files = list(Path("/kaggle/input").rglob("task.py"))
if len(files) != 1:
    raise RuntimeError("Attach only the Kaggle dataset containing task.py.")
_ = runpy.run_path(str(files[0]), run_name="__main__", init_globals={
    "JOB_ID": JOB_ID, "RANGES": RANGES, "MINUTES": MINUTES, "THREADS": THREADS})
