from pathlib import Path
from PIL import Image, ImageDraw
D=Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103\research\urban-doc')
fs=sorted(D.glob('opening_*.jpg'))
TW,TH=320,180; cols,rows=5,5
out=Image.new('RGB',(cols*(TW+6)+6,rows*(TH+22)+6),(15,18,23)); d=ImageDraw.Draw(out)
for k,p in enumerate(fs[:25]):
 im=Image.open(p).resize((TW,TH)); r,c=divmod(k,cols); x=6+c*(TW+6); y=6+r*(TH+22); out.paste(im,(x,y)); d.text((x+4,y+TH+2),f'{k*2:02d}s',fill='white')
out.save(D/'opening_50s.jpg',quality=90)
print(D/'opening_50s.jpg')