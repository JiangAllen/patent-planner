# Error Analysis

所有數字都來自 `reports/results.md`，是本批測試集的觀察值。exact match 附 95% bootstrap CI；CI 重疊的情況不宣稱有差異。訓練只跑一次，seed 固定為 42。

## 1. 整體結論

| run | test_id（n=121） | test_ood（n=149） |
|---|---|---|
| zero-shot | 0.413 [0.322, 0.504] | 0.208 [0.141, 0.275] |
| few-shot（3 shots） | 0.612 [0.521, 0.702] | 0.215 [0.148, 0.275] |
| **QLoRA r16** | **0.992 [0.975, 1.000]** | **0.443 [0.362, 0.517]** |

- 在 test_id 與 test_ood 上，QLoRA 的 CI 都與兩個 baseline 不重疊，可以說它比 baseline 好。
- few-shot 在 test_id 比 zero-shot 好，兩者的 CI 不重疊；但在 test_ood 上兩者完全重疊，**few-shot 對沒看過的結構幾乎沒有幫助**。
- 微調的進步**不只是學會輸出格式**：
  - JSON 合法率在微調前已有 0.95–0.98，所以格式不是主要差距。
  - 真正拉開差距的是：引用參數準確率（OOD 從 0.433 升到 0.520）、相依關係準確率（0.590 升到 0.690）、action 準確率（0.638 升到 0.953）。
  - 因此判斷不需要另外做 constrained decoding ablation。

## 2. 泛化：test_id vs test_ood

| run | test_id − test_ood |
|---|---|
| zero-shot | 0.205 |
| few-shot | 0.397 |
| QLoRA | 0.549 |

- 差距隨模型變強而擴大，意思是**模型越會做訓練時看過的結構，在沒看過的結構上落差越大**。
- QLoRA 在 val 上的 exact match 是 1.000（n=167），val loss 降到 1.5e-5。這表示模型已經把 30 個模板的結構完全學會，所以 val 指標無法反映泛化能力，**OOD 才是唯一可信的泛化訊號**。
- 把 test_ood 拆成 6 個 holdout 結構來看（QLoRA，每個結構 n≈25）：

| 結構 | 類型 | exact | 這個結構需要什麼 |
|---|---|---|---|
| S10 | parallel | 1.00 | 舊的步驟重新組合 |
| S17 | chain | 0.92 | 舊的步驟重新組合 |
| S30 | refuse | 0.72 | 根據工具清單判斷做不到 |
| S16 | chain | 0.00（還原嵌入引用後 0.44） | 舊的步驟，新的串接方式 |
| S22 | dag | 0.00 | **新的參數組合**（draft_response 同時帶 arguments 與 amendments） |
| S26 | clarify | 0.00 | **新的輸出形狀**（一次缺兩個欄位） |

**核心發現：只要是把訓練時看過的元件重新組合，模型都能泛化；需要訓練資料裡從沒出現過的元件時，就完全失敗。** 第 4 節用訓練集的統計數字證明這一點。

## 3. 依任務類型

![test_id](figs/exact_by_category_test_id.png)
![test_ood](figs/exact_by_category_test_ood.png)

- **進步最多的是 dag**（test_id 從 0.21 升到 1.00，n=19）**和 clarify**。clarify 在 action 混淆矩陣上，從 few-shot 判對 5/28 筆，升到 QLoRA 判對 28/28 筆。也就是說，模型已經學會「資訊不夠時要先問」。
- **最差的仍然是 OOD 的 dag（S22）與 clarify（S26），兩者都是 0.00**，原因見第 4 節。
- **refuse 有一個有教學價值的反例**：few-shot 讓 OOD 的 refuse 從 0.80 掉到 0.00（n=25）。3 個示範例子都是「工具夠用就產出 plan」，模型因此被帶偏成一律產出 plan，即使工具清單裡沒有 `calc_deadline` 也一樣。QLoRA 把它拉回 0.72。
- clarify 在 test_id 只有 n=4，因為改寫後的句子與 train 重複，被去重剔除了（見資料段）。clarify 的結論要以 test_ood 的 n=24 為主。

## 4. 錯誤型態

![errors](figs/error_distribution.png)

- **微調前後的比較**：test_ood 的 `format` 錯誤從 26/15（zero-shot / few-shot）降到 1，`hallucinated_args` 從 19/16 降到 0。仍然偏高的是 `ref_arg`（49）、`dependency`（31）、`wrong_missing`（24）。
- 以下 3 個模式來自細讀 30 筆失敗案例（`reports/failures_qlora-r16.md`，每筆都有觀察）。它們全部來自 test_ood，集中在 S16、S22、S26。另外有 1 筆 S17 屬於模式 C。

