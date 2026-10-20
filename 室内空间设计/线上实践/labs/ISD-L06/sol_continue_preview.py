#!/usr/bin/env python3
"""Continue a transport-truncated L06 preview from exact raw tail."""
from __future__ import annotations
import json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,r'D:\qjcNetDiskDownload\deepseek-harness\project\103')
from pipeline.llm import call

def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 raw=(HERE/'sol_raw.txt').read_text(encoding='utf-8')
 prefix=raw.split('```html',1)[1].lstrip('\r\n') if '```html' in raw else raw
 brief=(HERE/'brief_preview.md').read_text(encoding='utf-8')
 tail=prefix[-9000:]
 msg=[{'role':'system','content':'Continue a transport-truncated HTML file. Output ONLY continuation bytes, no markdown fence and no commentary. Do not repeat existing lines. Begin exactly after the final visible character. Finish every renderer, interaction, progressive Three.js loader, fallback, six selftests, QA globals, closing script/body/html. Check bracket balance.'},
 {'role':'user','content':f'Original implementation contract:\n{brief}\n\nExisting file tail (DO NOT REPEAT):\n---TAIL---\n{tail}\n---END TAIL---\nContinue from exact cutoff. Output continuation only and end with </html>.'}]
 t=time.time();txt,meta=call('sol',msg,effort='high',temperature=.7);secs=round(time.time()-t,1)
 (HERE/'sol_continue_raw.txt').write_text(txt,encoding='utf-8')
 cont=txt.strip()
 if cont.startswith('```html'):cont=cont[len('```html'):].lstrip()
 if cont.endswith('```'):cont=cont[:-3].rstrip()
 # conservative suffix/prefix overlap removal
 for k in range(min(4000,len(prefix),len(cont)),39,-1):
  if prefix.endswith(cont[:k]):cont=cont[k:];break
 final=prefix.rstrip()+cont
 if '</html>' not in final:
  print(json.dumps({'secs':secs,'status':'continuation still incomplete','chars':len(final),'finish':meta.get('finish')},ensure_ascii=False));(HERE/'render_preview.partial.html').write_text(final,encoding='utf-8');return 2
 final=final[:final.rfind('</html>')+7]+'\n'
 (HERE/'render_preview.html').write_text(final,encoding='utf-8')
 usage=json.loads((HERE/'usage.json').read_text(encoding='utf-8'))
 usage['calls'].append({'purpose':'L06 render preview continuation','model':'gpt-6.1-sol','effort':'high','secs':secs,'response_chars':len(txt),'finish':meta.get('finish'),'usage':meta.get('usage')})
 (HERE/'usage.json').write_text(json.dumps(usage,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'secs':secs,'continuation_chars':len(txt),'final_chars':len(final),'finish':meta.get('finish')},ensure_ascii=False));return 0
if __name__=='__main__':sys.exit(main())
