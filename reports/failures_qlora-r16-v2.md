# qlora-r16-v2 失敗案例（隨機 30 筆，seed 0）

## test_ood-00109（test_ood / clarify / S26）— wrong_missing

- 可用工具：calc_deadline, amend_claims, compare_claims, notify_client, get_office_action, get_case
- 需求：請求項1和引證案有什麼不同？

gold：
```json
{
 "action": "clarify",
 "missing": [
  "case_id",
  "reference_patent_no"
 ]
}
```
預測：
```
{"action":"clarify","missing":["reference_patent_no"]}
```

觀察：

## test_ood-00113（test_ood / clarify / S26）— wrong_missing

- 可用工具：get_patent, calc_deadline, get_case, compare_claims
- 需求：把我們的請求項1跟前案比較一下

gold：
```json
{
 "action": "clarify",
 "missing": [
  "case_id",
  "reference_patent_no"
 ]
}
```
預測：
```
{"action":"clarify","missing":["patent_no"]}
```

觀察：

## test_ood-00030（test_ood / chain / S16）— ref_arg

- 可用工具：get_patent, draft_response, get_office_action, notify_client, search_prior_art, calc_deadline
- 需求：幫 TW-2026-6572 的客戶計算 OA-2026-5865 延長 1 個月的期限並通知他們

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-5865"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s1.issue_date",
    "extension_months": 1
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2026-6572",
    "message": "$s2.deadline"
   },
   "depends_on": [
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-5865"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":1},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2026-6572","message":"OA-2026-5865 的答辯期限已延長至 $s2.deadline"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00090（test_ood / dag / S22）— distractor, dependency

- 可用工具：draft_response, amend_claims, get_case, get_office_action, calc_deadline, search_prior_art, get_patent
- 需求：先修正 TW-2025-9617 請求項 12（限定封裝層厚度小於 50 微米），然後依照 OA-2025-4144 的核駁理由撰寫答辯書。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-4144"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-9617",
    "claim_no": 12,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-4144",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-9617"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-4144"},"depends_on":[]},{"id":"s3","tool":"amend_claims","args":{"case_id":"TW-2025-9617","claim_no":12,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":["s1"]},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2025-4144","arguments":"$s2.grounds","amendments":"$s3.amended_claim"},"depends_on":["s2","s3"]}]}
```

觀察：

## test_ood-00122（test_ood / clarify / S26）— wrong_missing

- 可用工具：amend_claims, compare_claims, calc_deadline, get_case, draft_response
- 需求：請求項1和引證案有哪些不同？

gold：
```json
{
 "action": "clarify",
 "missing": [
  "case_id",
  "reference_patent_no"
 ]
}
```
預測：
```
{"action":"clarify","missing":["case_id"]}
```

觀察：

## test_ood-00082（test_ood / dag / S22）— distractor, missing_step, literal_arg, ref_arg, dependency

- 可用工具：amend_claims, translate_text, get_case, get_office_action, get_patent, draft_response
- 需求：幫 OA-2025-9343 準備答辯書，附上 TW-2025-8624 請求項 15 的修正：限定封裝層厚度小於 50 微米

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-9343"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-8624",
    "claim_no": 15,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-9343",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-8624"},"depends_on":[]},{"id":"s2","tool":"amend_claims","args":{"case_id":"TW-2025-8624","claim_no":15,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":[]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2025-9343","arguments":"$s1.claims[0]","amendments":"$s2.amended_claim"},"depends_on":["s1","s2"]}]}
```

觀察：

## test_ood-00118（test_ood / clarify / S26）— wrong_missing

- 可用工具：get_patent, compare_claims, draft_response, get_case
- 需求：請求項1和引證案有什麼不同？

gold：
```json
{
 "action": "clarify",
 "missing": [
  "case_id",
  "reference_patent_no"
 ]
}
```
預測：
```
{"action":"clarify","missing":["claim_text","reference_patent_no"]}
```

觀察：

## test_ood-00110（test_ood / clarify / S26）— wrong_missing

- 可用工具：notify_client, get_case, search_prior_art, compare_claims
- 需求：請幫我比對本案的請求項1與先前技術。

gold：
```json
{
 "action": "clarify",
 "missing": [
  "case_id",
  "reference_patent_no"
 ]
}
```
預測：
```
{"action":"clarify","missing":["case_id"]}
```

觀察：

## test_ood-00142（test_ood / refuse / S30）— missed_refuse

- 可用工具：get_case, get_office_action, notify_client, get_patent, translate_text
- 需求：OA-2025-1683 最遲什麼時候要回？

