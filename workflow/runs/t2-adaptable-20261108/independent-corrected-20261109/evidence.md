# TICKET-2 Evidence Log（独立方案发现）

- 运行目录: `/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-adaptable-20261108/independent-corrected-20261109`
- 时间: 2026-11-09（Asia/Shanghai）
- 规范输入: `/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json`（S1–S5，2026-11-08 抓取）
- 独立性: 未读取本次之外的候选方案/历史运行日志/旧工程解法。本地 `image_auth_repo` 工作树中的未提交修改与未跟踪文件（model_train/、serve_model.py、model_weights.npz、修改后的 starting-kit 文件等）判定为旧工程产物，**一律未读取**；仅使用该仓库 `origin/main`（= S4 官方参考仓库，pinned commit `d22762ef`）的 **committed 版本**文件。
- 流量: 本会话未发生任何对外下载/大流量；全部核验基于本地文件与离线 git 对象。

## 1. 任务与契约（来源: 规范 S1–S5 + 官方仓库 README @ d22762e）

| 事实 | 证据 |
|---|---|
| 三分类 1 / 0_1 / 0_2；domain=文档/风景/人物/动物 | 规范 S1/S2/S5（raw 记录于 t1 运行目录） |
| 排序指标 f1_0=(f1_0_1+f1_0_2)/2 | 规范 S1/S2；官方 README 一致 |
| **测试集 120 样本，零容忍失败（_score=0）** | 官方仓库 `origin/main:README.md`（103 行，已存 /tmp/README_startkit_ref.md）：“所有 120 个样本必须返回合法预测；任意样本在重试耗尽后仍失败，则本次评测无有效排行榜成绩” |
| 接口契约 POST /api/v1/image-authenticity {image_base64,image_format} → {success,message,result}；GET /ready；0.0.0.0:80；amd64 | 规范 S4/S5；starting-kit/main.py 实现逐字段对齐（已核验） |
| 评测不发送 id/image_name，须按内容判断 | 官方 README 注意事项 |
| 资源: 1/2 A100-40g 显存；"2c4g"（单位未明示） | 规范 S2；**2 核 CPU/4GB 内存为用户暂定解读，非已核实官方限制** |
| 冲突 C1（零容忍 vs 5%）、C2（镜像 vs 结果文件） | 规范记录未裁定；本方案按零容忍+镜像口径设计（S1 与官方 README 一致侧） |

## 2. 网络与代理核验（全部失败，记录具体错误）

环境探测（2026-11-09）:
- 环境变量: `HTTP(S)_PROXY=http://127.0.0.1:7589`（付费 mihomo）；`NO_PROXY` 含 `localhost,127.0.0.1,172.28.4.0/24,*.4pd.io,172.28.4.3`
- 结果（全部为出站失败，未产生对外流量）:
  - 免流代理 `172.28.4.16:18999`: `curl --proxy ... → (7) Couldn't connect to server`；`curl telnet://172.28.4.16:18999 → (7)`；无监听可达
  - 付费 `127.0.0.1:7589`: 无 mihomo 进程（ps 查无），`/proc/net/tcp` 无 7589/18999/8234/17890 监听；curl 经代理 → (7)
  - 直连: `curl --noproxy '*' http://114.114.114.114/ → (7) Couldn't connect`；`gitlab.4pd.io` DNS 解析失败（resolv.conf 为 tailscale 生成，100.100.100.100）
  - `lark-cli doctor`: `proxyconnect tcp: dial tcp 127.0.0.1:7589: socket: operation not permitted`（沙箱 EPERM 阻断出站 socket）；另有 token 存储只读文件系统警告
- 结论: **本会话沙箱阻断全部出站网络**；lark-cli 在线拉取/下载不可行；未切换路由（无可切目标）。在线核验项（live GitLab、Feishu 现行 revision、HF/GitHub、许可条款）全部记为 blocked，而非"不存在"。
- 未下载任何权重或附件（本地副本已存在，见 §3）。

## 3. 训练附件核验（关键未知项解除）

