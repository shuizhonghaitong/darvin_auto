# 独立实验证据归档

本目录归档 2026-11-11 比赛 196 实验的现存证据；归档过程没有重新运行实验。初次运行和获授权后的续跑是两次独立的 `codex exec` 调用，不是一次完整调用。

- `launch.sh` / `input.md`：首次启动命令和输入；外层退出码见 `exit-code.txt`（0）。
- `continuation-launch.sh` / `continuation-input.md`：续跑启动命令和输入；外层退出码见 `continuation-exit-code.txt`（0）。启动脚本仅作证据，请勿为验证归档而执行。
- `events.jsonl` / `continuation-events.jsonl`：分别保留全部 665 / 250 条事件的结构、类型、状态和标识。为防止公开凭证和其他敏感内容，任意命令、模型文本和工具输出等字段已整体遮蔽，替换为规范化 JSON 内容的 SHA-256 和字节数。因此这是脱敏结构轨迹，不是可阅读的完整原文；原文未提交。
- `t2-planning/solution_plan.json`：首次运行产生的 T2 方案。
- `continuation/`：提交、回执、状态、方案列表和完成任务列表的平台 JSON 原件。
- `manifest.json`：每个源文件的 SHA-256 和长度；轨迹另列归档文件的 SHA-256 和事件数。`build_archive.py` 记录脱敏方法，需要本地未公开的原始文件才能重建。

两次进程退出码为 0 不等于平台评测成功。首次运行结束时尚未提交；续跑的实际平台结果另见仓库中的 `continuation-final.md` 和本目录平台 JSON：任务 success、作业 SUCCEEDED、得分 42.21。两次调用及各自证据保持区分。
