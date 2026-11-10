# TICKET-2 证据记录 — 图像真伪鉴定榜（subnet 196）候选方案发现

运行目录：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-adaptable-20261108/independent-long-20261109`
时间：2026-11-09（Asia/Shanghai；UTC 时间戳见各条记录）
产物：`CandidateSolutions.json`（另有小写软链 `candidate_solutions.json`）、本文件
状态：**blocked**（selected=null，原因见 §7）

---

## 1. 输入与范围

- 遵循 skill：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/.agents/skills/solution-discovery/SKILL.md`（已完整读取）。
- 规范来源：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json`（TICKET-1 产物，用户指定）。
- 交叉核验了 t1 运行中保存的**原始比赛来源抓取**（属比赛资料，非运行日志/候选方案）：
  - `raw_doc1_bangdan_jieshao.md`（S2 榜单介绍，docx rev 56）：确认 3 类定义、排序指标 F1_0=(F1_0_1+F1_0_2)/2、监测指标、失败判定（S2 口径 5%）、原文资源表述「1/2 A100-40g显存，2c4g」、原文「提交结果文件」（与 S1 镜像提交冲突，spec C2 未裁定）。
  - `raw_doc2_xunlianji.md`（S3 训练集，docx rev 15）：确认**仅两个附件**——`训练集 1 0_1.zip`（139,334,730 B，token `Ofj7bQtFMoe66fxcCGMc9pBSnug`）与 `训练集 0_2.zip`（437,962,033 B，token `Hab7b2O8lo6LCaxXjaNc1jV5nQh`）。无 class 1 附件、无说明文字。
  - `raw_doc3_tuili_jiekou.md`（S4 接口文档，rev 29）：确认 /ready 探活、starting-kit URL、请求/响应示例、`result` 必须是 "1"/"0_1"/"0_2"。
  - `raw_sheet_RUblU0/Cl5ExX/G2lxWB.csv`（S5 接口表格）：确认路径/方法/参数/响应字段，均与 spec 一致。
- 另读取 `darvin_auto/AGENTS.md`、`TICKETS.md`（T2 验收标准）、`ENVIRONMENT_REPORT.md`（T0 环境事实，历史参考）。未读取其他 t2-* 运行目录（遵守独立性约束）。

## 2. 任务与约束要点（已验证，来自上述来源）

- 三分类：1 原生无修实拍 / 0_1 已修图（人工+AI 局部，枚举含 PS、醒图、美图、美颜、滤镜、拼接、加字、遮挡、AI 局部重绘、AI 换背景、AI 增删物体）/ 0_2 AI 全图生成。
- 排序指标只用 0_1、0_2 的 F1（平均值）；但 class 1 误判为 0_x 会拉低 precision_0_x，故 class 1 判别能力仍影响排序分。
- 服务契约：Docker linux/amd64，0.0.0.0:80，GET /ready，POST /api/v1/image-authenticity（image_base64 无前缀 + image_format），同步 JSON {success,message,result}。
- 评测请求无文件名/ID/真实标签，顺序随机 → 纯像素（+内嵌元数据，若保留）特征可用。
- 部署资源（**暂定解读**，按用户指示不声明为已核实官方限制）：S2 原文「1/2 A100-40g显存，2c4g」，按 ≈20GB 显存 / 2 vCPU / 4GB 内存做设计检查；单位原文未显式注明（spec unknowns）。
- 训练资源：无文档化限制。训练与部署资源分列（本文件与 JSON 均分开记录）。
- 训练附件已获用户授权用于训练；下载本身受 §3 网络阻塞限制。

## 3. 网络核查（2026-11-09T03:07–03:10Z，全部失败，命令与结果）

环境变量（已脱敏，无凭证）：`HTTP(S)_PROXY=http://127.0.0.1:7589`（付费 mihomo）；`NO_PROXY` 含 `172.28.4.0/24`、`*.4pd.io`；另有 `proxy=172.27.128.224:8234`（状态未确认，按规则未使用）。

