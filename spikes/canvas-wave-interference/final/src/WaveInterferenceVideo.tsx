import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Easing,interpolate,staticFile,useCurrentFrame} from 'remotion';
import './style.css';

const FIELD={x:74,y:176,w:1772,h:736};
const BUFFER={w:480,h:270};
const S1={x:0.36,y:0.53},S2={x:0.64,y:0.53};
const LAMBDA=0.105;
const FPS=30;
const ease=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const scene=(f:number)=>f<240?1:f<510?2:f<810?3:f<1140?4:f<1440?5:6;
const cues=[
 {a:0,b:240,text:'水面上的一个点源周期振动，会把圆形波纹不断向外送出。'},
 {a:240,b:510,text:'现在加入同频、同相的第二个波源。两组波都继续传播，并不是碰到后停下来。'},
 {a:510,b:810,text:'画面中的每一个位置，都同时接收到两列波。程序计算两项正弦，再把位移相加。'},
 {a:810,b:1140,text:'P 点到两个波源等远，路程差为零，两列波同相到达：峰遇峰，谷遇谷，振幅增强。'},
 {a:1140,b:1440,text:'Q 点的路程差多出半个波长，两列波反相到达，合振幅持续很小。'},
 {a:1440,b:1800,text:'记录每个位置能达到的最大振幅，就得到稳定条纹。波仍在传播，稳定的是增强区和削弱区。'}
];

const fieldPoint=(p:{x:number,y:number})=>({left:FIELD.x+p.x*FIELD.w,top:FIELD.y+p.y*FIELD.h});
const P={x:0.50,y:0.25}; // perpendicular bisector: Δr = 0 = 0λ
const Q={x:0.45,y:0.22}; // first nodal curve: |r1-r2| ≈ λ/2

const WaveCanvas:React.FC<{frame:number}>=({frame})=>{
 const ref=useRef<HTMLCanvasElement>(null);
 useLayoutEffect(()=>{
  const canvas=ref.current;if(!canvas)return;
  const ctx=canvas.getContext('2d');if(!ctx)return;
  const img=ctx.createImageData(BUFFER.w,BUFFER.h);const d=img.data;
  const s2Mix=ease(frame,220,310);const envelopeMix=ease(frame,1450,1580);
  const t=frame/FPS;const omega=Math.PI*2*0.78;const k=Math.PI*2/LAMBDA;
  for(let py=0;py<BUFFER.h;py++){
   const y=py/(BUFFER.h-1);
   for(let px=0;px<BUFFER.w;px++){
    const x=px/(BUFFER.w-1);
    const r1=Math.hypot(x-S1.x,(y-S1.y)*0.72);const r2=Math.hypot(x-S2.x,(y-S2.y)*0.72);
    const front1=clamp((t*0.21-r1+0.08)/0.055);const front2=clamp(((t-7.5)*0.21-r2+0.08)/0.055)*s2Mix;
    const a1=Math.sin(k*r1-omega*t)*front1;
    const a2=Math.sin(k*r2-omega*t)*front2;
    const instant=(a1+a2)/(1+s2Mix);
    const env=Math.abs(2*Math.cos(k*(r1-r2)/2))/2;
    const mag=Math.min(1,Math.abs(instant));
    let ir=8,ig=22,ib=34;
    if(instant>=0){ir+=Math.round(238*mag);ig+=Math.round(151*mag);ib+=Math.round(58*mag);}else{ir+=Math.round(34*mag);ig+=Math.round(118*mag);ib+=Math.round(204*mag);}
    const er=10+Math.round(238*env),eg=22+Math.round(184*env),eb=34+Math.round(58*env);
    const r=Math.round(ir*(1-envelopeMix)+er*envelopeMix);
    const g=Math.round(ig*(1-envelopeMix)+eg*envelopeMix);
    const b=Math.round(ib*(1-envelopeMix)+eb*envelopeMix);
    const i=(py*BUFFER.w+px)*4;d[i]=Math.min(255,r);d[i+1]=Math.min(255,g);d[i+2]=Math.min(255,b);d[i+3]=255;
   }
  }
  ctx.putImageData(img,0,0);
 },[frame]);
 return <canvas ref={ref} width={BUFFER.w} height={BUFFER.h} className="field"/>;
};

const Source:React.FC<{p:{x:number,y:number};name:string;second?:boolean;opacity?:number;frame:number}>=({p,name,second,opacity=1,frame})=>{const q=fieldPoint(p);const scale=1+0.14*Math.sin(frame/FPS*Math.PI*2*0.78);return <><div className={`source ${second?'s2':''}`} style={{left:q.left,top:q.top,opacity,transform:`scale(${scale})`}}/><div className="source-label" style={{left:q.left,top:q.top,opacity}}>{name}</div></>};

