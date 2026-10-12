# 鴻海二面：專利答辯 Agent Planner 微調 — 設計 spec

- 日期：2026-10-09；二面：**2026-10-16（五）**
- 實作位置：新 repo `JiangAllen/patent-planner`（本機 `C:\Users\USER\Desktop\patent-planner`），**先 private，面試前轉 public**；本 spec 核准後複製一份過去
- 評分重點（題目）：Planner Model Fine-tuning、Dataset / Experiment Design、Model Evaluation / Error Analysis

## 1. 目標與成功標準

- 交付：source code、訓練與評估結果、20 分鐘技術簡報。
- 成功標準：
  1. 微調模型在**沒看過的任務組合（test_ood）**上，plan exact match 明顯優於 zero-shot 與 few-shot baseline（95% bootstrap CI 不重疊才宣稱改善）。
  2. 能依任務類型說明哪裡進步、哪裡仍錯，並以 test_id 與 test_ood 的差距說明泛化程度。
- 限制：
  - 資料全部合成，**不碰任何前公司客戶案件內容**；也不沿用 `patent-oa-qlora` adapter（任務不同、7B 不符題目規格）。
  - 全程本地：本機 4070 SUPER 12GB 訓練，資料改寫用本地 Ollama，零 API 成本。設定需能在 Colab T4 16GB 重現。

## 2. Agent 定義

### 2.1 架構：Plan-and-Execute

Planner（被微調的 LLM）一次產出整張工具呼叫 DAG，Executor（一般程式）依相依關係執行、解析引用。相對於 ReAct（每步呼叫一次 LLM），優點是 LLM 呼叫次數少、可平行、小模型可行（TinyAgent / LLMCompiler 的論點）；缺點是規劃時看不到中間結果，改善方向為執行失敗時 replan。

### 2.2 工具庫（10 個 mock tool）

| Tool | 參數 | 回傳（可被 `$sN.` 引用） |
|---|---|---|
| `get_case` | `case_id` | `application_no`, `claims`, `oa_ids`, `status` |
| `get_office_action` | `oa_id` | `cited_refs`, `rejected_claims`, `grounds`, `issue_date` |
| `get_patent` | `patent_no` | `patent_no`, `title`, `abstract`, `claims` |
| `search_prior_art` | `query`, `date_before?`, `top_k?` | `results[].patent_no` |
| `compare_claims` | `claim_text`, `reference_patent_no` | `overlap`, `distinguishing_features` |
| `calc_deadline` | `issue_date`, `extension_months?` | `deadline` |
| `amend_claims` | `case_id`, `claim_no`, `instruction` | `amended_claim` |
| `draft_response` | `oa_id`, `arguments`, `amendments?` | `draft_id` |
| `translate_text` | `text`, `target_lang` | `translated` |
| `notify_client` | `case_id`, `message` | `sent` |

### 2.3 輸出格式（JSON，三種 action）

```json
{"action": "plan", "steps": [
  {"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0331"}, "depends_on": []},
  {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.cited_refs[0]"}, "depends_on": ["s1"]}
]}
{"action": "clarify", "missing": ["oa_id"]}
{"action": "refuse", "reason": "no_capable_tool"}
```

- `args` 的值可為字面值，或 `$<step_id>.<path>` 引用前一步回傳。
- `depends_on` 為空代表可立即執行；彼此無相依的 step 可平行。
- `clarify` 只輸出缺少的參數名稱（可程式化評分），反問語句由 Agent 其他層產生。
- 引用必須與 `depends_on` 一致（引用到的 step 必須列在 `depends_on`）。

### 2.4 任務類型（6 類，約平均分配）

| 類型 | 說明 |
|---|---|
| `single` | 1 個 tool |
| `parallel` | 多個 tool，彼此無相依 |
| `chain` | 2–4 步串接 |
| `dag` | 多來源匯合（fan-in） |
| `clarify` | 缺少必要參數 |
| `refuse` | 必要 tool 不在 `available_tools`，或需求超出工具能力 |

## 3. 資料集

### 3.1 產生方式：反向生成（先有答案，再產生題目）

