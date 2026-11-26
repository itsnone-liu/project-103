---
id: TASK-18
title: 题库
status: Done
assignee: []
created_date: '2026-11-21T12:07:00Z'
updated_date: '2026-11-26T06:01:00Z'
labels: []
milestone: m-2
dependencies: []
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
自动迁移自backlog.md欠账本
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 题库覆盖考纲
- [x] #2 抽样答案可从教材定位
- [x] #3 网盘manifest
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 网盘manifest上传完成且SHA256校验通过（用户明确豁免时在任务comment记录）
- [x] #2 交接comment三行：做到哪/下一步/坑在哪
<!-- DOD:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-11-26T06:01:00Z

---

做到哪：题库_v1.md 306 题/15 池（14 章×21＋附录 12），_build_qbank.py 校验 0 问题：题型数、编号唯一、选项答案自洽、标准号全部命中教材原文、无终局结论句式。\n下一步：把多选选项数在 4/5 之间统一，再按平台导入格式导出。\n坑在哪：多选答案写法有 A、B、C 与 ABC 两种、判断题有 √/× 与 正确/错误 两种，合并时必须归一化，否则校验会假失败。

---
<!-- COMMENTS:END -->
