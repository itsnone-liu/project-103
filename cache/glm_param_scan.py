import sys, json, urllib.request, urllib.error

sys.path.insert(0, r"D:\qjcNetDiskDownload\deepseek-harness\project\103\cache")
import glm_think_probe as p

cands = [
    ("thinking=str", {"thinking": "low"}),
    ("thinking.level", {"thinking": {"level": "low"}}),
    ("reasoning_effort", {"reasoning_effort": "low"}),
    ("type=enabled+level", {"thinking": {"type": "enabled", "level": "low"}}),
    ("budget_tokens", {"thinking": {"type": "enabled", "budget_tokens": 1024}}),
]
for name, extra in cands:
    payload = {"model": "glm-5.3",
               "messages": [{"role": "user", "content": "只回复两个字：正常"}],
               "max_tokens": 512}
    payload.update(extra)
    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + p._key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
        u, ch = d["usage"], d["choices"][0]
        rt = u.get("completion_tokens_details", {}).get("reasoning_tokens")
        content = (ch["message"].get("content") or "")[:16]
        print(name, "OK", "finish=", ch.get("finish_reason"), "content=", repr(content), "reasoning=", rt)
    except urllib.error.HTTPError as e:
        print(name, "HTTP", e.code, e.read().decode("utf-8", "replace")[:120])
