# TICKET-2 后续核查报告

状态：**阻塞**；P2 尚未达到「已通」。本次没有选择候选，也没有下载权重或提交比赛。

## 新证据和限制

- ForensicHub（C5）的固定版本 `92653068` 代码许可证已取得：`raw/forensichub-pinned-license.txt`，对应 <https://raw.githubusercontent.com/scu-zjz/ForensicHub/92653068/LICENSE>；GitHub 许可证 API 响应保存在 `raw/forensichub-license.json`。代码许可证为 CC BY 4.0；这不能证明另行提供的权重也采用同一许可。
- C5 固定版本有推理入口，README 指向权重渠道。`raw/aigc-folder.html` 保存了 Google Drive 公开目录页面，可见四个权重文件名、文件 ID 和页面标示的大小；目录可见不等于文件可下载、完整或许可明确。
- 对 `dualnet.pth` 直链执行 `curl --proxy http://127.0.0.1:7589 -L -I -sS --connect-timeout 6 --max-time 25 -o /dev/null -w 'dualnet HTTP %{http_code} content_type %{content_type} size %{size_download}\n' 'https://drive.google.com/uc?export=download&id=1r0LXfGsO0_5xwg8z_qkTAFr8jrHx4bod'`，退出码 0，输出 `dualnet HTTP 200 content_type text/html; charset=utf-8 size 0`。这是 HTML 响应，不是 checkpoint 文件下载或完整性验证。其他权重同样未完成下载验证。
- C5 的权重许可、目标环境显存和内存占用、三个结果类别的映射及实际覆盖仍缺证据。不能把多个模型的未经验证组合视为已覆盖三分类。比赛可用 GPU 显存约 20 GB；CPU/内存约束是否为 2 核 4 GB 仍需确认。
- FakeShield（C1）所需权重总大小约 44.16 GB，不能单凭磁盘权重大小推断实际推理显存超过 20 GB；其任务覆盖也尚未证明完整。候选 JSON 中关于 C1 已因显存排除的表述证据不足。
- `candidate_solutions.json` 和 `evidence.md` 是目标模型原始产物，保留原样。其中“ticket 禁止下载”的表述不准确：不下载权重是本轮目标环境测试提示中的限制，不能归因于 ticket 本身。它建议必须另开 ticket 才能核实权重，也不是已确立的授权要求。

## 目标环境验证

- 使用服务器的 `codex exec`、本地 provider `http://127.0.0.1:12804/v1` 和 `qwen3.8-27b-fp8` 实际运行复核；主要参数为 `--ephemeral --ignore-user-config --skip-git-repo-check -m qwen3.8-27b-fp8 -s workspace-write --json`。首次复核退出码 0，原始记录为 `events.jsonl`、`stderr.log`、`final.txt`，产出 `candidate_solutions.json` 和 `evidence.md`。模型元数据缺失警告保存在 stderr。
- 首次记录不足以独立证明读取了两份 Skill，故进行不联网的第二次复核。第一次尝试因 `Read-only file system (os error 30)` 初始化失败，证据为 `skill-check-stderr.log`；授权重试后，`skill-check2-events.jsonl` 的 `item.completed` 记录分别显示 `cat .agents/skills/darwin-workflow/SKILL.md` 和 `cat .agents/skills/solution-discovery/SKILL.md` 均退出 0，并有 `turn.completed`。该记录中模型说明了所应用的选择规则并维持 blocked。此重试的进程退出码未单独捕获，不以其为成功证据；`skill-check2-stderr.log` 记录模型列表解析错误。
- 独立解析候选 JSON：7 个候选，`status=blocked`，`selected_candidate_id=null`。当前不能证明任何候选满足全部已知约束；目标模型完成复核不等于 TICKET-2 验收已通过。

## 后续需要的证据

需要在许可和流量安排允许的条件下核实权重能否取得、完整加载及使用许可；确认比赛 CPU/内存约束，并对候选测量目标环境资源占用；提供实际验证的三分类覆盖和映射。只有存在满足全部已知约束且具有可复现入口和资源的候选，才可解除阻塞。
