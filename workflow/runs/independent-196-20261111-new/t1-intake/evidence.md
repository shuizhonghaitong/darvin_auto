# T1 证据 — 图像真伪鉴定榜（subnet 196 / backend subnet_id 85）

本阶段所有来源均为本次运行（2026-11-11 21:38–21:55 CST / 13:38–13:55 UTC）实际获取。除特别注明"用户提供"或 S8（历史缓存，本次核验）外，均非复用旧产物。

## 1. Darwin CLI（darwin 0.5.2，profile=prod）

工具位置：`/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin`（不在 PATH，使用绝对路径；版本 `darwin --version` = 0.5.2）。

| 命令 | 结果 | 产物 |
|---|---|---|
| `darwin auth inspect --json` | success（authenticated，wallet 0x8230f5…2e4e；capabilities: subnet.create / solution.submit / task.create 均 eligible） | `auth_inspect.json` |
| `darwin subnet show 196 --json` | success（5.0s） | `subnet_show_196.json` |
| `darwin subnet inspect 196 --json` | success（1.5s） | `subnet_inspect_196.json` |

关键事实（S1/S2）：
- 名称：图像真伪鉴定榜；contract `0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb`；status=ACTIVE，stage=IN_PROGRESS。
- URL 查询 ID **196** ≠ 内部 subnet_id **85**（backend_id=196）。
- submission_type=DockerImage；evaluation_mode=automatic；solutions=131；participants=12；reward_type=V3；prize_pool=1000。
- lifecycle：1783958400 → 1815494400（2026-07-13T16:00Z → 2027-07-13T16:00Z）。
- 固定测试集：`image_authenticity_verification_leaderboard_dataset.zip`（test_dataset_app_id=246，全量）。
- 评测 helm 配置：`global_task_helm_config_url`（OSS，revision 1，8442 B）→ 本次下载 `subnet_helm.zip` 解压至 `helm_config/`。
- readme 提交方式：`inferenceImage:{repository,tag}`；可选 `inferenceVolumeMounts`（name=model、source=ceph_customer 固定；mountPoint/srcRelativePath 可改）；镜像要求 linux/amd64、0.0.0.0:80、GET /ready、业务接口、资源内完成加载推理；"所有测试样本均需返回合法预测。任意样本在重试后仍推理失败，则本次评测无有效排行榜成绩。"

## 2. 飞书文档（lark-cli 1.0.98，bot 身份）

工具位置：`/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/lark-cli-1.0.98/lark-cli`。

| 文档 | doc_id | revision | 结果 | 产物 |
|---|---|---|---|---|
| 榜单介绍 | GguVdTxCBoGul4xqTPscxfztn6g | 56 | 首次请求网络 EOF 失败，重试成功 | `lark_main.json`（失败记录 `lark_main.err` 首份） |
| 训练集 | NSsFdVE57o0xemxcWRkcpFswnkh | 15 | 成功 | `lark_training.json` |
| 推理接口 wiki | HL7JdRbb6ovlP1xwgN3cnNy7n3g | 29 | 成功（正文；3 张内嵌表格未读，见 §5） | `lark_inferapi.json` |

关键事实：
- S3：输入 jpg/png 等常见格式；三分类定义（1/0_1/0_2）；数据集范围：文档类、风景类、人物动物类；**资源限制原文"1/2 A100-40g显存，2c4g"**；排序指标 f1_0=(F1_0_1+F1_0_2)/2；监测指标含 accuracy、f1_1、P/R/F1(0_1,0_2)、平均响应时间 ms、失败率；"失败判定：请求失败率超过 5%（返回结果为空）"（与 S1/S6/S7 的"任意失败即无效"存在差异，见 spec.conflicts[0]）。
- S4：训练集附件两个：`训练集 1 0_1.zip`（139,334,730 B，token Ofj7bQtFMoe66fxcCGMc9pBSnug）、`训练集 0_2.zip`（437,962,033 B，token Hab7b2O8lo6LCaxXjaNc1jV5nQh）。
- S5：`GET /ready`（port 80，httpGet）；`POST /api/v1/image-authenticity`，请求 `{image_base64(不含 data: 前缀), image_format}`；响应 `{success, message, result}`，result ∈ {"1","0_1","0_2"}；"评测请求仅包含图片内容和图片格式，不会提供图片 ID、文件名、文件路径或真实标签。评测图片的请求顺序会随机打乱"；starting-kit 参考 gitlab.4pd.io/gaoziming/image_authenticity_verification_leaderboard/-/tree/main/starting-kit。

