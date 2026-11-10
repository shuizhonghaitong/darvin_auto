# T4 bounded finishing verification (target Codex + Qwen agent, 2026-11-10)

Scope: verify the existing T4 service in this directory only. No training, no
implementation changes, no dependency installs, no Docker, no submission, no
rerun of T1–T3. All pre-existing evidence files were preserved untouched; this
file is the only artifact added by this run. Helper scripts lived in
`/tmp/t4-verify/` (outside the run directory). All commands were finite, with
explicit `timeout` wrappers.

## 1. Artifacts inspected

- `ServiceContract.md` — endpoints (`GET /ready`, `POST /api/v1/image-authenticity`),
  request/response shapes, 400 error table, label space `1`/`0_1`/`0_2`, fixed
  weight sha256, config via `--host/--port` or `MOCK_SERVER_*` env, stdlib-only
  HTTP layer + numpy/Pillow inference.
- `main.py` (read in full) — stdlib `ThreadingHTTPServer`; startup sha256 gate
  (`verify_weights_sha256`, exit 1 on mismatch); 400 + `success:false` for
  missing field / bad base64 / empty / non-image / invalid JSON; 404 JSON for
  unknown paths; `/ready` returns exactly `True`; no fabricated success paths.
- `serve_model.py` — numpy reimplementation of the T3 CNN
  (4× Conv3x3+BN+ReLU+MaxPool, 3→32→64→128→256, GAP, Linear(256,3)),
  160×160, `(x-0.5)/0.5` normalization.
- `start.sh`, `requirements.txt` (`numpy>=1.24`, `Pillow>=9.0`), `weights.sha256`.
- `run_report.md` — prior context: independent HTTP run 13/13; first port
  18080 attempt hit `Address already in use` (see `logs/independent-server.log`);
  previous target-agent run timed out at 900 s (`exit-status.txt` = 124) before
  finishing its own verification.
- Stage handoff basis: `.agents/skills/darwin-workflow/SKILL.md` (T3→T4 service
  adaptation handoff clause: reuse verified T3 implementation, produce
  ServiceArtifact + ServiceContract + startup notes + real interface evidence
  for T5, no T1–T3 rerun / image build / submission).

## 2. Weight checksum verification (new, this run)

Command (finite, `timeout 30`):

    sha256sum -c weights.sha256        # -> model_weights.npz: OK, rc=0
    sha256sum model_weights.npz        # -> 132efbd9a7397bbb497df48349114adce6da370d0440db4b897ba470ee2933bd

The actual digest equals the value fixed in `weights.sha256` and cited in
`ServiceContract.md` §2. A second independent confirmation came from
`main.load_model()` during the loopback attempt below, which re-hashed the file
at load time and printed
`[model] loaded .../model_weights.npz sha256=132efbd9...2933bd` (rc path
successful; the process then failed only at socket creation, see §5).

## 3. Existing independent HTTP evidence inspected (not rerun)

`logs/final-http-results.json` + `logs/final-test.log` (server on
`127.0.0.1:19389`, started via `start.sh` per `logs/final-server.log`,
2026-11-10 12:17): **total=13 pass=13 fail=0**, with actual recorded response
bodies:

- `GET /ready` → 200, body exactly `True`.
- 6 real T3 samples → 200, `success:true`, `message:"鉴定完成"`, results in test
  order `0_1, 1, 0_1, 1, 0_2, 0_2`; each equals the corresponding entry in
  `runs/t3-baseline-20261110/results/predictions.json` (verified field by
  field against that file, which lists per-image `prediction` values).
- Missing `image_base64`, empty `{}`, corrupted Base64, non-image bytes (valid
  Base64 text), invalid JSON → all 400 with `success:false`, `result:null` and
  the contract-specified messages; no fixed-class fallback.
- `GET /nope` → 404 JSON.

An earlier independent round (`logs/http-results.json`, port 19387) also
recorded 13/13 pass with the same case set. Known caveat (from `run_report.md`):
the test harness process exit status was not captured by the execution
interface in that round; the per-case assertion results are retained in the
logs above.

## 4. Bounded real inference (new, this run — non-HTTP)

