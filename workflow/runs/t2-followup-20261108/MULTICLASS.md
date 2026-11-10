# TICKET-2 多分类候选补充核查（2026-11-08）

## 比赛约束和覆盖

- 比赛标签：`1` 原生无修实拍，`0_1` 人工或 AI 局部修图，`0_2` AI 全图生成。原始资料和附件元数据见 `runs/2026-11-08-subnet-196/01-competition/evidence.md`。
- 资源原文是 `1/2 A100-40g显存，2c4g`，显存可按约 20 GB 初步评估；`2c4g` 的具体单位和含义未确认，不应据此断言可训练。
- 训练集附件名称包含 `1 0_1.zip` 和 `0_2.zip`，但未下载核查；其中的 `1` 是否代表原生实拍类别不能仅凭文件名确定。平台数据集内容也未核实，因此三类训练数据覆盖尚未证明。

## 候选：HiFi-IFDL

- 仓库 <https://github.com/CHELSEA234/HiFi_IFDL>，本次查询 HEAD 为 `0ca70d651087bb09959dec583947031c47d30209`。README 介绍生成图像与篡改检测及定位，提供预训练推理入口和权重目录；代码仓库 LICENSE 为 MIT。代码许可不能自动推断为权重许可。
- 固定版本的 `utils/load_data.py` 包含 `TrainData` 和 `ValData` 数据加载类；但本轮检查公开根目录和 README 后未找到明确的模型训练入口，也未证明可以配置比赛所需的三分类。存在训练数据加载类不等于提供了可复现训练流程。
- `HiFi_Net.py` 展示多层级模型输出，但其 `detect` 接口记录的是 real/forged 二分类。模型内部存在多层输出不证明能够直接映射比赛三个类别，也不证明训练后的准确率或资源满足要求。
- README 指向 [Google Drive 权重目录](https://drive.google.com/drive/folders/1v07aJ2hKmSmboceVwOhPvjebFMJFHyhm)。已获取目录页面，但尚未证明具体权重文件可下载，亦未找到明确的权重使用许可；没有下载权重或核验哈希。作者对真实图训练数据是否公开亦未给出确定结论。
- README 指定 Python 3.7 / PyTorch 1.11；未安装或运行该候选，未测显存、内存、训练耗时及目标环境兼容性。

## 本轮检查和边界

- `git -c http.proxy=http://127.0.0.1:7589 ls-remote https://github.com/CHELSEA234/HiFi_IFDL.git HEAD`：获得上述提交 ID。
- 经代理读取固定版本 README、LICENSE、`HiFi_Net.py`，并以 `curl .../utils/load_data.py | rg -n -i 'class |train|label|dataset' -m 30` 检查数据加载类。固定来源：<https://raw.githubusercontent.com/CHELSEA234/HiFi_IFDL/0ca70d651087bb09959dec583947031c47d30209/utils/load_data.py>、<https://raw.githubusercontent.com/CHELSEA234/HiFi_IFDL/0ca70d651087bb09959dec583947031c47d30209/HiFi_Net.py>。
- 已确认不计费代理 `172.28.4.16:18999` 连接后访问 GitHub 时 TLS 超时；核实 `mihomo` 监听 `7589` 后，仅用用户允许的计费路线查询少量公开元数据，未下载模型或数据集。GitHub 未认证 API 返回 403 且额度为 0，是服务端限额而不是网络不可达。
- 本轮未找到同时具有可核验多分类训练入口、可获取且许可明确的权重、三类数据和可行资源证据的候选；因此没有重复运行无法消除上述外部缺口的目标环境验证。已有 Codex + Qwen 检查及其阻塞结果见本目录 `REPORT.md`、`evidence.md`。

## 结论与下一步

TICKET-2 仍阻塞，HiFi-IFDL 暂不能作为满足验收条件的候选。继续寻找明确公开训练命令、权重许可和下载地址的图像取证仓库；独立核查三类数据来源与比赛资源限制，然后才在目标 Codex + Qwen 环境执行验证。若缺口只能通过受限数据、权重授权或比赛方说明解决，应明确请求对应访问权限或说明，不以假设代替证据。
