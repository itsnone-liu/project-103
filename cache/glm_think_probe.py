"""glm_think_probe.py — GLM slim+thinking-on 实验（KP-004 补全）。
用法: python cache/glm_think_probe.py [max_tokens]  （默认 16384；thinking 默认开）"""
import json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_PATH = os.path.join(ROOT, "cache", "glm_think_probe_prompt.txt")
OUT_PATH = os.path.join(ROOT, "cache", "glm_think_on_probe.html.md")

PROMPT = """你是自主动画工程师。写一个教学动画页面。

## 内容（3 句旁白）
1. 资金周转率 = 主营业务收入 / 资金平均占用额。
2. 周转 2 次，360 天口径下每圈 180 天。
3. 周转越快，同样的收入需要的平均资金越少。

## 旁白时钟（n+1 项=3 句起点+终点）
starts = [0.0, 6.0, 12.0, 18.0]

## 页面契约（硬约束）
自包含 index.html，无网络依赖。实现：
window.P103 = { duration: 18, fps: 24, width: 1920, height: 1080, renderFrame(t) {...} }
renderFrame(t) 必须纯函数式按 t 重建整帧（禁止 Date.now/setTimeout 驱动动画、未种子化随机），返回 true。
数学量必须精确呈现（公式、180 天推导、占用对比），中文清晰。

## 输出
只输出一个代码块：完整 index.html。视觉风格自主决定，要求有数学感、专业、动效细腻。"""


def _key():
    k = os.environ.get("GLM_API_KEY", "")
    if k:
        return k
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as rk:
        v, _ = winreg.QueryValueEx(rk, "GLM_API_KEY")
        return v


def main():
    max_tokens = int(sys.argv[1]) if len(sys.argv) > 1 else 16384
    if not os.path.exists(PROMPT_PATH):
        open(PROMPT_PATH, "w", encoding="utf-8").write(PROMPT)
    prompt = open(PROMPT_PATH, encoding="utf-8").read()
    payload = {"model": os.environ.get("PROBE_MODEL", "glm-5.3"),
               "messages": [{"role": "user", "content": prompt}],
               "max_tokens": max_tokens}
    if os.environ.get("PROBE_THINK_OFF") == "1":
        payload["thinking"] = {"type": "disabled"}
    elif os.environ.get("PROBE_BUDGET"):
        payload["thinking"] = {"type": "enabled",
                               "budget_tokens": int(os.environ["PROBE_BUDGET"])}
    endpoint = os.environ.get(
        "PROBE_ENDPOINT", "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions")
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + _key(),
                 "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=1500) as r:
        d = json.loads(r.read())
    ch, u = d["choices"][0], d["usage"]
    content = ch.get("message", {}).get("content") or ""
    print("耗时:", round(time.time() - t0), "s")
    print("finish:", ch.get("finish_reason"))
    print("usage:", json.dumps(u))
    print("content_len:", len(content))
    open(OUT_PATH, "w", encoding="utf-8").write(content)
    print("--- 头 300 字 ---")
    print(content[:300])


if __name__ == "__main__":
    main()
