# TICKET-2: resource and permission follow-up (2026-11-08)

## Scope and data permission

For this check only, 2 CPU cores and 4 GB RAM are assumptions supplied by the user. The competition introduction says `1/2 A100-40g显存，2c4g`; its precise meaning has not been independently confirmed. See `../t1-real-20261108/raw_doc1_bangdan_jieshao.md`.

The competition training-data document `../t1-real-20261108/raw_doc2_xunlianji.md` lists two training archives, named `训练集 1 0_1.zip` and `训练集 0_2.zip`. Their names and an older project record support the existence of data for the three labels, but have not been independently checked against the archive contents in this run. The available competition documents do not establish specific usage terms. The older project run record `/mnt/disk3/liuyutong_home/workspace/darwin_auto/reports/frontend_continuous_20261105/RUN_RECORD.md` explicitly says the data licence was unknown. Availability as a training attachment is not proof of unrestricted reuse or permission to publish derived weights. Seek the actual competition terms or written organizer clarification; do not assume the old dataset or fine-tuned checkpoint is licensed for reuse.

## Independent two-core base-model smoke test

The previously downloaded `timm/resnet18.a1_in1k` revision `491b427b45c94c7fb0e78b5474cc919aff584bbf` checkpoint at `/tmp/t2-resnet18-fw9Rkn/model.safetensors` had SHA-256 `80c49dee3da4822c009c5a7fe591e9223c5a2cfcf95a4067ca4dfb5a7b89c612`; model metadata identifies Apache-2.0. This licence statement is limited to that model, not competition data or the old trained checkpoint. The temporary checkpoint is not guaranteed to persist.

Actual command (the output was captured in `/tmp/t2-resource-smoke.log`):

```sh
/usr/bin/time -v taskset -c 0,1 env OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 /mnt/disk3/liuyutong_home/miniconda3/envs/qwen/bin/python -c 'import torch; from torchvision.models import resnet18; from safetensors.torch import load_file; torch.set_num_threads(2); m=resnet18(); w=load_file("/tmp/t2-resnet18-fw9Rkn/model.safetensors"); s=m.state_dict(); good={k:v for k,v in w.items() if k in s and v.shape==s[k].shape}; print("model_keys",len(s),"compatible",len(good),"weight_keys",len(w)); m.load_state_dict(good,strict=False); m.eval(); print("output_shape",tuple(m(torch.zeros(1,3,224,224)).shape))'
```

Exit status 0; 122/122 model and checkpoint keys matched in name and shape; output shape `(1, 1000)`; elapsed 2.70 s including process startup; maximum resident set size 830148 KiB. CPU affinity and thread limits were applied. This is one synthetic-input forward pass of the 1000-class base model: no 4 GB memory cap was enforced, and it does not establish three-class quality, training resource consumption, service overhead, or full competition compliance.

## Target Codex + Qwen run

The initial invocation used the default account instead of the local model provider and was rejected with a model-not-supported 400; its trace is `permission-resource-target-events.jsonl`. This was a configuration error, not proof of a network failure.

The subsequent invocation explicitly used local provider `http://127.0.0.1:12804/v1`, model `qwen3.8-27b-fp8`, `--ignore-user-config`, read-only sandbox, and a 180-second timeout. Trace: `permission-resource-local-events.jsonl`. It shows the agent reading `solution-discovery/SKILL.md`. The process timed out with status 124 and did not finish a final response; the trace also shows attempts to access the nonexistent path `/mnt/disk3/liuyutong_home/workspace/darvin_auto/image_auth_baseline` instead of the old project under `darwin_auto`. This is real target execution and skill loading, but not successful end-to-end target-environment acceptance. No global configuration or authentication was changed.

## Status

TICKET-2 remains incomplete. Independent three-class data verification, applicable data and derivative-artifact terms, and a completed target-agent run with independently checked outputs are still needed. The smoke test alone does not establish a viable complete competition solution.
# 后续目标环境定向复测

- 使用本机 local provider（`http://127.0.0.1:12804/v1`）、`qwen3.8-27b-fp8`、只读沙盒和 120 秒超时，命令退出状态为 0。调用显式要求读取 `solution-discovery/SKILL.md` 和本记录，并提供了旧工程的正确路径；事件见 `target-focused-events.jsonl`，完整答复见 `target-focused-final.txt`。
- 轨迹显示目标 Agent 读取技能及本记录。它区分了基座权重许可与数据、派生权重许可，指出两核下单次前向不证明训练或完整工作负载符合 4 GB 限制，并判断 TICKET-2 未完成。
- 这是在已提供证据和路径条件下的定向判断，不是独立搜索或端到端候选发现；Agent 本次未独立检查原始比赛文档、数据包及旧工程目录。其答复中提及的“目标 agent 运行未成功”指此前 180 秒超时的调用，不适用于这次已正常结束的定向复测。

## 用户授权与独立发现复测（2026-11-08）

- 用户确认“图像鉴定-训练集”附件可用于本次比赛训练；该确认更新上述数据使用条件的判断，但不构成对附件再分发、其他比赛用途或第三方权重许可的确认。两份压缩包的实际内容和三类样本覆盖仍未核验。
- `solution-discovery/SKILL.md` 已调整为先自主构思，必要时针对性查找参考；仍须核实复现入口、许可、数据覆盖及资源，不能将尚未实现的构想当成可复现方案。执行 `python /mnt/disk3/liuyutong_home/.codex/skills/.system/skill-creator/scripts/quick_validate.py workflow/.agents/skills/solution-discovery`，退出 0，输出 `Skill is valid!`。
- 首次独立测试误用了只读沙盒，技能要求输出文件，不能用于验收。第二次在全新空目录 `/tmp/t2-independent-clean-gNdawRdR` 使用 `codex exec --ephemeral --ignore-user-config --skip-git-repo-check`，指定 local provider `http://127.0.0.1:12804/v1`、模型 `qwen3.8-27b-fp8` 和 `-s workspace-write --json`；只给出比赛描述、用户授权、资源假设和技能入口，不提供旧候选或旧工程路径。首次启动因文件系统只读失败，按权限流程重试后进入目标模型执行。
- 重试轨迹见 `independent-clean-20261108-events.jsonl`：目标 Agent 读取了技能，进行了网络探测，也读取了系统网络配置；记录的命令未显示读取旧候选文件，但不满足提示中“除技能外不读任何已有本地文件”的字面限制。运行停滞后人工中断，进程退出 1；没有完成事件，也没有生成候选或证据文件。该次不能证明独立发现通过，也不足以证明目标模型无法完成任务。资源仍是两核 CPU、4 GB 内存的用户指定假设，并非已确认的官方解释。
- 当前状态：TICKET-2 部分完成，独立发现及其输出验收仍阻塞；未核实附件内容、完整三分类训练或目标资源约束下的端到端表现。