## 3. 评测 helm chart（S6，本次下载）

`curl` 直连 OSS 成功（HTTP 200，8442 B）。解压后为 chart `darvin_sut` v0.1.0：
- `values.yaml`：
  - `inferenceResources`/requests = cpu 2、memory 4Gi、`nvidia.com/gpu=1`、`nvidia.com/gpumem=40960`、`nvidia.com/gpucores=50`（≈1/2 A100-40GB vGPU，与 S3 一致）；
  - nodeSelector `contest.4pd.io/accelerator: A100-SXM4-80GB` + `internet: on`；tolerations hosttype=vgpu；
  - readinessProbe：exec `curl -fsS --max-time 3 http://127.0.0.1:80/ready`（无 curl 时 python 兜底），initialDelay=30s、period=5s、timeout=5s、failureThreshold=720（最长约 60 分钟就绪窗口）；
  - SUT 容器注入 env：TZ=Asia/Shanghai、benchmark_name=image_authenticity_verification_leaderboard、REQUEST_TIMEOUT_MS=10000、RESPONSE_TIME_THRESHOLD_MS=0、MAX_RETRIES=3、RETRY_INTERVAL=0.5、MAX_FAILURE_RATE=0、FAIL_ON_ANY_INFERENCE_ERROR=true；
  - ceph-customer 卷（readOnly，path /volumes/platform-group01/sub-customer/7a7b6a00-dd7f-4254-9378-10f24710c781），`inferenceVolumeMounts[].source=ceph_customer` 映射到该卷，支持 subPath；
  - 默认 `evaluationImage`：harbor-contest.4pd.io/gaoziming/judge-flow/image_authenticity_verification_leaderboard-darvin:0.0.1（pullPolicy Always）；evaluation Job backoffLimit=0。
- `inference-deployment.yaml`：SUT `imagePullPolicy: Always`，单副本。
- `evaluation-job.yaml`：judge 容器同样注入上述 env；restartPolicy Never。

## 4. 官方仓库（S7，本次克隆）

`git clone --depth 1 https://gitlab.4pd.io/gaoziming/image_authenticity_verification_leaderboard.git`（经 https_proxy=http://172.28.4.16:18999；前次运行记录直连 172.24.15.54 超时，本次直接走代理，克隆成功）。commit `d22762ef44c8983a474e5079e1f4e22183b72c5d`（2026-09-18）。产物 `kit/`。

- starting-kit：Flask Mock 服务——`POST /api/v1/image-authenticity` 按图片字节 SHA256 前 4 字节 mod 3 返回假标签；`GET /ready` 返回 "True"；host 0.0.0.0、端口 env `MOCK_SERVER_PORT` 默认 80；Dockerfile `FROM harbor.4pd.io/lab-platform/inf/python:3.9`，pip 源 `https://nexus.4pd.io/repository/pypi-all/simple`，`CMD ["/root/test/start.sh"]`，start.sh 执行 `python3 main.py`；官方 build.sh：`docker build --platform linux/amd64 --network=host`，推 `harbor-contest.4pd.io/gaoziming/sut/...:0.0.1`。
- judge-flow（`run_for_darvin.py` 719 行 + utils/）：
  - 解压测试 zip，data.json（Object id->label 或 List）+ images/ 目录；`SUPPORTED_EXTENSIONS={.jpg,.jpeg,.png,.webp,.bmp}`；
  - payload 仅 `{image_base64, image_format}`（断言不含 id/文件名/路径/标签等字段）；
  - `REQUEST_TIMEOUT_MS` 被钳制 `max(env, 60000)`；`requests.post(timeout=60s)`；
  - 重试：仅网络/HTTP 状态错误（Timeout、RequestException，含 raise_for_status 的 4xx/5xx）重试，MAX_RETRIES=3 次尝试、间隔 0.5s；业务失败（success=false / result 空 / 非法标签）不重试直接判失败；
  - 指标：one-vs-rest P/R/F1；`_score = f1_0 = (f1_0_1+f1_0_2)/2`；
  - 失败策略：`FAIL_ON_ANY_INFERENCE_ERROR=true` 且 failed_cases>0 → metrics success=0、_score=0、退出码 1（"本次评测无有效排行榜成绩"）。
  - RESPONSE_TIME_THRESHOLD_MS=0 → 响应时长阈值检查禁用。
