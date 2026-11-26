---
id: TASK-19
title: 线上实践lab全流程
status: Done
assignee: []
created_date: '2026-11-21T12:07:00Z'
updated_date: '2026-11-26T06:01:00Z'
labels: []
milestone: m-3
dependencies: []
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
线上实践lab全流程。注：理论型课程此件为章节测验（如现代设计史）；本课为实践型。
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 lab单元设计
- [x] #2 可挂载可提交
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

做到哪：15 张实验卡（DSS-L01…L15，14 章＋附录综合）按 lab-submit-v1 统一契约落地，QA 双路径 15/15 FAIL 0，挂载 /dsslab/ 与 /labs.html；线上实践 48 件已归档网盘。\n下一步：视频片尾任务卡可与对应实验卡互链。\n坑在哪：进度徽标只能由 lab_submit.js 写，dss_engine.js 再写会互相覆盖；卡片视频链接是百分号编码，内容审计要先 unquote。

---
<!-- COMMENTS:END -->
