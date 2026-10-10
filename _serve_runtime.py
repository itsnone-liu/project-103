"""_serve_runtime.py — Lesson Runtime 静态服务器（Range 支持，供视频 seek/移动端）。端口 8862。"""
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent / "lesson-runtime"
MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
        ".vtt": "text/vtt; charset=utf-8", ".md": "text/plain; charset=utf-8",
        ".mp4": "video/mp4", ".png": "image/png", ".svg": "image/svg+xml"}


class H(SimpleHTTPRequestHandler):
    def do_GET(self):
        p = (ROOT / self.path.lstrip("/").split("?")[0]).resolve()
        if self.path.startswith("/") and (p == ROOT or not p.exists()) and not self.path.startswith(("/runtime", "/course", "/index")):
            pass
        if not p.exists() or p.is_dir():
            p = ROOT / "index.html"
        if not p.exists():
            self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers(); return
        size = p.stat().st_size
        ctype = MIME.get(p.suffix, "application/octet-stream")
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            a, _, b = rng[6:].partition("-")
            start = int(a); end = int(b.split("/")[0]) if b.split("/")[0] else size - 1
            end = min(end, size - 1)
            with open(p, "rb") as f:
                f.seek(start); chunk = f.read(end - start + 1)
            self.send_response(206)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", str(len(chunk)))
            self.send_header("Accept-Ranges", "bytes"); self.end_headers()
            self.wfile.write(chunk); return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(size))
        self.send_header("Accept-Ranges", "bytes"); self.end_headers()
        with open(p, "rb") as f:
            while True:
                chunk = f.read(1 << 20)
                if not chunk: break
                self.wfile.write(chunk)

    def log_message(self, fmt, *a):
        print("%s %s" % (self.address_string(), fmt % a), flush=True)


if __name__ == "__main__":
    print(f"serving Lesson Runtime at http://100.84.28.40:8862/ (root={ROOT})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8862), partial(H, directory=str(ROOT))).serve_forever()
