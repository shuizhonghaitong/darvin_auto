# 证据 — 图像真伪鉴定榜 (Darwin subnet 196) 比赛需求理解

- 阶段：competition-intake（仅需求理解；未检索解法 / 未下载数据或模型 / 未提交比赛）
- 生成时间：2026-11-08T05:30:20Z (13:30 CST)
- 产物目录：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/subnet-196/01-competition/`
- 目标输入 URL：`https://darvin.originlabs.cc/subnet/detail?subnetId=196`
- 工具链：`darvin 0.5.2`（`/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin`）、`lark-cli 1.0.98`（`/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/lark-cli-1.0.98/lark-cli`），profile=prod
- 说明：本次 raw 文件（`subnet_inspect_fresh.json`、`fresh_doc*.md`、`fresh_sheet*.csv`）为调用方本次真实 CLI 抓取并已落盘。本回合基于这些已抓取文件做内容核对与 spec 生成，未重新发起网络抓取；命令为按 CLI `--help` 与文件内嵌元数据重建的确切语法，供独立复现。

## 1. 实际执行的命令（本回合，均为只读/本地）

```bash
# 定位 CLI（非 PATH，绝对路径）
find /mnt/disk3/liuyutong_home -maxdepth 6 -name darvin -o -name lark-cli

# 核对 CLI 版本与命令语法（本地，无网络）
/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin --version                # -> 0.5.2
/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin subnet inspect --help    # identifier {backend_id|contract} ; --profile ; --json
/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/lark-cli-1.0.98/lark-cli --version        # -> lark-cli version 1.0.98
lark-cli docs --help        # 子命令含 +fetch
lark-cli docs +fetch --help # --doc <url|token> --doc-format markdown --revision-id ...
lark-cli sheets +csv-get --help # --spreadsheet-token/--url (XOR) --sheet-id/--sheet-name (XOR) --range
```

### 抓取 raw 的确切命令（由文件内嵌元数据 + CLI help 重建，供复现）

```bash
# 1) Darwin 子网详情 -> raw/subnet_inspect_fresh.json
darvin subnet inspect 196 --json --profile prod
#    started_at 2026-11-08T05:22:54.754357Z, status success, duration_ms 2176

# 2) 榜单介绍文档 -> raw/fresh_doc1_introduction.md
lark-cli docs +fetch --doc "https://my.feishu.cn/docx/GguVdTxCBoGul4xqTPscxfztn6g" --doc-format markdown
#    document_id GguVdTxCBoGul4xqTPscxfztn6g, revision_id 56

# 3) 训练集文档 -> raw/fresh_doc2_training_set.md
lark-cli docs +fetch --doc "https://my.feishu.cn/docx/NSsFdVE57o0xemxcWRkcpFswnkh" --doc-format markdown
#    document_id NSsFdVE57o0xemxcWRkcpFswnkh, revision_id 15

# 4) 推理接口 wiki 文档 -> raw/fresh_doc3_inference_interface.md
lark-cli docs +fetch --doc "https://scn6dw1sar4n.feishu.cn/wiki/OLL0wZi94ilpgKkTHmkcXNVCn7f" --doc-format markdown
#    wiki node OLL0wZi94ilpgKkTHmkcXNVCn7f, document_id HL7JdRbb6ovlP1xwgN3cnNy7n3g, revision_id 29

# 5) 三张接口表格（同一电子表格 token Gz7OsS2NIhYCYCt09ybca1Y6nud, revision 26）
lark-cli sheets +csv-get --spreadsheet-token Gz7OsS2NIhYCYCt09ybca1Y6nud --sheet-id RUblU0   # -> raw/fresh_sheet_RUblU0.csv (A1:B5 接口说明)
lark-cli sheets +csv-get --spreadsheet-token Gz7OsS2NIhYCYCt09ybca1Y6nud --sheet-id Cl5ExX   # -> raw/fresh_sheet_Cl5ExX.csv (A1:D3 请求参数)
lark-cli sheets +csv-get --spreadsheet-token Gz7OsS2NIhYCYCt09ybca1Y6nud --sheet-id G2lxWB   # -> raw/fresh_sheet_G2lxWB.csv (A1:C4 响应要求)
```

## 2. 抓取结果与来源位置

