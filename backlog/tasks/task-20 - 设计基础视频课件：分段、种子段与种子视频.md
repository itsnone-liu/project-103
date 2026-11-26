---
id: TASK-20
title: 设计基础视频课件：分段、种子段与种子视频
status: In Progress
assignee: []
created_date: '2026-11-26T07:21:00Z'
labels: []
dependencies: []
priority: high
type: feature
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
设计基础已完成读本、教师手册、83幅配图与考务三件套，现按103视频生产流程启动视频课件。先产出全课分段方案，选定可验证主镜头语言的种子段，完成参考库调研，再用103管线（storyboard→TTS→decide→codegen→render→QA→repair→mux）做出可审阅的种子视频。结果文件不上GitHub，按用户指示暂不上网盘。
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 分段方案覆盖12章与绪论/案例专题，含段名、类型、锚点、时长与字数预算
- [ ] #2 种子段有明确选择理由与验收门禁
- [ ] #3 参考库含本地模板、外部参考与采/不采判断
- [ ] #4 种子视频产出final mp4，通过时长、音画、抽帧QA
- [ ] #5 台账MD/CSV与GitHub进度提交完成；结果文件不提交GitHub
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 网盘manifest上传完成且SHA256校验通过（用户明确豁免时在任务comment记录）
- [ ] #2 交接comment三行：做到哪/下一步/坑在哪
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. 读取设计基础读本结构与既有课程分段/种子样板；2. 写设计基础视频分段方案与参考库；3. 选定种子段并写topic；4. 用103管线做storyboard→TTS→decide→codegen→render→QA；5. 修复至过门禁；6. 更新台账、工作记录并push。
<!-- SECTION:PLAN:END -->
