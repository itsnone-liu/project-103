import React from 'react';
import {AbsoluteFill, Audio, Easing, interpolate, staticFile, useCurrentFrame} from 'remotion';
import './style.css';

const FPS=30;
const ease=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const pulse=(f:number,period=80)=>0.65+0.35*Math.sin((f/period)*Math.PI*2);
const cues=[
  {a:3,b:169,text:'白天，阳光同时照向海洋和陆地，但陆地升温更快。'},
  {a:167,b:384,text:'陆地上方的空气被加热，膨胀变轻，向上升起，近地面气压随之降低。'},
  {a:384,b:638,text:'海面上方空气相对较冷，近地面气压较高，于是空气从海洋流向陆地，这就是海风。'},
  {a:638,b:876,text:'升起的空气在高空转向海洋，再缓缓下沉，与近地面海风连成一个闭合环流。'},
];
const stage=(f:number)=>f<170?1:f<385?2:f<640?3:4;

const Arrow:React.FC<{d:string;color:string;show:number;dash?:number;label?:string;labelX?:number;labelY?:number}>=({d,color,show,dash=0,label,labelX=0,labelY=0})=>(
  <g style={{opacity:show}}><path d={d} fill="none" stroke="#fff" strokeWidth="29" strokeLinecap="round" strokeLinejoin="round" opacity=".62"/><path d={d} fill="none" stroke={color} strokeWidth="18" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="26 20" strokeDashoffset={-dash} markerEnd={`url(#arrow-${color.replace('#','')})`}/>{label&&<text x={labelX} y={labelY} className="arrow-label" fill={color}>{label}</text>}</g>
);

