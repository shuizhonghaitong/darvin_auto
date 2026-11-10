# TICKET-0 运行环境核验报告

日期：2026-11-08。范围是运行环境基线和最小调用验证，不实现比赛流程。

## 最新验收复核与后续安排（2026-11-08）

用户决定将 Darwin 执行环境对目标 Harbor 镜像的完整拉取验证留到实际提交时；此前宿主机认证、仓库令牌授权及匿名 manifest 访问的结果不能代替该验证。本次不创建 Darwin 任务、不推送镜像，也不提交方案。本节对下方各次检查的历史状态作最新汇总，不改变其当时的观测结果。

按 `TICKETS.md` 中 TICKET-0 的四条验收标准复核：

1. 能力盘点已列出来源、调用方式、证据及限制；旧工程能力仅完成文件和历史证据盘点，尚未在目标运行环境逐项验证。
2. 现有 `native-skill-run.log` 记录了目标 Codex CLI 使用 Qwen、发现并使用指定的最小测试 Skill、调用工具并在返回后继续完成任务。该证据不代表生产总控 Skill 或旧工程 Skill 已通过验证。
3. 本报告的“最小编排与交接约定”已说明总控方式、输入、阶段产物位置和失败记录方式；这些是约定，不代表后续流程已经实现。
4. 本报告记录了本次认证、网络和权限检查及其未验证项。该条要求如实记录，并不要求将所有未验证权限视作通过。

据现有记录，上述四条已有对应证据，可供 TICKET-0 验收复核；这不等同于 P0 总体阶段的所有平台权限均已验证。P0 暂维持“部分通”：目标 Harbor 仓库已有令牌 `push` 授权，但未实际推送；Darwin 侧完整拉取未验证；具体比赛资源权限也未验证。是否需要验证其他仓库，以实际比赛目标为准。

可继续的工作是基于旧 `darwin_auto` 工程的镜像制作、提交实现和历史回执，整理可复用入口及适用范围，并在后续相应 Ticket 中验证；同时梳理实际比赛需要哪些资源权限和仍有冲突的提交规则。不要把历史提交成功或令牌授权写成当前目标镜像已完整拉取或实际推送成功。待用户授权实际提交时，再核对目标比赛、镜像名称与摘要，并根据平台执行记录确认实际拉取结果。

## 旧工程复用范围与实际比赛待核实事项（2026-11-08）

本节依据旧工程本地交接说明和 Skill 文档整理，不代表对当前比赛或平台状态的实时核验；本次未构建、发布镜像，未创建任务或提交方案。

### 镜像与提交入口

- 旧工程 `skills/darvin-image/SKILL.md` 提供镜像制作方法：先获取比赛服务契约、基线源码、权重和依赖，再按实际架构、启动方式、端口及资源限制构建，并用真实镜像验证服务就绪与输入输出。构建脚本可能附带推送，应先检查；不能将文档或本地测试视为 Darwin 节点拉取成功。
- 旧图像鉴伪比赛使用既有 Harbor 镜像配置；旧工程 `skills/darvin/references/artifacts.md` 另描述平台镜像发布入口：`darvin image publish` 从目录构建并发布，`darvin image push` 发布已有的本地 linux/amd64 镜像，不负责拉取缺失镜像或重新构建。平台选择私有仓库；发布回执 READY 不等于运行节点拉取成功，也不自动创建任务或提交。两条路径的仓库、权限和证明范围不可互换；实际操作前还须核对当前 CLI 版本及帮助。
- 旧工程 `submission/image_auth_workflow.py` 是特定图像鉴伪榜的入口，使用已有镜像和配置，不负责模型搜索、镜像构建或发布，也不是任意比赛通用入口。当前代码明确禁止新提交，直到权威合约、镜像 digest 和完整提交历史的证据采集接入；有明确任务号可恢复跟踪，提交结果未知且无任务号时须先人工对账。`submission/run_pipeline.sh` 仍被显式禁用，不应运行或解除保护。

### 历史回执及其边界

