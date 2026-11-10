# TICKET-2 候选方案检索证据 (solution-discovery)

- 生成时间: 2026-11-08 ~09:12 UTC (Asia/Shanghai 17:12)
- 输入规范: `runs/t1-real-20261108/competition_spec.json` (JSON 已验证可解析)
- 产物: `runs/t2-real-20261108/candidate_solutions.json` (JSON 已验证可解析) + 本文件
- 范围: 仅真实检索与候选比较；未复现、未下载权重/数据集、未训练、未提交
- 原始抓取件: 本目录 `raw/` (README/LICENSE 快照、GitHub Search API 响应 JSON)

## 1. 网络与代理

| 项 | 结果 |
| --- | --- |
| 环境代理 | `http(s)_proxy=http://127.0.0.1:7589` (mihomo, 计费路由)。本 Ticket 明确授权"使用环境中已配置的代理"，故采用该路由；仅做元数据/README 级小流量请求(单个 1–4KB)，无数据集/权重下载 |
| github.com 预检 | `curl https://github.com` → HTTP 200 (1.5s) |
| gitlab.4pd.io | 直连(走 NO_PROXY `*.4pd.io`)超时 25s；经 7589 代理亦超时 30s。**结论: 本环境不可达**，非静默重试 |
| huggingface.co | API 正常 (models/spaces 查询 HTTP 200) |
| api.github.com/repos (repo API) | 未认证 60/小时限额被代理出口 IP 耗尽 (HTTP 403 rate limit) → **回退** `git ls-remote HEAD` 固定 commit + `raw.githubusercontent.com` 抓 README/LICENSE，未再依赖 repo API |

## 2. 实际检索动作

### 2.1 GitHub Search API (8 组查询, 原始响应存 `raw/gh_search_*.json`, `raw/gh_search2_*.json`)

1. `AI generated image detection` (stars desc) → ant-research/Awesome-AIGC-Image-Video-Detection (488★), shilinyan99/AIDE (347★), lynote-ai/ai-image-detector (337★), YZY-stack/Effort-AIGI-Detection (241★), wyczzy/AIGI-Holmes (189★) 等
2. `image forensics detection` → mjkwon2021/CAT-Net (316★), RonyAbecidan/ManTraNet-pytorch (127★) 等
3. `image splicing detection` → minyoungg/selfconsistency, Sh1p-wy/RRU-Net 等
4. `manipulated image detection` → 多为小项目，无新增短名单
5. `TruFor` → grip-unina/TruFor (286★) 官方
6. `GIMM image` → 无官方仓库 (最高相关仅 8★ 无关项目) → GIMM 代码不可定位，未纳入候选
7. `ImageForensics` → HighwayWu/ImageForensicsOSN (149★)；`S-Lab-SCUT/ImageForensics` 直接 ls-remote 失败/不存在 → 采用 HighwayWu/ImageForensicsOSN
8. `DIRE image generators` → 无官方仓库直接命中 (仅经 NPR README 得知 github.com/ZhendongWang6/DIRE 为数据集仓库；未再抓取)

### 2.2 Commit 固定 (git ls-remote HEAD, 2026-11-08)

