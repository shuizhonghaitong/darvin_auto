# TICKET-2 继续核查记录

状态：阻塞；P2 未达到「已通」。本轮未下载权重、未安装依赖、未选择候选，也未提交比赛。既有候选和证据保留在 `../t2-followup-20261108/`。

## 已核实与仍缺失的条件

- 比赛规格 `../t1-real-20261108/competition_spec.json` 要求输出 `1`、`0_1`、`0_2` 三类；比赛 GPU 资源为半张 A100 40 GB，即约 20 GB。CPU/内存是否为 2 核 / 4 GB 尚未确认。真实服务器的 A100 80 GB 不能代替比赛资源上限。
- ForensicHub 固定版本 `92653068` 存在推理入口，代码许可为 CC BY 4.0；已有 Google Drive 目录证据展示候选权重文件。代码许可不能推断另行分发的权重许可，目录可见亦不证明权重可下载、完整或可用于比赛。对于三类的实际覆盖及映射、权重加载和受限显存/内存实测，证据仍不足。
- FakeShield 的权重约 44.16 GB 是文件大小，不足以单独证明推理显存超过 20 GB；其完整三分类覆盖亦未证明。其他候选亦未证明同时满足入口、权重许可和可获取性、资源约束及三分类要求。不得将未验证的多个模型组合视作覆盖。
- 在 Hugging Face 本地缓存及当前 workflow 运行记录中按候选名和常见权重扩展名查找，未发现可复用的候选权重；这不是对全机器的穷尽性搜索。

## 本轮网络和硬件检查

这些检查输出在执行会话中观察到；以下是记录，不是额外保存的原始网络日志。所有请求均为小量元数据或 HEAD 请求，没有下载权重。

- `nvidia-smi`：受限环境退出 9；经授权在服务器执行成功，显示 8 张 A100-SXM4-80GB，其中 GPU 0–3 空闲，4–7 各使用约 76 GB。这是当时的服务器状态，不是比赛配额。
- `ss -lntp | rg ':(7589|18999|12804)\b'`：经授权确认本机 7589 代理及 12804 模型服务监听。
- `curl --proxy http://172.28.4.16:18999 --connect-timeout 5 --max-time 8 -sS -o /dev/null -w 'unmetered HTTP %{http_code}\n' https://github.com`：授权执行退出 28，代理 CONNECT 超时；未使用该路线下载。
- `curl --proxy http://127.0.0.1:7589 --connect-timeout 5 --max-time 12 -sS -o /dev/null -w 'metered HTTP %{http_code}\n' https://github.com`：退出 28，TLS 超时。使用计费代理前已通知用户。
- `curl --proxy http://127.0.0.1:7589 --connect-timeout 6 --max-time 20 -sS -I -w '\nHTTP %{http_code}\n' 'https://drive.google.com/uc?export=download&id=1r0LXfGsO0_5xwg8z_qkTAFr8jrHx4bod'`：退出 35；先收到代理的 `HTTP/1.1 200 Connection established`，随后 TLS unexpected EOF，最终 HTTP 000。隧道响应不代表取得权重或目标服务器响应。此前另一轮报告称得到 HTTP 200 HTML，但缺少原始命令输出，无法独立核实，详见 `../t2-followup-20261108/REPORT.md`。
- `curl --proxy http://127.0.0.1:7589 --connect-timeout 5 --max-time 15 -sS -L -o /dev/null -w 'hf-mirror HTTP %{http_code}\n' https://hf-mirror.com/api/models/scu-zjz/ForensicHub`：退出 0，最终 HTTP 401；表明服务有响应，但不能证明此模型路径存在公开可下载的权重，也不能据此推断其他来源的可用性。

## 目标环境复核

在 `workflow` 目录使用服务器的 `codex exec`、本地 provider `http://127.0.0.1:12804/v1`、模型 `qwen3.8-27b-fp8` 进行只读复核，禁止该次验证自行联网、安装或下载：

```sh
set -o pipefail
codex exec --ephemeral --ignore-user-config --skip-git-repo-check -c 'model_provider="local"' -c 'model_providers.local.name="local"' -c 'model_providers.local.base_url="http://127.0.0.1:12804/v1"' -c 'model_providers.local.wire_api="responses"' -m qwen3.8-27b-fp8 -s workspace-write --json -o runs/t2-cont-20261108/final.txt '只执行 TICKET-2 的只读复核。先实际读取 .agents/skills/darwin-workflow/SKILL.md 和 .agents/skills/solution-discovery/SKILL.md，再读取 runs/t2-followup-20261108/REPORT.md 与 runs/t1-real-20261108/competition_spec.json，核查候选权重获取与许可、比赛资源限制及三分类证据。不得联网、下载、安装、修改文件或假设缺失证据；逐项说明哪些已验证、哪些尚未验证及是否解除阻塞。' | tee runs/t2-cont-20261108/events.jsonl
```

原始事件见 `events.jsonl`。读取两份 Skill 及既有报告和规格的命令均已完成并退出 0；该次复核是否完成及最终结果以事件末尾和 `final.txt` 为准。此前目标环境成功执行 Skill 读取的证据及其限制见 `../t2-followup-20261108/REPORT.md`。仅有只读复核不等于候选实测成功。

独立解析事件文件：共 72 条，末条为 `turn.completed`，有 1 条 `turn.completed`、0 条 `turn.failed`；最终结果见 `final.txt`。本次 shell 管道的进程退出码未记录，不以此声称退出码为 0。目标模型指出上一轮报告中的 dualnet HEAD 结果没有相应原始命令输出可供独立复核，因此该历史记录只能视为报告陈述；本轮上文的 TLS 失败是另一次检查。目标模型还将 FakeShield 的文件大小直接视为运行时驻留内存下限，这一推断未经证实：文件大小不能单独确定实际加载方式及显存占用，本报告不采纳该推断。它提出的三分类映射和资源实测是后续需要的证据，并非本轮已完成的验证。

## 解除阻塞所需证据

取得可验证下载且使用许可明确的候选权重，验证完整性和可加载性；获得或确认比赛 CPU/内存约束；在不超过比赛资源上限的条件下测量实际占用，并用具有可信类别标注的样本验证三分类映射与覆盖。不能以当前证据声明 TICKET-2 完成。
