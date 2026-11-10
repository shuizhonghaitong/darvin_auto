# T2 验收命令

在 `workflow` 目录运行；仅与本机已有 Qwen 服务通信，运行 Agent 使用 workspace-write 沙盒。

```sh
timeout 120s codex exec --ephemeral --ignore-user-config -c 'model_provider="local"' -c 'model_providers.local.name="local"' -c 'model_providers.local.base_url="http://127.0.0.1:12804/v1"' -c 'model_providers.local.wire_api="responses"' -m qwen3.8-27b-fp8 -s workspace-write --json -o runs/t2-solution-planning-20261109-recheck/final-qwen.md - < runs/t2-solution-planning-20261109-recheck/input.md > runs/t2-solution-planning-20261109-recheck/events-qwen.jsonl 2> runs/t2-solution-planning-20261109-recheck/stderr-qwen.log
t2_exit=$?
printf '%s\n' "$t2_exit" > runs/t2-solution-planning-20261109-recheck/exit-status.txt
```
