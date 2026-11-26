---
id: TASK-15
title: 视频课件全流程（调研→种子→B1..B5→随堂测验→五件套）
status: Done
assignee: []
created_date: '2026-11-21T12:07:00Z'
labels: []
milestone: m-1
dependencies: []
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
自动迁移自backlog.md欠账本
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] 参考库调研
- [x] 种子制作（2段）
- [x] B1-B4全过线+网盘归档（32段）
- [x] B5全过线+五件套+manifest_b5（11段，含8-1/10-2历史幽灵修复）
- [x] 随堂测验嵌入44段视频（完成后中间件含TTS可清理）
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 网盘manifest上传完成且SHA256校验通过（用户明确豁免时在任务comment记录）
- [x] #2 交接comment三行：做到哪/下一步/坑在哪
<!-- DOD:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @agent
created: 2026-11-21T14:55:00Z

**2026-11-21 随堂测验收官（44/44），TASK-15全AC达成：**
- 做到哪：随堂测验题_v1.md 44题（单选26/简答18≈六四开）产出自 _labs/quiz_ijc.py（4批sol串行，BSD流程移植+插中段约束）；时间点全部落在视频40%–70%区间且经程序验证与口播句真实对齐（最大偏差0.1s=取整）；已归档 /apps/ss2archive/室内构造与材料学/随堂/（教师卷+manifest_suitang.json，DONE CLEAN）。至此 m-1 B视频线全结：44段成片五件套＋随堂题全部上网盘。
- 下一步：中间件清理（audio/ TTS、runs中间产物——用户已预授权"可清理"，待确认清单后执行）；A教材线TASK-14建议另开session（/name 103-A教材）。
- 坑在哪：①段名ca-1带连字符，assemble正则ca\d+漏收2段（已修ca-?\d+）；②时间点"不在句内"的12个实为MM:SS取整0.1s舍入，勿误判编造；③quiz依赖runs/*/out/final_*.ass——清理中间件时ass属五件套必须保留。

---
<!-- COMMENTS:END -->