Using only existing files and the preinstalled `evo` environment
(Python 3.10.21, numpy 1.26.4, Pillow 12.2.0 — versions match `run_report.md`):

    timeout 120 evo/bin/python /tmp/t4-verify/direct_infer.py   # rc=0

Loads `model_weights.npz` via the untouched `serve_model.ImageAuthModel` and
predicts the 6 `samples.txt` images directly:

    00a81fa0095f459f983c90bb0774b10d.jpg  direct=0_1  t3=0_1  probs=[0.1256, 0.5511, 0.3233]
    0025d7f16dca46749dd4e5eff21439b7.jpg  direct=1    t3=1    probs=[0.8543, 0.0490, 0.0967]
    00e6b1e3a4af4c29bcb884002d0d0b34.png  direct=0_1  t3=0_1  probs=[0.2469, 0.6746, 0.0785]
    002edfff50e84f6fa9b0f634bedcacef.jpg  direct=1    t3=1    probs=[0.5745, 0.3580, 0.0675]
    002b3da4bcf14e67b9067dc22d24e10e.jpg  direct=0_2  t3=0_2  probs=[0.2113, 0.0991, 0.6897]
    00b5cdd2cd694ac6bddd240ebf7b534b.jpg  direct=0_2  t3=0_2  probs=[0.2168, 0.1630, 0.6202]

**6/6 MATCH T3**; probabilities agree with T3's torch-run values to 4 decimal
places, consistent with T3's recorded numpy/torch cross-check
(max|Δlogit|=3.6e-07). Latency 48–88 ms per 160×160 image (CPU).

## 5. HTTP socket attempt in this environment (failed — documented)

Attempted a single finite, in-process loopback test
(`/tmp/t4-verify/loopback_http.py`, `timeout 180`) that imports the real
`main.Handler`, loads the model (sha256 verified OK at load) and serves on
`127.0.0.1:0`. Socket creation was denied by the sandbox:

    PermissionError: [Errno 1] Operation not permitted   (socket.socket(...))

**HTTP sockets are prohibited in this environment.** No new HTTP run was
performed or claimed; the HTTP-layer acceptance evidence is the pre-existing
independent record from §3. Model loading, weight checksum, and inference code
paths were still exercised successfully in-process before the socket failure.

## 6. Limitations

- New verification evidence is non-HTTP (direct inference) + checksum; the
  HTTP behavior evidence remains the independent 12:17 run (13/13), which this
  agent inspected but did not reproduce (sockets blocked).
- The earlier independent test harness's process exit status was never
  captured (pre-existing caveat); per-case results are recorded.
- The previous target-agent run ended by 900 s timeout (`exit-status.txt`=124);
  it completed implementation + independent checks but not its own verification
  pass. This bounded run completes the verification step; it is not a claim
  that the full T1–T4 workflow was validated end-to-end.
- Contract conflict C1 (error-response semantics for bad requests, 400 +
  `success:false`) remains deferred to the submission stage, unchanged.
- No performance/accuracy optimization, no Docker build, no submission, no
  T1–T3 rerun, no dependency installs, no file changes in this run directory
  except this report.

## 7. Conclusion: T5 handoff support

**The existing artifacts support T4 → T5 handoff.**

- ServiceArtifact present: `main.py`, `serve_model.py`, `start.sh`,
  `requirements.txt`, fixed `model_weights.npz` + `weights.sha256`
  (checksum re-verified OK by two independent methods in this run).
- ServiceContract present and consistent with the implementation as read.
- Real interface evidence exists: two independent HTTP rounds, each 13/13,
  with actual recorded responses; real-image results match the verified T3
  model, and this run additionally reproduced 6/6 predictions directly from
  the exact same weight file.
- Startup is self-contained (no old-project path dependency), weight-gated,
  and host/port configurable per contract.

Conditions to carry into T5: resolve C1 per the conflict ruling at submission
time; platform deployment binds `0.0.0.0:80` via `MOCK_SERVER_PORT=80` (not
exercised locally); and the HTTP acceptance evidence is the pre-existing
independent record, since this verification environment blocks new HTTP
sockets.
