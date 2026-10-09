"""專利答辯 Agent 的 10 個 mock tool 定義。Planner 只看定義，不會真的執行。"""

# params：參數名 → (型別, 是否必填)
TOOLS: dict[str, dict] = {
    "get_case": {
        "desc": "取得案件資料",
        "params": {"case_id": ("str", True)},
        "returns": ["application_no", "claims", "oa_ids", "status"],
    },
    "get_office_action": {
        "desc": "取得審查意見通知書（OA）",
        "params": {"oa_id": ("str", True)},
        "returns": ["cited_refs", "rejected_claims", "grounds", "issue_date"],
    },
    "get_patent": {
        "desc": "取得專利全文",
        "params": {"patent_no": ("str", True)},
        "returns": ["patent_no", "title", "abstract", "claims"],
    },
    "search_prior_art": {
        "desc": "依關鍵字搜尋先前技術，結果依相關度排序",
        "params": {"query": ("str", True), "date_before": ("str", False), "top_k": ("int", False)},
        "returns": ["results[].patent_no"],
    },
    "compare_claims": {
        "desc": "比對請求項文字與一件引證專利",
        "params": {"claim_text": ("str", True), "reference_patent_no": ("str", True)},
        "returns": ["overlap", "distinguishing_features"],
    },
    "calc_deadline": {
        "desc": "依 OA 發文日計算答辯期限，可指定延長月數",
        "params": {"issue_date": ("str", True), "extension_months": ("int", False)},
        "returns": ["deadline"],
    },
    "amend_claims": {
        "desc": "依指示修正案件的某一項請求項",
        "params": {"case_id": ("str", True), "claim_no": ("int", True), "instruction": ("str", True)},
        "returns": ["amended_claim"],
    },
    "draft_response": {
        "desc": "撰寫答辯書草稿",
        "params": {"oa_id": ("str", True), "arguments": ("str", True), "amendments": ("str", False)},
        "returns": ["draft_id"],
    },
    "translate_text": {
        "desc": "翻譯文字；target_lang 用語言代碼（en、ja、de）",
        "params": {"text": ("str", True), "target_lang": ("str", True)},
        "returns": ["translated"],
    },
    "notify_client": {
        "desc": "傳訊息通知案件的客戶",
        "params": {"case_id": ("str", True), "message": ("str", True)},
        "returns": ["sent"],
    },
}


def render_tools(names: list[str]) -> str:
    """把工具定義轉成 prompt 用的文字，選填參數以 ? 標記。"""
    lines = []
    for name in names:
        tool = TOOLS[name]
        params = ", ".join(f"{p}{'' if req else '?'}: {typ}" for p, (typ, req) in tool["params"].items())
        lines.append(f"- {name}({params}) -> {{{', '.join(tool['returns'])}}}：{tool['desc']}")
    return "\n".join(lines)
