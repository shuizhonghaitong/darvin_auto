---
name: darwin-workflow
description: 根据 Darwin 比赛 URL 或已有阶段产物，组织需求理解、方案设计及服务适配交接。
---

# Darwin 工作流

接收比赛详情 URL 或已有 CompetitionSpec，以及产物目录。若输入为 URL，调用 `$competition-intake`，传入原始 URL 和指定目录，获取 `competition_spec.json` 和证据；检查 JSON 可解析，证据记录实际来源、关键要求、未知项和冲突。若输入为已有 CompetitionSpec，读取并检查该文件，不重新执行需求理解。

调用 `$solution-planning`，传入 CompetitionSpec 和独立产物目录。检查 `solution_plan.json` 可解析，并将路径、方案依据、未知项及阻塞交给调用方和 T3。资料不足或工具失败时明确报告部分完成或阻塞，不以文件存在代替验收。方案设计结束后停止，不执行算法实现或后续比赛阶段。旧的 solution-discovery 保留但不再是主链路依赖。

如果调用方明确指定从 T3 交接进入服务适配，接收 CompetitionSpec、已验证的 Runnable Solution、模型资源和独立产物目录；核对协议、资源校验及本地推理证据，复用已有算法实现服务，产出 ServiceArtifact、ServiceContract、启动说明和实际接口验证记录供 T5 使用。记录未验证的约束及冲突，错误响应不得伪装成成功预测。不得因此重新执行 T1–T3、构建镜像或提交。这个交接约定不代表完整工作流已自动串通或通过验收。
