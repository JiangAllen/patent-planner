# 改寫抽查表

每筆標記 ✅（語意一致）或 ❌（語意偏移，寫明原因）。

## single

| id | 原句 | 改寫 | gold | 標記 |
|---|---|---|---|---|
| train-01080 | 發文日 2026-01-16，最晚什麼時候要回覆？ | 發文日期為 2026-01-16，最晚什麼時候回覆？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "calc_deadline", "args": {"issue_date": "2026-01-16"}, "depends_on": []}]}` |  |
| train-01195 | TW-2025-6810 的案件資料幫我調出來 | 請把TW-2025-6810案的資料調出來。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2025-6810"}, "depends_on": []}]}` |  |
| train-00081 | 搜尋跟晶圓級封裝有關的先前技術 | 搜尋與晶圓級封裝相關的先前技術 | `{"action": "plan", "steps": [{"id": "s1", "tool": "search_prior_art", "args": {"query": "晶圓級封裝"}, "depends_on": []}]}` |  |
| train-00771 | 有沒有關於散熱鰭片的既有專利？ | 是否有關於散熱鰭片的既有專利？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "search_prior_art", "args": {"query": "散熱鰭片"}, "depends_on": []}]}` |  |
| train-01443 | TW-2026-5656 的案件資料幫我調出來 | 請把TW-2026-5656案的資料調出來。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-5656"}, "depends_on": []}]}` |  |
| train-01358 | 發文日 2026-12-07，最晚什麼時候要回覆？ | 發文日 2026-12-07，最晚什麼時候回覆？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "calc_deadline", "args": {"issue_date": "2026-12-07"}, "depends_on": []}]}` |  |
| train-01145 | TW-2026-6390 的案件資料幫我調出來 | 請把TW-2026-6390案的資料調出來。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-6390"}, "depends_on": []}]}` |  |
| train-00864 | I758407 這件專利在講什麼？ | I758407 這件專利是關於什麼的？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I758407"}, "depends_on": []}]}` |  |
| train-01344 | 幫我讀一下 OA-2026-9703 的內容 | 請幫我查看一下 OA-2026-9703 的內容。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-9703"}, "depends_on": []}]}` |  |
| train-01016 | 找一些散熱鰭片的前案 | 找一些散熱鰭片的先前案情。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "search_prior_art", "args": {"query": "散熱鰭片"}, "depends_on": []}]}` |  |
| train-01598 | 幫我讀一下 OA-2026-0879 的內容 | 請幫我看一下 OA-2026-0879 的內容。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0879"}, "depends_on": []}]}` |  |
| train-00607 | 查一下 TW-2025-1194 這件目前的狀態 | 查一下 TW-2025-1194 目前的狀態。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2025-1194"}, "depends_on": []}]}` |  |
| train-01416 | I742233 這件專利在講什麼？ | I742233這件專利是關於什麼的？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I742233"}, "depends_on": []}]}` |  |
| train-00379 | 把 OA-2025-7601 這份審查意見通知書打開 | 請打開 OA-2025-7601 這份審查意見通知書。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2025-7601"}, "depends_on": []}]}` |  |
| train-00827 | 幫我讀一下 OA-2025-7158 的內容 | 請幫我看一下 OA-2025-7158 的內容。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2025-7158"}, "depends_on": []}]}` |  |

## parallel

