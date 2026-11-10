# TICKET-2 候选权重补充核验（2026-11-08）

## 结论

本次找到一个公开、模型卡声明 MIT、权重下载端点可访问的候选，但其公开应用代码只给出伪造与未伪造二分类，不能证明覆盖比赛三分类。尚未找到同时满足权重许可与获取、三分类映射及资源条件的候选；TICKET-2 仍阻塞，不能宣称复现或推理通过。本次没有完整下载权重，也没有进行目标环境推理。

## 比赛要求

- 原始接口表 `workflow/runs/t1-real-20261108/raw_sheet_G2lxWB.csv` 第 6 行：`1` 为原生无修实拍图、`0_1` 为已修图、`0_2` 为 AI 全图生成。`competition_spec.json` 第 93–95 行进一步记录已修图包括人工处理与 AI 局部处理。
- `workflow/runs/t1-real-20261108/competition_spec.json` 第 166–167、207 行引述比赛资料 S2：`1/2 A100-40g显存，2c4g`。前者按半张 40 GB A100 理解为约 20 GB 显存；`2c4g` 的单位原文未明确，不能将常见的 2 核/4 GB 解释视为已证实。

## 新候选与检查

- 模型仓库：[inzamamalii/image_forgery_detection](https://hf-mirror.com/inzamamalii/image_forgery_detection)，固定版本 `c2a375423c51f7ecd171c122990e9b874470935b`。模型 API 元数据记录 `private=false`、`gated=false`、`license:mit`；[固定版本模型卡](https://hf-mirror.com/inzamamalii/image_forgery_detection/raw/c2a375423c51f7ecd171c122990e9b874470935b/README.md) 仅包含 `license: mit` 声明，未见详细许可正文或训练数据权利证明。
- 固定版本 `model.keras` 元数据大小 39,249,572 字节，LFS SHA-256 `ded7ed6f356bad27b5642cbd3c94751327ab84f395618be6ad05e4932242c5e9`。对[固定版本下载地址](https://hf-mirror.com/inzamamalii/image_forgery_detection/resolve/c2a375423c51f7ecd171c122990e9b874470935b/model.keras) 的重定向 HEAD 检查最终返回 HTTP 200、`Content-Length: 39249572`、`Accept-Ranges: bytes`；这不是完整下载或本地哈希校验的证据。
- [固定版本应用代码](https://hf-mirror.com/inzamamalii/image_forgery_detection/raw/c2a375423c51f7ecd171c122990e9b874470935b/app.py) 加载作者本机绝对路径下的模型，预测结果仅返回 `Not Forged` 或 `Forged`，未提供已修图和 AI 全图生成之间的映射。因此不能作为已满足比赛三分类的候选；权重文件大小也不能代表实际显存或内存需求。
- 另发现 `salmanzaman777/digital-image-forgery-detection-model` 和 `usamaalam/image-forgery-detection-model` 的模型元数据含 MIT 标签，但本次未证实其完整许可、三分类覆盖或资源要求，不作为通过验收的候选。

## 实际检查与边界

- 通过 `curl --proxy http://172.28.4.16:18999 --connect-timeout 5 --max-time 10 -sS -I 'https://hf-mirror.com/api/models?limit=1'` 检查用户确认的不计费代理：HTTP CONNECT 200，目标 HTTP 200。其后只经该代理访问少量元数据、模型卡、应用代码及权重 HEAD，未进行大文件下载。
- 搜索接口 `https://hf-mirror.com/api/models?search=image%20forgery%20detection&limit=20&full=true` 返回上述候选元数据；固定版本 API 使用 `/api/models/inzamamalii/image_forgery_detection/revision/c2a375423c51f7ecd171c122990e9b874470935b?blobs=true` 检查大小与哈希。
- 使用 `rg -n 'A100|2c4g|原生|已修图|全图生成' workflow/runs/t1-real-20261108/competition_spec.json runs/2026-11-08-subnet-196/01-competition/evidence.md` 核对已有比赛证据；使用 `rg` 检查下载到临时目录的应用代码分类输出。
- 以上成功的 curl、rg 检查退出状态为 0。此前候选、失败与目标 Codex + Qwen 只读验证的证据见 `workflow/runs/t2-cont-20261108/REPORT.md`、`workflow/runs/t2-followup-20261108/REPORT.md`；此前的只读验证不是模型推理成功。本轮无合格的三分类候选，未启动目标环境权重推理或重复此前只读验证。