| 仓库 | HEAD commit |
| --- | --- |
| ant-research/Awesome-AIGC-Image-Video-Detection | f33ae84a4d5c1f9c69b29afcdf604c5786560057 |
| WisconsinAIVision/UniversalFakeDetect | 030495aea3300a8b54c0ec37ec7fe1dd7e63c619 |
| shilinyan99/AIDE | 6725b710d5c437ab2f59792908ce0377dfc907de |
| kartyg23/spai | b1b1422f2912594ba2620b311dde5d28a230d04c |
| YZY-stack/Effort-AIGI-Detection | 96f5dea2b534d400cfd7003f053c7e93c8e16461 |
| chuangchuangtan/NPR-DeepfakeDetection | 781ced3f7ca2cdc69ec9dd4ef27e8d0b3c07752a |
| chuangchuangtan/FreqNet-DeepfakeDetection | 2c6bd020cda1c0001e7a7d30ebd2dd5c55b5a8b6 |
| lynote-ai/ai-image-detector | d3f4976d36c59974a25f55a0a7850b9866d3223b |
| grip-unina/TruFor | ae54475df6f41a491d7615100feb19263dec13f7 |
| HighwayWu/ImageForensicsOSN | 42c2fe5611f39e0ebb3101c0c189b5b4b31440d3 |
| mjkwon2021/CAT-Net | 5eb85900b0e72423c95a8d41bc835b86c8671f8a |
| RonyAbecidan/ManTraNet-pytorch | 1af95cd4cfade7d22251be7abf0bebc0f9c199b0 |
| wyczzy/AIGI-Holmes | bae30b9e807230255a9f3fd18c9c64c08805b427 |
| hzlsaber/SIDA | 6b1c3aa9097a79849ea7aae95601854763014a9d |
| zhipeixu/FakeShield | b22717d7d524cbf617b8841d488d1edf56ceb7f3 |
| opendatalab/FakeVLM | fdcdcf111ecaff13ded65e32ce34d04cf876bc6f |
| minyoungg/selfconsistency | c173e6a24e2aa375317310718bd0ff1d8b4079ee |
| Sh1p-wy/RRU-Net | 288f62afb87c047039fb0e98c3a8f4139a692f95 |
| MatrixA/aicheck | 03cfb0b2c259261bd4720243f08d4dce9a3a5be9 (仅元数据, 未纳入候选: 元数据/水印路线, 与像素级鉴定任务不匹配) |
| S-Lab-SCUT/ImageForensics | NOT FOUND (ls-remote 失败) |

### 2.3 Hugging Face API (原始响应存 `raw/hf_*.json`, `raw/hf_space_npr.json`)

- models 搜索: `TruFor` / `ImageForensics` / `UniversalFakeDetect` / `AIDE` / `GIMM` / `fake image detection` / `DIRE image` → **无官方模型仓库**，仅社区移植 (TruFor CoreML/MLX、零散微调) → 候选权重基本只走 GitHub/Google Drive/Baidu
- spaces: `tancc/Generalizable_Deepfake_Detection-NPR-CVPR2024` → 存在, gradio, public, lastModified 2024-05-20 (NPR 可核验的公开推理入口；space 内权重文件未枚举)
- 结论: HF 不是本任务候选的主渠道

## 3. 关键结论 → 依据

