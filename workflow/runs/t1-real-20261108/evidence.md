# TICKET-1 证据 — 图像真伪鉴定榜 (subnetId=196) 需求理解

- 执行时间：2026-11-08 14:33–14:38（Asia/Shanghai，UTC+8）
- 产物目录：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108`
- 范围：仅比赛需求理解（darwin-workflow → competition-intake）。未下载数据/模型，未提交比赛，未修改 run 目录以外任何文件。
- 网络：全部外网命令均显式使用免流量代理前缀
  `env HTTP_PROXY=http://172.28.4.16:18999 HTTPS_PROXY=http://172.28.4.16:18999 http_proxy=http://172.28.4.16:18999 https_proxy=http://172.28.4.16:18999 NO_PROXY=localhost,127.0.0.1,172.28.4.16 no_proxy=localhost,127.0.0.1,172.28.4.16`，未使用其他代理。
- 数据新鲜度：本文件全部事实来自本次实际获取的原始输出（见下），未使用任何旧快照；与历史资料无关。

## 1. 工具

| 工具 | 精确路径 | 版本/说明 |
|---|---|---|
| Darwin CLI | `/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin` | 可执行，帮助正常 |
| 飞书 CLI | `/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/lark-cli-1.0.98/lark-cli` | v1.0.98（提示有 1.0.99，未升级，按既有版本使用） |

认证检查：`darvin auth inspect` 退出码 0，status=success，state=authenticated，live capabilities 含 `solution.submit eligible`。身份状态仅记录到 authenticated，不记录地址等身份细节。

## 2. 实际执行的命令与结果

以下命令均带上述代理前缀（下文省略前缀，标注 [proxy] 表示已加）；退出码均为 0，stderr 均为空（见各 `.err`/`.stderr` 文件，0 字节）。

1. `[proxy] darvin auth inspect` → success，authenticated（能力清单见上）。
2. `[proxy] darvin subnet inspect 196 --json > raw_subnet_196.json`
   - 结果：status=success，profile=prod，duration_ms=2034，warnings=[]，errors=[]。
   - 关键字段：backend_id=196，subnet_id=85（内部 ID 与查询 ID 不同，均已保留），name=图像真伪鉴定榜，contract=0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb，status=ACTIVE，stage=IN_PROGRESS，submission_type=DockerImage，evaluation_mode=automatic，solutions=114，participants=11，datasets=1，task_type='-'。
   - description 为完整 Markdown（原文已存档于 raw_subnet_196.json），内嵌 3 个飞书文档链接（见第 3 节来源映射）。
3. `[proxy] lark-cli docs +fetch --doc https://my.feishu.cn/docx/GguVdTxCBoGul4xqTPscxfztn6g --doc-format markdown > raw_doc1_bangdan_jieshao.md`
   - 结果：ok=true，identity=user，document_id=GguVdTxCBoGul4xqTPscxfztn6g，revision_id=56。
4. `[proxy] lark-cli docs +fetch --doc https://my.feishu.cn/docx/NSsFdVE57o0xemxcWRkcpFswnkh --doc-format markdown > raw_doc2_xunlianji.md`
   - 结果：ok=true，document_id=NSsFdVE57o0xemxcWRkcpFswnkh，revision_id=15。
   - 内容：两个 zip 附件卡片（训练集 1 0_1.zip，139334730 字节，token Ofj7bQtFMoe66fxcCGMc9pBSnug；训练集 0_2.zip，437962033 字节，token Hab7b2O8lo6LCaxXjaNc1jV5nQh）。附件未下载（超出 intake 范围）。
5. `[proxy] lark-cli docs +fetch --doc https://scn6dw1sar4n.feishu.cn/wiki/OLL0wZi94ilpgKkTHmkcXNVCn7f --doc-format markdown > raw_doc3_tuili_jiekou.md`
   - 结果：ok=true，wiki 节点解析为 document_id=HL7JdRbb6ovlP1xwgN3cnNy7n3g，revision_id=29。
   - 内容：/ready 探活、POST /api/v1/image-authenticity 请求/响应示例、starting-kit GitLab 链接、内嵌电子表格引用（token=Gz7OsS2NIhYCYCt09ybca1Y6nud，sheets RUblU0/Cl5ExX/G2lxWB）。
6. `[proxy] lark-cli sheets +csv-get --spreadsheet-token Gz7OsS2NIhYCYCt09ybca1Y6nud --sheet-id RUblU0 --format csv > raw_sheet_RUblU0.csv` → ok=true，revision=26，actual_range=A1:B5，has_more=false。
7. 同 6，`--sheet-id Cl5ExX > raw_sheet_Cl5ExX.csv` → ok=true，actual_range=A1:D3，has_more=false。
8. 同 6，`--sheet-id G2lxWB > raw_sheet_G2lxWB.csv` → ok=true，actual_range=A1:C4，has_more=false。

