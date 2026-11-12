# T5 镜像证据（本次运行实际执行）

## 标识

- 仓库：`harbor-contest.4pd.io/liuyutong/sut/image_authenticity_verification_leaderboard`
- tag：`20261111-independent-new`（唯一新 tag）
- manifest digest（远端，tag 与 digest 两种引用一致）：`sha256:2d2793dbf17f7542d17327fd18621d46f4b9bf6ad06b20fe0e521fbad5487ff8`
- config digest：`sha256:8c054997400b789f24fc17f8f1794b78e7ae636e918ef0bd094f6f671db28ab9`
- 架构/OS：amd64 / linux；未压缩 ~4.14GB，压缩 ~1.19GB

## 唯一性（push 前）

`docker manifest inspect <full_ref>` → `unknown: artifact liuyutong/sut/image_authenticity_verification_leaderboard:20261111-independent-new not found`（tag 此前不存在）。
对照组：`docker manifest inspect ...:0.0.2`（历史 tag）→ 返回 manifest（registry 可达且 auth 有效）。

## 构建

- 上下文 `t4-service/build-ctx`（241MB）：Dockerfile + main.py + start.sh + model/(best.pt 44.8MB, class_map.json) + vendor/(torch 2.6.0+cpu 178.6MB, torchvision 0.21.0+cpu 1.84MB, 9 个依赖轮子 ~36MB)。
- 首次 `build.sh`（buildx 默认 builder）失败：`failed to update builder last activity time: open ~/.docker/buildx/activity/…: read-only file system`（沙盒 home 只读）→ 记录于 `build.log`。
- 改用 `DOCKER_BUILDKIT=0 docker build --platform linux/amd64 --network=host`（daemon legacy builder）→ Step 1-10 成功（`build.log`）。
- 安装过程离线：`pip install --no-index --find-links=/tmp/wheels torch==2.6.0+cpu torchvision==0.21.0+cpu`，成功行见 `build.log`。
- 基础镜像：`harbor.4pd.io/lab-platform/inf/python:3.9`（本地缓存；官方 starting-kit Dockerfile 同款）。

## 推送

- `docker push <full_ref>` 成功；11 层中 5 层 "Layer already exists"（与基础镜像共享层），其余推送；返回 digest = `sha256:2d2793dbf17f…`（`push.log`）。

## 远端核验（push 后，registry-only 查询）

| 检查 | 命令 | 结果 |
|---|---|---|
| tag→digest | `docker buildx imagetools inspect <full_ref>` | OK，Digest 一致 |
| tag manifest | `docker manifest inspect <full_ref>` | OK（OCI v1，config 8c0549…，layers 11） |
| digest manifest | `docker manifest inspect <repo>@sha256:2d2793dbf17f…` | OK |

结论：本地构建 → 推送 → 远端可解析，digest 三处一致（push 返回 / tag inspect / digest inspect）。

## 本地运行时验证（T4，交叉引用）

见 `t4-service/VALIDATION.md`：/ready 6s 就绪；真实推理 3/3 正确（2.4–3.6s/张 @2CPU）；异常兜底合法标签。验证容器 `sut-verify-20261111` 已停止删除。

## 未验证项

- 平台侧 `imagePullPolicy: Always` 的实际拉取（提交后由平台执行；本方证据 = registry 可读 + digest 一致 + amd64）。
