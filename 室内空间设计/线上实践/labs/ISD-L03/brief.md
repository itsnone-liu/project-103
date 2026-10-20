# ISD-L03 实现简报（sol 高推理单文件实现）

产出 `bubble_lab.html`：自包含 HTML（内联 CSS/JS，零依赖，file:// 与静态服务器均可运行）。本科生《室内空间设计》第2章配套实验：学生把**功能气泡**装进 U90 冻结房间的槽位、在气泡间连**五档邻接边**并挂**证据标签**，引擎做白盒逻辑检查（面积超载/时段冲突/三角张力/区带错配/访谈覆盖/平面对表），A/B 两情境各存一版、写失效条件、导出"气泡图任务书"。**引擎永不生成平面、永不合成总分**。

## 0 全局纪律（违反即废）

1. 确定性：同一 state JSON → 同一 report JSON。无 Date.now/Math.random 参与计算。
2. 纯函数引擎 `window.BubbleEngine`（evaluate/baseline/change/move/fill/addEdge/serialize/deserialize 等），渲染层只调用。
3. 三层反馈分列：观察（客观测量）/ 规则建议（前缀"教学常用值·讨论工具"）/ 教师判断（静态）。页面显著标注"全部为教学假设/课堂讨论工具，非国家标准"。
4. UI 全简体中文，Microsoft YaHei，字号≥12px。教材制图风：白底、黑线框、分区浅色填充。
5. 代码紧凑：CSS≤4k，JS 短命名+共享 helper，分节注释。总文件目标≤56k 字符。
6. 所有冻结数据照抄 lab.yaml，不得改动或"顺手优化"数值。

## 1 数据常量（照抄）

### 1.1 气泡目录（19 个）
`{id,name,area,zone,slots(允许槽),periods[[起,止]],day,scenario?,fixed?}` 全表见 lab.yaml `bubbles`。要点：sleep_elder(5.5,私,21–6.5,每日,仅情境B)、care_elder(1.5,公,9–11/14–16,每日,仅B)、work_office(4,私,9–12/14–18/20–22,工作日)、work_office_w(4,私,14–19,周六)、cook(3,家务,11.5–12.5/17.5–18.5,每日)、bake(1.5,家务,10–12,周六)、meal_break(2,公,7–7.5,每日)、meal_dinner(3.5,公,18–19,每日)、work_prep(2.5,半私,19–21,每日)、tv_eld(2.5,公,13–14/19–21,每日)、guest(3,公,15–17,周六)、play(2.5,公,15–16,每日)、study_child(2,半私,16.5–17.5/19–20,每日)、sleep_child(5,私,20.5–7,每日)、sleep_master(8,私,22–7,每日)、laundry(2,家务,9–10,周六)、storage_bulk(4,家务,无时段)、bath_main(3.8,私,fixed 装在 bath_main_slot)、bath_pub(4.4,共用,fixed 装在 bath_pub_slot)。时段跨午夜（21–6.5）按 21–24 与 0–6.5 两段处理重叠；day 不同（工作日 vs 周六）不算重叠，但"每日"与任何 day 都同日。

### 1.2 房间槽（11 个）
kitchen 厨房6.3家务 / dining 餐区西厅(开放)9.5公 / living 客餐厅核心29.8公 / entry 玄关3.0过渡 / study 书房8.7私 / master 主卧13.9私 / child 儿童房9.6私 / storage 储物家政区(开放)6.1家务 / balcony_n 北阳台2.0家务 / bath_main_slot 主卫(套内)3.8私 / bath_pub_slot 公卫4.4共用。bath 两槽已由 fixed 气泡占用、不可拖出。

### 1.3 邻接事实表 slot_relations（22 对，见 lab.yaml；未列出的槽对 = far(1)）
等级：same_room 5 / open_adjacent 4 / door_adjacent 4 / corridor_near 3 / adjustable_wall 3 / fixed_wall 2 / far 1。

### 1.4 对表判据 claim_vs_actual
+2 需≥4；+1 需≥3；0 恒过；−1 需≤2；−2 需≤1。差1级=部分满足，差≥2级=不满足；边端点任一未装填=无法对照。输出逐边 {a,b,v,evidence,actualLevel,relationName,verdict}。

### 1.5 访谈要点 interview_points（14 条 ip1–ip14，need 列表见 lab.yaml）
覆盖规则见 lab.yaml coverage_rule：need 项=气泡已装填 或 指定边(a,b,v)存在；need 引用当前情境不存在的对象=留待情境B；全部就绪=覆盖；否则未覆盖。注意 ip 中的边 need 匹配时 v 必须相等、a/b 无向。

### 1.6 现状基线（关卡1 初始 state）
装填 current_fill_A、边 current_edges_A（6 条，见 lab.yaml），scenario=A。载入后引擎应报：0 面积超载；恰好 1 对时段冲突（play↔guest 15–16 周六 living）；对表中 sleep_master+2bath_main 满足；ip1/ip2/ip3 部分留待情境B、其余覆盖。

### 1.7 情境切换
A→B：托盘新增 sleep_elder、care_elder 气泡与预置边 sleep_elder+2bath_pub(访谈)（边直接加入图中，学生可改）；B→A：这两项移除。切换不清空学生已有装填/边。情境B_delta 检查 = 重算后与 A 版报告对比，列出新增冲突/超载/未覆盖。

