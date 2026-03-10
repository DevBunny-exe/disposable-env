#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

./scripts/start_redis.sh

nohup ./scripts/start_server.sh > /tmp/disposable-exec-api.log 2>&1 &
nohup ./scripts/start_worker.sh > /tmp/disposable-exec-worker.log 2>&1 &

echo "API log: /tmp/disposable-exec-api.log"
echo "Worker log: /tmp/disposable-exec-worker.log"
echo "Started redis + api + worker"