
<!-- BACKLOG.MD GUIDELINES START -->
<!-- backlog.md-instructions-version: 1.55.3 -->
<CRITICAL_INSTRUCTION>

## Backlog.md Workflow

This project uses Backlog.md for task and project management.

**At the beginning of each conversation in this project, run `backlog instructions overview` before answering or taking action. Re-read it only if you have not read it yet in the current conversation.**

Use the overview to decide whether to search, read, create, or update Backlog tasks.

Before task lifecycle actions, read the matching detailed guide:
- `backlog instructions task-creation` before creating or splitting tasks
- `backlog instructions task-execution` before planning, changing status or assignee, adding a plan or implementation notes, or implementing task work
- `backlog instructions task-finalization` before checking acceptance criteria, writing final summaries, or moving tasks to terminal statuses

Use `backlog <command> --help` before running unfamiliar commands. Help shows options, fields, and examples.

Do not edit Backlog task, draft, document, decision, or milestone markdown files directly. Use the `backlog` CLI so metadata, relationships, and history stay consistent.

</CRITICAL_INSTRUCTION>
<!-- BACKLOG.MD GUIDELINES END -->

---

## 课件进度台账、网盘归档与 GitHub 同步（强制）

本项目以 `课程课件完成情况台账_v1.md` 和 `课程课件完成情况台账_v1.csv` 为课程课件进度的**唯一事实源**。

**分工固定：**
- **GitHub 只提交进度更新**：台账 MD/CSV、工作流程文档、必要的轻量文本说明。
- **结果文件走网盘**：DOCX、PDF、PPTX、MP4、PNG/JPG/SVG 配图、图表包、交付压缩包等，统一归档到百度网盘，不提交 GitHub。
- **当前网盘归档范围：仅《设计基础》需要更新**。其他课程暂不重新上传，按既有网盘归档状态核对即可；后续范围变化以用户明确指令为准。

每门课程完成任一阶段性任务后，必须在同一工作回合内：

1. 更新 `课程课件完成情况台账_v1.md`：对应课程行、总览数字、视频专项表、归档状态、变更记录、文件头日期。
2. 同步更新 `课程课件完成情况台账_v1.csv`。
3. 只按文件系统中真实存在、可打开的产物记账，不按目录名、计划或口头描述推断完成度。
4. 按当前范围把结果文件归档到百度网盘；现阶段只要求《设计基础》更新，其他课程不强制重传。在台账中记录网盘路径/归档状态。未按范围归档的结果文件不得标记为“已交付”。
5. 只提交进度类文件：
   - `git add 课程课件完成情况台账_v1.md 课程课件完成情况台账_v1.csv <本次更新的流程文档>`
   - **不要** `git add` DOCX/PDF/PPTX/MP4/配图/结果压缩包。
   - 提交信息格式：`course(<课程名>): <阶段> — 更新课件台账`
   - 示例：`course(商业空间设计): 教师手册12章回填 — 更新课件台账`
6. 执行 `git push origin main`。未成功 push 的，不得把该阶段标记为“GitHub 已同步”；push 失败须在台账“变更记录”中写明阻塞原因。
7. 阶段性任务包括：读本批次、教师手册、配图批次、视频批次/收官、随堂测验、考试大纲、样卷、题库、lab/章测、正式交付。

> 该要求是课程生产流程门禁，不是可选的收尾动作。详细流程见 `课程生产框架_v1.md` 第 7 节。
