#!/usr/bin/env python3
"""Dual-tier preview browser QA; serves vendored assets locally before deployment."""
from __future__ import annotations
import http.server,json,re,socketserver,subprocess,sys,threading,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PORT=8486
class H(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(HERE),**k)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path.startswith('/isd-l06-vendor/'):
   self.path='/vendor/'+self.path[len('/isd-l06-vendor/'):]
  return super().do_GET()
def chrome(url,shot=None):
 prof=HERE/('.qa_profile-'+uuid.uuid4().hex)
 args=[CHROME,'--headless','--disable-gpu','--enable-unsafe-swiftshader','--no-first-run',f'--user-data-dir={prof}','--virtual-time-budget=20000','--window-size=1440,900']
 args+=([f'--screenshot={shot}'] if shot else ['--dump-dom'])
 p=subprocess.run(args+[url],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=150)
 return p.stdout or ''
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 with socketserver.TCPServer(('127.0.0.1',PORT),H) as srv:
  threading.Thread(target=srv.serve_forever,daemon=True).start()
  base=f'http://127.0.0.1:{PORT}'
  results={}
  for tier,param in [('enhanced',''),('basic','?offline=1')]:
   chrome(base+'/render_preview.html'+param,HERE/f'qa_{tier}.png')
   dom=chrome(base+'/qa_harness.html'+param)
   m=re.search(r'QA_RESULT_JSON:(\{.*?\})</pre>',dom,re.S)
   if not m:(HERE/f'qa_dom_{tier}.txt').write_text(dom,encoding='utf-8');print('NO QA RESULT',tier);return 2
   results[tier]=json.loads(m.group(1))
  srv.shutdown()
 (HERE/'qa_result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 ok=all(x['ready'] and x['selftest'] and x['selftest'].get('passed')==6 and not x['selftest'].get('failed') and not x['errors'] and x['canvasCount']>=1 for x in results.values())
 ok=ok and results['basic']['tier']=='basic' and results['enhanced']['tier']=='enhanced'
 print(json.dumps({'pass':ok,'results':results},ensure_ascii=False,indent=2))
 return 0 if ok else 1
if __name__=='__main__':sys.exit(main())