- 旧工程 `submission/SUBMISSION.md` 与 `submission/image_auth_independent_20261104/` 记录了 2026-11-04 图像真伪鉴定榜的一次独立试跑：提交 356、任务成功、评测作业 SUCCEEDED，得分 42.08，日志记录 120/120 条推理成功。这证明当时特定既有镜像和配置下的预检、提交、跟踪和取分链路；未重新验证从比赛 URL 获取要求、搜索方案、适配、构建和发布镜像，亦不证明当前排名或其他比赛可用。
- 旧工程当前配置中的镜像与另一份历史评测日志之间未建立对应关系，不能仅凭配置声称该日志验证了该镜像；上述历史回执也不能证明本 Ticket 目标 Harbor 镜像已被 Darwin 完整拉取。

### 实际比赛开始前的核实清单

- **规则与契约：**以目标比赛的权威页面、子网合约及模板核对参赛资格、报名和截止时间、提交次数或频率限制、评分与有效回执规则，以及方案类型、输入输出、服务端口、启动方式、架构和网络限制。旧比赛规则不能直接沿用。
- **账号和资源：**核对对应环境及账号的报名/参赛资格、目标子网和模型访问、创建任务与提交方案权限、可用额度，以及 CPU、内存、GPU、运行时长、网络等配额；登录或资格检查通过不等于各资源授权均通过。
- **数据与制品：**核对比赛数据、权重及 Hugging Face 等来源的访问和使用许可；分别确认镜像仓库读取/写入、Darwin 节点镜像拉取、附件上传和运行时挂载读取权限。旧文档中的文件上传回执和镜像 READY 均不能替代运行时验证。
- **提交安全：**确认目标子网的镜像字段和固定 digest 的填写方式、镜像与提交历史、日志可见性及去重恢复方式；提交结果不明时先查询对账，不盲目重试。实际比赛经授权提交时再验证目标 Harbor 镜像的完整拉取，并保留脱敏证据。

上述是待核实清单，不表示目标比赛存在某项特定限制或已具备对应权限。当前 TICKET-0 的已有验收证据与 P0「部分通」状态不因历史项目成功而升级；目标 Codex CLI + Qwen 的完整比赛链路仍未验证。

## 能力盘点

| 能力与来源 | 调用方式 | 验证结果 | 未知或限制 |
| --- | --- | --- | --- |
| Codex CLI，本机安装 | `codex --version`; `codex exec --help` | 分别退出 0；版本 0.162.1。输出见 `commands.log`。 | 版本和帮助不证明现有总控 Skill 可用。 |
| 本地 Qwen，127.0.0.1:12804 | `codex exec` 配置 local responses provider 和 `qwen3.8-27b-fp8` | 实际执行两次最小任务并退出 0，见两个 Qwen 日志。 | 本次仅实际运行 12804；其余三个实例仅有历史记录。模型元数据解析告警后使用回退配置。 |
| 测试 Skill，`runs/t0-runtime-check/.agents/skills/t0-smoke-check/SKILL.md` | 在该运行目录执行 `codex exec`，提示中指定 `$t0-smoke-check` | 原生发现该 Skill；模型调用 `pwd`，读取结果后输出 `T0_NATIVE_SKILL_CONTINUED`，退出 0。见 `native-skill-run.log`。 | 这是专为运行验证创建的最小 Skill，不是生产总控 Skill。 |
| 旧工程 Skill，`/mnt/disk3/liuyutong_home/workspace/darwin_auto/skills/` | 各目录的 `SKILL.md`；详见根目录 `ENVIRONMENT_REPORT.md` | 历史盘点包括 darvin、darvin-image、darvin-auto-benchmark、lark-shared、lark-doc、lark-wiki 和 open-source-baseline；文件可读。 | 旧版本未在本次加载或验证，不能认定其可用或适合直接复用；改写属于后续工作。 |
| Docker，宿主机服务 | `docker info` | 宿主机检查退出 0，服务版本 29.5.3；记录中敏感配置行已脱敏。 | 默认受限执行环境不能访问 Docker socket；构建和推送未在本次执行。 |
| Darwin CLI，旧工程 `runtime/venv/bin/darvin` | `darvin auth inspect --json` | 后续复核退出 0，认证状态为 `authenticated`。 | 特定比赛资源权限未知。 |
| 飞书 CLI | `lark-cli auth status --verify --json` | 后续复核退出 0，bot 和 user 均已验证，user token 状态为 valid。 | 特定比赛资源权限未知。 |
| Harbor 镜像仓库 | `/v2/`、用户 API 与 Docker 凭证机制；见 `ENVIRONMENT_REPORT.md` | 宿主机直连恢复，当前用户 API 返回 200；历史目标仓库的令牌授权包含 `push`，详见下方。 | 已验证当前认证及指定仓库的推送授权；未实际推送，Darwin 拉取权限未验证。 |
| GitHub / Hugging Face CLI | `gh auth status`；`hf auth whoami` | 前者退出 0；后者此前退出 1，用户重新登录后复核退出 0 并返回登录身份。 | 特定资源权限未知，Hugging Face 的 Git credential helper 未配置。 |

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

