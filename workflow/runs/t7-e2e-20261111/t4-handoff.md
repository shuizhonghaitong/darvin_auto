# T4 交接 — 服务（复用 + 本次全新 HTTP 实测）— t7-e2e-20261111

## 处置
- 复用：`runs/t4-service-20261110/`（main.py、serve_model.py、model_weights.npz、weights.sha256、start.sh、requirements.txt、tests/、ServiceContract.md、历史 HTTP 证据）。
- 本次新执行：将服务文件复制到本目录 `t4/`（未写旧目录）；本次全新权重 sha256 校验 + 全新本地 HTTP 15 用例实测（服务绑定 127.0.0.1:19522，跑完即关）。

## 本次命令与结果
```sh
cd runs/t7-e2e-20261111/t4
sha256sum -c weights.sha256     # → model_weights.npz: OK（132efbd9…2933bd，与 T5 manifest 三方一致）
PYTHON=<evo python> ./start.sh --host 127.0.0.1 --port 19522 &    # start.sh 容器内同款权重校验 OK 后启动 main.py
<evo python> tests/http_client_tests.py --base http://127.0.0.1:19522 --out t4-http-results.json
# → exit 0；total=15 pass=15 fail=0；服务按显式 PID 关闭，端口释放（t4-test.exit、t4-test.log）
```
解释器 `/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python`（numpy 1.26.4 / Pillow 12.2.0，环境既有，未安装依赖）。

## 实测结果（t4-http-results.json）
- GET /ready → 200 `True`。
- 6 张真实样例 → 200 success:true，序列 `0_1,1,0_1,1,0_2,0_2`（与本次 T3 复跑及 T3 基线逐项一致）。
- 7 个错误用例 → 400 success:false result:null（message 与契约一致：缺参/类型/坏 Base64/非图片/非法 JSON）；GET /nope → 404 success:false。
- 错误响应未伪装成功预测（result 恒为 null）。

## 失败轨迹（如实记录，均已保留）
1. 首跑：跨 exec 会话的 nohup 服务随会话回收而终止 → 测试 Connection refused（t4-test.stderr 第一版）。
2. 二跑：`PYTHON` 变量未随环境导出，start.sh 回退系统 python3（无 PIL）→ ModuleNotFoundError（t4-server.stderr 第一版）。
3. 三跑：`PYTHON=$PY ./start.sh` 修正后 2s 就绪，15/15 通过（最终证据为 t4-server.log / t4-test.log / t4-http-results.json 当前版本）。

## 契约核对
- 与 `runs/t4-service-20261110/ServiceContract.md`：端点、字段、错误表一致；端口经 --port/MOCK_SERVER_PORT 可配，平台要求 0.0.0.0:80 由镜像 start.sh 默认参数承载（T5 容器内实测验证）。

## 输出
- `t4/t4-http-results.json`、`t4/t4-test.exit`、`t4/t4-server.log`、`t4/t4-test.log`（本次新证据）；服务代码/权重为复制件（与原件摘要一致）。