1. **結構模板**（人工，約 30 個）：每個模板定義一張 tool DAG 形狀、所屬類型，以及 3–5 個中文句型（`request_templates`，含 `{OA_ID}` 等空格）。由 Claude 擬初稿、Allen 依實務經驗審稿。
2. **填值**（程式）：每個模板跑 N 次迴圈（約 80 次），每次隨機抽參數值（案號 `TW-2026-xxxx`、專利號 `I7xxxxx`、日期、請求項編號）與句型，同時填入句型與 steps，得到 `request` 與 `gold`。
3. **干擾項**（程式）：從其餘 tool 隨機抽 2–4 個加入並打亂順序，得到 `available_tools`；`refuse` 類刻意移除一個必要 tool。
4. **改寫**（本地 Ollama `qwen2.5:7b-instruct`）：把填好值的句子改寫成更自然的說法；與訓練底座為不同模型家族。
5. **品質檢查**（程式，不合格則退回模板原句）：
   - 所有參數值必須原樣保留；
   - 不得出現原句沒有的案號 / 專利號（防止 `clarify` 題被捏造參數而失效）；
   - 去重、剔除長度異常。
6. **人工抽查**：每類抽 10–20 筆，記錄改寫後語意偏移率，寫入報告。

標註正確性由建構保證；唯一的錯誤來源是改寫，由第 5、6 步控制。

### 3.2 JSONL 欄位

```json
{"id": "train-00042", "category": "dag", "structure_id": "S17", "split": "train",
 "available_tools": ["get_office_action", "notify_client", "get_patent", "calc_deadline", "compare_claims"],
 "request": "OA-2026-0331 這份通知書裡第一篇引證，幫我拿來跟被駁回的第一項請求項比一下",
 "gold": {"action": "plan", "steps": ["..."]}}
```

模型只看得到 `available_tools`（轉成 system prompt 中的 tool schema）與 `request`；其餘欄位供切分與分析使用。訓練時轉為 chat 格式（system / user / assistant=gold JSON）。

### 3.3 切分

| Split | 來源 | 約筆數 | 用途 |
|---|---|---|---|
| train | 24 個已見結構 | 2000 | 訓練 |
| val | 已見結構，與 train 隨機切開 | 200 | loss 監控、挑 checkpoint |
| test_id | 已見結構，新值與新句子 | 150 | 分布內能力 |
| test_ood | 6 個保留結構（`chain` 2 個；`parallel` / `dag` / `clarify` / `refuse` 各 1 個；`single` 無組合可保留） | 150 | 沒看過的組合 |

`test_id` 與 `test_ood` 的差距是簡報主軸：差距小代表學到規劃能力，差距大代表在背模板。

## 4. Baseline 與微調

- Base model：`unsloth/Qwen3-4B-Instruct-2507`（非 thinking 版；三個建議模型中中文與 tool calling 最強）。
- Baseline：
  - zero-shot：同一份 system prompt；
  - few-shot：固定 3 個 train 範例（3 種不同類型）。
- 微調：沿用 Data-Pipeline 的 `training/train_qlora.py`（unsloth + TRL SFT + MLflow），調整為 Qwen3 與 planner 資料。

| 項目 | 設定 |
|---|---|
| 量化 | 4-bit QLoRA |
| LoRA | r=16、alpha=32，所有 linear 層 |
| 學習率 / epochs | 2e-4、2–3 epochs |
| 有效 batch size | 16 |
| max_seq_length | 依長度統計決定（預計約 1500） |
| Loss | 只算 assistant 段（`train_on_responses_only`，`<\|im_start\|>` 分界） |
| Checkpoint 選擇 | val loss（early stopping patience 1；實作未在訓練中算 exact match，val exact 於訓練後另算） |

流程：20 步 smoke → 完整訓練（預計 30–60 分鐘）。

## 5. 評估

### 5.1 正規化

將每個 step 的 `$sN` 引用遞迴展開為不依賴編號的字串（例：`get_patent(patent_no=get_office_action(oa_id="OA-2026-0331").cited_refs[0])`），再以集合比對；step 編號或平行步驟順序不同不算錯。

### 5.2 指標

