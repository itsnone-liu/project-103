# -*- coding: utf-8 -*-
"""_rewrite_narration.py — 定向改写分镜旁白为口语化讲课口吻（保锚点/句数/字数预算，只改风格）。
用法: python _rewrite_narration.py runs/isd-XX/storyboard.md
"""
import re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import llm  # noqa: E402

STYLE_SPEC = """【口语化改写条款（保持内容零变化，只改口吻）】
- 口吻＝老师傅带徒弟的讲课感，不是播音稿、不是教材朗读：多用"你看""咱们""这一下""先别急""注意啊"等课堂指示语（每3-5句一处，不堆砌）；
- 短句为主（平均不超过26字）；书面连接词（因此/此外/即为/应当/需）换成口语（所以/还有/说白了/就是/得/要）；
- 允许设问自答（"为什么？因为……"）和少量自然语气词（对/其实）；禁感叹号轰炸、禁排比；
- 两条不口语化的例外：数字与术语句保持精确（"一千二百毫米"照读，不加语气词污染数据句）；金句/结论句保留书面力度（对仗句不加口语词）。
【硬约束】
1. 输出仍为完整 storyboard markdown：## Narration 下的编号句逐句对应改写（句数不变、编号不变），## Parameters 与 ## Math-check 及其余小节原样保留；
2. 每句的内容锚点、教学事实、数字、"教学常用值"标注、规范边界表述不得增删改（如 GB 55031-2022 只作查核入口、不转述条款数值）；
3. 全部旁白总字数与原稿相差不超过 ±8%（避免 TTS 时长出窗）；
4. 只输出改写后的完整 markdown，不要解释。"""

def main():
    sb = Path(sys.argv[1])
    old = sb.read_text(encoding="utf-8")
    bak = sb.with_suffix(".md.bak-precolloquial")
    if not bak.exists():
        shutil.copy2(sb, bak)
    prompt = ("你是《室内空间设计》课程视频的旁白定稿编辑。下面是一份分镜 storyboard，"
              "请把 ## Narration 的每一句改写得更口语化（讲课口吻），其余小节原样保留。\n"
              + STYLE_SPEC + "\n\n---\n" + old)
    out, meta = llm.call("sol", [{"role": "user", "content": prompt}], think="on", effort="high")
    sb.write_text(out.strip() + "\n", encoding="utf-8")
    old_n = re.findall(r"^\d+\.", old, re.M)
    new_n = re.findall(r"^\d+\.", out, re.M)
    def nchars(t):
        m = re.search(r"## Narration\n(.*?)\n## ", t, re.S)
        return len(re.sub(r"[^\u4e00-\u9fff0-9a-zA-Z]", "", m.group(1))) if m else -1
    print(f"sentences old={len(old_n)} new={len(new_n)} | chars old={nchars(old)} new={nchars(out)} | tok={meta['usage'].get('completion_tokens')}")

if __name__ == "__main__":
    main()
