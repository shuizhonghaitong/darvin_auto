# T3 交接 — Runnable Solution（复用 + 本次全新推理复跑）— t7-e2e-20261111

## 处置
- 复用：`runs/t3-baseline-20261110/`（predict.py 自包含推理、samples.txt、results/predictions.json 基线、run_report.md 全量核验记录：结构/标签/权重/预处理与旧工程逐项一致，V1/V2 实验在案）。
- 本次新执行：复制 `predict.py`+`samples.txt` 到本目录 `t3/`（未改旧目录），用同一解释器全新推理 6 样例。
- 未训练、未下载、未复制权重；权重按绝对路径只读引用 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_repo/model_train/out/model_full.pt`（1,574,261 B，mtime 2026-11-03）。

## 本次命令与结果
```sh
cd runs/t7-e2e-20261111/t3
/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python predict.py --samples samples.txt --json t3-rerun-predictions.json
# → t3-rerun.log / t3-rerun.stderr, exit 0（t3-rerun.exit）
```
6 样例文件存在性逐一核验 OK（含带空格路径 `训练集 0_2`）。

## 一致性核验（本次）
- 新预测序列 `0_1,1,0_1,1,0_2,0_2`，与 T3 基线、今日 08:46 network dry run 三方一致。
- 与基线逐样本 logits/probs 对比：**max|Δlogit|=0.0，max|Δprob|=0.0**（bit 级一致）。
- n=6，correct_vs_path_label=4（与基线相同；路径标签仅参考，不代表真实标签，继承基线记录）。

## 输出
- `t3/t3-rerun-predictions.json`（本次新产物）、`t3/t3-rerun.exit`、`t3/t3-rerun.log`、`t3/t3-rerun.stderr`。
- 供 T4 复用的预测基准：`t3/t3-rerun-predictions.json`（或 T3 基线 `results/predictions.json`，两者一致）。
