from pathlib import Path
import cv2
import numpy as np
root=Path(__file__).resolve().parent/'lineart-final'/'out'/'stills'
files=sorted(root.glob('f_*.png'), key=lambda p:int(p.stem.split('_')[1]))
thumbs=[]
for i,p in enumerate(files):
    im=cv2.imread(str(p)); im=cv2.resize(im,(640,360))
    cv2.rectangle(im,(0,0),(640,38),(247,241,223),-1)
    cv2.putText(im,f'S{i+1} frame {p.stem.split("_")[1]}',(14,27),cv2.FONT_HERSHEY_SIMPLEX,.7,(38,53,53),2,cv2.LINE_AA)
    thumbs.append(im)
rows=[]
for i in range(0,len(thumbs),3): rows.append(np.hstack(thumbs[i:i+3]))
sheet=np.vstack(rows)
out=root.parent/'contact-sheet.png';cv2.imwrite(str(out),sheet);print(out)
