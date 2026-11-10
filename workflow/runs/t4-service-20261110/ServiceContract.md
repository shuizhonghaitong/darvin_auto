# T4 ServiceContract — 图像真伪鉴定最小 HTTP 服务

- 依据：`runs/t1-real-20261108/competition_spec.json`（service / input / output 段，来源 S4/S5）
- 推理内核：T3 `runs/t3-baseline-20261110/` 已核验的真实模型（`model_full.pt` 的 numpy 导出）
- 协议：HTTP/1.1，JSON（UTF-8），同步返回

## 1. 端点

### GET /ready
- 就绪探针（spec: httpGet path=/ready）。
- 成功：`200`，`Content-Type: text/plain`，响应体恰为 `True`（4 字节，与 starting-kit 一致）。
- 其他 GET 路径：`404`，JSON `{"success": false, "result": null, "message": "not found"}`。

### POST /api/v1/image-authenticity
- 请求（spec 请求参数 S5）：
  ```json
  { "image_base64": "<图片二进制的 Base64，无 data: 前缀>", "image_format": "jpg|jpeg|png|..." }
  ```
  - `image_base64`：必填，string。Base64 允许缺 padding（服务端自动补齐，`validate=True` 严格字符集校验）。
  - `image_format`：按契约接收并写入日志；实际解码以字节内容为准（PIL 自动识别）。
    声明格式与内容不符时按解码结果如实处理（能解码即预测，不能解码即 400 错误）。
- 成功响应：`200`
  ```json
  { "success": true, "message": "鉴定完成", "result": "1" | "0_1" | "0_2" }
  ```
- 错误响应（全部 `400`，`result` 恒为 `null`，无固定类别兜底）：

  | 场景 | message |
  |---|---|
  | 请求体非 JSON / 非对象 | `请求体不是有效的 JSON` |
  | 缺 `image_base64` / 非字符串 / 空串 | `缺少必要参数: image_base64` |
  | Base64 字符集非法 | `图片 Base64 编码无效` |
  | 解码后 0 字节 | `图片内容为空` |
  | 合法 Base64 但非图片内容 | `图片解码失败: 无法识别的图片内容` |
  | 其他未捕获异常 | `500` `服务器错误: <异常>`（traceback 写 stderr） |

## 2. 类别与模型

- 标签空间（spec S1–S5）：`1`=原生无修实拍图，`0_1`=已修图，`0_2`=AI 全图生成。
- 模型：4×(Conv3x3→BN→ReLU→MaxPool2, 3→32→64→128→256)→GAP→Linear(256,3)，390,147 参数。
- 权重：本目录 `model_weights.npz`（1,571,082 B），sha256 固定于 `weights.sha256`：
  `132efbd9a7397bbb497df48349114adce6da370d0440db4b897ba470ee2933bd`
- 来源与核验：`image_auth_repo/starting-kit/model_weights.npz`（T3 run_report §5.1 已对拍
  `model_train/out/model_full.pt`：max|Δlogit|=3.6e-07，6/6 argmax 一致）。
  服务启动时二次校验 sha256，不匹配立即退出（非 0），不使用未校验权重。

## 3. 配置

| 项 | 方式 | 默认 |
|---|---|---|
| 监听地址 | `--host` / `MOCK_SERVER_HOST` | `0.0.0.0` |
| 监听端口 | `--port` / `MOCK_SERVER_PORT` | `8000`（本地默认；平台契约 0.0.0.0:80 用 `MOCK_SERVER_PORT=80`） |
| 权重路径 | `--weights` / `IMAGE_AUTH_MODEL_PATH` | 本目录 `model_weights.npz` |

启动：`./start.sh [--host H --port P]`（先 `sha256sum -c weights.sha256` 再 `exec python main.py`）。
默认解释器为 `python3`；可用 `PYTHON` 覆盖为已安装依赖的解释器。本机系统 Python 缺少 Pillow，独立验证使用 T3 的 evo 环境（numpy 1.26.4 + Pillow 12.2.0）。

## 4. 依赖

- `requirements.txt`：`numpy>=1.24`、`Pillow>=9.0`（均为环境既有，本次未安装任何包）。
- 其余为 Python 标准库（http.server / base64 / hashlib / json）；无 Flask、无 torch、无网络依赖。

## 5. 运行形态与限制

- 单进程 ThreadingHTTPServer（并发处理），无鉴权、无 TLS、无持久化——满足"最小服务"边界。
- 不做精度优化与性能测试（T4 边界）；6 图冒烟级 HTTP 实测见 `run_report.md`。
- 权重文件已被本目录 `.gitignore` 排除，不进入 Git；服务启动不依赖旧工程目录路径。
- 与 spec 冲突 C1（失败判定口径）相关：本服务对坏请求返回 400+success=false（非空结果），
  该口径选择留待提交阶段按冲突裁定处理，本阶段如实记录。
