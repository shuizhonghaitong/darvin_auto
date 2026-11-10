# TICKET-2 复核证据（followup）— 图像真伪鉴定榜 (Darwin 196)

- 生成时间：2026-11-08 ~09:40 UTC
- 性质：**TICKET-2 复核（followup re-audit）**。在 t2-audit 的 blocked 结论基础上，
  消化本目录 `raw/` 的新证据，逐项重核候选的：复现入口、固定版本、权重可获得性及
  单独许可、资源需求、三分类覆盖。
- 输入：
  - 规范：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json`
  - 前次审计：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-audit-20261108/candidate_solutions.json` + `evidence.md`
  - 原始检索证据：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-real-retry-20261108/raw/`（46 文件，t2-audit 已逐项复核）
  - 新证据：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-followup-20261108/raw/`（4 文件，本次逐一核验）
- 产物：本文件 + 同目录 `candidate_solutions.json`。
- 约束执行：本复核**零新增网络请求**、**未下载任何权重**、**未执行比赛提交**；
  只写入本目录两个产物文件，未修改任何其他文件。
  `events.jsonl`/`stderr.log` 为 codex exec 会话日志，非产物。

## 1. 新证据清单与核验

| 文件 | sha256 | 内容核验 |
|---|---|---|
| `raw/forensichub-pinned-license.txt` | `e3cda76e3e7da38645c755e237be21aeb6dd67ba0a8bf9557ecea0570d024528` | 37312 B，标准 CC-BY-4.0 全文（首行 "Attribution 4.0 International"，末段 Creative Commons 声明）。ticket 确认此为固定 SHA 92653068… 下取得的 LICENSE |
| `raw/forensichub-license.json` | `b9c10ab328f94614ac8c7b261d19f4004367e7bbc43986a5296ead9e162b21d4` | GitHub API `repos/scu-zjz/ForensicHub/contents/LICENSE?ref=master` 完整响应：name=LICENSE, size=37312, 许可分类器 `license.spdx_id=CC-BY-4.0`（key=cc-by-4.0），含 base64 全文 |
| `raw/pinned-license.json` | `6a2172a39b0c20b9974effd44d6582ae9b5a3fc8ffb167b5b6f51c9e8a1d0e8e` | GitHub API 未认证限流错误（"API rate limit exceeded"）——解释了固定 SHA 的 API 核验未走通、LICENSE 改经 raw 通道取得 |
| `raw/aigc-folder.html` | `8347003d0f1ad3c3129fe828f9b2673c47197c21632a867313833ef81e25ac1c` | GDrive 目录页存档（HTTP 200），title="AIGC_Bench - Google 云端硬盘"，folder id `1M-qe5xOblVZgKiBQ9j1Q-GQ4ao5VJMHZ` |

**字节级核验（离线执行）**
- `forensichub-license.json` 的 base64 `content` 解码 = 37312 B，与
  `forensichub-pinned-license.txt` **逐字节一致**（同 sha256 `e3cda76e…`）。
- 两者又与 t2-real-retry 审计中已核实的 `raw/lic_IMDLBenCo.txt`
  （IMDL-BenCo 的 CC-BY-4.0 LICENSE，37312 B）**逐字节一致**，即三方同源，
  为标准 CC-BY-4.0 文本。
- 注意：API 响应 ref=master（非固定 SHA）；pinned txt 的精确抓取 URL 未记录于
  raw 文件。判定置信依据 = 逐字节一致 + GitHub 分类器 + ticket 声明（见 R1 caveat）。

## 2. 逐项核查结论（对照 ticket 五个核查维度）

### 2.1 复现入口（E1）
- **C5**：维持 satisfied，补记限制（R4）。`runs/t2-real-retry-20261108/raw/forensichub_inference.py`
  （pinned SHA 抓取）展示完整推理模式：`build_from_registry(MODELS, model_args)` →
  `torch.load(init_path)` → 单图 forward → `pred_label`（示例 ConvNextSmall/256px）。
  但其示例 `init_path` 是作者本机绝对路径（`…/checkpoint-19.pth`），**公开 .pth 到
  模型配置的接线未验证**；入口存在 ≠ 入口+公开权重端到端可用。
- **C1/C2/C3/C4/C6/C7**：无新证据，t2-audit 判定维持（R7）。

### 2.2 固定版本
- 七个候选的固定 SHA 维持 t2-audit 记录（C5=`92653068ccb22744a5e58df6e47cc813e0441202`，
  与 `raw/sha_ForensicHub.txt` 一致）。本次唯一新增固定版本证据是 C5 的 LICENSE
  文件（pinned txt + master API 交叉一致）。

