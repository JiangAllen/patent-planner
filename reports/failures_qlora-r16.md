# qlora-r16 失敗案例（隨機 30 筆，seed 0）

## test_ood-00096（test_ood / dag / S22）— ref_arg

- 可用工具：compare_claims, draft_response, search_prior_art, get_office_action, amend_claims
- 需求：OA-2026-1884 要答辯：將 TW-2026-1347 請求項 14 修正為「加入散熱鰭片的結構限定」，再針對核駁理由擬答辯書。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-1884"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2026-1347",
    "claim_no": 14,
    "instruction": "加入散熱鰭片的結構限定"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2026-1884",
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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2026-1347","claim_no":14,"instruction":"加入散熱鰭片的結構限定"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-1884"},"depends_on":[]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2026-1884","arguments":"$s1.amended_claim"},"depends_on":["s1","s2"]}]}
```

觀察：

## test_ood-00100（test_ood / clarify / S26）— wrong_missing

- 可用工具：amend_claims, calc_deadline, compare_claims, get_case
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
{"action":"clarify","missing":["case_id"]}
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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-3719"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":1},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2025-5627","message":"OA-2025-3719的答辯期限已延後1個月，新期限為：$s2.deadline"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00080（test_ood / dag / S22）— missing_step, literal_arg, ref_arg, dependency

- 可用工具：get_office_action, compare_claims, draft_response, amend_claims, search_prior_art
- 需求：先修正 TW-2025-9776 請求項 4（限定封裝層厚度小於 50 微米）的部分，然後依照 OA-2025-6730 的核駁理由撰寫答辯書。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-6730"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-9776",
    "claim_no": 4,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-6730",
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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-9776","claim_no":4,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":[]},{"id":"s2","tool":"draft_response","args":{"oa_id":"OA-2025-6730","arguments":"核駁理由"},"depends_on":[]}]}
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
{"action":"clarify","missing":["claim_text","reference_patent_no"]}
```

觀察：

## test_ood-00098（test_ood / dag / S22）— ref_arg, dependency

- 可用工具：calc_deadline, compare_claims, amend_claims, draft_response, get_office_action
- 需求：OA-2025-7654 要答辯：將 TW-2025-4647 請求項 19 修正為「限定封裝層厚度小於 50 微米」，並針對核駁理由擬答辯書

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-7654"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-4647",
    "claim_no": 19,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-7654",
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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-4647","claim_no":19,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-7654"},"depends_on":[]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2025-7654","arguments":"核駁理由"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00085（test_ood / dag / S22）— missing_step, literal_arg, ref_arg, dependency

- 可用工具：compare_claims, get_patent, calc_deadline, get_office_action, amend_claims, draft_response
- 需求：幫OA-2026-2208準備答辯書，附上TW-2026-0747請求項3的修正：刪除重複的附屬項敘述。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-2208"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2026-0747",
    "claim_no": 3,
    "instruction": "刪除重複的附屬項敘述"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2026-2208",
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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2026-0747","claim_no":3,"instruction":"刪除重複的附屬項敘述"},"depends_on":[]},{"id":"s2","tool":"draft_response","args":{"oa_id":"OA-2026-2208","arguments":"TW-2026-0747請求項3已修正，刪除重複的附屬項敘述"},"depends_on":["s1"]}]}
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

## test_ood-00092（test_ood / dag / S22）— ref_arg, dependency

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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2026-2994","claim_no":8,"instruction":"加入散熱鰭片的結構限定"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-7341"},"depends_on":[]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2026-7341","arguments":"$s2.grounds"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00065（test_ood / chain / S17）— distractor, dependency

