# AUDIO.md — 103 音频管线（TTS 时序倒置 + 混音）

旁白不是后期配音，是**全片时钟**：先 TTS 实测时长，代码阶段的 `narr([...])`
表来自物理语音，动作窗（句内 15%-80%）落在真实念白上。

## 流程（5 步）

```
分镜 JSON (audio/scene_<name>.json, 逐句文案+锚点)
 1. python audio.py tts   scene.json   → 逐句 wav(剪头静音) + timing.json
                                          锚点贴合: anchor_start=开口时刻
                                          早到→垫拍等待; 迟到→5%阶梯加速(cap 30)
 2. python audio.py narration timing.json → narration.wav (adelay 对齐整轨)
 3. python audio.py audit narration.wav timing.json → silencedetect 反查 ±0.15s
 4. 渲染: config.duration = timing.total; 场景 narr(starts+total) 照抄
 5. python audio.py mux   video.mp4 timing.json → 成片
    (BGM 循环+0.13 电平+volume帧表达式淡入淡出; loudnorm -16 LUFS; aac 192k)
```

## 分镜 JSON 字段

```json
{"title":"patterns_demo2", "voice":"zh-CN-XiaoxiaoNeural",
 "bgm":{"file":"bgm/musicbox.wav","gain":0.13},
 "gap":0.25, "tail":1.8,
 "sentences":[{"text":"...","pause_after":0.25,"anchor_start":7.15,"rate_cap":30}]}
```

- `anchor_start`：该句**开口**时刻锚（数学事件对齐用——"七点二秒，相遇了！"
  锚 7.15，词落在 7.2 视觉相遇上）
- 锚前旁白预算按实测 **~3.5-4 字/秒** 反推文案长度（中文数字/英文词更贵）
- 说不过来就砍旁白，别砍数学：能交给 liveReadout/视觉说的就不念
  （demo2 把"差距缩小"交给 Δx 实时读数）

## BGM 曲库（bgm_gen.py 本地合成，BPM 构造精确）

| 曲目 | BPM | 情绪 | 适用 |
|---|---|---|---|
| musicbox | 100 | 轻快/讲解 | 默认 |
| plucky | 110 | 活泼/演示 | 过程演示 |
| calm | 70 | 沉静/总结 | 结论段 |

分镜选曲后 `beatCfg(曲目BPM)` → 视觉脉冲与音乐同拍。CC0（自己合成）。

## 已知约束（本机 ffmpeg 为 Remotion 精简版）

无 `afade`/`silenceremove`：淡入淡出用 `volume='min(1,t/x)*...'`:eval=frame，
头静音用 silencedetect 量出后 `-ss` 裁剪。滤镜图**标签后必须 `;` 分段**，
不能逗号续链。混流后 BGM 垫底 → silencedetect 失效，对齐审计必须在混流前做。

## 验证基线（2026-10-05）

patterns_demo2：5 句旁白全自然语速（0% 加速）、锚点全中
（"四秒时"↔C0=4.0、"七点二秒"↔MEET_T=7.2）、AUDIT PASS（+0.02~0.03s）、
成片 final_patterns_demo2.mp4 19.71s（视频 473 帧 + aac 立体声 + BGM）。
