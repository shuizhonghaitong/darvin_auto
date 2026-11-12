# T3 验证记录 — ResNet-18 三分类微调（本次运行实际执行）

环境：evo (Python 3.10.21, torch 2.8.0+cu128 CPU 模式, torchvision 0.23.0)，128 核 CPU，无 GPU。
数据：本地缓存训练集（T1 §6 已核验大小与结构）：类 1 / 0_1 / 0_2 各 400 张，共 1200；分层 900 train / 300 val，seed=196。

## 训练（train.py，12 epoch，batch 32，AdamW backbone 1e-4 / head 1e-3）

| epoch | loss | val acc | f1_0 | f1_1 | f1_0_1 | f1_0_2 |
|---|---|---|---|---|---|---|
| 1 | 0.8933 | 0.6667 | 0.6796 | 0.6502 | 0.6598 | 0.6994 |
| 4 | 0.2097 | 0.7167 | 0.7606 | 0.6359 | 0.7168 | 0.8045 |
| **9 (best)** | **0.1255** | **0.7700** | **0.8056** | **0.6957** | **0.7658** | **0.8454** |
| 12 | 0.1498 | 0.7500 | 0.7833 | 0.6804 | 0.7291 | 0.8374 |

- 总训练时长 **3.9 分钟**（12 epoch）。
- best checkpoint：`model/best.pt`（44.8 MB，epoch 9，val f1_0=0.8056），`model/class_map.json`，`model/best_summary.json`。
- 训练全量日志：`train.log`。

## 本地推理验证（validate_local.py，模拟服务全链路 base64→PIL→预处理→CPU argmax）

- 抽样 30 张（三类各 10，训练集内）：27 正确（90%；val 未见样本 acc=0.77 为更保守估计）。
- 平均 **55.5 ms/张**（含 base64 往返、PIL 解码、预处理、前向），首张 284 ms（预热）。
- 平台容器限 2 CPU，预期单张 ~150–400 ms，远低于 judge 有效超时 60 s/次。
- 异常输入（截断 base64 / 空串 / 非图片字节）均按预期解码失败 → 服务将走兜底路径返回合法先验标签（main.py 已实现）。

## 产物与复用说明

- 预训练权重：`resnet18-f37072fd.pth`（本地 torch-cache，零下载），加载用可写 TORCH_HOME 副本（`t3-solution/torch-cache/`）。
- 镜像运行时轮子（经免费代理 172.28.4.16:18999 各下载一次）：
  - `vendor/torch-2.6.0+cpu-cp39-cp39-linux_x86_64.whl`（178,631,197 B，zip 校验 OK）
  - `vendor/torchvision-0.21.0+cpu-cp39-cp39-linux_x86_64.whl`（1,843,984 B，zip 校验 OK）
  - `vendor/deps/`：filelock 3.19.1、fsspec 2025.10.0、jinja2 3.1.6、markupsafe 3.0.4、mpmath 1.3.0、networkx 3.2.1、numpy 1.26.4、sympy 1.13.1、typing_extensions 4.16.0（pip download --python-version 39，共 ~36 MB）
- 未复用任何历史方案/模型/服务产物；仅复用训练数据缓存、预训练权重缓存与基础镜像（均已在 T1 记录选择与验证）。

## 未验证项（交由 T4/T5 实证）

1. checkpoint 在镜像内 torch 2.6.0+cpu 的加载兼容性（2.8 保存 → 2.6 加载；main.py 已显式 weights_only=False）。
2. 平台 vGPU/CUDA 不可用情况下的 CPU 推理（本方案固定 CPU 推理路径，device 选择自动回退）。
3. 2 CPU 限流下的真实延迟（本地 128 核实测 55.5 ms）。
