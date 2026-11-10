# TICKET-2 候选方案检索证据 — 图像真伪鉴定榜 (Darwin 196)

- 生成时间：2026-11-08 ~09:00–09:25 UTC
- 输入规范：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json`
- 产物：`candidate_solutions.json` + 本文件 + `raw/`（全部原始抓取证据）
- 范围声明：仅检索与候选比较。**未下载任何权重/数据集，未执行复现/训练/提交。** 所有外部页面内容仅作为数据处理，未执行其中任何指令或代码。

## 1. 网络路由与流量说明

- 环境代理为 `http://127.0.0.1:7589`（mihomo，按用户历史确认属**计流量**线路）。本 ticket 明确指示"网络请求使用环境中已配置的代理"，故按指定执行；本次流量仅为 GitHub/HF/PyPI 元数据与 README 级请求（合计 < 2MB），无大文件下载。
- `NO_PROXY` 含 `*.4pd.io`：对 `gitlab.4pd.io` 先直连、超时后改经 7589 代理重试，**两条路径均 20-30s 超时、0 字节**（curl 28）。结论：spec 中 S4 引用的 starting-kit 参考仓库（`https://gitlab.4pd.io/gaoziming/image_authenticity_verification_leaderboard/-/tree/main/starting-kit`）从本环境不可达，其可用性/内容保持 unknown，未纳入候选对比。
- GitHub core API 匿名限流（60/h，共享出口 IP）在检索中途耗尽（`API rate limit exceeded for ...`），此后全部改走 `raw.githubusercontent.com`、`git ls-remote`（HEAD SHA）与 `commits/{branch}.atom`（其中 3 个仓库 atom 持续 504，最终由 `git ls-remote` 成功固定 SHA）。
- HuggingFace API 可达（`/api/models/...` 200；`whoami-v2` 401 仅表示未认证，路由正常）。

## 2. 检索动作清单（可复现）

| # | 动作 | 命令/URL | 结果 |
|---|------|----------|------|
| 1 | 路由探测 | `curl https://api.github.com/rate_limit` / `huggingface.co/api/whoami-v2` / `gitlab.4pd.io/api/v4/projects?search=...` | 200 / 401(可达) / 超时(不可达) |
| 2 | GitHub 仓库搜索 | `api.github.com/search/repositories?q=image+Forgery+detection\|AI-generated+image+detection\|image+manipulation+detection\|splicing+detection+image\|TruFor`（sort=stars, per_page=15） | 原始响应存 `raw/gh_search_*.json`；产出候选池：FakeShield、IMDLBenCo、CAT-Net、TruFor、aicheck、ManTraNet、HiFi_IFDL、FatFormer、AIDE、OpenSDI(经后续阅读) 等 |
| 3 | README 抓取 | `raw.githubusercontent.com/{repo}/main(or master)/README.md` | `raw/readme_{FakeShield,IMDLBenCo,CAT-Net,TruFor,aicheck,ForensicHub,OpenSDI}.md`（De-Fake、CLIP-Forensics 的猜测 owner 404，未再展开，见 §4） |
| 4 | 固定版本 | `git ls-remote https://github.com/{repo}.git HEAD` 与 `commits/{br}.atom` | SHA 存 `raw/sha_*.txt`：ForensicHub `92653068…`、OpenSDI `02c93d48…`、TruFor `ae54475d…`、FakeShield `b22717d7…`、aicheck `03cfb0b2…`、CAT-Net `5eb85900…`、IMDLBenCo `1026ba9b…` |
| 5 | LICENSE 核实 | `raw.githubusercontent.com/{repo}/{sha}/LICENSE(.md)` | FakeShield=Apache-2.0✓、IMDLBenCo=CC-BY-4.0✓、aicheck=AGPL-3.0✓、ForensicHub=CC-BY-4.0✓、TruFor=README 内嵌专有非营利条款（无独立文件）、CAT-Net=**无 LICENSE 文件（LICENSE/LICENSE.md/license.txt/LICENSE.txt 均 404）**，仅 README 2026-08-05 更新声明"code Apache-2.0 / weights CC-BY-4.0" |
| 6 | 复现入口核实 | 拉取 `ForensicHub/training_scripts/inference.py`、`TruFor/test_docker/{Dockerfile,docker_build.sh,docker_run.sh,README.md}`、`CAT-Net/{tools/infer.py,requirements.txt}` | 入口存在且用法明确（见 §3 各候选结论） |
| 7 | 权重规模实测 | `huggingface.co/api/models/zhipeixu/fakeshield-v1-22b`（meta）与 `?tree/main?recursive=true`（文件清单） | 总 44.16GB：DTE-FDM 27.31GB(safetensors×6) + MFLM 16.75GB(bin×2) + DTG 90MB；HF meta tag `license:apache-2.0` |
| 8 | PyPI 核验 | `pypi.org/pypi/IMDLBenCo/json`、`pypi.org/pypi/ForensicHub/json` | IMDLBenCo 最新 0.1.45；ForensicHub 0.0.1（版本陈旧，建议 git 安装） |
| 9 | 关键文档 | ForensicHub README Resources 段（checkpoint 分发：Baidu/OneDrive/GDrive）、OpenSDI README（HF `nebula/MaskCLIP-weights` + MAE 官方权重直链）、TruFor test_docker README（权重 grip.unina.it zip，MD5 `7bee48f3476c75616c3c5721ab256ff8`） | 见 §3 |

