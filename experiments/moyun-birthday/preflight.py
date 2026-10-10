"""Fail-closed offline preflight for approved OPEN/ASSISTED birthday experiment."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CARD = ROOT / "knowledge" / "success-cases" / "EXTERNAL-moyun-living-rice-paper-2026-10.md"
BRIEF = HERE / "brief.md"
WORDS = "岁岁欢喜，年年胜意"


def run():
    brief = BRIEF.read_text(encoding="utf-8")
    card = CARD.read_text(encoding="utf-8")
    assert WORDS in brief and "纸墨音效" in brief and "不调用付费视频生成模型" in brief
    assert "REFERENCE ONLY" in card and "NON-BINDING" in card
    texts = {}
    for arm in ("open", "assisted"):
        p = HERE / arm / "index.html"
        text = p.read_text(encoding="utf-8")
        assert WORDS in text and "生辰快乐" not in text, arm
        assert "window.P103" in text and "renderFrame" in text, arm
        code = text.split("<script>", 1)[1] if "<script>" in text else text
        assert not any(x in code for x in ("http://", "https://", "@import", "<img ", "<audio ", "Math.random")), arm
        # Evidence of deliberate design input, not evidence of an A/B causal effect.
        if arm == "assisted":
            assert (HERE / arm / "reference_used.md").is_file(), "Missing assisted reference trace"
        else:
            assert not (HERE / arm / "reference_used.md").exists(), "OPEN contaminated by case notes"
        texts[arm] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert texts["open"] != texts["assisted"], "A/B code identical"
    print(json.dumps({"status":"PASS", "approved_text":WORDS,
                      "sound":"paper_ink.wav", "external_video_model":False,
                      "brief_sha256":hashlib.sha256(brief.encode()).hexdigest(),
                      "case_sha256":hashlib.sha256(card.encode()).hexdigest(),
                      "html_sha256":texts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
