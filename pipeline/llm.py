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
    # codex 代理两个模型共用一个 key：用户注册表实测只有 CODEX_PROXY_API_KEY
    # （LUNA_API_KEY 从未设置——2026-10-10 修正，此前 401 的根因）
    "luna": ("http://127.0.0.1:8080/v1/chat/completions", "CODEX_PROXY_API_KEY", "gpt-6-luna"),
    "sol":  ("http://127.0.0.1:8080/v1/chat/completions", "CODEX_PROXY_API_KEY", "gpt-6.1-sol"),
    "glm":  ("https://open.bigmodel.cn/api/coding/paas/v4/chat/completions", "GLM_API_KEY", "glm-5.3"),
}


def _key_for(key_env: str) -> str:
    """环境变量优先；缺失时从用户注册表兜底（harness pwsh 不继承 User env——
    2026-10-06 教训：空 Bearer 报的也是 401"令牌已过期或验证不正确"，勿误诊为 key 失效）。"""
    k = os.environ.get(key_env, "")
    if k:
        return k
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as rk:
            v, _ = winreg.QueryValueEx(rk, key_env)
            return v
    except OSError:
        return k


def _post(url: str, key: str, payload: dict, timeout: int = 1800):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def call(model: str, messages: list, *, max_tokens: int = 65536,
         temperature: float | None = None, effort: str | None = None,
         think: str | None = None) -> tuple[str, dict]:
    """返回 (content, usage)。think: None=环境默认 / 'on'|'off'|'budget' 逐调用覆盖。
    2026-10-06 实验矩阵（KP-004 定稿）：coding 端点代码任务 thinking 必烧穿（与 prompt
    大小无关，271tok 也烧）；通用端点有 low/high/max 旋钮但 coding key 无余额(1113)。
    → 生产=分相：storyboard/decide 开，codegen/repair 关。"""
    url, key_env, model_id = ENDPOINTS[model]
    key = _key_for(key_env)
    payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        payload["temperature"] = temperature
    if model == "glm":
        # 2026-10-06 终局（官方 thinking 文档 + coding 端点实证）：
        # 顶层 reasoning_effort 在 Coding Plan 生效：5.3 档位 none/minimal/low→low, medium/high→high, xhigh/max→max
        # 实测 slim 代码任务：low=14.4k 推理后出内容✓, high=烧穿✗, 5.2+none=仍烧✗(文档与实现不符)
        policy = (think or os.environ.get("GLM_THINK", "off")).lower()
        if policy in ("on", "max"):
            pass  # 端点默认 = max 档（分镜/决策用，实测优秀）
        elif policy == "low":
            payload["reasoning_effort"] = "low"   # codegen 档：有思考且收敛
        else:
            payload["thinking"] = {"type": "disabled"}
    if effort and model in ("luna", "sol"):
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
            if "1113" in body or "余额不足" in body:
                raise RuntimeError("1113 余额不足/无资源包（该端点对此 key 不可用，不重试）") from e
            if "1210" in body:
                raise RuntimeError(f"1210 参数被拒（always-thinking 模型不吃该参数）: {body[:120]}") from e
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
