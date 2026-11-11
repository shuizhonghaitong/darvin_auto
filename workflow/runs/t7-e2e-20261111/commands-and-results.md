# commands-and-results — t7-e2e-20261111（本次真实 T7 端到端，2026-11-11 +08:00）

约定：`$D`=`/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin`（0.5.2）；`$PY`=`/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python`（3.10.21，numpy/Pillow/torch 既有）；镜像 `<IMG>`=`harbor-contest.4pd.io/liuyutong/darvin-t5:20261110`。Darwin 公网经已验证 7589 代理（本次少量请求）；`*.4pd.io` registry 走 NO_PROXY 直连。

## S0 环境基线（本次）
| 命令 | 结果 |
|---|---|
| `$D --version` | 0.5.2 |
| `docker version` | server 29.5.3 |
| `docker image inspect <IMG> --format '{{.Id}} …'` | `sha256:57004ba6…50e` amd64 78485812 cmd=[./start.sh --host 0.0.0.0 --port 80]（与 ImageManifest 一致） |
| `ss -tln \| grep 7589` | LISTEN *:7589（已验证可用）；18999 无监听（免流量代理不可用，按本次指令使用 7589） |
| `curl -x http://127.0.0.1:7589 https://darvin.originlabs.cc/` | 200 |
| env NO_PROXY | 含 localhost/127.0.0.1/172.28.4.0/24/*.4pd.io |

## T1（复用 spec + 本次平台复查）
| 命令 | 结果 |
|---|---|
| `python3 json.load(runs/t1-real-20261108/competition_spec.json)` | 可解析（复用核验） |
| `$D subnet inspect 196 --json` → `t1/raw_subnet_196_t7e2e.json` | exit 0，envelope success（939ms） |
| `$D auth inspect --json` → `t1/t1-auth-inspect.json` | exit 0；authenticated；solution.submit=eligible；task.create=eligible |
| 与 11-08 raw / 今日 08:46 raw 逐字段对比 | 仅 solutions 114→125→127、participants 11→12 计数变化；描述/文档 URL/类型/合约地址未变 |

## T2（复用 plan + 本次文件级核验）
| 命令 | 结果 |
|---|---|
| `python3` 解析 plan 并比对 spec 路径/URL/时间戳 → `t2/t2-file-check.json` | 全部 matches=true（未重新规划） |

## T3（复用 predict.py + 本次全新推理复跑）
| 命令 | 结果 |
|---|---|
| `cp` predict.py/samples.txt 到 `t3/`；6 样例存在性逐一核验 | 全部 OK（含带空格路径） |
| `$PY t3/predict.py --samples t3/samples.txt --json t3/t3-rerun-predictions.json` | exit 0（t3/t3-rerun.exit/.log） |
| 与 T3 基线、今日 network dry run 对比 | 序列 `0_1,1,0_1,1,0_2,0_2` 三方一致；max\|Δlogit\|=0.0（bit 级一致）；correct_vs_path_label=4（同基线） |

## T4（复用服务 + 本次全新 HTTP 实测）
| 命令 | 结果 |
|---|---|
| `cp` 服务 7 文件 + tests/ 到 `t4/`；`sha256sum -c weights.sha256` | `model_weights.npz: OK`（132efbd9…） |
| 尝试1：nohup 服务跨会话 + 15 用例 | 失败：会话回收后服务终止，Connection refused（轨迹 t4/t4-test.stderr 旧版） |
| 尝试2：单会话但 PYTHON 未导出 → start.sh 用系统 python3 | 失败：ModuleNotFoundError: PIL（轨迹 t4/t4-server.stderr 旧版） |
| 尝试3：`PYTHON=$PY ./start.sh --host 127.0.0.1 --port 19522 &` + `$PY tests/http_client_tests.py --base http://127.0.0.1:19522 --out t4-http-results.json` | ready 2s；**exit 0；total=15 pass=15 fail=0**（t4/t4-test.exit/.log/.json）；服务按 PID 关闭、端口释放 |

## T5（复用镜像 + 本次本地/容器/registry 三重核验）
| 命令 | 结果 |
|---|---|
| `docker image inspect <IMG>` → `t5/t5-image-inspect.json` | id/arch/size/cmd/ports/python3.11.16 与 ImageManifest 一致（注：`--format` 模板 WorkDir 键缺失为 containerd 存储格式差异，改 JSON 解析；失败轨迹在案） |
| context 5 文件 vs `t4-service-20261110/` sha256 → `t5/t5-context-check.json` | 5/5 SAME；weights.sha256 三方一致 |
| `docker run -d --name t7e2e-t5 --cpus 2 --memory 4g -p 127.0.0.1:19523:80 <IMG>` | run_exit=0；2s /ready=200（本地镜像启动，非拉取） |
| `$PY ../t4/tests/http_client_tests.py --base http://127.0.0.1:19523 --out t5/t5-container-http-results.json` | **test_exit=0；total=15 pass=15 fail=0** |
| `docker logs t7e2e-t5` → `t5/t5-container.log`；`docker rm -f t7e2e-t5` | 容器内权重 sha256 `model_weights.npz: OK`；rm_exit=0 清理完成 |
| `docker buildx imagetools inspect <IMG>` → `t5/t5-registry-inspect.txt`（NO_PROXY 直连，manifest 级） | exit 0；index digest `sha256:57004ba6…`=本地 ID=manifest；amd64 manifest `sha256:32233f079…`=manifest；unknown/unknown=attestation |

## T6 提交前（本次新执行）
| 命令 | 结果 |
|---|---|
| 新建 `t6/solution.yaml`（name=liuyutong-image-auth-t5-20261111-e2e）+ `t6/values.yaml` | 与 T1 合约地址/T5 镜像一致；training_image 平台 SUT digest pin 与历史一致 |
| `$D solution status 88c59e71a9f0f235352116c6409e0ee5 --config t6/solution.yaml --json` → `t6/t6-hist-364-status.json` | exit 0；历史 364：running，job RUNNING 尚无结果，can_cancel=true（>12h，非阻塞，未取消） |
| `$D solution list --subnet 0x35fC… --config t6/solution.yaml --json` → `t6/t6-solution-list.json` | exit 0；364 PROCESSING；365 READY_TO_DEPLOY/PENDING 无任务（来源维持未确认）；更早 350–357 历史对象 |
| `$D solution precheck --config t6/solution.yaml --json` → `t6/t6-precheck.json` | exit 0；8 pass + points/runtime 设计 unverified；0 blocking |

## T6 提交（本次唯一外部写操作，已授权，仅执行一次）
| 命令 | 结果 |
|---|---|
| `$D solution submit --config t6/solution.yaml --create-task --yes --json`（02:57:50Z–02:57:57Z） | **exit 0；envelope success；submission_id=396，model_app_id=14434，task_id=0359f8e60c923a42d74161795f505b80，stage=job_created，historical=false**（t6/t6-submit.json/.exit；本地回执 t6/.darvin/submissions/v1_b9b75c55….json） |

## 提交后只读核实（本次新执行）
| 命令 | 结果 |
|---|---|
| `$D solution status 0359f8e60c923a42d74161795f505b80 --config t6/solution.yaml --json` → `t6/t6-new-status.json` | exit 0；running；inference job 5f378999… **SCHEDULING**；can_cancel=true。（前两次尝试 exit 127：ro 挂载瞬断致 shebang exec ENOENT，文件与解释器均在、改用 `$V/python $V/darvin` 显式调用成功；只读查询，无平台写、无重复提交） |
| `$D solution list …` → `t6/t6-new-list.json` | exit 0；**396/14434 PROCESSING，Local receipt=yes**，任务 0359f8e6…（闭环一致）；397/14435 同名无任务条目（不在回执内，疑似平台配对生成，不认领）；364/365 状态未变 |

## 流量与外部操作汇总
- Darwin 公网（7589 代理，计量，本次指令允许的小量）：subnet inspect、auth inspect、status364、list、precheck、submit、status-new、list-new 共 **8 次请求**（其中 1 次为平台写=submit）。
- registry（*.4pd.io NO_PROXY 直连）：1 次 manifest 级只读 inspect（imagetools）+ docker run 使用本地镜像（无拉取）。
- 本地 docker：1 容器 run/rm（t7e2e-t5，已清理）；1 本地服务进程（127.0.0.1:19522，已停止、端口释放）。
- 未构建/未推送/未拉取镜像；未训练/未下载模型/依赖；未修改任何旧运行目录（只读引用 + 复制到本目录）；未取消历史任务；未记录认证秘密。
