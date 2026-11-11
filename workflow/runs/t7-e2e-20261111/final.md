

T7 端到端运行完成，唯一一次授权的真实提交已成功。

**结果**
- 新提交：**submission 396** / model app **14434** / task **`0359f8e60c923a42d74161795f505b80`**，stage=`job_created`，`historical=false`，命令 exit 0（仅执行一次，无重试）
- 提交后只读核实：任务 `running`，inference job `SCHEDULING`；列表中 396 为 PROCESSING 且 Local receipt=yes，与本地回执闭环一致
- 回执与证据：`runs/t7-e2e-20261111/t6/SubmissionReceipt.md`、`runs/t7-e2e-20261111/t6/t6-submit.json`、`runs/t7-e2e-20261111/final.md`、`runs/t7-e2e-20261111/commands-and-results.md`

**本次新执行（全部实测）**
- T1：`subnet inspect 196` + `auth inspect`（exit 0）——与历史逐字段对比仅 solutions 114→127/participants 11→12 计数变化，契约未变；submit/task.create 均 eligible
- T3：复制 `predict.py` 全新推理 6 样例，序列 `0_1,1,0_1,1,0_2,0_2` 与基线三方一致，max|Δlogit|=0.0
- T4：服务复制到本目录，权重 sha256 OK，本地 HTTP **15/15**（含 7 个 400 错误用例 + 404，错误响应 result 恒 null），端口已释放
- T5：本地镜像 ID/架构/大小与 ImageManifest 一致；context 5/5 摘要一致；**全新 2C4G 容器 15/15**（已 `docker rm -f`）；registry 只读 inspect（NO_PROXY 直连）index digest `sha256:57004ba6…`、amd64 manifest `sha256:32233f079…` 均与 manifest 一致
- T6：历史 **364**（running、尚无结果 >12h、can_cancel=true）与 **365**（READY_TO_DEPLOY/PENDING、来源维持未确认）只读核查在案，均非本次对象、不构成阻塞，未取消；新建提交配置（对象名 `liuyutong-image-auth-t5-20261111-e2e`），在线 precheck **8 pass + 2 设计 unverified，0 blocking**

**复用（均已重新核验）**：T1 spec（`t1-real-20261108`）、T2 plan（`t2-solution-planning-20261109-bounded`）、T3 推理/基线、T4 服务与测试、T5 镜像与 ImageManifest、`model_full.pt` 权重（只读引用）

**外部写操作**：仅 1 次平台写（submit 396 + 评测任务创建）。平台读 7 次小请求走 7589 代理；registry 1 次 manifest 级直连。无镜像 push/build/pull、无训练/下载、无旧目录修改、无历史任务取消、未记录认证秘密

**如实记录的异常与未验证项**
- 提交后核实阶段 ro 挂载瞬断致 CLI 两次 exit 127（仅只读查询，改显式 `venv/bin/python venv/bin/darvin` 调用后成功，无重复提交）
- 列表出现 397（model 14435，同名、无任务、无本地回执），疑似平台配对生成条目（与 364→365 同形态），未认领
- 未验证（平台侧）：镜像拉取/评测出分（需跟踪 task 0359f8e6…）、积分扣减额、C1/C2 规则冲突裁定

后续跟踪只需只读查询：`darvin solution status 0359f8e60c923a42d74161795f505b80 --config runs/t7-e2e-20261111/t6/solution.yaml --json`。需要的话我可以稍后再查一次任务推进状态。