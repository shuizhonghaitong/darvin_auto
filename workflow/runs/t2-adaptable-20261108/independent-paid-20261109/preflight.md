# 本次目标运行前的网络检查

- 免费代理 `http://172.28.4.16:18999`：此前检查 hf-mirror.com 返回 HTTP 200，github.com 超时；详见同级历史运行目录中的 network-preflight-20261109.md。
- 付费代理监听：`ss -lntp '( sport = :7589 )'`（需较高权限）显示 `mihomo-v1.19.33` 监听 `*:7589`。
- 付费代理 GitHub：`curl --http1.1 -sS -o /dev/null -w 'http_status=%{http_code}\n' --connect-timeout 5 --max-time 15 --proxy http://127.0.0.1:7589 https://github.com` 退出 0，返回 `http_status=200`。
- 上述为小流量检查；本次用户允许必要时使用付费出口，尚未授权静默下载大型文件。
