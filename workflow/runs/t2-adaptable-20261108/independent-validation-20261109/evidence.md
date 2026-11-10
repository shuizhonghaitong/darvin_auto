# TICKET-2 独立目标环境验证 — 证据报告

运行目录：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-adaptable-20261108/independent-validation-20261109`
日期：2026-11-09（Asia/Shanghai）。本报告仅基于本次运行自己的命令与输出；未读取历史候选方案、代理日志或结论作为证据。

## 1. 输入与范围

- CompetitionSpec：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t1-real-20261108/competition_spec.json`（完整读取：task/data/input/output/service/environment/submission/conflicts C1,C2/unknowns）。
- Skill：`/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/.agents/skills/solution-discovery/SKILL.md`（完整读取）。
- 用户授权：最小模型加载 + 三分类适配 + 单步训练测试；不授权 TICKET-3 实现、完整训练、比赛提交。
- 授权资产：`../independent-isolated-20261109/dinov2-base-f9e44-model.safetensors`（346,345,912 字节；声明来源 facebook/dinov2-base @ f9e44c814b77203eaa57a6bdbbd535f21ede1415；**未因提供而预设方案合适**，全部属性由本次实测推导）。
- 授权数据：比赛训练附件（飞书）。

## 2. 环境核验

| 项 | 实测 | 命令 |
|---|---|---|
| evo 环境 | python 3.10.21 / torch 2.8.0+cu128（cuda 不可用）/ transformers 4.57.0 / safetensors 0.7.0 / PIL 12.2.0 | `<env>/bin/python -c "import ..."`，exit 0 |
| qwen 环境 | python 3.11.16 / torch 2.9.0 / transformers 4.57.3（备用，未用于主测试） | 同上 |
| 宿主机 | 128 核 / 2TB RAM；测试用 `taskset -c 0,1` + `torch.set_num_threads(2)` + OMP/MKL=2 模拟 2 核 | `nproc`, `free -g` |
| GPU | 沙箱内不可见，`torch.cuda.is_available()=False`，全部为纯 CPU 路径 | 脚本输出 `torch_version` |

## 3. 权重资产实测（离线结构证据）

`work/validate_t2.py` 从 safetensors 头与张量直接推导（非资产自述）：

- 张量数 223；总参数 **86,580,480**（与 DINOv2 ViT-B/14 一致）。
- 架构：hidden 768、12 层、patch 14、MLP 3072、位置编码 **[1,1370,768] = 37×37+1 → 原生 518px**、patch 投影 [768,3,14,14]、cls_token [1,1,768]、mask_token [1,768]。
- 命名：官方 facebookresearch/dinov2 原始布局（`embeddings.*`、`encoder.layer.N.attention.attention.{query,key,value}`、`layer_scale*.lambda1`、`layernorm`）。
- 权重非平凡：patch_proj mean|w|=0.005664、max|w|=0.0582；cls_token norm=0.3997（排除全零/随机初始化冒充）。
- 本地 sha256：**d73036b56966966d07975d696bde331762f37297e2f095de8cea0040c3aa0841**（`sha256sum`）。
- 远端 pin 比对：被网络阻塞（见 §6），标记 unknown。

## 4. 加载与三分类适配（关键发现）

可复现：`work/run_validate.sh`（`/usr/bin/time -v -o validate_t2.time taskset -c 0,1 <evo python> validate_t2.py > validate_t2.log 2> validate_t2.err`），最终 exit 0。

1. **失败复现（等效证据）**：`Dinov2Config(image_size=224)`（默认）下 `load_state_dict(strict=False)` 抛出 `RuntimeError: size mismatch for embeddings.position_embeddings: [1,1370,768] vs [1,257,768]`。根因：transformers 4.57 由 `image_size/patch_size` 推导位置编码长度，checkpoint 是 518px 原生网格。
2. **适配方式**：`Dinov2Config(image_size=518, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, patch_size=14, layer_scale_init=1.0)`（数值全部由权重形状推导）→ `Dinov2Model.load_state_dict(strict=False)`：**missing=0，unexpected=0，223/223 全量载入**。`interpolate_pos_encoding` 对 224 输入自动插值（224 与 518 两档输入均前向成功）。
3. **三分类头**：`nn.Linear(768,3)` 接 layernorm 后 CLS token；标签映射 **index 0→"1"、1→"0_1"、2→"0_2"**（按 spec `output.label_space` 顺序）。未使用 HF pooler（官方 checkpoint 无 pooler 权重，避免随机初始化 pooler 参与）。
4. **前向**：合成 batch(2,3,224,224)（ImageNet mean/std 归一化；明确为**合成输入，只证明形状/梯度，不证明效果**）→ feat (2,768)、logits (2,3)、softmax 和 = 1.0。
5. **单步训练**：CE loss=2.835；`backward()` 后 head 权重梯度有限（norm 43.43）、偏置 0.95、编码器亦收到梯度（layernorm norm 0.526）；SGD(lr=0.1) 一步后 head 权重 max|Δ|=0.6407、偏置 0.0644 → **参数变化确认**。