| id | 原句 | 改寫 | gold | 標記 |
|---|---|---|---|---|
| train-00484 | 搜尋封裝基板相關前案，順便調出 I724837 | 搜尋封裝基板相關前案，順便調出I724837。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "search_prior_art", "args": {"query": "封裝基板"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "I724837"}, "depends_on": []}]}` |  |
| train-00276 | TW-2026-4963 請求項 2 要「刪除重複的附屬項敘述」；另外跟客戶說「審查意見通知書已收到」 | TW-2026-4963 請求項 2 要刪除重複的附屬項敘述；另外告知客戶審查意見通知書已收到。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "amend_claims", "args": {"case_id": "TW-2026-4963", "claim_no": 2, "instruction": "刪除重複的附屬項敘述"}, "depends_on": []}, {"id": "s2", "tool": "notify_client", "args": {"case_id": "TW-2026-4963", "message": "審查意見通知書已收到"}, "depends_on": []}]}` |  |
| train-01969 | 把 I781762 和 I773156 兩件專利都調出來 | 把I781762和I773156這兩件專利都調出來。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I781762"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "I773156"}, "depends_on": []}]}` |  |
| train-00790 | 搜尋散熱鰭片相關前案，順便調出 I715105 | 搜尋散熱鰭片相關前案，順便調出I715105。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "search_prior_art", "args": {"query": "散熱鰭片"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "I715105"}, "depends_on": []}]}` |  |
| train-01782 | 幫我找封裝基板的先前技術，另外把 I757034 的全文給我 | 請幫我查找封裝基板的先前技術，另外提供I757034的全文。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "search_prior_art", "args": {"query": "封裝基板"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "I757034"}, "depends_on": []}]}` |  |
| train-01949 | TW-2026-1817 的狀態和 OA-2026-9549 的內容都給我看 | TW-2026-1817的狀態和OA-2026-9549的內容都給我看看。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-1817"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2026-9549"}, "depends_on": []}]}` |  |
| train-00494 | 同時查案件 TW-2026-3468 跟通知書 OA-2026-9556 | 同時查案件 TW-2026-3468 和通知書 OA-2026-9556 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-3468"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2026-9556"}, "depends_on": []}]}` |  |
| train-00985 | 我需要 I783313 跟 I711395 這兩篇的全文 | 我需要 I783313 和 I711395這兩篇的全文。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I783313"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "I711395"}, "depends_on": []}]}` |  |
| train-00300 | 同時查 I709835、I734567 的內容 | 同時查閱 I709835、I734567 的內容 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I709835"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "I734567"}, "depends_on": []}]}` |  |
| train-00246 | 同時查 I751989、I764045 的內容 | 請同時查閱I751989、I764045的內容。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I751989"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "I764045"}, "depends_on": []}]}` |  |
| train-01085 | 把 I705123 和 I783835 兩件專利都調出來 | 請把編號I705123和I783835兩件專利都調出來。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I705123"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "I783835"}, "depends_on": []}]}` |  |
| train-01594 | TW-2026-1759 的狀態和 OA-2026-7602 的內容都給我看 | TW-2026-1759 的狀態和 OA-2026-7602 的內容都請 Fireplace 查閱。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-1759"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2026-7602"}, "depends_on": []}]}` |  |
| train-01853 | 通知 TW-2025-6919 的客戶「答辯期限即將到期」，也順便把請求項 18「刪除重複的附屬項敘述」 | 通知 TW-2025-6919 的客戶「答辯期限即將到期」，也順便把請求項 18「刪除重複的附屬項敘述」。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "amend_claims", "args": {"case_id": "TW-2025-6919", "claim_no": 18, "instruction": "刪除重複的附屬項敘述"}, "depends_on": []}, {"id": "s2", "tool": "notify_client", "args": {"case_id": "TW-2025-6919", "message": "答辯期限即將到期"}, "depends_on": []}]}` |  |
| train-00306 | 幫我找散熱鰭片的先前技術，另外把 I726748 的全文給我 | 請幫我查找散熱鰭片的先前技術，另外提供I726748的全文。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "search_prior_art", "args": {"query": "散熱鰭片"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "I726748"}, "depends_on": []}]}` |  |
| train-01150 | 把 TW-2025-2009 的請求項 14 修正為「刪除重複的附屬項敘述」，同時通知客戶「審查意見通知書已收到」 | 請將 TW-2025-2009 請求項 14 修正為「刪除重複的附屬項敘述」，並通知客戶「審查意見通知書已收到」。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "amend_claims", "args": {"case_id": "TW-2025-2009", "claim_no": 14, "instruction": "刪除重複的附屬項敘述"}, "depends_on": []}, {"id": "s2", "tool": "notify_client", "args": {"case_id": "TW-2025-2009", "message": "審查意見通知書已收到"}, "depends_on": []}]}` |  |

