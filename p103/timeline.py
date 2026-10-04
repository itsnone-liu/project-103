"""Versioned narration timeline and subtitle interchange for Project 103."""
from __future__ import annotations
import hashlib,json,re,unicodedata
from dataclasses import asdict,dataclass
from pathlib import Path
from typing import Iterable
SCHEMA_VERSION='p103.narration/v1'
_TIME=re.compile(r'^(?:(?P<hours>\d+):)?(?P<minutes>\d{1,2}):(?P<seconds>\d{2})[,.](?P<millis>\d{3})$');_CUE=re.compile(r'^\s*(\S+)\s+-->\s+(\S+)(?:\s+.*)?$');_TAG=re.compile(r'<[^>]*>')
@dataclass(frozen=True)
class NarrationLine:
 id:str;scene_id:str;display_text:str;narration_text:str;tts_text:str;start_ms:int;end_ms:int;tts_cue_text:str='';source:str='imported'
 @property
 def duration_ms(self):return self.end_ms-self.start_ms
 def at_ms(self,p):
  if not 0<=p<=1:raise ValueError('progress must be between 0 and 1')
  return round(self.start_ms+self.duration_ms*p)
 def during_ms(self,a,b):
  if not 0<=a<=b<=1:raise ValueError('during progress must satisfy 0 <= start <= end <= 1')
  return self.at_ms(a),self.at_ms(b)
 @property
 def start(self):return self.start_ms/1000
 @property
 def end(self):return self.end_ms/1000
 @property
 def duration(self):return self.duration_ms/1000
 def at(self,p):return self.at_ms(p)/1000
 def during(self,a,b):
  x,y=self.during_ms(a,b);return x/1000,y/1000
