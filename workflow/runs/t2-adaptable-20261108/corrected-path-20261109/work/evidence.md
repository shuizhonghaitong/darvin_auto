# TICKET-2 候选方案发现 — 证据记录（evidence.md）

- 运行身份：目标运行 Agent，仅 TICKET-2（独立方案发现与核验），未读取其他候选方案、历史运行日志或旧工程解法
- 规范输入：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json`（TICKET-1 产物，其 sources S1–S5 的原始抓取在 2026-11-08 完成，本 ticket 仅引用其中已固化证据，未重新抓取飞书）
- Skill 依据：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/.agents/skills/solution-discovery/SKILL.md`
- 时间窗口：2026-11-09 10:17–10:32 (UTC+8)

## 网络路线记录

所有出站请求均走免流代理 `http://172.28.4.16:18999`；`NO_PROXY=localhost,127.0.0.1,::1,172.28.0.0/16,10.0.0.0/8,192.168.0.0/16`（保留本机与内网直连）。**未使用**付费 mihomo `127.0.0.1:7589`，未下载任何 >20MB 文件。

| 时间(约) | 目标 | 路线 | 实际结果 |
|---|---|---|---|
| 10:19 | https://hf-mirror.com/ | 免流代理 | HTTP 200 |
| 10:19 | https://gitlab.4pd.io/gaoziming/image_authenticity_verification_leaderboard | 免流代理 | HTTP 200 |
| 10:22 | GitLab API 项目信息（gaoziming/image_authenticity_verification_leaderboard, id=13071） | 免流代理 | 200，default_branch=main，visibility=null（匿名可读） |
| 10:22 | GitLab API `repository/tree?path=starting-kit&ref=main` | 免流代理 | 200，6 个文件：.dockerignore/Dockerfile/build.sh/main.py/requirements.txt/start.sh |
| 10:22 | GitLab API `branches/main` | 免流代理 | 200，head commit `d22762ef44c8983a474e5079e1f4e22183b72c5d`（2026-09-18T11:59:11+08:00） |
| 10:24 | GitLab API 文件内容（ref=d22762ef）：Dockerfile、requirements.txt、start.sh、build.sh、.dockerignore | 免流代理 | 200，base64 解码成功 |
| 10:24 | 同上：starting-kit/main.py（file API） | 免流代理 | **404 File Not Found**（file API 异常） |
| 10:25 | 同上：starting-kit/main.py（raw URL `/-/raw/main/starting-kit/main.py`） | 免流代理 | **HTTP 200**，全文已保存 /tmp/sk_main.py 并核验 |
| 10:25 | GitLab API 仓库根 tree（ref=main） | 免流代理 | 200，见"starting-kit 内容"节 |
| 10:22–10:24 | HF mirror API 搜索：TamTam / TruFor / DIRE / fake+image+detection / UniversalFakeDetect（各 limit 8–10） | 免流代理 | 200，结果见"预训练候选核验"节 |
| 10:24 | HF mirror API `models/tamtam-lab/TamTam` | 免流代理 | 200，body `{"error": "Repository not found"}` |
| 10:24 | HF mirror API `models?author=tamtam-lab` | 免流代理 | 200，空列表（该组织在镜像上无可见模型） |
| 10:24 | api.github.com 搜索 "DIRE fake image detection" | 免流代理 | **失败：curl (28) 15s 超时无响应**（0 字节） |

## 关键事实与依据

### 1. 任务与指标（引自 competition_spec.json，S1/S2/S4/S5）
- 三分类：1=原生无修实拍图，0_1=已修图（人工+AI 局部），0_2=AI 全图生成；数据域：文档/风景/人物动物
- 排序指标 F1_0=(F1_0_1+F1_0_2)/2；1 类仅监测（accuracy、F1_1）
- 接口：POST /api/v1/image-authenticity {image_base64,image_format} → {success,message,result∈{"1","0_1","0_2"}}；GET /ready；0.0.0.0:80；linux/amd64 镜像
- 评测请求无图片 ID/文件名/真实标签，顺序随机（S4）
- 资源限制原文（S2 rev56）："1/2 A100-40g显存，2c4g"。本 ticket 按用户指令暂按 2 核 CPU / 4GB 内存检查，**未核实官方口径**（单位未注明，S1 仅要求"在规定资源范围内完成模型加载和推理"）
- 冲突 C1（评测失败判定：S1 零容忍 vs S2 失败率>5%）与 C2（镜像 vs 结果文件）均未裁定，沿用 spec 记录

### 2. 训练附件实际覆盖（S3 rev15，2026-11-08 抓取固化于 spec sources）
- `训练集 1 0_1.zip`：139,334,730 B，token `Ofj7bQtFMoe66fxcCGMc9pBSnug` → 标签 0_1
- `训练集 0_2.zip`：437,962,033 B，token `Hab7b2O8lo6LCaxXjaNc1jV5nQh` → 标签 0_2
- **标签 1（原生无修实拍图）无任何训练附件**（S3 未列出；spec unknowns 已记录"1 类训练数据缺失"）
- 本地可用性（本次实测，2026-11-09 10:20）：`find /mnt/disk3/liuyutong_home/workspace/darvin_auto -maxdepth 6 -name "*.zip"` → **无结果**；当前工作目录为空。附件未在本机落盘
- 附件内容（图片数/目录结构/真实标签分布）未解包核验；下载单文件 >20MB 按用户规则需确认，本 ticket 未下载

