# -*- coding: utf-8 -*-
"""通用端点视觉/视频理解可用性探针（v0 前置，省额度：最多 1 次图像 + 1 次视频）"""
import json, sys, base64, urllib.request
sys.path.insert(0, r"D:\qjcNetDiskDownload\deepseek-harness\project\103")
from pipeline.llm import _key_for

KEY = _key_for("glm")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def call(payload, tag):
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read())
            ch = d.get("choices", [{}])[0]
            msg = ch.get("message", {})
            content = (msg.get("content") or "")[:120]
            usage = d.get("usage", {})
            print(f"[{tag}] OK model={d.get('model')} finish={ch.get('finish_reason')} "
                  f"content={content!r} usage={usage.get('prompt_tokens')}/{usage.get('completion_tokens')}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        print(f"[{tag}] HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"[{tag}] {type(e).__name__}: {e}")
        return False

# 最小 1x1 红色 PNG
png = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
img_b64 = base64.b64encode(png).decode()

# 1) 图像理解（最便宜的可用性信号）
ok_img = None
for model in ["glm-4.5v", "glm-4.1v-thinking-flash", "glm-4v-flash"]:
    ok_img = call({"model": model, "messages": [
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
            {"type": "text", "text": "这张图是什么颜色？一个词。"}]},
    ], "max_tokens": 50}, f"image/{model}")
    if ok_img:
        break
    print(f"  -> {model} 不可用，试下一个")

# 2) 视频理解（仅当图像通道有余额时才试；用同一张图假装 url 不行——构造 2 帧 GIF? 直接用 video_url 不测了，
#    视频最小调用成本高；图像层通了说明余额存在，视频模型名单留到真正跑时再验证）
print("PROBE DONE image_ok =", bool(ok_img))