## 继续核验（2026-11-08）

- 固定使用不计费代理 `http://172.28.4.16:18999`，在获授权的宿主机环境执行 `curl --silent --show-error --output /dev/null --write-out 'HTTP=%{http_code}\n' --max-time 12 --proxy http://172.28.4.16:18999 https://example.com`，退出 0、HTTP 200。受限环境中的同一请求退出 7；这两项结果不保证其他外部服务均可访问。
- 使用该代理并设置大小写 HTTP(S) 代理变量，执行旧工程的 `runtime/venv/bin/darvin auth inspect --json`，退出 0；仅核验安全字段：顶层状态 `success`，`data.authentication.state` 为 `authenticated`。
- 使用相同代理设置执行旧工程的 `runtime/lark-cli-1.0.98/lark-cli auth status --verify --json`，退出 0；根级 `verified` 为 true，bot 与 user 的 `status` 均为 ready、`available` 和 `verified` 均为 true，user 的 `tokenStatus` 为 valid。未将身份信息或凭证写入本报告。
- Hugging Face 的 `hf auth whoami` 既有检查退出 1；用户反馈错误为 `Invalid user token` / `Invalid username or password`。用户重新登录后，在获授权的宿主机环境固定使用不计费代理 `http://172.28.4.16:18999`，设置大小写 HTTP(S) 代理变量，执行 `/mnt/disk3/liuyutong_home/.local/share/darvin-auto/hf-cli-py311/bin/hf auth whoami`，退出 0，标准输出非空并返回登录身份。输出仅检查、不记录身份或凭证；该结果不证明特定模型或数据集的访问权限。
- 以上是对前述补充检查中输出截断问题的后续复核，不代表已验证 Darwin 特定比赛权限、飞书特定资源权限或 Harbor 当前认证和推送权限。其余三个 Qwen 实例本次仍未逐一调用；用户确认 GPU 4–7 上的四个实例可用，但不替代逐个执行证据。

## Harbor 与 Darwin 镜像权限复核（2026-11-08）

- 宿主机上显式使用不计费代理 `http://172.28.4.16:18999` 请求 `https://harbor-contest.4pd.io/v2/`：`curl --proxy http://172.28.4.16:18999 --noproxy '' --connect-timeout 5 --max-time 12 -sS -o /dev/null -w 'HTTP %{http_code}\n' https://harbor-contest.4pd.io/v2/` 退出 28，代理 CONNECT 超时，HTTP 000。
- `ss -ltnp 'sport = :7589'` 在宿主机确认 mihomo 正在监听；随后将上述命令的代理替换为 `http://127.0.0.1:7589`，退出 28，TLS 连接超时，HTTP 000。经该计费代理以同样的超时设置请求 `https://example.com`，退出 0、HTTP 200：代理对照请求可用，但不证明 Harbor 可达或认证失败。本次仅发起小流量请求，未下载或推送镜像。
- 因 Harbor 未建立可用连接，未能验证现有 Docker 凭据的当前有效性或指定项目的写入权限；历史 API 200 和历史推送不代表当前权限。未进行写入操作，不能声称实际推送通过。
- 旧工程 `runtime/venv/bin/darvin image --help` 退出 0，列出 `publish` 和 `push`，未提供只读的 Darwin 侧镜像拉取权限检查。Darwin 执行主体对具体 Harbor 镜像的网络访问、凭据和实际拉取均未验证；本次未提交比赛。需在明确目标镜像及获授权的 Darwin 执行环境中进行实际拉取验证。
- TICKET-0 和 P0 仍为“部分通”：以上未验证权限须明确保留；镜像构建、推送与授权环境实际拉取属于 P5 后续验证，不能用本次连接检查替代。