### 3. starting-kit 参考仓库（本次实测核验）
- URL：https://gitlab.4pd.io/gaoziming/image_authenticity_verification_leaderboard （项目 id 13071，匿名可读）
- 固定版本：main @ `d22762ef44c8983a474e5079e1f4e22183b72c5d`（2026-09-18）
- 根目录：`no-manual-annotation/`、`starting-kit/`、`subnet/`、`tests/`、`utils/`、README.md、run_for_darvin.py、Dockerfile、build.sh 等
- `starting-kit/` 为**参赛方 Mock 服务**（main.py 自述："服务是真的，数据是假的"）：Flask 实现，`POST /api/v1/image-authenticity`、`GET /ready`、监听 `0.0.0.0:${MOCK_SERVER_PORT:-80}`；预测=图片字节 SHA256 前 4 字节 %3 映射到 ["1","0_1","0_2"]，同一图片稳定但无真实判别力；文件内 TODO 指明参赛方应保留接口、替换为真实模型
- 已核验缺陷：`starting-kit/requirements.txt` 仅含 requests/Pillow/PyYAML，**未包含 flask**（main.py 依赖 flask）→ 骨架不能零修改直接构建运行，需补依赖
- 仓库根部的 run_for_darvin.py / Dockerfile 为 **Judge-Flow（评测方）** 模板（build.sh 镜像名 `judge-flow/...`，FROM harbor.4pd.io/inf/base-python3.8-ubuntu:1.1.0，pip 源 nexus.4pd.io），非 SUT；不可直接当作参赛镜像
- 注意：S4 文档将 starting-kit 表述为 SUT 参考，而仓库现状为 mock SUT + 评测方模板混合，以固定 commit 实测为准

### 4. 预训练候选核验（HF mirror，2026-11-09）
- 搜索 "TamTam"：无官方 tamtam-lab 命中；`api/models/tamtam-lab/TamTam` → Repository not found；`author=tamtam-lab` → 空。TruFor 官方权重在 hf-mirror 上**不可定位**
- 搜索 "TruFor"：`benjaik/trufor-ph2`（pytorch，license:other，0 下载）、`alastorid/TruFor-Swift-MLX`、`alastorid/TruFor-DnCNN-CoreML-FP16`（license:other）。均为第三方仓库，**非官方出处未核验**，license:"other" 无法由标签判断条款
- 搜索 "DIRE"：无权威仓库命中（结果多为无关项目）
- 搜索 "fake+image+detection"：多个小仓库（如 Emmawang/mobilenet_v2_fake_image_detection，15 下载，无 license 标签），规模/出处/许可均不满足核验要求
- 搜索 "UniversalFakeDetect"：空
- GitHub API 搜索（DIRE 原仓库定位）：超时失败，未核验
- 结论：本次**未核验到**任何可直接取得、许可清晰的 0_1/0_2 预训练检测器权重；外部预训练路线维持条件性候选

### 5. 环境信息（非候选）
- lark-cli 已核实路径：`/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/lark-cli-1.0.98/lark-cli`（用户提供的附件抓取工具；本 ticket 未用它新拉附件，附件清单引自 spec S3 固化数据）
- darwin CLI：`/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin`（spec S1 使用；本 ticket 未再调用）

## 失败与未解决条件
1. 附件 zip 未下载/未解包（>20MB 需用户确认）→ 0_1/0_2 训练数据规模与质量未知
2. 1 类训练数据无来源 → 三分类中"1"的判别依据缺失，影响 F1_0_1/F1_0_2 的误判率
3. `tamtam-lab/TamTam` 在 hf-mirror 不存在；GitHub 路线超时 → TruFor/DIRE 权重与许可 unknown
4. 2c4g / 1/2 A100-40g 官方语义未核实（仅用户授权暂按 2 核/4GB 检查）
5. 附件及派生权重许可条款未在任何已抓取来源中给出 → 许可 unknown（用户已授权附件用于训练，属本次使用授权，不等同于对外许可）
6. starting-kit main.py 经 GitLab file API 返回 404 但 raw 可取（工具怪癖，已用 raw 核验全文）；requirements.txt 缺 flask
7. 评测失败口径 C1、提交形式 C2 冲突未裁定（不影响方案发现，影响实现取舍）

## 下一步（供决策）
1. 用户确认后，经免流代理用 lark-cli 下载两个训练 zip（合计约 577MB），解包清点（数量/格式/目录/标签），验证附件授权范围
2. 决策 1 类数据来源：向主办方确认 / 自采真实实拍（需许可）/ 仅按 0_1-0_2 二分类+保守判 1 的策略设计
3. 若走 C1：选定基础模型并核验其权重许可（如 OpenAI CLIP、google ViT 等，届时逐项记录 commit/revision/license 原文），补 flask 依赖，实现真实推理替换 mock
4. 向平台/主办方核实 2c4g 与 1/2 A100-40g 的确切约束（加载/推理阶段、显存配额语义）
