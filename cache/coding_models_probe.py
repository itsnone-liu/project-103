# -*- coding: utf-8 -*-
"""GLM coding 订阅可用模型探针：models 列表 + 候选名单最小调用（coding 端点）。"""
import json, sys, base64, urllib.request
sys.path.insert(0, r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
from pipeline.llm import _key_for

KEY = _key_for("GLM_API_KEY")   # 注意：传环境变量名，不是 'glm'（空 key 报的也是 401）
BASE = "https://open.bigmodel.cn/api/coding/paas/v4"

# 1) models 列表（若支持）
try:
    req = urllib.request.Request(BASE + "/models", headers={"Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
        ids = [m.get("id") for m in d.get("data", [])]
        print("[models 列表]", ids)
except Exception as e:
    print("[models 列表] 不支持或失败:", type(e).__name__, str(e)[:120])

# 2) 候选模型最小文本调用
def ping(model):
    payload = {"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 4}
    req = urllib.request.Request(BASE + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
            ch = d.get("choices", [{}])[0]
            print(f"[text] {model}: OK  finish={ch.get('finish_reason')} usage={d.get('usage', {}).get('prompt_tokens')}/{d.get('usage', {}).get('completion_tokens')}")
            return True
    except urllib.error.HTTPError as e:
        print(f"[text] {model}: HTTP {e.code} {e.read().decode('utf-8','replace')[:100]}")
    except Exception as e:
        print(f"[text] {model}: {type(e).__name__} {str(e)[:80]}")
    return False

for m in ["glm-5.3", "glm-5.2", "glm-5-turbo", "glm-4.7", "glm-4.6", "glm-4.5-air", "glm-4.5v", "glm-4.1v-thinking-flash"]:
    ping(m)

# 3) 视觉尝试（若 4.5v ping 通再试图）——1px png
png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
def ping_vision(model):
    payload = {"model": model, "messages": [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
        {"type": "text", "text": "什么颜色？一个词"}]}], "max_tokens": 8}
    req = urllib.request.Request(BASE + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read())
            msg = d.get("choices", [{}])[0].get("message", {})
            print(f"[vision] {model}: OK  content={(msg.get('content') or '')[:30]!r}")
    except urllib.error.HTTPError as e:
        print(f"[vision] {model}: HTTP {e.code} {e.read().decode('utf-8','replace')[:100]}")
    except Exception as e:
        print(f"[vision] {model}: {type(e).__name__} {str(e)[:80]}")

for m in ["glm-4.5v", "glm-4.1v-thinking-flash", "glm-5.3"]:
    ping_vision(m)
