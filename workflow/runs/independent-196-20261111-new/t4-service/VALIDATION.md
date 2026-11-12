# T4 服务验证记录（本次运行实际执行）

## 服务交接

- 代码：`t4-service/main.py`（Flask，0.0.0.0:80）、`t4-service/start.sh`（无参数，`exec python3 /app/main.py`，与平台 CMD 语义一致）、`t4-service/Dockerfile`、`t4-service/build.sh`、`t4-service/prepare_context.sh`。
- 模型：`t3-solution/model/best.pt`（epoch 9，val f1_0=0.8056）+ `class_map.json`。
- 镜像：`harbor-contest.4pd.io/liuyutong/sut/image_authenticity_verification_leaderboard:20261111-independent-new`（本地 ID 2d2793dbf17f，构建日志 `t5-image/build.log`）。

## 构建

- 首次 `build.sh` 失败：buildx 状态目录 `~/.docker/buildx/activity` 位于只读 home（read-only file system）→ 记录于 build.log 首行。
- 处置：`DOCKER_BUILDKIT=0` 走 daemon legacy builder，构建成功（Step 10/10）。
- 构建全程离线：torch 2.6.0+cpu / torchvision 0.21.0+cpu 及 9 个依赖轮子全部 vendor 于构建上下文（241MB），未使用任何外网（--network=host 仅为兼容官方 build 习惯）。
- 架构断言：`docker inspect --format '{{.Architecture}}'` = amd64（build.sh 内置检查）。

## 容器运行验证（模拟平台：无参数 ./start.sh，--cpus 2 -m 4g 对齐平台 2c4g）

- `docker run -d -p 18123:80 --cpus 2 -m 4g <image>`，容器 `sut-verify-20261111`。
- 启动日志：`loading model from /app/model/best.pt on cpu` → 6s 内 `GET /ready` = **200 "True"**（torch 2.6.0+cpu 成功加载 2.8 保存的 checkpoint，weights_only=False 生效）。
- 真实推理（3 张训练集图，每类 1 张，base64 POST）：
  | 真值 | 预测 | conf | 耗时 |
  |---|---|---|---|
  | 1 | 1 | 0.997 | 3464ms |
  | 0_1 | 0_1 | 0.9994 | 3489ms |
  | 0_2 | 0_2 | 0.9594 | 21090ms（一次，见下） |
- 21s 离群复测：同图再测 3455ms / 2397ms；10MP（3174px 边）文字图 3590ms → 判定为测试瞬间宿主机 CPU 争抢，非服务问题。2 CPU 限流下稳定值 ~2.4–3.6s/张，远小于 judge 有效超时 60s/次。
- 边界用例：
  - 截断 base64（可解码为非图片字节）→ HTTP 200，`success=true, result="1"`（兜底标签，日志有 fallback 记录）→ 保证评测不因异常样本整体作废；
  - 非图片字节 → 同上 200 兜底（2ms）；
  - 空 image_base64 → HTTP 400 `success=false`（judge 自身校验保证不会发送空图，见 T1 spec S7 encode_image_to_base64 前置检查）；
  - 请求体非 JSON → HTTP 400（同上，judge 不会发送）。
- 就绪前 `/ready` = 503（模型加载期间），符合平台 readiness probe 语义（probe 持续重试至 failureThreshold=720）。

## 未验证项

- 平台 vGPU 环境内运行（本机无 GPU，服务自动回退 CPU 路径，该路径已全链路验证）。
- 远端可拉取性（T5 push 后验证）。