飞书附件元数据（规范 S3, rev 15 记录）:
- "训练集 1 0_1.zip" 139,334,730 B，token `Ofj7bQtFMoe66fxcCGMc9pBSnug`
- "训练集 0_2.zip" 437,962,033 B，token `Hab7b2O8lo6LCaxXjaNc1jV5nQh`
- S3 未列出第三个 zip → 规范 unknown "class 1 数据" 待解

本地副本核验（`/mnt/disk3/liuyutong_home/workspace/darwin_auto/datasets/image_auth/`，2026-11-03 落盘）:
- `train_1_0_1.zip`: 139,334,730 B **与飞书元数据逐字节一致**；sha256 `b540fa9d90e1026dea4223cac23041251f6515c5aa5610025db0c74ea82144a8`；`unzip -t` 无错误
- `train_0_2.zip`: 437,962,033 B **与飞书元数据逐字节一致**；sha256 `3f10c7a8bb4e7b1d93ba1ea0555cf4231988dd947d17b3170829dc76589d9253`；`unzip -t` 无错误
- （身份判据: 大小精确一致+完整性通过，视为同一附件；未在线比对 token 下载流，网络阻断）

`unzip -Z1` 目录清点（排除 __MACOSX/.DS_Store）:
- train_1_0_1.zip 内部顶层为 **`0_1/` 与 `1/` 两个类目录**，各含 人物/动物/文字/风景 ×100 → **class 1 数据存在（400 张）**；0_1 400 张
- train_0_2.zip 内部 `训练集 0_2/0_2/` 四域 ×100 → 0_2 400 张
- **三类覆盖: 1=400, 0_1=400, 0_2=400, 共 1200；四域（人物/动物/文字/风景）每类齐全**
- 文件名 "训练集 1 0_1" 的含义解释为同时含类 1 与类 0_1（有内容证据，属合理解释，非官方说明）

格式清点（PIL 逐文件实际格式）:
- class 1: 400 JPEG
- 0_1: 332 JPEG + 50 PNG + 18 TIFF
- 0_2: **400 全部 PNG 实际格式**（382 个 .jpg 后缀 → 后缀不可信）
- 推论: 服务必须按内容解码（PIL/cv2 from bytes），不可依赖 extension/image_format；测试集若含 tiff/后缀错位需兼容

已解压目录核对: `datasets/image_auth/train_1_0_1`（800 图）、`train_0_2`（400 图），与 zip 一致（排除 __MACOSX 后），TICKET-3 可直接用。
许可: 用户已授权用于训练（本 ticket 输入）；其他条款 unknown。

## 4. starting-kit 官方参考核验（pinned: origin/main = d22762ef44c8983a474e5079e1f4e22183b72c5d，2026-09-18 最后 fetch）

