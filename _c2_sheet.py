from pathlib import Path
from PIL import Image,ImageDraw
root=Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\urban-doc-style-spike\C2_times_square\out');src=root/'frames';times=[0,3,7,8,11,14,15,18,22,23,26,29,30,33,36,37,40,44,45,48,51,52,55,59];cols=4;tw,th=480,270;gap=22;rows=(len(times)+cols-1)//cols
out=Image.new('RGB',(cols*tw,rows*(th+gap)),(12,16,24));d=ImageDraw.Draw(out)
for i,t in enumerate(times):
 p=src/f'f{t*24:05d}.jpg'
 if p.exists():x=(i%cols)*tw;y=(i//cols)*(th+gap);out.paste(Image.open(p).convert('RGB').resize((tw,th)),(x,y));d.text((x+5,y+th+2),f'{t:02d}s',fill='white')
out.save(root/'storyboard_24.jpg',quality=92);print(root/'storyboard_24.jpg')
