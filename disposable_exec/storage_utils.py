import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"


def ensure_storage_dir():
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default):
    ensure_storage_dir()
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def save_json(path: Path, data):
    ensure_storage_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
