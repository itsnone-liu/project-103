from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
root=Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\urban-doc-style-spike')
for variant in ('A_legacy','B_explicit'):
 src=root/variant/'out'/'frames'; times=[round(20+i*.5,1) for i in range(21)]; tw,th=320,180; cols=4; rows=6
 out=Image.new('RGB',(cols*tw,rows*(th+20)),(15,18,23)); d=ImageDraw.Draw(out)
 for i,t in enumerate(times):
  p=src/f'f{round(t*24):05d}.jpg'
  if p.exists():
   x=i%cols*tw;y=i//cols*(th+20);out.paste(Image.open(p).convert('RGB').resize((tw,th)),(x,y));d.text((x+3,y+th+2),f'{t}s',fill='white')
 out.save(root/variant/'out'/'motion_20_30.jpg',quality=92)
 vals=[]
 for t in (20,22,24,26,28,30,32,34,36,38,40,42,44,46):
  a=Image.open(src/f'f{t*24:05d}.jpg').convert('RGB').resize((160,90));b=Image.open(src/f'f{t*24+6:05d}.jpg').convert('RGB').resize((160,90)); diff=ImageChops.difference(a,b).convert('L');vals.append(round(sum(diff.getdata())/(160*90),2))
 print(variant,'mean abs luma frame difference at +0.25s:',vals)