## chain

| id | 原句 | 改寫 | gold | 標記 |
|---|---|---|---|---|
| train-01075 | 打開 OA-2026-2680 第一件引證的全文 | 打開 OA-2026-2680 第一件引證的全文觀看 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-2680"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.cited_refs[0]"}, "depends_on": ["s1"]}]}` |  |
| train-00757 | OA-2026-5445 最晚什麼時候要回？ | OA-2026-5445 最晚什麼時候回覆？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-5445"}, "depends_on": []}, {"id": "s2", "tool": "calc_deadline", "args": {"issue_date": "$s1.issue_date"}, "depends_on": ["s1"]}]}` |  |
| train-01447 | 打開 OA-2025-7503 第一件引證的全文 | 打開 OA-2025-7503 第一件引證的全文觀看 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2025-7503"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.cited_refs[0]"}, "depends_on": ["s1"]}]}` |  |
| train-01554 | 幫我算 OA-2026-5616 的答辯期限 | 請幫我計算OA-2026-5616的答辨期限。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-5616"}, "depends_on": []}, {"id": "s2", "tool": "calc_deadline", "args": {"issue_date": "$s1.issue_date"}, "depends_on": ["s1"]}]}` |  |
| train-00498 | 把 I709881 的摘要翻成英文 | 請將I709881的摘要翻譯成英文。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I709881"}, "depends_on": []}, {"id": "s2", "tool": "translate_text", "args": {"text": "$s1.abstract", "target_lang": "en"}, "depends_on": ["s1"]}]}` |  |
| train-01326 | 打開 OA-2025-4950 第一件引證的全文 | 打開 OA-2025-4950 第一件引證的全文觀看 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2025-4950"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.cited_refs[0]"}, "depends_on": ["s1"]}]}` |  |
| train-01164 | 搜尋電磁屏蔽層的前案，把最相關那篇的全文給我 | 搜尋電磁屏蔽層的前案，將最相關的那份全文提供給我。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "search_prior_art", "args": {"query": "電磁屏蔽層"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.results[0].patent_no"}, "depends_on": ["s1"]}]}` |  |
| train-01095 | 讀 OA-2025-4645，然後算出答辯期限 | 請閱OA-2025-4645，然後計算答辯期限。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2025-4645"}, "depends_on": []}, {"id": "s2", "tool": "calc_deadline", "args": {"issue_date": "$s1.issue_date"}, "depends_on": ["s1"]}]}` |  |
| train-01267 | I769924 的摘要給我日文版本 | 請提供I769924的摘要的日文版本。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I769924"}, "depends_on": []}, {"id": "s2", "tool": "translate_text", "args": {"text": "$s1.abstract", "target_lang": "ja"}, "depends_on": ["s1"]}]}` |  |
| train-00644 | 把 I715874 的摘要翻成英文 | 把I715874的摘要翻譯成英文 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I715874"}, "depends_on": []}, {"id": "s2", "tool": "translate_text", "args": {"text": "$s1.abstract", "target_lang": "en"}, "depends_on": ["s1"]}]}` |  |
| train-00150 | 調出 I753154，摘要翻譯成德文 | 調出案號 I753154，請將摘要翻譯成德文。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I753154"}, "depends_on": []}, {"id": "s2", "tool": "translate_text", "args": {"text": "$s1.abstract", "target_lang": "de"}, "depends_on": ["s1"]}]}` |  |
| train-01959 | 把 I762712 的摘要翻成日文 | 將I762712的摘要翻譯成日文 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I762712"}, "depends_on": []}, {"id": "s2", "tool": "translate_text", "args": {"text": "$s1.abstract", "target_lang": "ja"}, "depends_on": ["s1"]}]}` |  |
| train-01324 | OA-2026-8309 裡第一個引證專利是什麼內容？ | OA-2026-8309 中第一個引證專利的內容是什麼？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-8309"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.cited_refs[0]"}, "depends_on": ["s1"]}]}` |  |
| train-00047 | 找電磁屏蔽層相關專利，打開排第一的那篇 | 請查找與電磁屏蔽層相關的專利，開啟搜尋結果排第一的那篇。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "search_prior_art", "args": {"query": "電磁屏蔽層"}, "depends_on": []}, {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.results[0].patent_no"}, "depends_on": ["s1"]}]}` |  |
| train-00231 | 讀 OA-2026-9519，然後算出答辯期限 | 請閱讀OA-2026-9519，然後計算出答辯期限。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-9519"}, "depends_on": []}, {"id": "s2", "tool": "calc_deadline", "args": {"issue_date": "$s1.issue_date"}, "depends_on": ["s1"]}]}` |  |

