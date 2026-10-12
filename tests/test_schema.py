from planner.schema import parse_output, validate
from planner.tools import render_tools

PLAN = {"action": "plan", "steps": [
    {"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0331"}, "depends_on": []},
    {"id": "s2", "tool": "calc_deadline", "args": {"issue_date": "$s1.issue_date"}, "depends_on": ["s1"]},
]}


def test_parse_output_tolerates_fences_and_trailing_text():
    raw = '```json\n{"action":"refuse","reason":"no_capable_tool"}\n```\n以上。'
    assert parse_output(raw) == {"action": "refuse", "reason": "no_capable_tool"}


def test_parse_output_returns_none_on_garbage():
    assert parse_output("我不知道") is None
    assert parse_output('{"action": "plan", ') is None
    assert parse_output("[1, 2]") is None


def test_valid_plan_passes_strict():
    assert validate(PLAN, available_tools=["get_office_action", "calc_deadline"], strict=True) == []


def test_strict_rejects_tool_not_available():
    errs = validate(PLAN, available_tools=["get_office_action"], strict=True)
    assert any("calc_deadline" in e for e in errs)


def test_cycle_detected():
    bad = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_patent", "args": {"patent_no": "$s2.patent_no"}, "depends_on": ["s2"]},
        {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.patent_no"}, "depends_on": ["s1"]},
    ]}
    assert "相依關係有循環" in validate(bad)


def test_dangling_ref_detected():
    bad = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_patent", "args": {"patent_no": "$s9.patent_no"}, "depends_on": []},
    ]}
    assert any("s9" in e for e in validate(bad))


def test_strict_flags_ref_missing_from_depends_on_and_bad_field():
    bad = {"action": "plan", "steps": [
        PLAN["steps"][0],
        {"id": "s2", "tool": "calc_deadline", "args": {"issue_date": "$s1.deadline"}, "depends_on": []},
    ]}
    errs = validate(bad, strict=True)
    assert any("depends_on" in e for e in errs)
    assert any("deadline" in e for e in errs)


def test_strict_flags_missing_required_param():
    bad = {"action": "plan", "steps": [{"id": "s1", "tool": "amend_claims",
           "args": {"case_id": "TW-2026-0001", "claim_no": 1}, "depends_on": []}]}
    assert any("instruction" in e for e in validate(bad, strict=True))


def test_clarify_and_refuse_shapes():
    assert validate({"action": "clarify", "missing": ["oa_id"]}) == []
    assert validate({"action": "clarify", "missing": []}) != []
    assert validate({"action": "refuse", "reason": "no_capable_tool"}) == []
    assert validate({"action": "dance"}) != []
    assert validate({"action": "plan", "steps": []}) != []


def test_render_tools_marks_optional_params():
    text = render_tools(["search_prior_art"])
    assert "query: str" in text and "top_k?: int" in text and "results[].patent_no" in text


def test_parse_output_skips_braces_in_leading_prose():
    text = '說明 {不是 JSON}。結果：```json\n{"action": "refuse", "reason": "no_capable_tool"}\n```'
    assert parse_output(text) == {"action": "refuse", "reason": "no_capable_tool"}


def test_non_string_depends_on_is_format_error_not_crash():
    bad = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_case", "args": {"case_id": "x"}, "depends_on": [["s1"]]}]}
    assert validate(bad)
