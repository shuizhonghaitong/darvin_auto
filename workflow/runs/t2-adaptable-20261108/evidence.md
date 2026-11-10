# 证据记录 — 图片三分类 方案发现（solution-discovery）

- 生成时间：2026-11-08 22:31 (Asia/Shanghai)
- 工作目录：`/tmp/t2-independent-retry-eWUewO9a`（本次产物目录）
- 执行技能：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/.agents/skills/solution-discovery/SKILL.md`
- 总体状态：**blocked**（未选任何候选；详见 `candidate_solutions.json` 的 `blocking_conditions`）

## 1. 规范（CompetitionSpec）

无独立 spec 文件，规范内容来自本会话用户指令，已完整转录进 `candidate_solutions.json` 的 `competition_spec` 字段。要点：

- 任务：图片三分类 —— `1` 原生无修实拍 / `0_1` 人工或AI局部处理 / `0_2` AI全图生成；领域含文档、风景、人物动物。
- 数据：用户授权『训练集 1 0_1.zip』与『训练集 0_2.zip』用于本次比赛训练；内容未核实。
- 资源：两核 CPU、4GB 内存、半张 A100-40GB（需注明假设）。
- 约束：不读本地历史方案/旧工程；空目录产出；小流量检索、不下载大文件；阻塞也须尽快产出两文件。

## 2. 本地核验（实际执行，非推断）

| 检查 | 命令/方式 | 结果 |
|---|---|---|
| 工作目录内容 | `ls -la` | 仅 harness 文件（`.git`/`.agents`/`.codex`/`.aws`/`events.jsonl`/`stderr.log`），无训练附件、无历史方案 |
| zip 是否存在（/tmp，maxdepth 3） | `find /tmp -maxdepth 3 -iname '*训练集*'` | **未找到** |
| zip 是否存在（darvin_auto 工作区，全深度文件名匹配） | `find /mnt/.../darvin_auto -iname '*训练集*'` | **未找到** |
| 本地 Python 环境 | `python3 -c importlib` | Python 3.10.21（miniconda）；torch/timm/transformers/PIL 均未安装（仅 numpy 2.2.6）。此为本沙箱环境，**不能**代表比赛环境 |
| 技能目录 | `ls -R .../solution-discovery` | 仅 `SKILL.md`，无 schema/示例文件，无其他可参考资源 |

结论：B1（数据不可核实）成立——两个训练 zip 不在任何已检查位置，且未获得文件本体；三分类覆盖、数据规模与格式全部 unknown。

## 3. 网络核验（小流量，共 4 次诊断请求）

按用户全局偏好，先验证代理路由再产生流量。实际结果（均为 1 次小请求）：

| 路由 | 状态 |
|---|---|
| `http://172.28.4.16:18999`（已知免流量） | curl exit 7 `Couldn't connect to server` |
| `http://127.0.0.1:7589`（mihomo，计流量） | curl exit 7；`ss -tln` 显示本机**无任何 TCP 监听**（该沙箱内 mihomo 未运行） |
| `http://172.27.128.224:8234`（终端 env 的 `proxy`） | curl exit 7 |
| 直连 `--noproxy '*'` → api.github.com | curl exit 6 `Could not resolve host`（DNS 失败，沙箱无直连出口） |

判读（按用户偏好中"网络失败 vs 应用响应"准则）：ECONNREFUSED/DNS 失败均为网络/本地监听问题，未到达任何服务器，未取得任何外部页面数据。

结论：B2 成立。**本轮没有任何一次外部来源实测**（GitHub/HF/论文页均未访问成功）。因此 `candidate_solutions.json` 中所有 `fixed_revisions`、权重许可、可下载性字段均为 `unknown`；文中出现的版本/许可/体积数字均显式标注为"记忆/文档估计，未核实"，不作为证据。

## 4. 候选构思过程（先自主构思，后定向参考）

先仅依据规范独立构思，得到三条可执行路径 + 一条降级路径；开源项目仅在"需要核实组件许可/权重/入口"处被定向引用：