| 来源 ID | 本地路径 | 远端 | 版本/修订 | 状态 |
|---|---|---|---|---|
| S-darvin-subnet | `raw/subnet_inspect_fresh.json` | `…/subnet/detail?subnetId=196` | darvin 0.5.2, prod, started 05:22:54Z | 成功 |
| S-darvin-subnet-hist | `raw/../raw_subnet_196.json` | 同上 | started 05:18:46Z | 成功（历史副本，字段与本次一致） |
| S-doc-intro | `raw/fresh_doc1_introduction.md` | `my.feishu.cn/docx/GguVdTxCBoGul4xqTPscxfztn6g` | doc rev 56 | 成功 |
| S-doc-trainset | `raw/fresh_doc2_training_set.md` | `my.feishu.cn/docx/NSsFdVE57o0xemxcWRkcpFswnkh` | doc rev 15 | 成功 |
| S-doc-iface | `raw/fresh_doc3_inference_interface.md` | `scn6dw1sar4n.feishu.cn/wiki/OLL0wZi94ilpgKkTHmkcXNVCn7f` | wiki node / doc HL7J…, rev 29 | 成功 |
| S-sheet-iface | `raw/fresh_sheet_RUblU0.csv` | 电子表格 token `Gz7OsS2NIhYCYCt09ybca1Y6nud` / sheet RUblU0 | rev 26, A1:B5 | 成功 |
| S-sheet-reqparams | `raw/fresh_sheet_Cl5ExX.csv` | 同上 / sheet Cl5ExX | rev 26, A1:D3 | 成功 |
| S-sheet-resp | `raw/fresh_sheet_G2lxWB.csv` | 同上 / sheet G2lxWB | rev 26, A1:C4 | 成功 |
| S-doc-failed-hist | `raw/doc1_introduction.md`(+`.err`) 等 3 组 | 同 S-doc-intro/… | — | **历史失败**：0 字节内容，`.err` 为 token/keystore 只读（沙盒内 token 刷新写失败） |

历史失败 `.err` 的原始报错（已脱敏，不含凭据/用户标识）：
`[lark-cli][WARN] uat-client: token storage is not writable while refreshing: keychain Set failed: … read-only file system`
→ 本次 `fresh_doc*.md` 对同一资源重新成功抓取，取代失败副本。

## 3. 关键事实 ↔ 来源映射

- 名称「图像真伪鉴定榜」→ S-darvin-subnet + S-doc-intro
- 查询 ID=196（=backend_id）；内部 subnet_id=85（两者不同，未假定相等）→ S-darvin-subnet
- contract_address `0x35fC…2Eb`；status=ACTIVE；stage=IN_PROGRESS → S-darvin-subnet（与 -hist 一致）
- submission_type=DockerImage；evaluation_mode=automatic；solutions=114；participants=11；datasets=1 → S-darvin-subnet
- 三分类定义（1 / 0_1 / 0_2）与 0 超类 → S-doc-intro + S-darvin-subnet + S-sheet-resp
- 主排序 f1_0=(f1_0_1+f1_0_2)/2，_score=f1_0；监测指标 10 项 → S-darvin-subnet + S-doc-intro（两处一致）
- 数据范围：文档类/风景类/人物动物类 → S-doc-intro
- 训练集：2 个 zip（`训练集 1 0_1.zip` 139334730 B≈132.9 MiB；`训练集 0_2.zip` 437962033 B≈417.7 MiB；合计≈550.6 MiB）→ S-doc-trainset；下载 token 存于该 raw，本阶段不下载
- 测试集私有：仅图片内容+格式，无 ID/文件名/路径/标签，顺序随机 → S-doc-iface
- 接口：探活 GET /ready:80；业务 POST /api/v1/image-authenticity，application/json → S-darvin-subnet + S-doc-iface + S-sheet-iface
- 请求参数：image_base64(String,必填,无前缀)、image_format(String,必填) → S-sheet-reqparams + S-doc-iface
- 响应：success(Boolean)/message(String)/result(String∈{1,0_1,0_2}) → S-sheet-resp + S-doc-iface
- 环境：1/2 A100-40g 显存、2c、4g；镜像 linux/amd64；监听 0.0.0.0:80；可选 Ceph 挂载(name=model, source=ceph_customer 固定) → S-doc-intro + S-darvin-subnet
- starting-kit 参考仓库（外部数据，未拉取）→ S-doc-iface