| 層級 | 指標 |
|---|---|
| L0 格式 | JSON 合法率、schema 合法率 |
| L1 決策 | `action` 準確率 + 3×3 混淆矩陣 |
| L2 選工具 | tool selection P / R / F1、干擾項誤用率 |
| L3 參數 | 參數完全正確率（字面值 / 引用分開） |
| L4 相依 | `depends_on` 正確率 |
| L5 整體 | **plan exact match（主要指標）** |

`clarify` 比對 `missing` 集合；`refuse` 只比 `action`。

### 5.3 比較矩陣與統計

- 模型（zero-shot / few-shot / QLoRA）× 切分（test_id / test_ood）× 任務類型（6 類）。
- 推論一律 greedy（temperature 0），不做 constrained decoding（JSON 合法率本身就是指標）。
- 每個數字附 95% bootstrap CI 與 n；CI 重疊不宣稱改善。

### 5.4 Error Analysis

1. 程式自動分類：格式錯誤、該反問卻捏造參數、過度拒絕 / 過度反問、誤用干擾項、缺步驟 / 多步驟、參數值錯誤、引用路徑錯誤、相依錯誤。
2. 人工細讀 20–30 筆失敗案例，找出自動分類看不出的模式（例：錯誤是否集中在 3 步以上的結構）。
3. 產出各模型錯誤分布圖，呈現微調前後的變化。

## 6. Optional（依序砍除：unseen tools → demo → constrained decoding → 第二輪訓練）

- **第二輪訓練 / 資料改善**：依 error analysis 補資料後重訓。
- **Constrained decoding ablation**：baseline 加上 JSON 約束解碼，回答「微調是不是只學到格式」。
- **Executor demo**：mock tools + 約 50–100 行 Executor，依 `depends_on` 執行並解析引用，顯示每步中間結果；可兼作 execution-based 評估（計畫能否真的跑動）。
- **Unseen tools**：額外保留 2–3 個 tool 只出現在測試，檢驗模型是否真的讀 tool 描述。

## 7. Repo 結構

```text
patent-planner/
├── planner/      tools.py（tool 定義）、prompt.py（共用 system prompt）、schema.py（格式驗證）
├── datagen/      templates.py、generate.py、paraphrase.py
├── data/         產出的 JSONL（合成資料，進版控）
├── train/        train_qlora.py
├── eval/         infer.py、score.py（正規化 + 指標 + bootstrap CI）、analyze.py（錯誤分類 + 圖表）
├── demo/         executor.py（optional）
└── tests/        評分器正規化、gold 計畫合法性
```

必測：

- 評分器：step 編號不同、平行順序不同時仍判定一致；
- gold 合法：引用可解析、無循環相依、`depends_on` 與引用一致；非 `refuse` 類的必要 tool 都在 `available_tools`。

## 8. 時程

| 日期 | 工作 |
|---|---|
| 10/9（五） | spec + 實作計畫；確認 Qwen3-4B 可在 unsloth 載入 |
| 10/10（六） | tools、模板（Allen 審稿）、生成器；Ollama 改寫背景執行 → 資料集 v1 |
| 10/11（日） | 評分器 + 推論；zero-shot / few-shot baseline |
| 10/12（一） | smoke → 完整訓練 → 評估 |
| 10/13（二） | error analysis；第二輪或 constrained decoding ablation。**主線須在此日完成** |
| 10/14（三） | optional 項目；凍結所有結果 |
| 10/15（四） | 20 分鐘簡報 + 演練 |
| 10/16（五） | 二面 |

## 9. 簡報骨架（約 12–15 頁，對應題目四個 Delivery Points）

1. 問題與 Agent 定義（Plan-and-Execute 的選擇理由與 trade-off）
2. Tool 設計與任務類型
3. 資料設計：反向生成、改寫品質控制、test_ood 切分
4. Baseline 與微調設定、實作遇到的問題
5. 結果：分層指標 × 切分 × 類型（附 CI 與 n）
6. Error analysis：錯誤分布與典型案例
7. 限制與更多時間會做的事（自動產生模板、replan loop、unseen tools、更大規模資料）
