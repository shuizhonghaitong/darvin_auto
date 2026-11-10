#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T4 父进程 HTTP 实测客户端（stdlib only，经 FIFO 传输驱动真实服务子进程）。

客户端使用 http.client 生成/解析真实 HTTP/1.x 请求响应字节；
服务端为 server_session.py 子进程（真实模型 + sha256 固定校验）。
用例集与 tests/http_client_tests.py 相同:
  GET /ready; 6 张 T3 真实图片(JPG/PNG) 与 T3 本地预测比较;
  缺字段 / 空体 / 损坏 Base64 / 合法Base64非图片 / 非法JSON / 404。
全部符合期望退出 0，否则 1；结果写 --out JSON。
"""
import argparse
import base64
import http.client
import json
import os
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.path.dirname(HERE)


class FifoClientSocket(object):
    """http.client 的 socket 替身：sendall 写请求 FIFO，makefile('rb') 读响应 FIFO。"""

    def __init__(self, req_file, rsp_file):
        self._req = req_file
        self._rsp = rsp_file

    def sendall(self, data):
        self._req.write(data)
        self._req.flush()

    def makefile(self, mode, bufsize=None):
        assert "r" in mode and "w" not in mode, mode
        return self._rsp

    def settimeout(self, timeout):
        pass

    def close(self):
        pass


def _timeout(signum, frame):
    raise RuntimeError("HTTP 会话超时")


def call_session(session_idx, fifo_prefix, method, path, payload=None,
                 headers=None, timeout_s=60):
    req_path = "%s.req.%d" % (fifo_prefix, session_idx)
    rsp_path = "%s.rsp.%d" % (fifo_prefix, session_idx)
    signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(timeout_s)
    try:
        req_file = os.fdopen(os.open(req_path, os.O_RDWR), "wb")
        rsp_file = os.fdopen(os.open(rsp_path, os.O_RDONLY), "rb")
        conn = http.client.HTTPConnection("127.0.0.1", 8000)
        conn.sock = FifoClientSocket(req_file, rsp_file)
        hdrs = dict(headers or {})
        if payload is not None:
            hdrs.setdefault("Content-Type", "application/json")
        conn.request(method, path, body=payload, headers=hdrs)
        resp = conn.getresponse()
        body = resp.read()
        status = resp.status
        reason = resp.reason
        hdr_map = {k.lower(): v for k, v in resp.getheaders()}
    finally:
        signal.alarm(0)
        try:
            rsp_file.close()
        finally:
            req_file.close()
    return status, reason, hdr_map, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fifo-prefix", default="/tmp/t4srv")
    ap.add_argument("--server", default=os.path.join(HERE, "server_session.py"))
    ap.add_argument("--images", default=os.path.join(HERE, "test_images.txt"))
    ap.add_argument("--expect", default="/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t3-baseline-20261110/results/predictions.json")
    ap.add_argument("--python", default="/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    expect = {}
    with open(args.expect) as f:
        for item in json.load(f)["items"]:
            expect[item["input"]] = item["prediction"]

    with open(args.images) as f:
        image_paths = [ln.strip() for ln in f if ln.strip()]

    requests = [("GET", "/ready", None, None)]
    for path in image_paths:
        fmt = "png" if path.lower().endswith(".png") else "jpg"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        requests.append(("POST", "/api/v1/image-authenticity",
                         json.dumps({"image_base64": b64, "image_format": fmt}).encode("utf-8"),
                         path))
    error_cases = [
        ("缺字段: 无 image_base64", json.dumps({"image_format": "jpg"}).encode(), 400, "缺少必要参数: image_base64"),
        ("缺字段: 空对象 {}", b"{}", 400, "缺少必要参数: image_base64"),
        ("损坏 Base64", json.dumps({"image_base64": "!!!not@base64$$$", "image_format": "jpg"}).encode(),
         400, "图片 Base64 编码无效"),
        ("非图片输入(合法Base64纯文本)",
         json.dumps({"image_base64": base64.b64encode(b"hello world, definitely not an image " * 5).decode(),
                     "image_format": "jpg"}).encode(), 400, "图片解码失败"),
        ("非法 JSON", b"this is not json", 400, "请求体不是有效的 JSON"),
    ]
    for name, payload, _st, _frag in error_cases:
        requests.append(("POST", "/api/v1/image-authenticity", payload, name))
    requests.append(("GET", "/nope", None, None))

    n_sessions = len(requests)
    for i in range(n_sessions):
        for suffix in (".req.%d" % i, ".rsp.%d" % i):
            p = args.fifo_prefix + suffix
            if os.path.exists(p):
                os.unlink(p)
            os.mkfifo(p, 0o600)

    t_start = time.time()
    server = subprocess.Popen([args.python, args.server,
                               "--sessions", str(n_sessions),
                               "--fifo-prefix", args.fifo_prefix],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cases = []
    for i, (method, path, payload, ref) in enumerate(requests):
        t0 = time.time()
        try:
            status, reason, hdr_map, body = call_session(i, args.fifo_prefix, method, path, payload)
            err = None
        except Exception as e:
            status, reason, hdr_map, body, err = None, None, {}, b"", repr(e)
        ms = round((time.time() - t0) * 1000, 1)
        obj = None
        try:
            obj = json.loads(body.decode("utf-8"))
        except Exception:
            pass

        if ref is None and path == "/ready":
            ok = status == 200 and body == b"True"
            expected = "200 且 body == 'True'"
            name = "GET /ready"
        elif ref is None and path == "/nope":
            ok = status == 404 and obj is not None and obj.get("success") is False
            expected = "HTTP 404 success=false"
            name = "404: GET /nope"
        elif isinstance(ref, str) and ref in expect:
            exp_label = expect[ref]
            ok = (status == 200 and obj is not None and obj.get("success") is True
                  and obj.get("result") in ("1", "0_1", "0_2")
                  and obj.get("result") == exp_label)
            expected = "200 success=true result==T3 本地预测(%s)" % exp_label
            name = "image %d (%s)" % (i, os.path.basename(ref))
            extra = {"t3_local_prediction": exp_label, "service_result": obj.get("result") if obj else None}
        else:
            frag = [f for n, p, s, f in error_cases if n == ref][0]
            ok = (status == 400 and obj is not None and obj.get("success") is False
                  and obj.get("result") is None
                  and isinstance(obj.get("message"), str) and frag in obj["message"])
            expected = "HTTP 400 success=false 且 message 含「%s」" % frag
            name = ref
            extra = {}
        case = {"name": name, "method": method, "path": path,
                "http_status": status, "http_reason": reason,
                "content_type": hdr_map.get("content-type"),
                "body": body.decode("utf-8", "replace"), "ms": ms,
                "expected": expected, "pass": bool(ok), "error": err}
        if isinstance(ref, str) and ref in expect:
            case.update(extra)
        cases.append(case)
        print("%-4s %-34s http=%s  %s" % ("PASS" if ok else "FAIL", name,
                                          status, (body or b"")[:80].decode("utf-8", "replace").replace("\n", " ")))

    # 子进程应已处理完全部会话并退出
    try:
        out, errb = server.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        server.kill()
        out, errb = server.communicate()
        errb += b"\n[client] server timed out and was killed"
    server_out = out.decode("utf-8", "replace")
    server_err = errb.decode("utf-8", "replace")
    print("server exit code:", server.returncode)
    print("server stdout: %s" % server_out.strip())
    if server_err.strip():
        print("server stderr (tail): %s" % server_err.strip()[-2000:])

    n_pass = sum(1 for c in cases if c["pass"])
    result = {
        "transport": "FIFO (沙箱禁止 TCP socket/bind；HTTP 协议层由 http.client + main.Handler 真实执行)",
        "n_cases": len(cases), "n_pass": n_pass,
        "t3_expect_source": args.expect,
        "server_process": {"cmd": [args.python, args.server, "--sessions", str(n_sessions)],
                           "exit_code": server.returncode,
                           "stdout": server_out, "stderr_tail": server_err[-4000:]},
        "total_seconds": round(time.time() - t_start, 1),
        "cases": cases,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text + "\n")
    print("total=%d pass=%d fail=%d" % (len(cases), n_pass, len(cases) - n_pass))
    sys.exit(0 if n_pass == len(cases) and server.returncode == 0 else 1)


if __name__ == "__main__":
    main()
