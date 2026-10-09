# fewshot 失敗案例（隨機 30 筆，seed 0）

## test_ood-00083（test_ood / dag / S22）— distractor, ref_arg, dependency

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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-1437"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-5011"},"depends_on":[]},{"id":"s3","tool":"amend_claims","args":{"case_id":"TW-2025-1437","claim_no":7,"instruction":"加入散熱鰭片的結構限定"},"depends_on":["s1"]},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2025-5011","arguments":"請求項已修正，新增散熱鰭片結構限定以區別於前案","amendments":"$s3.amended_claim"},"depends_on":["s2","s3"]}]}}
```

觀察：

## test_ood-00092（test_ood / dag / S22）— distractor, ref_arg, dependency

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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-2994"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-7341"},"depends_on":[]},{"id":"s3","tool":"amend_claims","args":{"case_id":"TW-2026-2994","claim_no":8,"instruction":"加入散熱鰭片的結構限定"},"depends_on":["s1"]},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2026-7341","arguments":"請求項已修正為包含散熱鰭片結構，符合新技術特徵，應予以接受"},"depends_on":["s2","s3"]}]}
```

觀察：

## test_id-00031（test_id / refuse / S28）— missed_refuse

- 可用工具：notify_client, search_prior_art, compare_claims, get_patent
- 需求：請提供I768892的英文摘要。

gold：
```json
{
 "action": "refuse",
 "reason": "no_capable_tool"
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_patent","args":{"patent_no":"I768892"},"depends_on":[]}]}
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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-3892"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":3},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2026-2879","message":"已為OA-2026-3892申請延期3個月，新的答辯期限為 $s2.deadline。"},"depends_on":["s2"]}]}}
```

觀察：

## test_ood-00115（test_ood / clarify / S26）— hallucinated_args

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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-7963"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-1710"},"depends_on":[]},{"id":"s3","tool":"compare_claims","args":{"claim_text":"$s1.claims[0]","reference_patent_no":"$s2.cited_refs[0]"},"depends_on":["s1","s2"]}]}
```

觀察：

## test_ood-00109（test_ood / clarify / S26）— hallucinated_args

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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-2239"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-1710"},"depends_on":[]},{"id":"s3","tool":"compare_claims","args":{"claim_text":"$s1.claims[0]","reference_patent_no":"$s2.cited_refs[0]"},"depends_on":["s1","s2"]}]}
```

觀察：

## test_ood-00088（test_ood / dag / S22）— distractor, missing_step, literal_arg, ref_arg, dependency

- 可用工具：amend_claims, get_office_action, draft_response, compare_claims, notify_client, calc_deadline, translate_text
- 需求：幫 OA-2025-2138 準備答辯書，附上 TW-2025-7607 請求項 14 的修正：加入散熱鰭片的結構限定。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-2138"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2025-7607",
    "claim_no": 14,
    "instruction": "加入散熱鰭片的結構限定"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-2138",
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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-2138"},"depends_on":[]},{"id":"s2","tool":"get_case","args":{"case_id":"TW-2025-7607"},"depends_on":[]},{"id":"s3","tool":"compare_claims","args":{"claim_text":"$s2.claims[13]","reference_patent_no":"$s1.cited_refs[0]"},"depends_on":["s1","s2"]},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2025-2138","arguments":"本申請案請求項 14 已修正為包含散熱鰭片結構，以克服先前技術之缺陷。","amendments":"請求項 14 改為：包含散熱鰭片，其結構為由金屬材質製成，且表面具有微細紋路以增強熱傳導。"},"depends_on":["s3"]}]}}
```

觀察：

## test_ood-00047（test_ood / chain / S16）— ref_arg

- 可用工具：notify_client, get_office_action, translate_text, calc_deadline, compare_claims
- 需求：請幫 TW-2026-7744 的客戶計算 OA-2026-2323 延長 3 個月的期限並通知他們。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-2323"
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
    "case_id": "TW-2026-7744",
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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-2323"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":3},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2026-7744","message":"已計算延長 3 個月的答辯期限，新期限為 $s2.deadline。"},"depends_on":["s2"]}]}}
```

觀察：

## test_ood-00107（test_ood / clarify / S26）— hallucinated_args