## Harbor 直连与仓库授权复核（2026-11-08）

- 宿主机执行 `getent ahostsv4 harbor-contest.4pd.io`，退出 0，解析到私有地址 `172.28.5.32`。此前强制代理的两条路径均未连通；该私有服务可通过宿主机直连访问。未更改全局代理或认证配置。
- 宿主机执行 `curl --noproxy '*' --connect-timeout 5 --max-time 12 -sS -o /dev/null -w 'HTTP %{http_code}\n' https://harbor-contest.4pd.io/v2/`，退出 0、HTTP 401：网络及 TLS 已连通，服务要求认证；未认证的 401 不是凭据失效的证据。
- 使用现有 Docker Harbor 凭据，通过禁用代理的只读 HTTPS 请求访问 `/api/v2.0/users/current` 和 `/api/v2.0/projects/liuyutong`，均返回 HTTP 200；项目元数据标记为公开。凭据未输出或写入报告。
- 对历史记录中的目标仓库 `liuyutong/darvin-exam-baseline` 请求 Registry 令牌，所请求 scope 为 `pull,push`，令牌服务返回 HTTP 200；解析授权声明得到该仓库的 actions 包含 `pull` 和 `push`。这证明当前令牌对该具体仓库授予推送授权，不证明实际镜像推送成功，也不保证其他仓库同样有权写入。未输出令牌，未执行推送或比赛提交。
- Darwin 执行主体是否能够访问并拉取该镜像仍未验证。TICKET-0 / P0 保持“部分通”；P5 在明确目标和授权后，应分别验证真实推送及 Darwin 环境实际拉取。

## Darwin 镜像拉取条件补充核验（2026-11-08）

- 在获授权的宿主机环境直连 `https://harbor-contest.4pd.io/v2/`，返回 HTTP 401，确认宿主机到 Registry 的网络及 TLS 可达；这不代表 Darwin 执行环境的网络可达。
- 对 `liuyutong/darvin-exam-baseline` 匿名请求 Registry 的 `pull` 令牌，返回 HTTP 200，令牌授权声明包含该仓库的 `pull`。使用既有 Docker 凭据请求同一仓库的令牌也返回 HTTP 200，授权声明包含 `pull`、`push`。未记录凭据或令牌。
- Harbor 管理 API 返回 HTTP 200，确认仓库存在一个 artifact，标签为 `startup-qwen-20261103-v1`，摘要为 `sha256:4efc8d5aca6cc0dcbf8b4be8b8222827cde0b53bba667228839209f7903e2627`。使用匿名拉取令牌并在请求中声明 OCI / Docker 镜像清单格式后，按标签和摘要访问 Registry manifest 接口均返回 HTTP 200。此前未声明这些格式的请求返回 404，不应据此判断镜像不存在。
- 上述检查仅证明宿主机可匿名读取该镜像清单，未读取完整镜像层，也未证明 Darwin 执行主体的网络、镜像层读取或实际拉取成功。旧工程留有其他历史执行证据，但不能代替此标签的 Darwin 实际拉取证据；本次未推送镜像或提交比赛。
- TICKET-0 / P0 仍为“部分通”。下一步需在明确授权的 Darwin 执行环境内对上述具体镜像执行完整拉取并独立检查结果；如平台只能通过比赛提交触发拉取，应先明确比赛和提交授权。P5 的实际推送和完整拉取验收仍未完成。

## Darwin 执行环境完整拉取复核（2026-11-08）