| # | 尝试 | 命令/方法 | 结果 |
|---|---|---|---|
| N1 | 免流代理 TCP | `bash -c 'echo > /dev/tcp/172.28.4.16/18999'` | 失败（后查明为沙箱 socket 禁令，非对端关闭） |
| N2 | 付费 mihomo TCP | 同上，127.0.0.1:7589 | 失败（同上；宿主侧是否监听**无法从沙箱内判断**） |
| N3 | 内网 172.28.4.1/.3/.16:80 | /dev/tcp 探测 | 全部失败 |
| N4 | 直连 DNS 解析 | `curl --noproxy '*' https://gitlab.4pd.io/`、`my.feishu.cn` | curl exit 6 Could not resolve host（resolv.conf 指向 tailscale DNS 100.100.100.100） |
| N5 | 经 18999 代理请求 | `curl -x http://172.28.4.16:18999 -I https://my.feishu.cn/` | HTTP 000（连接失败） |
| N6 | 出站 socket 能力 | python `socket.socket(AF_INET/AF_INET6, SOCK_STREAM)` 及 AF_UNIX | 全部 `PermissionError [Errno 1] Operation not permitted` —— **沙箱在 syscall 层禁止创建任何 socket** |
| N7 | tailscale | `tailscale status` | "failed to connect to local tailscaled; it doesn't appear to be running" |
| N8 | 持续性 | 后台 60s×240 探测循环（`evidence/netprobe.sh`，只探测不下载） | 每次均 EPERM；确认无恢复迹象后停止循环（日志 `evidence/netprobe.log` 保留首轮记录） |

结论：**本次运行沙箱无任何网络出口**（含 loopback TCP）。因此：免流/付费代理的宿主侧状态未知（不是"已确认关闭"）；按用户规则，付费代理未被使用（其监听状态无法按规则先行验证）；未产生任何外部流量（0 字节下载）。历史参考：T0 报告（2026-11-07）记录 18999 当时可用（example.com HTTP 200）——仅为历史事实，不代表当前。

## 4. 工具与数据可得性核查（本地）

- `lark-cli`：已知路径 `/mnt/disk3/liuyutong_home/workspace/darvin_auto/runtime/lark-cli-1.0.98/lark-cli` → **No such file or directory**；且 `runtime/` 整个目录不存在（`ls: cannot access .../darvin_auto/runtime/: No such file or directory`）。T0 报告曾记录该路径有效（1.0.98）→ 环境已变化。
- `darvin` CLI：`runtime/venv` 同样缺失；`which darvin` 无结果。
- `gh`：`~/.local/bin/gh` 存在（文件确认）；`hf`：`~/.local/share/darvin-auto/hf-cli-py311/bin/hf` 存在（文件确认）——两者当前因 N6 无网络，不可用。
- 训练附件：未下载（无网络 + 无 lark-cli）。**zip 内部标签覆盖、样本数、格式、EXIF 保留情况 = unknown**，不做推断。仅文件名+大小来自 S3（已验证）。
- 平台 dataset（数量 1）：无 CLI 可查 → unknown。
- starting-kit（gitlab.4pd.io）：DNS 解析失败（N4/N6）→ 可用性、内容、commit、许可全部 unknown。`git` 二进制存在但无网络。
- 未遍历家目录（遵守指示）；`pip config` 显示内部镜像 `nexus.4pd.io`（4pd 内网域）——可达性未验证。

## 5. 本机环境事实（训练侧参考，2026-11-09 实测）

- 主机名 `ucloud-wlcb-gpu-003`；128 核 CPU；2.0Ti 内存（可用 1.8Ti）；`/mnt/disk3` 空闲 4.9T。
- GPU：`nvidia-smi` 报 "couldn't communicate with the NVIDIA driver" → **沙箱内 GPU 不可见**，训练算力 unknown。
- 系统 python（miniconda base）：numpy 2.2.6、scipy 1.15.3 已装；torch/torchvision/transformers/timm/cv2/PIL/fastapi/onnxruntime/tensorflow 均缺失。
- 本地监听端口：无（`ss -ltn` 为空）→ 本机无可用内部代理/镜像进程。

