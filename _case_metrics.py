from pathlib import Path
import cv2,re
p=Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\urban-doc-style-spike\C_times_square\code\index.html').read_text(encoding='utf-8')
print('header/footer functions:',bool(re.search(r'function\s+(header|footer)\s*\(',p)))
print('cameraAt exists:', 'cameraAt' in p, 'camera key rows:',len(re.findall(r'^\s*\[\s*\d',p,re.M)))
print('person/people:',len(re.findall(r'person',p,re.I)),'chair:',len(re.findall(r'chair',p,re.I)),'planter:',len(re.findall(r'planter',p,re.I)))
root=Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\urban-doc-style-spike\C_times_square\out\frames')
for t in range(0,55,5):
 a=cv2.imread(str(root/f'f{t*24:05d}.jpg')); b=cv2.imread(str(root/f'f{(t+1)*24:05d}.jpg'))
 a=cv2.resize(a,(480,270));b=cv2.resize(b,(480,270));g1=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY);g2=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
 flow=cv2.calcOpticalFlowFarneback(g1,g2,None,.5,3,15,3,5,1.2,0);mag=cv2.magnitude(flow[...,0],flow[...,1])
 print(f'{t:02d}-{t+1:02d}s flow={float(mag.mean()):.2f} dx={float(flow[...,0].mean()):.2f} dy={float(flow[...,1].mean()):.2f}')
