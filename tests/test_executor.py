import pytest

from planner.executor import execute, resolve

PLAN = {"action": "plan", "steps": [
    {"id": "s3", "tool": "compare_claims",
     "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}, "depends_on": ["s1", "s2"]},
    {"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-0412"}, "depends_on": []},
    {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0331"}, "depends_on": []},
]}


def test_resolve_nested_path():
    results = {"s1": {"results": [{"patent_no": "I700001"}]}}
    assert resolve("$s1.results[0].patent_no", results) == "I700001"
    assert resolve("TW-2026-0412", results) == "TW-2026-0412"


def test_resolve_embedded_reference_in_sentence():
    # 模型有時把引用嵌在句子裡（見 evaluation/sensitivity.py），執行時要代入值而不是原樣送出
    assert resolve("新期限為 $s2.deadline，請留意", {"s2": {"deadline": "2026-11-15"}}) == "新期限為 2026-11-15，請留意"


def test_execute_respects_dependencies_regardless_of_order():
    order = []
    results = execute(PLAN, log=lambda msg: order.append(msg))
    assert set(results) == {"s1", "s2", "s3"}
    assert "distinguishing_features" in results["s3"]
    assert [m for m in order if m.startswith("▶")][-1].startswith("▶ s3")


def test_execute_raises_on_unsatisfiable_dependency():
    bad = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_case", "args": {"case_id": "x"}, "depends_on": ["s9"]}]}
    with pytest.raises(RuntimeError):
        execute(bad, log=lambda msg: None)