gold：
```json
{
 "action": "refuse",
 "reason": "no_capable_tool"
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-1683"},"depends_on":[]},{"id":"s2","tool":"get_case","args":{"case_id":"$s1.application_no"},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"$s2.application_no","message":"OA 最遲回函日期為 $s1.issue_date"},"depends_on":["s2","s1"]}]}
```

觀察：

## test_ood-00075（test_ood / dag / S22）— missing_step, literal_arg, ref_arg, dependency

- 可用工具：draft_response, amend_claims, get_office_action, notify_client, compare_claims, get_patent, calc_deadline
- 需求：請為 OA-2025-5228 準備答辯書，並附上 TW-2025-9027 請求項 8 的修正：限定封裝層厚度小於 50 微米。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-5228"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-9027",
    "claim_no": 8,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-5228",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-9027","claim_no":8,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":[]},{"id":"s2","tool":"draft_response","args":{"oa_id":"OA-2025-5228","arguments":"$s1.amended_claim"},"depends_on":["s1"]}]}
```

觀察：

## test_ood-00087（test_ood / dag / S22）— missing_step, literal_arg, ref_arg, dependency

- 可用工具：calc_deadline, get_patent, get_office_action, draft_response, compare_claims, search_prior_art, amend_claims
- 需求：先修正 TW-2025-0197 的請求項 1（刪除重複的附屬項敘述），然後依 OA-2025-4789 的核駁理由擬寫答辯書。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-4789"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-0197",
    "claim_no": 1,
    "instruction": "刪除重複的附屬項敘述"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-4789",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-0197","claim_no":1,"instruction":"刪除重複的附屬項敘述"},"depends_on":[]},{"id":"s2","tool":"draft_response","args":{"oa_id":"OA-2025-4789","arguments":"$s1.amended_claim"},"depends_on":["s1"]}]}
```

觀察：

## test_ood-00078（test_ood / dag / S22）— distractor, dependency

- 可用工具：amend_claims, draft_response, calc_deadline, get_case, get_office_action, search_prior_art
- 需求：OA-2026-6819 要答辯：將 TW-2026-8267 請求項 15 修正為「加入散熱鰭片的結構限定」，再針對核駁理由擬答辯書。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-6819"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2026-8267",
    "claim_no": 15,
    "instruction": "加入散熱鰭片的結構限定"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2026-6819",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-8267"},"depends_on":[]},{"id":"s2","tool":"amend_claims","args":{"case_id":"TW-2026-8267","claim_no":15,"instruction":"加入散熱鰭片的結構限定"},"depends_on":["s1"]},{"id":"s3","tool":"get_office_action","args":{"oa_id":"OA-2026-6819"},"depends_on":[]},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2026-6819","arguments":"$s3.grounds","amendments":"$s2.amended_claim"},"depends_on":["s2","s3"]}]}
```

觀察：

## test_ood-00095（test_ood / dag / S22）— distractor, missing_step, literal_arg, ref_arg, dependency

- 可用工具：get_patent, amend_claims, translate_text, search_prior_art, get_office_action, draft_response, compare_claims
- 需求：OA-2026-4580 要答辯：將 TW-2026-0256 請求項 18 修正為「刪除重複的附屬項敘述」，再針對核駁理由擬答辯書

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-4580"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2026-0256",
    "claim_no": 18,
    "instruction": "刪除重複的附屬項敘述"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2026-4580",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case(case_id)","args":{"case_id":"TW-2026-0256"},"depends_on":[]},{"id":"s2","tool":"amend_claims","args":{"case_id":"TW-2026-0256","claim_no":18,"instruction":"刪除重複的附屬項敘述"},"depends_on":["s1"]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2026-4580","arguments":"$s2.amended_claim"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00041（test_ood / chain / S16）— ref_arg

- 可用工具：get_case, compare_claims, translate_text, notify_client, calc_deadline, draft_response, get_office_action
- 需求：OA-2025-3491 申請延期3個月，新的期限確定後通知TW-2025-0561的客戶

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-3491"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s1.issue_date",
    "extension_months": 3
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2025-0561",
    "message": "$s2.deadline"
   },
   "depends_on": [
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-3491"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":3},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2025-0561","message":"新的答辯期限為 $s2.deadline"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00089（test_ood / dag / S22）— distractor, missing_step, literal_arg, ref_arg, dependency

- 可用工具：calc_deadline, get_office_action, get_patent, amend_claims, draft_response, compare_claims, notify_client
- 需求：OA-2026-7614 要答辯：將 TW-2026-7871 請求項 7 修正為「限定封裝層厚度小於 50 微米」，再針對核駁理由擬答辯書

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-7614"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2026-7871",
    "claim_no": 7,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2026-7614",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_patent","args":{"patent_no":"TW-2026-7871"},"depends_on":[]},{"id":"s2","tool":"amend_claims","args":{"case_id":"TW-2026-7871","claim_no":7,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":["s1"]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2026-7614","arguments":"$s2.amended_claim"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00034（test_ood / chain / S16）— distractor, ref_arg

- 可用工具：search_prior_art, get_case, draft_response, get_office_action, notify_client, calc_deadline
- 需求：請幫 TW-2025-9888 的客戶計算 OA-2025-7070 延長1個月的期限並通知他們。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-7070"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s1.issue_date",
    "extension_months": 1
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2025-9888",
    "message": "$s2.deadline"
   },
   "depends_on": [
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-9888"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-7070"},"depends_on":[]},{"id":"s3","tool":"calc_deadline","args":{"issue_date":"$s2.issue_date","extension_months":1},"depends_on":["s2"]},{"id":"s4","tool":"notify_client","args":{"case_id":"TW-2025-9888","message":"OA-2025-7070 的答辯期限已延長至 $s3.deadline"},"depends_on":["s3"]}]}
```

