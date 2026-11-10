# T5 ImageManifest

- Image: `harbor-contest.4pd.io/liuyutong/darvin-t5:20261110`
- Registry manifest digest: `sha256:57004ba692901e804d8861ec18be2b7d045f114a8123175d09b0a885c3fa050e`
- Local image: `darvin-t5-local:20261110`; inspected image ID has the same SHA-256 value. Platform: `linux/amd64`. Image size: 78,485,812 bytes.
- Model weights SHA-256: `132efbd9a7397bbb497df48349114adce6da370d0440db4b897ba470ee2933bd`.
- Build evidence: `build.log`, `context/Dockerfile`; offline build used locally cached Python 3.11 and NumPy/Pillow. The original build command and exit status were not separately captured; successful build and image identification are evidenced by the build log and subsequent inspection and runs.
- Container validation: `http-results.json`, `http-retest.json`: each 15/15; six real-image predictions matched T3. Service was tested with 2 CPUs and 4 GiB memory, bound to localhost port 32784. The complete original run command and its exit status were not separately captured.
- Target runtime: local `qwen3.8-27b-fp8` via `http://127.0.0.1:12804/v1`; `events-qwen-live-authorized.jsonl`, `exit-qwen-live-authorized.txt`, `http-qwen-live.json`: Qwen used the Skill and tools for real HTTP tests, 15/15. It did not autonomously perform the Docker build or image-stage handoff. Earlier failed attempts are retained in the adjacent logs. An earlier failed HTTP JSON was overwritten by a later run; its execution trace remains.
- Push: `docker push harbor-contest.4pd.io/liuyutong/darvin-t5:20261110`, exit 0; `docker-push.log`, `docker-push.exit`. The registry reported the digest above.
- Pull: `docker pull harbor-contest.4pd.io/liuyutong/darvin-t5:20261110`, exit 0; `docker-pull.log`, `docker-pull.exit`. It used the local cache; a clean-environment pull and competition-platform access remain unverified.
- Security: context, image history, application directory and selected credential-like filenames were inspected; see `local-security-and-qwen-checkpoint.md`. This is not a comprehensive content scan or examination of every image layer. Full image-layer credential verification remains open.
- No Darwin submission was attempted. C1 evaluation-failure and C2 submission-form rule conflicts remain unresolved.
