# TICKET-2 验收命令

工作目录：`workflow`。外层执行需审批以访问本地 Qwen；运行 Agent 使用 `workspace-write`，任务禁止联网。

```sh
timeout 900s codex exec --ephemeral --ignore-user-config -c 'model_provider="local"' -c 'model_providers.local.name="local"' -c 'model_providers.local.base_url="http://127.0.0.1:12804/v1"' -c 'model_providers.local.wire_api="responses"' -m qwen3.8-27b-fp8 -s workspace-write --json -o runs/t2-solution-planning-20261109-bounded/final-qwen.md - < runs/t2-solution-planning-20261109-bounded/input.md > runs/t2-solution-planning-20261109-bounded/events-qwen.jsonl 2> runs/t2-solution-planning-20261109-bounded/stderr-qwen.log; result=$?; printf '%s\n' "$result" > runs/t2-solution-planning-20261109-bounded/exit-status.txt; exit "$result"
```
