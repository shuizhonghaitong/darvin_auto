# T6 SubmissionReceipt — t7-e2e-20261111（本次真实提交，唯一一次）

## 授权
- 用户明确授权本次最多一次新的真实 Darwin 提交并创建对应评测任务；提交命令**只执行了一次**，无重试。
- 命令与输出：`t6/t6-submit.json`（stdout，完整原始回执）、`t6/t6-submit.stderr`（空）、`t6/t6-submit.exit`（exit=0）。

## 提交命令（实际执行，2026-11-11T02:57:50Z–02:57:57Z）
```sh
/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin solution submit \
  --config /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t7-e2e-20261111/t6/solution.yaml \
  --create-task --yes --json
# → exit 0；平台 envelope status=success，duration_ms=6368，profile=prod
```

## 平台回执（t6-submit.json 关键字段）
| 字段 | 值 |
|---|---|
| stage | job_created |
| **submission_id** | **396** |
| **model_app_id** | **14434** |
| **task_id** | **0359f8e60c923a42d74161795f505b80** |
| task_name | liuyutong-image-auth-t5-20261111-e2e |
| trace_id | v1:b9b75c55ccd77f9ed5c390747f8eff53cfe197be7d9f447bc8bbc4dd1e0b8c6e |
| model_saved / task_created / job_created | true / true / true |
| historical | false |
| 本地回执文件 | `t6/.darvin/submissions/v1_b9b75c55ccd77f9ed5c390747f8eff53cfe197be7d9f447bc8bbc4dd1e0b8c6e.json`（CLI 写入） |

## 平台只读核实（本次新执行）
```sh
$D solution status 0359f8e60c923a42d74161795f505b80 --config t6/solution.yaml --json   # t6/t6-new-status.json, exit 0
$D solution list --subnet 0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb --config t6/solution.yaml --json  # t6/t6-new-list.json, exit 0
```
- 任务 0359f8e6…：status=running，can_cancel=true，model_app_id=14434；inference job `5f378999596ef29e9809af8110db84ef` 状态 **SCHEDULING**（尚无结果）。
- 列表：submission **396** / model 14434 / name `liuyutong-image-auth-t5-20261111-e2e` / PROCESSING / 关联任务 0359f8e6… / **Local receipt=yes** —— 与本地回执闭环一致。
- 列表另出现 **397**（model 14435，同名，READY_TO_DEPLOY/PENDING，无任务，Local receipt=no）：不在本次回执内、未由本次命令产生记录；形态与历史 364→365 成对模式一致（推测为平台侧生成的配对条目，未证实），如实记录，不认领、不据此操作。
- 历史 364（14397/任务 88c59e71…）仍 PROCESSING/running；365（14398）仍 READY_TO_DEPLOY/PENDING——两者均非本次提交，状态本次未再变化，也不构成阻塞（见 `t6-handoff.md`）。

## 限制（如实）
- 任务 running/SCHEDULING 只证明任务已创建并进入调度，**不证明镜像拉取成功、服务启动成功、评测成功或出分**。平台侧拉取/评测/积分消耗属 runtime 确认项，需后续跟踪（只读 `solution status 0359f8e6…` 即可）。
- 未记录任何认证秘密（auth inspect 仅含公开 wallet 地址与能力状态）。
