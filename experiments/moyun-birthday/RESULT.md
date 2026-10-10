# 岁添一枝春 · 双臂探索实验结果

状态：2026-10-09 本地两组 MP4 已生成并通过结构检查；用户已审片反馈「效果不错。文字多了逗号，音效看来还是琴音更好。不用改了，沉淀。」**按要求不修改两版成片**，细节反馈留待下一次类似制作参考，见 `knowledge/success-cases/PROJECT-moyun-birthday-user-review-2026-10.md`。依据 `brief.md` 当时确认的分镜/祝词/纸墨音效。**无 Runway、ComfyUI、付费视频模型调用；代码动画使用既有 WEB_2D 适配器**。

| 组别 | 可打开的本地成片 | 设计输入 | 输出 |
|---|---|---|---|
| OPEN | `runs/moyun-birthday/open/out/birthday_open.mp4` | `brief.md`，不含外部知识卡 | 12.000s，1280×720，24fps，288帧，H.264 + AAC |
| ASSISTED | `runs/moyun-birthday/assisted/out/birthday_assisted.mp4` | 相同 `brief.md` + `knowledge/success-cases/EXTERNAL-moyun-living-rice-paper-2026-10.md`（reference only） | 同上 |

复现入口：`python experiments/moyun-birthday/preflight.py` → `python experiments/moyun-birthday/sound.py`（默认写 experiments 下，正式共享音轨需用 `sound.create(ROOT/runs/moyun-birthday/paper_ink.wav)`）→ `python experiments/moyun-birthday/render.py open assisted` → `python experiments/moyun-birthday/verify.py open assisted`。本地音轨 `runs/moyun-birthday/paper_ink.wav` 的 SHA-256 `121555a4f88d5fad749467d2b93749fdecc4b24a3ab52ed10900f29641e5fe59`；两臂同一音轨。源文件位于 `experiments/moyun-birthday/{open,assisted}/index.html`；产物在 Git 忽略的 runs 下，仅本机可访问。原片也在 gitignored `video_perception/runs/breathing_ink`。

验收事实：`preflight.py` PASS（知识卡隔离 + 精确文案 + 输出契约）；两片在最终重渲后各 288 帧，12.000s，AAC 音轨；`verify.py` 两组 structural PASS，前3个增长间隔的像素差均非零；独立 ffmpeg 从两片各解出11.2s PNG 和 AAC→WAV 均成功；全分辨率末帧外部视觉核查均读到完整「岁岁欢喜，年年胜意」、梅枝红花无遮挡且无黑边（OPEN 原始印章版本曾触发额外字疑虑，已删除印章再渲染确认）。pipeline 离线回归 23 PASS / 0 FAIL（含修改后的 viewport capture）。**结构和单帧核查不能代替人审完整动态和听觉效果。**

实验边界：两组由不同实施代理分别写码，实施路径/迭代努力不相同；ASSISTED 源码也未使用 Moyun 的 WebGL 算法，仅参考活宣纸/墨洇可能性。本次 n=1 探索性对照**不能从哪组更好推断知识库因果增益**；用户看完后可回填项目级候选经验，不自动升级全局规则。原生 `pipeline.produce --mode assisted` 仍无知识卡检索加载；本次显式设计输入是隔离实验，不宣称生产主路径已改造。
