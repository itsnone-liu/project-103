# PATTERNS.md — Pattern Library v1 API（模型必读）

patterns.js 在引擎之后、场景之前加载。所有原语 t-无状态：每帧用 shot 局部时间
调用。szebra空间原语（标注 ⛶）必须在 `camEnd()` 之后调用。
完整裁决依据见 PATTERN_CORPUS.md（七源语料）。v1 新增原语标 🆕。

## 文字层（引擎原生）

引擎自带 `letter(txt, x, y, size, color, o)` / `sfx(txt,x,y,size,color,age,o)` /
`flushLetters()`：相机内自动投影（世界坐标直接传），默认顶层合成；若后续有
iris/wipe 要盖住文字，shot 尾部调用 `flushLetters()`。字为手写体（Permanent
Marker/Comic Sans），带墨影偏移。指南要求"少用文字"——教学动画的数字/结论是
正当例外，装饰性大段文字禁止。

## 时序/事件类

```js
freezeFrame(lt, {at, dur=.6, x, y, flash=true, ring=true})   // FREEZE_EVENT
```
关键瞬间时间门，shot 开头调用一次，全部绘制用返回值 ft。教学证据强（"到最值
处停下闪一下"）；永动展示场景弱。

```js
hold(lt, at, dur)                                            // HOLD
anticipation(t, {t0, windup=.3, strike=.15, settle=.5})      // ACCELERATE_AND_SETTLE
settle(t, t0, {amp=.25, decay=9, freq=30})        🆕         // 落地弹簧 → sq/dy
squash(k, amt=.6)                                 🆕         // VOLUME_SQUASH → scale 对
pushIn(t, {t0, t1, from=1, to=1.12, geo})         // CAMERA_PUSH（geo=true 指数推近）
staggerReveal(lt, n, {at, gap=.12, dur=.4})       // STAGGER_REVEAL
beatCfg(bpm, off=0) / beatAt(n) / pulseBeat(t,n,{k=6}) 🆕    // BEAT_GRID 节拍钟
shake(t, t0, {amp=12, decay=6})                   🆕         // SHAKE → [dx,dy] 加进 camBegin
narr(starts)                                      🆕         // NARRATION_ANCHOR
```
`narr` 返回 `{at(k,f), win(k), k(t)}`：一切时刻锚定"第 k 句旁白"，动作窗取句内
15%-80%，绝不写死秒数。

## 轨迹/强调类

```js
tracePath(samples, lt, {mode='dots'|'line', tail, col, bg, every, size})  // TRACE_PATH
dimOthers(x,y,w,h,k=.55,col)  ⛶                                  // EVENT_EMPHASIS
pulseRing(x,y,k,{r0,r1,col,double})                              // EVENT_EMPHASIS
impactBurst(x,y,t,t0,{n=10,g=1400,col,v0,spread,size,life})   🆕 // IMPACT_BURST 确定性碎片
arcThrow(t,t0,t1,a,b,{h=200,accel}) → [x,y,p]                 🆕 // ARC_TOSS 抛物线(p 转速)
ideaBurst(x,y,t,t0,{n=7,r0,r1,col,dist,spread})               🆕 // 灵感:glow+错峰星扇
```

## 教学 widget 类 ⛶（全部屏幕空间）

```js
label(txt,x,y,size,{col,align,rot,alpha})                     🆕 // LIVE_ANNOTATION 基础
countUp(t,t0,t1,a,b,x,y,{dec,unit,col,size})                  🆕 // 数字从 a 数到 b
liveReadout(x,y,[[名,值],...],{w,lh,size,valCol})              🆕 // 实时读数面板
stampAnswer(txt,x,y,t,t0,{col,w,h,size,rot})                   🆕 // STAMP_ANSWER 盖章确认
highlightBox(x,y,w,h,k,{col})                                  🆕 // 框选条件（角标先行）
beforeAfter(lt, {at,y,w,ticks,span,unit,numbers,title,rows:[{col,from,to,fromVal,toVal,dash}]})
```
beforeAfter 是标准收尾：刻度尺+双色行程条+数字标注。

## 几何标记/证明类 🆕（世界坐标，camBegin 内）

```js
markRight(x,y,s,{col,dot})        // LEAVE_MARK 直角符号
markTicks(a,b,n,{col})            // n 等分刻度
markParallel(x,y,s,{col})         // 平行箭头对
markAngle(x,y,r,p0,p1,{k,col,fill}) // 角弧+扇形(k 动画扫描); p0/p1 = 边上的点[x,y]或弧度数字(两种都收)
superposeCopy(pts,dx,dy,rot,k,{col}) // SUPERPOSE_COPY 复制品叠合证明
```

## 角色与标记（kit）

```js
creature(x,y,s,{kind:'turtle'|'snail'|'ball', col, shell, walk, dir})  // s≈3.5u 匹配 clawd 体量
marker(x,y,s,{kind:'post'|'flag'|'finish', col})                       // s=杆高,揭示帧勿被遮挡
const ROLE = {known:'teal', ask:'rose', aux:'sap', hi:'sun'}  🆕        // COLOR_BIND
roleCol(r)                                                             // known蓝/ask红/aux绿/hi黄
```

## 标注规则（对齐 lint 依赖）

每处实现某 pattern 的代码段前写 `// PATTERN: NAME`（与分镜 `[PATTERN: X]` 同拼写）。
词表外表达：分镜写 `[CUSTOM: 描述]`，代码写 `// PATTERN: CUSTOM:名字`。
词表即本文档全部原语名；组合优先于新增。
