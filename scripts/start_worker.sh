#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
  echo "[Disposable Exec] Loading environment from $ENV_FILE"
  set -a
  source "$ENV_FILE"
  set +a
else
  echo "[Disposable Exec] WARNING: .env not found at $ENV_FILE"
fi

echo "[Disposable Exec] Starting worker ..."
python3 -m disposable_exec.worker