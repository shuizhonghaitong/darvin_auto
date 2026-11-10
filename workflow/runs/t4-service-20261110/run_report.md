# T4 service run: independent verification and limitations

T3 MVP acceptance was confirmed externally; the T3 model was not retrained.
This directory is the T4 ServiceArtifact. `ServiceContract.md` describes the
interface. The implementation reuses the existing NumPy inference path and
the T3 model, with a Python standard-library HTTP server and NumPy/Pillow.

## Model and startup

`model_weights.npz` is a local copy of the existing starting-kit weights,
excluded from Git. `weights.sha256` fixes its SHA-256 to
`132efbd9a7397bbb497df48349114adce6da370d0440db4b897ba470ee2933bd`;
`start.sh` checks it before starting. A checkout without this local file must
restore an identical copy before startup. The verified environment was Python
in the existing `evo` environment, NumPy 1.26.4 and Pillow 12.2.0; see
`requirements.txt`. No dependency was installed for this run.

From this directory, the independently tested startup was:

```sh
PYTHON=/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python ./start.sh --host 127.0.0.1 --port 19389
/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python tests/http_client_tests.py --base http://127.0.0.1:19389 --out logs/final-http-results.json
```

The default startup binds `0.0.0.0:8000`; `PYTHON` can select an environment
with the required dependencies. The system default Python lacked Pillow, and
the first attempted port 18080 was already occupied; see
`logs/independent-server.log`. Startup and checksum evidence is in
`logs/final-server.log` and detailed HTTP responses in
`logs/final-http-results.json` and `logs/final-test.log`.

The independent test recorded `total=13 pass=13 fail=0`. Six real T3 JPG/PNG
samples returned, in test order, `0_1`, `1`, `0_1`, `1`, `0_2`, `0_2`,
matching the saved T3 predictions. `/ready` passed. Missing input, invalid
Base64, non-image bytes and invalid JSON returned errors instead of fabricated
success. The test command's process exit status was not captured reliably by
the execution interface; the retained test output establishes the individual
assertion results, not an independently recorded exit status.

## Target-agent evidence and remaining gap

The actual server `codex exec` run used model `qwen3.8-27b-fp8` and read the
workflow Skill; tool calls and implementation activity are preserved in
`events-qwen.jsonl`, with diagnostics in `stderr-qwen.log`. It timed out
after 900 seconds (exit 124, `exit-status.txt`), before completing its own
verification. Independent HTTP checks therefore do not establish a completed
target-agent run. The T4 MVP cannot yet be marked fully accepted under the
project's target-environment requirement, and a completed bounded Qwen run
plus its independent verification remains necessary before formal T5 handoff.
The full T1–T4 workflow has not been verified end-to-end. No Docker build,
image push, Darwin submission, training or accuracy optimization was performed.