- 仓库 origin = `https://gitlab.4pd.io/gaoziming/image_authenticity_verification_leaderboard.git`（与 S4 引用一致）
- committed `starting-kit/` 仅 6 文件: `main.py, requirements.txt, Dockerfile, build.sh, start.sh, .dockerignore`；**无训练代码、无 README、无 LICENSE**
- `main.py`（committed）: Flask；POST /api/v1/image-authenticity（base64 校验→400；mock=SHA256%3 生成 ["1","0_1","0_2"]，注释明示"TODO 接入真实模型"）；GET /ready 返回 "True"；`MOCK_SERVER_PORT` 默认 80，host 0.0.0.0，threaded=True
- `requirements.txt`: 仅 `Flask>=2.3.0`
- `Dockerfile`: `FROM harbor.4pd.io/lab-platform/inf/python:3.9`；pip 源 `nexus.4pd.io`（内部）；EXPOSE 80
- `build.sh`: `docker build --platform linux/amd64`；push 目标 `harbor-contest.4pd.io/gaoziming/sut/image_authenticity_verification_leaderboard:0.0.1`
- 边界声明: 工作树存在本地未提交修改（M starting-kit/*.py 等）与未跟踪文件（model_weights.npz、serve_model.py、model_train/）——属旧工程解法，本次**未读取**；以上结论仅基于 origin/main committed 对象
- 未验证项: live GitLab 是否在该 commit 之后更新；harbor/nexus/harbor-contest 内部注册表可达性（网络阻断）

## 5. 本地权重与训练/推理环境核验

- 权重缓存: `runtime/torch-cache/hub/checkpoints/resnet18-f37072fd.pth`（46,830,571 B，sha256 `f37072fd47e89c5e...` 前缀与文件名一致）
- **离线加载验证通过**: `TORCH_HOME=...torch-cache` + `torchvision.models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)` 成功（无网络）；11.69M 参数
- 3 类头前向验证通过: `Sequential(*children()[:-1], Flatten(), Linear(512,3))` → (2,3)
- 实测: CPU 前向 ~10 ms/图（224px，batch1，未优化，venv-train 单进程；仅本环境参考值）
- `venv-train`: torch 2.14.1+cpu（cuda 不可用）/ torchvision 0.29.2+cpu / transformers 4.57.6 / Flask 3.1.3 / Pillow 12.3.0 / numpy 2.2.6 → **CPU-only 训练环境可用**
- `venv-ml`: pip 缺失（不可用，记录）
- 本地无其他预训练骨干缓存；更大骨干当前不可得（网络阻断）→ 不作为候选依赖
- 许可: torchvision/ImageNet 权重条款本会话未核验（离线），标 unknown

## 6. 资源约束对照（部署，暂定 2c4g + 1/2 A100-40g）

| 项 | C1(ResNet18) 需求 | 判定 |
|---|---|---|
| VRAM (≈20GB, 口径暂定) | 45MB 权重，fp32 前向余量极大 | 文档估计满足（未实测） |
| CPU 核 (暂定 2) | 推理单图 ~10ms（CPU 实测参考） | 估计满足（未实测吞吐） |
| RAM (暂定 4GB) | torch+Flask+模型 RSS 估计 ~1–2GB | 文档估计满足（**未实测**；2c4g 单位本身未证实） |
| 镜像架构 | build.sh 强制 linux/amd64 | 已核验 |
| 启动/就绪 | /ready + 端口 80 | 已核验（脚手架） |
| 零容忍失败 | 设计: 内容解码（PIL bytes）+ 任意异常兜底返回合法 result（success=true） | 设计项（待实现验证） |

注意: 上表"满足"均为文档估计/设计保证，**实测须由 TICKET-3 在部署环境完成**；"未找到超限≠证明合规"。

## 7. 候选比较结论

- **C1 选中**: 数据（三类齐全,已核验）、权重（本地可用,已核验加载）、服务入口（官方脚手架,pinned,已核验）、训练环境（已核验）四要素全部落地；训练脚本为待实现的小组件（自拟，输入/标签映射已完全确定），不声称端到端已复现。
- C2 级联: 条件性备选（0_1/1 质量不足时）；已核验基础同 C1，但复杂度与失败面更大。
- C3 脚手架: 已核验组件，并入 C1 使用；单独非完整方案（mock）。
- C4 现成公开检测器: 本会话网络阻断无法核验任何具体模型 → 保持 blocked 状态的方向，不进入选择。

## 8. 阻塞与下一步（交接 TICKET-3）

阻塞/未验证（非发现阶段阻塞，属复现阶段必须确认）:
1. 训练脚本实现 + 模型训练 + 本地验证集评估（三类均衡 1200 图，建议按域分层切分）
2. 2c4g 官方单位确认 + 部署容器 RAM/VRAM 实测
3. live 网络恢复后: 校验 GitLab 是否更新（diff starting-kit）、harbor/nexus 可达性、resnet18 权重许可条款、Feishu S3 现行 revision 是否仍为 2 个 zip
4. 失败兜底策略实现与 120 样本压测（任意畸形输入不得空返回）

本 ticket 产物: `CandidateSolutions.json`（selected=C1, status=selected, 含全部 pinned 哈希/commit）、`evidence.md`（本文件）。
