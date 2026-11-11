# T5 交接 — 镜像（复用 + 本次本地/容器/registry 三重核验）— t7-e2e-20261111

## 处置
- 复用：`runs/t5-delivery-20261110/`（ImageManifest.md、build.log、docker-push/pull 证据、context/、历史容器 15/15 证据）。
- 本次新执行：本地镜像复核、构建上下文文件级比对、**全新 2C4G 容器实测（15 用例）**、registry 只读 digest 复核。未构建、未推送、未拉取（容器用本地已有镜像启动）。

## 镜像标识与一致性（本次复核）
| 项 | 值 | 与 ImageManifest 对比 |
|---|---|---|
| 镜像 | `harbor-contest.4pd.io/liuyutong/darvin-t5:20261110` | 一致 |
| 本地 image ID | `sha256:57004ba692901e804d8861ec18be2b7d045f114a8123175d09b0a885c3fa050e`（amd64，78,485,812 B） | 一致（t5-image-inspect.json） |
| registry OCI index digest | 同上（本次 live 查询，exit 0） | 一致（t5-registry-inspect.txt） |
| 远端 linux/amd64 manifest digest | `sha256:32233f079b0a8fbbda4bd9b60345fb3494061b77b3fdd8d2fe871738cca34826` | 一致 |
| `unknown/unknown` 条目 | attestation manifest（vnd.docker.reference.type=attestation-manifest） | 与 manifest 说明一致 |
| 镜像配置 | Cmd=`./start.sh --host 0.0.0.0 --port 80`，EXPOSE 80/tcp，Python 3.11.16 | 一致（平台契约 0.0.0.0:80） |
| 权重 sha256 | `132efbd9a7397bbb497df48349114adce6da370d0440db4b897ba470ee2933bd` | 一致 |

## 本次命令与结果
```sh
docker image inspect harbor-contest.4pd.io/liuyutong/darvin-t5:20261110          # t5-image-inspect.json
# context 5 文件（main.py/serve_model.py/start.sh/requirements.txt/model_weights.npz）
#   vs runs/t4-service-20261110/ 同名文件 sha256 比对 → 5/5 SAME（t5-context-check.json）
docker run -d --name t7e2e-t5 --cpus 2 --memory 4g -p 127.0.0.1:19523:80 <image>  # exit 0，2s 内 /ready=200
<evo python> ../t4/tests/http_client_tests.py --base http://127.0.0.1:19523 --out t5-container-http-results.json
# → test_exit=0；total=15 pass=15 fail=0（t5-container-http.log/.exit）
docker logs t7e2e-t5 → start.sh 容器内权重 sha256 校验 `model_weights.npz: OK`（t5-container.log）
docker rm -f t7e2e-t5 → rm_exit=0（清理完成）
docker buildx imagetools inspect <image>   # *.4pd.io NO_PROXY 直连，manifest 级小流量；exit 0（t5-registry-inspect.txt）
```

## 结论
- 镜像-服务-权重-平台契约一致性本次闭环：本地镜像 ID = registry index digest = manifest 记录；全新容器 15/15；6 图序列 `0_1,1,0_1,1,0_2,0_2` 与 T3/T4 一致。
- 未验证项（继承）：平台评测时的实际拉取、干净环境完整拉取、Harbor 匿名 401 与平台拉取凭据——属 runtime/平台侧，只有真实提交后跟踪。

## 输出
- `t5/t5-image-inspect.json`、`t5/t5-context-check.json`、`t5/t5-container-http-results.json`、`t5/t5-container-http.log`、`t5/t5-container.log`、`t5/t5-registry-inspect.txt`（本次新证据）。
