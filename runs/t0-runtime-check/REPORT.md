# TICKET-0 运行环境核验报告

日期：2026-11-08。范围是运行环境基线和最小调用验证，不实现比赛流程。

## 能力盘点

| 能力与来源 | 调用方式 | 验证结果 | 未知或限制 |
| --- | --- | --- | --- |
| Codex CLI，本机安装 | `codex --version`; `codex exec --help` | 分别退出 0；版本 0.162.1。输出见 `commands.log`。 | 版本和帮助不证明现有总控 Skill 可用。 |
| 本地 Qwen，127.0.0.1:12804 | `codex exec` 配置 local responses provider 和 `qwen3.8-27b-fp8` | 实际执行两次最小任务并退出 0，见两个 Qwen 日志。 | 本次仅实际运行 12804；其余三个实例仅有历史记录。模型元数据解析告警后使用回退配置。 |
| 测试 Skill，`runs/t0-runtime-check/.agents/skills/t0-smoke-check/SKILL.md` | 在该运行目录执行 `codex exec`，提示中指定 `$t0-smoke-check` | 原生发现该 Skill；模型调用 `pwd`，读取结果后输出 `T0_NATIVE_SKILL_CONTINUED`，退出 0。见 `native-skill-run.log`。 | 这是专为运行验证创建的最小 Skill，不是生产总控 Skill。 |
| 旧工程 Skill，`/mnt/disk3/liuyutong_home/workspace/darwin_auto/skills/` | 各目录的 `SKILL.md`；详见根目录 `ENVIRONMENT_REPORT.md` | 历史盘点包括 darvin、darvin-image、darvin-auto-benchmark、lark-shared、lark-doc、lark-wiki 和 open-source-baseline；文件可读。 | 旧版本未在本次加载或验证，不能认定其可用或适合直接复用；改写属于后续工作。 |
| Docker，宿主机服务 | `docker info` | 宿主机检查退出 0，服务版本 29.5.3；记录中敏感配置行已脱敏。 | 默认受限执行环境不能访问 Docker socket；构建和推送未在本次执行。 |
| Darwin CLI，旧工程 `runtime/venv/bin/darvin` | `darvin auth inspect` | 本次命令退出 0；历史核验提示身份服务不可用。 | 输出核验遇到工具截断，退出 0 不证明已登录，当前身份未知。 |
| 飞书 CLI | `lark-cli auth status --verify` | 本次命令退出 0；历史记录显示 bot 和 user 验证成功。 | 本次未核实状态输出，不能仅凭退出码确认认证；特定比赛资源权限未知。 |
| Harbor 镜像仓库 | `/v2/`、用户 API 与 Docker 凭证机制；见 `ENVIRONMENT_REPORT.md` | 历史记录显示服务可达且用户 API 返回 200。 | 本次未重新核验；本票没有执行推送，特定仓库权限未知。 |
| GitHub / Hugging Face CLI | `gh auth status`；`hf auth whoami` | 本次前者退出 0，后者退出 1；历史记录显示账户认证成功。 | Hugging Face 失败原因未确认；特定资源权限未知，Hugging Face 的 Git credential helper 未配置。 |

## 环境与权限

- 工作区可读写：本次已创建本目录中的测试 Skill、日志和本报告。测试中的模型以只读模式运行。
- 本次本地 Qwen HTTP 接口在受限执行环境连接失败；在获授权的宿主机执行环境中 `/v1/models` 与 `/v1/responses` 返回 HTTP 200，实际模型调用成功。该结果只证明当前本地路径可用，不证明外网连接。
- 本次复核：不计费代理 `172.28.4.16:18999` 请求 GitHub 超时（curl 退出 28）；确认本地 `127.0.0.1:7589` 的 mihomo 监听后，按已授权范围切换到计费代理，GitHub 首页和 Hugging Face 模型元数据接口均返回 HTTP 200。仅做少量请求，未下载依赖或模型。外部服务的历史结果不能代替当前状态。
- Docker 服务在宿主机可用，受限环境对 socket 的权限不足；镜像构建、仓库写权限和 Darwin 提交均未验证。

## 最小编排与交接约定

一次非交互 `codex exec` 接收用户任务、运行目录和明确指定的 Skill；Skill 给出操作步骤，模型通过工具执行并消费返回结果，再输出结果。本次可观测输入为提示和测试 Skill，运行产物集中在 `runs/t0-runtime-check/`：`commands.log` 记录基础命令及退出码，`native-skill-run.log` 记录原生 Skill 发现、工具调用和模型继续执行，`qwen-run.log` 记录直接读取 Skill 的补充测试。`SKILL.md` 是补充测试输入，不是生产 Skill。

后续运行的交接位置约定：`runs/<run-id>/inputs/` 保存任务输入，`runs/<run-id>/artifacts/<stage>/` 保存各阶段产物，`runs/<run-id>/logs/` 保存命令和安全输出，`runs/<run-id>/status.md` 记录阶段状态、产物位置、验证结果以及失败命令、退出状态和可安全公开的错误。这是目录约定，不表示后续阶段或状态管理已经实现。本次验证沿用现有 `runs/t0-runtime-check/` 文件布局。

无法验证的能力标记为未验证或阻塞，不以文件存在或模型自述代替验证。本次日志不包含凭证；不将主机认证材料写入产物。

## 本次补充检查与边界（2026-11-08）

- 在宿主机执行 `docker info`，退出 0；`darvin auth inspect` 和 `lark-cli auth status --verify` 均退出 0，但由于输出核验受工具截断影响，不能据此断言当前登录成功。
- 经上述计费代理执行 `gh auth status` 退出 0；执行已有 Hugging Face CLI 的 `hf auth whoami` 退出 1。网站元数据接口可达，但不足以判断认证失败的具体原因或令牌状态。
- Harbor 当前认证和推送未重新验证；历史用户 API 返回 200 和历史推送不能证明当前推送权限。Docker Hub 认证、推送及 Darwin 对镜像的拉取权限也未验证。
- 以上检查未记录或展示令牌、密码或代理凭证；命令退出码与 HTTP 状态是本节的观测证据，失败诊断未取得可靠输出。

## 可复验命令

基础检查：`codex --version`、`codex exec --help`、`docker info`；实际输出和退出码见 `commands.log`。原生测试执行命令及完整过程见 `native-skill-run.log`；补充测试见 `qwen-run.log`。涉及宿主机 socket 或本地服务时，执行权限和网络隔离会影响结果。
