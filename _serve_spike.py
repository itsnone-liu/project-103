"""Local review server for Sol A/B/C code-video spikes. Start: python _serve_spike.py"""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import re,time
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'runs'/'urban-doc-style-spike'
FILES={'/A.mp4':BASE/'A_legacy'/'out'/'video.mp4','/B.mp4':BASE/'B_explicit'/'out'/'video.mp4','/C.mp4':BASE/'C_times_square'/'out'/'video.mp4','/A-sheet.jpg':BASE/'A_legacy'/'out'/'selected.jpg','/B-sheet.jpg':BASE/'B_explicit'/'out'/'selected.jpg','/C-sheet.jpg':BASE/'C_times_square'/'out'/'storyboard_24.jpg','/evaluation.md':BASE/'EVALUATION.md'}
PAGE='''<!doctype html><meta charset=utf-8><title>Sol Urban Video Spikes</title><style>body{max-width:1100px;margin:30px auto;background:#101821;color:#eee;font:16px system-ui;padding:0 20px}h1,h2{color:#a5d4c7}video{width:100%;background:#000}img{max-width:100%;height:auto}p{line-height:1.6;color:#c4d0d7}.v{margin:36px 0;border-bottom:1px solid #45515d;padding-bottom:30px}</style><h1>Sol 城市纪录片式代码视频短样对照</h1><p>不是全片；请重点反馈构图是否脱卡片、人物/场景是否具体、视点运动是否自然、动画抽象感差距。</p><div class=v><h2>A · 旧上下文基线（城市化题材）</h2><video controls preload=metadata src=/A.mp4></video><img src=/A-sheet.jpg></div><div class=v><h2>B · 完整视觉指令（城市化题材）</h2><video controls preload=metadata src=/B.mp4></video><img src=/B-sheet.jpg></div><div class=v><h2>C · 时代广场案例短样（完整视觉指令）</h2><video controls preload=metadata src=/C.mp4></video><img src=/C-sheet.jpg></div><p><a href=/evaluation.md>技术记录与token/QA</a></p>'''
MIME={'.mp4':'video/mp4','.jpg':'image/jpeg','.md':'text/plain; charset=utf-8'}
class H(BaseHTTPRequestHandler):
 def sendfile(self,p):
  if not p.exists(): self.send_error(404);return
  size=p.stat().st_size; rng=self.headers.get('Range'); start,end=0,size-1
  if rng:
   m=re.match(r'bytes=(\d*)-(\d*)',rng)
   if m: start=int(m.group(1) or 0);end=min(int(m.group(2) or size-1),size-1);self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  else:self.send_response(200)
  self.send_header('Content-Type',MIME.get(p.suffix,'application/octet-stream'));self.send_header('Content-Length',str(end-start+1));self.send_header('Accept-Ranges','bytes');self.send_header('Cache-Control','no-cache');self.end_headers()
  with p.open('rb') as f:f.seek(start);self.wfile.write(f.read(end-start+1))
 def do_GET(self):
  if self.path=='/':
   b=PAGE.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  else:self.sendfile(FILES.get(self.path,Path('')))
 def log_message(self,fmt,*args):print(fmt%args,flush=True)
ThreadingHTTPServer(('0.0.0.0',8864),H).serve_forever()