## 5. 资源测量（2 核 CPU 模拟，4GB 为用户验证假设）

`work/validate_t2.time`（/usr/bin/time -v，exit 0）：

- **峰值 RSS = 3,075,004 KB ≈ 2.93 GiB**（整进程：解释器+torch/transformers+346MB 权重+前反向激活）→ 低于 4GB 假设，余量约 1.1GB；若按更严格口径（容器总内存）仍偏紧，需 T3 阶段在真实 2c4g 容器内复核。
- 墙钟 12.46s（含 import）；模型初始化+权重载入 1.67s；224px 单图推理 10 次平均 **224.2 ms**（纯 CPU 2 核；比赛服务若用 1/2 A100 应显著更快，未测）。
- `File system inputs: 30568`（页缓存已热，权重读盘 9ms；冷启动未测）。

## 6. 网络与数据核验尝试（全部记录）

| 尝试 | 命令/路线 | 结果 |
|---|---|---|
| 免流代理 18999 | `curl -x http://172.28.4.16:18999 https://huggingface.co/api/models/facebook/dinov2-base...` | `curl: (7) Couldn't connect to server`，http=000 |
| 本机 mihomo 7589 | `curl -x http://127.0.0.1:7589 https://hf-mirror.com/api/...` | `curl: (7) Couldn't connect to server`（未产生任何付费流量；未切换路线） |
| 直连（绕代理） | `curl --noproxy '*' https://hf-mirror.com`、`https://open.feishu.cn` | DNS 解析失败（沙箱禁 DNS）/ 000 |
| 本地数据缓存 | `find` 全盘（训练集/0_1/0_2/附件 token） | 无数据 zip 命中（token 仅出现在历史证据文件中，按指示未读取） |
| lark-cli | `darwin_auto/runtime/lark-cli-1.0.98/lark-cli` | 挂载目录间歇出现又消失；连续 3 次探测 absent，无法执行 |

结论：**数据覆盖未验证 ≠ 数据不存在**。spec 层面已知：S3（原始文档 raw_doc2，本次读取确认）仅列出 0_1、0_2 两个附件；1 类数据在来源中缺失（spec unknowns 已列）。zip 内部类别/文件数未核验。

## 7. 许可核验状态

- 权重许可：**unknown**。无法访问 HF model card / facebookresearch/dinov2 LICENSE 原文（网络阻塞）。"DINOv2 为 Apache-2.0"仅为常见声明，未在本运行核验，不作结论。
- 框架依赖：transformers（已安装 4.57.0）与 torch（2.8.0）为标准开源组件。
- 数据许可：unknown（附件未下载，来源文档未见使用条款）。
- 本运行**未读取/修改任何认证配置**（仅观察到 lark-cli 凭据目录存在，未触碰内容）。

## 8. 结果汇总与状态

- 技术路径（T2-C1：DINOv2-B/14 + 3 类头）在 2 核 CPU/4GB 假设下**加载、适配、前向、单步训练、双分辨率**全部实测通过，资源占用有实测证据。
- **status = blocked**（`candidate_solutions.json`）：B1 三类数据覆盖未验证（1 类数据缺口 + 附件不可下载）、B2 权重许可 unknown、B3 权重远端 pin 未确认。`selected_candidate_id = null`；T2-C1 为条件性推荐，解除 B1–B3 后可进入 T3。
- 未编造任何通过：网络受限字段均标 unknown 并附尝试记录；合成输入与真实数据严格区分。

## 9. 复现清单

```bash
cd /mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-adaptable-20261108/independent-validation-20261109/work
./run_validate.sh                 # 重跑全部模型验证（exit 0 预期；产物 validate_t2.{log,err,time}、validation_summary.json）
sha256sum ../independent-isolated-20261109/dinov2-base-f9e44-model.safetensors   # 期望 d73036b56966966d07975d696bde331762f37297e2f095de8cea0040c3aa0841
```

网络恢复后的待办（按优先级）：
1. `curl -x http://172.28.4.16:18999 'https://huggingface.co/api/models/facebook/dinov2-base?revision=f9e44c814b77203eaa57a6bdbbd535f21ede1415&blobs=true'` → 比对 model.safetensors 的远端 sha256 与 license 字段（B2/B3）。
2. 恢复 lark-cli（`darwin_auto/runtime` 挂载）→ 下载两个训练 zip（约 577MB，**先经用户确认路线与流量**）→ 清点内部类别与文件数，追查 1 类数据（B1）。
3. 在真实 2c4g 容器内复测内存峰值与 /ready+业务接口（T3 范围）。
