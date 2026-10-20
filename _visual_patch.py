# -*- coding: utf-8 -*-
"""_visual_patch.py — 人审定向视觉修复：只改指定场景的画面问题，音频/时长不动。
用法: python _visual_patch.py runs/isd-XX "<场景与问题描述>" [--scenes "句1-6,0-40s"]
流程: sol 修 code/index.html → web2d 重渲 → qa → mux 出 final。
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import llm, qa  # noqa: E402
from pipeline.adapters import web2d  # noqa: E402

ROOT = Path(__file__).resolve().parent

def main():
    wd = Path(sys.argv[1]); complaint = sys.argv[2]
    scenes = sys.argv[sys.argv.index("--scenes") + 1] if "--scenes" in sys.argv else "全片"
    title = wd.name
    code_path = wd / "code" / "index.html"
    code = code_path.read_text(encoding="utf-8")
    bak = code_path.with_suffix(".html.bak-visualpatch")
    bak.write_text(code, encoding="utf-8")
    timing = json.loads((ROOT / "audio" / f"timing_{title}.json").read_text(encoding="utf-8"))
    decision = json.loads((wd / "decision.json").read_text(encoding="utf-8"))

    prompt = [{"role": "user", "content": f"""用户看片后提出画面问题，请定向修复并重新输出完整 index.html（只输出一个完整代码块）。

## 后端
{decision.get('backend', 'WEB_2D')}

## 修复范围（只许动这里的画面，其余场景一律保持原样）
{scenes}

## 用户验收意见（必须逐条解决）
{complaint}

## 修复要求
- 只改上述场景的绘制逻辑（几何/比例/朝向/布局），不改旁白文本、时间轴、句序、时长与其它场景的视觉；
- 修完自查比例关系符合常识（人体工程学尺度），动画结构（renderFrame(t) 纯函数）不变；
- 输出完整文件，禁止省略段。

## 原代码
```
{code}
```"""}]
    fixed, meta = llm.call("sol", prompt, think="low", effort="high")
    m = re.search(r"```(?:\w+)?\n(.*?)```", fixed, re.S)
    if not m or len(m.group(1)) < 5000:
        print("PATCH FAIL: no code block"); return 1
    code_path.write_text(m.group(1).strip(), encoding="utf-8")
    print(f"patched: {len(m.group(1))} chars ({meta['usage'].get('completion_tokens')} tok)")

    res = web2d.render(wd, timing)
    if not res["ok"]:
        print("render FAIL:", res["errors"][:3]); return 1
    print("render OK ->", res["video"])
    report = qa.check(res["video"], timing, wd)
    print("qa:", "PASS" if report["pass"] else json.dumps(report["checks"], ensure_ascii=False)[:200])
    if not report["pass"]:
        return 1
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "audio.py"), "mux", res["video"],
                        str(ROOT / "audio" / f"timing_{title}.json"),
                        str(wd / "out" / f"final_{title}.mp4")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print([l for l in (r.stdout or "").splitlines() if l.startswith("final:")] or r.stderr[-200:])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
