只处理 TICKET-2，独立完成目标环境验证。首先完整读取 /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/.agents/skills/solution-discovery/SKILL.md 和 /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json。不要读取以往候选方案、运行 Agent 日志或结论；独立检索和判断，保留来源、命令、结果和产物。工作目录是本次运行目录，产物只写在此目录。

用户授权使用比赛训练附件，允许为可行性检查做最小模型加载、三分类适配及单步训练测试；不授权完整训练、TICKET-3 或比赛提交。核验候选来源及权重下载地址、固定版本、使用许可和依赖，核查比赛数据三类覆盖。无法核实的条件必须明确列为未验证，不能将合成输入证明当成真实数据覆盖或模型效果。

独立确定候选后可检查和复用本地缓存，避免重复下载；不得读取其他运行目录里的候选结论。已有 Python 环境 /mnt/disk3/liuyutong_home/miniconda3/envs/evo 和 /mnt/disk3/liuyutong_home/miniconda3/envs/qwen 可自行检查复用；不得安装依赖或修改环境。测试尽量使用两核 CPU，测量内存峰值，4GB 是用户指定的验证假设，不是已确认的官方比赛约束。可行时验证权重加载完整性、三类标签映射、三维输出和分类头反向传播及参数变化。保留复现命令、退出状态和关键日志。产出 CandidateSolutions 及报告，不满足关键条件时明确 blocked。

网络：只使用免流代理 http://172.28.4.16:18999；本轮不要使用付费出口或未经确认计费的其他出口。确需切换或产生大流量时停止并说明；不输出凭据。保留 localhost/private NO_PROXY，不读取或修改认证配置。
