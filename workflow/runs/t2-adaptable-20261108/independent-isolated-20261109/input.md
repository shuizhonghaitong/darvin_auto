你是目标运行 Agent。本次只验证 TICKET-2：独立根据比赛需求发现并评估可复现方案，不读取其他运行的候选方案、历史运行日志或旧工程解法。读取 /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/.agents/skills/solution-discovery/SKILL.md 和 /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json，遵循 Skill。

安全边界：禁止读取、复制、改写认证目录、密钥、token 或凭据；禁止更改认证方式或尝试绕过认证保护。此前附件工具的凭据刷新受到只读保护，因此本次不要运行 lark-cli 或尝试修复其认证。附件内容无法通过已授权的其他方式核验时记录 unknown 和具体限制，但继续独立核验其他条件。

比赛训练附件已获用户授权用于训练，但授权不证明附件内容或标签覆盖。暂按 2 核 CPU、4GB 内存检查部署资源，不得声称这是已核实的官方限制；区分训练与部署资源。核查三类标签、数据覆盖、训练入口、权重获取及各自许可；可以自己设计方案或针对性查询公开资料，不假装验证未证实的信息。

网络：免流代理 http://172.28.4.16:18999 可访问 hf-mirror.com，但访问 github.com 超时；付费代理 http://127.0.0.1:7589 已验证监听且 GitHub 返回 HTTP 200。用户允许必要时使用付费出口；仅使用必要的小型查询，不下载大文件。保留 localhost 和内网 NO_PROXY，记录实际代理和 HTTP 状态。不要使用其他付费代理。

在当前工作目录尽早写出 candidate_solutions.json 和 evidence.md 并随调查更新，保持有效 JSON，记录实际来源、代理、失败和未知项。不要读取其他运行目录中的候选，不要执行 TICKET-3 的复现或训练。给予充分时间；无法满足验收时明确 selected_candidate_id=null、具体阻塞和已尝试方法。
