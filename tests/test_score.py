from copy import deepcopy

from evaluation.score import bootstrap_ci, canonical_steps, classify_errors, score_sample

GOLD = {"action": "plan", "steps": [
    {"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-0412"}, "depends_on": []},
    {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0331"}, "depends_on": []},
    {"id": "s3", "tool": "compare_claims",
     "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"},
     "depends_on": ["s1", "s2"]},
]}


def test_identical_plan_is_exact():
    m = score_sample(GOLD, deepcopy(GOLD))
    assert m["exact"] and m["tool_tp"] == 3 and m["lit_ok"] == 2 and m["ref_ok"] == 2


def test_renumbered_and_reordered_plan_is_exact():
    pred = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0331"}, "depends_on": []},
        {"id": "s3", "tool": "compare_claims",
         "args": {"claim_text": "$s2.claims[0]", "reference_patent_no": "$s1.cited_refs[0]"},
         "depends_on": ["s2", "s1"]},
        {"id": "s2", "tool": "get_case", "args": {"case_id": "TW-2026-0412"}, "depends_on": []},
    ]}
    m = score_sample(GOLD, pred)
    assert m["exact"] and m["deps_ok"]
    assert classify_errors(GOLD, pred, m) == []


def test_int_and_str_literals_compare_equal():
    gold = {"action": "plan", "steps": [{"id": "s1", "tool": "amend_claims",
            "args": {"case_id": "TW-2026-0001", "claim_no": 3, "instruction": "x"}, "depends_on": []}]}
    pred = deepcopy(gold)
    pred["steps"][0]["args"]["claim_no"] = "3"
    assert score_sample(gold, pred)["exact"]


def test_wrong_ref_path_is_ref_arg_error():
    pred = deepcopy(GOLD)
    pred["steps"][2]["args"]["claim_text"] = "$s1.claim[0]"
    m = score_sample(GOLD, pred)
    assert not m["exact"] and m["ref_ok"] == 1 and m["ref_n"] == 2
    assert classify_errors(GOLD, pred, m) == ["ref_arg"]


def test_distractor_and_missing_step():
    pred = deepcopy(GOLD)
    pred["steps"][0] = {"id": "s1", "tool": "get_patent", "args": {"patent_no": "TW-2026-0412"}, "depends_on": []}
    m = score_sample(GOLD, pred)
    tags = classify_errors(GOLD, pred, m)
    assert m["distractor"] and {"distractor", "missing_step"} <= set(tags)


def test_missing_dependency_edge():
    pred = deepcopy(GOLD)
    pred["steps"][2]["args"]["reference_patent_no"] = "I700001"
    pred["steps"][2]["depends_on"] = ["s1"]
    m = score_sample(GOLD, pred)
    assert not m["deps_ok"] and {"ref_arg", "dependency"} <= set(classify_errors(GOLD, pred, m))


def test_cycle_in_prediction_does_not_hang():
    pred = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_patent", "args": {"patent_no": "$s2.patent_no"}, "depends_on": ["s2"]},
        {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.patent_no"}, "depends_on": ["s1"]},
    ]}
    m = score_sample(GOLD, pred)
    assert not m["schema_ok"] and classify_errors(GOLD, pred, m) == ["format"]
    assert "<cycle" in "".join(canonical_steps(pred).values())


def test_clarify_scoring():
    gold = {"action": "clarify", "missing": ["oa_id"]}
    assert score_sample(gold, {"action": "clarify", "missing": ["oa_id"]})["exact"]
    pred = {"action": "clarify", "missing": ["issue_date"]}
    m = score_sample(gold, pred)
    assert not m["exact"] and classify_errors(gold, pred, m) == ["wrong_missing"]
    assert m["deps_ok"] is None


def test_action_confusions():
    clarify = {"action": "clarify", "missing": ["oa_id"]}
    refuse = {"action": "refuse", "reason": "no_capable_tool"}
    plan = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0001"}, "depends_on": []}]}
    assert classify_errors(clarify, plan, score_sample(clarify, plan)) == ["hallucinated_args"]
    assert classify_errors(GOLD, refuse, score_sample(GOLD, refuse)) == ["over_refuse"]
    assert classify_errors(GOLD, clarify, score_sample(GOLD, clarify)) == ["over_clarify"]
    assert classify_errors(refuse, plan, score_sample(refuse, plan)) == ["missed_refuse"]


def test_unparseable_prediction():
    m = score_sample(GOLD, None)
    assert not m["parse_ok"] and m["pred_action"] == "invalid"
    assert m["tool_fn"] == 3 and m["ref_n"] == 2 and m["lit_n"] == 2 and m["deps_ok"] is False
    assert classify_errors(GOLD, None, m) == ["format"]


def test_bootstrap_ci_brackets_mean():
    mean, lo, hi = bootstrap_ci([1.0] * 30 + [0.0] * 10)
    assert mean == 0.75 and lo <= mean <= hi and hi - lo > 0


def test_paired_diff_detects_consistent_gain_and_zero_for_identical():
    from evaluation.sensitivity import paired_diff
    a = [0.0] * 50 + [1.0] * 50
    m, lo, hi = paired_diff(a, a)
    assert (m, lo, hi) == (0.0, 0.0, 0.0)
    b = [1.0] * 20 + [0.0] * 30 + [1.0] * 50  # 20 題由錯變對
    m, lo, hi = paired_diff(a, b)
    assert m == 0.2 and 0 < lo < m < hi