- 可用工具：search_prior_art, notify_client, compare_claims, get_case, calc_deadline, amend_claims
- 需求：請把我們的請求項1跟前案做一下比對。

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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-2239"},"depends_on":[]},{"id":"s2","tool":"search_prior_art","args":{"query":"related technology","top_k":1},"depends_on":[]},{"id":"s3","tool":"compare_claims","args":{"claim_text":"$s1.claims[0]","reference_patent_no":"$s2.results[0].patent_no"},"depends_on":["s1","s2"]}]}
```

觀察：

## test_ood-00076（test_ood / dag / S22）— distractor, ref_arg, dependency

- 可用工具：get_patent, get_case, get_office_action, draft_response, calc_deadline, amend_claims
- 需求：請準備 OA-2026-5772 的答辯書，並附上 TW-2026-3806 請求項 9 的修正：限定封裝層厚度小於 50 微米。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-5772"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2026-3806",
    "claim_no": 9,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2026-5772",
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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-3806"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-5772"},"depends_on":[]},{"id":"s3","tool":"amend_claims","args":{"case_id":"TW-2026-3806","claim_no":9,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":["s1"]},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2026-5772","arguments":"請求項已修正封裝層厚度限制，符合專利新穎性與實用性要求，請審查通過。","amendments":"$s3.amended_claim"},"depends_on":["s2","s3"]}]}}
```

觀察：

## test_ood-00134（test_ood / refuse / S30）— missed_refuse

- 可用工具：amend_claims, translate_text, get_patent, get_office_action
- 需求：OA-2025-1977 最晚什麼時候要回報？

gold：
```json
{
 "action": "refuse",
 "reason": "no_capable_tool"
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-1977"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date"},"depends_on":["s1"]}]}"
```

觀察：

## test_ood-00025（test_ood / chain / S16）— ref_arg

- 可用工具：translate_text, amend_claims, calc_deadline, get_office_action, notify_client
- 需求：OA-2026-2528申請延期2個月，新的期限計算好後告訴TW-2026-3938的客戶

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-2528"
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
    "case_id": "TW-2026-3938",
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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-2528"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":2},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2026-3938","message":"已為OA-2026-2528申請延期2個月，新的答辯期限為 $s2.deadline。"},"depends_on":["s2"]}]}}
```

觀察：

## test_ood-00114（test_ood / clarify / S26）— format

- 可用工具：calc_deadline, translate_text, compare_claims, get_patent, get_case
- 需求：請幫我比較本案請求項1與先前技術。

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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-2239"},"depends_on":[]},{"id":"s2","tool":"get_patent","args":{"patent_no":"TW-2024-1122"}},"depends_on":["s1"]},{"id":"s3","tool":"compare_claims","args":{"claim_text":"$s1.claims[0]","reference_patent_no":"$s2.patent_no"},"depends_on":["s1","s2"]}]}}
```

觀察：

## test_id-00091（test_id / single / S04）— other

- 可用工具：translate_text, compare_claims, get_office_action, search_prior_art, draft_response
- 需求：查找一些關於覆晶接合的先前案例

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "search_prior_art",
   "args": {
    "query": "覆晶接合"
   },
   "depends_on": []
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"search_prior_art","args":{"query":"覆晶接合","top_k":5},"depends_on":[]}]}
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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-5702"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2026-4876"},"depends_on":[]},{"id":"s3","tool":"calc_deadline","args":{"issue_date":"$s2.issue_date","extension_months":3},"depends_on":["s2"]},{"id":"s4","tool":"notify_client","args":{"case_id":"TW-2026-5702","message":"已計算延長3個月的答辯期限，新期限為 $s3.deadline。"},"depends_on":["s3"]}]}}
```

觀察：

## test_ood-00135（test_ood / refuse / S30）— missed_refuse

- 可用工具：compare_claims, notify_client, get_office_action, draft_response
- 需求：閱讀OA-2025-7570，然後計算答辯期限。

gold：
```json
{
 "action": "refuse",
 "reason": "no_capable_tool"
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-7570"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date"},"depends_on":["s1"]}]}"
```

觀察：

## test_id-00063（test_id / chain / S13）— format

- 可用工具：calc_deadline, translate_text, notify_client, get_office_action, get_case
- 需求：查 TW-2026-0059 的第一份審查意見，計算答辯期限

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_case",
   "args": {
    "case_id": "TW-2026-0059"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "get_office_action",
   "args": {
    "oa_id": "$s1.oa_ids[0]"
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s2.issue_date"
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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-0059"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"$s1.oa_ids[0]"},"depends_on":["s1"},{"id":"s3","tool":"calc_deadline","args":{"issue_date":"$s2.issue_date"},"depends_on":["s2"]}]}}
```

觀察：

## test_ood-00034（test_ood / chain / S16）— ref_arg

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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-7070"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"$s1.issue_date","extension_months":1},"depends_on":["s1"]},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2025-9888","message":"已為您的案件 OA-2025-7070 延長1個月，新期限為 $s2.deadline。"},"depends_on":["s2"]}]}}
```

觀察：

## test_ood-00121（test_ood / clarify / S26）— hallucinated_args

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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-2239"},"depends_on":[]},{"id":"s2","tool":"search_prior_art","args":{"query":"請求項1","top_k":1},"depends_on":[]},{"id":"s3","tool":"compare_claims","args":{"claim_text":"$s1.claims[0]","reference_patent_no":"$s2.results[0].patent_no"},"depends_on":["s1","s2"]}]}
```