- 检查旧工程安装的 `runtime/venv/bin/darvin` 顶层及 `image`、`solution`、`task`、`job`、`subnet` 帮助，未发现直接进入 Darwin 执行环境或对指定 Harbor 镜像发起独立完整拉取的 CLI 命令。`task create` 要求已有方案的 `model-app-id`、子网地址和任务名，不接受镜像引用；它会创建训练任务，不能作为无副作用的指定镜像拉取验证。
- 在 `runs` 和旧工程 `exam_baseline` 的相关文本文件中搜索目标标签及摘要，未发现目标修复版镜像的 Darwin 执行记录。旧工程 README 指出仍需核实考题榜单子网地址；旧版镜像的 READY 记录不能代替目标修复版的证据。
- 本轮未进入 Darwin 执行环境，未执行完整拉取，也未创建训练任务或提交比赛。因此 Darwin 侧的网络、全部镜像层读取及完整落地仍未验证；TICKET-0 / P0 保持“部分通”。
- 下一步需要可访问的 Darwin 执行环境或专门的镜像拉取入口。如果只能通过训练任务或方案提交触发，请明确具体子网、对应目标镜像的方案，并授权创建任务或提交比赛；再通过平台侧记录独立核实完整拉取。

## DEV 查询与旧工程历史证据（2026-11-08）

- 只读运行旧工程 CLI 的 `subnet list --profile dev --size 5` 和 `solution list --profile dev --size 5`，两者均退出码 1，提示本机 `dev` profile 没有登录会话。因此尚不能列出或确认可用 DEV 子网、方案及其对目标 Harbor 镜像的支持；这不是网络故障或权限不足的证明。
- 旧工程 `darwin_auto/submission/SUBMISSION.md` 记录了 2026-11-04 的图像鉴伪榜真实试跑：提交号 356、任务和作业已创建，评测 120/120 推理成功并取得 42.08 分。这是历史链路证据，不证明当前 DEV 可用，也未证明本次目标镜像已被 Darwin 完整拉取；该文档亦说明当前配置不能证明历史评测所用的镜像身份。
- 旧工程的 DEV 验证文档可作为后续操作参考，但尚未确认适用的 DEV 子网及目标镜像方案。本轮未创建任务或提交，也未尝试登录或变更认证。
- 可将目标镜像的 Darwin 侧完整拉取验证安排到首次获得授权的实际运行或提交前后：在真正提交前核实镜像身份、方案和拉取配置；当平台只有创建任务或提交才能触发拉取时，以节点或作业记录确认完整拉取，再认定验证通过。届时若拉取失败，需处理权限、网络或镜像问题；不能提前标记为通过。TICKET-0 / P0 仍为“部分通”。

## Darwin 执行入口进一步排查（2026-11-08）

- 检查旧工程 `darvin_cli/services/solution_service.py` 的预检实现：运行时检查标为 `unverified`，说明镜像拉取、附件挂载和评测须在运行时确认；预检不能作为完整拉取证据。
- 旧工程 `skills/darvin/references/dev-artifact-tests.md` 提供一条潜在的 DEV 验证路径：在获授权的 DEV 测试中使用方案与运行任务，并依据节点运行记录区分镜像拉取、挂载和业务错误。该文档明确是待执行验收计划，不是通过证明；它要求获授权账号、DEV 子网及节点拉取配置，且需对运行任务单独授权。尚未确认此路径能否直接使用本次目标 Harbor 镜像，也未找到可直接进入 Darwin 节点的环境或独立完整拉取入口。
- 本机检查 `kubectl`、`oc`、`k9s` 均未找到；这仅描述当前环境，不代表平台不存在其他管理入口。本轮未发起镜像下载、创建任务或提交比赛，未取得 Darwin 节点实际拉取证据。
- TICKET-0 / P0 保持“部分通”。建议提供获授权的 Darwin 执行环境或平台专用拉取验证入口；若选择 DEV 路径，先确认目标镜像可被使用、提供具体 DEV 子网及对应方案，并明确授权创建测试任务，之后核对平台节点的完整拉取记录。目标 Codex CLI + Qwen 环境的相关端到端验收仍未完成。