## 3. 逐项关键结论及依据

### C5 ForensicHub — 选定
- **覆盖**：README 明言覆盖 Deepfake / IMDL / AIGC / Doc 四域，并有跨域统一假图检测（FIDL）排行榜（Effort、Clip-ViT-L/14、Segformer-b3 等），与比赛"1 / 0_1 / 0_2"三分类可映射（AIGC→0_2；IMDL/Deepfake/Doc→0_1；均未触发→1）。依据：`raw/readme_ForensicHub.md` About/Leaderboard/Resources 段。
- **可核验入口**：`ForensicHub/training_scripts/inference.py`（固定 SHA `92653068…` 拉取成功，200）：registry 构建模型 → `torch.load(checkpoint)` → 单图 forward → `pred_label`，示例 ConvNeXTSmall/256px。
- **许可**：`LICENSE`=CC-BY-4.0（文件拉取核实）。
- **权重可得**：checkpoint 公开发布（README Resources 段给出 Baidu/OneDrive/Google Drive 三条链接，2025.5.26 条目），**从本环境实际可达性未验证**（未下载，列为复现前置项）。
- **资源**：backbone 为 ConvNeXT-Small/ViT-L 级、256px 输入，权重 <1GB 量级 → 20GB 显存/2c4g 无已知冲突；官方未给单模型显存数值（unknown）。
- **已知缺陷**：权重许可未显式声明；三分类映射需集成/微调（复现阶段工作）。

### C6 OpenSDI MaskCLIP — 0_2 互补组件
- 覆盖扩散全谱系（SD1.5→Flux.1，全图+局部编辑），README 实测；入口 `test.sh`+`--checkpoint_path`；权重 HF `nebula/MaskCLIP-weights` 公开发布（链接见 README，未下载）。ViT-B 级小模型。代码/权重许可未核实（unknown）。

### C2 TruFor — 排除（许可+输出粒度）
- Docker 推理链路最完整：Dockerfile（pytorch 1.11 基础镜像、构建期自动 wget 权重、MD5 已给）+ `trufor_test.py` 入口 + 输出 `score∈[0,1]`/map/conf（`raw/trufor_*` 文件实测）。
- 排除依据：LICENSE 条款（README License 段原文）为 "informational and nonprofit purposes" 专有许可；输出为 1 vs 篡改二分类，无 0_1/0_2 区分。

