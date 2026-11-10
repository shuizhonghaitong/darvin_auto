# TICKET-2 候选方案审计证据 — 图像真伪鉴定榜 (Darwin 196)

- 生成时间：2026-11-08 ~09:23 UTC
- 性质：**重审计（re-audit）**。基于已有检索证据逐项复核候选，严格执
  行 solution-discovery skill 的选择规则；**未做任何新检索、下载、复现或
  后续阶段操作**；**未修改 `runs/t2-real-20261108` 与 `runs/t2-real-retry-20261108`
  下的任何原始文件**。
- 输入规范：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json`
- 被审计记录：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-real-retry-20261108/candidate_solutions.json`（generated_at 2026-11-08T09:25:00Z，selected=C5-forensichub，status=completed）
- 证据来源：被审计记录 + 其 `evidence.md` + 其 `raw/` 目录（46 个原始抓取文件，本审计逐一复核了许可文件、复现入口文件、README 关键段落）
- 产物：本文件 + `candidate_solutions.json`（同目录）。`events.jsonl`/`stderr.log` 为本次 codex exec 会话日志，非审计产物。

## 1. 审计方法

- 判定刻度：`satisfied`（有证据表明满足）/ `unsatisfied`（有证据表明违反或合规风险不能排除）/ `unknown`（无证据，按 skill 规则**不得标为满足**）/ `proven_partial`（仅证实部分任务覆盖）/ `not_applicable`。
- 审计维度（对照 spec 全部已知约束 + skill 选择前置条件）：
  - `E1` 可核验复现入口（固定 SHA 下实际拉取的文件/命令）
  - `K1` 显存 ≤ 1/2 A100-40G（≈20GB）；`K2` CPU/内存 2c4g（spec 注明单位解读属 unknown 级）
  - `K8` 任务覆盖：三分类 1/0_1/0_2，排行指标 f1_0 仅考核 0_1/0_2
  - `W1` 必要权重获取条件**已核实**（公开发布且可达性验证）
  - `L1` 代码许可已核实且不妨碍交付；`L2` 权重许可已核实
  - `K3/K4/K5/K6/K7`（amd64 镜像、0.0.0.0:80+/ready、Ceph 挂载、base64 同步接口、失败零容忍兜底）：所有候选均为研究代码库，这些是**共同的服务化/复现阶段工作**，本审计不作为候选排除维度（见发现 F4）。
- 选择规则（skill 原文）：只有当至少一个候选具备**可核验的复现入口**和**资源获取条件**，并有**证据表明满足所有已知比赛约束**时才选择；否则 status=`blocked` 并列出具体缺失条件。"不能把未经验证的组件组合、改造或微调设想当作已证明覆盖比赛任务。"

## 2. 总体结论

| 项 | 原 t2-real-retry 记录 | 本审计 |
|---|---|---|
| selected_candidate_id | C5-forensichub | **null** |
| status | completed | **blocked** |
| blocking_conditions | 空 | **B1–B6**（见 §5） |

**没有候选满足严格选择标准。** 首选跟进核实对象仍为 C5-forensicHub 所在记录：C5-forensichub（E1 已核实 + 四域覆盖已证实 + 小 backbone），但其 W1 未核实、K1/K2 unknown、L1 经本审计复核降为 unknown、L2 unknown、完整三分类覆盖未证明 —— 按规则"不能被选中"。原记录的 selected 判定为**提前选择**（见 F1）。

## 3. 逐项审计矩阵（证据引用 raw/ 文件，均在被审计目录）

