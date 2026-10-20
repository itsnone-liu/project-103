#!/usr/bin/env python3
"""Generate ISD-L06 dual-tier rendering preview via sol high reasoning."""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
from pipeline.llm import call


def main():
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    brief=(HERE/'brief_preview.md').read_text(encoding='utf-8')
    msg=[{'role':'system','content':'You build one production-ready HTML/CSS/vanilla JS architectural 3D preview. Follow the Chinese brief exactly. The app must run WITHOUT libraries (canvas software fallback) and progressively enhance with legacy Three.js r147 UMD + OrbitControls + RoomEnvironment when vendored scripts load. Robust no-white-screen fallback and working orbit/zoom in both modes are crucial. Output EXACTLY one fenced ```html block. Check JS syntax and parentheses.'},
         {'role':'user','content':brief+'\nProduce render_preview.html now. Do not simulate enhanced mode with a 2D screenshot; actually initialize THREE.WebGLRenderer.'}]
    t=time.time(); txt,meta=call('sol',msg,effort='high',temperature=1.0); elapsed=round(time.time()-t,1)
    (HERE/'sol_raw.txt').write_text(txt,encoding='utf-8')
    m=re.search(r'```html\s*\n(.*?)```',txt,re.S)
    data={'secs':elapsed,'response_chars':len(txt),'finish':meta.get('finish'),'usage':meta.get('usage'),'html_chars':len(m.group(1)) if m else 0}
    (HERE/'usage.json').write_text(json.dumps({'calls':[{'purpose':'L06 render preview v1','model':'gpt-6.1-sol','effort':'high',**data}]},ensure_ascii=False,indent=2),encoding='utf-8')
    if not m: print('NO HTML BLOCK — see sol_raw.txt'); return 1
    (HERE/'render_preview.html').write_text(m.group(1).strip()+'\n',encoding='utf-8')
    print(json.dumps(data,ensure_ascii=False)); return 0

if __name__=='__main__': sys.exit(main())
