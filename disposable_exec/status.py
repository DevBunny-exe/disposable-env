import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATUS_FILE = BASE_DIR / "storage" / "status.json"


def set_status(execution_id, status):
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    data[execution_id] = status

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_status(execution_id):
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return None

    return data.get(execution_id)
