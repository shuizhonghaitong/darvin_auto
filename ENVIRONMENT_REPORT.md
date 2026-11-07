# T0 环境检查报告

检查时间：2026-11-07（Asia/Shanghai）。状态：**T0 环境盘点与报告已完成**；不表示后续比赛流程所需的全部资源权限均已验证。

## 运行位置与凭证边界

- 本次运行目录：`/mnt/disk3/liuyutong_home/workspace/darvin_auto`；本报告保存于该目录的 `ENVIRONMENT_REPORT.md`。其他阶段的产物目录尚未确定，不预设其结构。
- Darwin、飞书、GitHub、Hugging Face 和模型服务的认证应使用宿主管理的既有凭证，仅供宿主相应工具使用，不写入报告、代码或最终镜像。
- 镜像仓库凭证仅供镜像仓库认证、拉取或推送使用；不得因此将宿主其他平台凭证打包进镜像。本次未向镜像仓库推送镜像，也未提交 Darwin 比赛。

## 工具与 Skill

初次检查时 `darwin`、`feishu`、`lark`、`gh`、`hf`、`huggingface-cli`、`qwen` 均未在当前 PATH 中找到；后续已找到或安装下述独立入口，PATH 未必包含这些路径。

| 检查命令 | 实际输出或结果 |
|---|---|
| `docker --version` | `Docker version 29.5.3` |
| `codex --version` | `codex-cli 0.162.1`；另提示 PATH aliases 无法创建，文件系统只读。 |
| `/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/lark-cli-1.0.98/lark-cli --version` | `lark-cli version 1.0.98`。 |
| `/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin --version` | `0.5.2`。 |
| `/mnt/disk3/liuyutong_home/.local/bin/gh --version` | `gh version 2.4.0`。 |
| Hugging Face 独立环境的 `hf --version` | 不支持此参数；使用该环境的 `python -c 'import importlib.metadata; print(importlib.metadata.version("huggingface-hub"))'` 查询安装包，输出 `0.36.2`。CLI 位于 `/mnt/disk3/liuyutong_home/.local/share/darvin-auto/hf-cli-py311/bin/hf`。 |
| 检查 `/mnt/disk3/liuyutong_home/.codex/skills` | 未发现名称包含 Darwin、飞书或 Qwen 的已安装 Skill；仅按名称检查，不等于对其他位置或功能完成审计。 |

在旧工程 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/skills/` 找到 `darvin`、`darvin-image`、`darvin-auto-benchmark`、`lark-shared`、`lark-doc` 和 `lark-wiki` 等 Skill 文件；找到文件不代表已安装或已验证可用。本工程及旧工程的文件名搜索未发现 Qwen Skill。

再次检查上述六个 Skill 及 `open-source-baseline` 的 `SKILL.md` 均可读取，名称和用途声明分别覆盖平台操作、镜像、流程编排、飞书认证与文档、知识库和开源基线。它们不在本会话提供的可用 Skill 列表中，未验证会话加载或完整工作流；相关 CLI 的独立验证不等于 Skill 已安装或端到端可用。

## Docker 与镜像仓库

- `docker info --format '{{.ServerVersion}} {{.OperatingSystem}}'` 在受限环境内因访问 `/var/run/docker.sock` 被拒绝而失败；获授权后同一检查成功，输出 `29.5.3 Ubuntu 22.04.5 LTS`。
- 获授权后执行 `docker info --format 'ServerVersion={{.ServerVersion}} OperatingSystem={{.OperatingSystem}} Registry={{.IndexServerAddress}}'`，输出 `ServerVersion=29.5.3 OperatingSystem=Ubuntu 22.04.5 LTS Registry=https://index.docker.io/v1/`。后续 Docker 操作需要相应套接字权限。
- Docker 客户端配置中有比赛 Harbor 仓库 `harbor-contest.4pd.io` 的认证条目，未配置全局凭证存储或单独的凭证助手。凭证仅在内存中用于只读认证检查，未输出或写入报告。
- 使用已确认不计费的代理 `http://172.28.4.16:18999` 检查 `https://example.com`，获授权后返回 HTTP 200。相同代理访问 `https://registry-1.docker.io/v2/` 在 15 秒内超时。因此 Docker Hub 的可达性、认证有效性和推送权限均未确认，超时不等于认证失败。
- 同一不计费代理对 `https://auth.docker.io/token` 和 `https://index.docker.io/v1/` 的小型只读请求均返回超时、HTTP `000`（连接超时限制 5 秒）。用户授权后，确认本机计费代理 `127.0.0.1:7589` 的 mihomo 进程在监听；经该代理请求 Docker Hub 的 `/v2/` 返回 HTTP 401，说明网络到达且需要认证，并不证明本机已登录 Docker Hub。
- 通过不计费代理请求 Harbor `/v2/` 返回 HTTP 401；使用现有 Docker 凭证只读请求 Harbor `/api/v2.0/users/current` 返回 HTTP 200，确认该凭证的认证有效。未执行推送，推送权限尚未验证。
- 旧工程 `darwin_auto/exam_baseline/README.md` 记录曾上传 `harbor-contest.4pd.io/liuyutong/darvin-exam-baseline:startup-qwen-20261103-v1`，摘要为 `sha256:4efc8d5aca6cc0dcbf8b4be8b8222827cde0b53bba667228839209f7903e2627`；`darwin_auto/resume_baseline/README.md` 记录曾上传 `harbor-contest.4pd.io/liuyutong/darvin-resume-baseline:startup-qwen-20261103-v1`，摘要为 `sha256:79aff98a1d18c7c1064a7f6bb1ccf67f7730ffd174d75307b7c68a7c31a4f2df`。这是历史推送记录，并非本次对当前写权限或比赛平台拉取权限的验证；标签也可能变化。

