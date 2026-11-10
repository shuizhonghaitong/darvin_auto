# TICKET-1 证据与完整性检查

读取日期：2026-11-08。输入 URL：https://darvin.originlabs.cc/subnet/detail?subnetId=196 。以下是只读查询结果的摘录，不是未经截断的原始响应。命令经已验证的不计费 HTTP(S) 代理 `http://172.28.4.16:18999` 执行；CLI 路径相对于旧工程 `/mnt/disk3/liuyutong_home/workspace/darwin_auto`。

## 比赛详情与文档读取

- `runtime/venv/bin/darvin subnet inspect 196 --json`：成功。返回查询后台 ID 196、子网 ID 85，名称「图像真伪鉴定榜」，状态 ACTIVE / IN_PROGRESS，提交类型 DockerImage、自动评测。详情列出下列三份文档；还描述三类标签、F1 评分、Docker 提交与服务要求，整理见 CompetitionSpec。
- `runtime/lark-cli-1.0.98/lark-cli docs +fetch --doc https://my.feishu.cn/docx/GguVdTxCBoGul4xqTPscxfztn6g --doc-format markdown`：成功，修订 56。包含任务分类、图片类型、资源、提交和评测说明；其中结果文件提交和失败率条件与比赛详情存在冲突。
- `runtime/lark-cli-1.0.98/lark-cli docs +fetch --doc https://my.feishu.cn/docx/NSsFdVE57o0xemxcWRkcpFswnkh --doc-format markdown`：成功，修订 15。列出两个训练集附件 `训练集 1 0_1.zip`（139334730 字节）及 `训练集 0_2.zip`（437962033 字节）；未下载附件。
- `runtime/lark-cli-1.0.98/lark-cli docs +fetch --doc https://scn6dw1sar4n.feishu.cn/wiki/OLL0wZi94ilpgKkTHmkcXNVCn7f --doc-format markdown`：成功，文档 ID `HL7JdRbb6ovlP1xwgN3cnNy7n3g`，修订 29。提供端口、就绪检查、推理接口、示例、嵌入表格和 [starting-kit](https://gitlab.4pd.io/gaoziming/image_authenticity_verification_leaderboard/-/tree/main/starting-kit) 链接；未运行或下载该项目。
- 接口表格：`runtime/lark-cli-1.0.98/lark-cli sheets +cells-get --spreadsheet-token Gz7OsS2NIhYCYCt09ybca1Y6nud --sheet-id RUblU0 --range A1:H20 --max-chars 5000`：成功，修订 26，实际 A1:B5；确认 POST、路径和 JSON。
- 请求字段表：同一命令将 `--sheet-id` 换为 `Cl5ExX`，范围 `A1:H30`、`--max-chars 8000`：成功，实际 A1:D3；两个字符串参数均必填，Base64 不含 Data URL 前缀。
- 响应字段表：同上将 `--sheet-id` 换为 `G2lxWB`：成功，实际 A1:C4；确认 success 为 Boolean，message 和 result 为 String，result 为三种分类之一。三表返回 `has_more: false`、`truncated: false`。

## 关键输入输出完整性

| 项目 | 状态及来源 |
| --- | --- |
| 方法、路径、类型 | 已核对：POST `/api/v1/image-authenticity`，`application/json`；接口文档及接口表 |
| 输入 `image_base64` | 已核对：必填字符串，裸 Base64；请求字段表 |
| 输入 `image_format` | 已核对：必填字符串，示例 jpg/jpeg/png；请求字段表 |
| 其他输入上下文 | 已记录不提供 ID、文件名、路径及标签；接口文档 |
| 输出 `success` / `message` | 已核对：Boolean / String；响应字段表 |
| 输出 `result` | 已核对：字符串 `1`、`0_1`、`0_2`；响应字段表及接口文档 |
| 错误响应和 HTTP 状态码 | 未知，不能从已读资料确认 |
| 就绪检查 | GET `/ready`、端口 80；接口文档；响应体及超时未知 |
| 提交方式及失败条件 | 来源冲突，见 CompetitionSpec `conflicts`；需平台确认，不能视为已解决 |

本次没有下载训练集或构建、提交镜像。完整性检查说明已知及未知信息，不表示比赛端到端已完成。
