import os
from config import PARTY_ID

OUTPUT_FOLDER = "/outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
fname = f"output{PARTY_ID}.txt"
path = os.path.join(OUTPUT_FOLDER, fname)

def log(*args):
    with open(path, "a") as f:
        print(*args, file=f)
