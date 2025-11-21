import os
from config import PARTY_ID

OUTPUT_FOLDER = "/outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
fname = f"output{PARTY_ID}.txt"
path = os.path.join(OUTPUT_FOLDER, fname)
traffic_log_path = os.path.join(OUTPUT_FOLDER, f"traffic_{PARTY_ID}.log")

if os.path.exists(path):
    try:
        os.remove(path)
    except OSError as e:
        print(f"Error deleting old log file {path}: {e}")
if os.path.exists(traffic_log_path):
    try:
        os.remove(traffic_log_path)
    except OSError as e:
        print(f"Error deleting old log file {path}: {e}")

def log(*args):
    with open(path, "a") as f:
        print(*args, file=f)

def log_traffic(messageid, from_party, to_party, byte_size):
    with open(traffic_log_path, "a") as f:
        print(f"{messageid}\t{from_party}\t{to_party}\t{byte_size}", file=f)
