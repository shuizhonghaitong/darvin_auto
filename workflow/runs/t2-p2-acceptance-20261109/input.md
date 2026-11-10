本次只执行 TICKET-2 的 P2 Solution Discovery 独立验收。先完整读取 /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/.agents/skills/solution-discovery/SKILL.md，再读取 /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json。CompetitionSpec 是唯一比赛输入。按 Skill 自主发现并筛选候选，不得读取任何既有候选方案、本地模型权重、历史运行日志或结论，也不从其他本地文件寻找候选提示。

只进行初步可行性判断，不要求真实复现、训练、下载模型或数据、资源实测或服务化。通过公开搜索和外部工具独立发现候选，核查来源、固定版本、许可与选择依据；无法核实的内容明确标注未知或风险，不得假定许可允许使用。输出 candidate_solutions.json 和简短的筛选与证据说明到当前目录。即使没有合格候选，也输出已搜索证据和具体原因；网络或认证阻塞、Skill 能力不足、正常搜索无合格候选必须区分。

预算：最多 15 次搜索请求、50 次工具调用；自行计数并在达到任一上限前停止，输出已有结果。外部执行时间上限 25 分钟。只做小规模网页、API 和仓库元数据访问，不安装依赖，不下载权重或训练附件，不运行外部代码。不要重试无新证据的失败。

网络：优先使用免流代理 http://172.28.4.16:18999；访问 GitHub 必要时可以使用用户已授权的计费代理 http://127.0.0.1:7589，仅用于小规模元数据访问。保持本机及内网直连。GitHub API 可能返回 403，记录实际结果，不要擅自扩大权限。
