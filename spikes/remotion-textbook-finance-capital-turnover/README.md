# 资金周转率教学视频

Project 103 LessonVideo 实际制作，参照既有“存货周转率”成片的财务分析工作台风格。

## 内容来源

教学内容以[百度百科“资金周转率”移动页](https://wapbaike.baidu.com/item/资金周转率/10076554)公开正文为主，详见 `source.md`。桌面页面在生产环境返回 403，因此使用移动页内嵌结构化正文核验。

特别处理了词条本身的口径歧义：

- 主例题沿用百科原数：4000 万÷2000 万＝2 次/年；每次 180 天，隐含 360 天口径；
- 区分全部资金周转率、百科所称固定/流动资金周转率与营运资金周转率；
- 同时呈现信息框“越高越好”和正文“无通用标准、过高可能资本不足”的冲突，不机械评价。

## 产物

- `source.md`：百科来源与规范化内容
- `lesson-brief.md`：教学目标、误区防护和视觉分工
- `storyboard.md`：9 场景镜头设计
- `narration.txt`：中文普通话旁白
- `final/public/audio/narration.mp3`、`narration.vtt`：Edge TTS 音频与时间字幕
- `final/src/`：Remotion React/TypeScript 实现
- `final.mp4`：最终成片
- `representative.png`：代表帧
- `review.md`：内容、视觉和媒体审查
- `usage.json`：可审计用量记录

## 构建

```powershell
cd final
npm install
npm run typecheck
npm run render
npm run still
```

规格：1920×1080、30fps、8400 帧（280 秒）。实际旁白约 277.44 秒，尾部保留约 2.5 秒静止。画面底部使用按教学场景压缩后的摘要字幕；`narration.vtt` 保留 Edge TTS 输出的完整逐句时间文本。
