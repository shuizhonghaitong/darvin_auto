# TICKET-2 候选方案核验证据 (solution-discovery, 独立运行)

技能已完整读取：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/.agents/skills/solution-discovery/SKILL.md`
（ticket 提示的路径 `/mnt/disk3/liuyutong_home/.agents/skills/...` 不存在，实际技能在 workflow 的 `.agents` 根下，已按实际路径读取并遵循其交付约定。）
CompetitionSpec：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json`（已读）。
本阶段只做方案发现与核验：不复现、不下载大权重、不训练、不提交。

## 结论
`status = blocked`，`selected_candidate_id = null`。原因：执行沙箱阻断全部出站网络，任何外部权重/许可/仓库均无法核验；且提供的训练集不覆盖 1 类（原生）。未宣称任何候选通过验收。

## 实际执行的检索与命令
1. 读取 S3 训练集文档 `raw_doc2_xunlianji.md`(rev 15) 与 S2 榜单介绍 `raw_doc1_bangdan_jieshao.md`(rev 56) —— 均为比赛数据源（非既有方案/旧工程）。
2. 网络探针（显式设置 HTTP(S)_PROXY + 小写 + NO_PROXY/no_proxy 保留 localhost/127.0.0.1/私网，未输出凭据）：
   - 免流 `172.28.4.16:18999`：hf-mirror / github / gitlab.4pd.io / huggingface.co 全部 `curl (7) Couldn't connect`。
   - 付费 `127.0.0.1:7589`：全部 `curl (7) Couldn't connect`（本沙箱内不可达，即使调用前曾监听并返回 200）。
   - 直连无代理：`curl (6) Could not resolve host`。
   - Python `socket()`：loopback / 172.28.4.16:18999 / 8.8.8.8:53 全部 `PermissionError EPERM(errno 1)`；`getaddrinfo` `EAI_AGAIN`。
   → 判定：沙箱在网络层禁止一切出站 socket，非路由问题；未尝试绕过权限。
3. 本地缓存/工具链核验：
   - 基础 python3 3.10.21：torch/transformers/cv2/PIL/timm/sklearn/onnxruntime 均缺失。
   - conda env `evo`：torch 2.8.0+cu128 / torchvision 0.23.0 / transformers 4.57.0 / opencv 4.11.0 / numpy 1.26.4 / PIL 12.2.0 / accelerate 0.34.2（本机 cuda_available=False）。
   - conda env `qwen`：torch 2.9.0 / torchvision 0.24.0 / transformers 4.57.3 / opencv 4.12.0 / numpy 2.2.6 / PIL 12.0.0。
   - HF 缓存：仅 `kernels-community/flash-attn3`（kernel，无图像权重）；无 torch checkpoints 缓存；`~/.cache` 与 darvin_auto(maxdepth 6) 未找到相关 .safetensors/.ckpt/.pth 权重。

## 关键结论与依据
- 三类数据覆盖（已核验）：S3 训练集仅 2 个 zip —— `训练集 1 0_1.zip`(139,334,730 B, token `Ofj7bQtFMoe66fxcCGMc9pBSnug`, 类 0_1) 与 `训练集 0_2.zip`(437,962,033 B, token `Hab7b2O8lo6LCaxXjaNc1jV5nQh`, 类 0_2)。**无 1 类（原生）训练数据。**
- 排序指标（已核验）：`F1_0=(F1_0_1+F1_0_2)/2`（S2），不含 1 类；1 类仅监测 F1_1/准确率。→ 排序目标可围绕 0_1/0_2 优化，但原生样本误判会拉低 precision_0_1/0_2 与 F1_1/准确率，原生判定仍是未解决设计问题。
- 资源（假设，未实测）：`1/2 A100-40g + 2c4g`（S2 原文，单位未显式注明）；按 ticket 指令视为待验证假设。本机沙箱(64核/无GPU)与比赛环境不同，不能度量比赛资源占用。
- 训练入口：自拟候选（CAND-A/C）为待实现(pending)；工具链本地可支撑，但脚本未编写/训练/验证。
- 权重获取与许可：CAND-A/B/D 的外部预训练权重可获取性、版本、许可均 **unknown**（网络阻断，无法核实）；CAND-C 无外部权重，工具链层面可复现，但仍受原生数据缺口与资源未实测约束。
- starting-kit（CAND-D）：URL 存在但不可访问/不可核实（网络阻断）。

## 候选概览（详见 CandidateSolutions.json）
- CAND-A：轻量CNN 0_1/0_2 微调 + 原生残差（自拟，待实现）——排序对齐高，但原生数据缺口+权重许可 unknown。
- CAND-B：公开 AI生成/篡改检测器集成（外部）——未定位任何可核实的具体模型/权重/许可。
- CAND-C：无预训练权重（从头/取证特征）（自拟）——证明"无权重路径"工具链可复现，仍受数据缺口+资源未实测约束。
- CAND-D：starting-kit 参考仓库（外部）——不可访问/不可核实。

## 未满足条件 / 阻塞
1. 网络：沙箱禁止出站 socket（EPERM/EAI_AGAIN）→ 全部外部核验阻塞。
2. 数据：缺 1 类训练数据，原生判定未解决。
3. 权重许可：外部权重可获取性与许可 unknown。
4. 资源：2c4g+1/2 A100 未实测，且为假设。
5. 入口：自拟候选训练/推理入口待实现，未验证。

## 失败/未解决记录
- 所有外部 URL 抓取失败（见命令 2）：hf-mirror.com、huggingface.co、github.com/pytorch/vision、gitlab.4pd.io。
- 未下载 0_1/0_2 zip（网络阻断 + 单文件 >20MB 需用户进一步确认）。
- 未解压、未统计样本数/分布；zip 内实际类占比 unknown。
