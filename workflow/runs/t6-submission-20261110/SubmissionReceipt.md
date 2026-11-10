# T6 SubmissionReceipt

## 授权目标与配置

- 比赛：图像真伪鉴定榜；URL 的 subnetId 为 196，内部 subnet_id 为 85；实际 CLI 使用地址 `0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb`。
- 授权镜像：`harbor-contest.4pd.io/liuyutong/darvin-t5:20261110`，与 T5 `../t5-delivery-20261110/ImageManifest.md` 一致。
- 平台当前提交类型为 DockerImage；配置见 `solution.yaml` 和 `values.yaml`。平台模型 14397 的 `helmchart_value` 已只读核对，repository 和 tag 与上述镜像一致。CLI 原始回执里的 `training_image` 是平台 SUT 镜像，不是此推理镜像。
- C1 失败规则冲突仍未解决；未伪造预测或修改服务规避。Harbor 匿名访问返回 401，平台是否有拉取凭据未确认。

## 实际提交

用户授权本比赛、此镜像真实提交一次并创建评测任务。认证核验显示已登录，具备提交及创建任务的资格提示；实际权限以平台处理为准。目标环境通过 `codex exec` 使用 `qwen3.8-27b-fp8`，实际工具调用及输出见 `qwen-submit-local-events.jsonl`，Codex 退出状态为 0。Qwen 执行的命令为：

```sh
/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin solution submit --config /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t6-submission-20261110/solution.yaml --create-task --yes --json
```

命令退出状态 0；平台返回 success，submission ID **364**，model app ID **14397**，task ID **88c59e71a9f0f235352116c6409e0ee5**，阶段 `job_created`。原始回执为 `.darvin/submissions/v1_76d70ca8b7c8b22cb1a3ded242f5fa6f7a573117d7b8f3b4506a9792f70c7d47.json`。此前尝试因路径、配置路径或模型服务问题未发出 Darwin 提交请求，相关日志保留；成功后未再次提交。

## 独立核验与限制

- `darvin solution status 88c59e71a9f0f235352116c6409e0ee5 --config <本目录的 solution.yaml> --json` 返回运行中，job ID `015243b1b18dbee8c7d2121864124ec1`，inference 为 `RUNNING`；实际输出见 `platform-status.json`。这是任务状态，不单独证明镜像拉取或服务启动成功，也不是评测成功或榜单出分。
- `darvin solution list --subnet 0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb --config <本目录的 solution.yaml> --json` 返回提交 364 与上述模型、任务对应，见 `platform-list.json`。列表另有同名提交 365（模型 14398），无关联任务，其来源及与本次操作的关系不明；不据此重复提交，也不推测归属。
- 只读模型接口 `SolutionService().get_model_info(14397)` 返回上述推理镜像配置。平台任务渲染配置只读查询返回网络不可达；平台实际镜像拉取及服务启动没有独立确认。独立干净环境拉取也未验证。
- T5 既有交付和局限见 `../t5-delivery-20261110/closeout-minimal-20261110.md`、`../t5-delivery-20261110/closeout-credential-adjudication.md`；本阶段没有重新构建、推送、扫描或重复 Qwen Docker 交接实验。

T6 按已授权验收范围通过；可进入 T7，但其完整端到端运行需遵守真实提交授权边界，并继续如实跟踪上述平台验证事项。
