#!/usr/bin/env python3
"""Inventory and scan every saved image layer without logging matched values."""
import collections
import hashlib
import json
import re
import subprocess
import sys
import tarfile
import tempfile

IMAGE = 'harbor-contest.4pd.io/liuyutong/darvin-t5:20261110'
PATTERNS = {
    'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----',
    'aws_access_key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'github_token': rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b',
    'credential_assignment': rb'''(?i)["']?(?:api[_-]?key|access[_-]?token|secret[_-]?key|password|passwd)["']?\s*[:=]\s*["'][^"'\s]{12,}["']''',
    'bearer_token': rb'(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{24,}',
}
compiled = {name: re.compile(pattern) for name, pattern in PATTERNS.items()}
suspect_path = re.compile(r'(?i)(?:^|/)(?:\.ssh|\.aws|\.docker|\.kube)(?:/|$)|(?:^|/)(?:\.env|credentials|id_rsa|id_ed25519)$|\.(?:pem|p12|pfx|key)$')
findings = collections.Counter()
examples = collections.defaultdict(set)
counts = collections.Counter()

def scan(data, where):
    for name, pattern in compiled.items():
        if pattern.search(data):
            findings[name] += 1
            if len(examples[name]) < 30:
                examples[name].add(where)

def command(args):
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return p.stdout

try:
    inspect = command(['docker', 'image', 'inspect', IMAGE])
    history = command(['docker', 'history', '--no-trunc', '--format', '{{json .}}', IMAGE])
    scan(inspect, 'docker image inspect')
    scan(history, 'docker history')
    with tempfile.TemporaryFile() as archive:
        p = subprocess.run(['docker', 'image', 'save', IMAGE], stdout=archive, stderr=subprocess.PIPE)
        if p.returncode:
            raise RuntimeError('docker image save failed, exit ' + str(p.returncode))
        archive.seek(0)
        with tarfile.open(fileobj=archive, mode='r:') as outer:
            manifest = json.load(outer.extractfile('manifest.json'))[0]
            config = outer.extractfile(manifest['Config']).read()
            scan(config, 'saved image config')
            for index, layer in enumerate(manifest['Layers']):
                with tarfile.open(fileobj=outer.extractfile(layer), mode='r:*') as inner:
                    counts['layers'] += 1
                    for member in inner:
                        counts['entries'] += 1
                        label = 'layer %d: %s' % (index + 1, member.name)
                        if suspect_path.search(member.name):
                            findings['sensitive_path'] += 1
                            if len(examples['sensitive_path']) < 100:
                                examples['sensitive_path'].add(label)
                        if not member.isfile():
                            continue
                        counts['regular_files'] += 1
                        counts['file_bytes'] += member.size
                        f = inner.extractfile(member)
                        tail = b''
                        while True:
                            chunk = f.read(1024 * 1024)
                            if not chunk:
                                break
                            scan(tail + chunk, label)
                            tail = chunk[-1024:]
    result = {'status': 'complete', 'image': IMAGE, 'scope': 'docker inspect, full history, saved config, every layer entry and regular-file raw bytes including deleted files', 'limitations': 'pattern-based; nested compressed content and semantic credential validity not established; candidate paths require review', 'counts': dict(counts), 'candidate_counts': dict(findings), 'candidate_locations': {k: sorted(v) for k, v in examples.items()}, 'inspect_sha256': hashlib.sha256(inspect).hexdigest(), 'history_sha256': hashlib.sha256(history).hexdigest()}
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as exc:
    print(json.dumps({'status': 'incomplete', 'error_type': type(exc).__name__, 'detail': str(exc)}, ensure_ascii=False))
    sys.exit(1)
