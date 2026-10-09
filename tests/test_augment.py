import json
import random
import re

from datagen.augment import generate_v2, merge
from datagen.generate import build_sample
from datagen.templates import TEMPLATES, TEMPLATES_V2
from planner.schema import validate
from planner.tools import TOOLS

SLOT_RE = re.compile(r"\{([A-Z0-9]+)\}")


def test_v2_templates_are_new_non_holdout_structures():
    assert [t["id"] for t in TEMPLATES_V2] == ["S31", "S32", "S33", "S34", "S35"]
    assert not any(t.get("holdout") for t in TEMPLATES_V2)
    assert not {t["id"] for t in TEMPLATES} & {t["id"] for t in TEMPLATES_V2}


def test_v2_never_copies_a_holdout_structure():
    def sig(t):
        return json.dumps(t.get("steps") or [t.get("needs"), t.get("missing")], sort_keys=True)
    holdout = {sig(t) for t in TEMPLATES if t.get("holdout")}
    assert not {sig(t) for t in TEMPLATES_V2} & holdout
    # S22 的關鍵組合（.grounds 當論點且同時帶 amendments）不得出現在訓練模板
    for t in TEMPLATES_V2:
        for _, tool, args in t.get("steps", []):
            if tool == "draft_response" and "amendments" in args:
                assert not args["arguments"].endswith(".grounds"), t["id"]


def test_v2_covers_the_four_gaps():
    golds = [build_sample(t, random.Random(0))["gold"] for t in TEMPLATES_V2]
    text = json.dumps(golds)
    assert ".grounds" in text
    assert any(s["tool"] == "draft_response" and "amendments" in s["args"]
               for g in golds for s in g.get("steps", []))
    assert sum(len(g.get("missing", [])) == 2 for g in golds) == 2
    # 兩跳：某個需要的工具，其必填參數一個都不在 missing 裡（要問的是上游工具的輸入）
    assert any(not {p for p, (_, req) in TOOLS[n]["params"].items() if req} & set(t["missing"])
               for t in TEMPLATES_V2 if t["category"] == "clarify" for n in t["needs"])


def test_v2_templates_pass_v1_template_checks():
    rng = random.Random(0)
    for t in TEMPLATES_V2:
        arg_slots = {m for _, _, args in t.get("steps", []) for v in args.values()
                     if isinstance(v, str) for m in SLOT_RE.findall(v)}
        for sent in t["requests"]:
            assert arg_slots <= set(SLOT_RE.findall(sent)), (t["id"], sent)
        if t["category"] == "clarify":
            assert set(t["missing"]) <= {p for n in t["needs"] for p in TOOLS[n]["params"]}, t["id"]
            continue
        for _ in range(5):
            s = build_sample(t, rng)
            assert validate(s["gold"], s["available_tools"], strict=True) == [], t["id"]


def test_generate_v2_is_train_only_and_deterministic():
    a = generate_v2(seed=3, per=4)
    assert a == generate_v2(seed=3, per=4)
    assert len(a) == 20 and {r["split"] for r in a} == {"train"}


def test_merge_drops_eval_leakage_and_duplicates():
    base = {"category": "chain", "structure_id": "S31", "available_tools": ["x"], "gold": {}, "split": "train"}
    v1 = [{**base, "id": "train-00000", "request": "A"}]
    new = [{**base, "request": "A"}, {**base, "request": "B"}, {**base, "request": "B"},
           {**base, "request": "C"}]
    out = merge(v1, new, eval_requests={"C"})
    assert [r["request"] for r in out] == ["A", "B"]
    assert [r["id"] for r in out] == ["train-00000", "train-v2-00000"]
