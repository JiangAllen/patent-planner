# 第二輪：針對性補資料（qlora-r16-v2）

## 目標

驗證 error analysis 提出的假設：**OOD 失敗是因為訓練資料缺少某些元件，而不是模型能力不足。** 只補元件、不補 holdout 結構本身，看 S22 與 S26 能否從 0 分回升。

## 要補的缺口（全部來自 v1 train 的統計）

| 缺口 | v1 train 筆數 | 影響的 OOD 結構 |
|---|---|---|
| `draft_response` 帶 `amendments` 參數 | 0 / 2039 | S22 |
| 引用 `get_office_action` 的 `.grounds` 欄位 | 0 / 2039 | S22 |
| clarify 的缺漏清單有 2 項 | 0 / 237 | S26 |
| clarify 需要兩跳推理（缺的欄位要由另一個工具取得） | 只有 S23 一個方向（73 筆：`calc_deadline` → 追問 `oa_id`） | S26 |

## 新增 5 個模板（S31–S35，不設 holdout）

| id | 類型 | 結構 | 補的缺口 | 與 holdout 的差別 |
|---|---|---|---|---|
| S31 | chain | `get_office_action` → `draft_response(arguments=$s1.grounds)` | `.grounds` | 沒有修正步驟，不是 S22 |
| S32 | dag | `get_case` + `get_office_action` → `compare_claims` → `amend_claims` → `draft_response(arguments=$s3.distinguishing_features, amendments=$s4.amended_claim)` | `amendments`、匯合 | 論點來自比對結果，不是 `.grounds` |
| S33 | dag | `get_case` → `compare_claims(reference_patent_no={PAT})` + `amend_claims` → `draft_response(…, amendments=…)` | `amendments`、匯合 | 同上 |
| S34 | clarify | 需要 `get_patent`、`translate_text`；缺 `[patent_no, target_lang]` | 缺 2 項 | 不同工具 |
| S35 | clarify | 需要 `get_office_action`、`calc_deadline`、`notify_client`；缺 `[oa_id, case_id]` | 缺 2 項 + 兩跳（同 S23 方向） | 與 S26 的工具與兩跳方向都不同（初版設計太像 S26，實作時已改） |

**注意（簡報要誠實說明）**：補完之後，S22 從「需要沒見過的元件」變成「沒見過的元件組合」。所以 v2 驗證的是「補元件能否讓模型學會組合」，S22 與 S26 的 OOD 性質會變弱，這點要寫進報告。

## 不變的部分（確保 v1 與 v2 可以比較）

- val、test_id、test_ood **完全不動**，沿用 v1 的檔案。
- 超參數、底座模型、prompt、評分器都不變。只換 train 檔案。
- v1 的 adapter 與預測結果全部保留，作為對照組。

## 步驟與時間

| # | 步驟 | 誰 | 時間 |
|---|---|---|---|
| 1 | 新增 S31–S35 模板，並加測試：不得與 holdout 結構相同、gold 必須通過 `validate` | Claude | 30 分 |
| 2 | 新增 `datagen/augment.py`：只對新模板產生資料（每個模板 100 筆，共 500 筆），用既有的 `paraphrase()` 改寫，剔除與 val/test 重複的句子，寫出 `data/train_v2.jsonl`（v1 train + 新資料） | Claude | 20 分 |
| 3 | 執行 Ollama 改寫 500 筆（背景） | 機器 | 約 25 分 |
| 4 | `train_qlora.py` 加上 `--train-file` 參數（預設仍是 `train`），執行 smoke 20 步 | Claude + 機器 | 10 分 |
| 5 | 完整訓練 `qlora-r16-v2`（約 2540 筆，3 epoch，背景） | 機器 | 約 40 分 |
| 6 | 推論 val、test_id、test_ood（背景） | 機器 | 約 45 分 |
| 7 | 四組比較分析，更新 `error_analysis.md`，新增「第二輪」一節，然後 commit 並 push | Claude | 30 分 |

**總計約 3 小時 20 分鐘**，其中約 2 小時是機器在背景跑。你需要參與的只有：
- 現在：確認這份計畫。
- 步驟 1 完成後（選擇性）：看一眼新模板的句子，約 5 分鐘。

## 成功與失敗都有結論

- **S22 或 S26 明顯回升**（CI 與 v1 不重疊）：支持「缺的是資料元件」，下一步是系統性地依工具簽名產生資料。
- **沒有回升**：代表 4B 模型加 LoRA 無法從元件推出組合，這同樣是有價值的負面結果。
- **test_id 下降**：代表新資料干擾了原本學會的結構，要回報這個取捨。

## 風險

- 背景任務可能再次因為記憶體不足被系統停掉。跑之前請先關掉不需要的程式。
- 補資料後，「答辯書」類的請求比例變高，模型可能在 S16 這類需求上更傾向多做 `draft_response`。這要在四組比較時特別檢查。