觀察：

## test_id-00097（test_id / parallel / S09）— distractor, literal_arg, dependency

- 可用工具：get_patent, get_office_action, notify_client, translate_text, amend_claims, get_case
- 需求：通知 TW-2026-6513 的客戶「修正本已送出」，並順便把請求項 16「限定封裝層厚度小於 50 微米」確認一下。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "amend_claims",
   "args": {
    "case_id": "TW-2026-6513",
    "claim_no": 16,
    "instruction": "限定封裝層厚度小於 50 微米"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2026-6513",
    "message": "修正本已送出"
   },
   "depends_on": []
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-6513"},"depends_on":[]},{"id":"s2","tool":"notify_client","args":{"case_id":"TW-2026-6513","message":"修正本已送出"},"depends_on":["s1"]},{"id":"s3","tool":"amend_claims","args":{"case_id":"TW-2026-6513","claim_no":16,"instruction":"確認請求項 16 的內容"},"depends_on":["s1"]}]}"
```

觀察：

## test_ood-00049（test_ood / chain / S16）— missing_step, literal_arg, ref_arg, dependency

- 可用工具：translate_text, get_office_action, calc_deadline, draft_response, notify_client
- 需求：算出OA-2026-8921延長1個月後的答辯期限，再通知TW-2026-3205的客戶。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2026-8921"
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
    "case_id": "TW-2026-3205",
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
{"action":"plan","steps":[{"id":"s1","tool":"calc_deadline","args":{"issue_date":"2026-04-01","extension_months":1},"depends_on":[]},{"id":"s2","tool":"notify_client","args":{"case_id":"TW-2026-3205","message":"已計算延長1個月的答辯期限，期限為 $s1.deadline"},"depends_on":["s1"]}]}"
```

觀察：

## test_id-00066（test_id / chain / S13）— format

