"""profile.py — production-profile 加载（ARCHITECTURE-v2 §10-§12 三模式）。

零依赖 YAML 子集解析（缩进 / key: value / - item / # 注释 / null 字面量），
先构建泛型树（lookahead 区分"空值标量"与"子块开启"），再深合并进 DEFAULT。
缺省即 MODE A（OPEN）。schema 见 profiles/example.profile.yaml。
"""
from __future__ import annotations
import copy
from pathlib import Path

DEFAULT = {
    "mode": "OPEN",                      # OPEN | ASSISTED | PROJECT_ROUTE
    "visual": {"style_pack": None},
    "backend": {"preferred": None, "allowed": ["web_2d", "manim", "three_3d", "custom"]},
    "storyboard": {"pacing": "medium", "intro_max_seconds": 8},
    "knowledge": {"use_project_cases": False, "use_global_success_cases": False,
                  "use_failure_memory": True},
    "creative_freedom": {"allow_new_layout": True, "allow_new_transition": True,
                         "backend_escape_hatch": True},
}


def _scalar(s: str):
    s = s.strip()
    if s in ("true", "True"): return True
    if s in ("false", "False"): return False
    if s in ("null", "~", ""): return None
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"": return s[1:-1]
    try: return int(s)
    except ValueError:
        try: return float(s)
        except ValueError: return s


def _tokens(text: str):
    import re
    out = []
    for raw in text.splitlines():
        line = re.sub(r"\s+#.*$", "", raw.rstrip())   # 剥行内注释（值域不含 " #"）
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        out.append((len(line) - len(line.lstrip()), line.strip()))
    return out


def _tree(tokens: list) -> dict:
    """缩进树。`key:` 后跟更深缩进 → 子块；否则（含显式 null）→ 标量。
    列表块不进容器栈：记 (key缩进, 宿主dict, key)，缩进更深的 `- item` 挂到宿主上。"""
    root: dict = {}
    stack = [(-1, root)]                  # (indent, dict) —— 只放 dict 容器
    pending: list | None = None           # [key_indent, holder_dict, key]
    for i, (indent, line) in enumerate(tokens):
        if pending and indent <= pending[0]:
            pending = None
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if line.startswith("- "):
            if pending is None:
                raise ValueError(f"列表项无宿主 key: {line!r}")
            _, holder, key = pending
            lst = holder.setdefault(key, [])
            if not isinstance(lst, list):
                raise ValueError(f"{key} 已是 {type(lst).__name__}，不能接列表项")
            lst.append(_scalar(line[2:]))
        else:
            k, _, v = line.partition(":")
            k, v = k.strip(), _scalar(v)
            nxt = tokens[i + 1] if i + 1 < len(tokens) else (None, "")
            if v is None and nxt[0] is not None and nxt[0] > indent:
                if nxt[1].startswith("- "):            # 列表块：不进栈，记挂起上下文
                    holder = parent.setdefault(k, [])
                    if not isinstance(holder, list):
                        parent[k] = holder = []
                    pending = [indent, parent, k]
                else:                                  # dict 子块：进栈
                    block = parent.setdefault(k, {})
                    if not isinstance(block, dict):
                        parent[k] = block = {}
                    stack.append((indent, block))
            else:
                parent[k] = v
    return root


def _merge(base: dict, over: dict) -> dict:
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge(base[k], v)
        else:
            base[k] = v                    # 标量/列表整体替换
    return base


def load(path: str | Path | None) -> dict:
    prof = copy.deepcopy(DEFAULT)
    if not path:
        return prof
    tree = _tree(_tokens(Path(path).read_text(encoding="utf-8")))
    _merge(prof, tree)
    if prof["mode"] not in ("OPEN", "ASSISTED", "PROJECT_ROUTE"):
        raise ValueError(f"mode 非法: {prof['mode']}")
    return prof
