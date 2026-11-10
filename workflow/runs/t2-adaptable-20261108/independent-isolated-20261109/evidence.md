# TICKET-2 证据记录（独立运行 independent-isolated-20261109）

运行时间：2026-11-09（Asia/Shanghai）。终版。
隔离边界执行：未读取其他运行目录的候选方案/日志/旧工程解法（t2-* 目录下的 candidate_solutions.json、events.jsonl、REPORT.md 等均未打开；仅列目录名）。未运行 lark-cli；未读取认证目录/凭据（darwin_auto 根下 lark-*-qr.png、.aws 等未打开）。读取的比赛原始资料限于：competition_spec.json 及其 sources 列明的 raw_* 文件（t1-real-20261108 内）、用户授权的训练数据文件本身、任务指定的 starting-kit 公开仓库。
未做：训练、复现、大文件下载、提交（TICKET-3/4 范围）。

## 1. 任务与约束（来源：competition_spec.json + 本次补充实测）

- 三分类：1=原生无修实拍 / 0_1=已修图(人工/AI局部) / 0_2=AI全图生成；域：文字(文档)、风景、人物、动物。
- 主榜指标 f1_0=(f1_0_1+f1_0_2)/2；1 类不直接进主指标，但混淆伤害 0_1/0_2 的 P/R。
- 服务契约（S4/S5 与 starting-kit README 三方一致）：POST /api/v1/image-authenticity，请求 {image_base64(无 data: 前缀), image_format}，响应 {success, result∈{1,0_1,0_2}, message}；GET /ready；0.0.0.0:80；无 id/image_name 字段（不能依赖样本标识）。
- 部署资源（S2 原文"1/2 A100-40g显存，2c4g"，单位未官方注明）：本次按 1/2 A100(≈20GB VRAM)+2核CPU/4GB内存假设检查，**非已核实官方限制**；训练资源比赛未说明（unknown）。
- **新实测**（starting-kit 根 README @ d22762ef）：测试集 120 样本；任意样本重试耗尽后失败 → 本次评测 _score=0（与 S1 一致；S2 的 5% 口径为未裁定冲突 C1）。
- 提交：Docker 镜像（S1/S4/starting-kit 流程一致：darvin dataset upload → ref_id → deploy）；C2 冲突未裁定。

## 2. 网络路由实测（本次会话，实际代理+状态）