export const SeaBreezeVideo:React.FC=()=>{
  const f=useCurrentFrame(),s=stage(f),sun=ease(f,0,70),heat=ease(f,55,170),rise=ease(f,175,290),pressure=ease(f,270,385),surface=ease(f,390,535),upper=ease(f,610,760),closure=ease(f,745,850);
  const landGlow=heat*(0.7+0.3*pulse(f,65));
  const subtitle=cues.find(c=>f>=c.a&&f<c.b)?.text??'';
  const dash=f*1.8;
  return <AbsoluteFill className="video">
    <Audio src={staticFile('audio/narration.mp3')}/>
    <div className="sky-glow"/>
    <div className="topbar"><div className="lesson-chip">地理 · 热力环流</div><div className="progress"><i style={{width:`${(f/899)*100}%`}}/></div><div className="counter">{s}/4</div></div>
    <div className="headline">
      <div className="kicker">白天的海岸</div>
      <h1>{s===1?'同一束阳光，升温一样快吗？':s===2?'暖空气上升，地面留下什么？':s===3?'空气从高压流向低压':'一来一回，环流闭合'}</h1>
    </div>
    <svg className="world" viewBox="0 0 1920 840">
      <defs>
        <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#57c7e8"/><stop offset="1" stopColor="#087ba9"/></linearGradient>
        <linearGradient id="land" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#f2c06b"/><stop offset="1" stopColor="#b97839"/></linearGradient>
        <radialGradient id="warm"><stop stopColor="#ffb341" stopOpacity=".72"/><stop offset="1" stopColor="#ff6945" stopOpacity="0"/></radialGradient>
        {['f05c42','226fb2','7252c7','ffffff'].map(c=><marker key={c} id={`arrow-${c}`} viewBox="0 0 14 14" refX="11" refY="7" markerWidth="12" markerHeight="12" orient="auto"><path d="M1 1 L13 7 L1 13 Z" fill={`#${c}`}/></marker>)}
        <filter id="soft"><feGaussianBlur stdDeviation="14"/></filter>
      </defs>
      <circle cx="240" cy="140" r={62+sun*12} fill="#ffd352" opacity={sun}/><g opacity={sun*.72} stroke="#ffd352" strokeWidth="9">{Array.from({length:12}).map((_,i)=>{const a=i*Math.PI/6;return <line key={i} x1={240+95*Math.cos(a)} y1={140+95*Math.sin(a)} x2={240+135*Math.cos(a)} y2={140+135*Math.sin(a)}/>})}</g>
      {Array.from({length:8}).map((_,i)=><line key={i} x1={320+i*175} y1={180-(i%2)*24} x2={370+i*175} y2={360} stroke="#ffd352" strokeWidth="7" opacity={sun*.35}/>) }
      <path d="M0 520 C260 505 510 540 900 520 L900 840 H0 Z" fill="url(#sea)"/>
      <path d="M900 520 C1100 490 1270 530 1450 470 C1630 410 1760 460 1920 420 L1920 840 H900 Z" fill="url(#land)"/>
      <path d="M0 530 C250 510 530 548 900 523" fill="none" stroke="#dff9ff" strokeWidth="12" opacity=".8"/>
      <text x="350" y="675" className="zone-name sea-name">海洋</text><text x="1510" y="675" className="zone-name land-name">陆地</text>
      <g opacity={heat}><rect x="246" y="705" width="340" height="62" rx="31" className="temp-pill cool"/><text x="416" y="746" textAnchor="middle" className="temp-text">升温较慢</text><rect x="1260" y="705" width="340" height="62" rx="31" className="temp-pill hot"/><text x="1430" y="746" textAnchor="middle" className="temp-text">升温更快</text></g>
      <ellipse cx="1430" cy="500" rx="280" ry="260" fill="url(#warm)" opacity={landGlow}/>
      <g opacity={rise}><circle cx="1390" cy={500-rise*170} r="42" fill="#ff9a54" opacity=".35"/><circle cx="1470" cy={480-rise*235} r="55" fill="#ff9a54" opacity=".3"/><circle cx="1350" cy={470-rise*115} r="32" fill="#ff9a54" opacity=".4"/></g>
      <Arrow d="M1435 505 C1430 410 1420 310 1420 205" color="#f05c42" show={rise} dash={dash} label="暖空气上升" labelX={1480} labelY={330}/>
      <g opacity={pressure}><rect x="1215" y="535" width="160" height="72" rx="20" className="pressure low"/><text x="1295" y="581" textAnchor="middle" className="pressure-text">低压</text><rect x="600" y="535" width="160" height="72" rx="20" className="pressure high"/><text x="680" y="581" textAnchor="middle" className="pressure-text">高压</text></g>
      <Arrow d="M730 500 C900 480 1070 480 1255 500" color="#226fb2" show={surface} dash={dash} label="近地面：海洋 → 陆地" labelX={790} labelY={450}/>
      <g opacity={surface}><rect x="895" y="550" width="240" height="75" rx="37" className="breeze-pill"/><text x="1015" y="599" textAnchor="middle" className="breeze-text">海 风</text></g>
      <Arrow d="M1380 180 C1160 92 900 105 675 200" color="#7252c7" show={upper} dash={dash} label="高空：陆地 → 海洋" labelX={875} labelY={92}/>
      <Arrow d="M675 200 C610 285 590 385 620 485" color="#7252c7" show={closure} dash={dash} label="空气下沉" labelX={430} labelY={330}/>
      <g opacity={closure}><path d="M620 485 C650 500 685 505 730 500" fill="none" stroke="#fff" strokeWidth="23" opacity=".65"/><path d="M620 485 C650 500 685 505 730 500" fill="none" stroke="#7252c7" strokeWidth="14" markerEnd="url(#arrow-7252c7)"/><rect x="785" y="265" width="340" height="72" rx="24" className="loop-card"/><text x="955" y="311" textAnchor="middle" className="loop-text">闭合的热力环流</text></g>
      <g opacity={s===4?1:0}><circle cx="955" cy="420" r="255" fill="none" stroke="#ffffff" strokeWidth="2" opacity=".12"/></g>
    </svg>
    <div className="cause-strip">
      {['陆地升温快','暖空气上升','地面低压','海风吹向陆地','高空返回海洋'].map((x,i)=>{const thresholds=[70,185,290,400,620],active=ease(f,thresholds[i],thresholds[i]+35),visible=f>=thresholds[i]-8;return visible?<React.Fragment key={x}><div className="cause" style={{opacity:active,transform:`translateY(${(1-active)*12}px)`}}><span>{i+1}</span>{x}</div>{i<4&&f>=thresholds[i+1]-8?<div className="cause-arrow" style={{opacity:active}}>→</div>:null}</React.Fragment>:null})}
    </div>
    <div className="subtitle"><span>{subtitle}</span></div>
  </AbsoluteFill>;
};