### 模式 A：訓練資料沒出現過的參數組合，模型永遠不會產生（S22，25/25 失敗）

- **代表案例**：`test_ood-00098`。gold 是先取 OA、修正請求項，兩者再匯合到 `draft_response(arguments=$s1.grounds, amendments=$s2.amended_claim)`。模型修正了請求項，但 `draft_response` 只接一個來源，而且沒有 `amendments`。
- **證據**：
  - train 裡 `draft_response` 帶 `amendments` 的筆數是 **0/2039**。
  - QLoRA 在 S22 產出 `amendments` 的筆數也是 **0/25**。
  - 另有 15/25 筆直接漏掉 `get_office_action`，把字面文字（例如「核駁理由」）塞進 `arguments`。
- **解讀**：LoRA 學到的是「每個工具在訓練資料裡實際用過的參數樣式」，而不是工具簽名本身。即使工具清單已經寫明有 `amendments` 這個參數，模型也不會用。

### 模式 B：clarify 的缺漏清單長度被訓練資料固定（S26，24/24 失敗）

- **代表案例**：`test_ood-00109`。「請求項1和引證案有什麼不同？」的 gold 是 `missing=[case_id, reference_patent_no]`，模型回答 `[claim_text, reference_patent_no]`。
- **證據**：
  - train 的 clarify 中，缺漏清單長度是 1 的占 **237/237**。
  - S26 的預測分布：9 筆只列 `[case_id]`（長度 1）；13 筆照抄 `compare_claims` 的參數名 `[claim_text, reference_patent_no]`，沒想到請求項文字要先用 `get_case` 取得；2 筆列 `[patent_no]`。
- **解讀**：action 判斷 28/28 全對，代表模型知道「該問」，但不知道「要問什麼」。這一題需要兩跳推理：先看出 `compare_claims` 需要 `claim_text`，再推出 `claim_text` 要由 `get_case(case_id)` 取得。訓練資料沒有教過這種推理。

### 模式 C：引用的寫法不同，加上看到「客戶」就去查案件（S16、S17）

- **代表案例**：`test_ood-00029`。步驟、相依、引用都正確，但 `message` 寫成「…新期限為：$s2.deadline」，gold 要的是純引用 `$s2.deadline`。
- **敏感度分析**（`evaluation/sensitivity.py`）：把「字串裡恰好嵌入一個引用」的參數還原成純引用後，exact match 變化如下：
  - QLoRA 在 test_ood 從 0.443 升到 0.517，S16 從 0/25 升到 11/25。
  - 兩個 baseline 也同樣上升：zero-shot 從 0.208 升到 0.329，few-shot 從 0.215 升到 0.302。
  - 這代表**主指標中有一部分失敗，其實是違反了格式約定，而不是規劃錯誤**。主指標維持不變，因為 Executor 只能解析純引用。
- **另一個子模式**：S16 有 10/25 筆多加了一步 `get_case`，第一步就去查案件，導致後面的步驟編號全部位移。train 裡含「客戶」的 208 筆需求，沒有一筆用到 `get_case`，所以這不是從訓練資料學來的共現關係，**原因目前不確定**。

## 5. 限制與下一步

| 限制 | 影響 | 改善方式 |
|---|---|---|
| 只有 30 個模板，每個工具的參數樣式固定 | 造成模式 A 與 B：模型學到的是樣式，不是工具簽名 | 依工具簽名系統性地產生參數組合，並讓 clarify 的缺漏長度涵蓋 1–3 |
| OOD 只有 6 個結構，每個 n≈25 | 單一結構的結論粒度很粗；CI 是對樣本做 bootstrap，不是對結構做 bootstrap | 增加 holdout 結構數，改成以結構為單位計算 CI |
| 只訓練一次（seed 42） | 無法區分不同 seed 之間的變異和真正的效果 | 用 3 個 seed 重訓，回報平均值與範圍 |
| test_id 的 clarify 只有 n=4 | 這一格的結論不可靠 | 讓 clarify 的句型更多樣，避免去重後被剔除 |
| 改寫模型引入錯字（「答辨」51 筆、「答辦」3 筆，約 2.1%） | 視為真實使用者的錯字雜訊，沒有修正 | 在改寫檢查中加入領域詞白名單 |
| 主指標要求純引用 | 會把格式問題算成規劃錯誤（見模式 C） | 在 prompt 明確要求「引用不得嵌入句子」，或讓 Executor 支援字串插值 |
