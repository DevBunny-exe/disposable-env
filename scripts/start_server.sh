#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

set -a
source .env
set +a

python3 -m uvicorn disposable_exec.server:app --host 0.0.0.0 --port 8000