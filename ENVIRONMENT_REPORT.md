# T0 环境检查报告

检查时间：2026-11-07（Asia/Shanghai）。状态：**阻塞，未通过验收**。

## 运行位置与凭证边界

- 本次运行目录：`/mnt/disk3/liuyutong_home/workspace/darvin_auto`；本报告保存于该目录的 `ENVIRONMENT_REPORT.md`。其他阶段的产物目录尚未确定，不预设其结构。
- Darwin、飞书、GitHub、Hugging Face 和模型服务的认证应使用宿主管理的既有凭证，仅供宿主相应工具使用，不写入报告、代码或最终镜像。
- 镜像仓库凭证仅供镜像仓库认证、拉取或推送使用；不得因此将宿主其他平台凭证打包进镜像。本次未向镜像仓库推送镜像，也未提交 Darwin 比赛。

## 工具与 Skill

当前终端通过 `command -v` 分别检查命令位置。`darwin`、`feishu`、`lark`、`gh`、`hf`、`huggingface-cli`、`qwen` 均未在当前 PATH 中找到；这不等于宿主或旧工程没有对应工具。旧工程中找到飞书和名为 `darvin` 的 Darwin CLI 入口，见下表；其余工具尚未找到可运行入口。

| 检查命令 | 实际输出或结果 |
|---|---|
| `docker --version` | `Docker version 29.5.3` |
| `codex --version` | `codex-cli 0.162.1`；另提示 PATH aliases 无法创建，文件系统只读。 |
| `/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/lark-cli-1.0.98/lark-cli --version` | `lark-cli version 1.0.98`。 |
| `/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin --version` | `0.5.2`。 |
| 检查 `/mnt/disk3/liuyutong_home/.codex/skills` | 未发现名称包含 Darwin、飞书或 Qwen 的已安装 Skill；仅按名称检查，不等于对其他位置或功能完成审计。 |

在旧工程 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/skills/` 找到 `darvin`、`darvin-image`、`darvin-auto-benchmark`、`lark-shared`、`lark-doc` 和 `lark-wiki` 等 Skill 文件；找到文件不代表已安装或已验证可用。本工程及旧工程的文件名搜索未发现 Qwen Skill。

## Docker 与镜像仓库

- `docker info --format '{{.ServerVersion}} {{.OperatingSystem}}'` 在受限环境内因访问 `/var/run/docker.sock` 被拒绝而失败；获授权后同一检查成功，输出 `29.5.3 Ubuntu 22.04.5 LTS`。
- 获授权后执行 `docker info --format 'ServerVersion={{.ServerVersion}} OperatingSystem={{.OperatingSystem}} Registry={{.IndexServerAddress}}'`，输出 `ServerVersion=29.5.3 OperatingSystem=Ubuntu 22.04.5 LTS Registry=https://index.docker.io/v1/`。后续 Docker 操作需要相应套接字权限。
- Docker 客户端配置中有比赛 Harbor 仓库 `harbor-contest.4pd.io` 的认证条目，未配置全局凭证存储或单独的凭证助手。凭证仅在内存中用于只读认证检查，未输出或写入报告。
- 使用已确认不计费的代理 `http://172.28.4.16:18999` 检查 `https://example.com`，获授权后返回 HTTP 200。相同代理访问 `https://registry-1.docker.io/v2/` 在 15 秒内超时。因此 Docker Hub 的可达性、认证有效性和推送权限均未确认，超时不等于认证失败。
- 同一不计费代理对 `https://auth.docker.io/token` 和 `https://index.docker.io/v1/` 的小型只读请求均返回超时、HTTP `000`（连接超时限制 5 秒）。用户授权后，确认本机计费代理 `127.0.0.1:7589` 的 mihomo 进程在监听；经该代理请求 Docker Hub 的 `/v2/` 返回 HTTP 401，说明网络到达且需要认证，并不证明本机已登录 Docker Hub。
- 通过不计费代理请求 Harbor `/v2/` 返回 HTTP 401；使用现有 Docker 凭证只读请求 Harbor `/api/v2.0/users/current` 返回 HTTP 200，确认该凭证的认证有效。未执行推送，推送权限尚未验证。

## 平台认证与模型调用

