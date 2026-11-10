# TICKET-2 evidence log (independent solution discovery)

Run: t2-adaptable-20261108 / independent-paid-20261109
Started: 2026-11-09 (Asia/Shanghai). Scope: TICKET-2 only (discovery + verification), no reproduction/training (TICKET-3).

## Task summary (from competition_spec.json, TICKET-1)

- 三分类图像鉴定: `1` 原生无修实拍图 / `0_1` 已修图(人工+AI局部) / `0_2` AI 全图生成。
- 域: 文档类(发票/转账记录等)、风景类、人物动物类。
- 排序指标: F1_0 = (F1_0_1 + F1_0_2) / 2（**不含类 1**）。
- 接口: POST /api/v1/image-authenticity (json: image_base64, image_format) → {success,message,result∈{"1","0_1","0_2"}}; GET /ready:80; 镜像 linux/amd64。
- 评测无图片 ID/文件名/路径/真实标签，顺序随机。
- 失败口径冲突 C1: S1 零容忍 vs S2 >5% 失败率（未裁定）。
- 提交形式冲突 C2: 镜像 vs "提交结果文件"（未裁定，倾向镜像）。
- 资源（S2 原文）: "1/2 A100-40g显存，2c4g"。按 ticket 指示**暂按 2 核 CPU / 4GB 内存**作为部署侧检查假设（非官方核实值，单位未注明，spec unknowns 已记录）。GPU 表述 "1/2 A100-40g" 含义未裁定（1 到 2 张 A100-40G？半张 A100？）。
- 训练附件（S3 文档，revision 15）:
  - "训练集 1 0_1.zip" size=139,334,730 B, token=Ofj7bQtFMoe66fxcCGMc9pBSnug
  - "训练集 0_2.zip" size=437,962,033 B, token=Hab7b2O8lo6LCaxXjaNc1jV5nQh
  - **无类 1（原生无修实拍图）zip**（spec unknown 已确认，来自 S3 全文，仅两个 figure）。
- starting-kit 参考: https://gitlab.4pd.io/gaoziming/image_authenticity_verification_leaderboard/-/tree/main/starting-kit （未核验，待查）

## Local environment (verified 2026-11-09)

- 训练侧机器: 128 CPU, 2TB RAM, /mnt/disk3 剩余 4.9TB（`nproc`/`free -h`/`df -h`）。
- 默认 python3 无 torch（与 TICKET-2 无关，记录备查）。
- 部署资源与训练资源区分: 部署 = 比赛 SUT 容器（暂按 2c4g + 1/2 A100-40g，见上）；训练 = 本机，不受部署限制约束。

## Network plan (per ticket)

- 免流优先: http://172.28.4.16:18999（hf-mirror 200 已验证; github.com 超时已验证）。
- 付费备用: http://127.0.0.1:7589（mihomo v1.19.33 监听已验证; github.com 200 已验证）。仅小型查询。
- 每步记录实际代理与 HTTP 状态。

## Investigation log

(append as verification proceeds)
