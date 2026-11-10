#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""T4 最小 HTTP 服务：图像真伪三分类（1 / 0_1 / 0_2），推理内核复用 T3/starting-kit 既有真实模型权重。

契约（见 competition_spec.json service/output 段与 ServiceContract.md）:
    POST /api/v1/image-authenticity  {"image_base64": str, "image_format": str}
         -> {"success": bool, "message": str, "result": "1"|"0_1"|"0_2"|None}
    GET  /ready -> 200 "True"

实现说明:
- HTTP 层沿用旧工程 starting-kit/main.py 的 http.server 实现（stdlib，无 Flask），
  仅增加: 监听地址/端口可配置（--host/--port 或 MOCK_SERVER_HOST/MOCK_SERVER_PORT），
  启动时按 weights.sha256 固定校验权重（校验失败 exit 1，不做猜测兜底）。
- 推理层 serve_model.py 为 starting-kit 原文件（numpy+Pillow），权重 model_weights.npz
  为 T3 已核验的 model_full.pt 的 numpy 导出（T3 run_report §5.1: max|Δlogit|=3.6e-07,
  argmax 6/6 一致）。
- 错误（缺字段/坏 Base64/非图片）如实返回 400 + success=false，不固定返回某类别。
- image_format 字段按契约接收并记录，但解码以字节内容为准（PIL 自动识别格式）；
  声明格式与内容不符时按解码失败/成功如实报告。

用法:
    python main.py [--host 0.0.0.0] [--port 8000] [--weights PATH]
环境变量:
    MOCK_SERVER_HOST / MOCK_SERVER_PORT / IMAGE_AUTH_MODEL_PATH
"""
import argparse
import base64
import binascii
import hashlib
import json
import os
import sys
import time
import traceback

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from serve_model import get_model

MODEL = None
RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WEIGHTS = os.path.join(RUN_DIR, "model_weights.npz")
CHECKSUM_FILE = os.path.join(RUN_DIR, "weights.sha256")


def verify_weights_sha256(weights_path, checksum_file=CHECKSUM_FILE):
    """按固定校验值核对权重，不匹配即抛错（由 main 转成非 0 退出）。"""
    if not os.path.isfile(weights_path):
        raise RuntimeError("权重文件不存在: %s" % weights_path)
    if not os.path.isfile(checksum_file):
        raise RuntimeError("权重校验文件不存在: %s" % checksum_file)
    with open(checksum_file, encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    if not lines:
        raise RuntimeError("权重校验文件为空: %s" % checksum_file)
    expected = lines[-1].split()[0].lower()
    digest = hashlib.sha256()
    with open(weights_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected:
        raise RuntimeError("权重 sha256 不匹配: 期望 %s 实际 %s (%s)" % (expected, actual, weights_path))
    return actual


def load_model(weights_path):
    global MODEL
    os.environ["IMAGE_AUTH_MODEL_PATH"] = weights_path  # 与 serve_model.get_model 单一来源
    sha = verify_weights_sha256(weights_path)
    MODEL = get_model()
    print("[model] loaded %s sha256=%s" % (MODEL.weights_path, sha))


class Handler(BaseHTTPRequestHandler):
    server_version = "ImageAuthT4/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def _send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/ready":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", "4")
            self.end_headers()
            self.wfile.write(b"True")
        else:
            self._send_json({"success": False, "result": None, "message": "not found"}, 404)

    def do_POST(self):
        if self.path != "/api/v1/image-authenticity":
            self._send_json({"success": False, "result": None, "message": "not found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length > 0 else b""
            try:
                req_data = json.loads(raw.decode("utf-8"))
            except Exception:
                self._send_json({"success": False, "result": None,
                                 "message": "请求体不是有效的 JSON"}, 400)
                return
            if not isinstance(req_data, dict):
                self._send_json({"success": False, "result": None,
                                 "message": "请求体不是有效的 JSON"}, 400)
                return

            image_base64 = req_data.get("image_base64", "")
            image_format = req_data.get("image_format")
            if not image_base64 or not isinstance(image_base64, str):
                self._send_json({"success": False, "result": None,
                                 "message": "缺少必要参数: image_base64"}, 400)
                return

            padding = (-len(image_base64)) % 4
            try:
                image_bytes = base64.b64decode(image_base64 + "=" * padding, validate=True)
            except (binascii.Error, ValueError):
                self._send_json({"success": False, "result": None,
                                 "message": "图片 Base64 编码无效"}, 400)
                return
            if len(image_bytes) == 0:
                self._send_json({"success": False, "result": None,
                                 "message": "图片内容为空"}, 400)
                return

            t0 = time.time()
            try:
                result, probs = MODEL.predict(image_bytes)
            except Exception:
                traceback.print_exc()
                self._send_json({"success": False, "result": None,
                                 "message": "图片解码失败: 无法识别的图片内容"}, 400)
                return
            cost_ms = (time.time() - t0) * 1000.0

            self._send_json({
                "success": True,
                "result": result,
                "message": "鉴定完成",
            })
            sys.stderr.write("[inference] declared_format=%s label=%s probs=%s cost_ms=%.1f\n"
                             % (image_format, result, [round(p, 4) for p in probs], cost_ms))

        except BrokenPipeError:
            pass
        except Exception as e:
            traceback.print_exc()
            try:
                self._send_json({"success": False, "result": None,
                                 "message": "服务器错误: %s" % str(e)}, 500)
            except Exception:
                pass


def main():
    ap = argparse.ArgumentParser(description="T4 图像真伪鉴定最小 HTTP 服务")
    ap.add_argument("--host", default=os.getenv("MOCK_SERVER_HOST", "0.0.0.0"),
                    help="监听地址（默认 0.0.0.0）")
    ap.add_argument("--port", type=int, default=int(os.getenv("MOCK_SERVER_PORT", "8000")),
                    help="监听端口（默认 8000；平台部署可用 MOCK_SERVER_PORT=80）")
    ap.add_argument("--weights", default=None,
                    help="权重 npz 路径（默认本目录 model_weights.npz 或 IMAGE_AUTH_MODEL_PATH）")
    args = ap.parse_args()

    weights_path = args.weights or os.environ.get("IMAGE_AUTH_MODEL_PATH", DEFAULT_WEIGHTS)
    print("=" * 60)
    print("T4 图像真伪鉴定服务启动")
    print("=" * 60)
    try:
        load_model(weights_path)
    except Exception as e:
        print("[model] 加载失败: %s" % e, file=sys.stderr)
        sys.exit(1)

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print("接口列表:")
    print("  POST /api/v1/image-authenticity  - 图像真伪鉴定接口")
    print("  GET  /ready                      - 健康检查")
    print("listening on %s:%d" % (args.host, args.port))
    httpd.serve_forever()


if __name__ == "__main__":
    main()