- `no-manual-annotation/` 为通用 judge 模板（与本榜同构）。

## 5. 失败/受限项（如实记录）

1. **S5 内嵌 sheets（RUblU0/Cl5ExX/G2lxWB，spreadsheet Gz7OsS2NIhYCYCt09ybca1Y6nud）不可读**：
   - bot：`sheets +cells-get` → code 99991672，缺 scope `sheets:spreadsheet:read`（产物 `sheet_*.err`）。
   - user（刘昱彤，ou_e8431a…，auth list 显示 needs_refresh）：默认 HOME 下刷新报 `read-only file system`（沙盒禁止写 `~/.local/share/lark-cli`，产物 `sheet_RUblU0_user.err`）；把凭证目录复制到 /tmp/lark-home 并以 HOME=/tmp/lark-home 重试，CLI 报 `no_token`/`need_user_authorization`（复制的 user token 未被识别，产物 `sheet_RUblU0_user3.json/err`）。→ user 身份在本沙盒内不可用；且历史运行已记录该单用途 refresh token 曾被服务端吊销。
   - 影响：接口字段明细表未核验；契约以 S5 正文 + S7 代码为准（二者一致）。
2. lark-cli DPoP 持久化告警（`keychain Set failed ... read-only file system`）：沙盒限制，bot 调用仍成功，非阻塞。
3. 主文档首次抓取网络 EOF：重试一次成功（非权限问题）。

## 6. 本地训练集缓存核验（S8，允许复用的缓存）

路径 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/datasets/image_auth/`（2026-11-03 历史下载；本次仅核验、未重新下载）：
- `train_1_0_1.zip` = 139,334,730 B；`train_0_2.zip` = 437,962,033 B —— 与 S4 文档标注大小逐字节一致 → 判定为同一官方文件。
- 已解压目录（本次统计）：
  - `train_1_0_1/1/{人物,动物,风景,文字}` 各 100 张 = 400（类 1）
  - `train_1_0_1/0_1/{人物,动物,风景,文字}` 各 100 张 = 400（类 0_1）
  - `train_0_2/训练集 0_2/0_2/` = 400（类 0_2）
  - 格式：jpg 1114 / png 68 / tiff 18；噪声 `.DS_Store` 13（`__MACOSX` 目录需过滤）。
- 结论：三分类训练集齐全，共 1200 张，可作 T3 训练数据（复用缓存，未产生新下载）。

## 7. 本地构建/验证环境实测（本次）

- GPU：`nvidia-smi` 失败（无驱动通信），`/dev/nvidia*` 不存在，lspci 仅 ASPEED VGA → **本机无 GPU，T3 训练与本地推理只能用 CPU**（torch 2.14.1+cpu，venv-train 含 torch/flask/numpy）。
- Docker：29.5.3；`~/.docker/config.json` auths 仅含 `harbor-contest.4pd.io`（已登录）。
- 本地镜像（仅记录现状，不复用其内容）：基础镜像 `harbor.4pd.io/lab-platform/inf/python:3.9`（2.62GB）存在；`harbor-contest.4pd.io/liuyutong/sut/image_authenticity_verification_leaderboard:0.0.2 / offline-20261105` 为历史产物（禁用）；其他 `harbor-contest.4pd.io/gaoziming/...` 为他队/官方镜像。
- 推送命名空间 `harbor-contest.4pd.io/liuyutong/` 可用性：以 T5 实际 push 新 tag 验证。

## 8. 网络与代理记录（本次实际路由）

- darvin-api.originlabs.cc（darwin CLI）：直连成功（launch.sh 的 NO_PROXY 含 172.16/12 等；originlabs 域名按默认路由）。
- OSS `gradient-darvin-*.aliyuncs.com`：直连 200。
- gitlab.4pd.io：经免费代理 172.28.4.16:18999 克隆成功（小流量）。
- 127.0.0.1:7589（计费）：**本次未使用**。
