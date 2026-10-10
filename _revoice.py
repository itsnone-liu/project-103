"""_revoice.py — 换声重制编排：复制 run、换 voice 生成新 scene、（tts 后）把代码 STARTS/DUR 对齐新 timing。

⚠️ 陷阱：produce.py 在 timing_<title>.json 不存在时会无条件从 storyboard 重生成 scene_<title>.json
（默认晓晓），覆盖手工换声的 scene。因此 tts 必须直接调 audio.py，绝不能让 produce 走 tts 阶段。

用法:
  python _revoice.py setup <src-run> <dst-run> <new-voice>   # 复制 storyboard/decision/code + 生成换声 scene json
  python _revoice.py tts    <dst-run>                        # 直接 audio.py tts（绕过 produce 的 scene 重生成）
  python _revoice.py patch  <dst-run> <title>                # 从 timing_<title>.json 读 starts/total，改写 code/index.html
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103")

def setup(src_run: str, dst_run: str, voice: str):
    src, dst = ROOT / "runs" / src_run, ROOT / "runs" / dst_run
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "code").mkdir(exist_ok=True)
    for f in ("storyboard.md", "decision.json"):
        if (src / f).exists():
            shutil.copy(src / f, dst / f)
    # topic 文件名各异：复制 src 下所有 topic-*.md
    for t in src.glob("topic-*.md"):
        shutil.copy(t, dst / t.name)
    shutil.copy(src / "code" / "index.html", dst / "code" / "index.html")
    # ⚠️ 复用哨兵：produce 的 codegen 复用要求 code/.done 同时存在，漏拷会触发重新生成（白花 token）
    if (src / "code" / ".done").exists():
        shutil.copy(src / "code" / ".done", dst / "code" / ".done")
    # scene json 换声
    title_src = src_run.replace("-hr-yj", "-hr") if dst_run.endswith("-yj") else src_run
    scene = ROOT / "audio" / f"scene_{src_run}.json"
    sc = json.loads(scene.read_text(encoding="utf-8"))
    sc["title"] = dst_run
    sc["voice"] = voice
    (ROOT / "audio" / f"scene_{dst_run}.json").write_text(
        json.dumps(sc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"setup ok: {dst} voice={voice} sentences={len(sc['sentences'])}")

def patch(dst_run: str, title: str):
    dst = ROOT / "runs" / dst_run
    timing = json.loads((ROOT / "audio" / f"timing_{title}.json").read_text(encoding="utf-8"))
    starts, total = timing["starts"], round(timing["total"], 3)
    code_p = dst / "code" / "index.html"
    code = code_p.read_text(encoding="utf-8")
    # 替换 STARTS 数组字面量
    new_arr = "const STARTS = [\n  " + ",".join(f"{s}" for s in starts) + "\n];"
    code, n1 = re.subn(r"const STARTS\s*=\s*\[[\s\S]*?\];", new_arr, code, count=1)
    # 替换 duration 数字（P103 导出）
    code, n2 = re.subn(r"duration\s*:\s*[\d.]+", f"duration:{total}", code, count=1)
    # 兜底：残留的旧总时长字面量（如 DUR=348.611）
    code_p.write_text(code, encoding="utf-8")
    print(f"patch ok: STARTS x{n1} duration x{n2} -> {total}s, {len(starts)} 句")

def tts(dst_run: str):
    scene = ROOT / "audio" / f"scene_{dst_run}.json"
    import subprocess, sys
    r = subprocess.run([sys.executable, str(ROOT / "audio.py"), "tts", str(scene)],
                       capture_output=True, text=True, encoding="utf-8")
    print(r.stdout[-500:] if r.stdout else "", r.stderr[-300:] if r.stderr else "")
    raise SystemExit(r.returncode)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "setup":
        setup(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "tts":
        tts(sys.argv[2])
    elif cmd == "patch":
        patch(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(f"unknown cmd {cmd}")
