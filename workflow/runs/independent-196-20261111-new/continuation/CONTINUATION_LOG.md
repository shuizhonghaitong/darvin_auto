# Continuation Log — 提交与评测跟踪（第二次 codex exec 调用）

**运行目录**：`runs/independent-196-20261111-new`
**本次范围**：仅执行用户明确授权的一次 Darwin 提交（competition 196 / 图像真伪鉴定榜），只读核验前置状态，跟踪平台任务与评测结果。
**时间**：2026-11-12 00:53–01:45 UTC（CST = UTC+8，08:53–09:45 CST）
**不覆盖第一次调用的任何产物**；本目录 `continuation/` 为本次新增（第一次调用产物 t1–t6、events.jsonl、final.md、RUN_SUMMARY.md、approval-request.md 等原样保留）。

## 授权与对象（逐字符）

- 镜像 tag：`harbor-contest.4pd.io/liuyutong/sut/image_authenticity_verification_leaderboard:20261111-independent-new`
- digest：`sha256:2d2793dbf17f7542d17327fd18621d46f4b9bf6ad06b20fe0e521fbad5487ff8`
- 配置文件：`t6-submission/solution.yaml`（training_image 以 digest 固定）+ `t6-submission/values.yaml`
- 授权上限：**最多提交一次**；不取消任务；不重复提交；状态不明则只读查询并停止。
- 本次全程 **1 次** `solution submit`，0 次取消，0 次重试提交。

## 前置只读核验（本次实际执行，提交前完成）

| # | 命令（CLI 0.5.2，profile=prod，HOME=/tmp/darvin-home） | 结果 | 证据文件 |
|---|---|---|---|
| 1 | `darvin auth inspect --json` | success：authenticated，wallet 0x8230f54422252c68d1E3F084D7aBF01d72E32e4e；`solution.submit`/`task.create`/`subnet.create` 均 eligible（source: scientist.quiz.status 等）；warnings 空 | `01-auth-inspect.json` |
| 2 | `darvin solution list --config solution.yaml --include-unsubmitted --json` | success，data 为空 → 该 solution **无任何既有提交记录** | `02-solution-list.json` |
| 3 | `darvin solution list --subnet 0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb --size 100 --json` | success，data 为空 → 本账号该 subnet 无既有提交 | `03-solution-list-subnet.json` |
| 4 | `darvin task list --json` | success，data 为空 → 无 queued/running 任务（与用户陈述一致） | `04-task-list.json` |
| 5 | `docker manifest inspect <tag>`、`docker manifest inspect <repo>@<digest>`、`docker buildx imagetools inspect <tag>/<digest>`（registry 只读） | tag 与 digest 均可解析；tag 的 `Digest` 与授权 digest **逐字符一致**（sha256:2d2793…5487ff8） | `05-image-verify.log` |

- 登录状态：`~/.darvin-cli/profiles/prod.json` mtime 2026-11-12 08:36 CST（用户刷新登录）；提交前 `auth inspect` 证实 `solution.submit` eligible（第一次调用 401 的 scientist 端点已恢复）。
- 状态目录处理：将 `~/.darvin-cli` 完整复制到 `HOME=/tmp/darvin-home`（两端 prod.json sha256 一致，`state-fingerprint.txt`），全部 darvin 命令使用该 HOME，写路径确定、不改动原始状态；CLI 回执实际落盘于 `t6-submission/.darvin/submissions/`（运行目录内）。
- 第一次调用互证：`t6-submission/approval-wait.log` = WAIT_EXPIRED、从未执行 submit。
- 结论：提交前**无任何在先提交**，镜像身份与授权对象一致 → 满足执行条件。

## 提交（唯一一次）

- 命令：`cd t6-submission && HOME=/tmp/darvin-home darvin solution submit --config solution.yaml --yes --json`
- 时间：2026-11-12T00:55:19Z → 00:55:26Z（duration 7293 ms），exit=0，stderr 空
- 结果：**status=success，stage=job_created**；步骤 precheck / write receipt / create model and task 全部 success；warnings、errors 均空。
- 平台返回 ID：
  - `submission_id` = **422**
  - `model_app_id` = **14473**
  - `task_id` = **a02708ad1ecd608f0949ef1803a209ee**
  - `job_id` = **f6bdcb4df1d7253cece08f5e84c15037**
  - `trace_id` = `v1:3931633747c8c86358c1a600536a23fd6a3599a186b3e77c6d2c981c8913fc65`
  - `historical` = false（新提交，非历史重放）
- 回执副本：`07-receipt.json`；完整输出：`06-submit.json`

