# patent-planner

專利答辯 Agent 的 Planner 微調：以合成資料對 `Qwen3-4B-Instruct-2507` 做 QLoRA，並與 zero-shot / few-shot baseline 比較。

## 結果摘要

主指標是 **plan exact match**：整份計畫要完全對才算 1 分（工具、參數、引用、相依全部正確；clarify 要缺漏欄位集合相同；refuse 只看動作）。比對前會把 `$sN` 引用展開成不依賴步驟編號的形式，所以編號或步驟順序不同不扣分。括號內為 95% bootstrap CI。

| run | test_id（n=121，訓練看過的題型） | test_ood（n=149，6 種沒看過的題型） |
|---|---|---|
| zero-shot | 0.413 [0.322, 0.504] | 0.208 [0.141, 0.275] |
| few-shot（3 shots） | 0.612 [0.521, 0.702] | 0.215 [0.148, 0.275] |
| qlora-r16 | 0.992 [0.975, 1.000] | 0.443 [0.362, 0.517] |
| qlora-r16-v2（針對性補資料） | 1.000 | 0.544 [0.463, 0.617] |

同題配對 bootstrap（兩組考同一批題目，比獨立 CI 是否重疊更有檢定力）：

- qlora-r16 − few-shot：test_ood **+0.228** [+0.161, +0.295]
- qlora-r16-v2 − qlora-r16：test_ood **+0.101** [+0.040, +0.161]；test_id +0.008 [0, +0.025]，沒有退步

結論：微調讓模型穩定學會格式與已知題型，並能泛化部分「舊元件的新組合」；在本實驗的 6 個 holdout 結構上，模型未能可靠產生訓練資料沒示範過的參數用法或輸出形狀。第二輪補上元件後，元件學會了，但組合與兩跳推理沒有轉移（假設部分成立、部分不成立）。v2 是依測試集的失敗原因補資料，屬於針對性調整（targeted adaptation），其 OOD 數字不是無偏的泛化成績；主成果以 v1 為準。細節與限制見 `reports/error_analysis.md`。

所有數字皆為本批合成測試集的觀察值，不代表真實案件上的表現。

## 架構

Plan-and-Execute：Planner 一次輸出工具呼叫 DAG（JSON），Executor 依 `depends_on` 執行並解析 `$sN.欄位` 引用。輸出三種動作：`plan`、`clarify`（缺必要資訊）、`refuse`（沒有可用工具）。

## 重現步驟

1. 資料：`uv run python -m datagen.generate` → `uv run python -m datagen.paraphrase`（需本地 Ollama `qwen2.5:7b-instruct`；附 `data/paraphrase_cache*.jsonl`，有快取時不需要 Ollama）。第二輪：`uv run python -m datagen.augment`
2. 推論與訓練（WSL，CUDA GPU）：在 `train/` 下
   - `uv run python infer.py --run-name zeroshot`（few-shot 加 `--shots 3`；adapter 加 `--model ../outputs/adapters/<run>`）
   - `uv run python train_qlora.py --run-name qlora-r16`（第二輪加 `--train-file train_v2`）
3. 評估：`uv run python -m evaluation.analyze --runs zeroshot fewshot qlora-r16 qlora-r16-v2`
   - 配對比較：`uv run python -m evaluation.sensitivity --paired qlora-r16 qlora-r16-v2`
4. 測試：`uv run pytest -q`

## 文件

- **簡報素材總覽：`docs/briefing.md`**
- 設計：`docs/design.md`；第二輪計畫：`docs/plan-v2.md`
- 評估結果：`reports/results.md`
- Demo 與可執行率：`reports/demo.md`
- Error analysis：`reports/error_analysis.md`；失敗案例：`reports/failures_*.md`
