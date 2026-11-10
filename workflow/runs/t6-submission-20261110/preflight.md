# T6 read-only preflight — 2026-11-10

- Live `darvin subnet inspect 196 --json` exited 0: backend ID 196, internal subnet ID 85, 图像真伪鉴定榜, contract `0x35fC3c317F81D4a35fD764128FdF8023C96Fc2Eb`, ACTIVE / IN_PROGRESS, DockerImage submission.
- The current platform description requires `inferenceImage.repository` and `inferenceImage.tag` and valid predictions for every sample. The previously documented C1 failure-rule conflict remains unresolved.
- `solution.yaml` and `values.yaml` specify the requested inference image. The CLI also requires a training image; the configuration retains the separately pinned image from the existing submission configuration. Its current platform compatibility has not been independently verified. `auto_create_task` is enabled.
- Online `darvin solution precheck --config workflow/runs/t6-submission-20261110/solution.yaml --json` reported zero blocking checks, but warned that login has expired and that permissions and image pulling are confirmed later. This is not proof of submission permission or platform image access.
- `darvin auth inspect --json` exited 1 with `AUTH_REQUIRED` / Scientist API unauthorized. Authentication must be renewed before submission.
- The Harbor `/v2/` endpoint returned HTTP 401 through the designated unmetered proxy: reachable, but anonymous access was denied. Whether Darwin can pull using platform credentials is unverified.
- A real `codex exec` attempt used `qwen3.8-27b-fp8` and produced Darwin CLI precheck tool-call events in `qwen-precheck-events.jsonl`. It did not complete a successful target-environment precheck; the attempt used an incorrect working directory for the new configuration. The earlier sandboxed attempt failed to initialize with a read-only filesystem error.
- No submission was made; no SubmissionReceipt or platform pull/evaluation status exists for this T6 attempt. Explicit authorization for this particular submission and renewed authentication are required before proceeding.
