---
name: solution-planning
description: 根据 CompetitionSpec 自主设计可交给实现阶段的简单比赛 Baseline，输出结构化 SolutionPlan。
---

# Solution Planning

读取指定 CompetitionSpec，区分已确认要求、未知项和假设，理解任务、数据、协议和资源约束。检查必要的现有本地依赖与资源，设计最简单合理的方案；不要求搜索、下载、第三方权重或复现。不可把未经核实的环境或数据可用性写成事实。

在指定目录写入 `solution_plan.json`，使用 JSON 对象，至少包含：`competition_spec`（来源路径）、`task`、`confirmed_requirements`、`algorithm`（思路及选择理由）、`inputs_outputs`、`dependencies`（本地可用性及未确认项）、`resource_assumptions`、`implementation`（入口、步骤）、`validation`、`risks` 和 `unknowns`。内容应具体到 T3 能据此动手；不能确认的关键条件标明阻塞或待核实。

核对计划不违背已确认规格；说明已检查和未检查的可行性。仅产出计划，不编写算法、不训练、不执行后续阶段。
