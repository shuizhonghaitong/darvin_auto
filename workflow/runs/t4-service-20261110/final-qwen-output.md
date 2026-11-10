

Bounded T4 finishing verification complete. Report written to `runs/t4-service-20261110/final-qwen-verification.md`; all prior evidence preserved (only that one file added).

**What I did**
- Read the `darwin-workflow` skill (T3→T4 handoff clause), `ServiceContract.md`, full `main.py`/`serve_model.py`, `start.sh`, and `run_report.md`.
- Verified the weight checksum two ways: `sha256sum -c weights.sha256` → `model_weights.npz: OK` (`132efbd9…2933bd`), and `main.load_model()` re-hashed it successfully at load.
- Inspected the existing independent HTTP evidence: `logs/final-http-results.json` / `final-test.log` (port 19389) = **13/13 pass** with actual response bodies; 6 real T3 images returned `0_1, 1, 0_1, 1, 0_2, 0_2`, matching `runs/t3-baseline-20261110/results/predictions.json` field-by-field; error cases returned proper 400s, no fabricated success. An earlier round (port 19387) also recorded 13/13.
- Ran a new bounded real inference (no socket): `serve_model.ImageAuthModel` on the 6 samples with the `evo` env (Python 3.10.21, numpy 1.26.4, Pillow 12.2.0) → **6/6 match T3**, probabilities agree to 4 decimals, 48–88 ms/image.

**Limitation**
- HTTP sockets are prohibited in this sandbox (`PermissionError: [Errno 1]` at `socket.socket`, after successful in-process model load). No new HTTP run was performed or claimed; HTTP acceptance rests on the pre-existing independent record.

**T5 handoff judgment**
- Supported: ServiceArtifact + contract + checksum-gated weights + real interface evidence are all present and mutually consistent. Carry-ins for T5: conflict C1 (bad-request semantics) deferred to submission, platform bind `0.0.0.0:80` not locally exercised, and the pre-existing caveat that the earlier test harness exit status wasn't captured.