| 候选 | E1 入口 | K1 显存 | K2 内存 | K8 覆盖 | W1 权重获取 | L1 代码许可 | L2 权重许可 | 审计裁定 |
|---|---|---|---|---|---|---|---|---|
| C5-forensichub | ✓ satisfied（`forensichub_inference.py` 固定 SHA 拉取） | unknown（官方无数值） | unknown | partial_unproven（四域模型已证实；三分类映射为未验证组合） | ✗ 未核实（Baidu/OneDrive/GDrive 直链 raw README 证实存在，可达性未测） | **unknown**（原称 CC-BY-4.0 已核实，raw `lic_ForensicHub.txt`=404，见 F2） | unknown（README 未声明） | 不可选中；首选跟进 |
| C1-fakeshield | ✓ satisfied（cli_demo.sh + HF 清单） | **✗ unsatisfied**（HF 权重实测 44.16GB，`hf_fakeshield_tree.json`；文档化 FP16 路径 >40GB） | unknown（权重实测规模使 4GB 解读下推断不可行，无官方文档） | partial_unproven（三域 e-IFDL 已证实，映射需集成） | ✓ 存在性已实测（下载未执行） | ✓ Apache-2.0（`lic_FakeShield.txt` 11357B 全文） | ✓ apache-2.0（HF tag 实测） | 排除（K1 实测违反） |
| C2-trufor | ✓ satisfied（`trufor_Dockerfile` 等全套 raw） | unknown | unknown | proven_partial（1 vs 非1 二分类，**不区分 0_1/0_2**，而 f1_0 恰考核这两类） | ✗ 未核实（`grip.unina.it` zip 经 Dockerfile 证实含 MD5，可达性未测） | ✗ 非营利专有（`readme_TruFor.md` License 段原文），比赛用途合规性不能证实 | ✗ 同 L1 | 排除；许可可谈则备选（Docker 链路最现成） |
| C3-catnet | ✓ satisfied（`catnet_infer.py` + `catnet_requirements.txt`） | unknown | unknown | proven_partial（仅 0_1 家族；训练集无扩散全图） | ✗ 未核实（GDrive/Baidu 链接 raw README 证实，未测） | unknown（**无 LICENSE 文件**：LICENSE/.md/.txt 均 404，`lic_CAT-Net.md`/`lic_CAT-Net.txt` 为 404 占位；仅 README 声明 Apache-2.0） | unknown（README 声明 CC-BY 4.0，无文件） | 排除；0_1 备选 |
| C4-imdlbenco | ✓ satisfied（PyPI 0.1.45 实测，`pypi_imdlbenco.json`） | unknown（小模型估计） | unknown | proven_partial（IMDL 单域 0_1 家族） | ✗ 未核实（**仅 Baidu 单渠道**） | ✓ CC-BY-4.0（`lic_IMDLBenCo.txt` 37312B 全文） | unknown | 排除；0_1 备选/交叉验证 |
| C6-opensdi-maskclip | ✓ satisfied（`readme_OpenSDI.md` 含 test.sh/wget 命令） | unknown（ViT-B 估计） | unknown | proven_partial（0_2 扩散谱系 + 部分扩散类 0_1；**不覆盖 PS/滤镜 0_1 主体**） | ✗ 未核实（HF `nebula/MaskCLIP-weights` 与 MAE 直链仅路由级可达，仓库存在性未测） | unknown（未拉取） | unknown（HF 页面未核查） | 排除；0_2 交叉验证组件 |
| C7-aicheck | ✓ satisfied（`readme_aicheck.md`） | ✓ satisfied（CPU-only，无 GPU 权重） | unknown | proven_partial（窄：仅 0_2 边缘信号，依赖元数据留存，留存率 unknown） | n/a（无权重） | ✓ AGPL-3.0 已核实（`lic_aicheck.txt`）但**网络服务型交付的 copyleft 合规风险不能排除** | n/a | 排除；可选低成本 0_2 先验组件 |

## 4. 关键审计发现

### F1 原选择属提前判定（规则违反）
原记录 `selection_rationale` 以五条依据选中 C5，其中 (c)"公开发布的 checkpoint"仅证实**链接存在于 README**，未验证可达性（skill 要求"资源获取条件已核实"）；(d)"宽松代码许可（已核实）"被本审计推翻（见 F2）；且完整三分类映射"AIGC 分数→0_2、IMDL/Deepfake/Doc 分数→0_1、均未触发→1"是**未经验证的组件组合/微调设想**（skill 明文不得视为已证明覆盖）。原 `status=completed`、`blocking_conditions=[]` 与上述缺口互相矛盾。