export const WaveInterferenceVideo:React.FC=()=>{
 const f=useCurrentFrame(),s=scene(f),s2=ease(f,220,310),formula=ease(f,520,585),grid=ease(f,560,640)*(1-ease(f,735,800));
 const p=fieldPoint(P),q=fieldPoint(Q),focusP=ease(f,800,850)*(1-ease(f,1110,1140)),focusQ=ease(f,1130,1180)*(1-ease(f,1410,1440)),env=ease(f,1450,1580);
 const subtitle=cues.find(c=>f>=c.a&&f<c.b)?.text??'';
 const titles=['一个波源：圆形波向外传播','第二个波源加入：两列波继续传播','每一点，都在计算两列波的和','P 点：同相到达，振幅增强','Q 点：反相到达，振幅削弱','从瞬时波场，看见稳定干涉条纹'];
 return <AbsoluteFill className="video">
  <Audio src={staticFile('audio/narration.mp3')}/>
  <WaveCanvas frame={f}/>
  <div className="topbar"><div className="chip">物理 · 波的干涉</div><div className="progress"><i style={{width:`${f/1799*100}%`}}/></div><div className="counter">{s}/6</div></div>
  <div className="headline"><h1>{titles[s-1]}</h1><div className="question">同频 · 同相 · 线性叠加</div></div>
  <div className="legend"><div className="legend-title">瞬时水面位移</div><div className="gradient"/><div className="legend-labels"><span>波谷</span><span>平衡</span><span>波峰</span></div></div>
  <Source p={S1} name="S1" frame={f}/><Source p={S2} name="S2" opacity={s2} frame={f}/>
  {grid>0&&<div className="grid-overlay" style={{opacity:grid}}/>}
  {formula>0&&s===3&&<><div className="formula-card" style={{opacity:formula}}><div className="formula">A(x,y,t) = sin(kr₁−ωt) + sin(kr₂−ωt)</div><div className="formula-note">每个采样点：量距离 → 算相位 → 做加法</div></div><div className="sample-stat" style={{opacity:formula}}><strong>{BUFFER.w} × {BUFFER.h} = {(BUFFER.w*BUFFER.h).toLocaleString()}</strong> 个采样点 / 帧</div></>}
  {(focusP>0||focusQ>0)&&<svg className="route-svg" viewBox={`0 0 ${FIELD.w} ${FIELD.h}`}><g opacity={focusP}><line x1={S1.x*FIELD.w} y1={S1.y*FIELD.h} x2={P.x*FIELD.w} y2={P.y*FIELD.h} stroke="#ffda66" strokeWidth="4" strokeDasharray="14 12"/><line x1={S2.x*FIELD.w} y1={S2.y*FIELD.h} x2={P.x*FIELD.w} y2={P.y*FIELD.h} stroke="#ffda66" strokeWidth="4" strokeDasharray="14 12"/></g><g opacity={focusQ}><line x1={S1.x*FIELD.w} y1={S1.y*FIELD.h} x2={Q.x*FIELD.w} y2={Q.y*FIELD.h} stroke="#ff7598" strokeWidth="4" strokeDasharray="14 12"/><line x1={S2.x*FIELD.w} y1={S2.y*FIELD.h} x2={Q.x*FIELD.w} y2={Q.y*FIELD.h} stroke="#ff7598" strokeWidth="4" strokeDasharray="14 12"/></g></svg>}
  {focusP>0&&<><div className="point p" style={{left:p.left,top:p.top,opacity:focusP}}/><div className="point-tag" style={{left:p.left,top:p.top,opacity:focusP}}>P</div><div className="explain-card" style={{opacity:focusP}}><h2>P：Δr = 0 = 0λ <span className="badge">整数倍波长</span></h2><p>两列波保持同相：峰遇峰，谷遇谷。</p><div className="phase-bars"><span>S1 到达</span><i className="wavebar"/><span>S2 到达</span><i className="wavebar gold"/></div><div className="result good">合振幅更大 → 相长干涉</div></div></>}
  {focusQ>0&&<><div className="point q" style={{left:q.left,top:q.top,opacity:focusQ}}/><div className="point-tag" style={{left:q.left,top:q.top,opacity:focusQ}}>Q</div><div className="explain-card" style={{opacity:focusQ}}><h2>Q：Δr ≈ λ/2 <span className="badge">第一条相消线</span></h2><p>两列波反相：一列向上时，另一列向下。</p><div className="phase-bars"><span>S1 到达</span><i className="wavebar"/><span>S2 到达</span><i className="wavebar gold anti"/></div><div className="result cancel">合振幅持续很小 → 相消干涉</div></div></>}
  {s===6&&<><div className="mode-card">{env<.5?'瞬时位移：每一帧都在变化':'振幅包络：亮 = 增强，暗 = 削弱'}</div><div className="final-card" style={{opacity:ease(f,1570,1630)}}>干涉条纹 = 两个传播中的波，在每一点持续叠加后的振幅分布</div></>}
  <div className="subtitle"><span>{subtitle}</span></div>
 </AbsoluteFill>;
};
