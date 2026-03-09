#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[Disposable Exec] Starting Redis..."
bash "$ROOT_DIR/scripts/start_redis.sh"

echo "[Disposable Exec] Starting API server in a new terminal/session manually:"
echo "  bash $ROOT_DIR/scripts/start_server.sh"

echo "[Disposable Exec] Starting worker in a new terminal/session manually:"
echo "  bash $ROOT_DIR/scripts/start_worker.sh"

echo
echo "[Disposable Exec] Recommended terminal layout:"
echo "  Terminal 1 -> bash $ROOT_DIR/scripts/start_server.sh"
echo "  Terminal 2 -> bash $ROOT_DIR/scripts/start_worker.sh"
echo
echo "[Disposable Exec] Redis start step completed."