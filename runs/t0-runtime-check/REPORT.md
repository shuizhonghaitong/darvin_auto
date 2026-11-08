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
| Darwin CLI，旧工程 `runtime/venv/bin/darvin` | `darvin auth inspect` | 历史核验提示身份服务不可用，未确认身份；见 `ENVIRONMENT_REPORT.md`。 | 本次未重新核验，当前登录状态未知。 |
| 飞书 CLI | `auth status --verify` | 历史记录显示 bot 和 user 验证成功；见 `ENVIRONMENT_REPORT.md`。 | 本次未重新核验；特定比赛资源权限未知。 |
| Harbor 镜像仓库 | `/v2/`、用户 API 与 Docker 凭证机制；见 `ENVIRONMENT_REPORT.md` | 历史记录显示服务可达且用户 API 返回 200。 | 本次未重新核验；本票没有执行推送，特定仓库权限未知。 |
| GitHub / Hugging Face CLI | 已有 CLI 的认证检查；见 `ENVIRONMENT_REPORT.md` | 历史记录显示账户认证成功。 | 本次未重新核验；特定资源权限未知，Hugging Face 的 Git credential helper 未配置。 |

## 环境与权限

- 工作区可读写：本次已创建本目录中的测试 Skill、日志和本报告。测试中的模型以只读模式运行。
- 本次本地 Qwen HTTP 接口在受限执行环境连接失败；在获授权的宿主机执行环境中 `/v1/models` 与 `/v1/responses` 返回 HTTP 200，实际模型调用成功。该结果只证明当前本地路径可用，不证明外网连接。
- 外网、代理和外部服务认证结果均以根目录 `ENVIRONMENT_REPORT.md` 的历史证据为准；本次未重新核验，不将历史结果视作当前状态。未使用计费代理或下载依赖。
- Docker 服务在宿主机可用，受限环境对 socket 的权限不足；镜像构建、仓库写权限和 Darwin 提交均未验证。

## 最小编排与交接约定

一次非交互 `codex exec` 接收用户任务、运行目录和明确指定的 Skill；Skill 给出操作步骤，模型通过工具执行并消费返回结果，再输出结果。本次可观测输入为提示和测试 Skill，运行产物集中在 `runs/t0-runtime-check/`：`commands.log` 记录基础命令及退出码，`native-skill-run.log` 记录原生 Skill 发现、工具调用和模型继续执行，`qwen-run.log` 记录直接读取 Skill 的补充测试。`SKILL.md` 是补充测试输入，不是生产 Skill。

后续阶段应将实际输入、产物、验证命令及输出放入对应运行目录，并记录失败命令、退出状态和可安全公开的错误；无法验证的能力标记为未验证或阻塞，不以文件存在或模型自述代替验证。本次日志不包含凭证；不将主机认证材料写入产物。

## 可复验命令

基础检查：`codex --version`、`codex exec --help`、`docker info`；实际输出和退出码见 `commands.log`。原生测试执行命令及完整过程见 `native-skill-run.log`；补充测试见 `qwen-run.log`。涉及宿主机 socket 或本地服务时，执行权限和网络隔离会影响结果。