觀察：

## test_ood-00048（test_ood / chain / S16）— ref_arg

- 可用工具：notify_client, get_patent, calc_deadline, get_office_action, compare_claims, get_case
- 需求：OA-2026-8200 申請延期 3 個月，新的期限確定後通知 TW-2026-8209 的客戶

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-8200"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s1.issue_date",
    "extension_months": 3
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2026-8209",
    "message": "$s2.deadline"
   },
   "depends_on": [
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-8200"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":3},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2026-8209","message":"新的答辯期限為 $s2.deadline"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00112（test_ood / clarify / S26）— wrong_missing

- 可用工具：calc_deadline, search_prior_art, compare_claims, get_case
- 需求：請幫我比對本案請求項1與先前技術。

gold：
```json
{
 "action": "clarify",
 "missing": [
  "case_id",
  "reference_patent_no"
 ]
}
```
預測：
```
{"action":"clarify","missing":["case_id"]}
```

觀察：

## test_ood-00108（test_ood / clarify / S26）— wrong_missing

- 可用工具：get_case, notify_client, translate_text, search_prior_art, draft_response, compare_claims
- 需求：請求項1和引證案有哪些不同？

gold：
```json
{
 "action": "clarify",
 "missing": [
  "case_id",
  "reference_patent_no"
 ]
}
```
預測：
```
{"action":"clarify","missing":["claim_text","reference_patent_no"]}
```

觀察：

## test_ood-00031（test_ood / chain / S16）— ref_arg, dependency

- 可用工具：calc_deadline, amend_claims, get_office_action, search_prior_art, notify_client, get_case, get_patent
- 需求：算出 OA-2025-5607 延長 2 個月後的答辯期限，再通知 TW-2025-4794 的客戶。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-5607"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s1.issue_date",
    "extension_months": 2
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2025-4794",
    "message": "$s2.deadline"
   },
   "depends_on": [
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-5607"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":2},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2025-4794","message":"已計算答辯期限"},"depends_on":[]}]}
```

觀察：

## test_ood-00099（test_ood / dag / S22）— distractor, dependency

- 可用工具：amend_claims, get_patent, get_case, draft_response, get_office_action
- 需求：先修正 TW-2025-1588 請求項 13（限定封裝層厚度小於 50 微米）的部分，接著按照 OA-2025-8358 的核駁理由撰寫答辯書。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-8358"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-1588",
    "claim_no": 13,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-8358",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-1588"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-8358"},"depends_on":[]},{"id":"s3","tool":"amend_claims","args":{"case_id":"TW-2025-1588","claim_no":13,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":["s1"]},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2025-8358","arguments":"$s2.grounds","amendments":"$s3.amended_claim"},"depends_on":["s2","s3"]}]}
```

觀察：

## test_ood-00046（test_ood / chain / S16）— distractor, ref_arg

