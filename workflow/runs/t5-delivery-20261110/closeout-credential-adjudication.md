# T5 closeout: credential findings and clean environment — 2026-11-10

Scope: inspect the existing local image `harbor-contest.4pd.io/liuyutong/darvin-t5:20261110`, without rebuilding, pushing, or entering T6. `docker image inspect` returned local image ID `sha256:57004ba692901e804d8861ec18be2b7d045f114a8123175d09b0a885c3fa050e` (exit 0); this is not a registry manifest digest. Existing scan and handoff evidence remains in `closeout-review.md` and the files referenced there.

## Finding adjudication

- The `urllib/request.py` credential-assignment match is a documentation example describing hypothetical HTTP Basic Authentication, not an identified operational credential. This adjudicates the specific match, not all possible credentials in the image.
- The layer-1 GnuTLS library contains ten complete PEM-formatted private-key blocks: three `PRIVATE KEY`, five `EC PRIVATE KEY`, one `DSA PRIVATE KEY`, and one `RSA PRIVATE KEY`. A read-only, network-disabled disposable container inspection exited 0; `openssl pkey -noout` accepted three blocks. Non-acceptance of the other seven does not establish that they are invalid. No key contents were recorded. The library SHA-256 is `779b25d20249988bea2c1aa6bbeb218f5ae7ea8a9d30ce4f54ea37372965cc4b`; its image package reports `libgnutls30 3.7.9-2+deb12u7`, source `gnutls28`.
- The keys' provenance, intended use, and sensitivity remain unverified. Their presence in a system library alone does not prove they are harmless test keys or compromised production credentials. Treat this finding as unresolved for release; independently compare the exact library/package with a trusted source and establish the keys' purpose before closing it. The host lacks the matching library and cached package, so this comparison was not made locally. The earlier pattern-based layer scan also does not establish absence of other secrets, including inside nested archives.

## Independent clean Docker environment

- `docker context ls` exited 0 and listed only the default context at `unix:///var/run/docker.sock`; the user's `/run/user/1007/docker.sock` was absent. The previous pull used the existing daemon's cache and is not a clean pull.
- `unshare -Ur true` exited 0 and `/etc/subuid` and `/etc/subgid` contain subordinate ID allocations for the current user. However, checks for `newuidmap`, `newgidmap`, `slirp4netns`, `vpnkit`, and `fuse-overlayfs` found none on PATH; Podman was also absent. A check of their usual `/usr/bin` paths found the mapping helpers, slirp4netns and fuse-overlayfs absent. This does not prove all alternative isolation approaches impossible, but does not establish a usable, safely isolated rootless Docker setup here.
- No new daemon was started, no packages installed, and the existing Docker service was not changed. An independent clean environment is therefore not currently provided or verified; clean pull, digest comparison and runtime checks remain outstanding. Provision a separate clean host or otherwise independently administered Docker daemon, then perform those checks under the existing T5 acceptance requirements.

## Status

T5 remains **部分通**: the private-key finding and clean-environment verification remain unresolved; the previously recorded Qwen handoff timed out and was not rerun. C1/C2 are not closed. No image rebuild or push was performed and T6 was not started.
