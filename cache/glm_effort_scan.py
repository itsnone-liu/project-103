import sys, json, urllib.request, urllib.error

sys.path.insert(0, r"D:\qjcNetDiskDownload\deepseek-harness\project\103\cache")
import glm_think_probe as p

prompt = open(r"D:\qjcNetDiskDownload\deepseek-harness\project\103\cache\glm_think_probe_prompt.txt", encoding="utf-8").read()
CODING = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"

def probe(label, model, extra):
    payload = {"model": model,
               "messages": [{"role": "user", "content": prompt}],
               "max_tokens": 16384}
    payload.update(extra)
    req = urllib.request.Request(CODING, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + p._key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            d = json.loads(r.read())
        u, ch = d["usage"], d["choices"][0]
        rt = (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)
        content = (ch["message"].get("content") or "")
        print(f"[{label}] finish={ch.get('finish_reason')} reasoning={rt} content={len(content)}ch head={content[:60]!r}")
        return True
    except urllib.error.HTTPError as e:
        print(f"[{label}] HTTP {e.code} {e.read().decode('utf-8', 'replace')[:140]}")
        return False

# 1) coding 端点 + 5.3 + 顶层 reasoning_effort=low（文档：low 档轻推理，预期收敛）
probe("5.3+effort-low", "glm-5.3", {"reasoning_effort": "low"})
# 2) coding 端点 + 5.3 + effort=high（中档对照）
probe("5.3+effort-high", "glm-5.3", {"reasoning_effort": "high"})
# 3) coding 端点 + 5.2 + effort=none（文档：放弃思考，可关对照）
probe("5.2+effort-none", "glm-5.2", {"reasoning_effort": "none"})