### 2.3 权重可获得性及单独许可（W1 / L2）
- **W1 — C5（部分推进，未解除阻塞）**（R2）：
  - `aigc-folder.html` 的 folder id 与 pinned README 第 80 行
    "Checkpoints for AIGC Benchmark: … or https://drive.google.com/drive/folders/1M-qe5xOblVZgKiBQ9j1Q-GQ4ao5VJMHZ?usp=sharing"
    **逐字符一致**，页面为公开共享目录（文件状态 Shared、UI 含 Download 动作），
    列出 4 个 `application/x-zip` 文件（修改时间均 2025-09-11）：

    | 文件 | GDrive file id | 大小 |
    |---|---|---|
    | `dualnet.pth` | `1r0LXfGsO0_5xwg8z_qkTAFr8jrHx4bod` | 89.6 MiB (93,917,917 B) |
    | `hifinet.pth` | `1UjcM0IyPU0WIWOmD7Y0_zcRaZPXpLr_C` | 76.7 MiB（UI 显示值） |
    | `synthbuster.pth` | `15yiDWOaKuSDosS5-8Qjpk2Z9U7LnH9nW` | **11 KB（异常小）** |
    | `univfd.pth` | `1scHRBXvOnQgl0zHR5UO49qa5KSzYb8G6` | 1631.4 MiB (1,710,654,565 B) |
  - **按 ticket 规则：目录网页 HTTP 200 ≠ 权重可下载。** 本复核未执行任何下载，
    W1 维持 `unsatisfied_unverified`（存在性证据由"README 有链接"升级为"目录页存档
    + 逐文件 id/大小"）。Baidu NetDisk / OneDrive 渠道仍未测。
  - `synthbuster.pth` 11 KB 量级远小于常规 checkpoint，即使可下载其完整性/可用性
    也存疑 —— 列为 B1 跟进核实项。
- **L2 — C5（维持 unknown）**（R3）：目录页内无任何针对权重的许可/协议声明
  （页面中 "license/SPDX" 字样仅出现在 Google UI 代码自身的注释里）；按 ticket 规则
  **仓库 LICENSE 的 CC-BY-4.0 不自动覆盖独立分发的权重文件**，不得假定。
- **其余候选**：C1 维持 W1=存在性已实测（HF 44.16GB 清单，仍被 K1 排除）；
  C2/C3/C4/C6 维持未核实；C7 无权重（n/a）。

### 2.4 资源需求（K1/K2）
- **C5**（R5）：无官方数值。新数据点：`univfd.pth` 压缩 1.6 GB（解压权重 ≥1.6 GB），
  256px 输入下单模型推理"大概率"落入 20GB 显存/4GB 内存——仅为估计，按 skill 规则
  unknown 不得标为满足。README 指向 arXiv 2505.11003 的 hardware specifications
  （本次未获取，零新增请求）。K1/K2 维持 unknown。
- **其余候选**：维持 t2-audit（C1 K1=unsatisfied 实测；C7 K1=satisfied CPU-only）。

### 2.5 三分类覆盖（K8）
- **C5**（R6）：pinned README 证实四域（Deepfake/IMDL/AIGC/Doc）+ FIDL 跨域统一
  排行榜（Effort/Segformer-b3/Clip-ViT-L14/ConvNeXT/Mesorch/UnivFD/IML-ViT）；
  AIGC 域公开 checkpoint 目录已列出（§2.3）。但"域模型分数 → result∈{1,0_1,0_2}"
  （含"均未触发→1"）仍是**未经验证的组合**，按 ticket 明令不得假定满足约束。
  K8 维持 `partial_unproven`。
- **其余候选**：维持 t2-audit（均 proven_partial 或更窄）。

## 3. 阻塞条件变化

| ID | 前次审计 | 本次复核 | 依据 |
|---|---|---|---|
| B1 权重可下载性 | 未核实 | **未核实（存在性证据加强）** | §2.3；目录页 200≠可下载（ticket 规则）；synthbuster 11KB 异常 |
| B2 C5 代码许可 | unknown（raw 404） | **已解除：CC-BY-4.0 核实** | §1 字节级核验 + GitHub 分类器 |
| B3 显存/内存数值 | unknown | unknown（附 1.6GB 数据点） | §2.4 |
| B4 三分类映射 | unproven | unproven | §2.5 |
| B5 权重许可 | unknown | unknown（目录页亦无声明） | §2.3 |
| B6 starting-kit 不可达 | 维持 | 维持 | 无新证据 |

**状态：`blocked`；`selected_candidate_id=null`。**
C5 成为唯一 E1+L1 双满足且域覆盖最广的候选，但 W1/L2/K1/K2/K8 任一缺口按 skill
规则即"不能被选中"。

## 4. 失败与未解决条件记录

- GitHub API 固定 SHA 的 LICENSE 核验遇到未认证限流（`raw/pinned-license.json`，
  403）→ 改以 raw 通道 + master API 交叉字节比对完成，残留 caveat 见 §1。
- GDrive 单文件可下载性未实测（ticket 禁止下载）；hifinet.pth 精确字节数未从
  嵌入数据行提取（UI 显示 76.7 MiB）。
- `dualnet/hifinet/synthbuster` 与 pinned 代码中具体模型配置的对应关系未证实
  （仅 `univfd` 与 README FIDL 表 "UnivFD" 名称对应；pinned README 未枚举
  AIGC benchmark 模型名单，模型汇总文档页未获取）。
- 零新增网络请求；未下载权重；未执行比赛提交；未修改本目录两个产物之外的任何文件。

## 5. 自包含性

后续执行者凭本文件与同目录 `candidate_solutions.json` 即可：
定位规范（§输入）→ 理解前次审计与本次差异（§3）→ 复现全部字节级核验（§1 给出
sha256 与文件绝对路径）→ 执行解锁动作（B1 跟进中已列出 4 个 GDrive file id 与
建议的验证顺序）。
