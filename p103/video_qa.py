"""FFmpeg keyframes plus dependency-free PNG contact-sheet assembly."""
from __future__ import annotations
import math,shutil,subprocess,struct,zlib
from pathlib import Path
from .media import probe_media

def _tool(name:str,near:Path|None=None,*,search_root:Path|None=None)->str:
 p=shutil.which(name);exe=name if name.lower().endswith('.exe') else name+'.exe'
 if p:return p
 if near is not None:
  near=Path(near).resolve()
  for parent in (near.parent,*near.parents):
   q=parent/'node_modules'/'@remotion'/'compositor-win32-x64-msvc'/exe
   if q.is_file():return str(q)
 if search_root is not None:
  q=Path(search_root)/'runs'/'architecture-smoke'/'node_modules'/'@remotion'/'compositor-win32-x64-msvc'/exe
  if q.is_file():return str(q)
 raise RuntimeError(f'{name} not found on PATH or near project')
def extract_keyframes(video:Path,output_dir:Path,*,count:int=8,tool_root:Path|None=None)->list[Path]:
 if count<=0:raise ValueError('count must be positive')
 p=probe_media(video)
 if not p.get('has_video'):raise ValueError('Input has no video stream')
 ff=_tool('ffmpeg',video,search_root=tool_root);d=p['duration_ms']/1000;out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);files=[]
 for i in range(count):
  dst=out/f'keyframe-{i+1:02d}.png';t=d*(i+.5)/count
  subprocess.run([ff,'-hide_banner','-loglevel','error','-ss',f'{t:.3f}','-i',str(Path(video).resolve()),'-frames:v','1','-y',str(dst)],check=True)
  if not dst.is_file() or not dst.stat().st_size:raise RuntimeError(f'ffmpeg did not produce {dst}')
  files.append(dst)
 return files

def _read_png(path:Path):
 data=Path(path).read_bytes()
 if data[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError(f'Not a PNG: {path}')
 pos=8;w=h=depth=color=None;compressed=bytearray()
 while pos<len(data):
  n=struct.unpack('>I',data[pos:pos+4])[0];typ=data[pos+4:pos+8];chunk=data[pos+8:pos+8+n];pos+=12+n
  if typ==b'IHDR':w,h,depth,color,_,_,_=struct.unpack('>IIBBBBB',chunk)
  elif typ==b'IDAT':compressed.extend(chunk)
  elif typ==b'IEND':break
 if depth!=8 or color not in (2,6):raise ValueError(f'Only 8-bit RGB/RGBA keyframes supported: {path}')
 bpp=3 if color==2 else 4;raw=zlib.decompress(compressed);stride=w*bpp;rows=[];prev=bytearray(stride);at=0
 for _ in range(h):
  ft=raw[at];at+=1;scan=bytearray(raw[at:at+stride]);at+=stride
  for x in range(stride):
   a=scan[x-bpp] if x>=bpp else 0;b=prev[x];c=prev[x-bpp] if x>=bpp else 0
   if ft==1:scan[x]=(scan[x]+a)&255
   elif ft==2:scan[x]=(scan[x]+b)&255
   elif ft==3:scan[x]=(scan[x]+((a+b)//2))&255
   elif ft==4:
    p0=a+b-c;pa=abs(p0-a);pb=abs(p0-b);pc=abs(p0-c);pr=a if pa<=pb and pa<=pc else b if pb<=pc else c;scan[x]=(scan[x]+pr)&255
   elif ft!=0:raise ValueError(f'Unsupported PNG filter {ft}')
  rows.append(scan);prev=scan
 return w,h,bpp,rows

def _write_png(path:Path,w:int,h:int,rows:list[bytearray])->None:
 raw=b''.join(b'\0'+bytes(row) for row in rows);compressed=zlib.compress(raw,6)
 def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',compressed)+chunk(b'IEND',b'')
 Path(path).write_bytes(data)

def create_contact_sheet(images:list[Path],output:Path,*,columns:int=4,cell_width:int=480,cell_height:int=270,tool_root:Path|None=None)->Path:
 if not images:raise ValueError('At least one image is required')
 if min(columns,cell_width,cell_height)<=0:raise ValueError('columns and cell dimensions must be positive')
 columns=min(columns,len(images));rows_n=math.ceil(len(images)/columns);canvas=[bytearray(columns*cell_width*3) for _ in range(rows_n*cell_height)]
 for idx,path in enumerate(images):
  w,h,bpp,rows=_read_png(path);scale=min(cell_width/w,cell_height/h);nw=max(1,int(w*scale));nh=max(1,int(h*scale));ox=(idx%columns)*cell_width+(cell_width-nw)//2;oy=(idx//columns)*cell_height+(cell_height-nh)//2
  for dy in range(nh):
   sy=min(h-1,int(dy*h/nh));src=rows[sy]
   target=canvas[oy+dy];
   for dx in range(nw):
    sx=min(w-1,int(dx*w/nw));si=sx*bpp;di=(ox+dx)*3;target[di:di+3]=src[si:si+3]
 out=Path(output);out.parent.mkdir(parents=True,exist_ok=True);_write_png(out,columns*cell_width,rows_n*cell_height,canvas);return out

def verify_video(video:Path,*,expected_fps:float|None=None,expected_audio:bool=True,expected_width:int|None=None,expected_height:int|None=None)->dict:
 r=probe_media(video);errors=[]
 if not r.get('has_video'):errors.append('missing video stream')
 if expected_audio and not r.get('has_audio'):errors.append('missing audio stream')
 if expected_width is not None and r.get('width')!=expected_width:errors.append(f"width {r.get('width')} != {expected_width}")
 if expected_height is not None and r.get('height')!=expected_height:errors.append(f"height {r.get('height')} != {expected_height}")
 fps=r.get('fps')
 if expected_fps is not None:
  if not fps:errors.append('missing frame rate')
  else:
   n,_,d=str(fps).partition('/');got=float(n)/float(d or 1)
   if abs(got-expected_fps)>max(.02,expected_fps*.001):errors.append(f'fps {got:.3f} does not match expected {expected_fps}')
 if errors:raise ValueError('E_VIDEO_VERIFY: '+'; '.join(errors))
 return {**r,'verification':{'passed':True,'failures':[]}}
