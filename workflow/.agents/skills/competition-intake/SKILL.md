---
name: competition-intake
description: 从 Darwin 比赛 URL 和关联资料生成可追溯的 CompetitionSpec；仅执行比赛需求理解阶段。
---

# 比赛需求理解

接收 Darwin 比赛详情 URL 和产物目录。只开展本阶段，不检索解法、不下载数据或模型、不提交比赛。使用已有 Darwin 和飞书 CLI；先查看其帮助确认参数，不重新实现平台接口。若工具、认证或网络不可用，记录实际错误和未核验项，不伏造结果。

1. 从 URL 提取比赛查询 ID，调用 Darwin CLI 获取详情，保留查询 ID 与返回的内部 ID，不假定它们相同。读取详情中关联的飞书文档；对文档引用的接口表格等关键资料也用现有飞书 CLI 获取。记录每个来源 URL、可用的版本及获取结果。复用已有资料时必须区分历史资料和本次实际获取的内容。
2. 在指定产物目录写入 `competition_spec.json` 和 `evidence.md`。JSON 顶层包括 `schema_version`、`sources`、`competition`、`task`、`data`、`input`、`output`、`service`、`environment`、`submission`、`conflicts`。各项关键事实须带 `sources` 引用，可增加比赛确有需要的字段；不清楚的值使用 `unknown` 明确描述，不能猜测。来源矛盾时记录各方原文含义、来源和未解决状态，不擅自裁定。
3. `evidence.md` 列出实际执行的命令、结果、原始来源位置和关键事实对应关系，以及未核验事项；不得记录凭证。记录足够信息供独立核对。用 `python3 -m json.tool` 检查产物。若来源不可获取，标明部分完成或阻塞，不声称验收通过。

CLI 可使用 PATH 中的 `darvin` 和 `lark-cli`；若不在 PATH，调用方可提供现有可执行文件的绝对路径。产物目录由调用方明确指定；下游只需读取其中的 JSON 和证据文件，不依赖对话历史。
