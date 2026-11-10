

TICKET-2 独立验证完成。产物与状态如下：

**产物**
- `candidate_solutions.json`（/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-adaptable-20261108/independent-validation-20261109/candidate_solutions.json:1）— 4 个候选，`status=blocked`，`selected_candidate_id=null`（T2-C1 为条件性推荐）
- `evidence.md`（同目录 evidence.md:1）— 全部命令、退出状态、日志、资源与失败记录
- 可复现脚本 `work/validate_t2.py` + `work/run_validate.sh`，摘要 `work/validation_summary.json`（已与 stdout 日志逐项交叉核对，sha256 二次复核一致）

**已实测通过（2 核 CPU，evo 环境 torch 2.8.0/transformers 4.57.0）**
- 权重真实加载：223/223 张量，`missing=0 / unexpected=0`；关键发现是默认 `image_size=224` 会因 position_embeddings [1,1370,768] 形状不匹配加载失败（已复现），适配为 `image_size=518`（官方 DINOv2 用法）后全量 1:1 载入，224/518 双分辨率自动插值前向成功
- 三分类头：`Linear(768,3)` 接 layernorm 后 CLS，标签映射 0→"1"、1→"0_1"、2→"0_2"；输出 (B,3)、softmax 和=1.0
- 单步训练：loss 2.835，head/编码器梯度均有限，SGD 一步后 head 权重 max|Δ|=0.641 —— 参数变化确认
- 资源：峰值 RSS ≈ 2.93 GiB < 4GB 假设（余量约 1.1GB，偏紧待真实容器复核）；224px 单图推理平均 224ms
- 输入为合成像素，仅证明形状与梯度通路，不证明效果

**Blocked（未编造通过）**
- B1 数据三类覆盖未验证：来源文档仅列 0_1/0_2 两个 zip，1 类数据缺失；附件下载不可行（沙箱 DNS 被禁、免流代理 18999 与 mihomo 7589 均连接被拒——未切换路线、未产生付费流量；lark-cli 的 runtime 挂载间歇消失，3 次探测 absent）
- B2 权重许可 unknown（无法访问 HF model card/原始 LICENSE 核验）
- B3 权重远端 pin 未确认（本地 sha256 `d73036b5...aa0841` 已记录，远端比对被网络阻塞）

**需要你决策/协助的下一步**
1. 恢复网络路线后我可做小流量核验：HF API 比对 sha256 + license 字段（KB 级）
2. 训练 zip 共约 577MB，属大流量——确认路线（优先免流 18999）与 lark-cli 恢复后，我再下载清点三类覆盖
3. 4GB 峰值余量偏紧，建议 T3 在真实 2c4g 容器内复核