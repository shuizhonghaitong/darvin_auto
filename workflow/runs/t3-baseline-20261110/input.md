# T3: Baseline Implementation

你正在执行 T3，仅实现并验证可复用的图像三分类 Runnable Solution。请先实际读取 `.agents/skills/darwin-workflow/SKILL.md`，并在运行报告中说明采用了哪些适用于 T3 的指引；如果其中包含本任务以外的要求，以本任务的边界为准。请读取 `runs/t1-real-20261108/competition_spec.json` 和 `runs/t2-solution-planning-20261109-bounded/solution_plan.json`；后者仅供参考，不必机械执行。

只在 `runs/t3-baseline-20261110/` 内创建或修改本次产物，不修改 T2、旧工程或其他现有文件。优先复用既有合法本地资源，不下载任何文件、不安装依赖、不联网查询。可检查旧工程 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_repo/model_train/` 内模型及训练代码，以及 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/datasets/image_auth/` 内真实数据。可检查 `/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python` 和 `/mnt/disk3/liuyutong_home/miniconda3/envs/qwen/bin/python` 的现有依赖。独立核对模型结构、标签映射、权重加载和预处理是否一致。不要复制大量数据或权重；引用现有路径并记录依赖即可。

实现最小、真正处理图像并输出 `1`、`0_1` 或 `0_2` 的三分类算法；可以复用合适的已有模型，无需训练或追求准确率。使用不同类别的真实样例实际执行推理并保存输入路径、完整命令、退出状态、实际输出、相关日志；验证输出来自模型而非固定类别。提供清晰可调用的代码和运行报告，说明模型来源、环境、依赖、标签、预处理、限制和复现命令。测试数据的标签和模型预测分别记录，不要声称预测一定正确。输出应足以供 T4 后续复用。

禁止实现或运行 HTTP 服务、Docker、镜像推送或 Darwin 提交；不实现错误时固定返回类别的策略，不进行多轮调优或严格容器资源测试。遇到资源不可用时做有限检查，报告具体阻塞与证据，不扩大权限。最后总结实际修改、运行及各项验证结果。
