#!/usr/bin/env python3
"""Build a disclosure-limited, independently verifiable experiment archive."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = Path(__file__).resolve().parent
files = [
    "launch.sh", "continuation-launch.sh", "input.md", "continuation-input.md",
    "exit-code.txt", "continuation-exit-code.txt", "t2-planning/solution_plan.json",
    "continuation/06-submit.json", "continuation/07-receipt.json",
    "continuation/12-status-check-1.json", "continuation/13-solution-list-final.json",
    "continuation/14-task-list-completed.json",
]
manifest = {}
for name in files:
    data = (root / name).read_bytes()
    target = out / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    manifest[name] = {"source_sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}

# Arbitrary model/tool text can include credentials; keep its hash and length,
# not the text. Event types, status, identifiers, counters and timing survive.
opaque = {"text", "command", "aggregated_output", "arguments", "result", "error", "message"}
def clean(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key in opaque and item is not None:
                raw = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
                result[key] = {"redacted": True, "sha256_json": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
            else:
                result[key] = clean(item)
        return result
    if isinstance(value, list):
        return [clean(item) for item in value]
    return value

for name in ("events.jsonl", "continuation-events.jsonl"):
    source = root / name
    raw = source.read_bytes()
    lines = raw.splitlines()
    target = out / name
    with target.open("w", encoding="utf-8") as stream:
        for line in lines:
            stream.write(json.dumps(clean(json.loads(line)), ensure_ascii=False, separators=(",", ":")) + "\n")
    manifest[name] = {"source_sha256": hashlib.sha256(raw).hexdigest(), "source_bytes": len(raw),
                      "events": len(lines), "archived_sha256": hashlib.sha256(target.read_bytes()).hexdigest()}

(out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