- 可用工具：search_prior_art, get_patent, draft_response, get_case, translate_text, get_office_action, notify_client
- 需求：I740982 英文摘要翻譯完後通知 TW-2026-8918 的客戶

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_patent",
   "args": {
    "patent_no": "I740982"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "translate_text",
   "args": {
    "text": "$s1.abstract",
    "target_lang": "en"
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2026-8918",
    "message": "$s2.translated"
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
{"action":"plan","steps":[{"id":"s1","tool":"get_patent","args":{"patent_no":"I740982"},"depends_on":[]},{"id":"s2","tool":"translate_text","args":{"text":"$s1.abstract","target_lang":"en"},"depends_on":["s1"]},{"id":"s3","tool":"get_case","args":{"case_id":"TW-2026-8918"},"depends_on":[]},{"id":"s4","tool":"notify_client","args":{"case_id":"TW-2026-8918","message":"$s2.translated"},"depends_on":["s2","s3"]}]}
```

觀察：

## test_ood-00111（test_ood / clarify / S26）— wrong_missing

- 可用工具：get_office_action, search_prior_art, compare_claims, get_patent, get_case
- 需求：請把我們的請求項1跟前案作一個比對。

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

## test_ood-00041（test_ood / chain / S16）— distractor, ref_arg

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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-0561"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-3491"},"depends_on":[]},{"id":"s3","tool":"calc_deadline","args":{"issue_date":"$s2.issue_date","extension_months":3},"depends_on":["s2"]},{"id":"s4","tool":"notify_client","args":{"case_id":"TW-2025-0561","message":"OA-2025-3491 延期三個月，新的期限為 $s3.deadline"},"depends_on":["s3"]}]}
```

觀察：

## test_ood-00083（test_ood / dag / S22）— missing_step, literal_arg, ref_arg, dependency

- 可用工具：draft_response, amend_claims, translate_text, get_patent, get_office_action, compare_claims, get_case
- 需求：幫 OA-2025-5011 準備答辯書，附上 TW-2025-1437 請求項 7 的修正：加入散熱鰭片的結構限定。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-5011"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-1437",
    "claim_no": 7,
    "instruction": "加入散熱鰭片的結構限定"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-5011",
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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-1437","claim_no":7,"instruction":"加入散熱鰭片的結構限定"},"depends_on":[]},{"id":"s2","tool":"draft_response","args":{"oa_id":"OA-2025-5011","arguments":"$s1.amended_claim"},"depends_on":["s1"]}]}
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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-3892"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":3},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2026-2879","message":"新的答辯期限為：$s2.deadline"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00079（test_ood / dag / S22）— missing_step, literal_arg, ref_arg, dependency

- 可用工具：search_prior_art, draft_response, get_case, calc_deadline, amend_claims, get_office_action
- 需求：為 OA-2026-5453 準備答辯書，附上 TW-2026-9547 請求項 6 的修正：限定封裝層厚度小於 50 微米。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-5453"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2026-9547",
    "claim_no": 6,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2026-5453",
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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2026-9547","claim_no":6,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":[]},{"id":"s2","tool":"draft_response","args":{"oa_id":"OA-2026-5453","arguments":"TW-2026-9547 請求項 6 已修正為封裝層厚度小於 50 微米"},"depends_on":[]}]}
```

觀察：

## test_ood-00042（test_ood / chain / S16）— distractor, ref_arg

- 可用工具：notify_client, calc_deadline, get_case, translate_text, get_office_action
- 需求：幫TW-2026-5702的客戶計算OA-2026-4876延長3個月的期限並通知他們

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-4876"
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
    "case_id": "TW-2026-5702",
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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-5702"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-4876"},"depends_on":[]},{"id":"s3","tool":"calc_deadline","args":{"issue_date":"$s2.issue_date","extension_months":3},"depends_on":["s2"]},{"id":"s4","tool":"notify_client","args":{"case_id":"TW-2026-5702","message":"OA-2026-4876的答辯期限已延長3個月，新期限為：$s3.deadline"},"depends_on":["s3"]}]}
```

觀察：

## test_ood-00086（test_ood / dag / S22）— ref_arg, dependency

