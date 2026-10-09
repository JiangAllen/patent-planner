from planner.prompt import SYSTEM_PROMPT, build_messages, gold_text, pick_shots, sft_messages

GOLD = {"action": "plan", "steps": [
    {"id": "s1", "tool": "get_patent", "args": {"patent_no": "I712345"}, "depends_on": []}]}
S = {"available_tools": ["get_patent", "notify_client"], "request": "調出 I712345",
     "gold": GOLD, "category": "single"}


def test_user_turn_lists_only_available_tools():
    m = build_messages(S)
    assert m[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert "get_patent(" in m[1]["content"] and "notify_client(" in m[1]["content"]
    assert "calc_deadline(" not in m[1]["content"]
    assert m[1]["content"].endswith("需求：調出 I712345")


def test_shots_precede_query():
    m = build_messages(S, [{**S, "request": "範例"}])
    assert [x["role"] for x in m] == ["system", "user", "assistant", "user"]
    assert m[2]["content"] == gold_text(GOLD)
    assert m[3]["content"].endswith("需求：調出 I712345")


def test_sft_ends_with_gold():
    assert sft_messages(S)[-1] == {"role": "assistant", "content": gold_text(GOLD)}
    assert len(sft_messages(S)) == 3


def test_pick_shots_one_per_category_in_file_order():
    rows = [{**S, "category": c, "id": f"x{i}"}
            for i, c in enumerate(["single", "dag", "clarify", "dag", "refuse"])]
    assert [r["id"] for r in pick_shots(rows)] == ["x1", "x2", "x4"]


def test_gold_text_is_compact_and_keeps_chinese():
    assert gold_text({"a": "中"}) == '{"a":"中"}'
