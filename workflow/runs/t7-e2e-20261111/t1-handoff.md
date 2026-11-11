# T1 交接 — 需求理解（复用 + 本次平台复查）— t7-e2e-20261111

## 处置
- 复用：`runs/t1-real-20261108/competition_spec.json`（T1 real 2026-11-08 产物，含 S1–S5 来源与 raw 文件）。
- 本次新执行：`darvin subnet inspect 196 --json` 与 `darvin auth inspect --json`（只读，经已验证 7589 代理，各 1 次请求）。

## 本次命令与结果
```sh
/mnt/disk3/liuyutong_home/workspace/darvin_auto/runtime/venv/bin/darvin subnet inspect 196 --json
# → t1/raw_subnet_196_t7e2e.json, exit 0, envelope status=success, duration 939ms
/mnt/disk3/liuyutong_home/workspace/darvin_auto/runtime/venv/bin/darvin auth inspect --json
# → t1/t1-auth-inspect.json, exit 0, envelope status=success
```
执行时间 2026-11-11T02:51Z。

## 一致性核验（本次）
- spec JSON 可解析（本次验证）；`generated_at=2026-11-08T06:37:00Z`，source_url 与本次任务 URL 一致。
- 平台复查：`图像真伪鉴定榜`，backend_id=196，subnet_id=85，contract_address=`0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb`，status=ACTIVE/IN_PROGRESS，submission_type=DockerImage，evaluation_mode=automatic，datasets=1。
- 与 11-08 raw 及今日 08:46 dry run raw 逐字段对比：**仅计数变化**（solutions 114→125→127，participants 11→12）；description/文档 URL/提交类型/合约地址均未变。
- 认证：authenticated（wallet 0x82…2e4e，公开地址）；capabilities：`solution.submit=eligible`、`task.create=eligible`、`subnet.create=eligible`。

## 关键要求（继承 spec，未变）
- 三分类图像鉴定（1 / 0_1 / 0_2）；排行分 f1_0=(f1_0_1+f1_0_2)/2。
- 服务契约：HTTP 监听 0.0.0.0:80；GET /ready；POST /api/v1/image-authenticity（JSON: image_base64+image_format → {success,message,result}）。
- 提交形式：Docker 推理镜像（S1+S4；C2 与 S2 表述冲突未裁定，继承记录）。

## 未知/冲突（继承，未变）
- C1：失败口径（零容忍 vs 5%）未裁定；C2：提交形式表述冲突未裁定。
- 平台侧积分/冷却、Harbor 拉取凭据等仍属提交时/运行时确认项。

## 输出
- 交接文件：本文件；spec 路径：`runs/t1-real-20261108/competition_spec.json`。
