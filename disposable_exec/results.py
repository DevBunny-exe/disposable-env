import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESULT_FILE = BASE_DIR / "storage" / "results.json"


def save_result(execution_id, result):
    try:
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    data[execution_id] = result

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_result(execution_id):
    try:
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return None

    return data.get(execution_id)
