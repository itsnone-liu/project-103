from pathlib import Path
from PIL import Image, ImageDraw
root=Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\urban-doc-style-spike')
for variant in ('A_legacy','B_explicit'):
 src=root/variant/'out'/'frames'; dst=root/variant/'out'/'selected.jpg'
 times=[0,7,15,22,30,37,45,52,59]
 ims=[]
 for sec in times:
  p=src/f'f{round(sec*24):05d}.jpg'
  if p.exists(): ims.append((sec,Image.open(p).convert('RGB').resize((480,270))))
 if not ims: continue
 cols=3; rows=(len(ims)+cols-1)//cols; w,h=480,296
 out=Image.new('RGB',(cols*w,rows*h),(15,18,23)); d=ImageDraw.Draw(out)
 for i,(sec,im) in enumerate(ims):
  x=(i%cols)*w;y=(i//cols)*h;out.paste(im,(x,y));d.text((x+4,y+271),f'{sec}s',fill='white')
 out.save(dst,quality=90); print(variant,dst,len(ims))
