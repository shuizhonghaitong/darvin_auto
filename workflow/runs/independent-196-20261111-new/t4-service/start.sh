#!/bin/bash
set -u
log_info() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"; }
log_info "===== start.sh (no args, platform-style) ====="
log_info "cwd: $(pwd)"
log_info "python: $(python3 --version 2>&1)"
exec python3 /app/main.py
