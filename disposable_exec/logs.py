import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "storage" / "execution_logs.jsonl"


def write_log(execution_id, key_id, stdout, stderr, exit_code, duration):
    log = {
        "execution_id": execution_id,
        "key_id": key_id,
        "timestamp": int(time.time()),
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "duration": duration
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")