- 可用工具：amend_claims, get_office_action, get_case, notify_client, translate_text, calc_deadline
- 需求：幫 TW-2026-8735 的客戶計算 OA-2026-9940 延長 3 個月的期限並通知他們

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-9940"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s1.issue_date",
    "extension_months": 3
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2026-8735",
    "message": "$s2.deadline"
   },
   "depends_on": [
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-8735"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-9940"},"depends_on":[]},{"id":"s3","tool":"calc_deadline","args":{"issue_date":"$s2.issue_date","extension_months":3},"depends_on":["s2"]},{"id":"s4","tool":"notify_client","args":{"case_id":"TW-2026-8735","message":"OA-2026-9940 的答辯期限已延長至 $s3.deadline"},"depends_on":["s3"]}]}
```

觀察：

## test_ood-00092（test_ood / dag / S22）— distractor, missing_step, literal_arg, ref_arg, dependency

- 可用工具：get_office_action, compare_claims, get_case, translate_text, search_prior_art, amend_claims, draft_response
- 需求：OA-2026-7341 要答辯：將 TW-2026-2994 請求項 8 修正為「加入散熱鰭片的結構限定」，再根據核駁理由擬答辯書

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-7341"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2026-2994",
    "claim_no": 8,
    "instruction": "加入散熱鰭片的結構限定"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2026-7341",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-2994"},"depends_on":[]},{"id":"s2","tool":"amend_claims","args":{"case_id":"TW-2026-2994","claim_no":8,"instruction":"加入散熱鰭片的結構限定"},"depends_on":["s1"]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2026-7341","arguments":"$s2.amended_claim"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00097（test_ood / dag / S22）— missing_step, literal_arg, ref_arg, dependency

- 可用工具：get_case, get_office_action, notify_client, amend_claims, get_patent, draft_response, search_prior_art
- 需求：請準備答辯書，並附上 TW-2025-2206 請求項 15 的修正：限定封裝層厚度小於 50 微米（OA-2025-5046）

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-5046"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-2206",
    "claim_no": 15,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-5046",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-2206","claim_no":15,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":[]},{"id":"s2","tool":"draft_response","args":{"oa_id":"OA-2025-5046","arguments":"$s1.amended_claim"},"depends_on":["s1"]}]}
```

觀察：

## test_ood-00036（test_ood / chain / S16）— ref_arg

- 可用工具：notify_client, get_office_action, compare_claims, calc_deadline, get_patent, translate_text
- 需求：OA-2026-3892 申請延期3個月，新的期限計算好後通知TW-2026-2879的客戶。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-3892"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s1.issue_date",
    "extension_months": 3
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2026-2879",
    "message": "$s2.deadline"
   },
   "depends_on": [
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-3892"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":3},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2026-2879","message":"新的答辯期限為 $s2.deadline"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00121（test_ood / clarify / S26）— wrong_missing

- 可用工具：get_case, get_patent, draft_response, search_prior_art, compare_claims, calc_deadline
- 需求：請把我們的請求項1跟前案作比對一下。

gold：
```json
{
 "action": "clarify",
 "missing": [
  "case_id",
  "reference_patent_no"
 ]
}
```
預測：
```
{"action":"clarify","missing":["patent_no"]}
```

觀察：

## test_ood-00144（test_ood / refuse / S30）— missed_refuse

- 可用工具：get_case, get_patent, search_prior_art, get_office_action, notify_client
- 需求：請閱讀 OA-2025-6008，然後計算答辯期限。

gold：
```json
{
 "action": "refuse",
 "reason": "no_capable_tool"
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-6008"},"depends_on":[]},{"id":"s2","tool":"calculate_response_deadline","args":{"oa_data":"$s1.grounds"},"depends_on":["s1"]}]}
```

觀察：

## test_ood-00029（test_ood / chain / S16）— ref_arg

- 可用工具：search_prior_art, notify_client, get_patent, translate_text, compare_claims, calc_deadline, get_office_action
- 需求：幫TW-2025-5627的客戶計算OA-2025-3719延後1個月的期限並通知他們

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-3719"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s1.issue_date",
    "extension_months": 1
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2025-5627",
    "message": "$s2.deadline"
   },
   "depends_on": [
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-3719"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":1},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2025-5627","message":"OA-2025-3719的答辯期限已延後1個月，新期限為 $s2.deadline"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00077（test_ood / dag / S22）— missing_step, literal_arg, ref_arg, dependency

- 可用工具：amend_claims, draft_response, translate_text, get_office_action, calc_deadline
- 需求：先修正 TW-2025-7661 的請求項 10（刪除重複的附屬項敘述），然後根據 OA-2025-0935 的核駁理由撰寫答辯書。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-0935"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-7661",
    "claim_no": 10,
    "instruction": "刪除重複的附屬項敘述"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-0935",
    "arguments": "$s1.grounds",
    "amendments": "$s2.amended_claim"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-7661","claim_no":10,"instruction":"刪除重複的附屬項敘述"},"depends_on":[]},{"id":"s2","tool":"draft_response","args":{"oa_id":"OA-2025-0935","arguments":"$s1.amended_claim"},"depends_on":["s1"]}]}
```

觀察：

## test_ood-00117（test_ood / clarify / S26）— wrong_missing

- 可用工具：get_case, get_office_action, compare_claims, notify_client
- 需求：把我們的請求項1跟前案比較一下

gold：
```json
{
 "action": "clarify",
 "missing": [
  "case_id",
  "reference_patent_no"
 ]
}
```
預測：
```
{"action":"clarify","missing":["reference_patent_no"]}
```

觀察：