1. **C1（首选路径，自拟入口）**：预训练 backbone 微调 + 三分类头。理由：三分类任务结构与数据（类别目录 zip）天然匹配；资源需求（≤110M 参数）在假设的 20GB 半张 A100 与 4GB CPU 内存内可预期满足（文档估计）；backbone 库二选一（timm / HF transformers），权重来源二选一（timm hub / HF google/vit-base-patch16-224），最终选型待许可核验。入口 `train.py` 为待实现，未声称可复现。
2. **C2（外部组合）**：AIGC 检测（DIRE/UnivFD 系）+ 编辑检测（TrecTDE 2021 系）两段式映射三分类。定向参考原因：0_2 与"局部处理"正是这两个公开研究方向的任务。排除原因：权重访问路径（Google Drive、NIST 注册）与许可均无法核验；对"人工或AI局部处理"这一混合定义的覆盖无证据；组合决策规则需自拟且未验证。
3. **C3（外部基线/兜底）**：CLIP zero-shot / 冻结线性探针。保留原因：权重获取路径单一（HF）、资源需求最低，若 C1 的权重许可受阻可回退。排除主选原因：`1` vs `0_1` 依赖细微编辑痕迹，zero-shot 无有效精度证据。
4. **C4（自拟，不推荐）**：从零训练轻量 CNN。排除原因：有预训练权重可用时该路径预期更差更慢；仅作为"预训练权重全部不可得"的降级预案。

## 5. 逐项关键结论与依据

| 结论 | 依据 | 证据等级 |
|---|---|---|
| 训练 zip 不在本环境、内容 unknown | §2 find/ls 实测输出 | 实测（本地） |
| 本沙箱无网络出口，外部核验全部阻塞 | §3 四次 curl 诊断实测 | 实测（本地） |
| C1 入口为待实现，非已可复现 | 尚未编写/运行任何训练代码（技能要求：不做训练） | 事实陈述 |
| timm 代码 MIT / transformers 代码 Apache-2.0 / CLIP 代码 MIT | 记忆，**本轮未核实** | 未验证声明（unknown） |
| google/vit-base-patch16-224 权重 Apache-2.0、约 330MB；clip-vit-base-patch32 约 350MB | 记忆，**本轮未核实** | 未验证声明（unknown） |
| DIRE 代码许可（记忆 GPL-3.0 系）、权重经 Google Drive 分发；TrecTDE 数据为 NIST 研究用途条款 | 记忆，**本轮未核实** | 未验证声明（unknown） |
| C1 训练显存 <10GB、CPU 4GB 可覆盖预处理、CPU 推理百毫秒级 | 参数规模/模型类别的**文档估计**，非实测 | 估计（unknown 标记） |
| 半张 A100-40GB ≈ 20GB VRAM / 16 SM | 用户要求"注明假设"，采用 MIG 1g.20gb 类比 | 假设（未验证） |

## 6. 失败与未解决条件

- 失败：4 次网络诊断全部失败（§3）；2 次 zip 文件搜索均无结果（§2）。
- 未解决（阻塞，对应 JSON `blocking_conditions`）：
  - B1 zip 本体缺失、内容未清点（三分类覆盖前提）。
  - B2 网络出口不可用（外部版本/权重/许可无法实测）。
  - B3 评测协议缺失（指标/测试集/提交格式/推理硬件）。
  - B4 半张 A100 划分方式未确认。

## 7. 后续执行者需要的动作（自包含，不依赖本对话）

1. 按 JSON `next_actions` A1–A5 顺序执行。A1（zip 清点）与 A3（评测协议）不依赖网络；A2 的核验命令：
   - `curl -s https://api.github.com/repos/huggingface/timm`（取 `license`、默认分支），再 `.../commits/<branch>` 取 SHA；transformers、openai/CLIP、pqoq/DIRE 同理。
   - `curl -s https://huggingface.co/api/models/google/vit-base-patch16-224`、`.../openai/clip-vit-base-patch32`（取 `cardData.license` 与文件大小字段）。
2. B2 解除前，不要将本记录中任何"记忆"字段当作已核验事实使用。
3. 产物位置：`/tmp/t2-independent-retry-eWUewO9a/candidate_solutions.json`、`/tmp/t2-independent-retry-eWUewO9a/evidence.md`。