## 平台认证与模型调用

飞书 CLI 原先的 `auth status` 显示用户身份 `needs_refresh`。使用不计费代理执行 `lark-cli auth status --verify` 后，bot 和 user 均返回 `verified: true`、`server verification succeeded after refresh`；随后重新读取本地状态，用户身份为 `ready`、token 状态为 `valid`，bot 为 `ready`。未执行登录；这些结果不能证明比赛资料访问权限。旧工程文档指出 `auth check <scope>` 可检查指定权限，但实际所需 scope 尚未确定，未执行该检查。

Darwin CLI 此前的 `auth inspect --json` 经不计费代理返回 `AUTH_REQUIRED`。端口转发调整和用户操作后，直接运行 `/mnt/disk3/liuyutong_home/workspace/darwin_auto/runtime/venv/bin/darvin auth inspect` 返回 `warning`、身份 `unknown`，提示身份服务不可用；该结果不能证明登录成功或失败。当前终端的大小写 HTTP(S) 代理变量指向计费代理 `127.0.0.1:7589`，因此这次直接检查可能经过该代理，实际路径未确认。

随后通过 `curl --proxy http://172.28.4.16:18999 https://example.com` 的小型检查确认不计费代理返回 HTTP 200；明确设置大小写 HTTP(S) 代理变量为该地址后，再次运行上述 `darvin auth inspect`，返回 `success`，身份为 `authenticated`，`solution.submit`、`subnet.create` 和 `task.create` 均显示 `eligible`。身份标识不记录在报告中。CLI 说明各操作仍由后端逐次授权，因此这不是实际提交成功的证明。

本次用 `command -v` 检查，`codex` 和 `docker` 可在 PATH 中找到，`qwen`、`hf`、`huggingface-cli`、`lark` 和 `darvin` 不在 PATH 中。经用户授权，从免费代理获取系统软件源的 GitHub CLI 安装包，SHA-256 与本机软件源元数据一致，安装至 `/mnt/disk3/liuyutong_home/.local/bin/gh`，版本为 2.4.0。用户完成登录后，通过计费代理执行 `gh api user --jq .login`，确认账号为 `shuizhonghaitong`；已按授权创建公开仓库 https://github.com/shuizhonghaitong/darvin_auto，并使用 GitHub CLI 凭证辅助程序成功推送 `master`。计费代理对 `huggingface.co` 的请求返回 HTTP 200。经用户授权，使用旧工程缓存的安装包离线安装 `huggingface-hub==0.36.2` 至独立环境 `/mnt/disk3/liuyutong_home/.local/share/darvin-auto/hf-cli-py311`；用户登录后，通过计费代理执行该环境的 `bin/hf auth whoami`，返回 `user: lilac`，确认 Hub 认证有效。未验证特定模型、数据集或 Git 推送权限；用户登录输出指出未配置 Git 凭证助手。Qwen 通过以下本地服务接口验证，无需 Qwen CLI。

另发现现有 Codex 配置指定模型 `qwen3.8-27b`，服务地址为内网 `172.28.4.81:8020`。直接检查其 `/v1/models` 端点，在获授权的环境中返回连接被拒绝（HTTP `000`）；未经过代理，未调用模型。该结果只说明当时目标端口不可连接，不能判断模型或认证是否有效。

用户确认 Qwen 应使用卡 4–7 上的四个实例，无需认证。经 GPU UUID、进程及启动参数对应检查，四个 SGLang 实例依次监听本机端口 12804–12807。以下检查均使用 `--noproxy '*'`，没有经过外部代理：

- 对四个端口分别执行 `curl --noproxy '*' -sS --max-time 5 http://127.0.0.1:端口/v1/models`，均返回模型 ID `qwen3.8-27b-fp8`。
- 对四个端口分别执行 `curl --noproxy '*' -sS --max-time 45 -H 'Content-Type: application/json' -d '{"model":"qwen3.8-27b-fp8","messages":[{"role":"user","content":"Reply OK only."}],"max_tokens":32,"temperature":0,"chat_template_kwargs":{"enable_thinking":false}}' http://127.0.0.1:端口/v1/chat/completions`，均成功返回内容 `OK`、结束原因 `stop`。这验证了四个实例的实际推理调用，但不代表其他任务的质量或并发性能已验证。

## 后续风险与处理方式

1. 比赛和飞书资料的具体权限尚未确认；确定目标资源及所需 scope 后，使用对应 CLI 检查，例如飞书的 `auth check <scope>`，并在需要时申请授权。
2. GitHub 和 Hugging Face 的特定资源权限尚未确认；确定候选仓库、模型或数据集后分别验证访问权限。Hugging Face 的 Git 凭证助手未配置，如需 Git 推送再选择安全的认证方式。
3. Harbor 当前推送权限和比赛平台拉取权限尚未验证；历史推送记录不能替代当前验证。实际推送前应确认目标及授权，并验证比赛平台能否拉取。
4. 旧工程相关 Skill 文件可读，但尚未验证在本会话中加载或实际执行；后续需要时再验证其加载和对应工作流。

本报告完成 T0 所要求的盘点和证据记录，不代表后续阶段已完成，也不保证未验证的权限可用。