- 可用工具：translate_text, notify_client, get_office_action, calc_deadline, amend_claims, get_case
- 需求：TW-2025-3008 收到的第一份OA最晚何時需要答辯？

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_case",
   "args": {
    "case_id": "TW-2025-3008"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "get_office_action",
   "args": {
    "oa_id": "$s1.oa_ids[0]"
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "$s2.issue_date"
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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-3008"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"$s1.oa_ids[0]"},"depends_on":["s1"},{"id":"s3","tool":"calc_deadline","args":{"issue_date":"$s2.issue_date"},"depends_on":["s2"]}]}}
```

觀察：

## test_id-00050（test_id / dag / S20）— format

- 可用工具：notify_client, get_case, translate_text, compare_claims, draft_response, get_office_action
- 需求：請比較 TW-2025-8255 請求項 1 和 OA-2025-1259 的第一件引證，再依據差異擬寫答辨書。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_case",
   "args": {
    "case_id": "TW-2025-8255"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "get_office_action",
   "args": {
    "oa_id": "OA-2025-1259"
   },
   "depends_on": []
  },
  {
   "id": "s3",
   "tool": "compare_claims",
   "args": {
    "claim_text": "$s1.claims[0]",
    "reference_patent_no": "$s2.cited_refs[0]"
   },
   "depends_on": [
    "s1",
    "s2"
   ]
  },
  {
   "id": "s4",
   "tool": "draft_response",
   "args": {
    "oa_id": "OA-2025-1259",
    "arguments": "$s3.distinguishing_features"
   },
   "depends_on": [
    "s3"
   ]
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2025-8255"},"depends_on":[]},{"id":"s2","tool":"get_office_action","args":{"oa_id":"OA-2025-1259"},"depends_on":[]},{"id":"s3","tool":"compare_claims","args":{"claim_text":"$s1.claims[0]","reference_patent_no":"$s2.cited_refs[0]"},"depends_on":["s1","s2"},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2025-1259","arguments":"$s3.distinguishing_features"},"depends_on":["s3"]}]}}
```

觀察：

## test_ood-00061（test_ood / chain / S17）— format

- 可用工具：get_office_action, get_case, get_patent, notify_client, search_prior_art, translate_text
- 需求：將I791254的摘要翻譯成德文並傳給TW-2025-9363客戶

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_patent",
   "args": {
    "patent_no": "I791254"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "translate_text",
   "args": {
    "text": "$s1.abstract",
    "target_lang": "de"
   },
   "depends_on": [
    "s1"
   ]
  },
  {
   "id": "s3",
   "tool": "notify_client",
   "args": {
    "case_id": "TW-2025-9363",
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
{"action":"plan","steps":[{"id":"s1","tool":"get_patent","args":{"patent_no":"I791254"},"depends_on":[]},{"id":"s2","tool":"translate_text","args":{"text":"$s1.abstract","target_lang":"de"},"depends_on":["s1"},{"id":"s3","tool":"notify_client","args":{"case_id":"TW-2025-9363","message":"$s2.translated"},"depends_on":["s2"]}]}}
```

觀察：

## test_ood-00105（test_ood / clarify / S26）— format

- 可用工具：translate_text, compare_claims, search_prior_art, get_case, get_office_action
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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"本案"}},"depends_on":[]},{"id":"s2","tool":"search_prior_art","args":{"query":"本案請求項1相關技術","top_k":1},"depends_on":[]},{"id":"s3","tool":"compare_claims","args":{"claim_text":"$s1.claims[0]","reference_patent_no":"$s2.results[0].patent_no"},"depends_on":["s1","s2"]}]}}
```

觀察：

## test_ood-00127（test_ood / refuse / S30）— missed_refuse

- 可用工具：draft_response, get_office_action, get_case
- 需求：請幫我計算 OA-2025-4808 的答辨期限。

gold：
```json
{
 "action": "refuse",
 "reason": "no_capable_tool"
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-4808"},"depends_on":[]}]}
```

觀察：

## test_ood-00075（test_ood / dag / S22）— distractor, ref_arg, dependency

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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2025-5228"},"depends_on":[]},{"id":"s2","tool":"get_case","args":{"case_id":"TW-2025-9027"},"depends_on":[]},{"id":"s3","tool":"amend_claims","args":{"case_id":"TW-2025-9027","claim_no":8,"instruction":"限定封裝層厚度小於 50 微米"},"depends_on":["s2"]},{"id":"s4","tool":"draft_response","args":{"oa_id":"OA-2025-5228","arguments":"請求項已修正為封裝層厚度小於 50 微米，符合專利新穎性與實用性要求，請求接受審查。","amendments":"$s3.amended_claim"},"depends_on":["s1","s3"]}]}}
```

觀察：

## test_ood-00096（test_ood / dag / S22）— ref_arg, dependency

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
{"action":"plan","steps":[{"id":"s1","tool":"get_office_action","args":{"oa_id":"OA-2026-1884"},"depends_on":[]},{"id":"s2","tool":"amend_claims","args":{"case_id":"TW-2026-1347","claim_no":14,"instruction":"加入散熱鰭片的結構限定"},"depends_on":["s1"]},{"id":"s3","tool":"draft_response","args":{"oa_id":"OA-2026-1884","arguments":"針對核駁理由提出答辯，基於修正後的請求項內容","amendments":"$s2.amended_claim"},"depends_on":["s2"]}]}}
```

觀察：

## test_ood-00050（test_ood / chain / S17）— distractor

- 可用工具：compare_claims, search_prior_art, get_case, translate_text, get_patent, notify_client
- 需求：請將案號 I751246 的摘要翻譯成英文，發送給客戶 TW-2026-6952。

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "get_patent",
   "args": {
    "patent_no": "I751246"
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
    "case_id": "TW-2026-6952",
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
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"TW-2026-6952"},"depends_on":[]},{"id":"s2","tool":"get_patent","args":{"patent_no":"I751246"},"depends_on":[]},{"id":"s3","tool":"translate_text","args":{"text":"$s2.abstract","target_lang":"en"},"depends_on":["s2"]},{"id":"s4","tool":"notify_client","args":{"case_id":"TW-2026-6952","message":"$s3.translated"},"depends_on":["s3"]}]}
```

觀察：

## test_ood-00015（test_ood / parallel / S10）— distractor, missing_step, literal_arg

- 可用工具：get_office_action, get_case, search_prior_art, get_patent, calc_deadline
- 需求：兩件事：查 I737324；算從 2026-02-13 起的答辯期限

gold：
```json
{
 "action": "plan",
 "steps": [
  {
   "id": "s1",
   "tool": "calc_deadline",
   "args": {
    "issue_date": "2026-02-13"
   },
   "depends_on": []
  },
  {
   "id": "s2",
   "tool": "get_patent",
   "args": {
    "patent_no": "I737324"
   },
   "depends_on": []
  }
 ]
}
```
預測：
```
{"action":"plan","steps":[{"id":"s1","tool":"get_case","args":{"case_id":"I737324"},"depends_on":[]},{"id":"s2","tool":"calc_deadline","args":{"issue_date":"2026-02-13"},"depends_on":[]}]}
```

觀察：