飞书 CLI 原先的 `auth status` 显示用户身份 `needs_refresh`。使用不计费代理执行 `lark-cli auth status --verify` 后，bot 和 user 均返回 `verified: true`、`server verification succeeded after refresh`；随后重新读取本地状态，用户身份为 `ready`、token 状态为 `valid`，bot 为 `ready`。未执行登录；这些结果不能证明比赛资料访问权限。旧工程文档指出 `auth check <scope>` 可检查指定权限，但实际所需 scope 尚未确定，未执行该检查。

Darwin CLI 此前的 `auth inspect --json` 经不计费代理返回 `AUTH_REQUIRED`。端口转发调整和用户操作后，直接运行 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin auth inspect` 返回 `warning`、身份 `unknown`，提示身份服务不可用；该结果不能证明登录成功或失败。当前终端的大小写 HTTP(S) 代理变量指向计费代理 `127.0.0.1:7589`，因此这次直接检查可能经过该代理，实际路径未确认。

随后通过 `curl --proxy http://172.28.4.16:18999 https://example.com` 的小型检查确认不计费代理返回 HTTP 200；明确设置大小写 HTTP(S) 代理变量为该地址后，再次运行上述 `darvin auth inspect`，返回 `success`，身份为 `authenticated`，`solution.submit`、`subnet.create` 和 `task.create` 均显示 `eligible`。身份标识不记录在报告中。CLI 说明各操作仍由后端逐次授权，因此这不是实际提交成功的证明。

本次用 `command -v` 检查，`codex` 和 `docker` 可在 PATH 中找到，`qwen`、`hf`、`huggingface-cli`、`lark` 和 `darvin` 不在 PATH 中。经用户授权，从免费代理获取系统软件源的 GitHub CLI 安装包，SHA-256 与本机软件源元数据一致，安装至 `/mnt/disk3/liuyutong_home/.local/bin/gh`，版本为 2.4.0。用户完成登录后，通过计费代理执行 `gh api user --jq .login`，确认账号为 `shuizhonghaitong`；已按授权创建公开仓库 https://github.com/shuizhonghaitong/darvin_auto，并使用 GitHub CLI 凭证辅助程序成功推送 `master`。旧工程有 Hugging Face wheel，但尚未确认 CLI 可运行；计费代理对 `huggingface.co` 的请求返回 HTTP 200，未发现本地 Hugging Face token 文件或相关令牌环境变量，因此本机认证尚未确认。Qwen 通过以下本地服务接口验证，无需 Qwen CLI。

另发现现有 Codex 配置指定模型 `qwen3.8-27b`，服务地址为内网 `172.28.4.81:8020`。直接检查其 `/v1/models` 端点，在获授权的环境中返回连接被拒绝（HTTP `000`）；未经过代理，未调用模型。该结果只说明当时目标端口不可连接，不能判断模型或认证是否有效。

用户确认 Qwen 应使用卡 4–7 上的四个实例，无需认证。经 GPU UUID、进程及启动参数对应检查，四个 SGLang 实例依次监听本机端口 12804–12807。以下检查均使用 `--noproxy '*'`，没有经过外部代理：

- 对四个端口分别执行 `curl --noproxy '*' -sS --max-time 5 http://127.0.0.1:端口/v1/models`，均返回模型 ID `qwen3.8-27b-fp8`。
- 对四个端口分别执行 `curl --noproxy '*' -sS --max-time 45 -H 'Content-Type: application/json' -d '{"model":"qwen3.8-27b-fp8","messages":[{"role":"user","content":"Reply OK only."}],"max_tokens":32,"temperature":0,"chat_template_kwargs":{"enable_thinking":false}}' http://127.0.0.1:端口/v1/chat/completions`，均成功返回内容 `OK`、结束原因 `stop`。这验证了四个实例的实际推理调用，但不代表其他任务的质量或并发性能已验证。

## 待解决事项

1. 确认并复用上述平台的实际工具入口和版本查询、认证检查方式；逐项核验访问比赛、飞书资料、候选来源和模型服务所需权限，不输出凭证。
2. Qwen 的四个本地实例均已完成真实调用；后续按需复用上述端口，不需要认证。
3. Harbor 的访问和现有凭证认证已验证；具体镜像路径及推送权限尚未验证。GitHub CLI 登录与代码推送已验证；Hugging Face 认证仍待确认。
4. 重新检查所需 Skills 的实际位置和可用性；补全各项证据后再复核 T0 验收。

本报告反映当前检查结果，不代表环境准备完成。
