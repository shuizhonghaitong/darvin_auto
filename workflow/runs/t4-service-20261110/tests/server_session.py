#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T4 服务会话进程（子进程侧）。

与生产启动 main.py 相同的代码路径：sha256 固定校验 -> 加载真实模型 ->
main.Handler 处理真实 HTTP 请求字节。唯一差异：传输端点为命名管道（FIFO）
而非 TCP listener——本沙箱禁止 socket()/bind()（见 logs/server.err 的
PermissionError 证据），FIFO 是沙箱内可用的字节流传输。

会话协议（父进程先建好 req_N/rsp_N 两个 FIFO 并持有 req_N 的 O_RDWR）:
    子进程对每个 N: open(req_N, O_RDONLY) -> open(rsp_N, O_WRONLY)（阻塞，
    与父进程 open(rsp_N, O_RDONLY) 互为同步点）-> 处理 1 个完整请求 -> 写响应 -> 关闭。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main as svc  # noqa: E402（注意：不可用裸名 main，会被下方 def main() 遮蔽）


class FifoHandlerSocket(object):
    """适配 main.Handler（BaseHTTPRequestHandler.setup 调用 request.makefile）。"""

    def __init__(self, rfile, wfile):
        self._r = rfile
        self._w = wfile

    def makefile(self, mode, bufsize=None):
        return self._r if "r" in mode else self._w


def run_session(req_path, rsp_path, server_obj):
    req_fd = os.open(req_path, os.O_RDONLY)
    with os.fdopen(req_fd, "rb") as req_file:
        rsp_fd = os.open(rsp_path, os.O_WRONLY)
        with os.fdopen(rsp_fd, "wb") as rsp_file:
            sock = FifoHandlerSocket(req_file, rsp_file)
            try:
                svc.Handler(sock, ("fifo", 0), server_obj)
            except (BrokenPipeError, ConnectionResetError):
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", type=int, required=True)
    ap.add_argument("--fifo-prefix", default="/tmp/t4srv")
    ap.add_argument("--weights", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model_weights.npz"))
    args = ap.parse_args()

    svc.load_model(args.weights)  # 含 sha256 固定校验，失败抛异常 -> 非 0 退出
    print("[server-session] model loaded; serving %d FIFO sessions" % args.sessions, flush=True)
    server_obj = type("S", (), {"server_name": "fifo"})()
    for n in range(args.sessions):
        run_session("%s.req.%d" % (args.fifo_prefix, n),
                    "%s.rsp.%d" % (args.fifo_prefix, n), server_obj)
    print("[server-session] all sessions done", flush=True)


if __name__ == "__main__":
    main()
