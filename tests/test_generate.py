import random
import re
from collections import Counter

from datagen.generate import build_sample, finalize, generate, needed_tools
from datagen.templates import TEMPLATES
from planner.schema import validate
from planner.tools import TOOLS

SLOT_RE = re.compile(r"\{([A-Z0-9]+)\}")


def test_template_inventory():
    assert Counter(t["category"] for t in TEMPLATES) == {
        "single": 5, "parallel": 5, "chain": 7, "dag": 5, "clarify": 4, "refuse": 4}
    hold = [t for t in TEMPLATES if t.get("holdout")]
    assert Counter(t["category"] for t in hold) == {
        "parallel": 1, "chain": 2, "dag": 1, "clarify": 1, "refuse": 1}
    assert len({t["id"] for t in TEMPLATES}) == 30


def test_every_tool_is_seen_in_training_templates():
    seen = {tool for t in TEMPLATES if not t.get("holdout") for tool in needed_tools(t)}
    assert seen == set(TOOLS)


def test_arg_slots_appear_in_every_request_sentence():
    for t in TEMPLATES:
        arg_slots = {m for _, _, args in t.get("steps", []) for v in args.values()
                     if isinstance(v, str) for m in SLOT_RE.findall(v)}
        for sent in t["requests"]:
            assert arg_slots <= set(SLOT_RE.findall(sent)), (t["id"], sent)


def test_clarify_missing_names_are_real_params_of_needed_tools():
    for t in TEMPLATES:
        if t["category"] == "clarify":
            params = {p for n in t["needs"] for p in TOOLS[n]["params"]}
            assert set(t["missing"]) <= params, t["id"]


def test_generated_gold_is_valid_and_consistent():
    rng = random.Random(0)
    for t in TEMPLATES:
        for _ in range(5):
            s = build_sample(t, rng)
            assert all(x in s["request"] for x in s["surfaces"]), t["id"]
            assert len(s["available_tools"]) == len(set(s["available_tools"]))
            if t["category"] == "refuse":
                assert s["gold"] == {"action": "refuse", "reason": "no_capable_tool"}
                if t.get("drop"):
                    assert t["drop"] not in s["available_tools"]
                continue
            assert validate(s["gold"], s["available_tools"], strict=True) == [], t["id"]
            assert set(needed_tools(t)) <= set(s["available_tools"])
            assert 2 <= len(set(s["available_tools"]) - set(needed_tools(t))) <= 4


def test_generate_is_deterministic_and_splits_by_structure():
    a = generate(seed=1, per_seen=24, per_ood=5)
    assert a == generate(seed=1, per_seen=24, per_ood=5)
    ood_ids = {t["id"] for t in TEMPLATES if t.get("holdout")}
    for r in a:
        assert (r["split"] == "test_ood") == (r["structure_id"] in ood_ids)
    assert {r["split"] for r in a} == {"train", "val", "test_id", "test_ood"}


def test_finalize_drops_duplicates_and_train_leakage():
    base = {"category": "single", "structure_id": "S01", "available_tools": ["get_case"],
            "gold": {}, "surfaces": []}
    rows = [{**base, "split": "train", "request": "A"},
            {**base, "split": "train", "request": "A"},
            {**base, "split": "test_id", "request": "A"},
            {**base, "split": "test_id", "request": "B"},
            {**base, "split": "test_ood", "request": "A"}]
    out = finalize(rows)
    assert [(r["split"], r["request"]) for r in out] == [("train", "A"), ("test_id", "B")]
    assert [r["id"] for r in out] == ["train-00000", "test_id-00000"]