## 评测跟踪（只读轮询，共 2 个有界轮询 + 终态快照）

- 轮询脚本：`poll.sh`（02–31，~00:56–01:24Z）、`poll2.sh`（32–51，~01:24–01:43Z），每 ~54s 一次 `solution status --json`，落盘 `09-status-poll-NN.json` / `11-status-poll-NN.json`，汇总 `poll-summary.log`。
- 阶段轨迹：task=running；job stage=inference SCHEDULING→RUNNING（00:57Z）→ stage=evaluation RUNNING（00:58Z 起）。
- 评测日志快照（`solution logs --download-only`，只读）：`logs-eval/`（25/120 @09:04CST）、`logs-eval-2/`（77/120 @09:23CST）、`logs-eval-3/`（96/120 @09:31CST）、`logs-eval-4/`（116/120 @09:39CST）、`logs-eval-5/`（**120/120 完成 @09:41CST**）。
- 终态快照：`12-status-check-1.json`（01:43Z 后）→ **task=success，job=evaluation SUCCEEDED，score=42.21 (raw 42.21)**。

### 平台评测结果（judge 日志，`logs-eval-5/`）

- 批量推理：**120/120 成功，0 失败**（fail_rate=0.0000 → 未触发"任意样本重试后仍失败则评测无效"红线）
- 指标：**accuracy=0.4500，f1_1=0.5135，f1_0_1=0.4138，f1_0_2=0.4304，f1_0=0.4221**
- avg_response_time_ms=22132.75（平台 2c4g CPU；本地 128 核为 ~55ms/张，平台慢约 2 个数量级属预期）
- 平台得分 42.21 = f1_0×100（raw 42.21）
- 错误案例：66/120（judge 写入 bad_cases.json）
- 如实备注：本地训练集划分上 val f1_0=0.8056（第一次调用 T3），平台固定测试集上 f1_0=0.4221 —— 两者测试集不同，平台结果以 judge 为准。

## 轮询中的瞬时只读故障（已自愈，不影响提交/评测）

- poll 14（01:08Z）：`NETWORK_ERROR [SSL: UNEXPECTED_EOF_WHILE_READING]` → poll 15 立即成功（`09-status-poll-14.json` 存证）。
- `task list --size 100`（无 status 过滤，15-task-list-all.json）：`NETWORK_ERROR Server disconnected`；带 `--status completed` 的查询成功（data 空）。
- list 端点观察：提交后 `solution list --config` 与 `task list --status completed` 均返回空 data —— 这两个列表端点未回显本次自动评测任务；唯一性证据以"提交前列表为空 + 仅 1 次 submit 调用 + 平台回执 ID + 任务终态"为准。

## 状态三分法（终态）

| 维度 | 状态 | 依据 |
|---|---|---|
| Agent 运行 | **完成**（核验→唯一提交→有界轮询→记录） | 本文件 |
| 平台接受（submission accepted） | **已确认** | `06-submit.json`（stage=job_created，exit=0）+ `07-receipt.json` + `12-status-check-1.json` |
| 评测完成（evaluation completed） | **已确认** | task=success，job SUCCEEDED，score 42.21，judge 日志 120/120 |

## 文件清单（continuation/）

- `01-auth-inspect.json` / `.stderr` — 登录与能力核验
- `02-solution-list.json` — 提交前 solution 级列表（空）
- `03-solution-list-subnet.json` — 提交前 subnet 级列表（空）
- `04-task-list.json` — 提交前任务列表（空）
- `05-image-verify.log`（+ .err1/.err2）— 镜像 tag/digest 只读核验
- `06-submit.json` / `.stderr` — **唯一一次提交**完整输出
- `07-receipt.json` — CLI 提交回执副本
- `08-status-poll-01.json` — 首轮状态（running/SCHEDULING）
- `09-status-poll-02..31.json` — 有界轮询 1
- `11-status-poll-32..51.json` — 有界轮询 2
- `poll-summary.log`、`poll.sh`、`poll2.sh` — 轮询汇总与脚本
- `10-logs-download.json`、`12-status-check-1.json`、`13/14/15-*.json` — 日志下载与补充只读查询
- `logs-eval/`…`logs-eval-5/` — 平台 inference/evaluation 日志快照
- `state-fingerprint.txt` — CLI 状态目录复制指纹（无凭证明文）

## 阻塞处理（未触发）

无认证/配额/网络阻塞导致停止：唯一一次提交成功；评测正常完成。积分消耗 10/180（用户预检值；平台扣费记录未单独查询，如需要可后续 `darvin scientist points` 只读确认）。
