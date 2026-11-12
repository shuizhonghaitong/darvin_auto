#!/usr/bin/env bash
set -u
cd /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/independent-196-20261111-new
export HTTP_PROXY=http://172.28.4.16:18999 HTTPS_PROXY=http://172.28.4.16:18999
export http_proxy="$HTTP_PROXY" https_proxy="$HTTPS_PROXY"
export NO_PROXY=localhost,127.0.0.1,::1,172.16.0.0/12,10.0.0.0/8,192.168.0.0/16
export no_proxy="$NO_PROXY"
timeout --signal=TERM --kill-after=30s 14400s /mnt/disk3/liuyutong_home/.local/bin/codex exec --json --skip-git-repo-check --sandbox workspace-write -C "$PWD" -m qwen3.8-27b-fp8 -c 'model_provider="local_qwen"' -c 'model_providers.local_qwen.name="Local Qwen"' -c 'model_providers.local_qwen.base_url="http://127.0.0.1:12804/v1"' -c 'model_providers.local_qwen.wire_api="responses"' -c 'sandbox_workspace_write.network_access=true' -c 'approval_policy="never"' --output-last-message continuation-final.md - < continuation-input.md > continuation-events.jsonl 2> continuation-stderr.log
run_status=$?
printf '%s\n' "$run_status" > continuation-exit-code.txt
exit "$run_status"
