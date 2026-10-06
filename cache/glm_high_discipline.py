import sys, json, time, urllib.request, urllib.error

sys.path.insert(0, r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
sys.path.insert(0, r"D:\qjcNetDiskDownload\deepseek-harness\project\103\cache")
from pathlib import Path
from pipeline import prompts
import glm_think_probe as p

wd = Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\capital2")
timing = json.loads((Path(r"D:\qjcNetDiskDownload\deepseek-harness\project\103") / "audio" / "timing_capital2.json").read_text(encoding="utf-8"))
decision = json.loads((wd / "decision.json").read_text(encoding="utf-8"))
sb = (wd / "storyboard.md").read_text(encoding="utf-8")
messages = prompts.codegen_prompt(decision, sb, timing, {})

# 思考纪律注入：对最后一条 user 消息追加
discipline = """

## 思考纪律（严格遵守）
- 思考阶段目标：确定布局常量、调色板、每段的元素清单与入场方式，到此为止
- 得出方案后立即开始写代码，不要再回头权衡、不要再探索备选方案
- 最终答案必须以完整代码结尾，代码优先于一切解释文字
"""

messages[-1] = {"role": "user", "content": messages[-1]["content"] + discipline}

payload = {"model": "glm-5.3", "messages": messages, "max_tokens": 32768,
           "reasoning_effort": "high"}
req = urllib.request.Request(
    "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions",
    data=json.dumps(payload).encode(),
    headers={"Authorization": "Bearer " + p._key(), "Content-Type": "application/json"})
t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=1500) as r:
        d = json.loads(r.read())
    u, ch = d["usage"], d["choices"][0]
    rt = (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)
    content = ch["message"].get("content") or ""
    print(f"elapsed={time.time()-t0:.0f}s finish={ch.get('finish_reason')} "
          f"reasoning={rt} completion={u.get('completion_tokens')} content={len(content)}ch")
    print("head:", content[:120].replace("\n", " "))
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode("utf-8", "replace")[:150])
