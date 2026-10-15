from pathlib import Path
import cv2
root=Path(r'D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\urban-doc-style-spike')
for variant in ('A_legacy','B_explicit'):
 p=root/variant/'out'/'frames'; print('\n',variant)
 for sec in range(0,60,5):
  a=cv2.imread(str(p/f'f{sec*24:05d}.jpg'));b=cv2.imread(str(p/f'f{(sec+1)*24:05d}.jpg'))
  if a is None or b is None: continue
  a=cv2.resize(a,(480,270));b=cv2.resize(b,(480,270)); gray1=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY);gray2=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
  flow=cv2.calcOpticalFlowFarneback(gray1,gray2,None,.5,3,15,3,5,1.2,0)
  mag=cv2.magnitude(flow[...,0],flow[...,1]); med=float(cv2.mean(mag)[0]);
  medx=float(cv2.mean(flow[...,0])[0]);medy=float(cv2.mean(flow[...,1])[0]);
  print(f'{sec:02d}-{sec+1:02d}s: flow_mean={med:.3f}px/frame, dx={medx:.3f}, dy={medy:.3f}')