## dag

| id | 原句 | 改寫 | gold | 標記 |
|---|---|---|---|---|
| train-01203 | 搜尋覆晶接合前案，取第一名跟 I773283 的第一項請求項比較 | 搜尋覆晶接合前案，比較第一名與I773283的第一項請求項。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I773283"}, "depends_on": []}, {"id": "s2", "tool": "search_prior_art", "args": {"query": "覆晶接合"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-01908 | OA-2025-2613 引用的第一篇前案，和 TW-2025-7931 請求項 1 差在哪？ | OA-2025-2613 引用的第一篇前案和 TW-2025-7931 請求項 1 有何不同？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2025-7931"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2025-2613"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-00030 | OA-2026-1710 引用的第一篇前案，和 TW-2026-7963 請求項 1 差在哪？ | OA-2026-1710 引用的第一篇前案和 TW-2026-7963 請求項 1 有何不同？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-7963"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2026-1710"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-01842 | 搜尋電磁屏蔽層的前案，拿最相關那篇跟 TW-2025-9897 的請求項 1 比對 | 搜尋電磁屏蔽層的前案，取最相關的那篇與 TW-2025-9897 的請求項 1 進行比對。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2025-9897"}, "depends_on": []}, {"id": "s2", "tool": "search_prior_art", "args": {"query": "電磁屏蔽層"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-01472 | 把專利 I788833 的請求項 1 和電磁屏蔽層最相關的前案比對 | 將專利 I788833 的請求項 1 與電磁屏蔽層最相關的前案進行比對 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I788833"}, "depends_on": []}, {"id": "s2", "tool": "search_prior_art", "args": {"query": "電磁屏蔽層"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-00973 | 搜尋扇出型封裝前案，取第一名跟 I745451 的第一項請求項比較 | 搜尋扇出型封裝的前案，比較第一名和申請編號I745451的第1項請求項。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I745451"}, "depends_on": []}, {"id": "s2", "tool": "search_prior_art", "args": {"query": "扇出型封裝"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-00691 | 比對 TW-2025-9368 請求項 1 和 OA-2025-9594 的第一件引證，再根據差異擬答辯書 | 請比對 TW-2025-9368 請求項 1 和 OA-2025-9594 的第一件引證，再據此擬擬答辯書。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2025-9368"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2025-9594"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}, "depends_on": ["s1", "s2"]}, {"id": "s4", "tool": "draft_response", "args": {"oa_id": "OA-2025-9594", "arguments": "$s3.distinguishing_features"}, "depends_on": ["s3"]}]}` |  |
| train-00944 | 把專利 I799434 的請求項 1 和覆晶接合最相關的前案比對 | 將專利 I799434 的請求項 1 與覆晶接合最相關的前案進行比對 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I799434"}, "depends_on": []}, {"id": "s2", "tool": "search_prior_art", "args": {"query": "覆晶接合"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-00175 | OA-2026-3873 引用的第一篇前案，和 TW-2026-7741 請求項 1 差在哪？ | OA-2026-3873 引用的第一篇前案和 TW-2026-7741 請求項 1 有何不同？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-7741"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2026-3873"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-00524 | OA-2025-4482 要答辯：拿 TW-2025-2425 的請求項 1 跟第一件引證比，用找到的差異寫草稿 | OA-2025-4482 要答辯：拿 TW-2025-2425 的請求項 1 跟第一件引證比較，用找到的差異寫草稿 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2025-2425"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2025-4482"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}, "depends_on": ["s1", "s2"]}, {"id": "s4", "tool": "draft_response", "args": {"oa_id": "OA-2025-4482", "arguments": "$s3.distinguishing_features"}, "depends_on": ["s3"]}]}` |  |
| train-01734 | I742130 請求項 1 與電磁屏蔽層領域排名第一的前案差在哪？ | 請問I742130請求項1與電磁屏蔽層領域排名第一的前案有什麼不同？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_patent", "args": {"patent_no": "I742130"}, "depends_on": []}, {"id": "s2", "tool": "search_prior_art", "args": {"query": "電磁屏蔽層"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-00624 | OA-2025-7643 引用的第一篇前案，和 TW-2025-2157 請求項 1 差在哪？ | OA-2025-7643 引用的第一篇前案和 TW-2025-2157 請求項 1 有何不同？ | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2025-2157"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2025-7643"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-00678 | 找封裝基板的先前技術，用第一名跟 TW-2026-5407 第一項請求項做比對 | 找封裝基板的先前技術，用第一namescore和TW-2026-5407第一項請求項做比對。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-5407"}, "depends_on": []}, {"id": "s2", "tool": "search_prior_art", "args": {"query": "封裝基板"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"}, "depends_on": ["s1", "s2"]}]}` |  |
| train-00374 | 比對 TW-2025-8973 請求項 1 和 OA-2025-4130 的第一件引證，再根據差異擬答辯書 | 比對 TW-2025-8973 請求項 1 和 OA-2025-4130 的第一件引證，再根據差異擬答辯書。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2025-8973"}, "depends_on": []}, {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2025-4130"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}, "depends_on": ["s1", "s2"]}, {"id": "s4", "tool": "draft_response", "args": {"oa_id": "OA-2025-4130", "arguments": "$s3.distinguishing_features"}, "depends_on": ["s3"]}]}` |  |
| train-01622 | 找散熱鰭片的先前技術，用第一名跟 TW-2026-2627 第一項請求項做比對 | 查找散熱鰭片的先前技術，用第一名和 TW-2026-2627 第一項請求項進行比對。 | `{"action": "plan", "steps": [{"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-2627"}, "depends_on": []}, {"id": "s2", "tool": "search_prior_art", "args": {"query": "散熱鰭片"}, "depends_on": []}, {"id": "s3", "tool": "compare_claims", "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"}, "depends_on": ["s1", "s2"]}]}` |  |

## clarify

| id | 原句 | 改寫 | gold | 標記 |
|---|---|---|---|---|
| train-01038 | 幫我發訊息給客戶：「答辯書草稿已完成，請確認」 | 請將訊息發給客戶：「答辯書草稿已完成，請確認」。 | `{"action": "clarify", "missing": ["case_id"]}` |  |
| train-00263 | 通知客戶「答辯期限即將到期」 | 通知客戶「答辯期限即將到期」 | `{"action": "clarify", "missing": ["case_id"]}` |  |
| train-00241 | 把那件專利的摘要給我 | 請把那件專利的摘要提供給我。 | `{"action": "clarify", "missing": ["patent_no"]}` |  |
| train-00740 | 幫我發訊息給客戶：「答辯期限即將到期」 | 請幫我發訊息給客戶：「答辯期限即將到期」 | `{"action": "clarify", "missing": ["case_id"]}` |  |
| train-01171 | 幫我調出那篇引證專利的全文 | 請幫我調出那篇引證專利的全文。 | `{"action": "clarify", "missing": ["patent_no"]}` |  |
| train-01132 | 這份通知書的答辯期限幫我算一下 | 請幫我計算這份通知書的答辯期限。 | `{"action": "clarify", "missing": ["oa_id"]}` |  |
| train-00302 | 通知書最晚什麼時候要回覆？ | 通知書最晚什麼時候需要回覆？ | `{"action": "clarify", "missing": ["oa_id"]}` |  |
| train-00693 | 通知書最晚什麼時候要回覆？ | 通知書最晚什麼時候需要回覆？ | `{"action": "clarify", "missing": ["oa_id"]}` |  |
| train-01273 | 這份通知書的答辯期限幫我算一下 | 請幫我計算這份通知書的答辯期限。 | `{"action": "clarify", "missing": ["oa_id"]}` |  |
| train-00688 | 跟客戶說一聲「答辯書草稿已完成，請確認」 | 告知客戶：答辯書草稿已完成，請確認。 | `{"action": "clarify", "missing": ["case_id"]}` |  |
| train-01668 | 跟客戶說一聲「答辯期限即將到期」 | 告訴客戶「答辯期限即將到期」 | `{"action": "clarify", "missing": ["case_id"]}` |  |
| train-00356 | 把那件專利的摘要給我 | 請將那件專利的摘要提供給我。 | `{"action": "clarify", "missing": ["patent_no"]}` |  |
| train-01272 | 通知書最晚什麼時候要回覆？ | 通知書最晚什麼時候需要回覆？ | `{"action": "clarify", "missing": ["oa_id"]}` |  |
| train-00769 | 幫我算審查意見通知書的答辯期限 | 請幫我計算審查意見通知書的答辯期限。 | `{"action": "clarify", "missing": ["oa_id"]}` |  |
| train-01910 | 通知書最晚什麼時候要回覆？ | 通知書最遲什麼時候需要回覆？ | `{"action": "clarify", "missing": ["oa_id"]}` |  |

## refuse

| id | 原句 | 改寫 | gold | 標記 |
|---|---|---|---|---|
| train-01874 | 調出 I742620，摘要翻譯成德文 | 調出案號I742620，請將摘要翻譯成德文。 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-01190 | 把 TW-2026-0869 的專利證書寄到客戶公司 | 請將 TW-2026-0869 的專利證書寄往客戶公司。 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-00459 | 幫 TW-2026-8490 辦理年費減免 | 請處理 TW-2026-8490 的年費減免事宜 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-01972 | 幫我跟審查委員約面詢時間 | 請幫我與審查委員安排面詢時間。 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-01650 | 幫我跟審查委員約面詢時間 | 請幫我與審查委員安排面詢時間。 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-01336 | 幫 TW-2025-6566 辦理年費減免 | 請處理 TW-2025-6566 的年費減免事宜 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-01214 | TW-2026-4621 的年費幫我繳掉 | TW-2026-4621的年費幫我繳了。 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-01308 | TW-2025-8404 的年費幫我繳掉 | 請幫我繳納TW-2025-8404的年費。 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-00705 | OA-2026-9672 直接幫我提行政訴訟 | OA-2026-9672 請直接幫我提起行政訴訟。 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-01004 | 查一下 I796318 的專利權人電話 | 查一下專利號碼I796318的專利權人電話。 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-00219 | 幫 TW-2025-5734 辦理年費減免 | 請為 TW-2025-5734 件辦理年費減免事宜 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-01316 | 幫 TW-2026-1856 辦理年費減免 | 請辦理 TW-2026-1856 的年費減免事宜 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-00906 | 幫 TW-2025-2611 辦理年費減免 | 請為 TW-2025-2611 辦理年費減免事宜 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-00742 | 查一下 I763438 的專利權人電話 | 查一下專利號碼I763438的專利權人電話。 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
| train-01285 | OA-2025-9940 直接幫我提行政訴訟 | OA-2025-9940 請直接為我提出行政訴訟 | `{"action": "refuse", "reason": "no_capable_tool"}` |  |
