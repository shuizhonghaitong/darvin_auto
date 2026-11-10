# TICKET-2 网络预检（2026-11-09）

- 比赛附件工具路径 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/lark-cli-1.0.98/lark-cli` 经 `test -x` 检查可执行。
- 使用 `curl --http1.1` 显式指定免流代理 `http://172.28.4.16:18999`：`https://hf-mirror.com` 和 `https://www.example.com` 均返回 HTTP 200，退出码 0；`https://github.com` 在 12 秒超时，退出码 28、HTTP 000。分别是目的站点实测结果，不代表所有网站可用。
- 运行 `codex sandbox -c 'sandbox_mode="workspace-write"' -c sandbox_workspace_write.network_access=true -- curl --http1.1 -sS -o /dev/null -w 'http_status=%{http_code}\n' --connect-timeout 5 --max-time 12 --proxy http://172.28.4.16:18999 https://hf-mirror.com`，在获准的单条命令范围内返回 `http_status=200`、退出码 0。
- 本次没有使用付费代理。上述单命令测试不证明独立运行 Agent 已获网络权限、已执行或已发现方案。
- `codex exec --help` 显示可选沙箱模式；当前已核实的 `sandbox_workspace_write.network_access=true` 为通用网络开关，尚未确认可按代理地址限制。未在没有额外授权的情况下把通用网络权限赋予运行 Agent。
