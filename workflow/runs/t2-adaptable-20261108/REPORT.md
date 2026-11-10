# TICKET-2: 可改造候选方案与阻塞证据

## 当前结论

TICKET-2 **尚未完成**。旧工程的 ResNet-18 方案有实际的三分类训练入口和历史推理记录；通用预训练权重存在固定版本、明确的模型卡许可标注和可访问的下载地址。但这还不足以证明整个候选方案的代码、数据和已训练权重均可复用，也没有证明其资源占用符合比赛限制。历史三分类结果不能替代目标运行 Agent 的完整验收。

## 证据

- 旧工程最终方案见 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/reports/frontend_continuous_20261105/RUN_RECORD.md` 和 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_baseline/README.md`。`train/build_dataset.py` 和 `train/train.py` 包含 `1`、`0_1`、`0_2` 三类及交叉熵训练入口。历史记录称 CPU 对每类各三张图推理，9 张中 8 张正确；这不是独立复验或完整数据覆盖证明。
- 比赛原文与 CompetitionSpec 位于 `workflow/runs/t1-real-20261108/`，资源描述为“1/2 A100-40g显存，2c4g”。其中 `2c4g` 的精确定义未获独立确认；旧工程记录没有可对照该限制的峰值资源测量。
- 预训练模型仓库 [timm/resnet18.a1_in1k](https://huggingface.co/timm/resnet18.a1_in1k) 的镜像 API 返回固定版本 `491b427b45c94c7fb0e78b5474cc919aff584bbf`，模型卡元数据 `license: apache-2.0`；文件列表包含 `model.safetensors` 和 `pytorch_model.bin`。这是该模型仓库的许可声明，不自动覆盖旧工程代码、训练数据或其微调权重。
- 固定版本 [model.safetensors](https://hf-mirror.com/timm/resnet18.a1_in1k/resolve/491b427b45c94c7fb0e78b5474cc919aff584bbf/model.safetensors) 经免费代理实际下载成功；响应头标注长度 46,807,446 字节，下载后本地 SHA-256 为 `80c49dee3da4822c009c5a7fe591e9223c5a2cfcf95a4067ca4dfb5a7b89c612`，与远端对象摘要一致。文件暂存 `/tmp/t2-resnet18-fw9Rkn/model.safetensors`，该临时路径不保证长期保留。
- 旧工程 README 声称使用该预训练来源，但现有本地权重的来源与上述固定版本是否字节一致未被证明。旧工程微调权重、训练数据的复用授权尚未核实，不能以预训练权重的许可推定。
- 目标环境曾使用 Codex CLI + `qwen3.8-27b-fp8` 运行局部检查，过程见 `discovery-events.jsonl` 和 `guard-events.jsonl`。模型能找到旧工程候选和三分类入口，但两次将局部调查误称为 TICKET-2 完成；该行为不能作为完整目标环境验收通过的证据。

## 本轮检查

- `PYTHONDONTWRITEBYTECODE=1 python /mnt/disk3/liuyutong_home/.codex/skills/.system/skill-creator/scripts/quick_validate.py workflow/.agents/skills/solution-discovery`：退出 0，输出 `Skill is valid!`；仅验证技能格式，不代表运行 Agent 能力通过。
- 使用 `curl --proxy http://172.28.4.16:18999` 访问 `https://hf-mirror.com/api/models/timm/resnet18.a1_in1k` 查询版本、模型卡许可和文件列表；对上述固定版本地址检查响应头。受限环境直接访问失败后，经授权重试成功。
- `curl --proxy http://172.28.4.16:18999 --fail --location --silent --show-error --max-time 180 --output /tmp/t2-resnet18-fw9Rkn/model.safetensors https://hf-mirror.com/timm/resnet18.a1_in1k/resolve/491b427b45c94c7fb0e78b5474cc919aff584bbf/model.safetensors`：退出 0；`sha256sum /tmp/t2-resnet18-fw9Rkn/model.safetensors`：退出 0，结果与上述远端对象摘要一致。
- 在 `workflow/runs/t1-real-20261108/` 和旧工程运行记录中检索资源描述；没有发现足以完成资源验收的峰值占用证据。

## 未解除的阻塞

1. 旧工程训练代码、数据和微调权重的授权与可转交性尚未证实；可考虑仅采用有许可的预训练权重并用获授权的比赛数据重新训练，但不能假定比赛数据具备所需三类覆盖或可用于此目的。
2. 比赛 `2c4g` 的准确含义和方案实测峰值资源尚未得到可对照的证据。
3. 目标运行 Agent 尚未在完整验收范围下产出并独立验证合格的 CandidateSolutions；局部目标测试存在错误宣称完成的问题。
