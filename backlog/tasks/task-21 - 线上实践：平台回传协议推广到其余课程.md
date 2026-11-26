---
id: TASK-21
title: 线上实践：平台回传协议推广到其余课程
status: To Do
assignee: []
created_date: '2026-11-26T08:16:00Z'
updated_date: '2026-11-26T08:16:00Z'
labels: []
milestone: m-3
dependencies: []
priority: high
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
平台技术认可《设计制图》的 COURSE_PRACTICE_SUBMIT 回传结果后，把同一契约推广到其余全部线上实践课程。门禁：未获平台书面/口头认可前不动手。
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 平台技术认可设计制图样板（origin 校验、resultHtml 入库、字段够用）
- [ ] #2 设计标准与规范 15 卡接入并 QA 全绿
- [ ] #3 商业空间设计 12 卡接入并 QA 全绿
- [ ] #4 室内空间设计：先补 8 张缺提交模块的卡，再 12 卡接入
- [ ] #5 每门课三场景实测：内嵌带 parentOrigin / 内嵌不带 / 直开 file://
- [ ] #6 网盘重传 + manifest 重建 + 逐字节 sha256 复核
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 网盘manifest上传完成且SHA256校验通过（用户明确豁免时在任务comment记录）
- [ ] #2 交接comment三行：做到哪/下一步/坑在哪
- [ ] #3 网盘manifest上传完成且SHA256校验通过（用户明确豁免时在任务comment记录）
- [ ] #4 交接comment三行：做到哪/下一步/坑在哪
<!-- DOD:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-11-26T08:16:00Z

---

【门禁】等平台技术认可设计制图样板（已交：12 卡内嵌回传，父页面收到 resultHtml 与下载文件字节一致，5.9 KB/卡）后再动其他课程。\n做到哪：仅设计制图 12/12 已接；设计标准与规范 15 卡、商业空间设计 12 卡未接；室内空间设计 12 卡中只有 L01/L04/L09/L12 有统一 exportReport，其余 8 卡连提交模块都没有。\n下一步：认可后按 共享模块改 postMessage → 跑注入器 → 三场景实测 → QA → 网盘重传 的顺序逐课推。\n坑在哪：① 12 卡是单文件 HTML，模块内联，必须用各课注入器重灌，手改必漂移；② 各课全局名不同（DRW/LAB…），postMessage 段要跟着改；③ 室内空间设计那 8 卡得先补提交模块，工作量比另两门大。

---
<!-- COMMENTS:END -->