| # | 路由 | 目标 | 结果 | 用途 |
|---|---|---|---|---|
| 1 | 直连（NO_PROXY *.4pd.io） | gitlab.4pd.io | 失败 curl exit 28（20s 无数据） | 直连不通 |
| 2 | 免流 172.28.4.16:18999 | hf-mirror.com/ | 200（1.1s） | HF 元数据全部走此路 |
| 3 | 付费 127.0.0.1:7589 | github.com/ | 200（2.5s） | 许可核验走此路 |
| 4 | 免流 18999 | gitlab.4pd.io 仓库页 | 200（5.8s） | starting-kit 核验 |
| 5 | 免流 18999 | gitlab.4pd.io api/v4（project meta/tree/commits/files raw） | 200 | 固定 commit + 取文件 |
| 6 | 免流 18999 | harbor.4pd.io/v2/ | 401（5.2s） | 路由可达（registry 正常鉴权响应）；拉取权限 unknown |
| 7 | 免流 18999 | nexus.4pd.io pypi simple | 200（5.6s） | 内部 pip 源可达 |
| 8 | 付费 7589 | api.github.com/repos/* | 403（共享出口 IP 匿名限流）→ 改 raw.githubusercontent.com 成功 | 记录失败与替代 |
| 9 | 付费 7589 | raw.githubusercontent.com LICENSE 文件（CLIP/timm/transformers/pytorch/vision） | 200 | 仅 KB 级文件 |
| 10 | 付费 7589 | api.github.com/search/repositories（1 次） | 200 | 小型搜索 |
| 11 | 付费 7589 | pypi.org/pypi/Flask/3.0.3/json | 200 | license classifier |
| 12 | 免流 18999 | hf-mirror /api/models?search=* | 时 200 时返回 HTML 挑战页（镜像节流） | 搜索部分成功，已记录 |

环境现状：HTTP(S)_PROXY=127.0.0.1:7589（付费，监听已确认 ss -ltn）；NO_PROXY 含 localhost/127.0.0.1/172.28.4.0/24/*.4pd.io/172.28.4.3；proxy=172.27.128.224:8234（未使用，状态未知）。付费出口仅用于 #9-#11 的 KB 级查询，无大文件下载。

## 3. 训练数据核验（用户授权附件；本地副本零流量核验）

- 位置：/mnt/disk3/liuyutong_home/workspace/darwin_auto/datasets/image_auth/（2026-11-03 下载/解压；本次未重新下载）
- 大小与 S3 飞书文档附件元数据逐字节一致：train_1_0_1.zip=13,933,470B（"训练集 1 0_1.zip"）、train_0_2.zip=437,962,033B（"训练集 0_2.zip"）；testzip 无坏块
- SHA256（2026-11-09 本地计算）：
  - train_1_0_1.zip = b540fa9d90e1026dea4223cac23041251f6515c5aa5610025db0c74ea82144a8
  - train_0_2.zip = 3f10c7a8bb4e7b1d93ba1ea0555cf4231988dd947d17b3170829dc76589d9253
- 结构（目录即标签；文件名 MD5 风格；含 __MACOSX/.DS_Store 垃圾需剔除）：
  - train_1_0_1.zip：`0_1/{人物,动物,文字,风景}/` 100×4=400 张；`1/{人物,动物,文字,风景}/` 100×4=400 张
  - train_0_2.zip：`训练集 0_2/0_2/{人物,动物,文字,风景}/` 100×4=400 张
  - 格式合计：jpg 1114 / png 68 / tiff 18 = 1200 张
- **关键结论**：spec 中"1 类训练数据 unknown"解除——"训练集 1 0_1.zip"同时含 1 类与 0_1 类；三类标签、四域覆盖完整（400/400/400）。
- 限制：结构与计数核验 ≠ 每张图标注正确性（无法逐张人工验证）；样本量小（每类 400），训练充分性待 TICKET-3 实测；数据正式许可条款 unknown（用户授权本任务训练使用）。
- 备注：核验中一次瞬时 FileNotFoundError（train_1_0_1.zip），重试恢复，不影响结论。

## 4. starting-kit 仓库核验（免流代理 → gitlab.4pd.io，公开只读 API）

- 仓库：gaoziming/image_authenticity_verification_leaderboard（project id 13071），**固定 commit d22762ef44c8983a474e5079e1f4e22183b72c5d**（main，2026-09-18，全仓仅 3 commits，末次活动 2026-09-18）
- 结构：
  - `starting-kit/`：参赛方 SUT mock 服务——main.py（Flask；/api/v1/image-authenticity 按输入哈希生成假标签，文件内 TODO 明示替换为真实模型；/ready 返回 "True"；0.0.0.0:80，MOCK_SERVER_PORT 可配）、requirements.txt（Flask>=2.3.0）、Dockerfile（FROM harbor.4pd.io/lab-platform/inf/python:3.9；pip -i nexus.4pd.io）、start.sh（python3 main.py）、build.sh（--platform linux/amd64 构建+推送 harbor-contest.4pd.io/gaoziming/sut/...）
  - 根 README.md：任务/标签/指标/接口/评测规则（120 样本零容忍）/部署流程
  - 根 Dockerfile：Judge-Flow 评测镜像（主办方侧，FROM harbor.4pd.io/inf/base-python3.8-ubuntu:1.1.0）
  - tests/：6 个 pytest（call_inference/failure_branch/main_failure_path/security/starting_kit/timeout_resolution）——TICKET-3 可用
  - utils/：file/logger/request 辅助
- 许可：仓库**无 LICENSE 文件**（tree 实测未见），README 未声明 → 代码许可 unknown；接口契约与 mock 骨架属任务指定资料（S4 直接引用），复用契约/骨架合理，逐字复制代码的许可状态未确认。
- 结论：starting-kit 只提供**推理服务骨架**（mock 标签），不含训练代码与模型 → 训练入口必须自拟（各候选均标"待实现"）。

## 5. 模型/权重/许可核验（免流代理 → hf-mirror API；付费代理 → raw LICENSE，均小流量）

| 资源 | 固定版本 | 许可（证据） | 大小（实测） | 结论 |
|---|---|---|---|---|
| facebook/dinov2-base | main@f9e44c814b77203eaa57a6bdbbd535f21ede1415 | apache-2.0（HF cardData） | model.safetensors 346.3MB | **C1 主权重**：单塔视觉编码器，监督微调最干净路径 |
| google/siglip-base-patch16-224 | main@7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed | apache-2.0（HF cardData） | model.safetensors 812.7MB（双塔） | C1 备选权重 |
| openai/clip-vit-base-patch16 | main@57c216476eefef5ab752ec549e440a49ae4ae5f3 | MIT（openai/CLIP 仓库 raw LICENSE；HF 卡片无 license 标记） | pytorch_model.bin 598.6MB | C1 备选 + C4 zero-shot 权重 |
| Medsa/ai-image-authenticity-detector (TruthLens) | lastModified 2026-03-07 | **unknown**（卡片无 license；0 下载/1 like） | detector_scripted.pt 15.2MB + improved_detector_weights.pt 15.1MB | 仅二分类 FAKE/REAL、32×32 输入 → 不能覆盖 0_1/0_2 区分（C3） |
| Minteena/image-authenticity-model | — | unknown | 无权重（0 下载，占位） | 排除 |
| HF 搜索（image authenticity / aigc / ai generated image / deepfake / image forensics / image manipulation） | — | — | — | 未发现带许可的现成 1/0_1/0_2 三分类模型 |
| GitHub 搜索 "image authenticity detection"（1 次） | — | — | — | 436 repo，多为学术拼贴/篡改检测，无直接匹配的三分类鉴伪开源方案（未逐一核验，记录检索事实） |

依赖库许可（raw LICENSE / PyPI 元数据实测）：PyTorch BSD-3-Clause、torchvision BSD-3-Clause、transformers Apache-2.0、timm Apache-2.0、Flask BSD（PyPI classifier "OSI Approved :: BSD License"，GitHub LICENSE 路径 404 已记录）。
torchvision 预训练 checkpoint 的**权重条款**未逐一核验（C2 partial unknown）；download.pytorch.org 可达性未探测（C2 unknown）。
Docker 基础镜像 harbor.4pd.io/lab-platform/inf/python:3.9：内网工件，许可 unknown，拉取可行性待 TICKET-3（/v2/ 路由已通）。

## 6. 部署资源评估（暂定假设：2c4g 主机 + 1/2 A100-40g，未实测）

- DINOv2-base：346MB 权重（fp32）→ 推理峰值估计 1.5-2.5GB（GPU 或 CPU 单实例），对 4GB RAM/20GB VRAM 有数量级余量；2 核 CPU 单张推理估计秒级（监控指标 avg_response_time_ms 无硬性文档限值）。
- 结论：**估计可行、未实测**（本 ticket 不构建/不运行服务）。按 skill 要求区分"文件大小（实测）/文档估计/实际峰值（无）"，实际峰值留待 TICKET-3。

## 7. 失败、未知与未解决项

失败/受限：直连 *.4pd.io 超时（改免流代理成功）；api.github.com 匿名限流 403（改 raw 成功）；hf-mirror search 端点间歇 HTML 挑战（节流，换词部分成功）；timm/mobilenetv3_large_100.in1k 仓库 404（名称不存在，C2 权重改用 torchvision 路径，可达性未探测）；本地一次瞬时 FileNotFoundError（重试恢复）。

未知项（如实保留）：
- 数据正式许可条款（用户授权本任务训练使用 ≠ 正式条款）；平台 dataset(1) 内容（CLI 无只读列举）
- 2c4g 单位与是否为硬性官方限制（S2 原文未注明；按暂定假设检查）
- 测试集 120 样本的类别/域分布（README 仅给总数）；0_2 训练样本生成源分布是否与测试集一致（无法核验）
- starting-kit 代码许可（无 LICENSE 文件）；TruthLens 权重许可
- harbor 基础镜像拉取权限；docker build 在目标环境的行为
- 冲突 C1（评测失败口径，README 倾向 S1 但未平台终裁）与 C2（提交形式）未裁定
- 截止时间/提交次数限制（来源未提供）

## 8. 最终判定

- selected_candidate_id = **null**；status = **blocked**（发现工作完成；按 skill 选择规则不能选中——核心任务覆盖与部署资源符合性在"禁止训练/复现"的 ticket 边界内不可实测，"未经验证的微调设想不得当作已证明覆盖任务"）。
- 推荐路径（供 TICKET-3 直接执行，全部构件已固定）：**C1** = DINOv2-base（f9e44c8, Apache-2.0, 346MB，免流代理 hf-mirror 可达）+ 本地 1200 张三类数据（SHA256 已记录）+ 自拟 PyTorch 三分类微调（待实现，recipe 见 JSON）+ starting-kit @ d22762ef 服务骨架（契约已三方核验）。
- 降级备选：C2（轻量 CNN，权重可达性/许可部分 unknown）；对照基线：C4（CLIP zero-shot，无需训练）；C3（TruthLens）不建议采用（许可 unknown + 仅二分类）。
