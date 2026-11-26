---
id: TASK-22
title: 移动UI交互设计：考务五件套＋12卡线上实践
status: Done
assignee: []
created_date: '2026-11-26T15:38:00Z'
updated_date: '2026-11-26T15:39:00Z'
labels: []
dependencies: []
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
按平台要求补齐《移动UI交互设计》考务与实验：考试大纲、样卷、答案、题库252题、随堂测验43题，以及12张单文件实验卡（含 COURSE_PRACTICE_SUBMIT 回传）。
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 考务五件套（大纲/样卷/答案/题库252/随堂43）落盘并通过一致性检查
- [x] #2 12 张实验卡构建完成，QA 12/12 通过（空卷≤1、样例全绿）
- [x] #3 三场景实测 12/12 通过（iframe+parentOrigin 回传 / iframe 不回传 / file:// 直开）
- [x] #4 台账与课程生产框架已更新；网盘归档待用户通知后执行
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 网盘manifest上传完成且SHA256校验通过（用户明确豁免时在任务comment记录）
- [ ] #2 交接comment三行：做到哪/下一步/坑在哪
<!-- DOD:END -->
