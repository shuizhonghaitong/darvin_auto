# T6 交接 — 提交准备与真实提交 — t7-e2e-20261111

## 授权边界
- 调用方（用户）明确授权本次**最多一次**新的真实 Darwin 提交并创建对应评测任务；提交命令只执行一次，不自动重试；结果不明时仅只读查询。
- 禁止项均已遵守：未推送/构建/拉取镜像、未训练/下载模型、未修改旧运行目录、未取消历史任务。

## 提交前只读核查（本次新执行，2026-11-11T02:5xZ）
```sh
$D solution status 88c59e71a9f0f235352116c6409e0ee5 --config t6/solution.yaml --json   # t6/t6-hist-364-status.json, exit 0
$D solution list --subnet 0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb --config t6/solution.yaml --json  # t6/t6-solution-list.json, exit 0
```
- 历史 364（模型 14397，任务 88c59e71a9f0f235352116c6409e0ee5）：status=running / PROCESSING，inference job RUNNING“尚无结果”，can_cancel=true（自 11-10 起 >12h）。平台现状记录，**非本次提交**；其状态不构成对新提交的阻塞，按指令不无故中止、不取消。
- 历史 365（模型 14398）：READY_TO_DEPLOY / evaluation PENDING / 无关联任务；来源与 364 的关系维持历史“未确认”记录（继承 t6-submission-20261110/SubmissionReceipt.md），本次不认领、不据此操作。
- 列表另含更早的 350–357（liuyutong-image-auth-cnn-v1，分数 42.08 等），均为历史对象，与本次无关。

## 镜像一致性（T5 结论复核）
- 本地 image ID `sha256:57004ba6…` = registry OCI index digest = ImageManifest 记录；amd64 manifest digest `sha256:32233f079…` 一致；权重 sha256 `132efbd9…` 一致（t5/ 证据）。

## 本次提交配置（新对象）
- `t6/solution.yaml`：name=**liuyutong-image-auth-t5-20261111-e2e**（全新对象名，非历史 364/365 的 liuyutong-image-auth-t5-20261110）；subnet_address=0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb（本次 T1 平台复查确认）；submission_type=DockerImage；values_file=./values.yaml；training_image=平台 SUT 镜像 digest pin（与历史配置一致，36fccd…f7ac）；auto_create_task=true。
- `t6/values.yaml`：inferenceImage=harbor-contest.4pd.io/liuyutong/darvin-t5 : 20261110（T5 manifest 一致）。

## 在线 precheck（本次新执行）
```sh
$D solution precheck --config t6/solution.yaml --json   # t6/t6-precheck.json, exit 0
```
→ status=success；checks：config/local_input(digest b0617446d4cf)/training_image/session/prod wallet/subnet/datasets(1)/values_template/quiz 全部 **pass**（8/8）；`points`（积分/冷却/并发）与 `runtime`（镜像拉取/挂载/评测）按平台设计 **unverified**（提交时/运行时确认）；无 blocking。

## 真实提交（本次唯一一次外部写操作，已获明确授权）
```sh
$D solution submit --config t6/solution.yaml --create-task --yes --json   # 02:57:50Z–02:57:57Z，exit 0
```
- 平台回执（t6/t6-submit.json）：**submission_id=396，model_app_id=14434，task_id=0359f8e60c923a42d74161795f505b80**，stage=job_created，historical=false，trace_id=v1:b9b75c55…。本地回执：`t6/.darvin/submissions/v1_b9b75c55….json`。
- 详见 `t6/SubmissionReceipt.md`。

## 提交后只读核实（本次新执行）
- `solution status 0359f8e6…` → running，inference job SCHEDULING，can_cancel=true（t6/t6-new-status.json）。
- `solution list` → 396/14434 PROCESSING、Local receipt=yes（t6/t6-new-list.json）；另有平台侧 397/14435 同名无任务条目（不在回执内，不认领）。
- 核实过程中的本地环境异常（如实）：ro 挂载 `darwin_auto` 瞬断导致 CLI 两次 exit 127（文件在、shebang 解释器在、重试/改经 `venv/bin/python venv/bin/darvin` 显式调用即成功）；两次失败均为只读查询，未产生任何平台写操作，未触发任何重复提交。
