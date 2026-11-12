# 运行摘要 — 图像真伪鉴定榜 (subnet 196) 端到端独立实验

**运行目录**：`runs/independent-196-20261111-new`（本次全部产物）
**时间**：2026-11-11 21:38 → 2026-11-12 02:0x CST
**技能依据**：`workflow/.agents/skills/darwin-workflow/SKILL.md`（+ competition-intake / solution-planning），T1–T6 全链路。

## 状态总览（三项分别报告）

| 状态 | 结果 |
|---|---|
| Agent 运行 | **完成**：T1–T6 全部阶段执行完毕，产物与证据齐全；按 45 分钟授权窗口规则于 01:58 CST 停止 |
| 提交被接受 | **未提交**（未获得用户授权文件 approval.json，遵守"最多提交一次/未授权即停"规则） |
| 评测完成 | **未发生**（依赖提交，未提交故无平台评测） |

## 各阶段实际执行

- **T1 需求理解**（`t1-intake/`）：darwin CLI（0.5.2, prod）`subnet show/inspect 196`、飞书 3 篇文档（rev 56/15/29）、评测 helm chart（OSS 直连 8.4KB）、官方仓库克隆（commit d22762ef，经免费代理）。产出 `competition_spec.json` + `evidence.md`。关键冲突（失败判定 5% vs 任意失败即无效）按平台实际执行代码一侧实现并记录；接口 sheets 表格因 scope 缺失未核验（bot 99991672；user 身份沙盒内不可刷新，证据见 evidence.md §5）。
- **T2 方案规划**（`t2-planning/solution_plan.json`）：ResNet-18 微调（本地缓存 ImageNet 权重零下载）→ CPU 推理服务（torch 2.6.0+cpu 离线 vendor）；本机无 GPU 实测确认；平台 2c4g/vGPU 对齐策略。
- **T3 可运行方案**（`t3-solution/`）：1200 张（缓存核验一致）900/300 分层，12 epoch 训练 **3.9 分钟**，best=epoch9，val **f1_0=0.8056**（acc 0.77；f1_0_1=0.7658, f1_0_2=0.8454）；全链路推理 55.5ms/张（128 核本机）；异常解码兜底验证。`VALIDATION.md` + `train.log`。
- **T4 服务**（`t4-service/`）：Flask `main.py`（0.0.0.0:80，`/ready` 加载期 503→200，`POST /api/v1/image-authenticity`，异常兜底恒返回合法标签）+ 无参数 `start.sh`；容器 `--cpus 2 -m 4g` 模拟平台：6s 就绪，3/3 真实图分类正确（2.4–3.6s/张），截断/非图片 base64→200 兜底，空参→400（judge 不会发送）。`VALIDATION.md`。
- **T5 镜像**（`t5-image/`）：唯一新 tag `…image_authenticity_verification_leaderboard:20261111-independent-new`（push 前 registry 确认不存在）；`DOCKER_BUILDKIT=0` 离线构建（buildx 状态目录在只读 home → 记录失败证据）；push 成功；远端 digest 三处一致核验：
  - manifest digest `sha256:2d2793dbf17f7542d17327fd18621d46f4b9bf6ad06b20fe0e521fbad5487ff8`
  - `docker buildx imagetools inspect`（registry-only）/ `manifest inspect`（tag 与 digest）均 OK。
  `image_manifest.json` + `build.log` + `push.log` + `evidence.md`。
- **T6 提交准备**（`t6-submission/`）：`solution.yaml`（training_image 按 digest 固定）+ `values.yaml`（repository+tag）；`darwin solution precheck` = **10 check(s), 0 blocking**（quiz=unverified：scientist 端点 401 "Login expired"，CLI 源码确认 unverified 不阻塞 submit；points 由后端提交时确认）。`approval-request.md`（run 根目录，含精确 tag/digest 与全部验证结论）于 01:06:32 写入；轮询 approval.json 至 01:58:23（>45 分钟窗口）未出现 → **不提交**，`approval-wait.log` 记录。

## 复用与未复用（如实声明）

- **复用（通用/缓存，均已本次实测验证）**：darwin CLI 0.5.2、lark-cli 1.0.98、基础镜像 `harbor.4pd.io/lab-platform/inf/python:3.9`（本地缓存）、训练集缓存（大小与飞书文档逐字节一致）、ImageNet resnet18 预训练权重缓存、harbor-contest docker 登录态、历史 run 的**工具路径与接口契约线索**（仅作定位参考，未复用其产物）。
- **未复用（按用户禁令）**：历史比赛 spec/plan、任何历史模型 checkpoint、服务产物、镜像（0.0.2 / offline-20261105 / darvin-t5:* 等全部弃用）、提交回执。本次镜像与模型均为全新构建/训练。

## 阻塞与失败记录（未掩盖）

1. lark sheets 三张表格不可读（bot 缺 scope；user 身份沙盒只读+token 不可用）→ 接口契约以文档正文+官方代码为准（一致）。
2. buildx 默认 builder 因 home 只读失败 → DOCKER_BUILDKIT=0 解决（证据保留）。
3. 首次后台 nohup 进程被沙盒清理 → 改持久会话前台运行（无产物影响）。
4. darvin scientist 端点 401（token 过期且无 `DARVIN_WALLET_PRIVATE_KEY_PROD`/浏览器流程可非交互续期）→ 不阻塞 precheck；若 submit 主流程同样 401 将失败（无副作用、不扣积分、不自动重试）——已如实写入 approval-request.md 风险项。
5. 主文档首抓网络 EOF → 重试一次成功（记录在案）。

## 网络/代理合规

- 全部外网走免费代理 `172.28.4.16:18999`（gitlab.4pd.io、download.pytorch.org）或直连可达源（darvin-api、OSS、pypi.org、harbor-contest.4pd.io）。
- **计费代理 127.0.0.1:7589 未使用**；无大量不必要下载（新增下载仅 torch/torchvision/9 小依赖轮子 + 官方小仓库 + 8.4KB helm zip）。

## 若后续获得授权（新会话可执行）

在 `t6-submission/` 下运行（一次）：
`<darwin CLI 绝对路径> solution submit --config solution.yaml --yes --json`
随后 `solution status/list` 只读跟踪；结果不明只读对账，不重试。
