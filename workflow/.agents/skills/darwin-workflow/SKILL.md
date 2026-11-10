---
name: darwin-workflow
description: 根据 Darwin 比赛 URL 或已有 CompetitionSpec，组织比赛需求理解和自主方案设计。
---

# Darwin 工作流

接收比赛详情 URL 或已有 CompetitionSpec，以及产物目录。若输入为 URL，调用 `$competition-intake`，传入原始 URL 和指定目录，获取 `competition_spec.json` 和证据；检查 JSON 可解析，证据记录实际来源、关键要求、未知项和冲突。若输入为已有 CompetitionSpec，读取并检查该文件，不重新执行需求理解。

调用 `$solution-planning`，传入 CompetitionSpec 和独立产物目录。检查 `solution_plan.json` 可解析，并将路径、方案依据、未知项及阻塞交给调用方和 T3。资料不足或工具失败时明确报告部分完成或阻塞，不以文件存在代替验收。方案设计结束后停止，不执行算法实现或后续比赛阶段。旧的 solution-discovery 保留但不再是主链路依赖。
