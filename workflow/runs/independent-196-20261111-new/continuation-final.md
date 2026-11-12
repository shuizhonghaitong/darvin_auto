

All done — submission executed exactly once, evaluation completed on the platform, first-invocation artifacts verified untouched.

**Pre-submission reconcile (read-only)**
- Refreshed login confirmed: `auth inspect` → authenticated, `solution.submit` eligible (the 401 from the first run is gone); CLI state copied to `HOME=/tmp/darvin-home` with verified fingerprint so all writes were deterministic.
- No prior submission: `solution list` (config + subnet scope) and `task list` all empty, matching `t6-submission/approval-wait.log` (WAIT_EXPIRED, never submitted).
- Image identity: registry-only `manifest inspect`/`imagetools inspect` — tag `…:20261111-independent-new` resolves to exactly `sha256:2d2793db…5487ff8`.

**Submission (single, authorized)**
- `darvin solution submit --config solution.yaml --yes --json` at 00:55:19Z → success in 7.3s, `stage=job_created`, no warnings/errors.
- IDs: `submission_id=422`, `model_app_id=14473`, `task_id=a02708ad1ecd608f0949ef1803a209ee`, `job=f6bdcb4df1d7253cece08f5e84c15037`, trace `v1:3931…fc65`. Receipt copied to `continuation/07-receipt.json`.

**Evaluation result (platform judge, confirmed)**
- Task **success**, job **SUCCEEDED**, score **42.21** (raw 42.21 = f1_0×100).
- Inference **120/120 succeeded, 0 failures** (fail_rate 0 — no invalidation); accuracy=0.4500, f1_1=0.5135, f1_0_1=0.4138, f1_0_2=0.4304, f1_0=0.4221; avg 22.1s/image on platform 2c4g; 66 bad cases.
- Tracked via 50 bounded status polls + 5 read-only log snapshots (one transient SSL EOF on a read query self-recovered; no impact).
- Note, unspun: platform f1_0 (0.4221) is well below the local val estimate (0.8056, different split) — the fixed platform test set is the authoritative result.

**Artifacts**
- Everything in `continuation/`: `CONTINUATION_LOG.md` (narrative + file inventory), `01`–`15` numbered command outputs, `poll-summary.log`, `poll.sh`/`poll2.sh`, `logs-eval*/` platform logs. First-invocation files retain original timestamps; the CLI only *added* `t6-submission/.darvin/` (receipt) and `.gitignore`.

**Three-way status**: agent run — complete; platform acceptance — confirmed; evaluation completion — confirmed. Remaining 170 points (not independently re-queried; a read-only `darvin scientist points` can confirm if you want). No further action needed unless you'd like me to pull the detailed bad-case analysis from the judge output.