| 结论 | 依据 (抓取文件) |
| --- | --- |
| UFD: MIT, 权重在仓库内, 线性头微调入口 | `raw/readme_WisconsinAIVision_UniversalFakeDetect.md` (validate.py/train.py 命令); LICENSE=MIT (2026-11-08 抓取); `pretrained_weights/fc_weights.pth` raw HEAD → HTTP 200 |
| AIDE: MIT 代码, Model Zoo 走 Google Drive | `raw/readme_shilinyan99_AIDE.md` ("Model Zoo ... drive.google.com/folders/1qx76UFv..."; Chameleon 数据集 NC+邮件); LICENSE=MIT |
| SPAI: Apache-2.0 (代码+权重), 权重 GDrive + MFM backbone | `raw/readme_kartyg23_spai.md` License 节与 Weights 节; LICENSE 文件存在 |
| Effort: 无 LICENSE 文件, README 徽章 CC BY-NC 4.0 → 商用风险 | LICENSE/LICENSE.md/LICENCE 全部 404 (2026-11-08); `raw/readme_YZY-stack_Effort-AIGI-Detection.md` 徽章 |
| AIGI-Holmes: 无预训练权重 (官方 ToDo 未勾) | `raw/readme_wyczzy_AIGI-Holmes.md` "Pre-trained model weights and download links [ ]" |
| TruFor: 非营利限定, Docker 推理 + 训练代码 | `raw/readme_grip-unina_TruFor.md` License 节 ("nonprofit purposes"); `TruFor_train_test/LICENSE.txt` 与 `test_docker/LICENSE.txt` raw HEAD → 200 (根目录无 LICENSE) |
| ImageForensics-OSN: MIT, 权重 GDrive/Baidu | `raw/readme_HighwayWu_ImageForensicsOSN.md` Note 1/2/3; LICENSE=MIT |
| CAT-Net: 权重 GDrive/Baidu(码 ycft), 无 LICENSE 文件 | `raw/readme_mjkwon2021_CAT-Net.md` Setup 节; LICENSE 探测 404 |
| ManTraNet-pytorch: 权重随仓库, 无 LICENSE, CPU 慢 | `raw/readme_RonyAbecidan_ManTraNet-pytorch.md` "Where are the pre-trained weights" / "N.B." 节; LICENSE 探测 404 |
| lynote/ai-image-detector: MIT, FastAPI 服务形态, 默认 UnivFD 后端 | `raw/readme_lynote-ai_ai-image-detector.md` (Model Choice / FastAPI 节); LICENSE=MIT |
| 排行榜指标只考核 0_1/0_2 (f1_0) | 规范 `task.ranking_metric` (S1+S2) → 决定"0_2 头 + 0_1 头 + 三分类融合"的候选架构视角 |
| 本地半成品: 三分类小 CNN + starting-kit 本地副本 + 三类别本地训练数据 | 本地文件: `image_auth_baseline/{Dockerfile,main.py,model/}`, `image_auth_repo/starting-kit/{main.py,serve_model.py,model_weights.npz,Dockerfile}` (端点 grep: /ready + /api/v1/image-authenticity), `datasets/image_auth/train_1_0_1/{1,0_1}` 与 `train_0_2/训练集 0_2/0_2` 目录结构, `RUN_RECORD_image_auth.md` (parity 4.77e-07、14 项 TCP 契约测试、val f1_0 0.7052、1182 图) |
| "训练集 1 0_1.zip" 本地解压含 1 类目录 → 1 类训练数据很可能在该 zip 内 | `datasets/image_auth/train_1_0_1/1` 目录存在 (本地证据；平台侧未证实) |

## 4. 失败与未解决条件

1. **gitlab.4pd.io 不可达** (直连 + 代理均超时): 官方 starting-kit 远端无法核验新鲜度；依赖本地副本 `image_auth_repo @ d22762e` 缓解。列入 blocking_conditions。
2. **GitHub repo API 限流** (未认证, 代理出口 IP 共享): 已用 git ls-remote + raw 回退解决；repo 级元数据 (stars/pushed_at 等) 仅在 Search API 结果中部分保留。
3. **Google Drive / Baidu Pan 权重链接未验证** (AIDE, SPAI, TruFor, CAT-Net, ImageForensics-OSN, FreqNet): Ticket 禁止下载权重；链接存在性已核 (README 文本)，可达性 = unknown。
4. **GIMM / DIRE 官方代码仓库未定位**: 搜索无命中；不作为候选 (避免凭名称臆断)。
5. **MLLM 组资源需求未验证**: 仅能依据架构定性 (大 VLM vs 20GB 共享显存 + 4GB CPU 内存)，按"未知资源需求不视为满足约束"处理 → 排除。
6. **比赛商用性质未知**: 影响 TruFor(非营利)/Effort(NC) 可用性；未擅自裁定。
7. **baseline Docker 架构未固定**: `python:3.11-slim-bookworm` 为多架构 tag, amd64 需构建时验证 (超出本 Ticket 范围)。

## 5. 候选比较摘要 (详见 candidate_solutions.json)

- **0_2 头排序**: UFD > AIDE ≈ SPAI > (Effort/NPR/FreqNet 因许可/权重未验证出局) > MLLM 组 (资源风险)
- **0_1 头排序**: ImageForensics-OSN (MIT) ≈ TruFor (Docker 推理 + 训练代码, 但非营利许可) > CAT-Net > ManTraNet
- **服务骨架**: 官方 starting-kit 本地副本 (契约精确匹配) > lynote/ai-image-detector (MIT, FastAPI, 需适配端点)
- **选定**: `local-starting-kit-baseline` — 唯一同时满足"可核验复现入口 + 资源获取条件 + 已知约束证据"的候选；开源候选作为复现阶段 (TICKET-3) 的升级路径记录在案
