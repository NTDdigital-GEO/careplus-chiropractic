#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本機預覽伺服器。
必須用伺服器看，不能雙擊開 dist/index.html——
因為 CSS 與內部連結都用絕對路徑（/assets/…、/services/…），
file:// 會解析到硬碟根目錄，樣式與連結全都會失效。

    python3 serve.py          # http://localhost:4173
"""
import os, sys, functools, http.server, socketserver

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)   # 不用 chdir，避免 getcwd 失敗
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def send_error(self, code, message=None, explain=None):
        # 用真正的 404 頁，模擬正式環境的 Caddy 設定
        f404 = os.path.join(ROOT, "404.html")
        if code == 404 and os.path.isfile(f404):
            body = open(f404, "rb").read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)
    def log_message(self, fmt, *a):
        sys.stderr.write("  %s\n" % (fmt % a))

def lan_ip():
    """取得本機在區域網路上的 IP，讓同一個 WiFi 的手機可以連進來"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]
    except Exception:
        ip = None
    finally:
        s.close()
    return ip

socketserver.TCPServer.allow_reuse_address = True
# 綁 0.0.0.0：同一個 WiFi 底下的手機、平板也連得進來
with socketserver.TCPServer(("0.0.0.0", PORT), H) as httpd:
    ip = lan_ip()
    print("=" * 52)
    print(f"  這台電腦看：   http://localhost:{PORT}/")
    if ip:
        print(f"  手機／平板看： http://{ip}:{PORT}/")
        print(f"                （手機要連同一個 WiFi）")
    print(f"  審稿目錄：     http://localhost:{PORT}/_pages/")
    print("=" * 52)
    print("  要停止：在這個視窗按 Control + C")
    print()
    httpd.serve_forever()
