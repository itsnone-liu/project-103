"""llm.py — 统一模型调用层（luna / glm），沉淀 Case D 全部调用教训。

教训（KP-004）：glm coding 端点大 prompt 代码任务 thinking 会烧穿 65536
（reasoning_effort / thinking.budget_tokens 均无效）；已验证缓解=瘦身 prompt +
thinking disabled；slim+thinking-on 是首选待验组合（GLM_THINK=on 强制）。
1308（5h 窗口）→ 睡 900s；429/5xx → 75s；传输错误 → 60s。绝不盲连发。
"""
from __future__ import annotations
import json, os, time, urllib.request, urllib.error
from pathlib import Path

ENDPOINTS = {
    "luna": ("http://127.0.0.1:8080/v1/chat/completions", "LUNA_API_KEY", "gpt-6-luna"),
    "glm":  ("https://open.bigmodel.cn/api/coding/paas/v4/chat/completions", "GLM_API_KEY", "glm-5.3"),
}


def _post(url: str, key: str, payload: dict, timeout: int = 1800):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def call(model: str, messages: list, *, max_tokens: int = 65536,
         temperature: float | None = None, effort: str | None = None) -> tuple[str, dict]:
    """返回 (content, usage)。重试策略内建；烧穿（finish=length 且 0 内容）返回 ('', meta) 由上层裁决。"""
    url, key_env, model_id = ENDPOINTS[model]
    key = os.environ.get(key_env, "")
    payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        payload["temperature"] = temperature
    if model == "glm":
        # KP-004：thinking 策略可由环境强制；默认代码任务关（安全），GLM_THINK=on 为首选实验位
        policy = os.environ.get("GLM_THINK", "off").lower()
        if policy == "on":
            pass  # 端点默认 thinking，不传字段
        elif policy == "budget":
            payload["thinking"] = {"type": "enabled", "budget_tokens": 16384}
        else:
            payload["thinking"] = {"type": "disabled"}
    if effort and model == "luna":
        payload["reasoning_effort"] = effort
    for attempt in range(6):
        try:
            d = _post(url, key, payload)
            content = (d.get("choices") or [{}])[0].get("message", {}).get("content") or ""
            meta = {"usage": d.get("usage", {}),
                    "finish": (d.get("choices") or [{}])[0].get("finish_reason", "")}
            if model == "glm" and meta["finish"] == "length" and not content.strip():
                meta["burnout"] = True   # 推理烧穿：上层不得再原样重试（额度意识）
            return content, meta
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code in (429, 500, 502, 503, 504):
                wait = 900 if "1308" in body or "上限" in body else 75   # 教训：1308 报文不含 quota 字样
                print(f"[llm] HTTP {e.code} {body[:80]} — sleep {wait}s")
                time.sleep(wait); continue
            if e.code == 401:
                raise RuntimeError(f"401 Unauthorized（key 失效/错误）: {body}") from e
            raise RuntimeError(f"HTTP {e.code}: {body}") from e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"[llm] transport: {e} — sleep 60s"); time.sleep(60); continue
    raise RuntimeError(f"[llm] {model}: retries exhausted")
