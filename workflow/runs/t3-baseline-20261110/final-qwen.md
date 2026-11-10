

T3 完成。所有产物仅落在 `runs/t3-baseline-20261110/` 内，未动 T2、旧工程或其他文件；全程无下载、无安装、无联网、无 HTTP/Docker/提交。

**方案**
- 复用旧工程既有模型 `image_auth_repo/model_train/out/model_full.pt`（390,147 参数小 CNN，160×160，三类 `1/0_1/0_2`，全量 1,182 图训练），未重新训练。
- `predict.py` 自包含：独立重写 `Net`，state_dict 键名+形状白名单校验后 `strict` 加载；预处理 RGB→160 BILINEAR→(x−0.5)/0.5；出错时 stderr+非 0 退出，无固定类别兜底。
- 环境 `evo`（Py3.10.21 + torch 2.8.0 CPU + numpy 1.26.4 + PIL 12.2.0），与旧训练 pyc 的 3.10 一致；`qwen` 环境已检查但未用。

**独立核对与"非固定输出"验证**（`results/verify.json`，`all_pass: true`）
- 结构/参数量与 `train_report.json` 一致；标签顺序与 `train.py`/`serve_model.py` 相同，且 V2 实验把 fc 行按 (0,1,2)→(1,0,2) 置换后 6/6 图 argmax 按同一置换变化，证明标签走 fc 行索引。
- V1：torch 路径 vs 旧工程 numpy 导出（`model_weights.npz`）max|Δlogit|=3.6e-07、argmax 0 不一致。
- V3：`model_full.pt` 与 `model_valbest.pt` 在同一 6 图上 1 张预测不同，证明输出依赖具体权重。

**实际运行**
- 6 张不同类别真实样例（每类 2 张、跨子类、含 PNG）：`logs/predict_run.log` 记录完整命令、`exit_code=0`、完整输出；预测 4/6 与路径标签一致，覆盖全部三个类别、logit 各异。预测与标签分列记录（`results/predictions.json`），不声称预测正确；样例来自训练集，一致率非泛化证据。
- 首次运行两次 exit 1 均由独立键/形状核对捕获（`num_batches_tracked` 键缺失、形状为标量），修正后放行——过程证据已写入报告 §5.3。

**交接与限制**
- 复现：`evo/bin/python predict.py --samples samples.txt --json results/predictions.json`（单图亦可），preflight 路径检查命令在报告 §7。
- 限制：6 图冒烟级验证、CPU-only、权重/数据为外部绝对路径引用（该 ro 挂载有波动史，T4 先跑 preflight）；`model_full.pt` 无验证集指标。
- 详见 `runs/t3-baseline-20261110/run_report.md`（含 darwin-workflow SKILL.md 的 T3 适用指引说明：只读校验已有 Spec/Plan、以运行证据代替"文件存在"、阻塞如实上报；训练/服务化/容器属任务边界外未执行）。

需要的话，我可以下一步补一个 100 张级批量评估脚本（纯本地，供 T4 对照基线）。