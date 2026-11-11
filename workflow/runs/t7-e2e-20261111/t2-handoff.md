# T2 交接 — 方案规划（复用，本次文件级核验）— t7-e2e-20261111

## 处置
- 复用：`runs/t2-solution-planning-20261109-bounded/solution_plan.json`（T2 bounded run 2026-11-09 产物）。
- 本次新执行：仅文件级核验（JSON 可解析、与 T1 spec 一致性、关键内容摘录），见 `t2/t2-file-check.json`。**未重新执行方案设计。**

## 核验结果（本次）
- plan 可解析；`generated_at=2026-11-09T22:12:28+08:00`。
- plan 引用的 spec 路径/URL/时间戳与 `runs/t1-real-20261108/competition_spec.json` 完全一致（t2-file-check.json 各 *_matches=true）。
- 任务与契约：三分类（1/0_1/0_2），HTTP 0.0.0.0:80 + GET /ready + POST /api/v1/image-authenticity，与 T1 spec 一致。

## 已记录的范围偏差（继承，非本次新产生）
- T2 计划主路线为“从零训练 MobileNetV2 + 服务化 + 镜像 + 提交”；T3 任务指令明确“后者仅供参考，不必机械执行”，且 T3–T5 实际采用**复用既有本地已训练模型**（`image_auth_repo/model_train/out/model_full.pt`）的最小路线，见 `runs/t3-baseline-20261110/run_report.md` §2 的记录。本次 T7 沿用该已验证路线，不重新训练（本次运行明确禁止训练）。
- plan 中 open_items/unknowns（C1 失败口径、C2 提交形式冲突等）原样继承至提交前检查。

## 输出
- 交接文件：本文件；核验记录：`t2/t2-file-check.json`；plan 路径：`runs/t2-solution-planning-20261109-bounded/solution_plan.json`。
