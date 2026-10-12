# 端到端 Demo（qlora-r16-v2 + mock Executor）

注意：三句 demo 請求接近訓練模板（S18、S23、S27），只用來展示端到端流程，不作為泛化能力的證據；泛化看 `reports/error_analysis.md` 的 OOD 分析。

產生方式：`train/demo.py`（WSL，RTX 4070 SUPER，4-bit，greedy）。工具全是 mock，回傳固定假資料（`planner/executor.py`）。

## 1. 多步驟 DAG：比對請求項與引證

> 把 TW-2026-0412 的請求項 1 跟 OA-2026-0331 的第一件引證比對

Planner（8.3 秒，含首次 CUDA 暖機）：s1 `get_case` 與 s2 `get_office_action` 並行，s3 `compare_claims` 等兩者完成。

```
▶ s1 get_case(case_id='TW-2026-0412')
  → {'application_no': '112100001', 'claims': ['一種半導體封裝結構，包含基板與散熱鰭片…'], 'oa_ids': ['OA-2026-0331'], 'status': '審查中'}
▶ s2 get_office_action(oa_id='OA-2026-0331')
  → {'cited_refs': ['I701234', 'I705678'], 'rejected_claims': [...], 'grounds': '請求項 1 不具進步性', 'issue_date': '2026-09-15'}
▶ s3 compare_claims(claim_text='一種半導體封裝結構，包含基板與散熱鰭片…', reference_patent_no='I701234')
  → {'overlap': 0.62, 'distinguishing_features': '散熱鰭片的排列結構'}
[完成] 共 3 步
```

`$s1.claims[0]`、`$s2.cited_refs[0]` 在執行時被代入上一步的實際結果。

## 2. 缺資訊：追問

> 幫我算答辯期限

```json
{"action": "clarify", "missing": ["oa_id"]}
```

`calc_deadline` 需要發文日；模型沒有編造日期，而是追問 OA 編號（可再由 `get_office_action` 取得 `issue_date`）。

## 3. 超出能力：拒絕

> 幫我繳年費

```json
{"action": "refuse", "reason": "no_capable_tool"}
```

## 可執行率 vs 正確率

`uv run python -m evaluation.executability --runs zeroshot fewshot qlora-r16 qlora-r16-v2`：把每份預測計畫丟進 Executor，只看能不能跑完。

| run | split | plan 數 | 可執行 | 執行失敗 |
|---|---|---|---|---|
| zeroshot | test_id | 96 | 95 | 1 |
| zeroshot | test_ood | 102 | 101 | 1 |
| fewshot | test_id | 93 | 92 | 1 |
| fewshot | test_ood | 130 | 125 | 5 |
| qlora-r16 | test_id | 100 | 100 | 0 |
| qlora-r16 | test_ood | 106 | 103 | 3 |
| qlora-r16-v2 | test_id | 100 | 100 | 0 |
| qlora-r16-v2 | test_ood | 103 | 100 | 3 |

同一個分母比較：zero-shot 在 test_id 有 95 份計畫跑得完，其中只有 35 份 exact（37%）；test_ood 是 101 份中 11 份。**跑得完不代表做對**——錯接欄位、漏步驟、多做步驟都不會讓執行失敗。所以評估不能只看「有沒有報錯」，要對照 gold 計畫。執行失敗的少數案例是引用了不存在的欄位或索引。所有 gold 計畫皆可執行（mock 涵蓋完整）。
