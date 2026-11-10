# T3 Baseline Implementation 运行报告（2026-11-10）

## 1. 任务边界与 skill 指引采用情况

- 已实际读取 `.agents/skills/darwin-workflow/SKILL.md`。该 skill 是 T1→T2 的编排指引，其中适用于 T3 的部分：
  - “若输入为已有 CompetitionSpec，读取并检查该文件，不重新执行需求理解” → 本次直接读取并校验了 `runs/t1-real-20261108/competition_spec.json` 与 `runs/t2-solution-planning-20261109-bounded/solution_plan.json` 均可解析为 JSON，未重跑 intake/planning。
  - “不以文件存在代替验收” → 本报告全部结论附实际执行证据（命令、退出码、输出、日志文件），不是只确认文件存在。
  - “资料不足或工具失败时明确报告部分完成或阻塞” → 首次独立键/形状核对暴露了 `num_batches_tracked` 差异（见 §5.3），按证据修正后才放行。
- 该 skill 中“方案设计结束后停止”以及 T2 计划里的训练/服务化/容器/提交流程均属本任务边界之外；按任务指令执行：只实现并验证最小三分类 Runnable Solution，不训练、不起 HTTP 服务、不做 Docker/镜像/Darwin 提交、不做多轮调优、不做严格容器资源测试、不实现出错固定返回类别的兜底。

## 2. 方案与模型来源（复用既有本地资源，未复制权重/数据、未下载、未联网）

- 模型：旧工程 `image_auth_repo/model_train` 中训练好的小型三分类 CNN（torch `state_dict`），**`out/model_full.pt`**（1,574,261 B，mtime 2026-11-03 21:26，全量数据训练、deploy 候选）。
  - 结构：4×(Conv3x3 pad=1 → BatchNorm → ReLU → MaxPool2)，通道 3→32→64→128→256 → AdaptiveAvgPool → Linear(256,3)；390,147 参数（本次独立求和确认，与 `out/train_report.json` 的 `params` 一致）。
  - 训练数据（旧记录，仅引用）：1,182 图，类计数 1:400 / 0_1:382 / 0_2:400；`train_report.json` 记录 valbest 的 val acc 0.678、val f1_0 0.7052（参考指标，非本次测量、非承诺）。
- 参考代码（只读）：`model_train/train.py`（Net/CLASSES/预处理/数据类根）、`model_train/export_numpy.py`（torch→numpy 导出与对拍口径）、`starting-kit/serve_model.py`（numpy 推理，同构对照）、`starting-kit/model_weights.npz`（1,571,082 B，同权重的 numpy 导出）。
- T2 计划（从零训练 + serve + Docker + 提交）整体不执行；T3 仅复用其引用的既有模型做最小可运行推理，符合“可以复用合适的已有模型，无需训练”的授权。

## 3. 独立核对结果（结构 / 标签 / 权重 / 预处理）

`predict.py` 未 import 旧工程代码，而是独立重写 `Net` 并做键名+形状白名单校验后 `strict=True` 加载：

| 项 | 旧工程定义 | 本次实现/核对 | 结论 |
|---|---|---|---|
| 结构 | train.py `Net`（4 conv+BN 块 + GAP + Linear(256,3)） | predict.py `make_net()` 逐层对照 | 一致；state_dict 30 键（25 参数张量 + BN 缓冲）全部通过键/形状断言 |
| 参数量 | train_report.json: 390,147 | 本次 `sum(p.numel())` = 390,147 | 一致 |
| 标签映射 | `CLASSES = ["1","0_1","0_2"]`（train.py 与 serve_model.py 相同顺序），argmax 索引→类别 | 同序；并用 **V2 fc 行置换实验**证明标签确实经由 fc 行索引产生（见 §5.2） | 一致 |
| 权重加载 | `torch.save(model.state_dict())` | `torch.load(map_location="cpu")` + strict + 键形状校验；另用 **V1 对拍** 与旧工程 numpy 导出（`model_weights.npz`，由 export_numpy.py 生成）比较 logit | 一致（max |Δlogit| = 3.6e-07，argmax 6/6 相同） |
| 预处理 | train.py `load_item`(val 分支)+`to_tensor`；serve_model.preprocess：PIL→RGB→resize 160×160 BILINEAR→/255→(x-0.5)/0.5→CHW float32 | predict.py `preprocess()` 同流程（BN 在 eval 模式使用 running stats，与训练 val 分支等价） | 一致 |

