---
id: TASK-20
title: 设计基础视频课件：分段、种子段与种子视频
status: Done
assignee: []
created_date: '2026-11-26T07:21:00Z'
updated_date: '2026-11-26T08:35:00Z'
labels: []
dependencies: []
priority: high
type: feature
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
设计基础已完成读本、教师手册、83幅配图与考务三件套，现按103视频生产流程启动视频课件。先产出全课分段方案，选定可验证主镜头语言的种子段，完成参考库调研，再用103管线（storyboard→TTS→decide→codegen→render→QA→repair→mux）做出可审阅的种子视频。结果文件不上GitHub，种子视频按流程归档网盘；考务材料仍按用户要求暂缓上传。
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 分段方案覆盖12章与绪论/案例专题，含段名、类型、锚点、时长与字数预算
- [x] #2 种子段有明确选择理由与验收门禁
- [x] #3 参考库含本地模板、外部参考与采/不采判断
- [x] #4 种子视频产出final mp4，通过时长、音画、抽帧QA
- [x] #5 台账MD/CSV与GitHub进度提交完成；结果文件不提交GitHub
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 网盘manifest上传完成且SHA256校验通过（用户明确豁免时在任务comment记录）
- [x] #2 交接comment三行：做到哪/下一步/坑在哪
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. 读取设计基础读本结构与既有课程分段/种子样板；2. 写设计基础视频分段方案与参考库；3. 选定种子段并写topic；4. 用103管线做storyboard→TTS→decide→codegen→render→QA；5. 修复至过门禁；6. 更新台账、工作记录并push。
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-26 种子1完成。做到哪：分段方案、参考库、profile、dsb-2-03 topic/storyboard/code/成片落地；320.50s、54句、1548字，TTS audit PASS、QA PASS，MP4与验收记录已归档网盘种子1目录，SHA256一致。下一步：用户审片，确认后做种子2 dsb-5-05，再决定批产。坑在哪：6—7座要写清向下取整；7人/7次口径统一；教材图整页缩图不可读，要裁到关键流程；render缺教材图资源会报ASSET_MISSING。
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
完成设计基础视频课件第一阶段：56段分段方案、参考库、design-basic profile、种子1 dsb-2-03 全链成片。成片320.50s、54句、1548字，TTS audit PASS、QA PASS、blank_frames=0；修正6—7座取整、7人/7次口径、教材图裁切。MP4+验收记录已归档网盘种子1目录，SHA256一致；GitHub提交7c19124与564b176，仅进度文档。下一步待用户审片，再决定种子2 dsb-5-05与批产。
<!-- SECTION:FINAL_SUMMARY:END -->
