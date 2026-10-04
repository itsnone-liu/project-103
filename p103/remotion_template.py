"""Generate a configurable Remotion timeline consumer for bounded scene slots."""
from __future__ import annotations
import json,shutil
from pathlib import Path

def _validate_scenes(scene_specs:list[dict]|None,cues:list[dict])->list[dict]:
 if scene_specs is None:return []
 if not isinstance(scene_specs,list):raise ValueError('scene_specs must be an array')
 by_id={c['id']:c for c in cues};result=[]
 for i,s in enumerate(scene_specs):
  if not isinstance(s,dict):raise ValueError(f'scene_specs[{i}] must be an object')
  sid=s.get('segment_id');offset=s.get('offset_ms',0);duration=s.get('duration_ms')
  if sid not in by_id:raise ValueError(f'scene_specs[{i}] references unknown segment_id: {sid}')
  if not isinstance(offset,int) or isinstance(offset,bool) or offset<0:raise ValueError(f'scene_specs[{i}].offset_ms must be non-negative integer')
  if not isinstance(duration,int) or isinstance(duration,bool) or duration<=0:raise ValueError(f'scene_specs[{i}].duration_ms must be positive integer')
  cue=by_id[sid];length=cue['end_ms']-cue['start_ms']
  if offset>=length:raise ValueError(f'scene_specs[{i}] starts outside its segment')
  if offset+duration>length:raise ValueError(f'scene_specs[{i}] duration exceeds its segment boundary')
  transition=s.get('transition','cut')
  if transition not in {'cut','fade'}:raise ValueError(f'scene_specs[{i}].transition must be cut or fade')
  result.append({'id':s.get('id',f'scene-{i+1:02d}'),'segment_id':sid,'offset_ms':offset,'duration_ms':duration,'color':s.get('color','#101820'),'title':s.get('title',''),'transition':transition})
 return result

def write_consumer(project_root:Path,*,audio_static_path:str='audio/narration.mp3',scene_specs:list[dict]|None=None)->None:
 root=Path(project_root);src=root/'src';gen=src/'generated';gen.mkdir(parents=True,exist_ok=True)
 manifest_path=root/'audio'/'timeline.json'
 if not manifest_path.is_file():raise FileNotFoundError(f'Missing timeline manifest: {manifest_path}')
 manifest=json.loads(manifest_path.read_text(encoding='utf-8'));cues=manifest.get('cues',[]);scenes=_validate_scenes(scene_specs,cues)
 (gen/'scene-specs.json').write_text(json.dumps(scenes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 audio=json.dumps(audio_static_path,ensure_ascii=False)
 component='''import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, interpolate} from 'remotion';
import {CUES, FPS} from './timeline';
import SCENES_JSON from './scene-specs.json';
const SCENES = SCENES_JSON as Array<{id:string;segment_id:string;offset_ms:number;duration_ms:number;color:string;title:string;transition:'cut'|'fade'}>;
export const TimelineConsumer: React.FC = () => {
 const frame=useCurrentFrame();
 const cue=CUES.find((item)=>frame>=item.startFrame&&frame<item.endFrame);
 return <AbsoluteFill style={{backgroundColor:'#101820',color:'white',fontFamily:'sans-serif'}}>
  <Audio src={staticFile('''+audio+''')}/>
  {SCENES.map((scene)=>{
   const cueData=CUES.find((item)=>item.segmentId===scene.segment_id)!;
   const from=cueData.startFrame+Math.floor(scene.offset_ms*FPS/1000);
   const durationInFrames=Math.max(1,Math.ceil(scene.duration_ms*FPS/1000));
   const fadeFrames=Math.min(12,Math.floor(durationInFrames/2));
   const visual=<AbsoluteFill style={{backgroundColor:scene.color,justifyContent:'center',alignItems:'center'}}>
    <div style={{fontSize:56,fontWeight:700}}>{scene.title||cue?.text||''}</div>
   </AbsoluteFill>;
   return <Sequence key={scene.id} from={from} durationInFrames={durationInFrames}>
    {scene.transition==='fade'?<AbsoluteFill style={{opacity:interpolate(frame,[from,from+fadeFrames,from+durationInFrames-fadeFrames,from+durationInFrames],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>{visual}</AbsoluteFill>:visual}
   </Sequence>;
  })}
  <div style={{position:'absolute',left:80,right:80,bottom:72,textAlign:'center',fontSize:38,textShadow:'0 2px 6px #000'}}>{cue?.text??''}</div>
  <div style={{position:'absolute',top:32,right:48,opacity:.6}}>{frame}/{FPS}</div>
 </AbsoluteFill>;
};
'''
 (gen/'TimelineConsumer.tsx').write_text(component,encoding='utf-8')
 audio_descriptor=manifest.get('tts') or {}
 if audio_descriptor.get('path'):
  audio_file=(root/audio_descriptor['path']).resolve();public_audio=root/'public'/audio_static_path
  if root.resolve() not in audio_file.parents:raise ValueError('Registered audio path escapes run root')
  if not audio_file.is_file():raise FileNotFoundError(f'Registered narration missing: {audio_file}')
  if public_audio.resolve()!=audio_file and audio_file.is_file():
   public_audio.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(audio_file,public_audio)
 (src/'Root.tsx').write_text("import React from 'react';\nimport {Composition} from 'remotion';\nimport {DURATION_IN_FRAMES,FPS} from './generated/timeline';\nimport {TimelineConsumer} from './generated/TimelineConsumer';\nexport const RemotionRoot:React.FC=()=> <Composition id=\"P103TimelineConsumer\" component={TimelineConsumer} durationInFrames={DURATION_IN_FRAMES} fps={FPS} width={1920} height={1080}/>;\n",encoding='utf-8')
 (src/'index.ts').write_text("import {registerRoot} from 'remotion';\nimport {RemotionRoot} from './Root';\nregisterRoot(RemotionRoot);\n",encoding='utf-8')
