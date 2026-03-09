#!/usr/bin/env bash
set -e

echo "[Disposable Exec] Starting Redis..."
redis-server --daemonize yes

echo "[Disposable Exec] Redis started."