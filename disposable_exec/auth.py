from fastapi import Header, HTTPException
import json
import hashlib
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
API_KEYS_FILE = BASE_DIR / "storage" / "api_keys.json"


def load_api_keys():
    if not API_KEYS_FILE.exists():
        return []
    with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_api_keys(data):
    with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def find_api_key(raw_key: str):
    api_keys = load_api_keys()
    key_hash = hash_api_key(raw_key)

    for record in api_keys:
        if record.get("api_key_hash") == key_hash and record.get("is_active", False):
            return record
    return None


def create_api_key(user_id: str, name: str = "default", plan: str = "Free"):
    api_keys = load_api_keys()

    raw_key = "exec_live_" + secrets.token_urlsafe(24)
    key_hash = hash_api_key(raw_key)

    record = {
        "id": f"key_{len(api_keys) + 1:03d}",
        "user_id": user_id,
        "name": name,
        "api_key_hash": key_hash,
        "plan": plan,
        "is_active": True,
    }

    api_keys.append(record)
    save_api_keys(api_keys)

    return raw_key, record


def disable_api_key(key_id: str):
    api_keys = load_api_keys()

    for record in api_keys:
        if record.get("id") == key_id:
            record["is_active"] = False
            save_api_keys(api_keys)
            return True
    return False


def verify_api_key(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    api_key = authorization.split(" ", 1)[1].strip()

    record = find_api_key(api_key)
    if not record:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    return record
