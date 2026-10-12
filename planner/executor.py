"""Executor：依 depends_on 執行 plan，解析 $sN 引用，並印出每步中間結果。工具是 mock，不會呼叫真實系統。"""
import re

from planner.schema import REF_RE

MOCK = {
    "get_case": lambda a: {"application_no": "112100001", "claims": ["一種半導體封裝結構，包含基板與散熱鰭片…"],
                           "oa_ids": ["OA-2026-0331"], "status": "審查中"},
    "get_office_action": lambda a: {"cited_refs": ["I701234", "I705678"],
                                    "rejected_claims": ["一種半導體封裝結構，包含基板…"],
                                    "grounds": "請求項 1 不具進步性", "issue_date": "2026-09-15"},
    "get_patent": lambda a: {"patent_no": a["patent_no"], "title": "封裝基板及其製法",
                             "abstract": "本發明提供一種封裝基板…", "claims": ["一種封裝基板，包含…"]},
    "search_prior_art": lambda a: {"results": [{"patent_no": "I708888"}, {"patent_no": "I702222"}]},
    "compare_claims": lambda a: {"overlap": 0.62, "distinguishing_features": "散熱鰭片的排列結構"},
    "calc_deadline": lambda a: {"deadline": "2026-11-15" if not a.get("extension_months") else "2027-01-15"},
    "amend_claims": lambda a: {"amended_claim": f"（修正後）請求項 {a['claim_no']}：…{a['instruction']}"},
    "draft_response": lambda a: {"draft_id": "DRAFT-0001"},
    "translate_text": lambda a: {"translated": f"[{a['target_lang']}] translated text"},
    "notify_client": lambda a: {"sent": True},
}

# 嵌在句子裡的引用；路徑只收 ASCII，避免把後面的中文吃進去
EMBEDDED = re.compile(r"\$(s\d+)\.([A-Za-z_][A-Za-z0-9_\[\]\.]*[A-Za-z0-9_\]])")


def _walk(results: dict[str, dict], sid: str, path: str):
    cur = results[sid]
    for tok in re.findall(r"[A-Za-z_]\w*|\[\d+\]", path):
        cur = cur[int(tok[1:-1])] if tok.startswith("[") else cur[tok]
    return cur


def resolve(value, results: dict[str, dict]):
    if not isinstance(value, str):
        return value
    if m := REF_RE.match(value):
        return _walk(results, *m.groups())
    return EMBEDDED.sub(lambda m: str(_walk(results, *m.groups())), value)


def execute(plan: dict, log=print) -> dict[str, dict]:
    results: dict[str, dict] = {}
    pending = list(plan["steps"])
    while pending:
        ready = [s for s in pending if all(d in results for d in s["depends_on"])]
        if not ready:
            raise RuntimeError(f"無法繼續執行：{[s['id'] for s in pending]} 的相依無法滿足")
        for s in ready:
            args = {k: resolve(v, results) for k, v in s["args"].items()}
            log(f"▶ {s['id']} {s['tool']}({', '.join(f'{k}={v!r}' for k, v in args.items())})")
            results[s["id"]] = MOCK[s["tool"]](args)
            log(f"  → {results[s['id']]}")
            pending.remove(s)
    return results