## 2 引擎检查（纯函数，输出进 report.checks）

1. `area_overload`：每槽 sum(气泡area) > capacity×1.05 → {slot, used, capacity, ratio}。bath 槽不检（fixed）。
2. `time_conflict`：同槽、同日（每日∩任意=同日）、时段重叠、不同气泡 → {slot,a,b,overlap段,day}。play(每日)×guest(周六) 在周六冲突必须能检出。
3. `triangle_tension`：对气泡三点组，若存在边集使 |最高档−最低档|≥4 且含至少一正一负 → {triple:[a,b,c],edges}。构造样例 A+2B,B+2C,A−2C 必须命中。
4. `zone_mismatch`：气泡zone vs 槽zone：私∈{公,家务,过渡} 或 公∈{私} → 红；半私∈{家务} → 黄。bath fixed 不检。
5. `coverage`：14 条 ip 逐条 {id,text,status:覆盖|留待情境B|未覆盖,need状态}。
6. `table_check`：每条边对表（1.4 规则）。
7. `scenario_delta`：仅当 scenario=B：与"同 state 去掉 B 新增项"的 A 视图报告 diff 新增冲突/超载/未覆盖。
8. `summary`：counts（不含任何加权总分）。

## 3 交互与 UI

顶栏：标题"居住需求档案与气泡图任务书"+徽标（教学假设声明）+导航：关卡1·现状诊断 / 关卡2·关系处方（不锁功能，只换引导文案）/ 挑战·任务书导出(禁用至解锁) / 情境A|B 切换 / 存为A版 / 存为B版 / 载入A版 / 载入B版 / 重置现状。

左栏：①气泡托盘（按 公/私/半私/家务 分组，每泡=椭圆小样+名称+面积；未装填的可拖；fixed 两泡只显示）②访谈要点清单（14 条，每条显示覆盖状态色点：绿=覆盖/蓝=留待情境B/黄=未覆盖，点击高亮对应气泡/边）。

中栏 SVG 画布（~900×640）：房间槽按 U90 平面相对位置摆放的圆角矩形格子（kitchen 左上、entry/bath_pub 其右、study 右上、dining 左中、living 中部大格、master 左下、bath_main 内嵌 master、storage 右中、child 右下、balcony_n 厨房上方细条），槽底色按 zone（公米/私蓝灰/家务淡绿/过渡灰/共用淡紫），槽内显示名称+容量+占用条（sum/capacity，>105% 红）。装填的气泡=槽内小椭圆（名称+面积），可拖到其他允许槽（slots 白名单外的槽拖入弹回+状态栏提示）。**连边模式**：点"连边"按钮进入，依次点两气泡→弹小面板选档位（五档色块）+证据（访谈/观察/课程假设）→确认；点已有边可改档/改证据/删除。边画为两点间线+档位色+中点小签（+2 等）。

右栏三卡：①「检查报告」四段列表（面积超载/时段冲突/三角张力/区带错配），每项含"教学常用值·讨论工具"脚注；②「访谈覆盖与对表」：14 条 ip 状态表 + 逐边对表结果（满足绿/部分橙/不满足红/无法对照灰）；③「情境与任务书」：scenario_delta 摘要（B 时显示）、A/B 两版保存状态、两个失效条件 textarea（占位"当______时本任务书失效：______"）、解锁条件进度文案、导出任务书 JSON 按钮（含 bubbles/edges/两版快照/失效条件/检查报告/规则版本，字段名见 §5）。

状态栏 aria-live；selftest 面板（details+按钮）。

## 4 状态与 API

state JSON：`{scenario, tray:[气泡id未装填], fill:{槽id:[气泡id]}, edges:[{a,b,v,evidence}], versions:{A,B|null}, failures:{A,B}}`。`BubbleEngine.evaluate(state)→report`（report 含 checks 全量+summary+facts）；`baseline('A'|'B')`（A=现状；B=A 基线+情境B新增项默认也装入 study？**否**——B 基线=现状装填保持+托盘新增两泡+预置夜起边，学生自己决定装哪，引擎立刻亮 delta）；`change/fill/move/addEdge/removeEdge/serialize/deserialize`。

QA 钩子（渲染层导出）：`__LAB_READY__`、`__LAB_CONSOLE_ERRORS__`（捕获 error/unhandledrejection/console.error）、`__LAB_SET_LEVEL__(1|2)`、`__LAB_LOAD_BASELINE__('A'|'B')`、`__LAB_SET_SCENARIO__('A'|'B')`、`__LAB_EVALUATE__()`、`__LAB_SELFTEST__()`。

## 5 自检（__LAB_SELFTEST__，8 条断言照 lab.yaml selftest 一字不差）

实现注意：断言 3/4/5 在临时代改 state 上做，做完还原且断言 7 在还原后跑；断言 2 用 fill 把 sleep_elder 放 study（情境B state）；断言 6 的三条对表边分别构造。输出 {passed,failed:[],total:8}。

## 6 输出要求

只输出一个 ```html 代码块（完整文件，<title> 居住需求档案与气泡图任务书）。顺序：CSS→HTML→JS（常量→纯引擎→渲染→交互→QA钩子→初始 render→自检静默跑一次写控制台）。总长≤56k 字符；空间紧张时压缩视觉细节，保引擎与自检完整。