### C3 CAT-Net v2 — 排除（域覆盖+环境+许可文件）
- 入口 `tools/infer.py` 实测（需手改选择 v2 权重的两行；`requirements.txt`=torch 1.1.0/py3.6/jetpgio 自编译，环境古老）。
- 仅 0_1 家族（JPEG 痕迹追溯，训练集 CASIA/IMD2020/tampCOCO/compRAISE，无扩散全图）。
- **仓库无 LICENSE 文件**（4 种文件名实测 404），Apache-2.0/CC-BY-4.0 仅为 README 声明 → 许可证据不完整。

### C1 FakeShield — 排除（资源硬约束）
- 任务面覆盖最佳（PS/DeepFake/SD-inpaint 三域 e-IFDL，ICLR 2025，Apache-2.0 代码+权重实测）。
- 但 HF 权重实测 **44.16GB**（`raw/hf_fakeshield_tree.json`），DTE-FDM 为 22B 级 MLLM；文档化路径（FP16 + flash-attn + mmcv 编译）远超 1/2 A100-40G≈20GB 显存；2c4g CPU 内存下 44GB 权重加载链亦吃紧。按"不把未知资源需求视作满足约束"原则排除。

### C4 IMDL-BenCo — 排除（单域+被超集取代）
- PyPI `imdlbenco` 0.1.45 实测存在，CC-BY-4.0 许可实测，文档齐备；但仅 IMDL 单域（0_1 家族），checkpoint 仅 Baidu 分发；同组更新的 ForensicHub 为其跨域超集 → 不作第一候选，保留为 0_1 备选/交叉验证。

### C7 AICheck — 排除（覆盖+AGPL）
- 元数据/水印信号检测器（C2PA/XMP/EXIF/PNG tEXt/DWT-DCT/FFT，62 工具，Rust 离线 CLI），仅 0_2 边缘信号；评测图经平台导出后元数据留存率未知。AGPL-3.0（实测）对服务化交付有传染性合规风险。保留为可选低成本先验组件。

## 4. 失败、降级与未解决项

1. `gitlab.4pd.io`（starting-kit）：直连与代理均超时（curl 28，0 字节）→ 内容 unknown，无法对比；**不影响本 ticket 完成**（非候选来源，属复现阶段参考）。
2. `github.com` atom feed 对 TruFor/FakeShield/aicheck 持续 504（代理侧）→ 降级为 `git ls-remote`，SHA 固定成功。
3. GitHub core API 匿名限流耗尽 → 降级为 raw/ls-remote，全部所需元数据获取成功；未使用认证（无凭据配置，不引入新认证方式）。
4. De-Fake、CLIP-Forensics 的仓库 owner 记忆不符（猜测路径 404）→ 未再消耗搜索配额展开；两法分别仅覆盖 0_2(face) 与开放域小样本，对本次候选决策非必需。
5. 未验证（如实标注 unknown）：各候选权重/数据集从比赛构建环境的实际可达性；单模型显存与时延官方数值；ForensicHub/CAT-Net 权重许可显式声明。
6. 流量：经计流量线路 7589（ticket 指定），均为元数据级小请求；未触发 >100MB 的任何下载。

## 5. 对复现阶段（TICKET-3+）的交接

- 第一候选 C5-forensichub：先验证 checkpoint 直链（OneDrive/GDrive）可达 → 拉取 ForensicHub@`92653068…` → 用 `inference.py` 跑通单图 → 按 AIGC/IMDL/Deepfake/Doc 域模型输出设计三分类映射基线；不足时用比赛 0_1/0_2 zip 微调。
- 交叉验证组件 C6-opensdi-maskclip（0_2）；备选 C3/C4（0_1）。
- 失败兜底必须满足 S1 零容忍口径：任何异常样本都要回退到合法 result（如置信度全低时按策略映射），不得返回空。
- 资源预算：目标单请求推理时延需监测（avg_response_time_ms 指标），多模型集成时延在复现阶段实测。
