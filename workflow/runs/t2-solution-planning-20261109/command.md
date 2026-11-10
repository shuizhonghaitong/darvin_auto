# T2 自主方案设计验证命令

从 `workflow` 目录执行，使用本地 Qwen 服务；`timeout` 的状态保存在 exit-status.txt，124 表示外层限时到期，其他状态为命令退出状态。

```sh
timeout 120s codex exec --ephemeral --ignore-user-config -c 'model_provider="local"' -c 'model_providers.local.name="local"' -c 'model_providers.local.base_url="http://127.0.0.1:12804/v1"' -c 'model_providers.local.wire_api="responses"' -m qwen3.8-27b-fp8 -s workspace-write --json -o runs/t2-solution-planning-20261109/final-qwen.md - < runs/t2-solution-planning-20261109/input.md > runs/t2-solution-planning-20261109/events-qwen.jsonl 2> runs/t2-solution-planning-20261109/stderr-qwen.log
t2_exit=$?
printf '%s\n' "$t2_exit" > runs/t2-solution-planning-20261109/exit-status.txt
```
