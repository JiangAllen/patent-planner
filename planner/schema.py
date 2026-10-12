"""Planner 輸出的解析與格式驗證。"""
import json
import re

from planner.tools import TOOLS

REF_RE = re.compile(r"^\$(s\d+)\.(.+)$")
ACTIONS = {"plan", "clarify", "refuse"}


def parse_output(text: str) -> dict | None:
    """擷取輸出中的第一個 JSON 物件；容忍 ```json 圍欄與前後說明文字。失敗回傳 None。"""
    decoder = json.JSONDecoder()
    start = text.find("{")
    while start >= 0:  # 前面的說明文字可能也有花括號，逐一嘗試
        try:
            obj, _ = decoder.raw_decode(text[start:])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
        start = text.find("{", start + 1)
    return None


def step_refs(step: dict) -> list[str]:
    """回傳 step 的 args 中以 $sN.xxx 引用到的 step id。"""
    return [m.group(1) for v in step.get("args", {}).values()
            if isinstance(v, str) and (m := REF_RE.match(v))]


def _deps(step: dict) -> set[str]:
    return set(step["depends_on"]) | set(step_refs(step))


def _has_cycle(by_id: dict[str, dict]) -> bool:
    state: dict[str, int] = {}  # 1 = 走訪中，2 = 已完成

    def visit(sid: str) -> bool:
        if state.get(sid) == 1:
            return True
        if state.get(sid) == 2:
            return False
        state[sid] = 1
        if any(visit(d) for d in _deps(by_id[sid])):
            return True
        state[sid] = 2
        return False

    return any(visit(sid) for sid in by_id)


def _strict(steps: list[dict], by_id: dict[str, dict], available: list[str] | None) -> list[str]:
    errs = []
    for s in steps:
        tool = TOOLS.get(s["tool"])
        if tool is None:
            errs.append(f"{s['id']} 使用未知工具 {s['tool']}")
            continue
        if available is not None and s["tool"] not in available:
            errs.append(f"{s['id']} 使用不在可用清單的工具 {s['tool']}")
        for p, (_, required) in tool["params"].items():
            if required and p not in s["args"]:
                errs.append(f"{s['id']} 缺少必填參數 {p}")
        for p in s["args"]:
            if p not in tool["params"]:
                errs.append(f"{s['id']} 多出未定義參數 {p}")
        if not set(step_refs(s)) <= set(s["depends_on"]):
            errs.append(f"{s['id']} 的引用未列入 depends_on")
        for v in s["args"].values():
            m = REF_RE.match(v) if isinstance(v, str) else None
            if not m:
                continue
            target = TOOLS.get(by_id[m.group(1)]["tool"])
            field = re.match(r"[a-z_]*", m.group(2)).group(0)
            fields = {r.split("[")[0].split(".")[0] for r in target["returns"]} if target else set()
            if field not in fields:
                errs.append(f"{s['id']} 引用 {m.group(1)} 不存在的欄位 {field or m.group(2)}")
    return errs


def validate(obj: dict, available_tools: list[str] | None = None, strict: bool = False) -> list[str]:
    """回傳錯誤訊息清單；空清單代表合法。非 strict 只檢查結構。"""
    action = obj.get("action")
    if action not in ACTIONS:
        return [f"未知的 action：{action!r}"]
    if action == "clarify":
        missing = obj.get("missing")
        ok = isinstance(missing, list) and missing and all(isinstance(x, str) for x in missing)
        return [] if ok else ["clarify.missing 必須是非空字串陣列"]
    if action == "refuse":
        return [] if isinstance(obj.get("reason"), str) else ["refuse.reason 必須是字串"]

    steps = obj.get("steps")
    if not (isinstance(steps, list) and steps):
        return ["plan.steps 必須是非空陣列"]
    for s in steps:
        if not (isinstance(s, dict) and isinstance(s.get("id"), str) and isinstance(s.get("tool"), str)
                and isinstance(s.get("args"), dict) and isinstance(s.get("depends_on"), list)
                and all(isinstance(d, str) for d in s["depends_on"])):
            return [f"step 結構錯誤：{s!r}"]
    ids = [s["id"] for s in steps]
    errs = [] if len(set(ids)) == len(ids) else ["step id 重複"]
    by_id = {s["id"]: s for s in steps}
    for s in steps:
        for d in s["depends_on"] + step_refs(s):
            if d not in by_id:
                errs.append(f"{s['id']} 引用不存在的 step {d}")
    if not errs and _has_cycle(by_id):
        errs.append("相依關係有循環")
    if strict and not errs:
        errs += _strict(steps, by_id, available_tools)
    return errs
