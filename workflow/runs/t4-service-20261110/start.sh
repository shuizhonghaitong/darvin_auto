#!/bin/bash
# T4 服务启动脚本：先校验固定权重 sha256，再启动 main.py。
# 用法: ./start.sh [--host H] [--port P]   或 env MOCK_SERVER_HOST/MOCK_SERVER_PORT
set -euo pipefail
cd "$(dirname "$0")"

# 选择已安装 requirements.txt 中依赖的解释器；可用 PYTHON 覆盖。
PY="${PYTHON:-python3}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] 校验权重 sha256 ..."
sha256sum -c weights.sha256
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] 权重校验通过，启动 $PY main.py $*"
exec "$PY" main.py "$@"
