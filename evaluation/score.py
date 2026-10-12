"""Planner 輸出的評分：正規化比對、分層指標、錯誤分類與 bootstrap 信賴區間。"""
import random
from collections import Counter

from planner.schema import REF_RE, validate


def _is_ref(v) -> bool:
    return isinstance(v, str) and REF_RE.match(v) is not None


class Canon:
    """把 step 的 $sN 引用遞迴展開成不依賴編號的字串；循環引用以 <cycle> 標記，不會無窮遞迴。"""

    def __init__(self, steps: list[dict]):
        self.by_id = {s.get("id"): s for s in steps}
        self.memo: dict[str, str] = {}

    def step(self, sid: str, stack: tuple = ()) -> str:
        if sid in self.memo:
            return self.memo[sid]
        if sid in stack:
            return f"<cycle:{sid}>"
        if sid not in self.by_id:
            return f"<missing:{sid}>"
        s = self.by_id[sid]
        args = ",".join(f"{k}={self.value(v, stack + (sid,))}" for k, v in sorted(s.get("args", {}).items()))
        self.memo[sid] = f"{s.get('tool')}({args})"
        return self.memo[sid]

    def value(self, v, stack: tuple = ()) -> str:
        if _is_ref(v):
            sid, path = REF_RE.match(v).groups()
            return f"{self.step(sid, stack)}.{path}"
        return str(v).strip()

    def all(self) -> dict[str, str]:
        return {sid: self.step(sid) for sid in self.by_id}


def canonical_steps(plan: dict) -> dict[str, str]:
    return Canon(plan.get("steps", [])).all()


def _edges(steps: list[dict]) -> Counter:
    """相依結構只看「哪個工具等哪個工具」，參數錯誤不會連帶算成相依錯誤。"""
    tool = {s["id"]: s["tool"] for s in steps}
    return Counter((tool.get(d), s["tool"]) for s in steps for d in s["depends_on"])


def _canon_edges(steps: list[dict], canon: Canon) -> Counter:
    return Counter((canon.step(d), canon.step(s["id"])) for s in steps for d in s["depends_on"])


def score_sample(gold: dict, pred: dict | None) -> dict:
    gold_steps = gold.get("steps", [])
    gold_tools = Counter(s["tool"] for s in gold_steps)
    args = [v for s in gold_steps for v in s["args"].values()]
    m = {"parse_ok": pred is not None, "schema_ok": False, "action_ok": False, "pred_action": "invalid",
         "exact": False, "tool_tp": 0, "tool_fp": 0, "tool_fn": sum(gold_tools.values()),
         "distractor": False, "lit_ok": 0, "lit_n": sum(not _is_ref(v) for v in args),
         "ref_ok": 0, "ref_n": sum(_is_ref(v) for v in args),
         "deps_ok": False if gold["action"] == "plan" else None}
    if pred is None or validate(pred):
        return m

    m["schema_ok"], m["pred_action"] = True, pred["action"]
    m["action_ok"] = pred["action"] == gold["action"]
    pred_steps = pred["steps"] if pred["action"] == "plan" else []
    pred_tools = Counter(s["tool"] for s in pred_steps)
    tp = sum((gold_tools & pred_tools).values())
    m.update(tool_tp=tp, tool_fp=sum(pred_tools.values()) - tp, tool_fn=sum(gold_tools.values()) - tp,
             distractor=any(t not in gold_tools for t in pred_tools))

    if gold["action"] == "clarify":
        m["exact"] = m["action_ok"] and set(pred["missing"]) == set(gold["missing"])
    elif gold["action"] == "refuse":
        m["exact"] = m["action_ok"]
    else:
        g, p = Canon(gold_steps), Canon(pred_steps)
        used: set[str] = set()
        for gs in gold_steps:
            ps = next((x for x in pred_steps if x["tool"] == gs["tool"] and x["id"] not in used), None)
            if ps is not None:
                used.add(ps["id"])
            for k, v in gs["args"].items():
                if ps is not None and k in ps["args"] and p.value(ps["args"][k]) == g.value(v):
                    m["ref_ok" if _is_ref(v) else "lit_ok"] += 1
        m["deps_ok"] = m["action_ok"] and _edges(gold_steps) == _edges(pred_steps)
        # deps_ok 只看工具名（診斷用）；exact 另外比對以 Canon 表示的邊，重複工具對調相依時才分得出來
        m["exact"] = (m["deps_ok"] and Counter(g.all().values()) == Counter(p.all().values())
                      and _canon_edges(gold_steps, g) == _canon_edges(pred_steps, p))
    return m


def classify_errors(gold: dict, pred: dict | None, m: dict) -> list[str]:
    if m["exact"]:
        return []
    if not m["schema_ok"]:
        return ["format"]
    ga, pa = gold["action"], pred["action"]
    if ga != pa:
        if ga == "refuse":
            return ["missed_refuse"]
        if pa == "refuse":
            return ["over_refuse"]
        return ["hallucinated_args" if ga == "clarify" else "over_clarify"]
    if ga == "clarify":
        return ["wrong_missing"]
    gt, pt = Counter(s["tool"] for s in gold["steps"]), Counter(s["tool"] for s in pred["steps"])
    tags = []
    if m["distractor"]:
        tags.append("distractor")
    if m["tool_fn"]:
        tags.append("missing_step")
    if any(pt[t] > gt[t] for t in gt):
        tags.append("extra_step")
    if m["lit_ok"] < m["lit_n"]:
        tags.append("literal_arg")
    if m["ref_ok"] < m["ref_n"]:
        tags.append("ref_arg")
    if not m["deps_ok"]:
        tags.append("dependency")
    return tags or ["other"]


def bootstrap_ci(values: list[float], n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    if not values:
        nan = float("nan")
        return nan, nan, nan
    rng, n = random.Random(seed), len(values)
    means = sorted(sum(rng.choices(values, k=n)) / n for _ in range(n_boot))
    return sum(values) / n, means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]