@dataclass
class Timeline:
 version:str;duration_ms:int;cues:tuple[NarrationLine,...];source_format:str;fps:int=30;intro_padding_ms:int=0;tail_padding_ms:int=0;tts:dict|None=None;vtt:dict|None=None;segments:tuple[dict,...]=()
 @property
 def duration(self):return self.duration_ms/1000
 def to_dict(self):return {'schema_version':self.version,'fps':self.fps,'duration_ms':self.duration_ms,'audio_duration_ms':(self.tts or {}).get('audio_duration_ms'),'source_format':self.source_format,'intro_padding_ms':self.intro_padding_ms,'tail_padding_ms':self.tail_padding_ms,'tts':self.tts,'vtt':self.vtt,'segments':list(self.segments),'cues':[asdict(c)|{'duration_ms':c.duration_ms} for c in self.cues]}
 def write_json(self,path):
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(self.to_dict(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def parse_timestamp(value):
 m=_TIME.fullmatch(value.strip())
 if not m:raise ValueError(f'Invalid subtitle timestamp: {value!r}')
 h,mi,s,ms=int(m.group('hours') or 0),int(m.group('minutes')),int(m.group('seconds')),int(m.group('millis'))
 if mi>=60 or s>=60:raise ValueError(f'Timestamp component out of range: {value!r}')
 return ((h*60+mi)*60+s)*1000+ms
def _format_timestamp(ms):
 if ms<0:raise ValueError('timestamp cannot be negative')
 h,r=divmod(ms,3600000);m,r=divmod(r,60000);s,ms=divmod(r,1000);return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
def normalize_speech(text):
 text=_TAG.sub('',unicodedata.normalize('NFKC',text)).casefold();return ''.join(c for c in text if not unicodedata.category(c).startswith(('P','Z')) and not c.isspace())
def _clean(text):return ' '.join(_TAG.sub('',text).split()).strip()
def parse_cues(text,*,source_format='auto'):
 lines=text.lstrip('\ufeff').replace('\r\n','\n').replace('\r','\n').split('\n');first=next((x.strip() for x in lines if x.strip()),'');fmt=source_format.lower() if source_format!='auto' else ('vtt' if first.startswith('WEBVTT') else 'srt')
 if fmt not in {'vtt','srt'}:raise ValueError('source_format must be auto, vtt, or srt')
 out=[];i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line or line.startswith(('WEBVTT','NOTE','STYLE','REGION')):i+=1;continue
  m=_CUE.match(line)
  if not m:i+=1;continue
  try:a,b=parse_timestamp(m.group(1)),parse_timestamp(m.group(2))
  except ValueError as e:raise ValueError(f'Subtitle line {i+1}: {e}') from e
  i+=1;payload=[]
  while i<len(lines) and lines[i].strip():payload.append(lines[i].strip());i+=1
  caption=_clean(' '.join(payload))
  if not caption:raise ValueError(f'Subtitle cue at line {i+1} has no text')
  if b<=a:raise ValueError(f'Subtitle line {i}: end must be after start ({a}–{b} ms)')
  out.append((a,b,caption))
 if not out:raise ValueError('No subtitle cues found')
 return out,fmt
def normalize_cues(cues,*,overlap_tolerance_ms=50):
 if overlap_tolerance_ms<0:raise ValueError('overlap_tolerance_ms must be non-negative')
 out=[]
 for a,b,t in sorted(cues,key=lambda x:(x[0],x[1])):
  if not t.strip() or b<=a:continue
  if out and a<out[-1][1]:
   overlap=out[-1][1]-a
   if overlap>overlap_tolerance_ms:raise ValueError(f'E_NARR_OVERLAP: cues overlap by {overlap} ms (> {overlap_tolerance_ms} ms)')
   pa,_,pt=out[-1]
   if a<=pa:raise ValueError('E_NARR_OVERLAP: cannot normalize to positive intervals')
   out[-1]=(pa,a,pt)
  out.append((a,b,t.strip()))
 if not out:raise ValueError('No non-empty positive-duration cues after normalization')
 return out
def import_subtitles(path,*,display_texts=None,narration_texts=None,tts_texts=None,scene_id='scene-01',source_format=None,overlap_tolerance_ms=50,fps=30):
 path=Path(path);hint=source_format or {'.vtt':'vtt','.srt':'srt'}.get(path.suffix.lower(),'auto');raw,fmt=parse_cues(path.read_text(encoding='utf-8-sig'),source_format=hint);norm=normalize_cues(raw,overlap_tolerance_ms=overlap_tolerance_ms)
 layers=[list(v) if v is not None else [] for v in (display_texts,narration_texts,tts_texts)]
 for n,x in zip(('display_texts','narration_texts','tts_texts'),layers):
  if x and len(x)!=len(norm):raise ValueError(f'{n} count ({len(x)}) must match subtitle cues ({len(norm)})')
 cues=[]
 for i,((a,b,t),(_,_,rt)) in enumerate(zip(norm,raw),1):
  d=layers[0][i-1] if layers[0] else t;n=layers[1][i-1] if layers[1] else t;tt=layers[2][i-1] if layers[2] else n;cues.append(NarrationLine(f'{scene_id}-line-{i:02d}',scene_id,d,n,tt,a,b,rt,fmt))
 vtt={'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};segments=tuple({'id':c.id,'scene_id':c.scene_id,'start_ms':c.start_ms,'end_ms':c.end_ms,'display_text':c.display_text,'narration_text':c.narration_text,'tts_text':c.tts_text,'tts_cue_text':c.tts_cue_text} for c in cues)
 return Timeline(SCHEMA_VERSION,max(c.end_ms for c in cues),tuple(cues),fmt,fps=fps,vtt=vtt,segments=segments)
def align_tts_cues(timeline,cue_texts,cue_times=None):
 texts=list(cue_texts);actual=[normalize_speech(x) for x in texts];expected=[normalize_speech(c.tts_text) for c in timeline.cues];ex=''.join(expected);ac=''.join(actual)
 if not ex:raise ValueError('E_NARR_EMPTY: no tts_text to align')
 if ex!=ac:
  k=min(len(ex),len(ac));p=next((i for i in range(k) if ex[i]!=ac[i]),k);raise ValueError(f'E_NARR_TEXT_MISMATCH: normalized text differs at char {p}; expected={len(ex)}, cues={len(ac)}')
 times=list(cue_times) if cue_times is not None else [(c.start_ms,c.end_ms) for c in timeline.cues]
 if len(times)!=len(texts):raise ValueError('cue_times count must match cue_texts')
 if any(a<0 or b<=a for a,b in times):raise ValueError('cue_times must be positive intervals')
 spans=[];cursor=0
 for text,(a,b) in zip(actual,times):spans.append((cursor,cursor+len(text),a,b));cursor+=len(text)
 def tm(pos):
  for lo,hi,a,b in spans:
   if lo<=pos<=hi:
    if pos==hi:return b
    if pos==lo:return a
    return round(a+(b-a)*(pos-lo)/max(1,hi-lo))
  return spans[-1][3]
 result=[];pos=0
 for c,t in zip(timeline.cues,expected):end=pos+len(t);result.append({'segment_id':c.id,'start_ms':tm(pos),'end_ms':tm(end),'tts_text':c.tts_text});pos=end
 return result
def generate_srt(timeline,path,*,text_layer='display_text'):
 if text_layer not in {'display_text','narration_text','tts_text'}:raise ValueError('invalid text_layer')
 blocks=[]
 for i,c in enumerate(timeline.cues,1):
  t=getattr(c,text_layer).strip()
  if not t:raise ValueError(f'{c.id}: empty {text_layer}')
  blocks.append(f'{i}\r\n{_format_timestamp(c.start_ms)} --> {_format_timestamp(c.end_ms)}\r\n{t}')
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(('\r\n\r\n'.join(blocks)+'\r\n').encode('utf-8'))
def validate_timeline(timeline,*,frame_rate=None):
 errors=[]
 if timeline.version!=SCHEMA_VERSION:errors.append(f'unsupported timeline schema: {timeline.version}')
 if not timeline.cues:return ['timeline has no cues']
 ps=pe=-1
 for c in timeline.cues:
  if c.start_ms<0 or c.end_ms<=c.start_ms:errors.append(f'{c.id}: invalid cue interval')
  if c.start_ms<ps or c.start_ms<pe:errors.append(f'{c.id}: cues are not ordered/non-overlapping')
  ps,pe=c.start_ms,c.end_ms
  for f in ('display_text','narration_text','tts_text'):
   if not getattr(c,f).strip():errors.append(f'{c.id}: {f} is empty')
 if timeline.duration_ms<max(c.end_ms for c in timeline.cues):errors.append('timeline duration is shorter than its last cue')
 if frame_rate:
  try:remotion_frames(timeline,frame_rate,validate=False)
  except ValueError as e:errors.append(str(e))
 return errors
def remotion_frames(timeline,fps,*,validate=True):
 if fps<=0:raise ValueError('fps must be positive')
 if validate:
  errors=validate_timeline(timeline)
  if errors:raise ValueError('Invalid timeline: '+'; '.join(errors))
 out=[]
 for c in timeline.cues:
  a,b=c.start_ms*fps//1000,(c.end_ms*fps+999)//1000
  if b<=a:raise ValueError(f'{c.id}: interval collapses at {fps} fps')
  out.append({'id':c.id,'startFrame':a,'endFrame':b})
 return out