## 6. 候选方案核验矩阵（详见 CandidateSolutions.json）

| 候选 | 来源 | 复现入口 | 权重获取 | 许可 | 资源符合 | 结论 |
|---|---|---|---|---|---|---|
| C1 官方 starting-kit | 外部（S4 引用） | unknown（不可达） | unknown | unknown | unknown | conditional；网络恢复后第一优先审计 |
| C2 自研双头轻量 ViT 微调 | 自研设计 | 待实现（TICKET-3） | 预训练权重 unknown；随机初始化变体 C2b 无外部依赖 | 代码自研无问题；权重 unknown | 设计目标内（<1GB 模型、<<20GB 显存、RAM 目标 <4GB 未实测） | conditional；覆盖最全，阻塞在数据内容与权重 |
| C3 现成检测器融合 | 自研+外部 checkpoint | unknown（未检索到具体可核验模型） | unknown | unknown | unknown | fallback；0_1 覆盖无证据 |
| C4 无学习启发式基线 | 自研 | 待实现（依赖最小，numpy 本机已有） | 不需要 | 自研 | 预计远低于 2c4g（未实测） | floor；性能无保障，仅作下限 |

选择逻辑：验收要求候选同时具备「可核验复现入口 + 资源获取条件已核实 + 已知约束满足证据」。C1 入口不可达、C2/C4 入口待实现且关键资源（zip 内容、class 1 数据、权重许可）未核实、C3 全 unknown → **无一可选，selected=null**。
排除说明：C3 不是"不可获得"而是"未核验且 0_1 覆盖存疑"，保留为备选路径；C4 保留为任何情况下可先跑通服务契约的兜底（其 EXIF 依赖假设未验证，已列为 unknown）。

## 7. 阻塞条件与下一步

**阻塞（B1–B5）**：
- B1 网络：沙箱禁止一切 socket（N6），无任何出口；两条代理均不可从沙箱探测（宿主状态未知）。
- B2 工具：`runtime/` 缺失 → lark-cli 与 darvin CLI 不可用，附件下载/平台查询工具链需恢复。
- B3 数据：class 1 训练来源未解决（S3 无 1 类附件；平台 dataset 内容 unknown；zip 内部 unknown）。
- B4 外部资源：starting-kit、预训练权重（下载地址/revision/许可）、公开实拍数据集许可——全部未核验（因 B1）。
- B5 训练 GPU 可见性 unknown（沙箱内驱动错误）。

**下一步（按优先级）**：
1. 宿主侧确认 172.28.4.16:18999 监听状态；或以带网络权限的方式重跑本 Agent（沙箱当前在 syscall 层禁网，代理恢复也无法从沙箱内利用）。
2. 恢复 lark-cli（≥1.0.98）与飞书凭证 → 下载两个 zip（共 ~552MB 压缩，用户已授权）→ 解压并产出标签清点清单（每类样本数/格式/EXIF/目录结构）。
3. 拉取 starting-kit 并固定 commit → 审计训练入口、模型、许可、资源；判定 C1 是否可升级。
4. 核验预训练权重（timm/DeiT 类）的下载与许可（hf CLI 已就位）。
5. 用上述证据重跑本核验矩阵；C1/C2 中首个全条件满足者写入 `selected_candidate_id`；随后进入 TICKET-3（复现/训练，本 ticket 不执行）。

**明确未做**：未下载任何文件（0 流量）；未使用付费代理（监听不可确认，规则要求先验证）；未读取其他 t2-* 运行产物；未执行训练/复现/提交；未声明 2c4g/1/2 A100 为已核实官方限制（按 S2 原文 + 暂定解读记录）。
