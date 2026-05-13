#!/usr/bin/env python3
"""
CIO Dashboard - Local Server
Serves static files + handles JSON read/write for portfolio_state.json

Usage: python server.py
Then open: http://localhost:8080/dashboard.html
"""

import http.server
import json
import os
import shutil
from datetime import datetime

PORT = 8080
PORTFOLIO_FILE = "portfolio_state.json"


class CIOHandler(http.server.SimpleHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        super().do_GET()

    def do_POST(self):
        if self.path == "/save":
            self._handle_save()
        else:
            self.send_error(404)

    def _handle_save(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)

            if os.path.exists(PORTFOLIO_FILE):
                backup = "backups/portfolio_state_{}.json".format(
                    datetime.now().strftime('%Y%m%d_%H%M%S')
                )
                os.makedirs("backups", exist_ok=True)
                shutil.copy2(PORTFOLIO_FILE, backup)

            with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())

        except Exception as e:
            self.send_response(500)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def _cors(self):
        pass  # CORS now injected via end_headers for all responses

    def log_message(self, format, *args):
        if "POST" in (format % args) or "Error" in (format % args):
            print("[{}] {}".format(datetime.now().strftime('%H:%M:%S'), format % args))


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("""
CIO Dashboard Server
====================
Running at : http://localhost:{}
Serving    : {}
Portfolio  : {}
Backups    : ./backups/

Ctrl+C to stop
""".format(PORT, os.getcwd(), PORTFOLIO_FILE))

    with http.server.HTTPServer(("", PORT), CIOHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