## 4. 环境与依赖

- 解释器：`/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python`（Python 3.10.21）。选 evo 的原因：旧工程 `model_train/__pycache__/train.cpython-310.pyc` 表明训练即在 3.10 环境执行，与本次一致。
- 依赖（均为环境既有，未安装任何包、未联网）：torch 2.8.0+cu128（本机无 GPU，全程 CPU：`map_location="cpu"`）、numpy 1.26.4、Pillow 12.2.0。
- 备选环境 `qwen`（Python 3.11.16，torch 2.9.0+cu128，numpy 2.2.6，Pillow 12.0.0）已检查可 import 同名包，但本次未使用。
- 数据（只读引用，未复制）：`/mnt/disk3/liuyutong_home/workspace/darwin_auto/datasets/image_auth/`，类根与 train.py 一致：`train_1_0_1/1/`、`train_1_0_1/0_1/`、`train_0_2/训练集 0_2/0_2/`，子类 人物/风景/动物/文字，格式 jpg/png。
- 注意（继承 T2 观测）：`/mnt/disk3/liuyutong_home/workspace/darwin_auto` 曾出现 ro 挂载内容波动。本次（2026-11-10 10:18–10:23 +08:00）所有路径核实可用；T4 复用前请先执行 §7 的 preflight 命令。

## 5. 实际运行与验证证据

### 5.1 推理运行（6 张不同类别真实样例）

- 命令与完整输出：`logs/predict_run.log`（含逐条输入路径、`exit_code=0`、完整 JSON 输出）；stderr 为空（`logs/predict_run.stderr`，0 B）；结构化结果：`results/predictions.json`。
- 样例选择（`samples.txt`，每类 2 张、跨子类、含 1 张 PNG）：

| 输入路径（datasets/image_auth 下） | 路径标签 | 模型预测 | softmax 概率 [1, 0_1, 0_2] |
|---|---|---|---|
| train_1_0_1/1/人物/00a81fa0…b10d.jpg | 1 | 0_1 | [0.126, 0.551, 0.323] |
| train_1_0_1/1/风景/0025d7f1…39b7.jpg | 1 | 1 | [0.854, 0.049, 0.097] |
| train_1_0_1/0_1/人物/00e6b1e3…2b34.png | 0_1 | 0_1 | [0.247, 0.675, 0.078] |
| train_1_0_1/0_1/文字/002edfff…cacef.jpg | 0_1 | 1 | [0.574, 0.358, 0.068] |
| train_0_2/训练集 0_2/0_2/人物/002b3da4…e10e.jpg | 0_2 | 0_2 | [0.211, 0.099, 0.690] |
| train_0_2/训练集 0_2/0_2/风景/00b5cdd2…b534.jpg | 0_2 | 0_2 | [0.217, 0.163, 0.620] |

- 6 张中 4 张与路径标签一致。**预测与标签分别记录，不声称预测一定正确**；样例同时是模型训练数据，一致率不具泛化含义。
- 6 张图预测覆盖 `1 / 0_1 / 0_2` 三个类别且 logit 各不相同 → 输出随图像内容变化。
- 批量 6 图总耗时 139–160 ms（含 torch 初始化，CPU）。

### 5.2 “输出来自模型而非固定类别”验证（`logs/verify_run.log`，`exit_code=0`；结构化：`results/verify.json`，`all_pass: true`）

- **V1 torch↔numpy 对拍**：同一 `model_full` 权重，torch 路径 vs 旧工程 `serve_model.ImageAuthModel`（`model_weights.npz`）逐图比较 logit：max|Δ|=3.576e-07，argmax 不一致数 0/6 → 复用的权重文件与旧工程已验证的部署布局一致，且推理路径真实执行了前向。
- **V2 fc 行置换**：将 `fc.weight/fc.bias` 按行 (0,1,2)→(1,0,2) 置换后重跑，6/6 图 argmax 均按同一置换变化（如原索引 1→0、0→1、2→2）→ 类别标签严格经由 fc 输出行索引映射，非硬编码字符串。
- **V3 checkpoint 敏感性**：`model_full.pt` 与 `model_valbest.pt` 在同一 6 图上 1 张预测不同（002edfff…：full→0, valbest→1）→ 输出依赖具体权重文件。