只读帮助检查（不产生外部请求，无 [proxy]）：`darvin --help`、`darvin subnet --help`、`darvin subnet inspect --help`、`darvin auth --help`、`darvin dataset --help`、`darvin solution --help`、`darvin solution submit --help`、`lark-cli --help`、`lark-cli docs --help`、`lark-cli wiki --help`、`lark-cli docs +fetch --help`、`lark-cli sheets --help`、`lark-cli sheets +csv-get --help`。

未执行任何写操作命令（无 darvin solution submit / dataset upload / lark-cli 写类命令）。

## 3. 来源清单与原始文件

| ID | 来源 | 版本 | 原始文件（本目录） |
|---|---|---|---|
| S1 | Darwin 平台 subnet inspect 196（URL: https://darvin.originlabs.cc/subnet/detail?subnetId=196） | envelope schema_version=1, profile=prod, 2026-11-08T06:34:14Z | raw_subnet_196.json（+ raw_subnet_196.stderr 0 字节） |
| S2 | 飞书 docx《图像真伪鉴定榜》https://my.feishu.cn/docx/GguVdTxCBoGul4xqTPscxfztn6g | revision 56 | raw_doc1_bangdan_jieshao.md（+ raw_doc1.err 0 字节） |
| S3 | 飞书 docx《图像鉴定-训练集》https://my.feishu.cn/docx/NSsFdVE57o0xemxcWRkcpFswnkh | revision 15 | raw_doc2_xunlianji.md（+ raw_doc2.err 0 字节） |
| S4 | 飞书 wiki《图像真伪鉴定榜接口文档》https://scn6dw1sar4n.feishu.cn/wiki/OLL0wZi94ilpgKkTHmkcXNVCn7f → doc HL7JdRbb6ovlP1xwgN3cnNy7n3g | revision 29 | raw_doc3_tuili_jiekou.md（+ raw_doc3.err 0 字节） |
| S5 | 飞书电子表格 Gz7OsS2NIhYCYCt09ybca1Y6nud（S4 内嵌），sheets RUblU0/Cl5ExX/G2lxWB | revision 26 | raw_sheet_RUblU0.csv / raw_sheet_Cl5ExX.csv / raw_sheet_G2lxWB.csv（+ 3 个 0 字节 .err） |

S1 description 中引用的 3 个飞书链接与 S2/S3/S4 一一对应，无遗漏；S4 引用的接口表格（S5）已全部获取。

## 4. 关键事实 → 来源映射（摘要）

- 比赛名/状态/内部 ID(85)/契约地址/评测模式自动/提交类型 DockerImage → S1
- 三分类定义（1 / 0_1 / 0_2）、数据域范围（文档类/风景类/人物动物类）、输入格式 → S2
- 主排序指标 f1_0=(f1_0_1+f1_0_2)/2 与监测指标清单 → S1、S2（一致）
- 资源限制 1/2 A100-40g 显存、2c4g → S2
- 服务要求：监听 0.0.0.0:80、GET /ready、POST /api/v1/image-authenticity → S1、S4、S5（一致）
- 请求参数 image_base64（不含 data: 前缀）/ image_format；响应 success/message/result → S5（+ S4 示例一致）
- 评测请求只含图片内容与格式、顺序随机 → S4
- 训练数据两个 zip（仅 0_1、0_2）及附件 token/大小 → S3
- 提交 YAML：inferenceImage、inferenceVolumeMounts（name=model、source=ceph_customer 固定） → S1
- starting-kit 参考仓库（未获取） → S4

## 5. 冲突记录（未裁定）

- **C1 评测失败判定**：S1「任意样本重试后仍推理失败 → 本次评测无有效排行榜成绩」vs S2「请求失败率超过 5%（返回结果为空）判定失败」。两者口径不一致，保留原文，未擅自裁定。
- **C2 提交形式**：S1/S4 一致指向 Docker 镜像提交（SUT 镜像实现接口）；S2「提交方式」节写「提交结果文件」。未核验哪个为最新口径，保留记录。

## 6. 未核验事项 / unknown

- 截止时间、提交次数限制：所有来源均未提供。
- 1 类（原生无修实拍图）训练数据：S3 未列出对应附件。
- 平台 dataset（S1 显示 datasets=1）内容：darvin CLI 无只读列举命令（仅 upload），未核验。
- starting-kit GitLab 仓库可用性与内容：外部代码参考，非飞书资料，本阶段未获取。
- 测试集规模/分布：来源未提供。
- “2c4g”单位、文件名“训练集 1 0_1.zip”中“1”的含义：按原文保留，未解释。
- task_type：S1 返回 '-'，记为 unknown。
- S1 与 S2 指标名称语言差异已核对为同一组指标，无冲突。

## 7. 产物与验证

- `competition_spec.json`：顶层含 schema_version、sources、competition、task、data、input、output、service、environment、submission、conflicts（另加 unknowns）；关键事实带 sources 引用；不清楚值记为 unknown。
- 验证命令：`python3 -m json.tool competition_spec.json` → 退出码 0（JSON 可解析）。
- 凭证：本文件与 spec 中未记录任何 token/密码/API Key（飞书附件 token 属公开文档资源标识，非凭证，已按来源要求保留以便后续下载核对）。
