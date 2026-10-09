"""依模板反向生成資料：先決定答案（gold），再填出題目（request）。"""
import json
import random
from pathlib import Path

from datagen.templates import TEMPLATES
from planner.schema import step_refs
from planner.tools import TOOLS

SPLITS = ("train", "val", "test_id", "test_ood")
TOPICS = ["散熱鰭片", "晶圓級封裝", "矽穿孔", "扇出型封裝", "焊球陣列", "電磁屏蔽層", "覆晶接合", "封裝基板"]
LANGS = [("en", "英文"), ("ja", "日文"), ("de", "德文")]
MSGS = ["答辯書草稿已完成，請確認", "審查意見通知書已收到", "答辯期限即將到期", "修正本已送出"]
INSTRS = ["加入散熱鰭片的結構限定", "刪除重複的附屬項敘述", "限定封裝層厚度小於 50 微米"]
REPO = Path(__file__).resolve().parents[1]


def sample_slots(rng: random.Random) -> dict[str, tuple]:
    """回傳 slot 名 → (填入 args 的值, 出現在句子裡的字面)。"""
    year = rng.choice([2025, 2026])
    pat, pat2 = rng.sample(range(700000, 800000), 2)
    claim, months = rng.randint(1, 20), rng.randint(1, 3)
    plain = {
        "CASE": f"TW-{year}-{rng.randint(1, 9999):04d}",
        "OA": f"OA-{year}-{rng.randint(1, 9999):04d}",
        "PAT": f"I{pat}", "PAT2": f"I{pat2}",
        "DATE": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
        "QUERY": rng.choice(TOPICS), "MSG": rng.choice(MSGS), "INSTR": rng.choice(INSTRS),
    }
    slots = {k: (v, v) for k, v in plain.items()}
    slots["CLAIM"] = (claim, str(claim))
    slots["MONTHS"] = (months, str(months))
    slots["LANG"] = rng.choice(LANGS)
    return slots


def needed_tools(t: dict) -> list[str]:
    return [tool for _, tool, _ in t["steps"]] if "steps" in t else list(t["needs"])


def _fill_arg(v, slots):
    if isinstance(v, str) and v.startswith("{") and v.endswith("}") and v[1:-1] in slots:
        return slots[v[1:-1]][0]
    return v


def build_gold(t: dict, slots: dict) -> dict:
    if t["category"] == "clarify":
        return {"action": "clarify", "missing": list(t["missing"])}
    if t["category"] == "refuse":
        return {"action": "refuse", "reason": "no_capable_tool"}
    steps = []
    for sid, tool, args in t["steps"]:
        step = {"id": sid, "tool": tool, "args": {k: _fill_arg(v, slots) for k, v in args.items()}}
        step["depends_on"] = sorted(set(step_refs(step)))
        steps.append(step)
    return {"action": "plan", "steps": steps}


def build_sample(t: dict, rng: random.Random) -> dict:
    slots = sample_slots(rng)
    sentence = rng.choice(t["requests"])
    used = [k for k in slots if "{" + k + "}" in sentence]
    request = sentence.format(**{k: v[1] for k, v in slots.items()})
    drop = t.get("drop")
    needed = sorted(set(needed_tools(t)) - {drop})
    others = [n for n in TOOLS if n not in needed and n != drop]
    tools = needed + rng.sample(others, min(len(others), rng.randint(2, 4)))
    rng.shuffle(tools)
    return {"category": t["category"], "structure_id": t["id"], "available_tools": tools,
            "request": request, "request_original": request,
            "surfaces": [slots[k][1] for k in used], "gold": build_gold(t, slots)}


def generate(seed: int = 42, per_seen: int = 100, per_ood: int = 25) -> list[dict]:
    """已見結構切成 train / val / test_id（約 1/12 val、1/16 test_id）；holdout 結構全進 test_ood。"""
    rng = random.Random(seed)
    seen, ood = [], []
    for t in TEMPLATES:
        if t.get("holdout"):
            ood += [build_sample(t, rng) for _ in range(per_ood)]
        else:
            seen += [build_sample(t, rng) for _ in range(per_seen)]
    rng.shuffle(seen)
    n_val, n_test = len(seen) // 12, len(seen) // 16
    parts = {"val": seen[:n_val], "test_id": seen[n_val:n_val + n_test],
             "train": seen[n_val + n_test:], "test_ood": ood}
    return [{**r, "split": split} for split in SPLITS for r in parts[split]]


def finalize(rows: list[dict]) -> list[dict]:
    """改寫完成後呼叫：split 內去重、剔除 request 與 train 相同的 val / test_id，最後給 id。"""
    train_reqs = {r["request"] for r in rows if r["split"] == "train"}
    out = []
    for split in SPLITS:
        keys = set()
        for r in rows:
            if r["split"] != split:
                continue
            key = (r["request"], tuple(sorted(r["available_tools"])))
            if key in keys or (split in ("val", "test_id") and r["request"] in train_reqs):
                continue
            keys.add(key)
            out.append({"id": f"{split}-{len(keys) - 1:05d}", **r})
    return out


def main() -> None:
    rows = generate()
    path = REPO / "data" / "raw.jsonl"
    path.parent.mkdir(exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    counts = {s: sum(r["split"] == s for r in rows) for s in SPLITS}
    print(f"寫出 {len(rows)} 筆到 {path}：{counts}")


if __name__ == "__main__":
    main()
