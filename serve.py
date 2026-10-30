#!/usr/bin/env python3
"""安装脚本测试机的常驻服务：8000 端口。
/            环境概览
/healthz     健康检查
/exec?c=CMD  执行 shell 命令并回显（仅测试机，勿用于生产）
"""
import http.server
import json
import os
import platform
import shlex
import socketserver
import subprocess
import sys
import time

START = time.time()
PORT = int(os.environ.get("PORT", "8000"))


def sh(cmd, timeout=60):
    try:
        p = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return {"rc": p.returncode, "out": p.stdout[-8000:], "err": p.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        return {"rc": -1, "out": "", "err": "timeout"}


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        query = self.path.split("?", 1)[1] if "?" in self.path else ""

        if path == "/healthz":
            return self._send(200, "ok", "text/plain")
        if path == "/exec":
            from urllib.parse import parse_qs

            q = parse_qs(query)
            cmd = (q.get("c") or [""])[0]
            if not cmd:
                return self._send(400, json.dumps({"error": "missing ?c="}))
            return self._send(200, json.dumps(sh(cmd), ensure_ascii=False))
        if path in ("/", "/info"):
            info = {
                "host": platform.node(),
                "system": platform.platform(),
                "kernel": platform.release(),
                "machine": platform.machine(),
                "python": sys.version.split()[0],
                "uptime_sec": round(time.time() - START, 1),
                "cpu_count": os.cpu_count(),
                "env": {k: v for k, v in os.environ.items() if not k.lower().endswith(("token", "key", "secret", "pass"))},
                "disk": sh("df -h / /data 2>/dev/null")["out"].splitlines(),
                "mem": sh("free -m 2>/dev/null")["out"].splitlines(),
                "routes": ["GET /", "GET /healthz", "GET /exec?c=<shell command>"],
            }
            return self._send(200, json.dumps(info, indent=2, ensure_ascii=False))
        return self._send(404, json.dumps({"error": "not found", "path": path}))

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    os.makedirs("/data", exist_ok=True)
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), H) as httpd:
        httpd.allow_reuse_address = True
        print(f"listening on 0.0.0.0:{PORT}", flush=True)
        httpd.serve_forever()
