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

HOST="${DISPOSABLE_EXEC_HOST:-0.0.0.0}"
PORT="${DISPOSABLE_EXEC_PORT:-8000}"

echo "[Disposable Exec] Starting API server on ${HOST}:${PORT} ..."
python3 -m uvicorn disposable_exec.server:app --host "$HOST" --port "$PORT"