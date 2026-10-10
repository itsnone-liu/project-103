# 岁添一枝春 · 103 OPEN / ASSISTED 对照实验

用户确认：古韵生日含义、唯一画面文字「岁岁欢喜，年年胜意」、墨滴洇开→梅枝生长→朱砂红梅绽放、纸墨音效、仅 MP4、不调用付费视频生成模型、不加古琴/歌曲/人名。

输出预设：单镜 12s、1280×720、24fps；固定汉字逐字核对；同一画面同一音轨，只改变成功案例可见性。OPEN 臂只收上述 brief 和技术契约，不读取 `knowledge/success-cases`；ASSISTED 臂另收到 `knowledge/success-cases/EXTERNAL-moyun-living-rice-paper-2026-10.md`，仅参考、可拒绝，不锁 WebGL，也不照抄作者构图。两臂手工实现/编码时如开发者、模型、迭代时间不匹配，**仅是探索性对照，不能宣称知识库带来因果提升**。本次不是原生 `--mode assisted`，因为该 flag 尚不加载案例；实验通过将知识卡显式注入 ASSISTED 设计输入来保证两组输入有差别。

运行产物各置 `runs/moyun-birthday/{open,assisted}/`（Git 忽略），源码置 `experiments/moyun-birthday/{open,assisted}/index.html`；同一 deterministic `paper_ink.wav` 轨复用到两组。审核：对比首/中/末抽帧；全分辨率检查字体、笔画、标点；ffprobe 核时长/帧率/音轨；复渲同一 t 比像素，禁止网络依赖；反查两臂代码仅源于各自输入。不要将本次候选结果自动升格为全局规范。
