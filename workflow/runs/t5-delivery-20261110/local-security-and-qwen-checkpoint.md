# T5 local security and target-runtime checkpoint

- Build context inspected: `.dockerignore`, `Dockerfile`, `main.py`, `model_weights.npz`, `requirements.txt`, `serve_model.py`, `start.sh`, and `weights.sha256`. The Dockerfile copies only the listed application files and cached NumPy/Pillow packages into the final image.
- Image `darvin-t5-local:20261110`, ID `sha256:57004ba692901e804d8861ec18be2b7d045f114a8123175d09b0a885c3fa050e`: `/app` and image history were inspected; the application directory contained expected application files and Python bytecode caches.
- `docker run --rm --entrypoint sh darvin-t5-local:20261110 -c 'find / -xdev \( -name .git -o -name .aws -o -name .ssh -o -name .env -o -name id_rsa -o -name credentials -o -name config.json -o -name "*.key" \) -print 2>/dev/null'` exited 0 and printed no matches. This is a filename-based check, not a comprehensive secret scan. An earlier broader check also found public CA certificate `.pem` files.
- `docker image inspect darvin-t5-local:20261110 --format '{{range .Config.Env}}{{println .}}{{end}}' | cut -d= -f1` printed only `PATH`, `LANG`, `GPG_KEY`, `PYTHON_VERSION`, `PYTHON_SHA256`. Values were not recorded. `GPG_KEY` is a base-image environment variable name; this check alone does not establish its value or secret status.
- Target-runtime attempt with default provider failed because the selected model was unavailable to that account; see `events-qwen-authorized.jsonl` and `exit-qwen-authorized.txt`.
- A subsequent invocation selected the existing `newapi` provider only for that command, model `qwen3.8-27b-fp8`, with a 180-second bound and a read-only task. It exited 1: the provider returned HTTP 503, reporting no available channel for that model. See `events-qwen-newapi.jsonl`, `stderr-qwen-newapi.log`, and `exit-qwen-newapi.txt`. The request reached the provider; this is not evidence of successful Qwen execution or skill/tool use.
- No push or pull has been attempted. The user's gate requires successful target-runtime verification before pushing `harbor-contest.4pd.io/liuyutong/darvin-t5:20261110`.

## Subsequent progress

The preceding no-push statement records the state at that earlier checkpoint. Subsequently, the local Qwen model completed the bounded real HTTP test with Skill/tool trace and 15/15 results. The authorized image was pushed and pulled successfully on this host; the pull reused local cache. See `ImageManifest.md` and the push/pull logs. Docker-stage autonomous handoff and comprehensive per-layer credential inspection remain unverified.