### F2 C5 代码许可 raw 证据矛盾（本次审计新发现）
- 原记录：`code_license = CC-BY-4.0（LICENSE 文件已拉取核实）`，evidence.md §2 表格第 5 行亦记 "ForensicHub=CC-BY-4.0✓"。
- raw 证据：`raw/lic_ForensicHub.txt` 内容 = `404: Not Found`（14 字节）。
- 对照组（同批抓取）：`lic_FakeShield.txt` 11357 字节（Apache-2.0 全文）、`lic_IMDLBenCo.txt` 37312 字节（CC-BY-4.0 全文）、`lic_aicheck.txt` 725 字节（AGPL-3 头部声明）——均为真实许可文件。仅 C5 与 CAT-Net（后者记录中已如实标注 404）为 404 占位。
- README 中仅有 `shields.io/github/license` badge，其解析结果未被记录。
- 裁定：本 ticket 禁止重新检索，故 C5 `code_license` 降为 **unknown**，列入阻塞项 B2（需在任何复现/交付前核实固定 SHA 下的实际许可文件）。依据 AGENTS.md 3.2："不得仅凭文件名、代码存在或过往描述判断某项能力已经可用。"

### F3 其余声明复核成立
C1 权重 44.16GB（HF 清单）、C2 非营利许可与 zip MD5、C3 许可文件缺失、C4 CC-BY-4.0 与 PyPI、C6 权重命令、C7 AGPL —— 均与 raw 证据一致，排除理由维持不变。

### F4 共同服务化维度
K3/K4/K5/K6/K7 对全部候选均为复现阶段工作（无一候选自带 0.0.0.0:80 + /ready 的 amd64 服务镜像；C2 的 test_docker 最接近但入口非 HTTP 服务）。本审计不因此排除任何候选，但复现阶段必须完成，且失败兜底按 C1 冲突从严（任何样本必须返回合法 result）。

## 5. 阻塞条件（status=blocked 的具体缺失）

| ID | 缺失条件 | 涉及候选 | 优先级 | 跟进动作（需另行授权检索/实测） |
|---|---|---|---|---|
| B1 | 必要权重获取可达性未验证（仅链接存在性证实） | C5/C2/C3/C4/C6 | 1 | 从比赛构建环境实测直链可达性/分块下载，优先 C5 的 OneDrive/GDrive |
| B2 | C5 代码许可 unverified（raw 404，与记录声明矛盾） | C5 | 1 | 固定 SHA 92653068… 下核实实际许可文件及条款 |
| B3 | 显存 ≤20GB 无官方/实测数值 | C2/C3/C4/C5/C6 | 2 | 复现阶段单模型最小 checkpoint 实测显存与时延 |
| B4 | 完整三分类覆盖未证明（任何候选） | 全部 | 2 | C5 域模型 + 比赛 0_1/0_2 训练 zip 构建映射基线，实测 f1_0 |
| B5 | 权重许可未声明 | C4/C5/C6 | 3 | 随 B1/B2 核实 README/issue/HF 模型卡 |
| B6 | starting-kit 官方参考仓库不可达（原检索 direct+proxy 均超时） | 规范参考 | 3 | 复现阶段重试或向平台确认 |

## 6. 一致性与自包含性检查

- `selected_candidate_id=null` 与 `status=blocked`、B1–B6、各候选 unknowns 之间无矛盾。
- 每个候选的每个判定均引用 raw/ 文件或被审计记录中的可复现命令；不能证实的条件一律 `unknown`。
- 后续执行者无需本次对话上下文即可：定位规范（§输入规范）、定位被审计记录与 raw 证据（§证据来源，绝对路径）、理解判定依据（§3/§4）、执行解锁动作（§5）。
- 原始记录零改动：`runs/t1-real-20261108/*`、`runs/t2-real-retry-20261108/*`（含 events.jsonl、stderr.log、raw/）全部未写入。
