#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T4 HTTP 实测客户端（stdlib only）。

对运行中的服务执行:
  1) GET /ready
  2) POST 真实图片（JPG/PNG，来自 tests/test_images.txt）并比较 T3 本地预测
     （runs/t3-baseline-20261110/results/predictions.json 的 prediction 字段）
  3) 错误用例: 缺字段 / 空体 / 损坏 Base64 / 合法 Base64 非图片 / 非法 JSON / 404
每个用例记录 HTTP 状态码、响应体、耗时；全部符合期望退出 0，否则 1。
结果写入 --out JSON。
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request


def call(base, method, path, payload=None):
    url = base + path
    data = payload if isinstance(payload, bytes) else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        status = e.code
    return status, body, round((time.time() - t0) * 1000, 1)


def parse_json(body):
    try:
        return json.loads(body)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--images", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_images.txt"))
    ap.add_argument("--expect", default="/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t3-baseline-20261110/results/predictions.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    expect = {}
    with open(args.expect) as f:
        for item in json.load(f)["items"]:
            expect[item["input"]] = item["prediction"]

    cases = []

    st, body, ms = call(args.base, "GET", "/ready")
    cases.append({"name": "GET /ready", "http_status": st, "body": body, "ms": ms,
                  "expected": "200 且 body == 'True'", "pass": st == 200 and body == "True"})

    with open(args.images) as f:
        image_paths = [ln.strip() for ln in f if ln.strip()]
    for idx, path in enumerate(image_paths):
        fmt = "png" if path.lower().endswith(".png") else "jpg"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        payload = json.dumps({"image_base64": b64, "image_format": fmt}).encode("utf-8")
        st, body, ms = call(args.base, "POST", "/api/v1/image-authenticity", payload)
        obj = parse_json(body)
        exp_label = expect.get(path)
        ok = (st == 200 and obj is not None and obj.get("success") is True
              and obj.get("result") in ("1", "0_1", "0_2")
              and obj.get("result") == exp_label)
        cases.append({"name": "image %d (%s, %s)" % (idx + 1, os.path.basename(path), fmt),
                      "path": path, "http_status": st, "body": body, "ms": ms,
                      "t3_local_prediction": exp_label, "service_result": obj.get("result") if obj else None,
                      "expected": "200 success=true result==T3 本地预测(%s)" % exp_label, "pass": ok})

    error_cases = [
        ("缺字段: 无 image_format", json.dumps({"image_base64": "YQ=="}).encode(), 400,
         "缺少必要参数或类型错误: image_format"),
        ("类型错误: image_format 非字符串", json.dumps({"image_base64": "YQ==", "image_format": 123}).encode(), 400,
         "缺少必要参数或类型错误: image_format"),
        ("缺字段: 无 image_base64", json.dumps({"image_format": "jpg"}).encode(), 400,
         "缺少必要参数: image_base64"),
        ("缺字段: 空对象 {}", b"{}", 400, "缺少必要参数: image_base64"),
        ("损坏 Base64", json.dumps({"image_base64": "!!!not@base64$$$", "image_format": "jpg"}).encode(),
         400, "图片 Base64 编码无效"),
        ("非图片输入(合法Base64纯文本)",
         json.dumps({"image_base64": base64.b64encode(b"hello world, definitely not an image " * 5).decode(),
                     "image_format": "jpg"}).encode(), 400, "图片解码失败"),
        ("非法 JSON", b"this is not json", 400, "请求体不是有效的 JSON"),
    ]
    for name, payload, exp_status, msg_fragment in error_cases:
        st, body, ms = call(args.base, "POST", "/api/v1/image-authenticity", payload)
        obj = parse_json(body)
        ok = (st == exp_status and obj is not None and obj.get("success") is False
              and obj.get("result") is None
              and isinstance(obj.get("message"), str) and msg_fragment in obj["message"])
        cases.append({"name": name, "http_status": st, "body": body, "ms": ms,
                      "expected": "HTTP %d success=false 且 message 含「%s」" % (exp_status, msg_fragment),
                      "pass": ok})

    st, body, ms = call(args.base, "GET", "/nope")
    obj = parse_json(body)
    cases.append({"name": "404: GET /nope", "http_status": st, "body": body, "ms": ms,
                  "expected": "HTTP 404", "pass": st == 404 and obj is not None and obj.get("success") is False})

    n_pass = sum(1 for c in cases if c["pass"])
    out = {"base": args.base, "n_cases": len(cases), "n_pass": n_pass,
           "t3_expect_source": args.expect, "cases": cases}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text + "\n")
    for c in cases:
        print("%-4s %-34s http=%s  %s" % ("PASS" if c["pass"] else "FAIL", c["name"],
                                          c["http_status"], (c.get("body") or "")[:80].replace("\n", " ")))
    print("total=%d pass=%d fail=%d" % (len(cases), n_pass, len(cases) - n_pass))
    sys.exit(0 if n_pass == len(cases) else 1)


if __name__ == "__main__":
    main()
