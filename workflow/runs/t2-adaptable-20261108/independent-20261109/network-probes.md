# Network checks, 2026-11-09

Checks were run outside the restricted execution environment after the initial
restricted checks could not read listener status or connect. No credentials were
printed. These are endpoint-specific observations, not a claim that an entire
proxy is universally unavailable.

- `ss -ltn` showed listeners on `:12804` (local model service) and `:7589`
  (the configured metered proxy).
- A HEAD request to `https://huggingface.co` explicitly through
  `http://172.28.4.16:18999`, with `--noproxy ''`, a 4-second connect timeout
  and an 8-second total timeout, returned curl exit 28: `Proxy CONNECT aborted
  due to timeout`, `HTTP 000`, remote `172.28.4.16`.
- The equivalent HEAD request explicitly through `http://127.0.0.1:7589`
  returned HTTP 200, curl exit 0. This was a small connectivity check on the
  metered route, announced to the user beforehand.

The target run was then supplied both routes and their cost distinction; it was
instructed to prefer the unmetered route, record actual checks, avoid unnecessary
downloads and ask before downloading any individual file larger than 20 MB.