- 可用工具：draft_response, get_patent, get_case, get_office_action, search_prior_art, amend_claims
- 需求：OA-2025-3076 要答辯：將 TW-2025-4590 的請求項 5 修正為「加入散熱鰭片的結構限定」，並針對核駁理由擬答辯書。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-3076"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-4590",
    "claim_no": 5,
    "instruction": "加入散熱鰭片的結構限定"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-3076",
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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-4590","claim_no":5,"instruction":"加入散熱鰭片的結構限定"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-3076"},"depends_on":[]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2025-3076","arguments":"$s2.rejected_claims"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00115（test_ood / clarify / S26）— wrong_missing

- 可用工具：compare_claims, translate_text, get_office_action, search_prior_art, get_case, get_patent
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

## test_ood-00033（test_ood / chain / S16）— ref_arg

- 可用工具：get_office_action, notify_client, calc_deadline, draft_response, amend_claims
- 需求：請計算TW-2026-4217客戶的OA-2026-1664期限延長2個月，並通知他們。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-1664"
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
    "case_id": "TW-2026-4217",
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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-1664"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":2},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2026-4217","message":"OA-2026-1664的答辯期限已延長2個月，新期限為：$s2.deadline"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00104（test_ood / clarify / S26）— wrong_missing

- 可用工具：get_case, compare_claims, get_office_action, search_prior_art, notify_client
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

## test_ood-00101（test_ood / clarify / S26）— wrong_missing

- 可用工具：get_case, translate_text, get_office_action, compare_claims
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

## test_ood-00090（test_ood / dag / S22）— ref_arg, dependency

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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-9617","claim_no":12,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-4144"},"depends_on":[]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2025-4144","arguments":"$s2.grounds"},"depends_on":["s2"]}]}
```

觀察：

## test_ood-00045（test_ood / chain / S16）— distractor, ref_arg, dependency

- 可用工具：notify_client, get_case, get_office_action, calc_deadline, compare_claims
- 需求：計算 OA-2026-0380 延長 1 個月後的答辯期限，再通知 TW-2026-0701 的客戶

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-0380"
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
    "case_id": "TW-2026-0701",
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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-0701"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-0380"},"depends_on":[]},{"id":"s3","tool":"calc_deadline","args":{"issue_date":"$s2.issue_date","extension_months":1},"depends_on":["s2"]},{"id":"s4","tool":"notify_client","args":{"case_id":"TW-2026-0701","message":"OA-2026-0380 的答辯期限為 $s3.deadline"},"depends_on":["s1","s3"]}]}
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
{"action":"plan","steps":[{"id":"s1","tool":"amend_claims","args":{"case_id":"TW-2025-7661","claim_no":10,"instruction":"刪除重複的附屬項敘述"},"depends_on":[]},{"id":"s2","tool":"draft_response","args":{"oa_id":"OA-2025-0935","arguments":"根據 OA-2025-0935 的核駁理由撰寫答辯書"},"depends_on":[]}]}
```

觀察：

## test_ood-00082（test_ood / dag / S22）— distractor, ref_arg, dependency

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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-8624"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-9343"},"depends_on":[]},{"id":"s3","tool":"amend_claims","args":{"case_id":"TW-2025-8624","claim_no":15,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":["s1"]},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2025-9343","arguments":"$s1.claims[15]"},"depends_on":["s1"]}]}
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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-5865"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":1},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2026-6572","message":"OA-2026-5865 的答辯期限已延長 1 個月，新期限為：$s2.deadline"},"depends_on":["s2"]}]}
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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-8735"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-9940"},"depends_on":[]},{"id":"s3","tool":"calc_deadline","args":{"issue_date":"$s2.issue_date","extension_months":3},"depends_on":["s2"]},{"id":"s4","tool":"notify_client","args":{"case_id":"TW-2026-8735","message":"OA-2026-9940 的答辯期限已延長 3 個月，新期限為：$s3.deadline"},"depends_on":["s3"]}]}
```

觀察：

## test_ood-00120（test_ood / clarify / S26）— wrong_missing

- 可用工具：calc_deadline, amend_claims, get_case, get_patent, compare_claims
- 需求：請比較一下我們的請求項1與前案。

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
