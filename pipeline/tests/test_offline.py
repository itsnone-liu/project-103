"""test_offline — 离线脊柱自测（零 LLM 消耗）。

覆盖：profile 解析 / 后端注册表+菜单文本 / 提示词契约要素（why-not、n+1 timing、无 Pattern 默认注入）/
web_2d 冒烟夹具端到端（捕获→编码→QA 帧活力）/ manim 环境探针诚实报缺 / 契约错误通道。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import profile as prof_mod, prompts, backends            # noqa: E402
from pipeline.adapters import web2d, manim                              # noqa: E402
from pipeline import qa as qa_mod                                       # noqa: E402

PASS, FAIL = [], []


def t(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not cond else ""))


def main() -> int:
    print("== profile 解析")
    p = prof_mod.load(ROOT / "profiles" / "example.profile.yaml")
    t("mode", p["mode"] == "PROJECT_ROUTE", p["mode"])
    t("allowed", p["backend"]["allowed"] == ["manim", "web_2d"], str(p["backend"]["allowed"]))
    t("preferred", p["backend"]["preferred"] == "manim")
    t("style_pack null", p["visual"]["style_pack"] is None)
    t("failure_memory", p["knowledge"]["use_failure_memory"] is True)
    t("escape_hatch", p["creative_freedom"]["backend_escape_hatch"] is True)
    d = prof_mod.load(None)
    t("default OPEN", d["mode"] == "OPEN" and d["backend"]["preferred"] is None)

    print("== 后端注册表 + 菜单")
    t("四后端", set(backends.BACKENDS) == {"web_2d", "manim", "three_3d", "custom"})
    mt = backends.menu_text(p)
    t("菜单含 MANIM", "MANIM" in mt and "限制" in mt)

    print("== 提示词契约")
    steps = prompts.decision_prompts("测试主题", "## Narration\n1. 测试", p)
    t("两步决策", len(steps) == 2)
    t("步A无菜单锚", "WEB_2D" not in steps[0][0]["content"] and "可用后端" not in steps[0][0]["content"])
    t("步B含 why_not", "why_not" in steps[1][0]["content"])
    blind = prompts.decision_prompts("t", "s", p, blind=True)
    t("盲测单步", len(blind) == 1)
    cg = prompts.codegen_prompt({"backend": "WEB_2D", "reason": "t"}, "sb",
                                {"starts": [0.0, 1.0, 2.0], "total": 3.0}, p)[0]["content"]
    t("timing n+1 注入", "[0.0, 1.0, 2.0, 3.0]" in cg.replace(", ", ", "))
    t("五关契约注入", "逐帧确定性" in cg)
    t("无 Pattern 默认注入", "markAngle" not in cg and "PATTERNS" not in cg)
    t("无美学预设", "手绘" not in cg)
    hp = prompts._pitfalls(["web_2d", "generic"])
    t("坑文档检索非空", len(hp) > 50 and "KP-" in hp)

    print("== web_2d 端到端（夹具）")
    wd = ROOT / "runs" / "_spine_test"
    wd.mkdir(parents=True, exist_ok=True)
    res = web2d.smoke(wd)
    t("smoke ok", res["ok"], json.dumps(res.get("errors", []), ensure_ascii=False)[:200])
    if res["ok"]:
        rep = qa_mod.check(res["video"], {"total": 10 / 24}, wd)
        t("qa 时长", rep["checks"]["duration"]["pass"], str(rep["checks"]["duration"]))
        fv = rep["checks"]["frame_variance"]
        t("qa 帧活力", fv["pass"], str(fv))
        t("contact sheet", Path(rep["checks"]["contact_sheet"]["path"]).exists())

    print("== manim 探针（预期诚实报缺）")
    pr = manim.probe()
    t("探针结构", ("ok" in pr) and (pr["ok"] or "hint" in pr), str(pr)[:120])

    print(f"\n== 结果: {len(PASS)} PASS / {len(FAIL)} FAIL")
    if FAIL:
        print("失败项:", FAIL)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
