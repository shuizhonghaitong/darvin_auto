# T5 closeout review — 2026-11-10

**Historical checkpoint:** Subsequent Debian source verification, remote manifest inspection, and the user's decision to defer the independent clean pull are recorded in [closeout-minimal-20261110.md](closeout-minimal-20261110.md). The Qwen attempt recorded below remains not passed.

Target: `harbor-contest.4pd.io/liuyutong/darvin-t5:20261110`; local image ID `sha256:57004ba692901e804d8861ec18be2b7d045f114a8123175d09b0a885c3fa050e`. The local image ID and registry manifest digest are distinct identifier types; see the updated evidence for their independently observed values.

## Image security review: incomplete

The existing `closeout-layer-audit.py` was run against the image and exited 0; its retained output is `closeout-layer-audit-result.json`. It inspects image configuration and history and scans the exported image layers, including files deleted by later layers. It reported 12 layers, 9,323 entries and 7,402 regular files (224,872,026 bytes); content-rule counts were one private-key marker and one credential-assignment candidate, and 152 path candidates. These are rule matches, not confirmed credential counts.

The private-key match is in `usr/lib/x86_64-linux-gnu/libgnutls.so.30.34.3` in layer 1. Offline inspection of the image file identified ten complete PEM-formatted private-key blocks embedded in that library. Their purpose and sensitivity have not been independently established; this finding cannot be dismissed or presented as a clean audit. The credential-assignment rule matched `usr/local/lib/python3.11/urllib/request.py` in layer 3; its context has not been conclusively adjudicated. No secret values are reproduced here.

The original output caps path examples at 100. A read-only rerun of the same scanner with that cap raised, using `python3 -c` to load the existing script and alter only the reporting limit and output, exited 0. All 152 reported path hits were under `etc/ssl/certs/` except `usr/lib/ssl/cert.pem` and `usr/local/lib/python3.11/site-packages/pip/_vendor/certifi/cacert.pem`. Names alone do not verify every file's contents. The scan is pattern-based, may miss credentials or irrelevant sensitive data, and does not recursively unpack embedded archives; it is not proof of absence. Image configuration and history were also checked by the existing scan; see the retained result and `local-security-and-qwen-checkpoint.md` for the observed configuration names and prior context/history review.

## Independent clean pull: blocked

`docker info` succeeded with authorized access to the existing Docker service. `docker context ls` showed only the default context, and `command -v podman` found no Podman. No independent clean Docker environment was available. The earlier pull reused local cache and is not evidence of a clean pull. Consequently, a clean-environment digest comparison, 2 CPU / 4 GiB execution, `/ready`, and real-image request were not performed. The existing daemon was not disrupted and no new daemon was installed.

## Local Qwen handoff: not passed

One bounded run used server `codex exec` with local provider `http://127.0.0.1:12804/v1`, model `qwen3.8-27b-fp8`, workspace-write sandbox, and `timeout 180s`. The exact task prompt is retained in `closeout-qwen-handoff-prompt.md`; event and stderr logs are `closeout-qwen-events.jsonl` and `closeout-qwen-stderr.log`. It exited 124 (timeout). The event log shows that the agent read the T4 contract and existing T5 manifest and attempted Docker CLI inspection; its requested `ImageManifest-qwen-handoff.md` was not created. Therefore the autonomous handoff and independent verification of a newly produced manifest did not pass. This is not evidence that the previous build, push or HTTP checks failed.

## Decision

T5 remains **部分通**, not Done: security findings require adjudication, the independent clean pull is blocked, and the bounded Qwen handoff did not complete. C1/C2 remain unresolved. Do not start T6 on the basis of this closeout. The formal image was not rebuilt or pushed, and the formal T5 run was not repeated.