### 5.3 过程中的失败与修正（证据留存）

- 首次运行 exit 1：独立键白名单发现 state_dict 多出 4 个 `net.{1,5,9,13}.num_batches_tracked`（BatchNorm 持久缓冲，train.py 未显式列出）→ 补入白名单。
- 二次运行 exit 1：`num_batches_tracked` 实际形状为标量 `()` 而非 `(1,)` → 修正形状断言。
- 两次失败均发生在“独立核对权重”这一环节并如实记录，说明核对逻辑有效；最终版全部运行 exit 0。

## 6. 产物清单（全部位于 `runs/t3-baseline-20261110/`）

| 文件 | 说明 |
|---|---|
| `predict.py` | 最小三分类推理入口（自包含：Net 定义 + 键/形状校验 + 预处理 + CLI，无旧工程 import 依赖） |
| `verify_model.py` | 一致性验证（V1/V2/V3），供 T4 复跑 |
| `samples.txt` | 6 张测试样例绝对路径（每行一个，含空格安全） |
| `results/predictions.json` | 逐图输入路径、路径标签、预测、logits、softmax 概率 |
| `results/verify.json` | V1/V2/V3 逐图明细与通过标志 |
| `logs/predict_run.log` / `logs/predict_run.stderr` | 推理运行：完整命令、输入、退出码、输出 |
| `logs/verify_run.log` / `logs/verify_run.stderr` | 验证运行：完整命令、输入、退出码、输出 |
| `run_report.md` | 本报告 |

## 7. 复现命令

```bash
cd /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t3-baseline-20261110

# preflight：确认被引用的既有路径仍可用（ro 挂载有波动史）
for f in \
  /mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_repo/model_train/out/model_full.pt \
  /mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_repo/starting-kit/model_weights.npz \
  /mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python; do test -e "$f" && echo "OK $f" || echo "MISSING $f"; done

# 推理（CPU，约 0.2s 级）
/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python predict.py --samples samples.txt --json results/predictions.json
# 或单图： ... predict.py /path/to/img.jpg --weights /abs/path/model_full.pt

# 一致性验证
/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python verify_model.py --samples samples.txt --json results/verify.json
```

## 8. 限制与风险（供 T4）

- 仅 6 图冒烟级验证；未做全量 1,182 图评估、未测延迟/内存/并发（任务边界禁止）。`model_full.pt` 无验证集指标（valbest 的 f1_0=0.7052 只属于 `model_valbest.pt`）。
- 测试样例来自训练集，标签=路径结构推断；“4/6 一致”不是泛化证据。
- 权重/数据均为外部绝对路径引用（任务要求不复制）；若 T4 时挂载波动导致路径缺失，需先恢复引用源再运行，不要在本目录伪造副本。
- 预处理未处理 EXIF 旋转、截断图（与训练时 val 分支行为一致：直接 RGB resize；训练分支的随机裁剪/翻转/噪声仅训练态使用）。
- `predict.py` 出错时向 stderr 报错并 exit 非 0（任务禁止“固定返回类别”兜底）；T4 若要做零失败服务层，应在 T4 自行设计兜底策略并与 spec 冲突 C1 对齐。
- torch 为 cu128 构建但本机无 GPU，全程 CPU；如 T4 换环境，请保持 `map_location="cpu"` 行为或自行适配。

## 9. T4 交接要点

- 可直接复用：`predict.py`（推理内核 `load_model`/`preprocess`/`predict_image` 可作为服务层或批量推理的 import 目标）、`samples.txt`、`results/*.json`（作为基线对照）。
- 契约参考（不属 T3 实现范围）：spec R3–R5（POST /api/v1/image-authenticity，{success,message,result}，result∈{1,0_1,0_2}）。
- 服务层/容器/提交相关决策点仍为 T2 所列 D1（registry）、C2（提交形式口径）、D5（docker 可用性），T3 未触碰。