## 4. 冲突 / 歧义（未裁定，详见 spec.conflicts）

- **C1 失败标准**：S-darvin-subnet「任意样本重试后仍失败→本次评测无有效成绩」vs S-doc-intro「失败率>5%（返回空）」。不一致。
- **C2 提交形态**：S-darvin-subnet/S-doc-iface（Docker 镜像 + HTTP 接口，内部一致）vs S-doc-intro「提交结果文件」。不一致，severity=high。
- **C3 输出表述**：S-doc-intro「鉴定结果文件」vs S-sheet-resp/S-doc-iface「逐请求 JSON result」。与 C2 相关。
- **C4 数据计数**：S-darvin-subnet datasets=1 vs S-doc-trainset 实际 2 个 zip。可能同属一个数据集。

## 5. 未核验 / unknown 事项

- 训练集 zip 内部目录结构、标注文件格式、样本量与类别分布：unknown（需 P2 下载后核验；本阶段不下数据）。
- 测试集规模 / 分布 / 是否分轮：unknown（仅知私有、无标签、随机顺序）。
- GPU 精确配额：原文「1/2 A100-40g 显存」按字面 ≈20GB，精确分配方式 unknown。
- 延迟/超时阈值：监测 `avg_response_time_ms` 但无硬性阈值；推理超时/重试次数 unknown。
- 每队提交次数、评测频率、截止时间、排行榜更新周期：unknown（来源未提供；status=ACTIVE/stage=IN_PROGRESS）。
- 具体参赛模型 / 基线 / Ceph 模型路径：unknown（本阶段不做方案检索）。
- lark-cli 1.0.99 为可用更新（`_notice`），本次未升级（保持 1.0.98）。

## 6. 产物自检

```bash
python3 -m json.tool competition_spec.json   # -> JSON VALID（顶层含 schema_version/sources/competition/task/data/input/output/service/environment/submission/conflicts）
```
- 顶层字段齐备：schema_version, sources, competition, task, data, input, output, service, environment, submission, conflicts ✓
- 关键事实均带 sources 引用；不确定值显式 `unknown` ✓
- 证据含实际命令、结果、来源位置、事实映射、未核验项 ✓
- 历史报错已脱敏；规范和原始资料仍包含来源返回的下载或文档资源 token，未经进一步核验不得视为可公开的无敏感信息材料。

## 7. 状态结论

- 比赛需求理解：**完成**（基于本次真实 CLI 抓取资料，内容已交叉核对）。
- 资料充分性：核心需求（任务定义、类别、指标、接口、环境、提交形态）齐全；存在 4 处来源冲突/歧义（C1–C4）与若干 unknown（数据内部结构、测试集规模、配额/时限），均已在 spec 中如实记录，未擅自裁定。
- 阻塞：无（本阶段无阻塞）。后续 P2 复现需先确认 C2（提交形态=镜像接口）与 C1（失败判定）后再落地。

## 8. 真实 Codex CLI + Qwen 复核（2026-11-08）

- 使用真实 `codex exec`、本地 `qwen3.8-27b-fp8` 模型执行只读复核；运行中明确读取了 `darwin-workflow/SKILL.md` 和 `competition-intake/SKILL.md`。这是显式要求读取的证据，不代表已证明自动发现或自动触发 Skill。
- 使用旧工程的 Darwin CLI 执行 `subnet inspect 196 --json --profile prod`，以及飞书 CLI 执行 `docs +fetch --doc https://my.feishu.cn/docx/GguVdTxCBoGul4xqTPscxfztn6g --doc-format markdown`，两条命令均成功。复核使用已确认的不计费代理，未迁移 CLI。
- 重新获取的 Darwin 数据与已保存原始数据除时间字段外一致；飞书简介文档与已保存版本一致。比赛规范 JSON 可解析，记录了四项来源冲突及未确认事项。
- 本次复核重新获取了 Darwin 信息和一份飞书文档；其余两份文档和三份表格仅核对了此前保存的快照，不代表本次重新获取。原始运行事件和模型总结分别暂存于 `/tmp/darvin-t1-skill-events-20261108.jsonl` 和 `/tmp/darvin-t1-skill-final-20261108.md`，临时文件可能被系统清理，不应公开传播。
